/**
 * API Hook Implementation - Node.js Example
 * 用於監控與記錄 API 呼叫的 Node.js/Express 實作範例
 */

const crypto = require('crypto');
const fs = require('fs');
const yaml = require('js-yaml');

/**
 * API Hook 核心類別
 */
class APIHook {
  /**
   * 初始化 API Hook
   * @param {Object} options - 配置選項
   * @param {string} options.configPath - 配置檔案路徑
   */
  constructor(options = {}) {
    this.config = this._loadConfig(options.configPath || 'config.yaml');
    this.sensitiveFields = this.config.security?.sensitive_fields || [];
    this.logs = [];
    console.log('API Hook initialized');
  }

  /**
   * 載入配置檔案
   * @private
   */
  _loadConfig(configPath) {
    try {
      // 簡化實作：實際應從 YAML 檔案載入
      return {
        security: {
          sensitive_fields: ['password', 'api_key', 'token', 'secret'],
          encrypt_sensitive_data: true,
          hash_algorithm: 'SHA256'
        },
        logging: {
          level: 'INFO',
          storage: 'database'
        },
        performance: {
          async_processing: true
        }
      };
    } catch (error) {
      console.error('Failed to load config:', error);
      return {};
    }
  }

  /**
   * 清理敏感資料
   * @private
   */
  _sanitizeData(data) {
    if (!data || typeof data !== 'object') return data;

    const sanitized = { ...data };

    this.sensitiveFields.forEach(field => {
      if (sanitized[field]) {
        const value = String(sanitized[field]);
        const hash = crypto
          .createHash('sha256')
          .update(value)
          .digest('hex')
          .substring(0, 16);
        sanitized[field] = `[REDACTED:${hash}]`;
      }
    });

    return sanitized;
  }

  /**
   * 創建日誌條目
   * @private
   */
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
      security_context: {
        authentication_method: options.authMethod || 'OAuth2',
        authorization_level: options.authLevel || 'User',
        session_id: options.sessionId || options.requestId
      },
      result: options.result,
      error_message: options.errorMessage || null
    };
  }

  /**
   * 儲存日誌
   * @private
   */
  _saveLog(logEntry) {
    console.log('API Log:', JSON.stringify(logEntry));
    this.logs.push(logEntry);

    // 實際實作範例：
    // if (this.config.logging.storage === 'database') {
    //   await this.db.insert('api_logs', logEntry);
    // } else if (this.config.logging.storage === 'elasticsearch') {
    //   await this.es.index('api-logs', logEntry);
    // }
  }

  /**
   * 檢查異常行為
   * @private
   */
  _checkAnomalies(logEntry) {
    // 檢查回應時間
    if (logEntry.response_time_ms > 5000) {
      this._triggerAlert(
        'Slow Response Time',
        `API ${logEntry.endpoint} took ${logEntry.response_time_ms}ms`,
        'WARNING'
      );
    }

    // 檢查錯誤
    if (logEntry.result === 'error') {
      this._triggerAlert(
        'API Error',
        `API ${logEntry.endpoint} failed: ${logEntry.error_message}`,
        'ERROR'
      );
    }

    // 檢查未授權存取
    if (logEntry.response_code === 401) {
      this._triggerAlert(
        'Unauthorized Access',
        `Unauthorized access attempt from ${logEntry.source_ip}`,
        'CRITICAL'
      );
    }
  }

  /**
   * 觸發警報
   * @private
   */
  _triggerAlert(alertName, message, severity) {
    const alert = {
      timestamp: new Date().toISOString(),
      alert_name: alertName,
      message: message,
      severity: severity
    };

    console.warn('ALERT:', JSON.stringify(alert));

    // 實際實作：發送到警報系統
    // await this._sendWebhook(alert);
    // await this._sendEmail(alert);
  }

  /**
   * Express.js 中介軟體
   * 自動監控所有 HTTP 請求
   */
  middleware(options = {}) {
    const {
      logRequests = true,
      validateAuth = false,
      trackPerformance = true
    } = options;

    return (req, res, next) => {
      const startTime = Date.now();
      const requestId = crypto.randomUUID();

      // 儲存原始的 res.json 方法
      const originalJson = res.json.bind(res);

      // 覆寫 res.json 以攔截回應
      res.json = (body) => {
        const responseTimeMs = Date.now() - startTime;

        if (logRequests) {
          const logEntry = this._createLogEntry({
            requestId: requestId,
            userId: req.user?.id || req.session?.userId,
            sourceIp: req.ip || req.connection.remoteAddress,
            method: req.method,
            endpoint: req.path,
            parameters: {
              query: req.query,
              body: req.body,
              params: req.params
            },
            responseCode: res.statusCode,
            responseTimeMs: responseTimeMs,
            result: res.statusCode < 400 ? 'success' : 'error',
            errorMessage: body.error || null,
            authMethod: req.authMethod,
            authLevel: req.user?.role,
            sessionId: req.sessionID
          });

          this._saveLog(logEntry);
          this._checkAnomalies(logEntry);
        }

        // 呼叫原始的 json 方法
        return originalJson(body);
      };

      next();
    };
  }

  /**
   * 端點保護裝飾器
   * 為特定端點添加額外的監控與驗證
   */
  protect(options = {}) {
    const { level = 'medium', logBody = true } = options;

    return (req, res, next) => {
      // 添加額外的安全檢查
      if (level === 'critical' || level === 'high') {
        // 檢查速率限制
        // 驗證 token
        // 記錄詳細資訊
      }

      // 標記此端點的安全等級
      req.securityLevel = level;
      req.logBody = logBody;

      next();
    };
  }

  /**
   * 手動記錄事件
   */
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

    // 如果是嚴重事件，觸發警報
    if (severity === 'error' || severity === 'critical') {
      this._triggerAlert(
        eventType.charAt(0).toUpperCase() + eventType.slice(1),
        message,
        severity.toUpperCase()
      );
    }
  }

  /**
   * 取得統計資訊
   */
  getStats() {
    const stats = {
      total_logs: this.logs.length,
      success_count: this.logs.filter(l => l.result === 'success').length,
      error_count: this.logs.filter(l => l.result === 'error').length,
      avg_response_time: 0
    };

    if (this.logs.length > 0) {
      const totalTime = this.logs.reduce((sum, log) => sum + (log.response_time_ms || 0), 0);
      stats.avg_response_time = Math.round(totalTime / this.logs.length * 100) / 100;
    }

    return stats;
  }
}

