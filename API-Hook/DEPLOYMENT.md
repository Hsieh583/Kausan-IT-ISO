# API Hook 部署指南

> 本指南說明如何在生產環境中部署 API Hook 監控框架

---

## 一、部署前準備

### 系統需求確認

```bash
# 檢查作業系統版本
cat /etc/os-release

# 檢查可用記憶體
free -h

# 檢查磁碟空間
df -h
```

**最低需求**：
- CPU: 2 核心
- RAM: 4GB
- 磁碟: 100GB（日誌儲存）
- 網路: 1Gbps

---

## 二、環境設定

### 2.1 Python 環境（適用於 Python 實作）

```bash
# 安裝 Python 3.9+
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 建立虛擬環境
cd /opt/api-hook
python3 -m venv venv
source venv/bin/activate

# 安裝依賴套件
pip install pyyaml psycopg2-binary pymongo cryptography prometheus-client
```

### 2.2 Node.js 環境（適用於 Node.js 實作）

```bash
# 安裝 Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安裝依賴套件
cd /opt/api-hook
npm install express js-yaml pg mongodb crypto uuid
```

### 2.3 資料庫設定（PostgreSQL）

```bash
# 安裝 PostgreSQL
sudo apt install postgresql postgresql-contrib

# 啟動服務
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 建立資料庫與使用者
sudo -u postgres psql
```

```sql
-- 在 psql 中執行
CREATE DATABASE api_logs;
CREATE USER api_logger WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE api_logs TO api_logger;

-- 建立日誌表
\c api_logs
CREATE TABLE api_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    request_id UUID NOT NULL,
    user_id VARCHAR(255),
    source_ip INET,
    method VARCHAR(10),
    endpoint VARCHAR(500),
    parameters JSONB,
    response_code INTEGER,
    response_time_ms NUMERIC(10,2),
    security_context JSONB,
    result VARCHAR(50),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 建立索引以加速查詢
CREATE INDEX idx_timestamp ON api_log(timestamp DESC);
CREATE INDEX idx_user_id ON api_log(user_id);
CREATE INDEX idx_endpoint ON api_log(endpoint);
CREATE INDEX idx_source_ip ON api_log(source_ip);
CREATE INDEX idx_result ON api_log(result);

-- 建立分區表（按月份）
CREATE TABLE api_log_2026_01 PARTITION OF api_log
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- 自動建立未來分區的函數（建議設定每月執行）
CREATE OR REPLACE FUNCTION create_monthly_partitions()
RETURNS void AS $$
DECLARE
    start_date DATE;
    end_date DATE;
    partition_name TEXT;
BEGIN
    -- 為未來 3 個月建立分區
    FOR i IN 0..2 LOOP
        start_date := DATE_TRUNC('month', CURRENT_DATE + (i || ' month')::INTERVAL);
        end_date := start_date + INTERVAL '1 month';
        partition_name := 'api_log_' || TO_CHAR(start_date, 'YYYY_MM');
        
        IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = partition_name) THEN
            EXECUTE format('CREATE TABLE %I PARTITION OF api_log FOR VALUES FROM (%L) TO (%L)',
                          partition_name, start_date, end_date);
            RAISE NOTICE 'Created partition: %', partition_name;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 執行一次以建立初始分區
SELECT create_monthly_partitions();

-- 設定權限
GRANT SELECT, INSERT ON api_log TO api_logger;
GRANT USAGE, SELECT ON SEQUENCE api_log_id_seq TO api_logger;
```

---

## 三、配置檔案設定

### 3.1 複製範例配置

```bash
cd /opt/api-hook
cp config.example.yaml config.yaml
chmod 600 config.yaml  # 限制權限
```

### 3.2 編輯配置檔案

```bash
vi config.yaml
```

**關鍵設定項目**：

```yaml
api_hook:
  mode: "production"
  
  logging:
    storage: "database"
    database:
      type: "postgresql"
      host: "localhost"
      port: 5432
      database: "api_logs"
      username: "api_logger"
      password: "${DB_PASSWORD}"  # 從環境變數讀取
  
  security:
    authentication_required: true
    encrypt_sensitive_data: true
    
  monitoring:
    alerting:
      enabled: true
      webhook_url: "https://alerts.example.com/webhook"
      email_recipients:
        - "security@example.com"
```

