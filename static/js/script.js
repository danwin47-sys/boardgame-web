const apiBase = '/api';
let allGames = [];
let allMembers = []; // 儲存所有會員資料
let memberNameToId = {}; // 姓名到工號的映射表
let currentStatusFilter = 'all';
let currentPlayerFilters = new Set(); // 使用 Set 儲存多個人數條件

// 分頁配置
const ITEMS_PER_PAGE = 50;
let currentPage = 1;
let totalPages = 1;
let currentFilteredGames = []; // 儲存當前篩選後的遊戲列表

// 固定表格標題
function initStickyHeader() {
    const table = document.getElementById('gameTable');
    const thead = table.querySelector('thead');
    const theadClone = thead.cloneNode(true);

    // 創建固定標題容器
    const stickyHeader = document.createElement('div');
    stickyHeader.id = 'stickyTableHeader';
    stickyHeader.className = 'sticky-table-header';
    stickyHeader.style.display = 'none';

    const stickyTable = document.createElement('table');
    stickyTable.appendChild(theadClone);
    stickyHeader.appendChild(stickyTable);
    document.body.appendChild(stickyHeader);

    // 監聽滾動事件
    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const tableRect = table.getBoundingClientRect();
                const tableTop = tableRect.top;
                const tableBottom = tableRect.bottom;

                // 當表格頂部滾出視窗且底部還在視窗內時，顯示固定標題
                if (tableTop < 0 && tableBottom > 100) {
                    stickyHeader.style.display = 'block';
                    stickyHeader.style.left = tableRect.left + 'px';
                    stickyHeader.style.width = tableRect.width + 'px';

                    // 同步列寬 - 使用精確寬度
                    const originalCells = thead.querySelectorAll('th');
                    const clonedCells = theadClone.querySelectorAll('th');
                    originalCells.forEach((cell, index) => {
                        if (clonedCells[index]) {
                            const width = cell.getBoundingClientRect().width;
                            clonedCells[index].style.width = width + 'px';
                            clonedCells[index].style.minWidth = width + 'px';
                            clonedCells[index].style.maxWidth = width + 'px';
                        }
                    });
                } else {
                    stickyHeader.style.display = 'none';
                }

                ticking = false;
            });
            ticking = true;
        }
    });
}

// Toast 通知系統
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => { toast.classList.remove('show'); }, 3000);
}

// 更新統計資訊
function updateStats() {
    document.getElementById('totalCount').textContent = allGames.length;

    // 計算主遊戲數量（排除擴充）
    const mainGames = allGames.filter(g => {
        const isExpansion = String(g.is_expansion || '').trim();
        return !(isExpansion === '1' || isExpansion.toLowerCase() === 'true');
    });
    document.getElementById('mainGameCount').textContent = mainGames.length;

    document.getElementById('availableCount').textContent = allGames.filter(g => g.status !== '借出').length;
    document.getElementById('borrowedCount').textContent = allGames.filter(g => g.status === '借出').length;
}

// --- 手機版篩選面板控制 ---
function initMobileFilterPanel() {
    // 檢查是否為手機版且尚未初始化
    if (window.innerWidth > 768 || document.querySelector('.filter-panel-toggle')) {
        return;
    }

    const filterContainer = document.querySelector('.filter-buttons');
    if (!filterContainer) return;

    // 創建切換按鈕
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'filter-panel-toggle btn primary';
    toggleBtn.innerHTML = `
        <span>🔍 篩選與排序</span>
        <span class="icon">▼</span>
    `;

    // 插入到篩選容器之前
    filterContainer.parentNode.insertBefore(toggleBtn, filterContainer);

    // 點擊事件
    toggleBtn.addEventListener('click', () => {
        const isExpanded = filterContainer.classList.contains('show');

        if (isExpanded) {
            filterContainer.classList.remove('show');
            toggleBtn.classList.remove('active');
        } else {
            filterContainer.classList.add('show');
            toggleBtn.classList.add('active');
        }
    });
}

// 監聽視窗大小改變，動態處理
window.addEventListener('resize', () => {
    const toggleBtn = document.querySelector('.filter-panel-toggle');
    const filterContainer = document.querySelector('.filter-buttons');

    if (window.innerWidth <= 768) {
        initMobileFilterPanel();
    } else {
        // 電腦版移除手機特有元素
        if (toggleBtn) toggleBtn.remove();
        if (filterContainer) filterContainer.classList.remove('show');
    }
});

