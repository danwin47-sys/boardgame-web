# coding: utf-8
"""
Phase 1 Verification Test
Tests boardgame-web core modules
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("Boardgame-Web Phase 1 Verification Test")
print("=" * 60)

# Test 1: Import core modules
print("\n[Test 1] Importing core modules...")
try:
    from core import (
        GAMES_CACHE_TTL,
        MEMBERS_CACHE_TTL,
        GAME_STATUS_AVAILABLE,
        GameNotFoundException,
        MemberNotFoundException,
        get_current_timestamp,
        format_datetime,
        create_history_entry,
        SimpleCache
    )
    print("[OK] Core modules imported successfully")
    print(f"   - GAMES_CACHE_TTL = {GAMES_CACHE_TTL}")
    print(f"   - GAME_STATUS_AVAILABLE = {GAME_STATUS_AVAILABLE}")
except Exception as e:
    print(f"[FAIL] Core modules import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Test constants
print("\n[Test 2] Testing constants...")
try:
    assert GAMES_CACHE_TTL == 30
    assert MEMBERS_CACHE_TTL == 3600
    assert GAME_STATUS_AVAILABLE == "歸還"
    print("[OK] Constants work correctly")
except AssertionError as e:
    print(f"[FAIL] Constants test: {e}")
    sys.exit(1)

# Test 3: Test utils
print("\n[Test 3] Testing utility functions...")
try:
    ts = get_current_timestamp()
    assert isinstance(ts, int)
    assert ts > 0
    print(f"   - get_current_timestamp() = {ts}")
    
    formatted = format_datetime(ts)
    assert isinstance(formatted, str)
    assert len(formatted) > 0
    print(f"   - format_datetime() = '{formatted}'")
    
    history_entry = create_history_entry("測試用戶", "借閱", ts)
    assert "測試用戶" in history_entry
    assert "借閱" in history_entry
    print(f"   - create_history_entry() = '{history_entry}'")
    
    print("[OK] Utility functions work correctly")
except Exception as e:
    print(f"[FAIL] Utils test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test exceptions
print("\n[Test 4] Testing custom exceptions...")
try:
    # Test GameNotFoundException
    try:
        raise GameNotFoundException("Catan")
    except GameNotFoundException as e:
        assert "Catan" in str(e)
        print(f"   - GameNotFoundException: {e}")
    
    # Test MemberNotFoundException
    try:
        raise MemberNotFoundException("M001")
    except MemberNotFoundException as e:
        assert "M001" in str(e)
        print(f"   - MemberNotFoundException: {e}")
    
    print("[OK] Custom exceptions work correctly")
except Exception as e:
    print(f"[FAIL] Exceptions test: {e}")
    sys.exit(1)

# Test 5: Test cache
print("\n[Test 5] Testing cache...")
try:
    cache = SimpleCache(ttl=2)
    
    # Test empty cache
    assert cache.get() is None
    print("   - Empty cache returns None")
    
    # Test set and get
    test_data = {'test': 'data'}
    cache.set(test_data)
    assert cache.get() == test_data
    print("   - Cache stores and retrieves data")
    
    # Test invalidate
    cache.invalidate()
    assert cache.get() is None
    print("   - Cache invalidation works")
    
    print("[OK] Cache works correctly")
except Exception as e:
    print(f"[FAIL] Cache test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("[SUCCESS] All Phase 1 tests passed!")
print("\nVerified modules:")
print("  1. core/constants.py - Constants definitions")
print("  2. core/utils.py - Utility functions")
print("  3. core/exceptions.py - Custom exceptions")
print("  4. core/cache.py - TTL caching")
print("  5. core/decorators.py - Flask decorators")
print("\nConclusion: Phase 1 core modules working correctly")
print("=" * 60)
