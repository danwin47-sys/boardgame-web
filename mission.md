# Agent Mission

**Objective:** Build and maintain a comprehensive boardgame management system.

## Description

This system should provide:

1. **Inventory Management**: Track boardgame collection with borrowing/returning functionality.
2. **BGG Integration**: Link games to BoardGameGeek for rich metadata (images, ratings, player counts).
3. **Member Management**: Track members, their borrowing history, and achievements.
4. **Gallery Wall**: Visual display of the game collection with filtering capabilities.
5. **Admin Features**: Secure backend for batch operations and system monitoring.

## Success Criteria

- The system reliably syncs with Google Sheets.
- BGG data is accurately retrieved and cached.
- The UI is responsive and user-friendly.
- All operations are logged for accountability.
- Test coverage maintains 80%+ for critical paths.

## Technology Stack

- **Backend**: Flask + Python 3.8+
- **Database**: Google Sheets (via gspread)
- **External APIs**: BoardGameGeek XML API
- **Frontend**: Vanilla HTML/CSS/JS
- **Testing**: pytest
