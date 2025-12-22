// BGG (BoardGameGeek) 功能模組
// 處理 BGG 搜尋、詳情顯示、加入館藏等功能

// ============ BGG 搜尋功能 ============

let bggSearchTimeout = null;

// 預加載的分類數據緩存
const bggCategoryCache = {};

// 初始化 BGG 功能
function initBGG() {
    const bggSearchBtn = document.getElementById('bggSearchBtn');

    if (bggSearchBtn) {
        // 搜尋按鈕點擊 - 開啟 modal
        bggSearchBtn.addEventListener('click', () => openBGGSearchModal());
    }

    // 預加載所有分類數據
    preloadAllData();
}

// 開啟 BGG 搜尋 Modal
function openBGGSearchModal() {
    // 建立 Modal HTML
    const modal = document.createElement('div');
    modal.className = 'bgg-modal';
    modal.id = 'bggSearchModal';
    modal.innerHTML = `
        <div class="bgg-modal-content bgg-search-modal-content">
            <span class="bgg-modal-close" onclick="closeBGGSearchModal()">&times;</span>
            <h2>🔍 搜尋 BoardGameGeek 桌遊</h2>
            <div class="bgg-search-box">
                <div class="search-input-group">
                    <input type="text" id="bggSearchBoxModal" class="search" placeholder="輸入桌遊名稱（中文或英文）...">
                    <button class="btn primary" onclick="searchBGGInModal()">搜尋</button>
                </div>
                <p class="search-hint">💡 提示：輸入至少 3 個字元會自動搜尋</p>
            </div>
            <div class="bgg-search-results">
                <div id="bggSearchResultsModal" class="bgg-results-list"></div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // 設定搜尋框事件監聽
    const searchBox = document.getElementById('bggSearchBoxModal');
    if (searchBox) {
        // Enter 鍵搜尋
        searchBox.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchBGGInModal();
            }
        });

        // 即時搜尋 (debounce 500ms)
        searchBox.addEventListener('input', () => {
            clearTimeout(bggSearchTimeout);
            const query = searchBox.value.trim();
            if (query.length >= 3) {
                bggSearchTimeout = setTimeout(() => searchBGGInModal(), 500);
            }
        });

        // 自動 focus
        searchBox.focus();
    }
}

// 關閉 BGG 搜尋 Modal
function closeBGGSearchModal() {
    const modal = document.getElementById('bggSearchModal');
    if (modal) {
        modal.remove();
    }
}

// 在 Modal 中搜尋 BGG 桌遊
async function searchBGGInModal() {
    const query = document.getElementById('bggSearchBoxModal').value.trim();
    if (!query) {
        showToast('請輸入搜尋關鍵字', 'error');
        return;
    }

    const resultsDiv = document.getElementById('bggSearchResultsModal');
    resultsDiv.innerHTML = '<p class="loading">正在搜尋...</p>';

    try {
        const response = await fetch(`/api/bgg/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success && data.results && data.results.length > 0) {
            displayBGGResultsInModal(data.results);
        } else {
            resultsDiv.innerHTML = '<p class="no-results">找不到相關桌遊，請嘗試其他關鍵字</p>';
        }
    } catch (error) {
        console.error('BGG search error:', error);
        resultsDiv.innerHTML = '<p class="error">搜尋時發生錯誤，請稍後再試</p>';
    }
}

// 在 Modal 中顯示 BGG 搜尋結果
function displayBGGResultsInModal(results) {
    const resultsDiv = document.getElementById('bggSearchResultsModal');
    resultsDiv.innerHTML = '<h3>搜尋結果</h3>';

    results.forEach(game => {
        const card = createBGGGameCard(game);
        resultsDiv.appendChild(card);
    });
}

// 顯示 BGG 搜尋結果
function displayBGGResults(results) {
    const resultsDiv = document.getElementById('bggResults');
    const resultsList = document.getElementById('bggResultsList');

    if (!results || results.length === 0) {
        resultsDiv.style.display = 'none';
        showToast('沒有找到相關桌遊', 'info');
        return;
    }

    resultsList.innerHTML = '';
    results.forEach(game => {
        const card = createBGGGameCard(game);
        resultsList.appendChild(card);
    });

    resultsDiv.style.display = 'block';
}

