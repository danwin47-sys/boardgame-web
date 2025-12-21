/**
 * 行動裝置手勢操作
 * 支援滑動、長按等觸控手勢
 */

class GestureHandler {
    constructor() {
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.longPressTimer = null;
        this.SWIPE_THRESHOLD = 50;
        this.LONG_PRESS_DURATION = 500;

        this.init();
    }

    /**
     * 初始化手勢處理
     */
    init() {
        // 只在觸控裝置上啟用
        if ('ontouchstart' in window) {
            this.attachEventListeners();
        }
    }

    /**
     * 附加事件監聽器
     */
    attachEventListeners() {
        document.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: true });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
    }

    /**
     * 處理觸控開始
     */
    handleTouchStart(e) {
        this.touchStartX = e.changedTouches[0].screenX;
        this.touchStartY = e.changedTouches[0].screenY;

        // 啟動長按計時器
        this.longPressTimer = setTimeout(() => {
            this.handleLongPress(e);
        }, this.LONG_PRESS_DURATION);
    }

    /**
     * 處理觸控移動
     */
    handleTouchMove(e) {
        // 取消長按
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
            this.longPressTimer = null;
        }
    }

    /**
     * 處理觸控結束
     */
    handleTouchEnd(e) {
        // 取消長按
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
            this.longPressTimer = null;
        }

        this.touchEndX = e.changedTouches[0].screenX;
        this.touchEndY = e.changedTouches[0].screenY;

        this.handleSwipe();
    }

    /**
     * 處理滑動手勢
     */
    handleSwipe() {
        const deltaX = this.touchEndX - this.touchStartX;
        const deltaY = this.touchEndY - this.touchStartY;

        // 水平滑動
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            if (Math.abs(deltaX) > this.SWIPE_THRESHOLD) {
                if (deltaX > 0) {
                    this.onSwipeRight();
                } else {
                    this.onSwipeLeft();
                }
            }
        }
        // 垂直滑動
        else {
            if (Math.abs(deltaY) > this.SWIPE_THRESHOLD) {
                if (deltaY > 0) {
                    this.onSwipeDown();
                } else {
                    this.onSwipeUp();
                }
            }
        }
    }

    /**
     * 處理長按
     */
    handleLongPress(e) {
        const target = e.target.closest('.game-card, .search-item');
        if (target) {
            // 觸發長按事件
            const event = new CustomEvent('longpress', { detail: { target } });
            target.dispatchEvent(event);

            // 觸覺反饋（如果支援）
            if (navigator.vibrate) {
                navigator.vibrate(50);
            }
        }
    }

    /**
     * 向右滑動
     */
    onSwipeRight() {
        // 可用於返回上一頁或關閉側邊欄
        console.log('Swipe right detected');
    }

    /**
     * 向左滑動
     */
    onSwipeLeft() {
        // 可用於打開側邊欄或下一頁
        console.log('Swipe left detected');
    }

    /**
     * 向上滑動
     */
    onSwipeUp() {
        // 可用於顯示更多內容
        console.log('Swipe up detected');
    }

    /**
     * 向下滑動
     */
    onSwipeDown() {
        // 可用於重新整理
        console.log('Swipe down detected');
    }
}

// 全域實例
window.gestureHandler = new GestureHandler();
