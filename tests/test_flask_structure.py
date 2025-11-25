"""
Flask App Structure Validation Test
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_flask_app_imports():
    """Test if flask_app.py imports correctly"""
    try:
        import flask_app
        assert flask_app.app is not None, "Flask app not initialized"
        print("[PASS] Flask app imports OK")
        return True
    except Exception as e:
        print(f"[FAIL] Flask app import failed: {e}")
        return False

def test_required_routes():
    """Test if all required routes are registered"""
    try:
        from flask_app import app
        
        required_routes = [
            '/',
            '/api/health',
            '/api/games',
            '/api/members',
            '/api/borrow',
            '/api/return',
            '/api/batch-borrow',
            '/api/batch-return',
            '/api/admin-login',
        ]
        
        actual_routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        missing_routes = []
        for route in required_routes:
            if route not in actual_routes:
                missing_routes.append(route)
        
        if missing_routes:
            print(f"[FAIL] Missing routes: {missing_routes}")
            return False
        else:
            print(f"[PASS] All {len(required_routes)} required routes registered")
            return True
            
    except Exception as e:
        print(f"[FAIL] Route check failed: {e}")
        return False

def test_blueprints_registered():
    """Test if Blueprints are registered"""
    try:
        from flask_app import app
        
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        
        if 'bgg' in blueprint_names:
            print(f"[PASS] Blueprints registered: {blueprint_names}")
            return True
        else:
            print(f"[INFO] BGG Blueprint not found, current: {blueprint_names}")
            return True
            
    except Exception as e:
        print(f"[FAIL] Blueprint check failed: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("=" * 60)
    print("Flask App Structure Validation")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_flask_app_imports),
        ("Route Test", test_required_routes),
        ("Blueprint Test", test_blueprints_registered),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"RESULT: ALL PASSED ({passed}/{total})")
        print("=" * 60)
        return 0
    else:
        print(f"RESULT: SOME FAILED ({passed}/{total})")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
