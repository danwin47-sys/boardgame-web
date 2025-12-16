/**
 * 主題切換功能
 * 支援深色/淺色模式切換
 */

class ThemeSwitcher {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.init();
    }

    /**
     * 初始化主題系統
     */
    init() {
        // 應用儲存的主題
        this.applyTheme(this.currentTheme);

        // 創建切換按鈕
        this.createToggleButton();

        // 監聽系統主題變化
        this.watchSystemTheme();
    }

    /**
     * 取得儲存的主題偏好
     */
    getStoredTheme() {
        return localStorage.getItem('theme');
    }

    /**
     * 取得系統主題偏好（預設為淺色）
     */
    getSystemTheme() {
        // 預設使用淺色模式
        return 'light';
    }

    /**
     * 應用主題
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);

        // 更新按鈕圖示
        this.updateToggleIcon();
    }

    /**
     * 切換主題
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    /**
     * 創建切換按鈕
     */
    createToggleButton() {
        const button = document.createElement('button');
        button.className = 'theme-toggle';
        button.setAttribute('aria-label', 'Toggle theme');
        button.innerHTML = '<span class="theme-toggle-icon">🌙</span>';

        button.addEventListener('click', () => this.toggleTheme());

        document.body.appendChild(button);
        this.toggleButton = button;

        // 初始化圖示
        this.updateToggleIcon();
    }

    /**
     * 更新切換按鈕圖示
     */
    updateToggleIcon() {
        if (this.toggleButton) {
            const icon = this.currentTheme === 'light' ? '🌙' : '☀️';
            this.toggleButton.querySelector('.theme-toggle-icon').textContent = icon;
        }
    }

    /**
     * 監聽系統主題變化
     */
    watchSystemTheme() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', (e) => {
                // 只有在沒有手動設定時才跟隨系統
                if (!localStorage.getItem('theme')) {
                    const newTheme = e.matches ? 'dark' : 'light';
                    this.applyTheme(newTheme);
                }
            });
        }
    }
}

// 頁面載入時初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeSwitcher = new ThemeSwitcher();
    });
} else {
    window.themeSwitcher = new ThemeSwitcher();
}
