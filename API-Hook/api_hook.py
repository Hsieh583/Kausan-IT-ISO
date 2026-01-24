"""
API Hook Implementation - Python Example
用於監控與記錄 API 呼叫的 Python 實作範例
"""

import json
import time
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from functools import wraps
import uuid

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('api_hook')


class APIHook:
    """
    API Hook 核心類別
    提供 API 呼叫攔截、記錄與監控功能
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化 API Hook
        
        Args:
            config_path: 配置檔案路徑
        """
        self.config = self._load_config(config_path)
        self.sensitive_fields = self.config.get('security', {}).get('sensitive_fields', [])
        logger.info("API Hook initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """載入配置檔案"""
        # 簡化實作：實際應從 YAML 檔案載入
        return {
            'security': {
                'sensitive_fields': ['password', 'api_key', 'token', 'secret'],
                'encrypt_sensitive_data': True,
                'hash_algorithm': 'SHA256'
            },
            'logging': {
                'level': 'INFO',
                'storage': 'database'
            },
            'performance': {
                'async_processing': True
            }
        }
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理敏感資料
        將敏感欄位替換為雜湊值或遮罩
        
        Args:
            data: 原始資料
            
        Returns:
            清理後的資料
        """
        sanitized = data.copy()
        
        for field in self.sensitive_fields:
            if field in sanitized:
                # 使用雜湊值替代敏感資料
                value = str(sanitized[field])
                hash_value = hashlib.sha256(value.encode()).hexdigest()[:16]
                sanitized[field] = f"[REDACTED:{hash_value}]"
        
        return sanitized
    
    def _create_log_entry(
        self,
        request_id: str,
        user_id: str,
        source_ip: str,
        method: str,
        endpoint: str,
        parameters: Dict[str, Any],
        response_code: int,
        response_time_ms: float,
        result: str,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        創建日誌條目
        
        Returns:
            格式化的日誌條目
        """
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'request_id': request_id,
            'user_id': user_id,
            'source_ip': source_ip,
            'method': method,
            'endpoint': endpoint,
            'parameters': self._sanitize_data(parameters),
            'response_code': response_code,
            'response_time_ms': round(response_time_ms, 2),
            'security_context': {
                'authentication_method': 'OAuth2',
                'authorization_level': 'User',
                'session_id': request_id
            },
            'result': result,
            'error_message': error_message
        }
    
    def _save_log(self, log_entry: Dict[str, Any]):
        """
        儲存日誌
        實際實作應根據配置寫入資料庫、檔案或 Elasticsearch
        
        Args:
            log_entry: 日誌條目
        """
        # 簡化實作：僅輸出到標準輸出
        logger.info(f"API Log: {json.dumps(log_entry, ensure_ascii=False)}")
        
        # 實際實作範例：
        # if self.config['logging']['storage'] == 'database':
        #     self.db.insert('api_logs', log_entry)
        # elif self.config['logging']['storage'] == 'elasticsearch':
        #     self.es.index('api-logs', log_entry)
    
    def monitor(
        self,
        endpoint: str,
        security_level: str = "medium",
        log_params: bool = True,
        log_response: bool = False
    ) -> Callable:
        """
        裝飾器：監控 API 端點
        
        Args:
            endpoint: API 端點路徑
            security_level: 安全等級 (low, medium, high, critical)
            log_params: 是否記錄參數
            log_response: 是否記錄回應內容
            
        Returns:
            裝飾器函數
            
        Example:
            @hook.monitor(endpoint="/api/v1/users", security_level="high")
            def create_user(request):
                return {"status": "success"}
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                request_id = str(uuid.uuid4())
                start_time = time.time()
                
                # 提取請求資訊（簡化，實際應從框架中提取）
                user_id = kwargs.get('user_id', 'anonymous')
                source_ip = kwargs.get('source_ip', '0.0.0.0')
                method = kwargs.get('method', 'GET')
                parameters = kwargs if log_params else {}
                
                try:
                    # 執行原始函數
                    result = func(*args, **kwargs)
                    response_code = 200
                    status = 'success'
                    error_message = None
                    
                except Exception as e:
                    result = {'error': str(e)}
                    response_code = 500
                    status = 'error'
                    error_message = str(e)
                    logger.error(f"API Error: {endpoint} - {str(e)}")
                    raise
                
                finally:
                    # 計算執行時間
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    # 創建並儲存日誌
                    log_entry = self._create_log_entry(
                        request_id=request_id,
                        user_id=user_id,
                        source_ip=source_ip,
                        method=method,
                        endpoint=endpoint,
                        parameters=parameters,
                        response_code=response_code,
                        response_time_ms=response_time_ms,
                        result=status,
                        error_message=error_message
                    )
                    
                    self._save_log(log_entry)
                    
                    # 檢查異常行為
                    self._check_anomalies(log_entry)
                
                return result
            
            return wrapper
        return decorator
    
    def _check_anomalies(self, log_entry: Dict[str, Any]):
        """
        檢查異常行為
        
        Args:
            log_entry: 日誌條目
        """
        # 檢查回應時間
        if log_entry['response_time_ms'] > 5000:
            self._trigger_alert(
                'Slow Response Time',
                f"API {log_entry['endpoint']} took {log_entry['response_time_ms']}ms",
                'WARNING'
            )
        
        # 檢查錯誤
        if log_entry['result'] == 'error':
            self._trigger_alert(
                'API Error',
                f"API {log_entry['endpoint']} failed: {log_entry['error_message']}",
                'ERROR'
            )
        
        # 檢查未授權存取
        if log_entry['response_code'] == 401:
            self._trigger_alert(
                'Unauthorized Access',
                f"Unauthorized access attempt from {log_entry['source_ip']}",
                'CRITICAL'
            )
    
    def _trigger_alert(self, alert_name: str, message: str, severity: str):
        """
        觸發警報
        
        Args:
            alert_name: 警報名稱
            message: 警報訊息
            severity: 嚴重程度
        """
        alert = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'alert_name': alert_name,
            'message': message,
            'severity': severity
        }
        
        logger.warning(f"ALERT: {json.dumps(alert, ensure_ascii=False)}")
        
        # 實際實作：發送到警報系統、Email、Webhook 等
        # self._send_webhook(alert)
        # self._send_email(alert)
    
    def log_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        手動記錄事件
        
        Args:
            event_type: 事件類型 (security, performance, audit, etc.)
            severity: 嚴重程度 (info, warning, error, critical)
            message: 事件訊息
            metadata: 額外的元資料
            
        Example:
            hook.log_event(
                event_type="security",
                severity="critical",
                message="Brute force attack detected",
                metadata={"ip": "192.168.1.100", "attempts": 10}
            )
        """
        event = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'severity': severity,
            'message': message,
            'metadata': metadata or {}
        }
        
        logger.info(f"Event: {json.dumps(event, ensure_ascii=False)}")
        
        # 儲存事件
        self._save_log(event)
        
        # 如果是嚴重事件，觸發警報
        if severity in ['error', 'critical']:
            self._trigger_alert(event_type.title(), message, severity.upper())


# 使用範例
if __name__ == '__main__':
    # 初始化 API Hook
    hook = APIHook(config_path="config.yaml")
    
    # 範例 1：使用裝飾器監控 API 函數
    @hook.monitor(
        endpoint="/api/v1/users",
        security_level="high",
        log_params=True
    )
    def create_user(user_id: str, username: str, password: str, **kwargs):
        """創建使用者"""
        # 模擬 API 邏輯
        print(f"Creating user: {username}")
        return {
            'status': 'success',
            'user_id': '12345',
            'username': username
        }
    
    # 範例 2：使用裝飾器監控認證 API
    @hook.monitor(
        endpoint="/api/v1/auth/login",
        security_level="critical",
        log_params=True
    )
    def login(user_id: str, username: str, password: str, **kwargs):
        """使用者登入"""
        print(f"User login: {username}")
        if password == "wrong":
            raise Exception("Invalid credentials")
        return {
            'status': 'success',
            'token': 'jwt-token-here'
        }
    
    # 測試 API 呼叫
    print("\n=== 測試 1: 成功的 API 呼叫 ===")
    result = create_user(
        user_id='user123',
        username='john_doe',
        password='secure_password',
        source_ip='192.168.1.100',
        method='POST'
    )
    print(f"Result: {result}\n")
    
    # 測試失敗的 API 呼叫
    print("=== 測試 2: 失敗的 API 呼叫 ===")
    try:
        result = login(
            user_id='user456',
            username='jane_doe',
            password='wrong',
            source_ip='192.168.1.101',
            method='POST'
        )
    except Exception as e:
        print(f"Error caught: {e}\n")
    
    # 測試手動事件記錄
    print("=== 測試 3: 手動記錄安全事件 ===")
    hook.log_event(
        event_type="security",
        severity="critical",
        message="Suspicious login pattern detected",
        metadata={
            "ip": "192.168.1.100",
            "attempts": 10,
            "user": "admin"
        }
    )
    
    print("\n=== API Hook 測試完成 ===")
