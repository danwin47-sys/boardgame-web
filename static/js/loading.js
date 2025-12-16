/**
 * 載入狀態管理
 */

class LoadingManager {
    constructor() {
        this.overlay = null;
        this.init();
    }

    /**
     * 初始化載入覆蓋層
     */
    init() {
        // 創建載入覆蓋層
        this.overlay = document.createElement('div');
        this.overlay.className = 'loading-overlay';
        this.overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(this.overlay);
    }

    /**
     * 顯示載入指示器
     */
    show() {
        if (this.overlay) {
            this.overlay.classList.add('show');
        }
    }

    /**
     * 隱藏載入指示器
     */
    hide() {
        if (this.overlay) {
            this.overlay.classList.remove('show');
        }
    }
}

// 全域實例
window.loadingManager = new LoadingManager();

/**
 * 便利函數
 */
function showLoading() {
    window.loadingManager.show();
}

function hideLoading() {
    window.loadingManager.hide();
}

// 導出給其他模組使用
window.showLoading = showLoading;
window.hideLoading = hideLoading;
