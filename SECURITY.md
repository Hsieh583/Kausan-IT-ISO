# 安全與隱私指南 / Security and Privacy Guidelines

## 📋 概述 / Overview

此儲存庫為公開專案，包含 ISO 27001 資訊安全管理系統的文件範本和實施指南。所有敏感資訊已被移除或替換為通用佔位符。

This is a public repository containing ISO 27001 Information Security Management System document templates and implementation guides. All sensitive information has been removed or replaced with generic placeholders.

---

## ⚠️ 重要提醒 / Important Notices

### 🚫 請勿提交以下內容 / DO NOT Commit:

1. **真實憑證 / Real Credentials**
   - API 金鑰、密碼、令牌
   - 資料庫連接字串
   - SSH 金鑰或憑證檔案 (.pem, .key, .p12, .pfx)

2. **個人資料 / Personal Information**
   - 真實姓名、電話號碼
   - 真實電子郵件地址
   - 身份證號碼或其他個人識別資訊

3. **公司敏感資訊 / Company Sensitive Information**
   - 實際的公司網域名稱或 IP 位址
   - 真實的組織架構或人員名單
   - 專有的商業資訊

4. **環境配置檔 / Environment Configuration Files**
   - `.env` 檔案
   - `config.yaml` 包含真實設定
   - `secrets.yaml` 或類似檔案

---

## ✅ 已採取的安全措施 / Security Measures Taken

### 1. 已移除的敏感資訊 / Removed Sensitive Information:
- ✅ 真實公司電子郵件已替換為 `security@company.com`
- ✅ 作者姓名已替換為角色名稱（如「資訊安全經理」）
- ✅ 測試憑證已標記為 `TEST DATA` 並使用明顯的佔位符

### 2. 使用的安全佔位符 / Safe Placeholders Used:
- 電子郵件: `@example.com`, `@company.com`
- 網域: `company.com`, `example.com`
- IP 位址: 僅使用私有範圍（192.168.x.x, 10.x.x.x）
- 密碼: `test_password_123`, `example-jwt-token-placeholder`

### 3. .gitignore 配置 / .gitignore Configuration:
已配置忽略以下類型的檔案：
- 環境變數檔案 (`.env`, `.env.*`)
- 配置檔案 (`config.yaml`, `secrets.yaml`)
- 憑證檔案 (`*.pem`, `*.key`, `*.p12`, `*.pfx`)
- PDF 文件 (`*.pdf`)

---

## 🔐 使用此專案的最佳實踐 / Best Practices for Using This Project

### 複製並客製化 / Fork and Customize:

1. **建立私有分支 / Create a Private Fork:**
   ```bash
   # 複製此儲存庫到您的組織
   git clone https://github.com/Hsieh583/Kausan-IT-ISO.git
   cd Kausan-IT-ISO
   
   # 設定為您自己的私有儲存庫
   git remote set-url origin YOUR_PRIVATE_REPO_URL
   ```

2. **使用環境變數 / Use Environment Variables:**
   ```bash
   # 建立 .env 檔案（已被 .gitignore 忽略）
   cp .env.example .env
   
   # 在 .env 中設定真實值
   COMPANY_EMAIL=security@yourcompany.com
   API_KEY=your-real-api-key
   ```

3. **客製化模板 / Customize Templates:**
   - 將佔位符替換為您的實際資訊
   - 確保不將敏感資訊推送到公開儲存庫

---

## 📝 測試資料說明 / Test Data Notice

所有包含密碼或憑證的測試檔案都已標記為 `TEST DATA`，這些不是真實的憑證：

All test files containing passwords or credentials are marked as `TEST DATA` and are not real credentials:

- `API-Hook/test_api_hook.js` - 測試用假資料
- `API-Hook/api_hook.py` - 範例實作
- `API-Hook/api_hook.js` - 範例實作

這些檔案僅用於演示和測試目的。在生產環境中使用時，請使用適當的憑證管理系統。

These files are for demonstration and testing purposes only. Use proper credential management systems in production.

---

## 🛡️ 報告安全問題 / Reporting Security Issues

如果您發現此儲存庫中有任何敏感資訊洩漏，請立即通知：

If you discover any sensitive information leakage in this repository, please notify immediately:

1. **不要**在公開 issue 中報告安全問題
2. 直接聯絡專案維護者
3. 提供詳細的位置和建議的修復方式

1. **DO NOT** report security issues in public issues
2. Contact the project maintainers directly
3. Provide details of the location and suggested fixes

---

## 📚 相關資源 / Related Resources

- [ISO/IEC 27001:2022 標準](https://www.iso.org/standard/27001)
- [OWASP 安全最佳實踐](https://owasp.org/)
- [GitHub 安全最佳實踐](https://docs.github.com/en/code-security)

---

## 📄 授權 / License

此專案中的所有模板和文件僅供參考和教育目的。使用者應根據自己組織的需求進行客製化。

All templates and documents in this project are for reference and educational purposes only. Users should customize them according to their organization's needs.

---

**最後更新 / Last Updated:** 2026-02-06  
**版本 / Version:** 1.0