// 初始執行
document.addEventListener('DOMContentLoaded', () => {
    initMobileFilterPanel();
    loadGames(); // 原有的 loadGames
});

// 載入桌遊資料
async function loadGames() {
    try {
        // 同時載入遊戲和會員資料
        const [gamesResp, membersResp] = await Promise.all([
            fetch(`${apiBase}/games`),
            fetch(`${apiBase}/members`)
        ]);

        if (!gamesResp.ok || !membersResp.ok) throw new Error('Server error');

        allGames = await gamesResp.json();
        allMembers = await membersResp.json();

        // 建立姓名到工號的映射表
        memberNameToId = {};
        allMembers.forEach(member => {
            const name = String(member.name || '').trim();
            const id = String(member.id || '').trim();
            if (name && id) {
                memberNameToId[name] = id;
            }
        });

        updateStats();
        applyCurrentFilter();

        // 更新最後更新時間
        const now = new Date();
        const timeString = now.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
        const timeElement = document.getElementById('lastUpdateTime');
        if (timeElement) {
            timeElement.textContent = `最後更新：${timeString}`;
        }
    } catch (e) {
        console.error("載入失敗:", e);
        showToast('載入資料失敗', 'error');
    }
}

// 格式化日期
function formatDate(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// 渲染表格
function renderTable(games) {
    const tbody = document.querySelector('#gameTable tbody');
    tbody.innerHTML = '';

    const isAdmin = document.body.classList.contains('admin-page');
    const fragment = document.createDocumentFragment();

    // 儲存當前篩選後的遊戲列表（用於分頁）
    currentFilteredGames = games;

    // 資料驗證：過濾掉無效的遊戲資料
    const validGames = games.filter(game => {
        if (!game || !game.name) {
            console.warn('Invalid game data (missing name):', game);
            return false;
        }
        // 確保 name 是字串
        if (typeof game.name !== 'string') {
            console.warn('Invalid game data (name is not string):', game);
            return false;
        }
        return true;
    });

    // 如果沒有有效遊戲，直接返回
    if (validGames.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 20px;">無有效遊戲資料</td></tr>';
        totalPages = 1;
        renderPagination();
        return;
    }

    // 計算分頁
    totalPages = Math.ceil(validGames.length / ITEMS_PER_PAGE);
    // 確保當前頁面在有效範圍內
    if (currentPage > totalPages) {
        currentPage = totalPages;
    }
    if (currentPage < 1) {
        currentPage = 1;
    }

    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const pageGames = validGames.slice(startIndex, endIndex);

    // --- 層級化邏輯開始 ---
    // 1. 建立索引與分組
    const gameMap = {};
    const parentToExpansions = {};
    const rootGames = [];

    // 建立名稱索引（使用當前頁面的遊戲）
    pageGames.forEach(g => {
        gameMap[g.name] = g;
    });

    // 進行分組 (智慧偵測邏輯)
    pageGames.forEach(game => {
        let isExp = String(game.is_expansion || '').trim().toLowerCase() === 'true' || game.is_expansion === '1';
        let parentName = String(game.parent_game || '').trim();

        // 檢查資料庫是否有明確設定 is_expansion
        const hasExplicitExpansionValue = game.is_expansion !== undefined &&
            game.is_expansion !== null &&
            String(game.is_expansion).trim() !== '';

        // --- 智慧偵測:只在資料庫沒有明確設定時才嘗試從名稱推斷 ---
        if (!hasExplicitExpansionValue && !isExp && !parentName) {
            // 模式 1: "主遊戲名稱: 擴充名稱"
            if (game.name.includes(':')) {
                const potentialParent = game.name.split(':')[0].trim();
                if (gameMap[potentialParent] && potentialParent !== game.name) {
                    isExp = true;
                    parentName = potentialParent;
                }
            }
            // 模式 2: "主遊戲名稱 (擴充名稱)" 或 "主遊戲名稱 - 擴充"
            else if (game.name && (game.name.includes('(') || game.name.includes('-'))) {
                const potentialParent = game.name.split(/[()-]/)[0].trim();
                // 只有當主遊戲長度夠長且真的存在時才判定
                if (potentialParent.length >= 2 && gameMap[potentialParent] && potentialParent !== game.name) {
                    isExp = true;
                    parentName = potentialParent;
                }
            }
        }

        if (isExp && parentName && gameMap[parentName]) {
            // 確保被標記為擴充
            game.is_expansion = 'true';
            game.parent_game = parentName;

            if (!parentToExpansions[parentName]) {
                parentToExpansions[parentName] = [];
            }
            parentToExpansions[parentName].push(game);
        } else {
            rootGames.push(game);
        }
    });

    function renderGameRow(game, isChild = false, childExpansions = null) {
        const tr = document.createElement('tr');
        const hasChildren = childExpansions && childExpansions.length > 0;

        if (isChild) {
            tr.classList.add('expansion-row');
            tr.setAttribute('data-parent', game.parent_game);
        }

        if (game.status === '借出') {
            tr.classList.add('status-borrowed');
        }

        let borrowerDisplay = game.borrower || '';
        if (game.status === '借出' && game.borrower) {
            borrowerDisplay = `<strong>${game.borrower}</strong>`;
        }

        let checkboxHtml = '';
        if (isAdmin) {
            checkboxHtml = `<td><input type="checkbox" class="game-checkbox" value="${game.name}"></td>`;
        }

        const statusText = game.status === '借出' ? '借出' : '在庫';
        const statusClass = game.status === '借出' ? 'status-borrowed' : 'status-available';

        const escapedName = String(game.name || '')
            .replace(/\\/g, '\\\\')
            .replace(/'/g, "\\'")
            .replace(/"/g, '&quot;')
            .replace(/`/g, '\\`');

        const bggIcon = game.bgg_id
            ? `<span class="bgg-linked" title="已連結到 BGG (ID: ${game.bgg_id})" onclick="viewBGGGameDetails(${game.bgg_id}, \`${escapedName}\`)">🔗</span>`
            : `<span class="bgg-not-linked" title="連結到 BGG" onclick="openBGGLinkModal(\`${escapedName}\`)">➕</span>`;

        // 圖片懶載入：使用 loading="lazy" 和 Intersection Observer
        const thumbnailHtml = game.bgg_thumbnail
            ? `<img src="${game.bgg_thumbnail}" 
                    class="game-thumbnail" 
                    alt="縮圖" 
                    loading="lazy"
                    onclick="viewBGGGameDetails(${game.bgg_id}, \`${escapedName}\`)">`
            : '';

        // **關鍵修復**: 必須在使用前先宣告這些變數
        let toggleBtnHtml = '';
        let treeCellContent = '';

        if (isChild) {
            // 擴充遊戲：顯示樹狀符號
            treeCellContent = '<span class="tree-symbol">└─</span>';
        } else if (hasChildren) {
            // 主遊戲有擴充：顯示展開按鈕
            toggleBtnHtml = `<span class="toggle-expansions-btn" onclick="toggleExpansionRows(event, this, '${escapedName.replace(/'/g, "\\'")}')\" title="展開/收起擴充"></span>`;
            tr.classList.add('has-expansions');
            treeCellContent = toggleBtnHtml;
        }

        // 構建表格行內容
        tr.innerHTML = `
            ${checkboxHtml}
            <td class="tree-cell">${treeCellContent}</td>
            <td class="game-name-cell">
                <div class="game-name-wrapper">
                    ${thumbnailHtml}
                    ${bggIcon}
                    <span>${game.name}</span>
                </div>
            </td>
            <td>${(() => {
                const isExpansion = String(game.is_expansion || '').trim();

                if (isExpansion === '1' || isExpansion.toLowerCase() === 'true') {
                    return '<span class="expansion-badge">🧩 擴充</span>';
                }
                return '<span class="main-game-badge">🎮 主遊戲</span>';
            })()}</td>
            <td><span class="status-badge ${statusClass}"><span class="status-dot"></span>${statusText}</span></td>
            <td>${borrowerDisplay}</td>
            <td>${(() => {
                let displayBorrowerId = game.borrower_id || '';
                if (!displayBorrowerId && game.borrower) {
                    const borrowerName = String(game.borrower).trim();
                    displayBorrowerId = memberNameToId[borrowerName] || '';
                }
                return displayBorrowerId;
            })()}</td>
            <td>${game.custodian || ''}</td>
            <td>${formatDate(game.mdate)}</td>
            <td>${game.location || ''}</td>
            <td>${game.diff || ''}</td>
            <td>${game.players || ''}</td>
            <td class="action-cell">
                ${isAdmin ? `<button class="btn-edit" onclick="openEditGameModal('${escapeHtml(game.name)}')" title="編輯遊戲資訊"><svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/></svg></button>` : ''}
            </td>
        `;

        if (isAdmin) {
            tr.addEventListener('dblclick', () => {
                if (game.status === '借出') {
                    executeSingleReturn(game.name);
                } else {
                    executeSingleBorrow(game.name);
                }
            });
        }

        fragment.appendChild(tr);

        if (hasChildren) {
            childExpansions.forEach(exp => {
                renderGameRow(exp, true);
            });
        }
    }

    // 2. 執行根遊戲渲染
    rootGames.forEach(game => {
        renderGameRow(game, false, parentToExpansions[game.name]);
    });
    // --- 層級化邏輯結束 ---

    tbody.appendChild(fragment);

    // 更新結果數量顯示和分頁
    updateResultCount(validGames.length, pageGames.length);
    renderPagination();
}

// 更新結果數量顯示
function updateResultCount(filteredCount, displayedCount) {
    const resultCountElement = document.getElementById('resultCount');
    if (resultCountElement) {
        resultCountElement.textContent = `顯示 ${displayedCount} / 篩選 ${filteredCount} / 總共 ${allGames.length} 款桌遊`;
    }
}

// 渲染分頁控制
function renderPagination() {
    const table = document.getElementById('gameTable');
    let paginationDiv = document.getElementById('pagination');

    if (!paginationDiv) {
        paginationDiv = document.createElement('div');
        paginationDiv.id = 'pagination';
        paginationDiv.className = 'pagination';
        table.parentNode.insertBefore(paginationDiv, table.nextSibling);
    }

    if (totalPages <= 1) {
        paginationDiv.style.display = 'none';
        return;
    }

    paginationDiv.style.display = 'flex';
    paginationDiv.innerHTML = `
        <button onclick="changePage(-1)" ${currentPage === 1 ? 'disabled' : ''} class="page-btn">
            ← 上一頁
        </button>
        <span class="page-info">第 ${currentPage} / ${totalPages} 頁</span>
        <button onclick="changePage(1)" ${currentPage === totalPages ? 'disabled' : ''} class="page-btn">
            下一頁 →
        </button>
        <button onclick="jumpToPage(1)" ${currentPage === 1 ? 'disabled' : ''} class="page-btn-small">
            首頁
        </button>
        <button onclick="jumpToPage(${totalPages})" ${currentPage === totalPages ? 'disabled' : ''} class="page-btn-small">
            末頁
        </button>
    `;
}

// 切換頁面
function changePage(delta) {
    const newPage = currentPage + delta;
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        renderTable(currentFilteredGames);
        // 滾動到頂部
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// 跳轉到指定頁面
function jumpToPage(page) {
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        renderTable(currentFilteredGames);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * 切換擴充列的顯示狀態
 */
function toggleExpansionRows(event, btn, parentName) {
    if (event) event.stopPropagation();

    const isExpanded = btn.classList.contains('expanded');

    // 切換按鈕狀態
    if (isExpanded) {
        btn.classList.remove('expanded');
    } else {
        btn.classList.add('expanded');
    }

    // 找到所有對應的子列
    const tbody = btn.closest('tbody');
    const rows = tbody.querySelectorAll(`tr.expansion-row[data-parent="${parentName}"]`);

    rows.forEach(row => {
        if (isExpanded) {
            // 收起：移除 visible class
            row.classList.remove('visible');
        } else {
            // 展開：加上 visible class
            row.classList.add('visible');
        }
    });
}

// 單筆借出 (含驗證)
async function executeSingleBorrow(gameName) {
    try {
        // 1. 先驗證是否可借出（檢查擴充依賴）
        const validResp = await fetch(`/api/games/${encodeURIComponent(gameName)}/validate-borrow`);
        const validData = await validResp.json();

        if (!validData.success) {
            showToast('驗證失敗: ' + validData.error, 'error');
            return;
        }

        // 如果有訊息（警告或錯誤），需要處理
        if (validData.message) {
            if (!validData.can_borrow) {
                // 不可借出（例如：合併收納的擴充）
                alert(`❌ 無法借出\n\n${validData.message}`);
                return;
            } else {
                // 可借出但有警告（例如：獨立收納擴充提醒）
                if (!confirm(`⚠️ 提醒\n\n${validData.message}\n\n是否仍要繼續借出？`)) {
                    return;
                }
            }
        }

        // 2. 執行借出流程
        const memberId = prompt(`借出桌遊：${gameName}\n請輸入工號：`);
        if (memberId) {
            const borrowResp = await fetch('/api/borrow', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: gameName,
                    member_id: memberId
                })
            });
            const borrowData = await borrowResp.json();

            if (borrowData.success) {
                showToast('借出成功');
                loadGames();
            } else {
                showToast(borrowData.message || borrowData.error, 'error');
            }
        }
    } catch (err) {
        showToast('借出流程發生錯誤', 'error');
        console.error(err);
    }
}

// 單筆歸還
function executeSingleReturn(gameName) {
    if (confirm(`確定要歸還《${gameName}》嗎？`)) {
        fetch('/api/return', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: gameName })
        })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showToast('歸還成功');
                    loadGames();
                } else {
                    showToast(data.message || data.error, 'error');
                }
            })
            .catch(err => {
                showToast('歸還失敗', 'error');
                console.error(err);
            });
    }
}

