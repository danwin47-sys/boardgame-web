# coding: utf-8
"""
快取模組
提供簡單的 TTL 快取功能
"""
import time
from typing import Any, Optional


class SimpleCache:
    """
    簡單的 TTL（Time To Live）快取
    
    用於暫存需要頻繁讀取但變化不大的資料
    """
    
    def __init__(self, ttl: int):
        """
        初始化快取
        
        Args:
            ttl: 快取存活時間（秒）
        """
        self.ttl = ttl
        self._data: Optional[Any] = None
        self._timestamp: float = 0
    
    def get(self) -> Optional[Any]:
        """
        取得快取資料（若未過期）
        
        Returns:
            快取的資料，若快取過期或為空則返回 None
        """
        if self._data is not None and (time.time() - self._timestamp < self.ttl):
            return self._data
        return None
    
    def set(self, data: Any) -> None:
        """
        設置快取資料
        
        Args:
            data: 要快取的資料
        """
        self._data = data
        self._timestamp = time.time()
    
    def invalidate(self) -> None:
        """使快取失效（清空快取）"""
        self._data = None
        self._timestamp = 0
    
    def is_valid(self) -> bool:
        """
        檢查快取是否有效
        
        Returns:
            bool: 快取是否仍在有效期內
        """
        return self._data is not None and (time.time() - self._timestamp < self.ttl)
