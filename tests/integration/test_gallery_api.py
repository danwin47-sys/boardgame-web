"""Gallery API Integration Tests"""
import pytest
from flask import json


def test_get_gallery_games_success(client):
    """測試獲取展示牆遊戲列表成功"""
    response = client.get('/api/gallery/games')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'games' in data
    assert 'total' in data
    assert isinstance(data['games'], list)


def test_get_gallery_games_with_status_filter(client):
    """測試狀態篩選功能"""
    response = client.get('/api/gallery/games?status=在庫')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] is True
    # 驗證所有返回的遊戲狀態都是"在庫"
    for game in data['games']:
        if game.get('status'):  # 有些遊戲可能沒有狀態欄位
            assert game['status'] == '在庫'


def test_game_data_structure(client):
    """測試遊戲資料結構完整性"""
    response = client.get('/api/gallery/games')
    data = json.loads(response.data)
    
    if len(data['games']) > 0:
        game = data['games'][0]
        # 必要欄位
        assert 'id' in game
        assert 'name' in game
        assert 'status' in game
        # 可選但重要的欄位
        assert 'types' in game
        assert 'tags' in game
        assert isinstance(game['types'], list)
        assert isinstance(game['tags'], list)


def test_player_range_in_games(client):
    """測試人數資訊是否正確解析"""
    response = client.get('/api/gallery/games')
    data = json.loads(response.data)
    
    # 檢查是否有遊戲包含人數資訊
    games_with_players = [g for g in data['games'] if 'minPlayers' in g]
    
    if games_with_players:
        for game in games_with_players:
            assert 'minPlayers' in game
            assert 'maxPlayers' in game
            assert isinstance(game['minPlayers'], int)
            assert isinstance(game['maxPlayers'], int)
            assert game['minPlayers'] <= game['maxPlayers']


def test_game_classification(client):
    """測試遊戲類型分類"""
    response = client.get('/api/gallery/games')
    data = json.loads(response.data)
    
    # 確保所有遊戲都有類型分類
    for game in data['games']:
        assert 'types' in game
        assert len(game['types']) > 0  # 至少有一個類型（可能是"其他"）


def test_bgg_integration(client):
    """測試 BGG 數據整合"""
    response = client.get('/api/gallery/games')
    data = json.loads(response.data)
    
    # 檢查是否有遊戲包含 BGG 資訊
    games_with_bgg = [g for g in data['games'] if 'bggId' in g]
    
    if games_with_bgg:
        # 驗證 BGG 數據結構
        for game in games_with_bgg[:5]:  # 測試前5個有BGG ID的遊戲
            assert 'bggId' in game
            # 可能包含的 BGG 額外資訊
            # 注意：這些可能不會全部存在，取決於 BGG API 狀態
            if 'bggRating' in game:
                assert isinstance(game['bggRating'], (int, float))
                assert 0 <= game['bggRating'] <= 10
