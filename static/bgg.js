// BGG (BoardGameGeek) 功能模組
// 處理 BGG 搜尋、詳情顯示、加入館藏等功能

// ============ BGG 搜尋功能 ============

let bggSearchTimeout = null;

// 初始化 BGG 功能
function initBGG() {
    const bggSearchBox = document.getElementById('bggSearchBox');
    const bggSearchBtn = document.getElementById('bggSearchBtn');

    if (bggSearchBox && bggSearchBtn) {
        // 搜尋按鈕點擊
        bggSearchBtn.addEventListener('click', () => searchBGG());

        // Enter 鍵搜尋
        bggSearchBox.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchBGG();
            }
        });

        // 即時搜尋 (debounce 500ms)
        bggSearchBox.addEventListener('input', () => {
            clearTimeout(bggSearchTimeout);
            const query = bggSearchBox.value.trim();
            if (query.length >= 3) {
                bggSearchTimeout = setTimeout(() => searchBGG(), 500);
            }
        });

        // 載入熱門桌遊
        loadHotGames();
    }
}

// 搜尋 BGG 桌遊
async function searchBGG() {
    const query = document.getElementById('bggSearchBox').value.trim();
    if (!query) {
        showToast('請輸入搜尋關鍵字', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/bgg/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success) {
            displayBGGResults(data.results);
        } else {
            showToast(data.error || '搜尋失敗', 'error');
        }
    } catch (error) {
        console.error('BGG search error:', error);
        showToast('搜尋時發生錯誤', 'error');
    }
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
function viewBGGGameDetails(gameId) {
    fetch(`/api/bgg/games/${gameId}`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showBGGGameModal(data.game);
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
function showBGGGameModal(game) {
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
                <button class="btn" onclick="closeBGGModal()">關閉</button>
                <button class="btn primary" onclick="addBGGGameToCollection(${game.id}, '${game.name}')">加入館藏</button>
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
    const custodian = prompt(`要將「${gameName}」加入館藏，請輸入保管人名稱：`);
    if (!custodian) return;

    fetch('/api/bgg/collection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            game_id: gameId,
            custodian: custodian
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                closeBGGModal();
                if (typeof loadGames === 'function') {
                    loadGames(); // 重新載入遊戲列表
                }
            } else {
                alert(data.error || '加入失敗');
            }
        })
        .catch(err => {
            console.error('Error adding game:', err);
            alert('加入失敗');
        });
}

// 載入熱門桌遊
async function loadHotGames() {
    try {
        const response = await fetch('/api/bgg/hot?limit=10');
        const data = await response.json();

        if (data.success) {
            displayHotGames(data.games);
        }
    } catch (error) {
        console.error('Error loading hot games:', error);
    }
}

// 顯示熱門桌遊
function displayHotGames(games) {
    const hotList = document.getElementById('bggHotList');
    if (!hotList) return;

    hotList.innerHTML = '';
    games.forEach((game, index) => {
        const card = document.createElement('div');
        card.className = 'bgg-hot-card';
        card.innerHTML = `
            <div class="bgg-hot-rank">#${index + 1}</div>
            ${game.thumbnail ? `<img src="${game.thumbnail}\" alt="${game.name}" class="bgg-hot-thumbnail">` : ''}
            <div class="bgg-hot-info">
                <h4>${game.name}</h4>
                <p>${game.year || ''}</p>
                <button class="btn small" onclick="viewBGGGameDetails(${game.id})">查看</button>
            </div>
        `;
        hotList.appendChild(card);
    });
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