// 建立 BGG 遊戲卡片
function createBGGGameCard(game) {
    const card = document.createElement('div');
    card.className = 'bgg-game-card';
    card.innerHTML = `
        <div class="bgg-game-info">
            <h4>${game.name}</h4>
            <p class="bgg-game-year">${game.year || 'N/A'}</p>
        </div>
        <div class="bgg-game-actions">
            <button class="btn small" onclick="viewBGGGameDetails(${game.id})">查看詳情</button>
            <button class="btn small primary" onclick="addBGGGameToCollection(${game.id}, '${game.name}')">加入館藏</button>
        </div>
    `;
    return card;
}

// 查看 BGG 遊戲詳情
function viewBGGGameDetails(gameId, gameName = null) {
    fetch(`/api/bgg/games/${gameId}`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showBGGGameModal(data.game, gameName);  // 傳遞 gameName 參數
            } else {
                alert('無法載入遊戲詳情');
            }
        })
        .catch(err => {
            console.error('Error fetching game details:', err);
            alert('載入失敗');
        });
}

// 顯示遊戲詳情 Modal
function showBGGGameModal(game, linkedGameName = null) {
    // 根據是否為已連結遊戲顯示不同按鈕
    const footerButtons = linkedGameName
        ? `<button class="btn" onclick="closeBGGModal()">關閉</button>
           <button class="btn danger" onclick="unlinkGameFromBGG('${linkedGameName.replace(/'/g, "\\'")}')">斷開連結</button>`
        : `<button class="btn" onclick="closeBGGModal()">關閉</button>
           <button class="btn primary" onclick="addBGGGameToCollection(${game.id}, '${game.name.replace(/'/g, "\\'")}')">加入館藏</button>`;

    // 建立 Modal
    const modal = document.createElement('div');
    modal.className = 'bgg-modal';
    modal.innerHTML = `
        <div class="bgg-modal-content">
            <span class="bgg-modal-close" onclick="closeBGGModal()">&times;</span>
            <div class="bgg-modal-header">
                ${game.image ? `<img src="${game.image}" alt="${game.name}" class="bgg-game-image">` : ''}
                <div>
                    <h2>${game.name}</h2>
                    <p class="bgg-game-year">發行年份: ${game.year || 'N/A'}</p>
                </div>
            </div>
            <div class="bgg-modal-body">
                <div class="bgg-game-stats">
                    <div class="stat"><strong>評分:</strong> ⭐ ${game.rating_average}/10</div>
                    <div class="stat"><strong>排名:</strong> #${game.rank || 'N/A'}</div>
                    <div class="stat"><strong>玩家數:</strong> ${game.players_display}</div>
                    <div class="stat"><strong>遊戲時間:</strong> ${game.playing_time_display}</div>
                    <div class="stat"><strong>年齡限制:</strong> ${game.min_age || 'N/A'}+</div>
                    <div class="stat"><strong>評分人數:</strong> ${game.rating_users} 人</div>
                </div>
                ${game.description ? `<div class="bgg-game-description"><h3>遊戲簡介</h3><p>${stripHTML(game.description.substring(0, 300))}...</p></div>` : ''}
                ${game.categories && game.categories.length > 0 ? `<div class="bgg-game-categories"><strong>類別:</strong> ${game.categories.join(', ')}</div>` : ''}
                ${game.mechanics && game.mechanics.length > 0 ? `<div class="bgg-game-mechanics"><strong>機制:</strong> ${game.mechanics.join(', ')}</div>` : ''}
            </div>
            <div class="bgg-modal-footer">
                ${footerButtons}
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// 關閉 Modal
function closeBGGModal() {
    const modal = document.querySelector('.bgg-modal');
    if (modal) {
        modal.remove();
    }
}

// 加入桌遊到館藏
function addBGGGameToCollection(gameId, gameName) {
    showAddGameModal(gameId, gameName);
}

// 顯示加入遊戲的 Modal
function showAddGameModal(gameId, gameName, isDuplicate = false, existingGame = null) {
    // 建立 Modal
    const modal = document.createElement('div');
    modal.className = 'bgg-modal add-game-modal';
    modal.id = 'addGameModal';
    
    let warningHtml = '';
    let actionButtonText = '確認加入';
    let actionButtonClass = 'btn primary';
    
    if (isDuplicate && existingGame) {
        warningHtml = `
            <div class="duplicate-warning">
                <div class="warning-icon">⚠️</div>
                <div class="warning-content">
                    <h4>遊戲已存在於館藏中</h4>
                    <p><strong>名稱：</strong>${existingGame.name}</p>
                    <p><strong>BGG ID：</strong>${existingGame.bgg_id}</p>
                    <p><strong>保管人：</strong>${existingGame.custodian || '無'}</p>
                    <p><strong>狀態：</strong>${existingGame.status}</p>
                    <p class="warning-note">如果仍要加入此遊戲，請點擊「強制加入」</p>
                </div>
            </div>
        `;
        actionButtonText = '強制加入';
        actionButtonClass = 'btn danger';
    }
    
    modal.innerHTML = `
        <div class="bgg-modal-content add-game-content">
            <span class="bgg-modal-close" onclick="closeAddGameModal()">&times;</span>
            <h2>加入遊戲到館藏</h2>
            <div class="add-game-form">
                <div class="game-name-display">
                    <label>遊戲名稱：</label>
                    <strong>${gameName}</strong>
                </div>
                ${warningHtml}
                <div class="form-group">
                    <label for="custodianInput">保管人：</label>
                    <input type="text" id="custodianInput" class="form-control" placeholder="請輸入保管人名稱" ${isDuplicate ? '' : 'required'}>
                </div>
                <div class="modal-actions">
                    <button class="btn" onclick="closeAddGameModal()">取消</button>
                    <button class="${actionButtonClass}" id="confirmAddBtn" onclick="confirmAddGame(${gameId}, '${gameName.replace(/'/g, "\\'")}', ${isDuplicate})">
                        ${actionButtonText}
                    </button>
                </div>
                <div id="addGameLoading" class="loading-indicator" style="display: none;">
                    <span>處理中...</span>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 自動 focus 到輸入框
    setTimeout(() => {
        const input = document.getElementById('custodianInput');
        if (input) {
            input.focus();
            // Enter 鍵確認
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    confirmAddGame(gameId, gameName, isDuplicate);
                }
            });
        }
    }, 100);
}

