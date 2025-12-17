/**
 * admin.js
 * 處理管理者系統的遊戲編輯與擴充管理邏輯
 */

// 編輯遊戲 Modal 相關功能
let currentEditingGame = null;

/**
 * 開啟編輯遊戲 Modal
 * @param {string} gameName - 遊戲名稱
 */
async function openEditGameModal(gameName) {
    const modal = document.getElementById('editGameModal');
    if (!modal) return;

    // 清空並顯示載入中
    document.getElementById('editGameForm').reset();
    currentEditingGame = gameName;
    document.getElementById('editGameTitle').textContent = `編輯桌遊：${gameName}`;

    // 顯示 Modal
    modal.classList.add('show');

    try {
        // 載入遊戲詳細資料 (包含家族資訊)
        const response = await fetch(`/api/games/${encodeURIComponent(gameName)}/family`);
        const data = await response.json();

        if (data.success) {
            populateEditForm(data);
        } else {
            showToast('無法載入遊戲資料', 'error');
            closeEditGameModal();
        }
    } catch (e) {
        console.error('載入遊戲資料失敗:', e);
        showToast('載入失敗', 'error');
        closeEditGameModal();
    }
}

/**
 * 關閉編輯遊戲 Modal
 */
function closeEditGameModal() {
    const modal = document.getElementById('editGameModal');
    if (modal) {
        modal.classList.remove('show');
    }
    currentEditingGame = null;
}

/**
 * 填充編輯表單
 */
function populateEditForm(data) {
    const game = data.parent && data.parent.name === currentEditingGame ? data.parent :
        (data.expansions.find(e => e.name === currentEditingGame) || { name: currentEditingGame });

    // 設定遊戲類型 (主遊戲/擴充)
    const isExpansion = (game.is_expansion === '1' || String(game.is_expansion).toLowerCase() === 'true');
    document.querySelector('input[name="gameType"][value="main"]').checked = !isExpansion;
    document.querySelector('input[name="gameType"][value="expansion"]').checked = isExpansion;

    // 設定其他欄位
    updateFormVisibility();

    if (isExpansion) {
        const parentName = game.parent_game || '';
        document.getElementById('parentGameInput').value = parentName;

        const storageMode = game.storage_mode || 'independent';
        document.getElementById('storageMode').value = storageMode;
    }

    // 處理 BGG 載入按鈕
    const bggBtn = document.getElementById('loadBggBtn');
    if (game.bgg_id) {
        bggBtn.style.display = 'inline-block';
        bggBtn.onclick = () => loadBggInfo(game.bgg_id);
    } else {
        bggBtn.style.display = 'none';
    }
}

/**
 * 從 BGG 載入擴充資訊
 */
async function loadBggInfo(bggId) {
    if (!confirm('確定要從 BGG 載入資訊嗎？這將會覆蓋目前的設定。')) return;

    try {
        const response = await fetch(`/api/bgg/games/${bggId}`);
        const data = await response.json();

        if (data.success && data.game) {
            const game = data.game;

            if (game.is_expansion) {
                // 切換為擴充
                const expansionRadio = document.querySelector('input[name="gameType"][value="expansion"]');
                if (expansionRadio) {
                    expansionRadio.checked = true;
                }
                updateFormVisibility();

                // 填入主遊戲
                if (game.parent_game) {
                    document.getElementById('parentGameInput').value = game.parent_game;
                }

                showToast('已從 BGG 載入擴充資訊');
            } else {
                // 切換為主遊戲
                const mainRadio = document.querySelector('input[name="gameType"][value="main"]');
                if (mainRadio) {
                    mainRadio.checked = true;
                }
                updateFormVisibility();
                showToast('BGG 顯示此遊戲為主遊戲');
            }
        } else {
            showToast('無法取得 BGG 資訊', 'error');
        }
    } catch (e) {
        console.error('BGG 載入失敗:', e);
        showToast('連線失敗', 'error');
    }
}

/**
 * 更新表單顯示狀態 (根據選擇的類型)
 */
function updateFormVisibility() {
    const isExpansion = document.querySelector('input[name="gameType"][value="expansion"]').checked;
    const expansionFields = document.getElementById('expansionFields');

    if (isExpansion) {
        expansionFields.style.display = 'block';
    } else {
        expansionFields.style.display = 'none';
    }
}

/**
 * 儲存遊戲變更
 */
async function saveGameChanges() {
    if (!currentEditingGame) return;

    const isExpansion = document.querySelector('input[name="gameType"][value="expansion"]').checked;
    const submitData = {
        name: currentEditingGame,
        is_expansion: isExpansion,
        parent_game: isExpansion ? document.getElementById('parentGameInput').value.trim() : '',
        storage_mode: isExpansion ? document.getElementById('storageMode').value : ''
    };

    try {
        const response = await fetch('/api/admin/games/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(submitData)
        });

        const data = await response.json();

        if (data.success) {
            showToast('儲存成功');
            closeEditGameModal();
            loadGames(); // 重新載入列表
        } else {
            showToast(data.error || '儲存失敗', 'error');
        }
    } catch (e) {
        console.error('儲存失敗:', e);
        showToast('系統錯誤', 'error');
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 綁定 Radio Button 切換事件
    document.querySelectorAll('input[name="gameType"]').forEach(radio => {
        radio.addEventListener('change', updateFormVisibility);
    });
});
