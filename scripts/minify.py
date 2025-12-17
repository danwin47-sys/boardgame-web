# -*- coding: utf-8 -*-
"""
Frontend Resource Minifier
Automatically minify CSS and JavaScript files
"""
import os
import sys
from pathlib import Path

try:
    import rcssmin  # type: ignore
    import jsmin  # type: ignore
except ImportError:
    print("Error: Missing required packages")
    print("Please run: pip install rcssmin jsmin")
    sys.exit(1)


def minify_css(input_path, output_path):
    """Minify CSS file"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        minified = rcssmin.cssmin(css_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified)
        
        original_size = len(css_content)
        minified_size = len(minified)
        reduction = (1 - minified_size / original_size) * 100
        
        print(f"[OK] CSS: {input_path.name} -> {output_path.name}")
        print(f"  Size: {original_size:,} -> {minified_size:,} bytes ({reduction:.1f}% reduction)")
        
        return True
    except Exception as e:
        print(f"[FAIL] CSS minify failed {input_path}: {e}")
        return False


def minify_js(input_path, output_path):
    """Minify JavaScript file"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        minified = jsmin.jsmin(js_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified)
        
        original_size = len(js_content)
        minified_size = len(minified)
        reduction = (1 - minified_size / original_size) * 100
        
        print(f"[OK] JS: {input_path.name} -> {output_path.name}")
        print(f"  Size: {original_size:,} -> {minified_size:,} bytes ({reduction:.1f}% reduction)")
        
        return True
    except Exception as e:
        print(f"[FAIL] JS minify failed {input_path}: {e}")
        return False


def main():
    """Main function"""
    # Get project root directory
    project_root = Path(__file__).parent.parent
    static_dir = project_root / 'static'
    
    css_dir = static_dir / 'css'
    js_dir = static_dir / 'js'
    
    print("=" * 60)
    print("Frontend Resource Minifier")
    print("=" * 60)
    print()
    
    # Minify CSS files
    print("Minifying CSS files...")
    print("-" * 60)
    
    css_files = [
        'style.css',
        'bgg-style.css',
        'bgg-recommendations.css',
        'search.css',
        'lazy-load.css'
    ]
    
    css_success = 0
    for css_file in css_files:
        input_path = css_dir / css_file
        if input_path.exists():
            output_path = css_dir / css_file.replace('.css', '.min.css')
            if minify_css(input_path, output_path):
                css_success += 1
        else:
            print(f"[WARN] File not found: {css_file}")
    
    print()
    
    # Minify JS files
    print("Minifying JavaScript files...")
    print("-" * 60)
    
    js_files = [
        'script.js',
        'bgg.js',
        'search.js',
        'lazy-load.js',
        'gallery.js'
    ]
    
    js_success = 0
    for js_file in js_files:
        input_path = js_dir / js_file
        if input_path.exists():
            output_path = js_dir / js_file.replace('.js', '.min.js')
            if minify_js(input_path, output_path):
                js_success += 1
        else:
            print(f"[WARN] File not found: {js_file}")
    
    print()
    print("=" * 60)
    print(f"Done! Successfully minified {css_success} CSS and {js_success} JS files")
    print("=" * 60)


if __name__ == '__main__':
    main()
