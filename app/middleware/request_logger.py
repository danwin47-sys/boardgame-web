"""
請求日誌追蹤中介軟體

為每個 HTTP 請求分配唯一的追蹤 ID，並記錄請求的開始和結束。
這使得在日誌中追蹤特定請求的完整執行路徑變得容易。
"""
import logging
import time
import uuid

from flask import g, request

logger = logging.getLogger(__name__)


def init_request_logging(app):
    """
    初始化請求日誌中介軟體

    為每個請求添加：
    - 唯一追蹤 ID (g.request_id)
    - 開始時間 (g.start_time)
    - 請求開始/結束日誌
    - 回應標頭中的追蹤 ID

    Args:
        app: Flask 應用程式實例
    """

    @app.before_request
    def before_request():
        """在處理請求前執行"""
        # 產生唯一追蹤 ID（8位元組，方便閱讀）
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.time()

        # 記錄請求開始
        logger.info(
            f"[{g.request_id}] --> {request.method} {request.path}",
            extra={
                "request_id": g.request_id,
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent", "")[:100],
            },
        )

    @app.after_request
    def after_request(response):
        """在發送回應前執行"""
        # 計算請求耗時
        duration = time.time() - g.start_time

        # 根據狀態碼決定日誌層級
        if response.status_code >= 500:
            log_level = logging.ERROR
        elif response.status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        logger.log(
            log_level,
            f"[{g.request_id}] <-- {response.status_code} ({duration*1000:.0f}ms)",
            extra={
                "request_id": g.request_id,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            },
        )

        # 在回應標頭加入追蹤 ID（方便前端除錯）
        response.headers["X-Request-ID"] = g.request_id
        return response

    @app.teardown_request
    def teardown_request(exception=None):
        """請求結束時清理（無論成功或失敗）"""
        if exception:
            request_id = getattr(g, "request_id", "unknown")
            logger.error(
                f"[{request_id}] !! 請求處理時發生未捕獲的異常",
                exc_info=True,
                extra={"request_id": request_id},
            )
