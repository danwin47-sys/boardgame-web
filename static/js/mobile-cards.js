/**
 * 手機版卡片渲染功能
 */

// 渲染手機版卡片列表
function renderMobileCards(games) {
    let container = document.getElementById('mobileCardsContainer');

    // 如果容器不存在，創建它
    if (!container) {
        const tableWrapper = document.querySelector('.table-wrapper');
        container = document.createElement('div');
        container.id = 'mobileCardsContainer';
        container.className = 'mobile-cards-container';
        tableWrapper.parentNode.insertBefore(container, tableWrapper.nextSibling);
    }

    // 清空容器
    container.innerHTML = '';

    // 如果沒有遊戲，顯示空狀態
    if (!games || games.length === 0) {
        container.innerHTML = '<div class="mobile-cards-empty"></div>';
        return;
    }

    // 組織遊戲數據（主遊戲和擴充）
    const gameMap = new Map();
    const rootGames = [];

    games.forEach(game => {
        const isExpansion = String(game.is_expansion || '').trim();
        const isExp = isExpansion === '1' || isExpansion.toLowerCase() === 'true';

        if (isExp && game.parent_game) {
            if (!gameMap.has(game.parent_game)) {
                gameMap.set(game.parent_game, []);
            }
            gameMap.get(game.parent_game).push(game);
        } else {
            rootGames.push(game);
        }
    });

    // 渲染每個遊戲卡片
    rootGames.forEach(game => {
        const childExpansions = gameMap.get(game.name) || [];
        const card = createGameCard(game, false, childExpansions);
        container.appendChild(card);

        // 渲染擴充卡片
        childExpansions.forEach(expansion => {
            const expansionCard = createGameCard(expansion, true, []);
            container.appendChild(expansionCard);
        });
    });
}

// 創建單個遊戲卡片
function createGameCard(game, isExpansion, childExpansions) {
    const card = document.createElement('div');
    card.className = 'game-card';
    if (isExpansion) {
        card.classList.add('expansion-card');
    }

    const hasChildren = childExpansions && childExpansions.length > 0;

    // Safe escape function
    const escapeHtml = window.escapeHtml || function (text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };

    const escapedName = escapeHtml(game.name || '');

    // 狀態相關
    const statusText = game.status === '借出' ? '借出' : '在庫';
    const statusClass = game.status === '借出' ? 'status-borrowed' : 'status-available';

    // 類型標籤
    const isExp = String(game.is_expansion || '').trim();
    const typeText = (isExp === '1' || isExp.toLowerCase() === 'true') ? '🧩 擴充' : '🎮 主遊戲';
    const typeBadgeClass = (isExp === '1' || isExp.toLowerCase() === 'true') ? 'expansion-badge' : 'main-game-badge';

    // 縮圖
    const thumbnailHtml = game.bgg_thumbnail
        ? `<img src="${game.bgg_thumbnail}" class="game-card-thumbnail" alt="縮圖" loading="lazy">`
        : '';

    // BGG 圖示
    const bggIcon = game.bgg_id
        ? `<span class="bgg-icon" title="BGG ID: ${game.bgg_id}">🎲</span>`
        : '';

    // 借閱人顯示
    let borrowerDisplay = game.borrower || '-';
    if (game.status === '借出' && game.borrower) {
        borrowerDisplay = `<strong>${game.borrower}</strong>`;
    }

    // 工號
    let displayBorrowerId = game.borrower_id || '-';
    if (!displayBorrowerId || displayBorrowerId === '-') {
        if (game.borrower && window.memberNameToId) {
            const borrowerName = String(game.borrower).trim();
            displayBorrowerId = window.memberNameToId[borrowerName] || '-';
        }
    }

    card.innerHTML = `
        <div class="game-card-header">
            ${thumbnailHtml}
            <div class="game-card-title-section">
                <div class="game-card-title">${game.name}</div>
                <div class="game-card-badges">
                    <span class="${typeBadgeClass}">${typeText}</span>
                    <span class="status-badge ${statusClass}">
                        <span class="status-dot"></span>${statusText}
                    </span>
                    ${bggIcon}
                </div>
            </div>
        </div>
        
        <div class="game-card-content">
            <div class="game-card-field">
                <div class="game-card-label">借閱人</div>
                <div class="game-card-value">${borrowerDisplay}</div>
            </div>
            <div class="game-card-field">
                <div class="game-card-label">工號</div>
                <div class="game-card-value">${displayBorrowerId}</div>
            </div>
            <div class="game-card-field">
                <div class="game-card-label">遊玩人數</div>
                <div class="game-card-value">${game.players || '-'}</div>
            </div>
            <div class="game-card-field">
                <div class="game-card-label">難度</div>
                <div class="game-card-value">${game.diff || '-'}</div>
            </div>
        </div>
        
        <div class="game-card-details" id="details-${escapedName.replace(/[^a-zA-Z0-9]/g, '_')}">
            <div class="game-card-detail-row">
                <span class="game-card-detail-label">保管人</span>
                <span class="game-card-detail-value">${game.custodian || '-'}</span>
            </div>
            <div class="game-card-detail-row">
                <span class="game-card-detail-label">位置</span>
                <span class="game-card-detail-value">${game.location || '-'}</span>
            </div>
            <div class="game-card-detail-row">
                <span class="game-card-detail-label">修改日期</span>
                <span class="game-card-detail-value">${window.formatDate ? window.formatDate(game.mdate) : (game.mdate || '-')}</span>
            </div>
        </div>
        
        <button class="game-card-expand-btn" onclick="toggleCardDetails('${escapedName.replace(/'/g, "\\'")}')">
            <span class="expand-icon">▼</span>
            <span class="expand-text">顯示更多</span>
        </button>
        
        ${(window.isAdmin || false) ? `
        <div class="game-card-actions">
            <button class="game-card-btn game-card-btn-primary" onclick="openEditGameModal('${escapedName}')">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/>
                </svg>
                編輯
            </button>
        </div>
        ` : ''}
    `;

    return card;
}

// 切換卡片詳細資訊
function toggleCardDetails(gameName) {
    const safeId = gameName.replace(/[^a-zA-Z0-9]/g, '_');
    const details = document.getElementById(`details-${safeId}`);
    const btn = event.currentTarget;
    const icon = btn.querySelector('.expand-icon');
    const text = btn.querySelector('.expand-text');

    if (details.classList.contains('show')) {
        details.classList.remove('show');
        icon.textContent = '▼';
        text.textContent = '顯示更多';
    } else {
        details.classList.add('show');
        icon.textContent = '▲';
        text.textContent = '顯示較少';
    }
}

// 檢測是否為手機裝置
function isMobileDevice() {
    return window.innerWidth <= 768;
}

// 監聽視窗大小變化
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        // 重新渲染適當的視圖
        if (window.currentFilteredGames && window.currentFilteredGames.length > 0) {
            if (typeof window.renderTable === 'function') {
                window.renderTable(window.currentFilteredGames);
            }
            if (isMobileDevice()) {
                renderMobileCards(window.currentFilteredGames);
            }
        }
    }, 250);
});

// 修改原有的 renderTable 函數，同時渲染手機版
if (typeof window.renderTable === 'function') {
    const originalRenderTable = window.renderTable;
    window.renderTable = function (games) {
        // 渲染桌面版表格
        originalRenderTable(games);

        // 如果是手機裝置，也渲染卡片
        if (isMobileDevice()) {
            renderMobileCards(games);
        }
    };
}
