#!/usr/bin/env python3
"""
程式碼庫分析工具

自動分析 Python 檔案的結構、類別、函數和依賴關係，
生成初步的文檔框架。
"""
import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Set
import json


class CodeAnalyzer:
    """程式碼分析器"""
    
    def __init__(self, project_root: str):
        """
        初始化分析器
        
        Args:
            project_root: 專案根目錄路徑
        """
        self.project_root = Path(project_root)
        self.results: Dict[str, Any] = {}
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        分析單個 Python 檔案
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            分析結果字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            result = {
                'path': str(file_path.relative_to(self.project_root)),
                'lines': len(content.splitlines()),
                'classes': [],
                'functions': [],
                'imports': [],
                'docstring': ast.get_docstring(tree) or ''
            }
            
            # 分析 AST
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or '',
                        'methods': [],
                        'line': node.lineno
                    }
                    
                    # 提取方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append({
                                'name': item.name,
                                'docstring': ast.get_docstring(item) or '',
                                'line': item.lineno
                            })
                    
                    result['classes'].append(class_info)
                
                elif isinstance(node, ast.FunctionDef):
                    # 只記錄模組層級的函數
                    if node.col_offset == 0:
                        result['functions'].append({
                            'name': node.name,
                            'docstring': ast.get_docstring(node) or '',
                            'line': node.lineno
                        })
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            result['imports'].append(alias.name)
                    else:
                        module = node.module or ''
                        result['imports'].append(module)
            
            return result
            
        except Exception as e:
            return {
                'path': str(file_path.relative_to(self.project_root)),
                'error': str(e)
            }
    
    def analyze_directory(self, directory: str, exclude_dirs: Set[str] = None) -> List[Dict[str, Any]]:
        """
        分析目錄中的所有 Python 檔案
        
        Args:
            directory: 目錄路徑
            exclude_dirs: 要排除的目錄集合
            
        Returns:
            分析結果列表
        """
        if exclude_dirs is None:
            exclude_dirs = {
                'venv', '__pycache__', '.pytest_cache', 
                'boardgame-web-master', '.git', 'node_modules'
            }
        
        results = []
        dir_path = self.project_root / directory
        
        for py_file in dir_path.rglob('*.py'):
            # 檢查是否在排除目錄中
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue
            
            result = self.analyze_file(py_file)
            results.append(result)
        
        return results
    
    def generate_markdown_doc(self, analysis_result: Dict[str, Any]) -> str:
        """
        根據分析結果生成 Markdown 文檔框架
        
        Args:
            analysis_result: 分析結果
            
        Returns:
            Markdown 文檔字串
        """
        md = []
        path = analysis_result.get('path', '')
        
        md.append(f"### 📄 {Path(path).name}\n")
        md.append(f"**路徑**: `{path}`  ")
        md.append(f"**行數**: {analysis_result.get('lines', 0)}  ")
        
        if analysis_result.get('docstring'):
            md.append(f"**描述**: {analysis_result['docstring']}\n")
        
        # 類別
        classes = analysis_result.get('classes', [])
        if classes:
            md.append("#### 核心類別\n")
            for cls in classes:
                md.append(f"- **`{cls['name']}`** (L{cls['line']})")
                if cls['docstring']:
                    md.append(f"  - {cls['docstring']}")
                
                if cls['methods']:
                    md.append("  - 方法:")
                    for method in cls['methods'][:5]:  # 只顯示前5個
                        md.append(f"    - `{method['name']}()` (L{method['line']})")
                md.append("")
        
        # 函數
        functions = analysis_result.get('functions', [])
        if functions:
            md.append("#### 主要函數\n")
            for func in functions[:5]:  # 只顯示前5個
                md.append(f"- **`{func['name']}()`** (L{func['line']})")
                if func['docstring']:
                    md.append(f"  - {func['docstring']}")
                md.append("")
        
        # 依賴
        imports = analysis_result.get('imports', [])
        if imports:
            # 只顯示專案內部的導入
            internal_imports = [imp for imp in imports if imp.startswith(('core', 'app'))]
            if internal_imports:
                md.append("#### 內部依賴\n")
                for imp in sorted(set(internal_imports))[:10]:
                    md.append(f"- `{imp}`")
                md.append("")
        
        md.append("---\n")
        
        return '\n'.join(md)
    
    def save_results(self, output_file: str):
        """
        儲存分析結果為 JSON
        
        Args:
            output_file: 輸出檔案路徑
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)


def main():
    """主函數"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方式: python analyze_codebase.py <directory>")
        print("範例: python analyze_codebase.py core")
        sys.exit(1)
    
    project_root = Path(__file__).parent.parent.parent
    analyzer = CodeAnalyzer(str(project_root))
    
    directory = sys.argv[1]
    print(f"分析目錄: {directory}")
    
    results = analyzer.analyze_directory(directory)
    
    print(f"\n找到 {len(results)} 個檔案\n")
    print("=" * 80)
    
    for result in results:
        if 'error' in result:
            print(f"❌ {result['path']}: {result['error']}")
        else:
            print(analyzer.generate_markdown_doc(result))
    
    # 儲存 JSON 結果
    output_file = project_root / 'docs' / f'{directory}_analysis.json'
    analyzer.results = {directory: results}
    analyzer.save_results(str(output_file))
    print(f"\n分析結果已儲存至: {output_file}")


if __name__ == '__main__':
    main()
