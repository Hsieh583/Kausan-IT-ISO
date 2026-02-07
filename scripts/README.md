# ISO 27001 自動化證據生成工具

## 🎯 專案目標

本工具提供 ISO 27001 證據文件的自動化生成與管理功能，旨在：

- ✅ **自動化證據生成**: 從模板快速生成帶有時間戳記的證據文件
- ✅ **結構化數據填充**: 支援 JSON/YAML 格式的數據輸入
- ✅ **自動歸檔管理**: 按照日期自動歸檔至 `記錄與證據/{類別}/{YYYY}/{MM}/` 路徑
- ✅ **合規性檢查**: 掃描目錄結構並生成合規狀態報告
- ✅ **週報生成**: 從 Git Commit 歷史自動生成週報

## 📋 功能特色

### 1. 模板引擎整合

使用 Jinja2 模板引擎，支援：
- 變數替換
- 條件判斷
- 迴圈處理
- 自動日期填充

### 2. 自動填充邏輯

- 支援 JSON 和 YAML 數據格式
- 自動添加當前日期、時間等上下文變數
- 靈活的數據結構支援

### 3. 智慧歸檔路徑

自動生成符合規範的歸檔路徑：
```
記錄與證據/
  └── {類別}/
      └── {YYYY}/
          └── {MM}/
              └── {檔案名稱}_{YYYYMMDD}.md
```

### 4. 合規性檢查

- 掃描所有證據類別
- 統計模板和記錄數量
- 識別缺少記錄的類別
- 生成詳細的合規報告

## 🚀 快速開始

### 安裝依賴

```bash
cd scripts
pip install -r requirements.txt
```

### 基本使用

#### 1. 列出所有可用模板

```bash
python iso_automation.py list-templates
```

輸出範例：
```
找到 31 個模板:

  [備份與復原] 備份執行紀錄_Template.md
  [備份與復原] 備份還原測試報告_Template.md
  [備份與復原] 異地備份驗證紀錄_Template.md
  [帳號與存取管理] 帳號申請與核准單_Template.md
  ...
```

#### 2. 列出特定類別的模板

```bash
python iso_automation.py list-templates --category "備份與復原"
```

#### 3. 生成證據文件

從 JSON 數據生成證據：

```bash
python iso_automation.py generate \
  --template "記錄與證據/備份與復原/備份執行紀錄_Template.md" \
  --data examples/backup_data.json
```

從 YAML 數據生成證據：

```bash
python iso_automation.py generate \
  --template "記錄與證據/帳號與存取管理/帳號申請與核准單_Template.md" \
  --data examples/account_data.yaml
```

#### 4. 生成合規性報告

```bash
# 輸出到終端
python iso_automation.py compliance-report

# 輸出到檔案
python iso_automation.py compliance-report --output compliance_report.md
```

#### 5. 生成週報（從 Git Commit）

```bash
# 生成本週週報
python iso_automation.py weekly-report \
  --since 2026-01-17 \
  --until 2026-01-24 \
  --output weekly_report.md
```

## 📝 數據格式範例

### JSON 格式範例 (backup_data.json)

```json
{
  "備份管理員": "張三",
  "備份策略": "完整+增量",
  "備份時間": "02:00",
  "本地備份位置": "\\\\fileserver\\backup\\",
  "異地備份位置": "Backblaze B2 Cloud",
  "備份對象列表": [
    {
      "對象": "檔案伺服器",
      "類型": "完整",
      "開始時間": "02:00",
      "結束時間": "03:30",
      "大小": "500",
      "耗時": "90",
      "結果": "成功",
      "異常信息": ""
    }
  ],
  "備份總大小": "730",
  "備份成功率": "100",
  "異常件數": "0"
}
```

### YAML 格式範例 (account_data.yaml)