### 3.3 設定環境變數

```bash
# 建立環境變數檔案
vi /opt/api-hook/.env
```

```bash
# .env 內容
DB_PASSWORD=your_secure_password
ES_PASSWORD=elasticsearch_password
WEBHOOK_SECRET=webhook_secret_key
```

```bash
# 限制權限
chmod 600 /opt/api-hook/.env

# 載入環境變數
source /opt/api-hook/.env
```

---

## 四、應用程式整合

### 4.1 Python 應用程式整合

```python
# app.py
from flask import Flask, request, jsonify
from api_hook import APIHook
import os

app = Flask(__name__)

# 初始化 API Hook
hook = APIHook(config_path="/opt/api-hook/config.yaml")

@app.before_request
def log_request():
    # 記錄請求開始
    request.start_time = time.time()

@app.after_request
def log_response(response):
    # 記錄請求結束
    response_time = (time.time() - request.start_time) * 1000
    
    hook._save_log(hook._create_log_entry(
        request_id=request.headers.get('X-Request-ID', str(uuid.uuid4())),
        user_id=request.headers.get('X-User-ID', 'anonymous'),
        source_ip=request.remote_addr,
        method=request.method,
        endpoint=request.path,
        parameters={'query': dict(request.args), 'body': request.get_json()},
        response_code=response.status_code,
        response_time_ms=response_time,
        result='success' if response.status_code < 400 else 'error'
    ))
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 4.2 Node.js 應用程式整合

```javascript
// server.js
const express = require('express');
const APIHook = require('./api_hook');

const app = express();
const hook = new APIHook({ configPath: '/opt/api-hook/config.yaml' });

// 使用 API Hook 中介軟體
app.use(express.json());
app.use(hook.middleware({
  logRequests: true,
  validateAuth: true,
  trackPerformance: true
}));

