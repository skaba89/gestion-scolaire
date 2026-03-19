/**
 * Load Testing Suite for EtudePlus (SchoolFlow Pro)
 * Using k6 for performance testing
 * 
 * Run with: k6 run load-tests/etudeplus-load.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const loginTrend = new Trend('login_duration');
const apiTrend = new Trend('api_duration');
const dbQueries = new Counter('db_queries');

// Test configuration
export const options = {
  // Stages for ramp-up test
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 users
    { duration: '1m', target: 50 },    // Ramp up to 50 users
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '1m', target: 100 },   // Stay at 100 users
    { duration: '30s', target: 0 },    // Ramp down
  ],
  
  // Thresholds
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% under 500ms, 99% under 1s
    errors: ['rate<0.05'],  // Less than 5% errors
    login_duration: ['p(95)<1000'],
    api_duration: ['p(95)<300'],
  },
  
  // Scenarios for different test types
  scenarios: {
    // Smoke test - quick validation
    smoke: {
      executor: 'constant-vus',
      vus: 5,
      duration: '1m',
      tags: { test_type: 'smoke' },
      exec: 'smokeTest',
    },
    
    // Load test - normal load
    load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 50 },
        { duration: '5m', target: 50 },
        { duration: '1m', target: 0 },
      ],
      tags: { test_type: 'load' },
      exec: 'loadTest',
    },
    
    // Stress test - beyond normal capacity
    stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },
        { duration: '5m', target: 200 },
        { duration: '2m', target: 300 },
        { duration: '1m', target: 0 },
      ],
      tags: { test_type: 'stress' },
      exec: 'stressTest',
    },
    
    // Spike test - sudden load increase
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 100 },
        { duration: '30s', target: 100 },
        { duration: '10s', target: 0 },
      ],
      tags: { test_type: 'spike' },
      exec: 'spikeTest',
    },
  },
};

// Base URL from environment or default
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_V1 = `${BASE_URL}/api/v1`;

// Test data
const TEST_USERS = [
  { email: 'admin@test.local', password: 'Test123!', role: 'admin' },
  { email: 'teacher@test.local', password: 'Test123!', role: 'teacher' },
  { email: 'student@test.local', password: 'Test123!', role: 'student' },
];

// Authentication helper
function authenticate(user) {
  const response = http.post(`${API_V1}/auth/login`, JSON.stringify({
    email: user.email,
    password: user.password,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  loginTrend.add(response.timings.duration);
  
  check(response, {
    'login successful': (r) => r.status === 200,
    'has access token': (r) => r.json('access_token') !== undefined,
  });
  
  if (response.status !== 200) {
    errorRate.add(1);
    return null;
  }
  
  return response.json('access_token');
}

// Common headers helper
function getHeaders(token, tenantId = 'test-tenant-1') {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    'X-Tenant-ID': tenantId,
  };
}

// Health check
export function smokeTest() {
  const response = http.get(`${BASE_URL}/health/`);
  
  check(response, {
    'health check passed': (r) => r.status === 200,
    'status is healthy': (r) => r.json('status') === 'healthy',
  });
  
  sleep(1);
}

// Normal load simulation
export function loadTest() {
  const user = TEST_USERS[Math.floor(Math.random() * TEST_USERS.length)];
  const token = authenticate(user);
  
  if (!token) {
    return;
  }
  
  const headers = getHeaders(token);
  
  // Simulate typical user actions
  const actions = [
    () => http.get(`${API_V1}/users/me`, { headers }),
    () => http.get(`${API_V1}/students/`, { headers }),
    () => http.get(`${API_V1}/grades/`, { headers }),
    () => http.get(`${API_V1}/attendance/`, { headers }),
    () => http.get(`${API_V1}/dashboard/`, { headers }),
  ];
  
  // Random action
  const action = actions[Math.floor(Math.random() * actions.length)];
  const response = action();
  
  apiTrend.add(response.timings.duration);
  
  check(response, {
    'API response OK': (r) => r.status === 200 || r.status === 403,
  });
  
  if (response.status >= 400 && response.status !== 403) {
    errorRate.add(1);
  }
  
  dbQueries.add(1);
  sleep(Math.random() * 3 + 1); // 1-4 seconds between requests
}

// Stress test - heavier load
export function stressTest() {
  const user = TEST_USERS[0]; // Use admin for stress test
  const token = authenticate(user);
  
  if (!token) {
    return;
  }
  
  const headers = getHeaders(token);
  
  // Multiple rapid requests
  const responses = http.batch([
    ['GET', `${API_V1}/students/`, null, { headers }],
    ['GET', `${API_V1}/grades/`, null, { headers }],
    ['GET', `${API_V1}/attendance/`, null, { headers }],
    ['GET', `${API_V1}/analytics/`, null, { headers }],
  ]);
  
  responses.forEach(response => {
    apiTrend.add(response.timings.duration);
    check(response, {
      'response OK under stress': (r) => r.status < 500,
    });
    if (response.status >= 500) {
      errorRate.add(1);
    }
  });
  
  sleep(0.5);
}

// Spike test - sudden burst
export function spikeTest() {
  const user = TEST_USERS[0];
  const token = authenticate(user);
  
  if (!token) {
    return;
  }
  
  const headers = getHeaders(token);
  
  // Rapid fire requests
  for (let i = 0; i < 10; i++) {
    const response = http.get(`${API_V1}/health/`, { headers });
    check(response, {
      'spike response OK': (r) => r.status === 200 || r.status === 429,
    });
    if (response.status >= 500) {
      errorRate.add(1);
    }
  }
  
  sleep(1);
}

// Setup function - runs once per VU
export function setup() {
  console.log(`Starting load test against ${BASE_URL}`);
  
  // Verify API is accessible
  const health = http.get(`${BASE_URL}/health/`);
  if (health.status !== 200) {
    throw new Error('API health check failed');
  }
  
  return { startTime: Date.now() };
}

// Teardown function - runs once after all VUs finish
export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000;
  console.log(`Load test completed in ${duration}s`);
}

// Handle summary
export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'load-test-results.json': JSON.stringify(data, null, 2),
  };
}

function textSummary(data, opts) {
  // Simple text summary
  return `
Load Test Summary
==================
Total Requests: ${data.metrics.http_reqs?.values?.count || 0}
Failed Requests: ${data.metrics.errors?.values?.rate || 0}
Avg Response Time: ${data.metrics.http_req_duration?.values?.avg || 0}ms
P95 Response Time: ${data.metrics.http_req_duration?.values?.['p(95)'] || 0}ms
P99 Response Time: ${data.metrics.http_req_duration?.values?.['p(99)'] || 0}ms
`;
}
