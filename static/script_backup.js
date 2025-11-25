const apiBase = '/api';
let allGames = [];
let currentStatusFilter = 'all';
let currentPlayerFilter = 'all';

// Toast ?�知系統
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => { toast.classList.remove('show'); }, 3000);
}

// ?�新統�?資�?
function updateStats() {
    document.getElementById('totalCount').textContent = allGames.length;
    document.getElementById('availableCount').textContent = allGames.filter(g => g.status !== '?�出').length;
    document.getElementById('borrowedCount').textContent = allGames.filter(g => g.status === '?�出').length;
    document.getElementById('unstockedCount').textContent = allGames.filter(g => g.status === '?�入�?).length;
}

// 載入桌�?資�?
async function loadGames() {
    try {
        const resp = await fetch(`${apiBase}/games`);
        if (!resp.ok) throw new Error('Server error');
        allGames = await resp.json();

        updateStats();
        applyCurrentFilter();

        // ?�新?�後更?��???
        const now = new Date();
        const timeString = now.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
        const timeElement = document.getElementById('lastUpdateTime');
        if (timeElement) {
            timeElement.textContent = `?�後更?��?${timeString}`;
        }
    } catch (e) {
        console.error("載入失�?:", e);
        showToast('載入資�?失�?', 'error');
    }
}

// 渲�?表格
function renderTable(games) {
    const tbody = document.querySelector('#gameTable tbody');
    tbody.innerHTML = '';

    const isAdmin = document.body.classList.contains('admin-page');

    games.forEach(game => {
        const tr = document.createElement('tr');

        // ?��??�?�設定樣�?
        if (game.status === '?�出') {
            tr.classList.add('status-borrowed');
        }

        // ?��??�閱人顯�?
        let borrowerDisplay = game.borrower || '';
        if (game.status === '?�出' && game.borrower) {
            borrowerDisplay = `<strong>${game.borrower}</strong>`;
        }

        let checkboxHtml = '';
        if (isAdmin) {
            checkboxHtml = `<td><input type="checkbox" class="game-checkbox" value="${game.name}"></td>`;
        }

        tr.innerHTML = `
            ${checkboxHtml}
            <td>${game.name}</td>
            <td><span class="status-badge ${game.status === '?�出' ? 'status-borrowed' : 'status-available'}">${game.status}</span></td>
            <td>${borrowerDisplay}</td>
            <td>${game.borrower_id || ''}</td>
            <td>${game.custodian || ''}</td>
            <td>${game.mdate || ''}</td>
            <td>${game.location || ''}</td>
            <td>${game.diff || ''}</td>
            <td>${game.players || ''}</td>
        `;

        if (isAdmin) {
            // ?��??�出/歸�? (?��?管�???
            tr.addEventListener('dblclick', () => {
                if (game.status === '?�出') {
                    executeSingleReturn(game.name);
                } else {
                    executeSingleBorrow(game.name);
                }
            });
        }

        tbody.appendChild(tr);
    });

    // ?�新結�??��?顯示
    const resultCountElement = document.getElementById('resultCount');
    if (resultCountElement) {
        resultCountElement.textContent = `顯示 ${games.length} / 總共 ${allGames.length} 款�??�`;
    }
}

// ?��??��??�出
function executeSingleBorrow(gameName) {
    const memberId = prompt(`請輸?�借閱??{gameName}?��?工�?：`);
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
                    showToast('?�出?��?');
                    loadGames();
                } else {
                    showToast(data.message || data.error, 'error');
                }
            })
            .catch(err => {
                showToast('?�出失�?', 'error');
                console.error(err);
            });
    }
}

// ?��??��?歸�?
function executeSingleReturn(gameName) {
    if (confirm(`確�?要歸?��?{gameName}?��?？`)) {
        fetch('/api/return', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: gameName })
        })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    showToast('歸�??��?');
                    loadGames();
                } else {
                    showToast(data.message || data.error, 'error');
                }
            })
            .catch(err => {
                showToast('歸�?失�?', 'error');
                console.error(err);
            });
    }
}

// 篩選?�能
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

// ?��??�能
document.getElementById('searchBox').addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = allGames.filter(game =>
        Object.values(game).some(val =>
            String(val).toLowerCase().includes(term)
        )
    );
    renderTable(filtered);
});

// ?��??�能
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

// ?��???
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

    // Admin ?�面?�能
    if (document.body.classList.contains('admin-page')) {
        // ?�選?�能
        const selectAll = document.getElementById('selectAll');
        if (selectAll) {
            selectAll.addEventListener('change', (e) => {
                document.querySelectorAll('.game-checkbox').forEach(cb => cb.checked = e.target.checked);
            });
        }

        // ?�次?�出
        const batchBorrowBtn = document.getElementById('batchBorrowBtn');
        if (batchBorrowBtn) {
            batchBorrowBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const selected = Array.from(document.querySelectorAll('.game-checkbox:checked')).map(cb => cb.value);
                if (selected.length === 0) return showToast('請�??��?桌�?', 'error');

                const memberId = prompt(`將借出 ${selected.length} 款�??��?請輸?�工?��?`);
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
                            showToast('?�次?�出?��?');
                            loadGames();
                            if (selectAll) selectAll.checked = false;
                        } else {
                            showToast(data.message || data.error, 'error');
                        }
                    });
            });
        }

        // ?�次歸�?
        const batchReturnBtn = document.getElementById('batchReturnBtn');
        if (batchReturnBtn) {
            batchReturnBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const selected = Array.from(document.querySelectorAll('.game-checkbox:checked')).map(cb => cb.value);
                if (selected.length === 0) return showToast('請�??��?桌�?', 'error');

                if (confirm(`確�?要歸?��?${selected.length} 款�??��?？`)) {
                    fetch('/api/batch-return', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ game_names: selected })
                    })
                        .then(r => r.json())
                        .then(data => {
                            if (data.success) {
                                showToast('?�次歸�??��?');
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

    // ?��??�新?��? (�?0?��?)
    setInterval(loadGames, 1800000);
});