```yaml
申請人姓名: 王小明
申請人部門: 資訊部
申請人職位: 系統工程師
員工編號: EMP-2026-001
申請帳號用途: 新進員工入職
系統名稱: Active Directory, 檔案伺服器, 郵件系統
帳號名稱: wang.xiaoming
所需權限等級: 基本使用者
具體權限內容: 存取共享資料夾、收發電子郵件、使用企業入口網站
帳號生命週期: 按職務（職務變更時停用）
部門主管姓名: 李經理
核准意見: 核准
核准理由: 新進員工到職，需要建立基本帳號存取公司系統
```

## 🔧 進階使用

### 使用 Jinja2 模板語法

模板支援完整的 Jinja2 語法，例如：

```markdown
# 備份執行紀錄

**備份管理員**: {{ 備份管理員 }}
**備份日期**: {{ current_date }}

## 備份對象列表

{% for 對象 in 備份對象列表 %}
- **{{ 對象.對象 }}**: {{ 對象.結果 }} (耗時: {{ 對象.耗時 }} 分鐘)
{% endfor %}
```

### 自動提供的變數

工具自動提供以下上下文變數：

- `current_date`: 當前日期（格式：2026年01月24日）
- `current_datetime`: 當前日期時間（格式：2026-01-24 14:30:00）
- `current_year`: 當前年份（格式：2026）
- `current_month`: 當前月份（格式：01）
- `current_day`: 當前日期（格式：24）

### 指定自訂輸出路徑

```bash
python iso_automation.py generate \
  --template "記錄與證據/備份與復原/備份執行紀錄_Template.md" \
  --data examples/backup_data.json \
  --output custom_output.md \
  --no-archive
```

## 📊 合規性報告範例

執行 `compliance-report` 指令後會生成類似以下的報告：

```markdown
# ISO 27001 合規性掃描報告

**掃描時間**: 2026-01-24 14:30:00

## 摘要

- **證據類別總數**: 8
- **模板總數**: 31
- **證據記錄總數**: 5
- **有證據記錄的類別數**: 2/8

## 各類別詳情

### ✅ 備份與復原

- **模板數量**: 3
- **證據記錄數**: 3
- **可用模板**:
  - 備份執行紀錄_Template.md
  - 備份還原測試報告_Template.md
  - 異地備份驗證紀錄_Template.md

### ⚠️ 帳號與存取管理

- **模板數量**: 4
- **證據記錄數**: 0
- **可用模板**:
  - 帳號申請與核准單_Template.md
  - 帳號停用紀錄_Template.md
  ...

## 建議

### 缺少證據記錄的類別

以下類別有模板但尚未生成任何證據記錄：

- 帳號與存取管理
- 密碼與認証管理
- 資產管理
- ...

建議使用 `iso_automation.py` 工具根據模板生成相應的證據記錄。
```

## 🔄 GitHub Actions 整合

工具支援與 GitHub Actions 整合，實現自動化合規檢查。詳見 `.github/workflows/verify-compliance.yml`。

### 觸發條件

- 每次 Push 到主分支
- 每週定期執行
- 手動觸發

### 執行內容

1. 安裝依賴
2. 執行合規性掃描
3. 生成報告
4. 上傳報告為 Artifact

## 📁 專案結構

```
scripts/
├── iso_automation.py      # 主程式
├── requirements.txt       # Python 依賴
├── examples/             # 範例數據檔案
│   ├── backup_data.json
│   └── account_data.yaml
└── README.md             # 本文件
```

## 🛠️ 開發與測試

### 執行測試

```bash
cd scripts
pytest
```

### 程式碼覆蓋率

```bash
pytest --cov=iso_automation --cov-report=html
```

## 📖 參考文件

- [ISO 27001 合規稽核清單](../ISO%2027001%20合規稽核清單.md)
- [記錄系統目錄指南](../記錄與證據/記錄系統目錄指南.md)
- [工具與技術選型](../資訊營運/工具與技術選型.md)

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

## 📄 授權

本專案採用 MIT 授權。

## 📞 聯絡資訊

如有問題或建議，請聯繫：

- **維護者**: 謝正強
- **Email**: [專案維護者信箱]
- **專案網址**: https://github.com/Hsieh583/Kausan-IT-ISO

---

**最後更新**: 2026-01-24
