"""
測試 core/logging_config.py 模組
"""
import logging
import os
from unittest.mock import patch

import pytest

from core.logging_config import get_logger, setup_logging


class TestSetupLogging:
    """測試 setup_logging 函數"""

    def test_setup_logging_default(self):
        """測試預設設定"""
        setup_logging()
        logger = logging.getLogger("test")
        assert logger is not None

    def test_setup_logging_with_level(self):
        """測試指定日誌等級"""
        setup_logging(level="DEBUG")
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_setup_logging_with_env_variable(self):
        """測試從環境變數讀取等級"""
        with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}):
            setup_logging()
            root_logger = logging.getLogger()
            assert root_logger.level == logging.WARNING

    def test_setup_logging_simple_format(self):
        """測試簡化格式"""
        setup_logging(simple_format=True)
        # 只要不報錯就算通過
        assert True

    def test_setup_logging_clears_handlers(self):
        """測試清除既有 handlers"""
        root_logger = logging.getLogger()
        initial_handler_count = len(root_logger.handlers)
        setup_logging()
        setup_logging()  # 呼叫兩次
        # handlers 不應該重複增加
        assert len(root_logger.handlers) <= 2  # 最多 console + file


class TestGetLogger:
    """測試 get_logger 函數"""

    def test_get_logger_returns_logger(self):
        """測試返回 logger 實例"""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_same_name_returns_same_instance(self):
        """測試相同名稱返回相同實例"""
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")
        assert logger1 is logger2
