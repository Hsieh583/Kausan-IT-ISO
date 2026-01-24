/**
 * Simplified test for API Hook (no external dependencies)
 */

const crypto = require('crypto');

class APIHook {
  constructor(options = {}) {
    this.config = {
      security: {
        sensitive_fields: ['password', 'api_key', 'token', 'secret'],
        encrypt_sensitive_data: true,
        hash_algorithm: 'SHA256'
      }
    };
    this.sensitiveFields = this.config.security.sensitive_fields;
    this.logs = [];
    console.log('API Hook initialized');
  }

  _sanitizeData(data) {
    if (!data || typeof data !== 'object') return data;
    const sanitized = { ...data };
    this.sensitiveFields.forEach(field => {
      if (sanitized[field]) {
        const value = String(sanitized[field]);
        const hash = crypto.createHash('sha256').update(value).digest('hex').substring(0, 16);
        sanitized[field] = `[REDACTED:${hash}]`;
      }
    });
    return sanitized;
  }

  _createLogEntry(options) {
    return {
      timestamp: new Date().toISOString(),
      request_id: options.requestId,
      user_id: options.userId || 'anonymous',
      source_ip: options.sourceIp || '0.0.0.0',
      method: options.method || 'GET',
      endpoint: options.endpoint,
      parameters: this._sanitizeData(options.parameters),
      response_code: options.responseCode,
      response_time_ms: Math.round(options.responseTimeMs * 100) / 100,
      result: options.result,
      error_message: options.errorMessage || null
    };
  }

  _saveLog(logEntry) {
    console.log('API Log:', JSON.stringify(logEntry));
    this.logs.push(logEntry);
  }

  logEvent(eventType, severity, message, metadata = {}) {
    const event = {
      timestamp: new Date().toISOString(),
      event_type: eventType,
      severity: severity,
      message: message,
      metadata: metadata
    };
    console.log('Event:', JSON.stringify(event));
    this._saveLog(event);
  }

  getStats() {
    return {
      total_logs: this.logs.length,
      success_count: this.logs.filter(l => l.result === 'success').length,
      error_count: this.logs.filter(l => l.result === 'error').length
    };
  }
}

// Test the API Hook
console.log('\n=== Test 1: Successful API Call ===');
const hook = new APIHook();

const logEntry1 = hook._createLogEntry({
  requestId: crypto.randomUUID(),
  userId: 'user123',
  sourceIp: '192.168.1.100',
  method: 'POST',
  endpoint: '/api/v1/users',
  parameters: {
    username: 'john_doe',
    password: 'secret123',
    email: 'john@example.com'
  },
  responseCode: 200,
  responseTimeMs: 125.5,
  result: 'success'
});

hook._saveLog(logEntry1);

console.log('\n=== Test 2: Failed API Call ===');
const logEntry2 = hook._createLogEntry({
  requestId: crypto.randomUUID(),
  userId: 'user456',
  sourceIp: '192.168.1.101',
  method: 'POST',
  endpoint: '/api/v1/auth/login',
  parameters: {
    username: 'jane_doe',
    password: 'wrong'
  },
  responseCode: 401,
  responseTimeMs: 50.2,
  result: 'error',
  errorMessage: 'Invalid credentials'
});

hook._saveLog(logEntry2);

console.log('\n=== Test 3: Manual Event Logging ===');
hook.logEvent(
  'security',
  'critical',
  'Suspicious login pattern detected',
  {
    ip: '192.168.1.100',
    attempts: 10,
    user: 'admin'
  }
);

console.log('\n=== Statistics ===');
console.log(JSON.stringify(hook.getStats(), null, 2));

console.log('\n=== API Hook Test Completed ===');
