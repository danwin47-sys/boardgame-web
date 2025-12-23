"""
進階監控指標 API
提供 API 回應時間、錯誤率、請求計數等指標
"""
from flask import Blueprint, jsonify, request
import logging
import time
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)

metrics_bp = Blueprint("metrics", __name__, url_prefix="/api/metrics")

# 全域指標儲存（生產環境應使用 Redis 或資料庫）
_metrics = {
    "requests": defaultdict(int),  # 請求計數
    "errors": defaultdict(int),  # 錯誤計數
    "response_times": defaultdict(list),  # 回應時間
    "endpoints": defaultdict(lambda: {"count": 0, "errors": 0, "avg_time": 0}),
}
_metrics_lock = Lock()


def record_request(endpoint: str, method: str, status_code: int, response_time: float):
    """記錄請求指標"""
    with _metrics_lock:
        key = f"{method}:{endpoint}"
        _metrics["requests"][key] += 1
        _metrics["response_times"][key].append(response_time)

        if status_code >= 400:
            _metrics["errors"][key] += 1

        # 更新端點統計
        endpoint_stats = _metrics["endpoints"][key]
        endpoint_stats["count"] += 1
        if status_code >= 400:
            endpoint_stats["errors"] += 1

        # 計算平均回應時間（保留最近 100 筆）
        times = _metrics["response_times"][key][-100:]
        endpoint_stats["avg_time"] = sum(times) / len(times) if times else 0


@metrics_bp.route("/summary", methods=["GET"])
def get_metrics_summary():
    """獲取指標摘要"""
    try:
        with _metrics_lock:
            total_requests = sum(_metrics["requests"].values())
            total_errors = sum(_metrics["errors"].values())
            error_rate = (
                (total_errors / total_requests * 100) if total_requests > 0 else 0
            )

            # 計算整體平均回應時間
            all_times = []
            for times in _metrics["response_times"].values():
                all_times.extend(times[-100:])
            avg_response_time = sum(all_times) / len(all_times) if all_times else 0

            summary = {
                "success": True,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": round(error_rate, 2),
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "timestamp": datetime.now().isoformat(),
            }

        return jsonify(summary)
    except Exception as e:
        logger.error(f"獲取指標摘要失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@metrics_bp.route("/endpoints", methods=["GET"])
def get_endpoint_metrics():
    """獲取各端點的詳細指標"""
    try:
        with _metrics_lock:
            endpoints_data = []

            for endpoint, stats in _metrics["endpoints"].items():
                if stats["count"] > 0:
                    error_rate = (
                        (stats["errors"] / stats["count"] * 100)
                        if stats["count"] > 0
                        else 0
                    )

                    endpoints_data.append(
                        {
                            "endpoint": endpoint,
                            "total_requests": stats["count"],
                            "errors": stats["errors"],
                            "error_rate": round(error_rate, 2),
                            "avg_response_time_ms": round(stats["avg_time"] * 1000, 2),
                        }
                    )

            # 按請求數排序
            endpoints_data.sort(key=lambda x: x["total_requests"], reverse=True)

        return jsonify(
            {
                "success": True,
                "endpoints": endpoints_data[:20],  # 只返回前 20 個
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"獲取端點指標失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@metrics_bp.route("/response-times", methods=["GET"])
def get_response_times():
    """獲取回應時間分布"""
    try:
        with _metrics_lock:
            all_times = []
            for times in _metrics["response_times"].values():
                all_times.extend(times[-100:])

            if not all_times:
                return jsonify({"success": True, "message": "尚無資料", "stats": {}})

            all_times.sort()
            count = len(all_times)

            stats = {
                "min_ms": round(min(all_times) * 1000, 2),
                "max_ms": round(max(all_times) * 1000, 2),
                "avg_ms": round(sum(all_times) / count * 1000, 2),
                "median_ms": round(all_times[count // 2] * 1000, 2),
                "p95_ms": round(all_times[int(count * 0.95)] * 1000, 2),
                "p99_ms": round(all_times[int(count * 0.99)] * 1000, 2),
                "sample_size": count,
            }

        return jsonify(
            {"success": True, "stats": stats, "timestamp": datetime.now().isoformat()}
        )
    except Exception as e:
        logger.error(f"獲取回應時間失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@metrics_bp.route("/reset", methods=["POST"])
def reset_metrics():
    """重置所有指標（僅供開發/測試使用）"""
    try:
        with _metrics_lock:
            _metrics["requests"].clear()
            _metrics["errors"].clear()
            _metrics["response_times"].clear()
            _metrics["endpoints"].clear()

        return jsonify(
            {
                "success": True,
                "message": "指標已重置",
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"重置指標失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# 中介軟體：自動記錄所有請求
def setup_metrics_middleware(app):
    """設置指標收集中介軟體"""

    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        # 跳過靜態文件請求，避免干擾 Flask 靜態文件服務
        if (request.path.startswith("/css/") or 
            request.path.startswith("/js/") or
            request.path.startswith("/images/") or
            request.path.startswith("/static/")):
            return response
            
        if hasattr(request, "start_time"):
            response_time = time.time() - request.start_time

            # 記錄指標
            endpoint = request.endpoint or "unknown"
            method = request.method
            status_code = response.status_code

            record_request(endpoint, method, status_code, response_time)

            # 添加回應時間標頭
            response.headers["X-Response-Time"] = f"{response_time * 1000:.2f}ms"

        return response

    logger.info("✅ 指標收集中介軟體已啟用")