// 使用範例
if (require.main === module) {
  const express = require('express');
  const app = express();

  // 初始化 API Hook
  const hook = new APIHook({
    configPath: 'config.yaml'
  });

  // 使用中介軟體
  app.use(express.json());
  app.use(hook.middleware({
    logRequests: true,
    validateAuth: true,
    trackPerformance: true
  }));

  // 範例端點 1：一般 API
  app.get('/api/v1/users', (req, res) => {
    res.json({
      status: 'success',
      users: [
        { id: 1, name: 'John Doe' },
        { id: 2, name: 'Jane Smith' }
      ]
    });
  });

  // 範例端點 2：受保護的高安全性 API
  app.post('/api/v1/users', hook.protect({ level: 'high' }), (req, res) => {
    const { username, email } = req.body;

    // 模擬創建使用者
    console.log(`Creating user: ${username}`);

    res.json({
      status: 'success',
      user_id: '12345',
      username: username,
      email: email
    });
  });

  // 範例端點 3：認證 API（關鍵安全性）
  app.post('/api/v1/auth/login', hook.protect({ level: 'critical' }), (req, res) => {
    const { username, password } = req.body;

    // 模擬認證 - TEST DATA ONLY
    if (password === 'test_wrong_password') {  // TEST DATA
      return res.status(401).json({
        status: 'error',
        error: 'Invalid credentials'
      });
    }

    res.json({
      status: 'success',
      token: 'example-jwt-token-placeholder'  // TEST DATA - Not a real JWT
    });
  });

  // 範例端點 4：觸發錯誤
  app.get('/api/v1/error', (req, res) => {
    res.status(500).json({
      status: 'error',
      error: 'Internal server error'
    });
  });

  // 統計端點
  app.get('/api/stats', (req, res) => {
    res.json(hook.getStats());
  });

  // 啟動伺服器
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    console.log(`\n=== API Hook Demo Server ===`);
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`\nTest endpoints:`);
    console.log(`  GET  http://localhost:${PORT}/api/v1/users`);
    console.log(`  POST http://localhost:${PORT}/api/v1/users`);
    console.log(`  POST http://localhost:${PORT}/api/v1/auth/login`);
    console.log(`  GET  http://localhost:${PORT}/api/v1/error`);
    console.log(`  GET  http://localhost:${PORT}/api/stats`);
    console.log(`\n測試指令範例：`);
    console.log(`  curl http://localhost:${PORT}/api/v1/users`);
    console.log(`  curl -X POST http://localhost:${PORT}/api/v1/users -H "Content-Type: application/json" -d '{"username":"john","email":"john@example.com"}'`);
  });

  // 測試手動事件記錄
  setTimeout(() => {
    console.log('\n=== 測試手動事件記錄 ===');
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
  }, 2000);
}

module.exports = APIHook;
