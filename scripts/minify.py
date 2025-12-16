"""
前端資源壓縮腳本
自動壓縮 CSS 和 JavaScript 檔案
"""
import os
import sys
from pathlib import Path

try:
    import rcssmin
    import jsmin
except ImportError:
    print("錯誤：缺少必要的套件")
    print("請執行：pip install rcssmin jsmin")
    sys.exit(1)


def minify_css(input_path, output_path):
    """壓縮 CSS 檔案"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        minified = rcssmin.cssmin(css_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified)
        
        original_size = len(css_content)
        minified_size = len(minified)
        reduction = (1 - minified_size / original_size) * 100
        
        print(f"✓ CSS: {input_path.name} -> {output_path.name}")
        print(f"  大小: {original_size:,} -> {minified_size:,} bytes ({reduction:.1f}% 減少)")
        
        return True
    except Exception as e:
        print(f"✗ 壓縮 CSS 失敗 {input_path}: {e}")
        return False


def minify_js(input_path, output_path):
    """壓縮 JavaScript 檔案"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        minified = jsmin.jsmin(js_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified)
        
        original_size = len(js_content)
        minified_size = len(minified)
        reduction = (1 - minified_size / original_size) * 100
        
        print(f"✓ JS: {input_path.name} -> {output_path.name}")
        print(f"  大小: {original_size:,} -> {minified_size:,} bytes ({reduction:.1f}% 減少)")
        
        return True
    except Exception as e:
        print(f"✗ 壓縮 JS 失敗 {input_path}: {e}")
        return False


def main():
    """主函數"""
    # 取得專案根目錄
    project_root = Path(__file__).parent.parent
    static_dir = project_root / 'static'
    
    css_dir = static_dir / 'css'
    js_dir = static_dir / 'js'
    
    print("=" * 60)
    print("前端資源壓縮工具")
    print("=" * 60)
    print()
    
    # 壓縮 CSS 檔案
    print("壓縮 CSS 檔案...")
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
            print(f"⚠ 檔案不存在: {css_file}")
    
    print()
    
    # 壓縮 JS 檔案
    print("壓縮 JavaScript 檔案...")
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
            print(f"⚠ 檔案不存在: {js_file}")
    
    print()
    print("=" * 60)
    print(f"完成！成功壓縮 {css_success} 個 CSS 檔案和 {js_success} 個 JS 檔案")
    print("=" * 60)


if __name__ == '__main__':
    main()
