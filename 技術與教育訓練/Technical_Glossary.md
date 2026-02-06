# 技術詞彙表 Technical Glossary

> **文件版本 Document Version**: v1.0  
> **最後更新 Last Updated**: 2026-01-30  
> **維護者 Maintainer**: IT部門 / IT Department  
> **用途 Purpose**: 統一技術術語，支援培訓講義與技術文件

---

## 目錄 Table of Contents

- [可靠性與容災 Reliability & DR](#可靠性與容災-reliability--dr)
- [防禦與監控 Defense & Monitoring](#防禦與監控-defense--monitoring)
- [身份與存取管理 Identity & Access](#身份與存取管理-identity--access)
- [自動化與工具 Automation & Tools](#自動化與工具-automation--tools)
- [合規與稽核 Compliance & Audit](#合規與稽核-compliance--audit)

---

## 可靠性與容災 Reliability & DR

### RTO (Recovery Time Objective)
**復原時間目標**

系統從故障到恢復正常運作所需的最大可接受時間。例如：RTO=4小時表示系統必須在4小時內恢復。

- **範例 Example**: 核心業務系統RTO設定為4小時
- **相關文件 Related Docs**: [DR_BCP業務連續性講義](L1_可靠性與容災/DR_BCP_Business_Continuity_Training.md)
- **ISO 27001**: A17.1.2, A17.2.1

---

### RPO (Recovery Point Objective)
**復原點目標**

系統故障時可容忍的最大數據損失時間。例如：RPO=1小時表示最多損失1小時的數據。

- **範例 Example**: 客戶資料庫RPO設定為15分鐘（每15分鐘備份一次）
- **相關文件 Related Docs**: [DR_BCP業務連續性講義](L1_可靠性與容災/DR_BCP_Business_Continuity_Training.md)
- **ISO 27001**: A17.1.2

---

### HA (High Availability)
**高可用性**

透過冗餘配置確保系統在組件故障時仍能持續運作的架構設計。目標通常為99.9%以上的可用性。

- **技術實現 Implementation**: 雙主機、負載均衡、自動故障轉移
- **工具 Tools**: Proxmox VE HA, VMware vSphere HA, SQL Server Always On
- **相關文件 Related Docs**: [DR_BCP業務連續性講義](L1_可靠性與容災/DR_BCP_Business_Continuity_Training.md)
- **ISO 27001**: A17.2.1

---

### DR (Disaster Recovery)
**災難復原**

在重大災難（火災、水災、地震、網路攻擊）後恢復IT系統與業務運作的計劃與流程。

- **包含 Includes**: 異地備份、備援機房、復原程序、演練計劃
- **相關文件 Related Docs**: [DR_BCP業務連續性講義](L1_可靠性與容災/DR_BCP_Business_Continuity_Training.md)
- **ISO 27001**: A17.1.1, A17.1.3

---

### BCP (Business Continuity Plan)
**業務持續計劃**

確保組織在災難或中斷事件後能持續提供關鍵業務服務的整體計劃，涵蓋IT、人員、設施等。

- **範疇 Scope**: 比DR更廣，包含業務流程、人員調度、替代辦公地點
- **相關文件 Related Docs**: [DR_BCP業務連續性講義](L1_可靠性與容災/DR_BCP_Business_Continuity_Training.md)
- **ISO 27001**: A17.1.1

---

### 3-2-1 Backup Rule
**3-2-1備份原則**

業界最佳實踐備份策略：保留3份數據副本、使用2種不同儲存媒體、1份副本存放異地。

- **範例 Example**: 原始數據（生產系統）+ 本地備份（NAS）+ 異地備份（雲端）
- **相關文件 Related Docs**: [備份驗證指南](L3_使用者體驗/Backup_Verification_Guide.md)
- **ISO 27001**: A12.3.1

---

## 防禦與監控 Defense & Monitoring

### SIEM (Security Information and Event Management)
**資安資訊與事件管理系統**

集中收集、分析、儲存來自多個來源的安全日誌與事件，提供即時監控與威脅偵測。

- **功能 Functions**: 日誌聚合、關聯分析、告警、合規報告
- **工具 Tools**: ELK Stack (Elasticsearch + Logstash + Kibana), Wazuh, Splunk
- **相關文件 Related Docs**: [Wazuh SIEM運維指南](L2_防禦與監控/Wazuh_SIEM_Operations_Guide.md)
- **ISO 27001**: A12.4.1, A16.1.2

---

### MTTR (Mean Time To Repair/Respond)
**平均修復/回應時間**

從檢測到安全事件或故障到完全解決的平均時間。用於衡量事件回應效率。

- **目標 Target**: 本組織設定為≤4小時（資安事件）
- **相關文件 Related Docs**: [事件回應流程SOP](L3_使用者體驗/Incident_Response_SOP.md)
- **ISO 27001**: A16.1.5

---

### MTTD (Mean Time To Detect)
**平均偵測時間**

從威脅或異常發生到被偵測的平均時間。越短表示監控能力越強。

- **目標 Target**: 本組織設定為≤1小時
- **相關文件 Related Docs**: [Wazuh SIEM運維指南](L2_防禦與監控/Wazuh_SIEM_Operations_Guide.md)
- **ISO 27001**: A12.4.1

---

### IDS/IPS (Intrusion Detection/Prevention System)
**入侵偵測/防禦系統**

- **IDS**: 偵測並告警可疑活動（被動）
- **IPS**: 偵測並自動阻擋攻擊（主動）

- **工具 Tools**: Suricata, Snort, pfSense (Suricata模組)
- **部署 Deployment**: 網路邊界、DMZ、核心網段
- **相關文件 Related Docs**: [防火牆策略與網路分段](L5_文件與合規/Firewall_Network_Segmentation.md)
- **ISO 27001**: A13.1.1

---

### EDR (Endpoint Detection and Response)
**端點偵測與回應**

在終端設備（電腦、伺服器）上進行威脅偵測、調查與回應的安全工具。

- **功能 Functions**: 行為分析、惡意軟體偵測、自動隔離、取證
- **工具 Tools**: Microsoft Defender for Endpoint, Wazuh Agent
- **相關文件 Related Docs**: [Wazuh SIEM運維指南](L2_防禦與監控/Wazuh_SIEM_Operations_Guide.md)
- **ISO 27001**: A12.2.1

---

### MITRE ATT&CK
**MITRE攻擊框架**

全球公認的網路攻擊技術與戰術知識庫，用於威脅分析、偵測規則設計、防禦策略規劃。

- **用途 Use Cases**: 設計偵測規則、評估防禦缺口、威脅情報對應
- **網址 URL**: https://attack.mitre.org/
- **相關文件 Related Docs**: [Wazuh SIEM運維指南](L2_防禦與監控/Wazuh_SIEM_Operations_Guide.md)

---

## 身份與存取管理 Identity & Access

### IAM (Identity and Access Management)
**身份與存取管理**

管理使用者身份、認證、授權的完整體系，確保「正確的人」在「正確的時間」存取「正確的資源」。

- **核心功能 Core Functions**: 帳號供應/停用、權限管理、SSO、MFA
- **工具 Tools**: Okta, Azure AD, Active Directory
- **相關文件 Related Docs**: [IAM帳號管理手冊](L3_使用者體驗/IAM_Account_Management_Manual.md)
- **ISO 27001**: A9.2.1, A9.2.2, A9.2.3

---

### MFA (Multi-Factor Authentication)
**多因素認證**

結合兩種以上認證方式（知道的密碼、擁有的裝置、生物特徵）提升帳號安全性。

- **範例 Example**: 密碼 + 手機簡訊驗證碼、密碼 + Authenticator App
- **強制對象 Mandatory For**: 特權帳號、遠端存取、敏感系統
- **相關文件 Related Docs**: [IAM帳號管理手冊](L3_使用者體驗/IAM_Account_Management_Manual.md)
- **ISO 27001**: A9.4.2

---

### SSO (Single Sign-On)
**單一登入**

使用者只需登入一次即可存取多個應用系統，無需重複輸入帳密。

- **技術 Technology**: SAML 2.0, OAuth 2.0, OpenID Connect
- **優點 Benefits**: 提升使用者體驗、降低密碼疲勞、集中管理
- **相關文件 Related Docs**: [IAM帳號管理手冊](L3_使用者體驗/IAM_Account_Management_Manual.md)
- **ISO 27001**: A9.4.2

---

### RBAC (Role-Based Access Control)
**角色基礎存取控制**

根據使用者角色（職位、部門）分配權限，而非個別指派。簡化權限管理與審查。

- **範例 Example**: "財務經理"角色自動擁有會計系統讀寫權限
- **優點 Benefits**: 權限標準化、降低人為錯誤、易於審查
- **相關文件 Related Docs**: [IAM帳號管理手冊](L3_使用者體驗/IAM_Account_Management_Manual.md)
- **ISO 27001**: A9.2.3

---

### Privileged Account
**特權帳號**

擁有系統管理員或高階權限的帳號（如Domain Admin、root、sa）。需特別保護與監控。

- **管理要求 Requirements**: MFA強制、使用紀錄審計、定期密碼變更、最小權限原則
- **相關文件 Related Docs**: [IAM帳號管理手冊](L3_使用者體驗/IAM_Account_Management_Manual.md)
- **ISO 27001**: A9.2.3

---

## 自動化與工具 Automation & Tools

### IaC (Infrastructure as Code)
**基礎設施即代碼**

用程式碼定義與管理IT基礎設施（伺服器、網路、儲存），實現自動化部署與版本控制。

- **工具 Tools**: Ansible, Terraform, Vagrant
- **優點 Benefits**: 可重複性、版本控制、快速部署、減少人為錯誤
- **相關文件 Related Docs**: [Git文件版本控制](L5_文件與合規/Git_Version_Control_Guide.md)
- **ISO 27001**: A12.1.2, A14.2.2

---

### CI/CD (Continuous Integration/Continuous Deployment)
**持續整合/持續部署**

自動化軟體開發流程：程式碼提交→自動測試→自動部署至生產環境。

- **工具 Tools**: GitLab CI/CD, Jenkins, GitHub Actions
- **優點 Benefits**: 加速交付、降低人為錯誤、提早發現問題
- **相關文件 Related Docs**: 待開發（Phase 3）
- **ISO 27001**: A14.2.2

---

### Ansible
**自動化配置管理工具**

無代理(agentless)的IT自動化工具，透過SSH執行配置任務，使用YAML語法撰寫Playbook。

- **用途 Use Cases**: 系統配置、軟體部署、帳號管理、合規檢查
- **優點 Benefits**: 易學習、無需安裝Agent、社群豐富
- **相關文件 Related Docs**: 待開發（Phase 3）
- **ISO 27001**: A12.1.2

---

### Prometheus + Grafana
**監控與視覺化平台**

- **Prometheus**: 時間序列資料庫，收集與儲存指標數據
- **Grafana**: 數據視覺化工具，建立儀表板

- **用途 Use Cases**: 系統效能監控、服務可用性、容量規劃、告警
- **相關文件 Related Docs**: 待開發（Phase 3）
- **ISO 27001**: A12.1.3

---

## 合規與稽核 Compliance & Audit

### ISO 27001
**資訊安全管理系統國際標準**

國際公認的資訊安全管理標準，定義114項控制措施（Annex A），協助組織建立、實施、維護ISMS。

- **版本 Version**: ISO/IEC 27001:2022（最新版）
- **核心 Core**: PDCA循環（計畫-執行-檢查-行動）
- **相關文件 Related Docs**: [ISO27001內部稽核指南](L2_防禦與監控/ISO27001_Internal_Audit_Guide.md)
- **官網 Official**: https://www.iso.org/isoiec-27001-information-security.html

---

### ISMS (Information Security Management System)
**資訊安全管理系統**

組織用於管理資訊安全的系統化方法，包含政策、程序、流程、資源、責任分配。

- **組成 Components**: 政策文件、程序SOP、風險評估、控制措施、稽核機制
- **相關文件 Related Docs**: [ISO27001內部稽核指南](L2_防禦與監控/ISO27001_Internal_Audit_Guide.md)
- **ISO 27001**: Clause 4-10

---

### Non-Conformity (不符合項)
**不符合項**

稽核中發現的不符合ISO 27001要求的項目。分為重大（Major）與輕微（Minor）。

- **Major NC**: 嚴重缺失，可能導致認證失敗（如核心系統無備份）
- **Minor NC**: 輕微偏差，需在期限內改正（如文件日期錯誤）
- **相關文件 Related Docs**: [ISO27001內部稽核指南](L2_防禦與監控/ISO27001_Internal_Audit_Guide.md)
- **ISO 27001**: Clause 10.2

---

### CAR (Corrective Action Request)
**矯正措施要求**

針對不符合項提出的改善行動，包含根本原因分析、改善措施、完成期限、驗證方法。

- **流程 Process**: 問題識別 → 根因分析 → 改善措施 → 執行 → 驗證 → 結案
- **相關文件 Related Docs**: [ISO27001內部稽核指南](L2_防禦與監控/ISO27001_Internal_Audit_Guide.md)
- **ISO 27001**: Clause 10.1

---

### Evidence (證據)
**稽核證據**

證明控制措施已實施且有效運作的客觀記錄。可為文件、記錄、照片、截圖、日誌等。

- **範例 Examples**: 備份執行紀錄、權限審查報告、培訓簽到表、變更申請單
- **要求 Requirements**: 可追溯、完整、真實、及時
- **相關文件 Related Docs**: [ISO27001內部稽核指南](L2_防禦與監控/ISO27001_Internal_Audit_Guide.md)
- **對應資料夾 Folder**: [記錄與證據](../記錄與證據/)
- **ISO 27001**: 所有控制項

---

### Risk Assessment (風險評估)
**風險評估**

識別資訊資產面臨的威脅與弱點，評估風險等級，決定處理策略（接受、降低、轉移、迴避）。

- **方法 Methods**: 定性分析、定量分析、矩陣法
- **頻率 Frequency**: 至少每年1次，或重大變更時
- **相關文件 Related Docs**: 待開發（Phase 2）
- **ISO 27001**: Clause 6.1.2

---

## 縮寫對照表 Abbreviations

| 縮寫 | 英文全名 | 中文 |
|------|---------|------|
| AD | Active Directory | 活動目錄 |
| API | Application Programming Interface | 應用程式介面 |
| BYOD | Bring Your Own Device | 攜帶自有裝置 |
| CAB | Change Advisory Board | 變更諮詢委員會 |
| CISO | Chief Information Security Officer | 資訊安全長 |
| CMDB | Configuration Management Database | 配置管理資料庫 |
| CVE | Common Vulnerabilities and Exposures | 常見漏洞與曝險 |
| CVSS | Common Vulnerability Scoring System | 通用漏洞評分系統 |
| DMZ | Demilitarized Zone | 非軍事區（網路隔離區） |
| DNS | Domain Name System | 網域名稱系統 |
| DNSSEC | DNS Security Extensions | DNS安全擴充 |
| ELK | Elasticsearch, Logstash, Kibana | ELK日誌分析平台 |
| GDPR | General Data Protection Regulation | 歐盟一般資料保護規範 |
| ITIL | IT Infrastructure Library | IT基礎架構庫 |
| ITSM | IT Service Management | IT服務管理 |
| KPI | Key Performance Indicator | 關鍵績效指標 |
| LDAP | Lightweight Directory Access Protocol | 輕量級目錄存取協定 |
| NAS | Network Attached Storage | 網路附接儲存 |
| NC | Non-Conformity | 不符合項 |
| NIST | National Institute of Standards and Technology | 美國國家標準與技術研究院 |
| OTP | One-Time Password | 一次性密碼 |
| PDCA | Plan-Do-Check-Act | 計畫-執行-檢查-行動 |
| SAST | Static Application Security Testing | 靜態應用安全測試 |
| SLA | Service Level Agreement | 服務等級協議 |
| SOP | Standard Operating Procedure | 標準作業程序 |
| TLS | Transport Layer Security | 傳輸層安全協定 |
| VPN | Virtual Private Network | 虛擬私人網路 |
| VLAN | Virtual Local Area Network | 虛擬區域網路 |

---

## 維護指南 Maintenance Guide

### 新增術語流程
1. 確認術語在現有清單中不存在
2. 添加中英文名稱、簡短定義（1-2句）
3. 提供範例或實際應用情境
4. 連結相關培訓文件或SOP
5. 標註對應的ISO 27001控制項（如適用）

### 更新週期
- **每月審查**: 新增培訓文件中出現的新術語
- **季度更新**: 補充工具版本、外部連結有效性
- **年度檢視**: 移除過時術語、整合同義詞

### 貢獻者
歡迎IT團隊成員提出新術語或改進建議，請透過以下方式：
- 提交Pull Request（推薦）
- 郵件至: it-team@company.com
- 於每月IT會議提出

---

**文件歷史 Document History**
- v1.0 (2026-01-30): 初版建立，涵蓋L1-L5核心術語
