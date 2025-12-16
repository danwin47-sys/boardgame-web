/**
 * 圖片懶加載模組
 * 使用 Intersection Observer API 實現高效能的圖片懶加載
 */

class LazyLoader {
    constructor(options = {}) {
        this.options = {
            root: options.root || null,
            rootMargin: options.rootMargin || '50px',
            threshold: options.threshold || 0.01,
            loadingClass: options.loadingClass || 'lazy-loading',
            loadedClass: options.loadedClass || 'lazy-loaded',
            errorClass: options.errorClass || 'lazy-error'
        };

        this.observer = null;
        this.init();
    }

    /**
     * 初始化 Intersection Observer
     */
    init() {
        if (!('IntersectionObserver' in window)) {
            // 不支援 Intersection Observer，直接載入所有圖片
            console.warn('Intersection Observer not supported, loading all images immediately');
            this.loadAllImages();
            return;
        }

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadImage(entry.target);
                    this.observer.unobserve(entry.target);
                }
            });
        }, this.options);

        // 觀察所有懶加載圖片
        this.observeImages();
    }

    /**
     * 觀察所有需要懶加載的圖片
     */
    observeImages() {
        const images = document.querySelectorAll('img[data-src], [data-bg]');
        images.forEach(img => {
            this.observer.observe(img);
        });
    }

    /**
     * 載入單張圖片
     */
    loadImage(element) {
        const isImg = element.tagName === 'IMG';
        const src = element.dataset.src || element.dataset.bg;

        if (!src) return;

        // 添加載入中樣式
        element.classList.add(this.options.loadingClass);

        if (isImg) {
            // 處理 <img> 標籤
            const img = new Image();

            img.onload = () => {
                element.src = src;
                element.classList.remove(this.options.loadingClass);
                element.classList.add(this.options.loadedClass);
                element.removeAttribute('data-src');
            };

            img.onerror = () => {
                element.classList.remove(this.options.loadingClass);
                element.classList.add(this.options.errorClass);
                // 設定預設圖片
                element.src = '/images/placeholder.png';
                element.alt = '圖片載入失敗';
            };

            img.src = src;
        } else {
            // 處理背景圖片
            const img = new Image();

            img.onload = () => {
                element.style.backgroundImage = `url('${src}')`;
                element.classList.remove(this.options.loadingClass);
                element.classList.add(this.options.loadedClass);
                element.removeAttribute('data-bg');
            };

            img.onerror = () => {
                element.classList.remove(this.options.loadingClass);
                element.classList.add(this.options.errorClass);
            };

            img.src = src;
        }
    }

    /**
     * 載入所有圖片（降級方案）
     */
    loadAllImages() {
        const images = document.querySelectorAll('img[data-src], [data-bg]');
        images.forEach(img => this.loadImage(img));
    }

    /**
     * 手動觀察新增的圖片
     */
    observe(element) {
        if (this.observer) {
            this.observer.observe(element);
        } else {
            this.loadImage(element);
        }
    }

    /**
     * 停止觀察
     */
    disconnect() {
        if (this.observer) {
            this.observer.disconnect();
        }
    }
}

// 全域實例
let lazyLoader = null;

/**
 * 初始化懶加載
 */
function initLazyLoad() {
    lazyLoader = new LazyLoader({
        rootMargin: '100px', // 提前 100px 開始載入
        threshold: 0.01
    });
}

/**
 * 為動態新增的圖片啟用懶加載
 */
function lazyLoadImage(element) {
    if (lazyLoader) {
        lazyLoader.observe(element);
    }
}

// 頁面載入時初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLazyLoad);
} else {
    initLazyLoad();
}

// 導出給其他模組使用
window.lazyLoadImage = lazyLoadImage;
