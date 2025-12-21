// ==================== 全域變數 ====================
let allGames = [];
let filteredGames = [];
let activeFilters = {
    players: new Set(),
    location: new Set(),
    status: 'all'
};

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', () => {
    loadGames();
});

// ==================== API 調用 ====================
async function loadGames() {
    try {
        const response = await fetch('/api/gallery/games');
        const data = await response.json();

        if (data.success) {
            allGames = data.games;
            document.getElementById('totalGamesCount').textContent = `共 ${data.total} 款桌遊`;
            applyFilters();
            renderGames();
        } else {
            showError('載入遊戲列表失敗: ' + (data.error || '未知錯誤'));
        }
    } catch (error) {
        console.error('載入遊戲失敗:', error);
        showError('無法連接到伺服器，請稍後再試');
    }
}

// ==================== 篩選器處理 ====================
// 篩選器已在 HTML 中固定定義，不需要動態生成

function toggleFilter(type, value) {
    const filterSet = activeFilters[type];

    if (filterSet.has(value)) {
        filterSet.delete(value);
    } else {
        filterSet.add(value);
    }

    // 更新按鈕樣式
    updateFilterButtonStyles();

    // 重新篩選和渲染
    applyFilters();
    renderGames();
}

function toggleStatusFilter(status) {
    activeFilters.status = status;

    // 更新狀態篩選按鈕樣式
    document.querySelectorAll('[data-filter-type="status"]').forEach(btn => {
        if (btn.dataset.value === status) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // 重新篩選和渲染
    applyFilters();
    renderGames();
}

function updateFilterButtonStyles() {
    // 更新所有篩選按鈕的 active 狀態
    document.querySelectorAll('.filter-tag:not([data-filter-type="status"])').forEach(btn => {
        const type = btn.dataset.filterType;
        const value = btn.dataset.value;

        let actualValue = value;
        if (type === 'players') {
            actualValue = parseInt(value);
        }

        if (activeFilters[type] && activeFilters[type].has(actualValue)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

function clearAllFilters() {
    activeFilters = {
        players: new Set(),
        location: new Set(),
        status: 'all'
    };

    // 更新所有按鈕樣式
    document.querySelectorAll('.filter-tag').forEach(btn => {
        btn.classList.remove('active');
    });

    // 重新激活"全部"狀態按鈕
    document.querySelector('[data-filter-type="status"][data-value="all"]').classList.add('active');

    // 重新渲染
    applyFilters();
    renderGames();
}

function applyFilters() {
    filteredGames = allGames.filter(game => {
        // 狀態篩選
        if (activeFilters.status !== 'all') {
            if (game.status !== activeFilters.status) {
                return false;
            }
        }

        // 人數篩選 (AND邏輯：所有選中的人數都要符合)
        if (activeFilters.players.size > 0) {
            const matchPlayers = [...activeFilters.players].every(p => {
                const min = game.minPlayers || 1;
                const max = game.maxPlayers || 10;
                if (p === '10+') {
                    return max >= 10;
                }
                return p >= min && p <= max;
            });
            if (!matchPlayers) return false;
        }

        // 位置篩選 (AND邏輯：遊戲必須符合所有選中的位置)
        if (activeFilters.location.size > 0) {
            const matchLocation = [...activeFilters.location].every(loc =>
                game.location === loc
            );
            if (!matchLocation) return false;
        }

        return true;
    });

    // 更新篩選結果統計
    const filterCount = document.getElementById('filteredGamesCount');
    if (filteredGames.length < allGames.length) {
        filterCount.textContent = `(已篩選出 ${filteredGames.length} 款)`;
        filterCount.style.color = '#ffd43b';
    } else {
        filterCount.textContent = '';
    }
}

// ==================== 遊戲卡片渲染 ====================
function renderGames() {
    const grid = document.getElementById('galleryGrid');

    if (filteredGames.length === 0) {
        grid.innerHTML = `
            <div class="no-results">
                <h3>😔 沒有找到符合條件的桌遊</h3>
                <p>請嘗試調整篩選條件</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = filteredGames.map(game => {
        const imageUrl = getGameImage(game);

        // 狀態判斷邏輯：只根據 status 欄位判斷借出狀態
        const isBorrowed = game.status === '借出';
        const statusClass = isBorrowed ? 'borrowed' : 'available';
        const statusText = isBorrowed ? '借出' : '在庫';

        // 檢查是否已收藏
        const favorites = JSON.parse(localStorage.getItem('gallery_favorites') || '[]');
        const isFavorited = favorites.includes(game.id);

        return `
            <div class="game-card">
                <div class="card-inner">
                    <!-- 卡片正面 -->
                    <div class="card-front">
                        <div class="game-card-image">
                            <img src="${imageUrl}" 
                                 alt="${escapeHtml(game.name)}"
                                 loading="lazy"
                                 onerror="this.src='https://via.placeholder.com/300x420/667eea/ffffff?text=No+Image'">
                            <div class="game-top-labels">
                                ${game.label ? `<span class="game-label">${escapeHtml(game.label)}</span>` : ''}
                                ${(game.minPlayers && game.maxPlayers) ? `<span class="game-players-badge">${game.minPlayers == game.maxPlayers ? game.minPlayers + '人' : game.minPlayers + '-' + game.maxPlayers + '人'}</span>` : ''}
                            </div>
                            <span class="game-status-badge ${statusClass}">${statusText}</span>
                            <div class="game-card-title">${escapeHtml(game.name)}</div>
                        </div>
                    </div>
                    
                    <!-- 卡片背面 -->
                    <div class="card-back">
                        <h3>${escapeHtml(game.name)}</h3>
                        <div class="card-back-info">
                            ${game.minPlayers && game.maxPlayers ? `
                                <p>👥 ${game.minPlayers}${game.minPlayers !== game.maxPlayers ? `-${game.maxPlayers}` : ''} 人</p>
                            ` : ''}
                            ${game.minMinutes && game.maxMinutes ? `
                                <p>⏱️ ${game.minMinutes}${game.minMinutes !== game.maxMinutes ? `-${game.maxMinutes}` : ''} 分鐘</p>
                            ` : ''}
                            ${game.difficulty ? `<p>🎯 難度：${escapeHtml(game.difficulty)}</p>` : ''}
                            ${game.status ? `<p>📦 ${escapeHtml(game.status)}</p>` : ''}
                            ${game.location ? `<p>📍 ${escapeHtml(game.location)}</p>` : ''}
                        </div>
                        <div style="display: flex; gap: 10px; margin-top: 15px;">
                            <button class="favorite-btn-back ${isFavorited ? 'favorited' : ''}" 
                                    onclick="toggleFavorite(event, '${escapeHtml(game.id)}')">
                                ${isFavorited ? '❤️ 已收藏' : '♥ 收藏'}
                            </button>
                            <button class="detail-btn" onclick="showGameDetail('${escapeHtml(game.id)}')">查看詳情</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function getGameImage(game) {
    // 優先使用自訂圖片
    if (game.image) {
        return game.image;
    }

    // 使用 thumbnail（從後端 API 獲取的 BGG thumbnail）
    if (game.thumbnail) {
        return game.thumbnail;
    }

    // 如果有 BGG ID 但沒有圖片 URL，可以嘗試從後端 API 獲取
    // 注意：這需要後端提供額外的端點，目前作為 fallback
    if (game.bggId) {
        // 這會觸發 onerror，進而使用預設占位圖
        // 未來可以實作 /api/gallery/bgg-thumbnail/${game.bggId} 端點
        return `https://via.placeholder.com/300x420/667eea/ffffff?text=BGG+${game.bggId}`;
    }

    // 預設占位圖
    return 'https://via.placeholder.com/300x420/667eea/ffffff?text=No+Image';
}

// ==================== 模態視窗 ====================
function showGameDetail(gameId) {
    const game = allGames.find(g => g.id === gameId);
    if (!game) {
        console.error('找不到遊戲:', gameId);
        return;
    }

    const modal = document.getElementById('gameModal');
    const content = document.getElementById('modalContent');

    const imageUrl = getGameImage(game);

    // 使用更高品質的圖片（BGG 原圖而非 thumbnail）
    let modalImageUrl = imageUrl;
    if (game.bggId) {
        // 如果有 BGG ID，嘗試使用更高品質的圖片
        // BGG thumbnail 格式通常是 __small，可以替換為更大的版本
        modalImageUrl = imageUrl.replace('__small', '__medium').replace('__thumb', '__medium');
    }

    content.innerHTML = `
        <button class="modal-close" onclick="closeModal()">✕</button>
        <img src="${modalImageUrl}" 
             alt="${escapeHtml(game.name)}" 
             class="modal-image"
             onerror="this.src='${imageUrl}'">
        <h2>${escapeHtml(game.name)}</h2>
        <div class="game-info">
            ${game.minPlayers && game.maxPlayers ? `
                <p><strong>🎮 遊玩人數：</strong>${game.minPlayers}${game.minPlayers !== game.maxPlayers ? `-${game.maxPlayers}` : ''} 人</p>
            ` : ''}
            ${game.minMinutes && game.maxMinutes ? `
                <p><strong>⏱️ 遊戲時間：</strong>${game.minMinutes}${game.minMinutes !== game.maxMinutes ? `-${game.maxMinutes}` : ''} 分鐘</p>
            ` : ''}
            ${game.difficulty ? `<p><strong>🎯 難度：</strong>${escapeHtml(game.difficulty)}</p>` : ''}
            ${game.status ? `<p><strong>📦 狀態：</strong>${escapeHtml(game.status)}</p>` : ''}
            ${game.borrower ? `<p><strong>👤 借閱人：</strong>${escapeHtml(game.borrower)}</p>` : ''}
            ${game.location ? `<p><strong>📍 位置：</strong>${escapeHtml(game.location)}</p>` : ''}
            ${game.custodian ? `<p><strong>🔑 保管人：</strong>${escapeHtml(game.custodian)}</p>` : ''}
            ${game.types && game.types.length > 0 ? `
                <p><strong>🏷️ 類型：</strong>${game.types.map(t => escapeHtml(t)).join(', ')}</p>
            ` : ''}
            ${game.tags && game.tags.length > 0 ? `
                <p><strong>🔖 標籤：</strong>${game.tags.map(t => escapeHtml(t)).join(', ')}</p>
            ` : ''}
        </div>
        ${game.bggId ? `
            <a href="https://boardgamegeek.com/boardgame/${game.bggId}" 
               target="_blank" 
               rel="noopener noreferrer"
               class="bgg-link">
                在 BoardGameGeek 查看 ↗
            </a>
        ` : ''}
    `;

    modal.classList.add('active');

    // 防止背景滾動
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('gameModal');
    modal.classList.remove('active');

    // 恢復背景滾動
    document.body.style.overflow = '';
}

// ESC 鍵關閉模態視窗
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// ==================== 收藏功能 ====================
function toggleFavorite(event, gameId) {
    event.stopPropagation(); // 防止觸發卡片點擊

    let favorites = JSON.parse(localStorage.getItem('gallery_favorites') || '[]');
    const index = favorites.indexOf(gameId);

    if (index > -1) {
        favorites.splice(index, 1);
    } else {
        favorites.push(gameId);
    }

    localStorage.setItem('gallery_favorites', JSON.stringify(favorites));

    // 更新按鈕樣式
    const btn = event.target;
    btn.classList.toggle('favorited');

    // 顯示提示
    const gameName = allGames.find(g => g.id === gameId)?.name || '遊戲';
    const message = index > -1 ? `已取消收藏 ${gameName}` : `已收藏 ${gameName}`;
    showToast(message);
}

function showToast(message) {
    // 創建 toast 元素
    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #333;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(toast);

    // 3 秒後移除
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 添加動畫樣式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==================== 工具函數 ====================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    const grid = document.getElementById('galleryGrid');
    grid.innerHTML = `
        <div class="no-results">
            <h3>⚠️ 發生錯誤</h3>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}