// 關閉加入遊戲 Modal
function closeAddGameModal() {
    const modal = document.getElementById('addGameModal');
    if (modal) {
        modal.remove();
    }
}

// 確認加入遊戲
function confirmAddGame(gameId, gameName, isForce = false) {
    const custodianInput = document.getElementById('custodianInput');
    const custodian = custodianInput ? custodianInput.value.trim() : '';
    
    // 如果不是強制加入，則驗證保管人欄位
    if (!isForce && !custodian) {
        showToast('請輸入保管人名稱', 'error');
        custodianInput.focus();
        return;
    }
    
    // 顯示載入中
    const loadingDiv = document.getElementById('addGameLoading');
    const confirmBtn = document.getElementById('confirmAddBtn');
    if (loadingDiv) loadingDiv.style.display = 'block';
    if (confirmBtn) confirmBtn.disabled = true;
    
    // 發送請求
    fetch('/api/bgg/collection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            game_id: gameId,
            custodian: custodian,
            force: isForce
        })
    })
        .then(r => r.json().then(data => ({ status: r.status, data: data })))
        .then(({ status, data }) => {
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (confirmBtn) confirmBtn.disabled = false;
            
            if (status === 409 && data.duplicate) {
                // 遊戲重複，顯示警告
                closeAddGameModal();
                showAddGameModal(gameId, gameName, true, data.existing_game);
                showToast(data.message, 'warning');
            } else if (data.success) {
                // 成功加入
                showToast(data.message, 'success');
                closeAddGameModal();
                closeBGGModal(); // 同時關閉遊戲詳情 modal
                if (typeof loadGames === 'function') {
                    loadGames(); // 重新載入遊戲列表
                }
            } else {
                // 其他錯誤
                showToast(data.error || '加入失敗', 'error');
            }
        })
        .catch(err => {
            console.error('Error adding game:', err);
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (confirmBtn) confirmBtn.disabled = false;
            showToast('加入失敗，請稍後再試', 'error');
        });
}


// 斷開桌遊與 BGG 的連結
function unlinkGameFromBGG(gameName) {
    if (!confirm(`確定要將「${gameName}」與 BGG 斷開連結嗎？`)) {
        return;
    }

    fetch(`/api/bgg/games/link/${encodeURIComponent(gameName)}`, {
        method: 'DELETE'
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showToast('✅ 已成功斷開連結');
                closeBGGModal();
                if (typeof loadGames === 'function') {
                    loadGames(); // 重新載入遊戲列表
                }
            } else {
                showToast(data.error || '斷開連結失敗', 'error');
            }
        })
        .catch(err => {
            console.error('Error unlinking game:', err);
            showToast('斷開連結失敗', 'error');
        });
}


