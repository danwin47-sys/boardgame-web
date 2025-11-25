const apiBase = '/api';
let allGames = [];
let currentStatusFilter = 'all';
let currentPlayerFilter = 'all';

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
        const resp = await fetch(`${apiBase}/games`);
        if (!resp.ok) throw new Error('Server error');
        allGames = await resp.json();

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

        // BGG 連結圖示
        const bggIcon = game.bgg_id
            ? `<span class="bgg-linked" title="已連結到 BGG (ID: ${game.bgg_id})" onclick="viewBGGGameDetails(${game.bgg_id})">🔗</span>`
            : `<span class="bgg-not-linked" title="連結到 BGG" onclick="openBGGLinkModal('${game.name}')">➕</span>`;

        tr.innerHTML = `
            ${checkboxHtml}
            <td>${game.name} ${bggIcon}</td>
            <td><span class="status-badge ${statusClass}"><span class="status-dot"></span>${statusText}</span></td>
            <td>${borrowerDisplay}</td>
            <td>${game.borrower_id || ''}</td>
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
    currentPlayerFilter = players;
    document.querySelectorAll('.player-btn').forEach(btn => {
        if (btn.dataset.players === players) btn.classList.add('active');
        else btn.classList.remove('active');
    });
    applyCurrentFilter();
}

// 清除篩選
function clearFilters() {
    currentStatusFilter = 'all';
    currentPlayerFilter = 'all';

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
        const playerMatch = currentPlayerFilter === 'all' || matchesPlayerCount(game.players, currentPlayerFilter);
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

// 搜尋功能 (使用防抖)
document.getElementById('searchBox').addEventListener('input', debounce((e) => {
    const term = e.target.value.toLowerCase();
    const filtered = allGames.filter(game =>
        Object.values(game).some(val =>
            String(val).toLowerCase().includes(term)
        )
    );
    renderTable(filtered);
}, 300));

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

function openBGGLinkModal(gameName) {
    // 建立 Modal HTML
    const modal = document.createElement('div');
    modal.className = 'bgg-modal';
    modal.id = 'bggLinkModal';
    modal.innerHTML = `
        <div class="bgg-modal-content">
            <span class="bgg-modal-close" onclick="closeBGGLinkModal()">&times;</span>
            <h2>連結「${gameName}」到 BGG</h2>
            <div class="bgg-link-search">
                <p>正在搜尋 BoardGameGeek...</p>
                <div id="bggLinkResults"></div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // 自動搜尋
    searchAndLinkBGG(gameName);
}

function closeBGGLinkModal() {
    const modal = document.getElementById('bggLinkModal');
    if (modal) {
        modal.remove();
    }
}

async function searchAndLinkBGG(gameName) {
    try {
        const response = await fetch(`/api/bgg/games/link/search/${encodeURIComponent(gameName)}`);
        const data = await response.json();

        if (data.success && data.results && data.results.length > 0) {
            displayBGGLinkResults(gameName, data.results);
        } else {
            document.getElementById('bggLinkResults').innerHTML =
                '<p class="no-results">找不到相關的 BGG 桌遊。請確認名稱是否正確。</p>';
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
        card.innerHTML = `
            <div class="bgg-link-info">
                <h4>${game.name}</h4>
                <p>年份: ${game.year || 'N/A'} | ID: ${game.id}</p>
            </div>
            <button class="btn small primary" onclick="linkGameToBGG('${gameName}', ${game.id}, '${game.name}')">
                選擇此遊戲
            </button>
        `;
        resultsDiv.appendChild(card);
    });
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