// 篩選功能
function filterByStatus(status) {
    currentStatusFilter = status;
    document.querySelectorAll('.filter-btn').forEach(btn => {
        if (btn.dataset.filter === status) btn.classList.add('active');
        else btn.classList.remove('active');
    });
    applyCurrentFilter();
}

function filterByPlayers(players) {
    const btn = document.querySelector(`.player-btn[data-players="${players}"]`);

    if (currentPlayerFilters.has(players)) {
        // 如果已選中，則取消選中
        currentPlayerFilters.delete(players);
        btn.classList.remove('active');
    } else {
        // 如果未選中，則選中
        currentPlayerFilters.add(players);
        btn.classList.add('active');
    }

    applyCurrentFilter();
}

// 清除篩選
function clearFilters() {
    currentStatusFilter = 'all';
    currentPlayerFilters.clear(); // 清空 Set

    document.querySelectorAll('.filter-btn').forEach(btn => {
        if (btn.dataset.filter === 'all') btn.classList.add('active');
        else btn.classList.remove('active');
    });

    document.querySelectorAll('.player-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    applyCurrentFilter();
}

function applyCurrentFilter() {
    const filteredGames = allGames.filter(game => {
        const statusMatch = currentStatusFilter === 'all' || game.status === currentStatusFilter;

        // 人數篩選：如果沒有選擇任何人數（Set 為空），則顯示全部
        // AND 邏輯：遊戲必須同時符合所有選中的人數條件
        const playerMatch = currentPlayerFilters.size === 0 ||
            Array.from(currentPlayerFilters).every(filter => matchesPlayerCount(game.players, filter));

        return statusMatch && playerMatch;
    });
    renderTable(filteredGames);
}

function matchesPlayerCount(gamePlayers, filterPlayers) {
    if (!gamePlayers) return false;
    const parts = String(gamePlayers).split('-').map(p => parseInt(p.trim()));
    const min = parts[0];
    const max = parts.length > 1 ? parts[1] : min;

    if (filterPlayers === '10+') return max >= 10;
    const target = parseInt(filterPlayers);
    return target >= min && target <= max;
}

// 防抖函數
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============ 搜尋歷史功能 ============
const MAX_SEARCH_HISTORY = 10;

function getSearchHistory() {
    try {
        const history = localStorage.getItem('tableSearchHistory');
        return history ? JSON.parse(history) : [];
    } catch {
        return [];
    }
}

function saveSearchToHistory(query) {
    if (!query || query.length < 2) return; // 太短不儲存

    let history = getSearchHistory();
    history = history.filter(item => item !== query);
    history.unshift(query);

    if (history.length > MAX_SEARCH_HISTORY) {
        history = history.slice(0, MAX_SEARCH_HISTORY);
    }

    localStorage.setItem('tableSearchHistory', JSON.stringify(history));
}

function clearSearchHistory() {
    localStorage.removeItem('tableSearchHistory');
    hideSearchHistory();
}

function removeSearchHistoryItem(index) {
    let history = getSearchHistory();
    history.splice(index, 1);
    localStorage.setItem('tableSearchHistory', JSON.stringify(history));
    showSearchHistory();
}

function showSearchHistory() {
    const historyContainer = document.getElementById('tableSearchHistory');
    const history = getSearchHistory();

    if (history.length === 0) {
        historyContainer.innerHTML = '';
        historyContainer.classList.remove('show');
        return;
    }

    let html = '<div class="search-history-header">';
    html += '<span class="search-history-title">🕐 最近搜尋</span>';
    html += '<button class="search-history-clear" onclick="clearSearchHistory()">清空</button>';
    html += '</div>';
    html += '<div class="search-history-items">';

    history.forEach((item, index) => {
        html += `
            <div class="search-history-item">
                <span class="search-history-text" onclick="fillSearchBox('${escapeHtml(item)}')">${escapeHtml(item)}</span>
                <button class="search-history-delete" onclick="removeSearchHistoryItem(${index})" title="刪除">✕</button>
            </div>
        `;
    });

    html += '</div>';
    historyContainer.innerHTML = html;
    historyContainer.classList.add('show');
}

function hideSearchHistory() {
    const historyContainer = document.getElementById('tableSearchHistory');
    historyContainer.classList.remove('show');
}

function fillSearchBox(query) {
    const searchBox = document.getElementById('searchBox');
    searchBox.value = query;
    searchBox.dispatchEvent(new Event('input'));
    hideSearchHistory();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 搜尋功能 (使用防抖) - 只搜尋桌遊名稱、借閱人、工號
const searchBox = document.getElementById('searchBox');
let searchPerformed = false;

searchBox.addEventListener('input', debounce((e) => {
    const term = e.target.value.toLowerCase();

    if (!term) {
        // 空白時顯示所有遊戲
        applyCurrentFilter();
        hideSearchHistory();
        searchPerformed = false;
        return;
    }

    const filtered = allGames.filter(game => {
        // 只搜尋特定欄位：桌遊名稱、借閱人、工號
        const nameMatch = String(game.name || '').toLowerCase().includes(term);
        const borrowerMatch = String(game.borrower || '').toLowerCase().includes(term);
        const borrowerIdMatch = String(game.borrower_id || '').toLowerCase().includes(term);

        return nameMatch || borrowerMatch || borrowerIdMatch;
    });

    renderTable(filtered);
    searchPerformed = true;

    // 儲存到搜尋歷史（延遲儲存，避免每次輸入都儲存）
    if (term.length >= 2) {
        setTimeout(() => {
            if (searchBox.value === term) {
                saveSearchToHistory(term);
            }
        }, 1000);
    }
}, 50)); // 縮短延遲至 50ms，提供即時搜尋體驗

// 獲得焦點時顯示搜尋歷史
searchBox.addEventListener('focus', () => {
    if (!searchBox.value.trim()) {
        showSearchHistory();
    }
});

// 失去焦點時隱藏搜尋歷史（延遲以允許點擊歷史項目）
searchBox.addEventListener('blur', () => {
    setTimeout(hideSearchHistory, 200);
});

// 按 ESC 清空搜尋
searchBox.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        searchBox.value = '';
        searchBox.dispatchEvent(new Event('input'));
        searchBox.blur();
    }
});

