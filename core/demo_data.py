"""
BGG 演示資料模組
包含用於演示模式的範例桌遊資料
"""

# 演示用的範例桌遊搜尋結果
DEMO_GAMES = {
    'catan': [
        {'id': 13, 'name': 'Catan', 'year': 1995, 'type': 'boardgame'},
        {'id': 278, 'name': 'Catan: Cities & Knights', 'year': 1998, 'type': 'boardgameexpansion'},
        {'id': 926, 'name': 'Catan: Seafarers', 'year': 1997, 'type': 'boardgameexpansion'},
    ],
    'pandemic': [
        {'id': 30549, 'name': 'Pandemic', 'year': 2008, 'type': 'boardgame'},
        {'id': 110308, 'name': 'Pandemic Legacy: Season 1', 'year': 2015, 'type': 'boardgame'},
    ],
    '7 wonders': [
        {'id': 68448, 'name': '7 Wonders', 'year': 2010, 'type': 'boardgame'},
        {'id': 149526, 'name': '7 Wonders Duel', 'year': 2015, 'type': 'boardgame'},
    ],
    'ticket to ride': [
        {'id': 9209, 'name': 'Ticket to Ride', 'year': 2004, 'type': 'boardgame'},
        {'id': 14996, 'name': 'Ticket to Ride: Europe', 'year': 2005, 'type': 'boardgame'},
    ],
    'default': [
        {'id': 13, 'name': 'Catan', 'year': 1995, 'type': 'boardgame'},
        {'id': 30549, 'name': 'Pandemic', 'year': 2008, 'type': 'boardgame'},
        {'id': 68448, 'name': '7 Wonders', 'year': 2010, 'type': 'boardgame'},
    ]
}


# 演示用的詳細遊戲資料
DEMO_GAME_DETAILS = {
    13: {  # Catan
        'id': 13,
        'name': 'Catan',
        'year': 1995,
        'description': '《卡坦島》是一款多人桌上遊戲，由Klaus Teuber設計。玩家扮演島上的開拓者，透過收集資源、建立聚落和道路來獲得勝利點數。',
        'image': 'https://placehold.co/400x300/4F46E5/FFFFFF/png?text=Catan',
        'thumbnail': 'https://placehold.co/200x150/4F46E5/FFFFFF/png?text=Catan',
        'min_players': 3,
        'max_players': 4,
        'players_display': '3-4',
        'playing_time': 120,
        'playing_time_display': '120 分鐘',
        'min_age': 10,
        'rating_average': 7.12,
        'rating_bayes_average': 7.12,
        'rating_users': 91234,
        'rank': 371,
        'categories': ['經濟', '談判'],
        'mechanics': ['擲骰', '交易', '網絡建設'],
        'designers': ['Klaus Teuber'],
        'artists': ['Volkan Baga', 'Tanja Donner'],
        'publishers': ['Kosmos', '999 Games']
    },
    30549: {  # Pandemic
        'id': 30549,
        'name': 'Pandemic',
        'year': 2008,
        'description': '《瘟疫危機》是一款合作遊戲，玩家必須共同對抗四種致命疾病的爆發。遊戲中玩家扮演不同角色，利用各自的特殊能力來治療疾病、建立研究站，並找到解藥。',
        'image': 'https://placehold.co/400x300/DC2626/FFFFFF/png?text=Pandemic',
        'thumbnail': 'https://placehold.co/200x150/DC2626/FFFFFF/png?text=Pandemic',
        'min_players': 2,
        'max_players': 4,
        'players_display': '2-4',
        'playing_time': 45,
        'playing_time_display': '45 分鐘',
        'min_age': 8,
        'rating_average': 7.61,
        'rating_bayes_average': 7.61,
        'rating_users': 89456,
        'rank': 72,
        'categories': ['醫療', '合作'],
        'mechanics': ['手牌管理', '點對點移動', '設定收集'],
        'designers': ['Matt Leacock'],
        'artists': ['Joshua Cappel', 'Christian Hanisch'],
        'publishers': ['Z-Man Games', 'Asmodee']
    }
}
