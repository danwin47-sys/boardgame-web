/**
 * 全站搜尋功能
 * 提供遊戲和會員的即時搜尋
 */

let searchTimeout = null;
const SEARCH_DEBOUNCE_MS = 300;

/**
 * 初始化搜尋功能
 */
function initSearch() {
    const searchInput = document.getElementById('globalSearchInput');
    const searchResults = document.getElementById('searchResults');

    if (!searchInput) return;

    // 監聽輸入事件
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();

        // 清除之前的計時器
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }

        // 如果查詢為空，隱藏結果
        if (!query) {
            hideSearchResults();
            return;
        }

        // 延遲搜尋（debounce）
        searchTimeout = setTimeout(() => {
            performGlobalSearch(query);
        }, SEARCH_DEBOUNCE_MS);
    });

    // 點擊外部關閉搜尋結果
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            hideSearchResults();
        }
    });

    // 按 ESC 關閉搜尋結果
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hideSearchResults();
            searchInput.blur();
        }
    });
}

/**
 * 執行全站搜尋
 */
async function performGlobalSearch(query) {
    const searchResults = document.getElementById('searchResults');

    try {
        // 顯示載入中
        showSearchLoading();

        const response = await fetch(`/api/search/global?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success) {
            // 儲存搜尋歷史
            saveSearchHistory(query);
            displaySearchResults(data.results, query);
        } else {
            showSearchError(data.error || '搜尋失敗');
        }
    } catch (error) {
        console.error('搜尋錯誤:', error);
        showSearchError('搜尋時發生錯誤');
    }
}

/**
 * 儲存搜尋歷史
 */
function saveSearchHistory(query) {
    const MAX_HISTORY = 10;
    let history = getSearchHistory();

    // 移除重複項目
    history = history.filter(item => item !== query);

    // 添加到開頭
    history.unshift(query);

    // 限制數量
    if (history.length > MAX_HISTORY) {
        history = history.slice(0, MAX_HISTORY);
    }

    localStorage.setItem('searchHistory', JSON.stringify(history));
}

/**
 * 取得搜尋歷史
 */
function getSearchHistory() {
    try {
        const history = localStorage.getItem('searchHistory');
        return history ? JSON.parse(history) : [];
    } catch {
        return [];
    }
}

/**
 * 清除搜尋歷史
 */
function clearSearchHistory() {
    localStorage.removeItem('searchHistory');
}

/**
 * 顯示搜尋結果
 */
function displaySearchResults(results, query) {
    const searchResults = document.getElementById('searchResults');
    const { games, members, total } = results;

    if (total === 0) {
        searchResults.innerHTML = `
            <div class="search-no-results">
                <p>找不到「${escapeHtml(query)}」的相關結果</p>
            </div>
        `;
        searchResults.classList.add('show');
        return;
    }

    let html = '';

    // 顯示遊戲結果
    if (games && games.length > 0) {
        html += '<div class="search-section">';
        html += `<div class="search-section-title">🎲 遊戲 (${games.length})</div>`;
        html += '<div class="search-items">';

        games.slice(0, 5).forEach(game => {
            const gameName = game.name || '未知遊戲';
            const gameStatus = game.status || '';
            const statusClass = gameStatus === '可用' ? 'available' : 'borrowed';

            html += `
                <div class="search-item" onclick="window.location.href='/'">
                    <div class="search-item-icon">🎮</div>
                    <div class="search-item-content">
                        <div class="search-item-title">${escapeHtml(gameName)}</div>
                        <div class="search-item-meta">
                            <span class="status-badge ${statusClass}">${escapeHtml(gameStatus)}</span>
                        </div>
                    </div>
                </div>
            `;
        });

        if (games.length > 5) {
            html += `<div class="search-more">還有 ${games.length - 5} 個遊戲...</div>`;
        }

        html += '</div></div>';
    }

    // 顯示會員結果
    if (members && members.length > 0) {
        html += '<div class="search-section">';
        html += `<div class="search-section-title">👥 會員 (${members.length})</div>`;
        html += '<div class="search-items">';

        members.slice(0, 5).forEach(member => {
            const memberName = member.name || '未知會員';
            const memberId = member.id || '';

            html += `
                <div class="search-item">
                    <div class="search-item-icon">👤</div>
                    <div class="search-item-content">
                        <div class="search-item-title">${escapeHtml(memberName)}</div>
                        <div class="search-item-meta">${escapeHtml(memberId)}</div>
                    </div>
                </div>
            `;
        });

        if (members.length > 5) {
            html += `<div class="search-more">還有 ${members.length - 5} 個會員...</div>`;
        }

        html += '</div></div>';
    }

    searchResults.innerHTML = html;
    searchResults.classList.add('show');
}

/**
 * 顯示載入中
 */
function showSearchLoading() {
    const searchResults = document.getElementById('searchResults');
    searchResults.innerHTML = `
        <div class="search-loading">
            <div class="spinner"></div>
            <p>搜尋中...</p>
        </div>
    `;
    searchResults.classList.add('show');
}

/**
 * 顯示錯誤訊息
 */
function showSearchError(message) {
    const searchResults = document.getElementById('searchResults');
    searchResults.innerHTML = `
        <div class="search-error">
            <p>❌ ${escapeHtml(message)}</p>
        </div>
    `;
    searchResults.classList.add('show');
}

/**
 * 隱藏搜尋結果
 */
function hideSearchResults() {
    const searchResults = document.getElementById('searchResults');
    if (searchResults) {
        searchResults.classList.remove('show');
    }
}

/**
 * HTML 轉義
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 頁面載入時初始化
document.addEventListener('DOMContentLoaded', initSearch);