// 排序功能
document.querySelectorAll('th[data-col]').forEach(th => {
    th.addEventListener('click', () => {
        const col = th.dataset.col;
        const isAsc = th.classList.contains('asc');

        document.querySelectorAll('th').forEach(t => t.classList.remove('asc', 'desc'));

        th.classList.toggle('asc', !isAsc);
        th.classList.toggle('desc', isAsc);

        const sorted = [...allGames].sort((a, b) => {
            const valA = String(a[col] || '');
            const valB = String(b[col] || '');
            return isAsc ? valB.localeCompare(valA, 'zh-Hant') : valA.localeCompare(valB, 'zh-Hant');
        });

        renderTable(sorted);
    });
});

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadGames().then(() => {
        // 初始化固定標題（在表格渲染後）
        setTimeout(() => initStickyHeader(), 100);
    });

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => filterByStatus(btn.dataset.filter));
    });

    document.querySelectorAll('.player-btn').forEach(btn => {
        btn.addEventListener('click', () => filterByPlayers(btn.dataset.players));
    });

    const clearBtn = document.getElementById('clearFiltersBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearFilters);
    }

    // Admin 頁面功能
    if (document.body.classList.contains('admin-page')) {
        // 監聽 Checkbox 變更 (限制最多選5個)
        const gameTable = document.getElementById('gameTable');
        if (gameTable) {
            gameTable.addEventListener('change', (e) => {
                if (e.target.classList.contains('game-checkbox')) {
                    const checkedCount = document.querySelectorAll('.game-checkbox:checked').length;
                    if (checkedCount > 5) {
                        e.target.checked = false;
                        showToast('單筆資料最多只能選5個', 'error');
                    }

                    // 更新全選按鈕狀態
                    const allCheckboxes = document.querySelectorAll('.game-checkbox');
                    const selectAll = document.getElementById('selectAll');
                    if (selectAll) {
                        selectAll.checked = allCheckboxes.length > 0 && checkedCount === allCheckboxes.length;
                    }
                }
            });
        }

        // 全選功能 (最多選5個)
        const selectAll = document.getElementById('selectAll');
        if (selectAll) {
            selectAll.addEventListener('click', (e) => {
                const checkboxes = document.querySelectorAll('.game-checkbox');
                const isChecked = e.target.checked;

                if (isChecked) {
                    let count = 0;
                    checkboxes.forEach(cb => {
                        if (count < 5) {
                            cb.checked = true;
                            count++;
                        } else {
                            cb.checked = false;
                        }
                    });

                    if (checkboxes.length > 5) {
                        showToast('已自動選取前5筆 (單筆上限5個)', 'warning');
                    }
                } else {
                    checkboxes.forEach(cb => cb.checked = false);
                }
            });
        }

        // 批次借出
        const batchBorrowBtn = document.getElementById('batchBorrowBtn');
        if (batchBorrowBtn) {
            batchBorrowBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const selected = Array.from(document.querySelectorAll('.game-checkbox:checked')).map(cb => cb.value);
                if (selected.length === 0) return showToast('請選擇桌遊', 'error');

                const memberId = prompt(`將借出 ${selected.length} 款桌遊，請輸入工號：`);
                if (!memberId) return;

                fetch('/api/batch-borrow', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        game_names: selected,
                        member_id: memberId
                    })
                })
                    .then(r => r.json())
                    .then(data => {
                        if (data.success) {
                            showToast('批次借出成功');
                            loadGames();
                            if (selectAll) selectAll.checked = false;
                        } else {
                            showToast(data.message || data.error, 'error');
                        }
                    });
            });
        }

        // 批次歸還
        const batchReturnBtn = document.getElementById('batchReturnBtn');
        if (batchReturnBtn) {
            batchReturnBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const selected = Array.from(document.querySelectorAll('.game-checkbox:checked')).map(cb => cb.value);
                if (selected.length === 0) return showToast('請選擇桌遊', 'error');

                if (confirm(`確定要歸還 ${selected.length} 款桌遊？`)) {
                    fetch('/api/batch-return', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ game_names: selected })
                    })
                        .then(r => r.json())
                        .then(data => {
                            if (data.success) {
                                showToast('批次歸還成功');
                                loadGames();
                                if (selectAll) selectAll.checked = false;
                            } else {
                                showToast(data.message || data.error, 'error');
                            }
                        });
                }
            });
        }
    }

    // 定期更新 (30分鐘)
    setInterval(loadGames, 1800000);
});

