/**
 * Phase 2 & 3: 進階互動功能
 */

// 篩選面板切換
// 篩選面板切換
function initFilterPanel() {
    if (!isMobileDevice()) return;

    // 防止重複創建
    if (document.querySelector('.filter-panel-toggle')) return;

    const filterButtons = document.querySelector('.filter-buttons');
    if (!filterButtons) return;

    // 創建切換按鈕
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'filter-panel-toggle';
    toggleBtn.innerHTML = `
        <span>篩選選項</span>
        <span class="icon">▼</span>
    `;

    // 插入到篩選按鈕前面
    filterButtons.parentNode.insertBefore(toggleBtn, filterButtons);

    // 預設收起
    filterButtons.classList.remove('show');

    // 點擊切換
    toggleBtn.addEventListener('click', () => {
        filterButtons.classList.toggle('show');
        toggleBtn.classList.toggle('active');
    });
}

// 下拉刷新功能
let pullStartY = 0;
let pullMoveY = 0;
let isPulling = false;

function initPullToRefresh() {
    if (!isMobileDevice()) return;

    const pullIndicator = document.createElement('div');
    pullIndicator.className = 'pull-to-refresh';
    pullIndicator.innerHTML = '<div class="pull-to-refresh-icon"></div>';
    document.body.prepend(pullIndicator);

    let startY = 0;
    let currentY = 0;

    document.addEventListener('touchstart', (e) => {
        if (window.scrollY === 0) {
            startY = e.touches[0].pageY;
        }
    }, { passive: true });

    document.addEventListener('touchmove', (e) => {
        if (window.scrollY === 0 && startY > 0) {
            currentY = e.touches[0].pageY;
            const diff = currentY - startY;

            if (diff > 0 && diff < 100) {
                pullIndicator.style.top = `${diff - 60}px`;
            } else if (diff >= 100) {
                pullIndicator.classList.add('show');
            }
        }
    }, { passive: true });

    document.addEventListener('touchend', () => {
        if (pullIndicator.classList.contains('show')) {
            // 觸發刷新
            location.reload();
        }
        pullIndicator.style.top = '-60px';
        pullIndicator.classList.remove('show');
        startY = 0;
    });
}

// 平滑滾動到頂部
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// 顯示「回到頂部」按鈕
function initScrollToTop() {
    if (!isMobileDevice()) return;

    const btn = document.createElement('button');
    btn.className = 'scroll-to-top-btn';
    btn.innerHTML = '↑';
    btn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-size: 24px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
        z-index: 999;
    `;

    document.body.appendChild(btn);

    // 監聽滾動
    let scrollTimer;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimer);

        if (window.scrollY > 300) {
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
        } else {
            btn.style.opacity = '0';
            btn.style.pointerEvents = 'none';
        }
    });

    btn.addEventListener('click', scrollToTop);
}

// 觸控手勢支援
function initTouchGestures() {
    if (!isMobileDevice()) return;

    let touchStartX = 0;
    let touchStartY = 0;

    document.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
    }, { passive: true });

    document.addEventListener('touchend', (e) => {
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;

        const diffX = touchEndX - touchStartX;
        const diffY = touchEndY - touchStartY;

        // 左右滑動切換頁面（如果有分頁）
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 100) {
            if (diffX > 0) {
                // 向右滑動 - 上一頁
                const prevBtn = document.querySelector('.page-btn[onclick*="changePage"][onclick*="-1"]');
                if (prevBtn && !prevBtn.disabled) {
                    prevBtn.click();
                }
            } else {
                // 向左滑動 - 下一頁
                const nextBtn = document.querySelector('.page-btn[onclick*="changePage"][onclick*="1"]');
                if (nextBtn && !nextBtn.disabled) {
                    nextBtn.click();
                }
            }
        }
    }, { passive: true });
}

// 虛擬鍵盤處理
function handleVirtualKeyboard() {
    if (!isMobileDevice()) return;

    const searchBox = document.getElementById('searchBox');
    if (!searchBox) return;

    searchBox.addEventListener('focus', () => {
        // 滾動到搜尋框
        setTimeout(() => {
            searchBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    });

    searchBox.addEventListener('blur', () => {
        // 恢復滾動
        window.scrollTo(0, 0);
    });
}

// 卡片長按選單
function initCardLongPress() {
    if (!isMobileDevice()) return;

    let pressTimer;

    document.addEventListener('touchstart', (e) => {
        const card = e.target.closest('.game-card');
        if (!card) return;

        pressTimer = setTimeout(() => {
            // 顯示選單
            showCardContextMenu(card, e.touches[0].clientX, e.touches[0].clientY);
        }, 500);
    }, { passive: true });

    document.addEventListener('touchend', () => {
        clearTimeout(pressTimer);
    });

    document.addEventListener('touchmove', () => {
        clearTimeout(pressTimer);
    });
}

function showCardContextMenu(card, x, y) {
    // 實現長按選單功能
    const gameName = card.querySelector('.game-card-title').textContent;

    // 震動反饋
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }

    // 顯示選項（複製、分享等）
    console.log('Long press on:', gameName);
}

// 初始化所有進階功能
function initMobileAdvancedFeatures() {
    if (!isMobileDevice()) return;

    initFilterPanel();
    initScrollToTop();
    initTouchGestures();
    handleVirtualKeyboard();
    initCardLongPress();

    // 可選：下拉刷新（可能干擾正常滾動）
    // initPullToRefresh();
}

// 在 DOM 載入完成後初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileAdvancedFeatures);
} else {
    initMobileAdvancedFeatures();
}

// 視窗大小改變時重新初始化
window.addEventListener('resize', () => {
    clearTimeout(window.mobileResizeTimer);
    window.mobileResizeTimer = setTimeout(() => {
        if (isMobileDevice()) {
            initMobileAdvancedFeatures();
        }
    }, 250);
});