// ============ BGG 推薦區塊功能 ============

// ============ BGG 推薦區塊功能 ============

let currentBGGSource = 'bgg'; // 'bgg' or 'club'

// 預加載的分類數據 Promise 快取
// Key: `${source}-${category}`
// Value: Promise<Array>
const bggCategoryPromises = {};

// 全局靜態快取數據
let staticRecommendationsCache = null;

// 追蹤每個分類目前顯示的遊戲數量
// Key: `${source}-${category}`
// Value: number (當前顯示數量)
const categoryDisplayState = {};

// 儲存當前分類的完整遊戲列表
let currentCategoryGames = [];

// 獲取分類數據 (返回 Promise)
function fetchCategoryData(source, category) {
    const cacheKey = `${source}-${category}`;

    // 1. 如果靜態快取已載入，直接從靜態快取返回
    if (staticRecommendationsCache && staticRecommendationsCache[cacheKey]) {
        console.log(`[Static Cache] Hit for ${cacheKey}`);
        return Promise.resolve(staticRecommendationsCache[cacheKey]);
    }

    // 2. 如果已經有請求正在進行或已完成，直接返回該 Promise
    if (bggCategoryPromises[cacheKey]) {
        return bggCategoryPromises[cacheKey];
    }

    // 3. 建立新的請求 Promise (Fallback to API)
    console.log(`[API Fallback] Fetching ${cacheKey}`);
    const promise = fetch(`/api/bgg/recommendations?source=${source}&category=${category}`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                return data.games || [];
            } else {
                throw new Error(data.error || 'Unknown error');
            }
        })
        .catch(err => {
            console.error(`Error fetching ${cacheKey}:`, err);
            // 失敗時移除快取，讓下次可以重試
            delete bggCategoryPromises[cacheKey];
            throw err;
        });

    // 存入快取
    bggCategoryPromises[cacheKey] = promise;
    return promise;
}

// 預加載所有數據 (優先嘗試載入靜態 JSON)
function preloadAllData() {
    console.log('開始預加載 BGG 與社團熱門遊戲...');

    // 嘗試載入靜態快取檔案
    fetch('/data/recommendations.json')
        .then(r => {
            if (!r.ok) throw new Error('Static cache not found');
            return r.json();
        })
        .then(data => {
            console.log(`[Static Cache] Loaded successfully (Updated: ${data.updated_at})`);
            staticRecommendationsCache = data.data;
        })
        .catch(err => {
            console.warn('[Static Cache] Load failed, falling back to API pre-loading:', err);
            // 如果靜態檔案載入失敗，回退到 API 預加載
            const sources = ['bgg', 'club'];
            const categories = ['party', 'strategy', 'family', 'children'];

            sources.forEach(source => {
                categories.forEach(category => {
                    fetchCategoryData(source, category);
                });
            });
        });
}

function toggleRecommendations(source) {
    const content = document.getElementById('bggRecContent');
    const bggBtn = document.getElementById('bggRecommendationsBtn');
    const clubBtn = document.getElementById('clubRecommendationsBtn');

    // 如果點擊的是當前已開啟的來源，則關閉
    if (content.style.display === 'block' && currentBGGSource === source) {
        content.style.display = 'none';
        return;
    }

    // 切換來源
    currentBGGSource = source;
    content.style.display = 'block';

    // 重置分類顯示
    const listDiv = document.getElementById('bggCategoryList');
    listDiv.innerHTML = '';
    document.querySelectorAll('.bgg-tab').forEach(tab => tab.classList.remove('active'));
    currentBGGCategory = null;

    // 自動加載第一個分類
    loadBGGCategory('party');
}

// 保留舊函數以兼容（如果有其他地方調用）
function toggleBGGRecommendations() {
    toggleRecommendations('bgg');
}

// 当前选中的分类
let currentBGGCategory = null;