// ============ BGG 連結功能 ============

/**
 * 智慧清理遊戲名稱，移除常見後綴以提高 BGG 搜尋成功率
 * @param {string} gameName - 原始遊戲名稱
 * @returns {string} 清理後的遊戲名稱
 */
function cleanGameNameForBGGSearch(gameName) {
    let cleaned = gameName.trim();

    // 移除末尾的單一字母後綴（空格或無空格）如：超級犀牛A, 超級犀牛 A
    cleaned = cleaned.replace(/[\s-_]*[A-Za-z]$/, '');

    // 移除末尾的數字（空格或無空格）如：卡坦島2, 卡坦島 2
    cleaned = cleaned.replace(/[\s-_]*\d+$/, '');

    // 移除破折號後的內容（常用於版本標註）如：璀璨寶石-豪華版
    cleaned = cleaned.split(/[-_]/)[0].trim();

    return cleaned;
}

function openBGGLinkModal(gameName) {
    const cleanedName = cleanGameNameForBGGSearch(gameName);

    // 建立 Modal HTML
    const modal = document.createElement('div');
    modal.className = 'bgg-modal';
    modal.id = 'bggLinkModal';
    modal.innerHTML = `
        <div class="bgg-modal-content">
            <span class="bgg-modal-close" onclick="closeBGGLinkModal()">&times;</span>
            <h2>連結「${gameName}」到 BGG</h2>
            <div class="bgg-search-box">
                <label>搜尋關鍵字：</label>
                <div class="search-input-group">
                    <input type="text" id="bggSearchInput" value="${cleanedName}" placeholder="輸入搜尋關鍵字">
                    <button class="btn small primary" onclick="manualSearchBGG('${gameName}')">搜尋</button>
                </div>
                <p class="search-hint">💡 提示：如找不到，請嘗試英文原名或簡化名稱</p>
            </div>
            <div class="bgg-link-search">
                <p>正在搜尋 BoardGameGeek...</p>
                <div id="bggLinkResults"></div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // 自動搜尋（使用清理後的名稱）
    searchAndLinkBGG(gameName, cleanedName);
}

function closeBGGLinkModal() {
    const modal = document.getElementById('bggLinkModal');
    if (modal) {
        modal.remove();
    }
}

async function searchAndLinkBGG(originalGameName, searchQuery = null) {
    try {
        const query = searchQuery || cleanGameNameForBGGSearch(originalGameName);
        const response = await fetch(`/api/bgg/games/link/search/${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success && data.results && data.results.length > 0) {
            displayBGGLinkResults(originalGameName, data.results);
        } else {
            document.getElementById('bggLinkResults').innerHTML =
                `<p class="no-results">找不到「${query}」相關的 BGG 桌遊。<br>請嘗試修改搜尋關鍵字或使用英文名稱。</p>`;
        }
    } catch (error) {
        console.error('BGG search error:', error);
        document.getElementById('bggLinkResults').innerHTML =
            '<p class="error">搜尋時發生錯誤，請稍後再試。</p>';
    }
}

