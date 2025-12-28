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

// 創建單個遊戲卡片 (GitHub Style List View)
function createGameCard(game, isExpansion, childExpansions) {
    const card = document.createElement('div');
    card.className = 'game-card';
    if (isExpansion) {
        card.classList.add('expansion-card');
    }

    // Safe escape function
    const escapeHtml = window.escapeHtml || function (text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };

    const escapedName = escapeHtml(game.name || '');

    // 狀態標籤 (GitHub Style Badges)
    const isBorrowed = game.status === '借出';
    const statusText = isBorrowed ? 'Borrowed' : 'Available'; // 英文標籤更像 GitHub
    const statusClass = isBorrowed ? 'status-borrowed' : 'status-available';
    const statusIcon = isBorrowed ? '🟣' : '🟢';

    // 類型標籤
    const isExp = String(game.is_expansion || '').trim();
    const isExpBool = (isExp === '1' || isExp.toLowerCase() === 'true');
    const typeText = isExpBool ? 'Expansion' : 'Game';
    const typeLabelClass = isExpBool ? 'Label Label--secondary' : 'Label Label--primary';

    // 縮圖 (左側)
    const thumbnailHtml = game.bgg_thumbnail
        ? `<img src="${game.bgg_thumbnail}" class="game-list-thumbnail" alt="縮圖" loading="lazy">`
        : `<div class="game-list-thumbnail-placeholder">${game.name.charAt(0)}</div>`;

    // 借閱資訊
    let borrowerInfo = '';
    if (isBorrowed && game.borrower) {
        borrowerInfo = `
            <span class="text-small color-fg-muted">
                Borrowed by <strong>${escapeHtml(game.borrower)}</strong>
            </span>
        `;
    }

    // 擴充數量
    let expansionInfo = '';
    if (childExpansions && childExpansions.length > 0) {
        expansionInfo = `
            <span class="text-small color-fg-muted ml-2">
                • ${childExpansions.length} expansions
            </span>
        `;
    }

    card.innerHTML = `
        <div class="game-list-row">
            <div class="game-list-left">
                ${thumbnailHtml}
            </div>
            <div class="game-list-content">
                <div class="game-list-header">
                    <div class="game-list-title-row">
                        <span class="game-list-title">${escapedName}</span>
                        <span class="game-list-status ${statusClass}">
                            ${statusText}
                        </span>
                    </div>
                    <div class="game-list-meta">
                        <span class="${typeLabelClass}">${typeText}</span>
                        ${expansionInfo}
                    </div>
                </div>
                
                ${borrowerInfo ? `<div class="game-list-borrower">${borrowerInfo}</div>` : ''}
                
                <div class="game-list-details" id="details-${escapedName.replace(/[^a-zA-Z0-9]/g, '_')}">
                    <div class="game-detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">Players</span>
                            <span class="detail-value">${game.players || '-'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Diff</span>
                            <span class="detail-value">${game.diff || '-'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Loc</span>
                            <span class="detail-value">${game.location || '-'}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="game-list-action">
                <button class="btn-icon" onclick="toggleCardDetails('${escapedName.replace(/'/g, "\\'")}')">
                    <span class="icon-chevron-down">▼</span>
                </button>
            </div>
        </div>
        
        <!-- 主要操作區 (展開後或底部) -->
        <div class="game-card-actions" id="actions-${escapedName.replace(/[^a-zA-Z0-9]/g, '_')}">
             ${(window.isAdmin || false) ? `
             <button class="btn btn-sm" onclick="openEditGameModal('${escapedName}')">Edit</button>
             ` : ''}
             <button class="btn btn-sm btn-primary" onclick="openBorrowModal('${escapedName}')" ${isBorrowed ? 'disabled' : ''}>
                ${isBorrowed ? 'Unavailable' : 'Borrow'}
             </button>
        </div>
    `;

    return card;
}

// 切換卡片詳細資訊
function toggleCardDetails(gameName) {
    const safeId = gameName.replace(/[^a-zA-Z0-9]/g, '_');
    const details = document.getElementById(`details-${safeId}`);
    const actions = document.getElementById(`actions-${safeId}`); // Also toggle actions visibility if needed

    // 這裡我們用簡單的 class toggle
    if (details.classList.contains('show')) {
        details.classList.remove('show');
        actions.classList.remove('show');
    } else {
        details.classList.add('show');
        actions.classList.add('show');
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
