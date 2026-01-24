#!/usr/bin/env python3
"""
ISO 27001 自動化證據生成工具

此工具用於自動化生成 ISO 27001 證據文件，包括：
- 從模板生成帶有時間戳記的證據紀錄
- 支援 JSON/YAML 格式的數據填充
- 自動歸檔至正確的路徑
- 合規性檢查和報告生成
"""

import os
import sys
import json
import yaml
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template


class ISOAutomation:
    """ISO 27001 自動化工具核心類別"""
    
    def __init__(self, base_path: str = None):
        """
        初始化自動化工具
        
        Args:
            base_path: 專案根目錄路徑，預設為當前目錄
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.evidence_path = self.base_path / "記錄與證據"
        self.checklist_path = self.base_path / "ISO 27001 合規稽核清單.md"
        
    def list_templates(self, category: str = None) -> List[Path]:
        """
        列出所有可用的模板
        
        Args:
            category: 證據類別（如：備份與復原），留空則列出所有
            
        Returns:
            模板檔案路徑列表
        """
        templates = []
        
        if category:
            category_path = self.evidence_path / category
            if category_path.exists():
                templates = list(category_path.glob("*_Template.md"))
        else:
            templates = list(self.evidence_path.glob("**/*_Template.md"))
            
        return sorted(templates)
    
    def load_template(self, template_path: Path) -> str:
        """
        讀取模板內容
        
        Args:
            template_path: 模板檔案路徑
            
        Returns:
            模板內容字串
        """
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def fill_template(self, template_content: str, data: Dict[str, Any]) -> str:
        """
        使用 Jinja2 填充模板
        
        Args:
            template_content: 模板內容
            data: 要填充的數據字典
            
        Returns:
            填充後的內容
        """
        # 添加當前日期和時間到數據中
        data['current_date'] = datetime.now().strftime('%Y年%m月%d日')
        data['current_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['current_year'] = datetime.now().strftime('%Y')
        data['current_month'] = datetime.now().strftime('%m')
        data['current_day'] = datetime.now().strftime('%d')
        
        # 創建 Jinja2 模板
        template = Template(template_content)
        
        # 渲染模板
        return template.render(**data)
    
    def generate_filename(self, template_name: str, date: datetime = None) -> str:
        """
        根據模板名稱生成帶時間戳的檔名
        
        Args:
            template_name: 模板名稱（如：備份執行紀錄_Template.md）
            date: 日期，預設為當前日期
            
        Returns:
            生成的檔名（如：備份執行紀錄_20260124.md）
        """
        if date is None:
            date = datetime.now()
            
        # 移除 _Template 後綴
        base_name = template_name.replace('_Template.md', '')
        
        # 添加日期戳記
        timestamp = date.strftime('%Y%m%d')
        return f"{base_name}_{timestamp}.md"
    
    def get_archive_path(self, category: str, filename: str, date: datetime = None) -> Path:
        """
        根據類別和檔名生成歸檔路徑
        
        Args:
            category: 證據類別
            filename: 檔案名稱
            date: 日期，預設為當前日期
            
        Returns:
            完整的歸檔路徑（如：記錄與證據/備份與復原/2026/01/備份執行紀錄_20260124.md）
        """
        if date is None:
            date = datetime.now()
            
        year = date.strftime('%Y')
        month = date.strftime('%m')
        
        archive_path = self.evidence_path / category / year / month
        return archive_path / filename
    
    def ensure_directory(self, path: Path):
        """
        確保目錄存在，不存在則創建
        
        Args:
            path: 目錄路徑
        """
        path.mkdir(parents=True, exist_ok=True)
    
    def generate_evidence(self, template_path: Path, data: Dict[str, Any], 
                         output_path: Path = None, auto_archive: bool = True) -> Path:
        """
        生成證據文件
        
        Args:
            template_path: 模板路徑
            data: 填充數據
            output_path: 輸出路徑（如果指定，則不使用自動歸檔）
            auto_archive: 是否自動歸檔
            
        Returns:
            生成的檔案路徑
        """
        # 讀取模板
        template_content = self.load_template(template_path)
        
        # 填充模板
        filled_content = self.fill_template(template_content, data)
        
        # 決定輸出路徑
        if output_path:
            final_path = output_path
        elif auto_archive:
            # 獲取類別
            category = template_path.parent.name
            
            # 生成檔名
            filename = self.generate_filename(template_path.name)
            
            # 獲取歸檔路徑
            final_path = self.get_archive_path(category, filename)
        else:
            raise ValueError("必須指定 output_path 或啟用 auto_archive")
        
        # 確保目錄存在
        self.ensure_directory(final_path.parent)
        
        # 寫入檔案
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(filled_content)
        
        return final_path
    
    def load_data(self, data_path: Path) -> Dict[str, Any]:
        """
        從 JSON 或 YAML 檔案載入數據
        
        Args:
            data_path: 數據檔案路徑
            
        Returns:
            數據字典
        """
        with open(data_path, 'r', encoding='utf-8') as f:
            if data_path.suffix in ['.json']:
                return json.load(f)
            elif data_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                raise ValueError(f"不支援的檔案格式: {data_path.suffix}")
    
    def scan_compliance(self) -> Dict[str, Any]:
        """
        掃描目錄結構，檢查合規性
        
        Returns:
            合規性檢查報告
        """
        report = {
            'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'categories': {},
            'summary': {
                'total_categories': 0,
                'total_templates': 0,
                'total_records': 0,
                'categories_with_records': 0,
            }
        }
        
        # 掃描所有類別
        if not self.evidence_path.exists():
            report['error'] = f"證據路徑不存在: {self.evidence_path}"
            return report
        
        for category_path in self.evidence_path.iterdir():
            if category_path.is_dir() and not category_path.name.startswith('.'):
                category_name = category_path.name
                
                # 跳過指南文件
                if category_name.endswith('.md'):
                    continue
                
                templates = list(category_path.glob("*_Template.md"))
                
                # 計算記錄數量（排除模板）
                records = []
                for year_path in category_path.iterdir():
                    if year_path.is_dir() and year_path.name.isdigit():
                        for month_path in year_path.iterdir():
                            if month_path.is_dir():
                                records.extend(list(month_path.glob("*.md")))
                
                report['categories'][category_name] = {
                    'templates': len(templates),
                    'records': len(records),
                    'template_list': [t.name for t in templates],
                    'has_records': len(records) > 0,
                }
                
                report['summary']['total_categories'] += 1
                report['summary']['total_templates'] += len(templates)
                report['summary']['total_records'] += len(records)
                if len(records) > 0:
                    report['summary']['categories_with_records'] += 1
        
        return report
    
    def generate_compliance_report(self, output_path: Path = None) -> str:
        """
        生成合規性報告
        
        Args:
            output_path: 報告輸出路徑（可選）
            
        Returns:
            報告內容
        """
        scan_result = self.scan_compliance()
        
        report_lines = []
        report_lines.append("# ISO 27001 合規性掃描報告")
        report_lines.append("")
        report_lines.append(f"**掃描時間**: {scan_result['scan_date']}")
        report_lines.append("")
        
        if 'error' in scan_result:
            report_lines.append(f"## 錯誤")
            report_lines.append(f"{scan_result['error']}")
            report_content = '\n'.join(report_lines)
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            return report_content
        
        # 摘要
        summary = scan_result['summary']
        report_lines.append("## 摘要")
        report_lines.append("")
        report_lines.append(f"- **證據類別總數**: {summary['total_categories']}")
        report_lines.append(f"- **模板總數**: {summary['total_templates']}")
        report_lines.append(f"- **證據記錄總數**: {summary['total_records']}")
        report_lines.append(f"- **有證據記錄的類別數**: {summary['categories_with_records']}/{summary['total_categories']}")
        report_lines.append("")
        
        # 詳細資訊
        report_lines.append("## 各類別詳情")
        report_lines.append("")
        
        for category_name, category_data in sorted(scan_result['categories'].items()):
            status = "✅" if category_data['has_records'] else "⚠️"
            report_lines.append(f"### {status} {category_name}")
            report_lines.append("")
            report_lines.append(f"- **模板數量**: {category_data['templates']}")
            report_lines.append(f"- **證據記錄數**: {category_data['records']}")
            
            if category_data['template_list']:
                report_lines.append("- **可用模板**:")
                for template in category_data['template_list']:
                    report_lines.append(f"  - {template}")
            
            report_lines.append("")
        
        # 建議
        report_lines.append("## 建議")
        report_lines.append("")
        
        empty_categories = [name for name, data in scan_result['categories'].items() 
                           if not data['has_records'] and data['templates'] > 0]
        
        if empty_categories:
            report_lines.append("### 缺少證據記錄的類別")
            report_lines.append("")
            report_lines.append("以下類別有模板但尚未生成任何證據記錄：")
            report_lines.append("")
            for category in empty_categories:
                report_lines.append(f"- {category}")
            report_lines.append("")
            report_lines.append("建議使用 `iso_automation.py` 工具根據模板生成相應的證據記錄。")
        else:
            report_lines.append("所有有模板的類別都已生成證據記錄。")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("*此報告由 ISO 27001 自動化工具生成*")
        
        report_content = '\n'.join(report_lines)
        
        if output_path:
            self.ensure_directory(output_path.parent)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
        
        return report_content
    
    def get_git_commits(self, since: str = None, until: str = None, 
                       author: str = None) -> List[Dict[str, str]]:
        """
        獲取 Git Commit 記錄
        
        Args:
            since: 起始日期（格式：YYYY-MM-DD）
            until: 結束日期（格式：YYYY-MM-DD）
            author: 作者篩選
            
        Returns:
            Commit 列表
        """
        import subprocess
        
        cmd = ['git', 'log', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=short']
        
        if since:
            cmd.append(f'--since={since}')
        if until:
            cmd.append(f'--until={until}')
        if author:
            cmd.append(f'--author={author}')
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.base_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0][:7],
                            'author': parts[1],
                            'email': parts[2],
                            'date': parts[3],
                            'message': parts[4],
                        })
            
            return commits
        except subprocess.CalledProcessError as e:
            print(f"獲取 Git Commit 記錄失敗: {e}", file=sys.stderr)
            return []


def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(
        description='ISO 27001 自動化證據生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 列出所有可用模板
  %(prog)s list-templates
  
  # 列出特定類別的模板
  %(prog)s list-templates --category "備份與復原"
  
  # 從 JSON 數據生成證據
  %(prog)s generate --template "記錄與證據/備份與復原/備份執行紀錄_Template.md" --data data.json
  
  # 生成合規性報告
  %(prog)s compliance-report --output compliance_report.md
  
  # 生成週報（從 Git Commit）
  %(prog)s weekly-report --since 2026-01-17 --until 2026-01-24
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用指令')
    
    # list-templates 指令
    list_parser = subparsers.add_parser('list-templates', help='列出可用模板')
    list_parser.add_argument('--category', help='證據類別')
    
    # generate 指令
    gen_parser = subparsers.add_parser('generate', help='生成證據文件')
    gen_parser.add_argument('--template', required=True, help='模板路徑')
    gen_parser.add_argument('--data', required=True, help='數據檔案路徑 (JSON/YAML)')
    gen_parser.add_argument('--output', help='輸出路徑（可選，預設自動歸檔）')
    gen_parser.add_argument('--no-archive', action='store_true', 
                           help='不使用自動歸檔（需指定 --output）')
    
    # compliance-report 指令
    report_parser = subparsers.add_parser('compliance-report', 
                                         help='生成合規性報告')
    report_parser.add_argument('--output', help='報告輸出路徑')
    
    # weekly-report 指令
    weekly_parser = subparsers.add_parser('weekly-report', 
                                         help='生成週報（從 Git Commit）')
    weekly_parser.add_argument('--since', help='起始日期 (YYYY-MM-DD)')
    weekly_parser.add_argument('--until', help='結束日期 (YYYY-MM-DD)')
    weekly_parser.add_argument('--author', help='作者篩選')
    weekly_parser.add_argument('--output', help='輸出路徑')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 初始化工具
    automation = ISOAutomation()
    
    # 執行指令
    if args.command == 'list-templates':
        templates = automation.list_templates(args.category)
        
        if templates:
            print(f"找到 {len(templates)} 個模板:")
            print()
            for template in templates:
                category = template.parent.name
                print(f"  [{category}] {template.name}")
        else:
            print("未找到模板")
            return 1
    
    elif args.command == 'generate':
        template_path = Path(args.template)
        data_path = Path(args.data)
        
        if not template_path.exists():
            print(f"錯誤: 模板不存在: {template_path}", file=sys.stderr)
            return 1
        
        if not data_path.exists():
            print(f"錯誤: 數據檔案不存在: {data_path}", file=sys.stderr)
            return 1
        
        try:
            # 載入數據
            data = automation.load_data(data_path)
            
            # 生成證據
            output_path = Path(args.output) if args.output else None
            auto_archive = not args.no_archive
            
            result_path = automation.generate_evidence(
                template_path,
                data,
                output_path=output_path,
                auto_archive=auto_archive
            )
            
            print(f"✅ 證據文件已生成: {result_path}")
            return 0
            
        except Exception as e:
            print(f"錯誤: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    elif args.command == 'compliance-report':
        try:
            output_path = Path(args.output) if args.output else None
            report = automation.generate_compliance_report(output_path)
            
            if not output_path:
                print(report)
            else:
                print(f"✅ 合規性報告已生成: {output_path}")
            
            return 0
            
        except Exception as e:
            print(f"錯誤: {e}", file=sys.stderr)
            return 1
    
    elif args.command == 'weekly-report':
        try:
            commits = automation.get_git_commits(
                since=args.since,
                until=args.until,
                author=args.author
            )
            
            if not commits:
                print("未找到符合條件的 Commit 記錄")
                return 1
            
            # 生成週報內容
            report_lines = []
            report_lines.append("# 週報")
            report_lines.append("")
            
            if args.since and args.until:
                report_lines.append(f"**期間**: {args.since} ~ {args.until}")
            else:
                report_lines.append(f"**生成日期**: {datetime.now().strftime('%Y-%m-%d')}")
            
            report_lines.append("")
            report_lines.append("## 本週完成事項")
            report_lines.append("")
            
            for commit in commits:
                report_lines.append(f"- [{commit['date']}] {commit['message']} (by {commit['author']})")
            
            report_lines.append("")
            report_lines.append(f"**總計**: {len(commits)} 個提交")
            
            report_content = '\n'.join(report_lines)
            
            if args.output:
                output_path = Path(args.output)
                automation.ensure_directory(output_path.parent)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"✅ 週報已生成: {output_path}")
            else:
                print(report_content)
            
            return 0
            
        except Exception as e:
            print(f"錯誤: {e}", file=sys.stderr)
            return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