function displayBGGLinkResults(gameName, results) {
    const resultsDiv = document.getElementById('bggLinkResults');
    resultsDiv.innerHTML = '<h3>選擇要連結的桌遊：</h3>';

    results.forEach(game => {
        const card = document.createElement('div');
        card.className = 'bgg-link-card';

        // 跳脫遊戲名稱中的特殊字元以避免破壞 onclick 屬性
        const escapedGameName = gameName.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;');
        const escapedBggName = game.name.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '&quot;');

        card.innerHTML = `
            <div class="bgg-link-info">
                <h4>${game.name}</h4>
                <p>年份: ${game.year || 'N/A'} | ID: ${game.id}</p>
            </div>
            <button class="btn small primary" onclick="linkGameToBGG('${escapedGameName}', ${game.id}, '${escapedBggName}')">
                選擇此遊戲
            </button>
        `;
        resultsDiv.appendChild(card);
    });
}

function manualSearchBGG(originalGameName) {
    const searchInput = document.getElementById('bggSearchInput');
    const searchQuery = searchInput.value.trim();

    if (!searchQuery) {
        alert('請輸入搜尋關鍵字');
        return;
    }

    document.getElementById('bggLinkResults').innerHTML = '<p>正在搜尋...</p>';
    searchAndLinkBGG(originalGameName, searchQuery);
}

async function linkGameToBGG(gameName, bggId, bggName) {
    if (!confirm(`確定要將「${gameName}」連結到 BGG 的「${bggName}」(ID: ${bggId}) 嗎？`)) {
        return;
    }

    try {
        const response = await fetch(`/api/bgg/games/link/${encodeURIComponent(gameName)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bgg_id: bggId })
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ 連結成功！');
            closeBGGLinkModal();
            loadGames(); // 重新載入遊戲列表
        } else {
            showToast(data.error || '連結失敗', 'error');
        }
    } catch (error) {
        console.error('Link error:', error);
        showToast('連結時發生錯誤', 'error');
    }
}

// viewBGGGameDetails 已在 bgg.js 中定義，這裡不需要重複