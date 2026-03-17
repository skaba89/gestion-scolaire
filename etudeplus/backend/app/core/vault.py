"""
HashiCorp Vault Integration for Secrets Management
Supports: KV secrets engine, database credentials, PKI, encryption keys
"""
import os
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class VaultConfig:
    """Configuration for Vault connection."""
    url: str = os.getenv("VAULT_ADDR", "http://vault:8200")
    token: str = os.getenv("VAULT_TOKEN", "")
    role_id: str = os.getenv("VAULT_ROLE_ID", "")
    secret_id: str = os.getenv("VAULT_SECRET_ID", "")
    namespace: str = os.getenv("VAULT_NAMESPACE", "")
    kv_mount: str = os.getenv("VAULT_KV_MOUNT", "secret")
    db_mount: str = os.getenv("VAULT_DB_MOUNT", "database")
    pki_mount: str = os.getenv("VAULT_PKI_MOUNT", "pki")
    timeout: int = 10
    verify_ssl: bool = os.getenv("VAULT_SKIP_VERIFY", "false").lower() != "true"
    
    @property
    def use_approle(self) -> bool:
        """Check if AppRole authentication should be used."""
        return bool(self.role_id and self.secret_id)


class VaultError(Exception):
    """Base exception for Vault operations."""
    pass


class VaultAuthenticationError(VaultError):
    """Authentication failed."""
    pass


class VaultSecretNotFoundError(VaultError):
    """Secret not found."""
    pass


