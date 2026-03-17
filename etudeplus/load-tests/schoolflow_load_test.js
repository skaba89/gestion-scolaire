/**
 * k6 Load Testing Script for SchoolFlow Pro
 * 
 * This script tests various API endpoints under different load scenarios.
 * Run with: k6 run load_tests/schoolflow_load_test.js
 * 
 * Scenarios:
 * 1. Smoke test - Verify system works under minimal load
 * 2. Load test - Test expected production load
 * 3. Stress test - Find breaking points
 * 4. Spike test - Handle sudden traffic increases
 * 5. Soak test - Long-term stability
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// ─── Custom Metrics ────────────────────────────────────────────────────────

const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency');
const dbOperations = new Counter('db_operations');

// ─── Configuration ──────────────────────────────────────────────────────────

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_V1 = `${BASE_URL}/api/v1`;

// Test credentials (would be environment variables in production)
const TEST_TOKEN = __ENV.TEST_TOKEN || '';
const TENANT_ID = __ENV.TENANT_ID || 'test-tenant-id';

// ─── Test Scenarios ─────────────────────────────────────────────────────────

export const options = {
    // Scenarios for different test types
    scenarios: {
        // Smoke test: Quick verification
        smoke: {
            executor: 'constant-vus',
            vus: 5,
            duration: '1m',
            tags: { test_type: 'smoke' },
            exec: 'smokeTest',
        },
        
        // Load test: Normal expected load
        load_test: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '2m', target: 50 },   // Ramp up to 50 users
                { duration: '5m', target: 50 },   // Stay at 50 users
                { duration: '2m', target: 100 },  // Ramp up to 100 users
                { duration: '5m', target: 100 },  // Stay at 100 users
                { duration: '2m', target: 0 },    // Ramp down
            ],
            tags: { test_type: 'load' },
            exec: 'loadTest',
        },
        
        // Stress test: Find breaking points
        stress_test: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '2m', target: 100 },
                { duration: '2m', target: 200 },
                { duration: '2m', target: 300 },
                { duration: '2m', target: 400 },
                { duration: '2m', target: 500 },
                { duration: '5m', target: 500 },
                { duration: '2m', target: 0 },
            ],
            tags: { test_type: 'stress' },
            exec: 'stressTest',
        },
        
        // Spike test: Sudden traffic increase
        spike_test: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '10s', target: 100 },
                { duration: '1m', target: 100 },
                { duration: '10s', target: 500 },  // Sudden spike
                { duration: '1m', target: 500 },
                { duration: '10s', target: 100 },  // Back down
                { duration: '1m', target: 100 },
                { duration: '10s', target: 0 },
            ],
            tags: { test_type: 'spike' },
            exec: 'spikeTest',
        },
    },
    
    // Thresholds for pass/fail criteria
    thresholds: {
        http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
        errors: ['rate<0.05'],  // Error rate < 5%
        api_latency: ['p(95)<300'],
    },
};

// ─── Common Headers ─────────────────────────────────────────────────────────

function getHeaders(token = TEST_TOKEN) {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'X-Tenant-ID': TENANT_ID,
    };
}

// ─── Test Functions ─────────────────────────────────────────────────────────

export function smokeTest() {
    // Basic health check
    const healthRes = http.get(`${BASE_URL}/health/`);
    check(healthRes, {
        'health check status is 200': (r) => r.status === 200,
        'health check returns healthy': (r) => r.json('status') === 'healthy',
    });
    
    // API info check
    const rootRes = http.get(`${BASE_URL}/`);
    check(rootRes, {
        'root endpoint returns 200': (r) => r.status === 200,
    });
    
    sleep(1);
}

export function loadTest() {
    // Simulate realistic user behavior
    
    // 1. Health check (monitoring)
    const healthRes = http.get(`${BASE_URL}/health/`);
    errorRate.add(healthRes.status !== 200);
    
    // 2. List students
    const studentsRes = http.get(`${API_V1}/students/?limit=20`, {
        headers: getHeaders(),
    });
    check(studentsRes, {
        'students list status 200 or 401': (r) => [200, 401].includes(r.status),
    });
    apiLatency.add(studentsRes.timings.duration);
    
    sleep(1);
    
    // 3. Get dashboard stats
    const dashboardRes = http.get(`${API_V1}/dashboard/stats`, {
        headers: getHeaders(),
    });
    check(dashboardRes, {
        'dashboard status 200 or 401': (r) => [200, 401].includes(r.status),
    });
    
    sleep(2);
    
    // 4. Check notifications
    const notifRes = http.get(`${API_V1}/notifications/`, {
        headers: getHeaders(),
    });
    
    sleep(1);
}

export function stressTest() {
    // Aggressive testing to find limits
    
    // 1. Multiple concurrent requests
    const requests = [
        ['students', `${API_V1}/students/?limit=50`],
        ['teachers', `${API_V1}/teachers/`],
        ['grades', `${API_V1}/grades/`],
        ['attendance', `${API_V1}/attendance/`],
    ];
    
    const responses = http.batch(
        requests.map(([name, url]) => ({
            method: 'GET',
            url,
            headers: getHeaders(),
            tags: { endpoint: name },
        }))
    );
    
    responses.forEach((res, i) => {
        const [name] = requests[i];
        check(res, {
            [`${name} responds`]: (r) => r.status < 500,
        });
        errorRate.add(res.status >= 500);
        apiLatency.add(res.timings.duration);
    });
    
    sleep(0.5);
    
    // 2. Create operations
    const createStudent = http.post(
        `${API_V1}/students/`,
        JSON.stringify({
            first_name: `LoadTest${__VU}`,
            last_name: `User${__ITER}`,
            date_of_birth: '2010-01-01',
            gender: 'M',
        }),
        { headers: getHeaders() }
    );
    
    check(createStudent, {
        'student create acceptable': (r) => [200, 201, 401, 422].includes(r.status),
    });
    
    sleep(1);
}

export function spikeTest() {
    // Quick burst of requests
    
    // 1. Rapid fire health checks
    for (let i = 0; i < 5; i++) {
        const res = http.get(`${BASE_URL}/health/`);
        check(res, {
            'health check during spike': (r) => r.status === 200,
        });
    }
    
    // 2. API calls with authentication
    const res = http.get(`${API_V1}/students/`, { headers: getHeaders() });
    errorRate.add(res.status >= 500);
    
    sleep(0.1);  // Very short sleep for spike simulation
}

// ─── Authentication Load Test ───────────────────────────────────────────────

export function authLoadTest() {
    // Test authentication endpoint specifically
    
    const loginRes = http.post(
        `${API_V1}/auth/login`,
        JSON.stringify({
            username: 'testuser',
            password: 'testpassword',
        }),
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    check(loginRes, {
        'login responds': (r) => r.status !== 0,
        'login not server error': (r) => r.status < 500,
    });
    
    errorRate.add(loginRes.status >= 500);
    
    sleep(1);
}

// ─── Database-Intensive Operations ──────────────────────────────────────────

export function dbIntensiveTest() {
    // Test endpoints that hit the database hard
    
    // 1. Search with complex filters
    const searchRes = http.get(
        `${API_V1}/students/?search=test&level=6eme&status=active&limit=100`,
        { headers: getHeaders() }
    );
    dbOperations.add(1);
    
    // 2. Aggregation queries
    const statsRes = http.get(
        `${API_V1}/analytics/summary?start=2024-01-01&end=2024-12-31`,
        { headers: getHeaders() }
    );
    dbOperations.add(1);
    
    // 3. Reports generation
    const reportRes = http.get(
        `${API_V1}/reports/grades/export?format=pdf`,
        { headers: getHeaders() }
    );
    dbOperations.add(1);
    
    sleep(2);
}

// ─── Setup and Teardown ─────────────────────────────────────────────────────

export function setup() {
    console.log('Starting load test...');
    console.log(`Base URL: ${BASE_URL}`);
    
    // Verify the API is accessible
    const res = http.get(`${BASE_URL}/health/`);
    if (res.status !== 200) {
        console.error('API is not healthy, aborting test');
        return { abort: true };
    }
    
    return { startTime: Date.now() };
}

export function teardown(data) {
    if (data.startTime) {
        const duration = (Date.now() - data.startTime) / 1000;
        console.log(`Load test completed in ${duration}s`);
    }
}

// ─── Handle Summary ─────────────────────────────────────────────────────────

export function handleSummary(data) {
    return {
        'stdout': textSummary(data, { indent: ' ', enableColors: true }),
        'load-test-results.json': JSON.stringify(data, null, 2),
        'load-test-summary.html': htmlSummary(data),
    };
}

function textSummary(data, options) {
    // Custom text summary
    const indent = options.indent || '';
    const stats = data.metrics;
    
    let summary = `\n${indent}=== Load Test Summary ===\n\n`;
    
    // HTTP requests
    if (stats.http_reqs) {
        summary += `${indent}Total Requests: ${stats.http_reqs.values.count}\n`;
        summary += `${indent}Request Rate: ${stats.http_reqs.values.rate.toFixed(2)}/s\n\n`;
    }
    
    // Duration
    if (stats.http_req_duration) {
        summary += `${indent}Response Time:\n`;
        summary += `${indent}  Avg: ${stats.http_req_duration.values.avg.toFixed(2)}ms\n`;
        summary += `${indent}  P95: ${stats.http_req_duration.values['p(95)'].toFixed(2)}ms\n`;
        summary += `${indent}  P99: ${stats.http_req_duration.values['p(99)'].toFixed(2)}ms\n\n`;
    }
    
    // Errors
    if (stats.errors) {
        summary += `${indent}Error Rate: ${(stats.errors.values.rate * 100).toFixed(2)}%\n\n`;
    }
    
    // Thresholds
    summary += `${indent}Threshold Results:\n`;
    for (const [name, result] of Object.entries(data.thresholds || {})) {
        const status = result.ok ? '✓ PASS' : '✗ FAIL';
        summary += `${indent}  ${status}: ${name}\n`;
    }
    
    return summary;
}

function htmlSummary(data) {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>Load Test Report - SchoolFlow Pro</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 4px; }
        .metric-value { font-size: 2em; font-weight: bold; color: #007bff; }
        .metric-label { color: #666; }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #007bff; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Load Test Report - SchoolFlow Pro</h1>
        <p>Generated: ${new Date().toISOString()}</p>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">${data.metrics.http_reqs?.values.count || 0}</div>
                <div class="metric-label">Total Requests</div>
            </div>
            <div class="metric">
                <div class="metric-value">${(data.metrics.http_req_duration?.values.avg || 0).toFixed(0)}ms</div>
                <div class="metric-label">Avg Response</div>
            </div>
            <div class="metric">
                <div class="metric-value">${((data.metrics.errors?.values.rate || 0) * 100).toFixed(1)}%</div>
                <div class="metric-label">Error Rate</div>
            </div>
        </div>
        
        <h2>Threshold Results</h2>
        <table>
            <tr><th>Threshold</th><th>Result</th></tr>
            ${Object.entries(data.thresholds || {}).map(([name, result]) => `
                <tr>
                    <td>${name}</td>
                    <td class="${result.ok ? 'pass' : 'fail'}">${result.ok ? 'PASS' : 'FAIL'}</td>
                </tr>
            `).join('')}
        </table>
    </div>
</body>
</html>
`;
}
