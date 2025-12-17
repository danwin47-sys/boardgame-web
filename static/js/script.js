const apiBase = '/api';
let allGames = [];
let allMembers = []; // 儲存所有會員資料
let memberNameToId = {}; // 姓名到工號的映射表
let currentStatusFilter = 'all';
let currentPlayerFilters = new Set(); // 使用 Set 儲存多個人數條件

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
    document.getElementById('availableCount').textContent = allGames.filter(g => g.status !== '借出').length;
    document.getElementById('borrowedCount').textContent = allGames.filter(g => g.status === '借出').length;
    document.getElementById('unstockedCount').textContent = allGames.filter(g => g.status === '未入庫').length;
}

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

    games.forEach(game => {
        const tr = document.createElement('tr');

        // 根據狀態設定樣式
        if (game.status === '借出') {
            tr.classList.add('status-borrowed');
        }

        // 借閱人顯示
        let borrowerDisplay = game.borrower || '';
        if (game.status === '借出' && game.borrower) {
            borrowerDisplay = `<strong>${game.borrower}</strong>`;
        }

        let checkboxHtml = '';
        if (isAdmin) {
            checkboxHtml = `<td><input type="checkbox" class="game-checkbox" value="${game.name}"></td>`;
        }

        // 狀態顯示：借出顯示"借出"，其他顯示"在庫"
        const statusText = game.status === '借出' ? '借出' : '在庫';
        const statusClass = game.status === '借出' ? 'status-borrowed' : 'status-available';

        // BGG 連結圖示 - 改進字串跳脫以處理特殊字元
        const escapedName = String(game.name || '')
            .replace(/\\/g, '\\\\')   // 反斜線
            .replace(/'/g, "\\'")     // 單引號
            .replace(/"/g, '&quot;')  // 雙引號
            .replace(/`/g, '\\`');    // 反引號
        const bggIcon = game.bgg_id
            ? `<span class="bgg-linked" title="已連結到 BGG (ID: ${game.bgg_id})" onclick="viewBGGGameDetails(${game.bgg_id}, \`${escapedName}\`)">🔗</span>`
            : `<span class="bgg-not-linked" title="連結到 BGG" onclick="openBGGLinkModal(\`${escapedName}\`)">➕</span>`;

        // BGG 縮圖
        const thumbnailHtml = game.bgg_thumbnail
            ? `<img src="${game.bgg_thumbnail}" class="game-thumbnail" alt="縮圖" onclick="viewBGGGameDetails(${game.bgg_id}, \`${escapedName}\`)">`
            : '';

        tr.innerHTML = `
            ${checkboxHtml}
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
                // 自動根據借閱人顯示工號
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
        `;

        if (isAdmin) {
            // 雙擊借出/歸還 (僅管理者)
            tr.addEventListener('dblclick', () => {
                if (game.status === '借出') {
                    executeSingleReturn(game.name);
                } else {
                    executeSingleBorrow(game.name);
                }
            });
        }

        fragment.appendChild(tr);
    });

    tbody.appendChild(fragment);

    // 更新結果數量顯示
    const resultCountElement = document.getElementById('resultCount');
    if (resultCountElement) {
        resultCountElement.textContent = `顯示 ${games.length} / 總共 ${allGames.length} 款桌遊`;
    }
}

// 單筆借出
function executeSingleBorrow(gameName) {
    const memberId = prompt(`借出桌遊：${gameName}\n請輸入工號：`);
    if (memberId) {
        fetch('/api/borrow', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: gameName,
                member_id: memberId
            })
        })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showToast('借出成功');
                    loadGames();
                } else {
                    showToast(data.message || data.error, 'error');
                }
            })
            .catch(err => {
                showToast('借出失敗', 'error');
                console.error(err);
            });
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
    loadGames();

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