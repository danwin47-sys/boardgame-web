# coding: utf-8
"""
API 文件模組

提供 OpenAPI 規格的 API 文件，可透過 /api/docs 查看。
"""
from typing import Any, Dict

from flask import Blueprint, jsonify

api_docs_bp = Blueprint("api_docs", __name__, url_prefix="/api")


def get_api_spec() -> Dict[str, Any]:
    """取得 OpenAPI 3.0 規格"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Boardgame-Web API",
            "description": "桌遊管理系統 API 文件",
            "version": "3.0.0",
            "contact": {"name": "Boardgame-Web Team"},
        },
        "servers": [{"url": "/", "description": "本地伺服器"}],
        "paths": {
            "/api/games": {
                "get": {
                    "summary": "取得所有遊戲",
                    "tags": ["Games"],
                    "responses": {"200": {"description": "遊戲列表"}},
                }
            },
            "/api/games/borrow": {
                "post": {
                    "summary": "借用遊戲",
                    "tags": ["Games"],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "user_name": {"type": "string"},
                                        "user_id": {"type": "string"},
                                    },
                                    "required": ["name", "user_name", "user_id"],
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "借用成功"},
                        "400": {"description": "請求錯誤"},
                        "404": {"description": "遊戲不存在"},
                    },
                }
            },
            "/api/games/return": {
                "post": {
                    "summary": "歸還遊戲",
                    "tags": ["Games"],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"name": {"type": "string"}},
                                    "required": ["name"],
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "歸還成功"}},
                }
            },
            "/api/members": {
                "get": {
                    "summary": "取得所有會員",
                    "tags": ["Members"],
                    "responses": {"200": {"description": "會員列表"}},
                }
            },
            "/api/bgg/search": {
                "get": {
                    "summary": "搜尋 BGG 遊戲",
                    "tags": ["BGG"],
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "搜尋關鍵字",
                        }
                    ],
                    "responses": {"200": {"description": "搜尋結果"}},
                }
            },
            "/api/bgg/hot": {
                "get": {
                    "summary": "取得 BGG 熱門遊戲",
                    "tags": ["BGG"],
                    "responses": {"200": {"description": "熱門遊戲列表"}},
                }
            },
            "/api/bgg/add-to-collection": {
                "post": {
                    "summary": "加入遊戲到館藏",
                    "tags": ["BGG"],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "game_id": {"type": "integer"},
                                        "custodian": {"type": "string"},
                                        "force": {"type": "boolean"},
                                    },
                                    "required": ["game_id"],
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "加入成功"},
                        "409": {"description": "遊戲已存在"},
                    },
                }
            },
            "/api/gallery/games": {
                "get": {
                    "summary": "取得圖庫遊戲列表",
                    "tags": ["Gallery"],
                    "parameters": [
                        {
                            "name": "status",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "狀態過濾",
                        }
                    ],
                    "responses": {"200": {"description": "遊戲列表"}},
                }
            },
            "/health": {
                "get": {
                    "summary": "健康檢查",
                    "tags": ["System"],
                    "responses": {"200": {"description": "服務正常"}},
                }
            },
        },
        "tags": [
            {"name": "Games", "description": "遊戲管理 API"},
            {"name": "Members", "description": "會員管理 API"},
            {"name": "BGG", "description": "BoardGameGeek 整合 API"},
            {"name": "Gallery", "description": "圖庫 API"},
            {"name": "System", "description": "系統 API"},
        ],
    }


@api_docs_bp.route("/docs")
def api_docs():
    """API 文件頁面（Swagger UI）"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Boardgame-Web API Docs</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: "/api/openapi.json",
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
            layout: "BaseLayout"
        });
    </script>
</body>
</html>
"""


@api_docs_bp.route("/openapi.json")
def openapi_spec():
    """取得 OpenAPI JSON 規格"""
    return jsonify(get_api_spec())