class VaultClient:
    """
    HashiCorp Vault client with:
    - AppRole and Token authentication
    - Automatic token renewal
    - Secret caching with TTL
    - Database credential leasing
    - Encryption/Decryption operations
    """
    
    def __init__(self, config: Optional[VaultConfig] = None):
        self.config = config or VaultConfig()
        self._token: Optional[str] = None
        self._token_lease_expiry: float = 0
        self._secret_cache: Dict[str, tuple] = {}  # path -> (data, expiry)
        self._session = self._create_session()
        
        # Auto-authenticate if configured
        if self.config.use_approle or self.config.token:
            self.authenticate()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        if self.config.namespace:
            session.headers["X-Vault-Namespace"] = self.config.namespace
        
        return session
    
    def _url(self, path: str) -> str:
        """Build full URL for Vault API endpoint."""
        return f"{self.config.url}/v1/{path}"
    
    def _headers(self) -> Dict[str, str]:
        """Build headers with authentication token."""
        headers = {}
        if self._token:
            headers["X-Vault-Token"] = self._token
        return headers
    
    def authenticate(self) -> bool:
        """Authenticate with Vault using AppRole or static token."""
        if self.config.use_approle:
            return self._auth_approle()
        elif self.config.token:
            self._token = self.config.token
            return self._verify_token()
        return False
    
    def _auth_approle(self) -> bool:
        """Authenticate using AppRole method."""
        try:
            response = self._session.put(
                self._url("auth/approle/login"),
                json={
                    "role_id": self.config.role_id,
                    "secret_id": self.config.secret_id
                },
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            data = response.json()
            auth = data.get("auth", {})
            self._token = auth.get("client_token")
            self._token_lease_expiry = time.time() + auth.get("lease_duration", 3600)
            
            logger.info("Successfully authenticated with Vault via AppRole")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Vault AppRole authentication failed: {e}")
            raise VaultAuthenticationError(f"AppRole auth failed: {e}")
    
    def _verify_token(self) -> bool:
        """Verify that the token is valid."""
        try:
            response = self._session.get(
                self._url("auth/token/lookup-self"),
                headers=self._headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            if response.status_code == 200:
                data = response.json()
                self._token_lease_expiry = time.time() + data["data"]["ttl"]
                logger.info("Vault token verified successfully")
                return True
            return False
            
        except requests.RequestException as e:
            logger.error(f"Vault token verification failed: {e}")
            return False
    
    def renew_token(self) -> bool:
        """Renew the current token."""
        if not self._token:
            return False
            
        try:
            response = self._session.post(
                self._url("auth/token/renew-self"),
                headers=self._headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            data = response.json()
            self._token_lease_expiry = time.time() + data["auth"]["lease_duration"]
            logger.info("Vault token renewed successfully")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Token renewal failed: {e}")
            return False
    
    def check_token_needs_renewal(self) -> bool:
        """Check if token needs renewal (within 5 minutes of expiry)."""
        return time.time() > (self._token_lease_expiry - 300)
    
    def ensure_valid_token(self) -> None:
        """Ensure we have a valid token, renewing if necessary."""
        if self.check_token_needs_renewal():
            self.renew_token()
    
    # ─── KV Secrets Engine ─────────────────────────────────────────────
    
    def get_secret(
        self, 
        path: str, 
        key: Optional[str] = None,
        cache_ttl: int = 300,
        mount: Optional[str] = None
    ) -> Any:
        """
        Retrieve a secret from KV engine.
        
        Args:
            path: Secret path (without mount prefix)
            key: Specific key within the secret (optional)
            cache_ttl: Cache TTL in seconds (0 to disable)
            mount: KV mount point (default from config)
        
        Returns:
            Secret value (dict if key=None, otherwise specific value)
        """
        self.ensure_valid_token()
        mount = mount or self.config.kv_mount
        full_path = f"{mount}/data/{path}"
        
        # Check cache
        if cache_ttl > 0 and full_path in self._secret_cache:
            data, expiry = self._secret_cache[full_path]
            if time.time() < expiry:
                logger.debug(f"Secret cache hit: {path}")
                return data.get(key) if key else data
        
        try:
            # KV v2 API
            response = self._session.get(
                self._url(full_path),
                headers=self._headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            if response.status_code == 404:
                raise VaultSecretNotFoundError(f"Secret not found: {path}")
            
            response.raise_for_status()
            
            data = response.json()["data"]["data"]
            
            # Cache the result
            if cache_ttl > 0:
                self._secret_cache[full_path] = (data, time.time() + cache_ttl)
            
            return data.get(key) if key else data
            
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve secret {path}: {e}")
            raise VaultError(f"Failed to retrieve secret: {e}")
    
    def set_secret(
        self, 
        path: str, 
        data: Dict[str, Any],
        mount: Optional[str] = None
    ) -> bool:
        """
        Store a secret in KV engine.
        
        Args:
            path: Secret path
            data: Secret data to store
            mount: KV mount point
        
        Returns:
            True if successful
        """
        self.ensure_valid_token()
        mount = mount or self.config.kv_mount
        full_path = f"{mount}/data/{path}"
        
        try:
            response = self._session.post(
                self._url(full_path),
                headers=self._headers(),
                json={"data": data},
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            # Invalidate cache
            if full_path in self._secret_cache:
                del self._secret_cache[full_path]
            
            logger.info(f"Secret stored: {path}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to store secret {path}: {e}")
            raise VaultError(f"Failed to store secret: {e}")
    
    def delete_secret(self, path: str, mount: Optional[str] = None) -> bool:
        """Delete a secret."""
        self.ensure_valid_token()
        mount = mount or self.config.kv_mount
        full_path = f"{mount}/metadata/{path}"
        
        try:
            response = self._session.delete(
                self._url(full_path),
                headers=self._headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            # Invalidate cache
            if full_path in self._secret_cache:
                del self._secret_cache[full_path]
            
            logger.info(f"Secret deleted: {path}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to delete secret {path}: {e}")
            raise VaultError(f"Failed to delete secret: {e}")
    
    # ─── Database Credentials ───────────────────────────────────────────
    
    def get_database_credentials(
        self, 
        db_name: str = "schoolflow",
        role: str = "app"
    ) -> Dict[str, str]:
        """
        Get dynamic database credentials from Vault.
        
        Args:
            db_name: Database connection name in Vault
            role: Database role name
        
        Returns:
            Dict with 'username', 'password', 'lease_id', 'lease_duration'
        """
        self.ensure_valid_token()
        path = f"{self.config.db_mount}/creds/{role}"
        
        try:
            response = self._session.get(
                self._url(path),
                headers=self._headers(),
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            data = response.json()
            return {
                "username": data["data"]["username"],
                "password": data["data"]["password"],
                "lease_id": data["lease_id"],
                "lease_duration": data["lease_duration"]
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to get DB credentials: {e}")
            raise VaultError(f"Failed to get DB credentials: {e}")
    
    def revoke_lease(self, lease_id: str) -> bool:
        """Revoke a lease (e.g., database credentials)."""
        self.ensure_valid_token()
        
        try:
            response = self._session.put(
                self._url("sys/leases/revoke"),
                headers=self._headers(),
                json={"lease_id": lease_id},
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to revoke lease: {e}")
            return False
    
    # ─── Transit (Encryption) ───────────────────────────────────────────
    
    def encrypt(
        self, 
        plaintext: str, 
        key_name: str = "default",
        mount: str = "transit"
    ) -> str:
        """Encrypt data using Transit engine."""
        self.ensure_valid_token()
        import base64
        
        encoded = base64.b64encode(plaintext.encode()).decode()
        
        try:
            response = self._session.post(
                self._url(f"{mount}/encrypt/{key_name}"),
                headers=self._headers(),
                json={"plaintext": encoded},
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            return response.json()["data"]["ciphertext"]
            
        except requests.RequestException as e:
            logger.error(f"Encryption failed: {e}")
            raise VaultError(f"Encryption failed: {e}")
    
    def decrypt(
        self, 
        ciphertext: str, 
        key_name: str = "default",
        mount: str = "transit"
    ) -> str:
        """Decrypt data using Transit engine."""
        self.ensure_valid_token()
        import base64
        
        try:
            response = self._session.post(
                self._url(f"{mount}/decrypt/{key_name}"),
                headers=self._headers(),
                json={"ciphertext": ciphertext},
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            
            encoded = response.json()["data"]["plaintext"]
            return base64.b64decode(encoded).decode()
            
        except requests.RequestException as e:
            logger.error(f"Decryption failed: {e}")
            raise VaultError(f"Decryption failed: {e}")
    
    # ─── Health & Status ────────────────────────────────────────────────
    
    def health_check(self) -> Dict[str, Any]:
        """Check Vault health status."""
        try:
            response = self._session.get(
                f"{self.config.url}/v1/sys/health",
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            
            return {
                "healthy": response.status_code in [200, 429, 472, 473],
                "initialized": response.json().get("initialized", False),
                "sealed": response.json().get("sealed", True),
                "standby": response.json().get("standby", False),
            }
            
        except requests.RequestException as e:
            return {
                "healthy": False,
                "error": str(e)
            }


# ─── Singleton Instance ─────────────────────────────────────────────────

_vault_client: Optional[VaultClient] = None


def get_vault_client() -> VaultClient:
    """Get or create the Vault client singleton."""
    global _vault_client
    
    if _vault_client is None:
        # Only initialize if Vault is enabled
        if os.getenv("VAULT_ENABLED", "false").lower() == "true":
            _vault_client = VaultClient()
            logger.info("Vault client initialized")
        else:
            # Return a non-functional client that falls back to env vars
            _vault_client = VaultClient(config=VaultConfig())
            logger.info("Vault disabled, using environment variables")
    
    return _vault_client


def get_secret_with_fallback(
    vault_path: str,
    env_var: str,
    key: Optional[str] = None,
    default: str = ""
) -> str:
    """
    Get secret from Vault with environment variable fallback.
    
    Args:
        vault_path: Path in Vault
        env_var: Environment variable name for fallback
        key: Key within the secret
        default: Default value if neither source has the secret
    
    Returns:
        Secret value
    """
    vault_enabled = os.getenv("VAULT_ENABLED", "false").lower() == "true"
    
    if vault_enabled:
        try:
            client = get_vault_client()
            return client.get_secret(vault_path, key=key) or os.getenv(env_var, default)
        except VaultError as e:
            logger.warning(f"Vault lookup failed for {vault_path}, using env var: {e}")
            return os.getenv(env_var, default)
    
    return os.getenv(env_var, default)


# ─── Decorator for Database Credentials Rotation ─────────────────────────

def with_vault_db_credentials(db_name: str = "schoolflow", role: str = "app"):
    """
    Decorator to inject fresh database credentials from Vault.
    Use with FastAPI dependency injection.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            vault_enabled = os.getenv("VAULT_ENABLED", "false").lower() == "true"
            
            if vault_enabled:
                client = get_vault_client()
                creds = client.get_database_credentials(db_name, role)
                kwargs["db_credentials"] = creds
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