// 你的 API 路由
app.get('/api/v1/users', (req, res) => {
  res.json({ users: [] });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

---

## 五、系統服務設定

### 5.1 建立 Systemd 服務（Python）

```bash
sudo vi /etc/systemd/system/api-hook-python.service
```

```ini
[Unit]
Description=API Hook Monitoring Service (Python)
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/api-hook
Environment="PATH=/opt/api-hook/venv/bin"
EnvironmentFile=/opt/api-hook/.env
ExecStart=/opt/api-hook/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.2 建立 Systemd 服務（Node.js）

```bash
sudo vi /etc/systemd/system/api-hook-nodejs.service
```

```ini
[Unit]
Description=API Hook Monitoring Service (Node.js)
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/api-hook
EnvironmentFile=/opt/api-hook/.env
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.3 啟動服務

```bash
# 重新載入 systemd
sudo systemctl daemon-reload

# 啟動服務
sudo systemctl start api-hook-python.service
# 或
sudo systemctl start api-hook-nodejs.service

# 設定開機自動啟動
sudo systemctl enable api-hook-python.service

# 檢查服務狀態
sudo systemctl status api-hook-python.service

# 查看日誌
sudo journalctl -u api-hook-python.service -f
```

---

## 六、監控與警報設定

### 6.1 Prometheus 整合

```bash
# 安裝 Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# 編輯配置
vi prometheus.yml
```

```yaml
scrape_configs:
  - job_name: 'api-hook'
    static_configs:
      - targets: ['localhost:9090']
```

### 6.2 Grafana 儀表板

```bash
# 安裝 Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# 啟動 Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

訪問 `http://localhost:3000`（預設帳密：admin/admin）

建立儀表板監控以下指標：
- API 呼叫量（每分鐘）
- 錯誤率
- 平均回應時間
- 慢查詢警報

---

## 七、備份與災難復原

### 7.1 資料庫備份

```bash
# 建立備份腳本
vi /opt/api-hook/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/api-hook"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 備份資料庫
pg_dump -U api_logger -h localhost api_logs | gzip > $BACKUP_DIR/api_logs_$DATE.sql.gz

# 保留最近 30 天的備份
find $BACKUP_DIR -name "api_logs_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
# 設定執行權限
chmod +x /opt/api-hook/backup.sh

# 建立 cron 工作（每日備份）
crontab -e
```

```cron
0 2 * * * /opt/api-hook/backup.sh >> /var/log/api-hook-backup.log 2>&1
```

### 7.2 災難復原

```bash
# 還原資料庫
gunzip < /var/backups/api-hook/api_logs_YYYYMMDD.sql.gz | psql -U api_logger -h localhost api_logs
```

---

## 八、安全強化

### 8.1 防火牆設定

```bash
# 僅允許必要的連接埠
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 5432/tcp  # PostgreSQL（僅內部網路）
sudo ufw allow 9090/tcp  # Prometheus metrics
sudo ufw enable
```

### 8.2 SSL/TLS 設定

```bash
# 產生自簽憑證（測試用）
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# 或使用 Let's Encrypt（生產環境）
sudo apt install certbot
sudo certbot certonly --standalone -d api-hook.example.com
```

### 8.3 檔案權限

```bash
# 設定正確的檔案權限
sudo chown -R www-data:www-data /opt/api-hook
sudo chmod 750 /opt/api-hook
sudo chmod 600 /opt/api-hook/config.yaml
sudo chmod 600 /opt/api-hook/.env
```

---

## 九、效能調校

### 9.1 PostgreSQL 調校

```bash
sudo vi /etc/postgresql/14/main/postgresql.conf
```

```conf
# 記憶體設定
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB

# 連接設定
max_connections = 100

# 日誌設定
log_min_duration_statement = 1000  # 記錄慢查詢（>1秒）
```

```bash
sudo systemctl restart postgresql
```

### 9.2 應用程式調校

- 啟用非同步處理（`async_processing: true`）
- 調整批次插入大小（`batch_insert_size: 100`）
- 使用連接池（`pool_size: 20`）
- 啟用快取機制（`cache.enabled: true`）

---

## 十、驗證部署

### 10.1 健康檢查

```bash
# 檢查服務狀態
sudo systemctl status api-hook-python.service

# 檢查資料庫連接
psql -U api_logger -h localhost -d api_logs -c "SELECT COUNT(*) FROM api_log;"

# 測試 API 端點
curl http://localhost:5000/health
```

### 10.2 功能測試

```bash
# 發送測試請求
curl -X POST http://localhost:5000/api/v1/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# 檢查日誌是否已記錄
psql -U api_logger -h localhost -d api_logs -c "SELECT * FROM api_log ORDER BY timestamp DESC LIMIT 5;"
```

### 10.3 效能測試

```bash
# 安裝 Apache Bench
sudo apt install apache2-utils

# 壓力測試
ab -n 1000 -c 10 http://localhost:5000/api/v1/users

# 檢查系統資源使用
htop
```

---

## 十一、維護計畫

### 每日維護

- [ ] 檢查服務狀態
- [ ] 檢查磁碟空間
- [ ] 審查重大警報
- [ ] 確認備份完成

### 每週維護

- [ ] 審查異常事件
- [ ] 更新警報規則
- [ ] 分析效能趨勢
- [ ] 測試災難復原

### 每月維護

- [ ] 產生合規報告
- [ ] 審查存取權限
- [ ] 更新系統套件
- [ ] 容量規劃評估

---

## 十二、疑難排解

### 問題 1：服務無法啟動

```bash
# 檢查日誌
sudo journalctl -u api-hook-python.service -n 50

# 常見原因：
# - 配置檔案錯誤：檢查 config.yaml 語法
# - 資料庫連接失敗：檢查 PostgreSQL 服務與憑證
# - 權限問題：檢查檔案擁有者與權限
```

### 問題 2：日誌未記錄

```bash
# 檢查資料庫連接
psql -U api_logger -h localhost -d api_logs

# 檢查表格是否存在
\dt

# 檢查權限
\dp api_log
```

### 問題 3：效能緩慢

```bash
# 檢查資料庫查詢效能
psql -U api_logger -h localhost -d api_logs
EXPLAIN ANALYZE SELECT * FROM api_log WHERE timestamp > NOW() - INTERVAL '1 day';

# 檢查索引
\di

# 重建索引
REINDEX TABLE api_log;
```

---

## 十三、聯絡資訊

**技術支援**：it-support@example.com  
**安全事件報告**：security@example.com  
**文件更新**：請提交 Pull Request

---

**維護責任**：IT 營運團隊  
**最後更新**：2026年1月24日  
**版本**：v1.0.0