// 加载指定分类的游戏（使用 API）
function loadBGGCategory(category) {
    const listDiv = document.getElementById('bggCategoryList');

    // 如果點擊的是當前分類，且列表不為空，則不動作
    if (currentBGGCategory === category && listDiv.innerHTML !== '') {
        return;
    }

    currentBGGCategory = category;

    // 重置該分類的顯示狀態
    const categoryKey = `${currentBGGSource}-${category}`;
    categoryDisplayState[categoryKey] = 10;

    // 更新标签样式
    document.querySelectorAll('.bgg-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.textContent.includes(getCategoryIcon(category))) {
            tab.classList.add('active');
        }
    });

    listDiv.innerHTML = '<p class="loading" style="text-align: center; padding: 20px; color: #718096;">正在加載...</p>';

    // 使用 fetchCategoryData 獲取數據 (可能是快取的 Promise)
    fetchCategoryData(currentBGGSource, category)
        .then(games => {
            // 確保數據回來時，使用者還停留在同一個分類
            if (currentBGGCategory === category) {
                if (games.length > 0) {
                    displayCategoryGames(games);
                } else {
                    listDiv.innerHTML = '<p style="text-align: center; padding: 20px; color: #718096;">此分類暫無遊戲</p>';
                }
            }
        })
        .catch(err => {
            if (currentBGGCategory === category) {
                listDiv.innerHTML = `<div style="text-align: center; padding: 20px; color: #e53e3e;">
                    <p>無法加載遊戲列表</p>
                    <p style="font-size: 0.85em; margin-top: 5px;">錯誤: ${err.message}</p>
                </div>`;
            }
        });
}

// 获取分类图标（用于匹配标签）
function getCategoryIcon(category) {
    const icons = {
        'party': '🎉',
        'strategy': '🧠',
        'family': '👨\u200d👩\u200d👧',
        'children': '🧸'
    };
    return icons[category] || '';
}

// 显示分类游戏（支援分頁顯示）
function displayCategoryGames(games) {
    const listDiv = document.getElementById('bggCategoryList');

    if (!games || games.length === 0) {
        listDiv.innerHTML = '<p style="text-align: center; padding: 20px; color: #718096;">暫無遊戲</p>';
        return;
    }

    // 儲存完整遊戲列表
    currentCategoryGames = games;

    // 取得當前分類的 key
    const categoryKey = `${currentBGGSource}-${currentBGGCategory}`;

    // 初始化顯示狀態（預設顯示 10 款）
    if (!categoryDisplayState[categoryKey]) {
        categoryDisplayState[categoryKey] = 10;
    }

    // 清空列表
    listDiv.innerHTML = '';

    // 取得當前應該顯示的數量
    const displayCount = Math.min(categoryDisplayState[categoryKey], games.length);

    // 顯示遊戲卡片
    for (let i = 0; i < displayCount; i++) {
        const game = games[i];
        const card = document.createElement('div');
        card.className = 'bgg-category-card';
        card.style.cursor = 'pointer';

        // 判斷是否有中文名稱
        const displayName = game.chinese_name || game.name;
        const hasChineseName = !!game.chinese_name;

        card.innerHTML = `
            <div class="bgg-card-rank">#${i + 1}</div>
            ${game.thumbnail ? `<img src="${game.thumbnail}" alt="${displayName}" class="bgg-card-thumbnail">` : '<div class="bgg-card-no-image">無圖片</div>'}
            <div class="bgg-card-info">
                <h4>${displayName}</h4>
                ${hasChineseName ? `<p class="bgg-card-english-name" style="font-size: 0.85em; color: #718096; margin-top: 2px;">${game.name}</p>` : ''}
                <p class="bgg-card-year">${game.year || 'N/A'}</p>
            </div>
        `;

        // 點擊卡片查看詳情
        card.addEventListener('click', () => {
            viewBGGGameDetails(game.id);
        });

        listDiv.appendChild(card);
    }

    // 如果還有更多遊戲，顯示「加載更多」按鈕
    if (displayCount < games.length) {
        const loadMoreBtn = document.createElement('div');
        loadMoreBtn.className = 'load-more-btn';
        loadMoreBtn.innerHTML = `
            <button class="btn primary" onclick="loadMoreGames()">
                ▼ 顯示更多遊戲 (還有 ${games.length - displayCount} 款)
            </button>
        `;
        listDiv.appendChild(loadMoreBtn);
    }
}

// 加載更多遊戲
function loadMoreGames() {
    const categoryKey = `${currentBGGSource}-${currentBGGCategory}`;

    // 增加顯示數量（每次增加 10 款）
    categoryDisplayState[categoryKey] = (categoryDisplayState[categoryKey] || 10) + 10;

    // 重新顯示遊戲（使用儲存的完整列表）
    displayCategoryGames(currentCategoryGames);
}

// 移除 HTML 標籤
function stripHTML(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
}

// 在頁面載入時初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBGG);
} else {
    initBGG();
}
