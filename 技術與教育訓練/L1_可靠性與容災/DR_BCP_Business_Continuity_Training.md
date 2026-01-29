# DR/BCP 業務連續性培訓講義
# Disaster Recovery & Business Continuity Training Manual

> **文件版本 Document Version**: v1.0  
> **最後更新 Last Updated**: 2026-01-30  
> **培訓時數 Training Hours**: 40小時 (5天密集課程)  
> **優先級 Priority**: 🔴 P0 緊急生存級  
> **受眾 Audience**: IT經理、系統管理員、資安實施工程師  
> **前置條件 Prerequisites**: 基礎系統管理經驗、虛擬化概念

---

## 📋 課程大綱 Course Outline

### Day 1: 業務連續性基礎 Fundamentals (8小時)
- RTO/RPO概念與業務影響分析
- 單點故障識別與風險評估
- 業務連續性框架（ISO 22301 vs ISO 27001 A17）

### Day 2: 高可用性架構設計 HA Architecture (8小時)
- 主備配置 (Active-Passive)
- 雙活配置 (Active-Active)
- 負載均衡與自動故障轉移

### Day 3: 災難復原計劃制定 DR Planning (8小時)
- 異地備份策略
- 復原程序設計
- DR站點規劃與選址

### Day 4: 實作演練 Hands-on Lab (8小時)
- Proxmox VE HA集群建置
- SQL Server Always On配置
- 故障轉移測試

### Day 5: 桌面演練與考核 Tabletop Exercise (8小時)
- 災難情境模擬
- 團隊協作演練
- 知識考核與證書頒發

---

## 第一天：業務連續性基礎
## Day 1: Business Continuity Fundamentals

### 模組1.1：為什麼需要BCP/DR？(1小時)
### Module 1.1: Why Do We Need BCP/DR?

#### 真實災難案例 Real-World Disasters

**案例A：2011日本311大地震**
- 災難類型：地震+海嘯+核災
- IT影響：東京數據中心斷電72小時
- 企業損失：無DR計劃公司，平均停業30-90天
- 教訓：異地備份必須跨地理區域（>100km）

**案例B：2021 Colonial Pipeline勒索軟體攻擊**
- 災難類型：網路攻擊（勒索軟體）
- IT影響：所有IT系統加密，無法運作
- 企業損失：支付$4.4M贖金，停業6天
- 教訓：離線備份（Air-gapped backup）的重要性

**案例C：本公司潛在風險評估**
```
風險評估矩陣 Risk Matrix:

高 High   │       │  ⚠️   │  ⚠️
          │       │ 硬體 │ 火災
          │       │ 故障 │ 水災
────────────────────────────
中 Medium │   🟡   │  ⚠️   │      
          │ 人為  │ 網路 │      
          │ 錯誤  │ 攻擊 │      
────────────────────────────
低 Low    │       │       │      
          │       │       │      
          └───────┴───────┴──────
           低      中      高
          Low    Medium  High
          
          機率 Probability →
```

**當前最嚴重威脅**：
1. 🔴 核心伺服器硬體故障（5年老舊，故障機率90%）
2. 🔴 機房火災/水災（無異地備份）
3. 🟡 勒索軟體攻擊（缺乏隔離備份）

---

### 模組1.2：RTO/RPO核心概念 (2小時)
### Module 1.2: RTO/RPO Core Concepts

#### RTO (Recovery Time Objective) 復原時間目標

**定義**：  
系統從故障發生到恢復正常運作的最大可接受時間。

**業務影響公式**：
```
每小時損失 = 營收損失 + 客戶流失 + 品牌傷害 + 罰款
Hourly Loss = Revenue Loss + Customer Churn + Brand Damage + Penalties

範例：核心業務系統
• 營收損失：$5,000/小時（無法處理訂單）
• 客戶流失：$2,000/小時（客戶轉向競爭者）
• 品牌傷害：$1,000/小時（社群媒體負評）
• 合約罰款：$0（SLA罰款條款）
──────────────────────────
總計：$8,000/小時

若停機24小時 → 損失 $192,000
若停機1週 → 損失 $1,344,000 + 倒閉風險
```

**RTO分級標準**：

| RTO等級 | 時間範圍 | 適用系統 | 技術要求 | 成本 |
|---------|---------|---------|---------|------|
| **Tier 1** | ≤1小時 | 核心業務系統、金融交易 | 雙活+自動故障轉移 | 極高 |
| **Tier 2** | ≤4小時 | 客戶資料庫、郵件系統 | 主備+手動切換 | 高 |
| **Tier 3** | ≤24小時 | 內部管理系統、報表 | 每日備份+還原 | 中 |
| **Tier 4** | ≤72小時 | 歷史資料、測試環境 | 週備份 | 低 |

**本公司RTO目標設定**（初稿，待管理層批准）：

```yaml
# 核心系統 Core Systems
核心業務系統:
  系統名稱: ERP/CRM
  RTO: 4小時
  當前狀態: 無HA，預估RTO >24小時 ⚠️
  差距: 嚴重不足
  
客戶資料庫:
  系統名稱: SQL Server (Customer DB)
  RTO: 4小時
  當前狀態: 單機部署，預估RTO >12小時 ⚠️
  差距: 不足

AD域控制器:
  系統名稱: Active Directory
  RTO: 2小時
  當前狀態: 單DC，預估RTO >8小時 ⚠️
  差距: 嚴重不足

# 次要系統 Secondary Systems
檔案伺服器:
  系統名稱: NAS/File Server
  RTO: 24小時
  當前狀態: 每日備份，符合目標 ✅
  差距: 無

郵件系統:
  系統名稱: Email Server
  RTO: 8小時
  當前狀態: 每日備份，預估RTO ~12小時 🟡
  差距: 輕微
```

---

#### RPO (Recovery Point Objective) 復原點目標

**定義**：  
系統故障時可接受的最大數據損失時間。

**數據價值評估**：
```
數據損失成本 = 重建成本 + 業務影響 + 合規罰款
Data Loss Cost = Recreation Cost + Business Impact + Compliance Penalties

範例：客戶訂單數據
• 重建成本：$500/小時（人工重新輸入）
• 業務影響：訂單遺失 → 客戶退款 → $10,000損失
• 合規罰款：個資法罰款（若涉及個人資料）→ $50,000+
```

**RPO分級標準**：

| RPO等級 | 時間範圍 | 備份頻率 | 適用數據 | 技術方案 |
|---------|---------|---------|---------|---------|
| **Tier 1** | 0 (零損失) | 即時同步 | 交易數據、金融 | 同步複寫、Always On |
| **Tier 2** | ≤15分鐘 | 每15分鐘 | 客戶訂單、業務數據 | 日誌傳送、CDP |
| **Tier 3** | ≤1小時 | 每小時 | 一般業務數據 | 增量備份 |
| **Tier 4** | ≤24小時 | 每日 | 內部文件、報表 | 每日完整備份 |

**本公司RPO目標設定**（初稿）：

```yaml
# 核心數據 Core Data
客戶資料庫:
  數據類型: 客戶資訊、訂單、交易記錄
  RPO: 15分鐘
  當前狀態: 每日備份，RPO=24小時 ⚠️
  差距: 嚴重不足，風險高

業務系統數據:
  數據類型: ERP/CRM交易數據
  RPO: 1小時
  當前狀態: 每日備份，RPO=24小時 ⚠️
  差距: 不足

# 次要數據 Secondary Data
文件與協作:
  數據類型: 共享文件、內部文件
  RPO: 24小時
  當前狀態: 每日備份，符合目標 ✅
  差距: 無

郵件數據:
  數據類型: Email、聯絡資料
  RPO: 4小時
  當前狀態: 每日備份，RPO=24小時 🟡
  差距: 輕微
```

---

#### RTO vs RPO視覺化 Visual Comparison

```
時間軸 Timeline:

正常運作 ←────→ 故障發生 ←─── RPO ───→←─── RTO ───→ 恢復運作
Normal          Failure                            Recovery

              數據最後備份點      開始復原      完成復原
              Last Backup        Start         Complete
              
│●●●●●●●●●│     ╳╳╳╳╳    │▒▒▒▒▒▒▒▒▒▒│●●●●●●●●●│
 運作正常       數據損失      系統停機      運作正常
 Operating      Data Loss    Downtime     Operating

              ◄─────────►   ◄─────────────►
                 RPO             RTO
             (數據損失)      (業務中斷)
            (Data Loss)     (Downtime)
```

**關鍵理解 Key Understanding**：
- ✅ **RPO影響數據完整性**：遺失多少數據？
- ✅ **RTO影響業務連續性**：停機多久？
- ✅ **兩者獨立設定**：可以有不同的目標
- ✅ **成本平衡**：更嚴格的目標 = 更高成本

---

### 模組1.3：業務影響分析 (BIA) 實作 (2小時)
### Module 1.3: Business Impact Analysis (BIA) Workshop

#### BIA工作坊步驟 Workshop Steps

**步驟1：系統清單盤點** (30分鐘)

團隊協作：列出所有IT系統與服務

| 系統名稱 | 主要功能 | 使用者數 | 業務關鍵性 | 現有保護 |
|---------|---------|---------|-----------|---------|
| 核心業務系統 | 訂單處理、庫存 | 50 | 極高 | 無HA |
| 客戶資料庫 | 客戶資料、歷史 | 50 | 極高 | 每日備份 |
| AD域控 | 身份認證 | 100 | 高 | 單DC |
| 檔案伺服器 | 文件共享 | 100 | 中 | 每日備份 |
| 郵件系統 | Email | 100 | 中 | 每日備份 |
| 網站 | 對外官網 | 公開 | 中 | 無HA |

---

**步驟2：中斷影響評估** (45分鐘)

針對每個系統，評估中斷1小時/4小時/24小時的影響：

**範例：核心業務系統中斷評估**

| 中斷時間 | 業務影響 | 財務損失 | 客戶影響 | 法規影響 |
|---------|---------|---------|---------|---------|
| **1小時** | 訂單無法處理 | $5,000 | 輕微抱怨 | 無 |
| **4小時** | 業務停擺 | $20,000 | 部分客戶流失 | 無 |
| **24小時** | 重大損失 | $120,000 | 大量客戶流失 | 可能違約 |
| **1週** | 生存威脅 | $840,000+ | 品牌嚴重受損 | 合約賠償 |

**評分準則**：
- **財務損失**：直接營收損失+間接成本
- **客戶影響**：滿意度下降、流失率、品牌傷害
- **法規影響**：合約違約、SLA罰款、個資法

---

**步驟3：RTO/RPO目標設定** (45分鐘)

根據影響評估，設定合理且可實現的目標：

```
決策矩陣 Decision Matrix:

業務影響 ↑
High │  ⭐         ⭐⭐        ⭐⭐⭐
     │  RTO: 24h   RTO: 4h    RTO: 1h
     │  RPO: 24h   RPO: 1h    RPO: 0
     │
Med  │  ⭐         ⭐⭐        ⭐⭐
     │  RTO: 72h   RTO: 24h   RTO: 4h
     │  RPO: 24h   RPO: 4h    RPO: 15min
     │
Low  │  ⭐         ⭐         ⭐
     │  RTO: 1周    RTO: 72h   RTO: 24h
     │  RPO: 1周    RPO: 24h   RPO: 4h
     └────────────────────────────→
        Low        Medium      High
                 成本承受度 Cost Tolerance
```

**實作練習**：  
為本公司5個核心系統設定RTO/RPO，並說明理由。

---

### 模組1.4：ISO 27001 A17合規要求 (1.5小時)
### Module 1.4: ISO 27001 A17 Compliance

#### A17.1.1 規劃資訊安全連續性
#### Planning Information Security Continuity

**控制措施要求**：
> 組織應建立並文件化資訊安全連續性需求，包含BCP/DR計劃。

**合規檢查清單**：
- [ ] 已識別所有關鍵IT系統與服務
- [ ] 已定義每個系統的RTO/RPO
- [ ] 已進行業務影響分析（BIA）
- [ ] 已制定BCP/DR書面計劃
- [ ] 計劃已經管理層批准
- [ ] 計劃每年審查與更新

**稽核證據**：
- BIA報告
- RTO/RPO定義文件
- BCP/DR計劃（含版本記錄）
- 管理審查會議記錄

---

#### A17.1.2 實施資訊安全連續性
#### Implementing Information Security Continuity

**控制措施要求**：
> 組織應建立、文件化、實施並維護流程、程序與控制措施，以確保在中斷情況下資訊安全連續性。

**技術實施要點**：
1. **備份機制**：
   - 定期備份（符合RPO）
   - 異地儲存（≥50km）
   - 加密保護

2. **HA架構**：
   - 冗餘配置（無單點故障）
   - 自動或手動故障轉移
   - 負載均衡

3. **復原程序**：
   - 詳細復原步驟
   - 聯絡清單
   - 決策流程

**稽核證據**：
- 備份執行紀錄（每日）
- HA配置文件
- 復原程序SOP
- 系統架構圖

---

#### A17.1.3 驗證、審查與評估
#### Verify, Review and Evaluate

**控制措施要求**：
> 組織應定期驗證與測試BCP/DR計劃，確保其有效性。

**測試類型與頻率**：

| 測試類型 | 說明 | 頻率 | 參與者 |
|---------|------|------|--------|
| **桌面演練** | 紙上模擬，討論應對 | 每季 | IT團隊 |
| **功能測試** | 測試單一系統復原 | 每月 | 系統管理員 |
| **完整演練** | 實際切換至DR站點 | 每年 | 全IT+業務 |

**當前狀況**：
- 🔴 **桌面演練**：0次/年（目標4次）
- 🔴 **功能測試**：1次/季（目標12次/年）
- 🔴 **完整演練**：0次（目標1次/年）

**稽核證據**：
- 演練計劃
- 演練報告（含發現問題）
- 改善措施追蹤
- 照片/錄影記錄

---

### 模組1.5：單點故障識別實作 (1.5小時)
### Module 1.5: Single Point of Failure Identification

#### 當前架構檢視 Current Architecture Review

**系統架構圖**（簡化版）：

```
                    Internet
                       │
                       │
                  ┌────▼────┐
                  │ 防火牆   │ ◄─── ⚠️ SPOF #1
                  │pfSense  │
                  └────┬────┘
                       │
              ┌────────┴────────┐
              │                  │
         ┌────▼────┐        ┌───▼────┐
         │ 核心交換機│◄──┐   │ WiFi AP │
         │         │    │   │         │
         └────┬────┘    │   └─────────┘
              │         │
    ┌─────────┼─────────┼─────────┐
    │         │         │         │
┌───▼───┐ ┌──▼───┐  ┌──▼───┐ ┌──▼───┐
│ AD DC  │ │ERP/DB│  │ NAS  │ │Mail  │
│單DC ⚠️│ │單機 ⚠️│  │      │ │      │
└────────┘ └──────┘  └──────┘ └──────┘
  SPOF#2    SPOF#3
```

**識別的單點故障 (SPOF)**：

1. **🔴 SPOF #1: 防火牆單機**
   - 影響：全網斷網，所有服務中斷
   - 機率：中（硬體3年）
   - 風險等級：極高
   - 改善方案：HA防火牆對（$3-5k）

2. **🔴 SPOF #2: AD域控單機**
   - 影響：無法登入任何系統
   - 機率：中（5年老舊伺服器）
   - 風險等級：極高
   - 改善方案：增加第2台DC（$10k）

3. **🔴 SPOF #3: 核心業務系統/資料庫單機**
   - 影響：業務全面停擺
   - 機率：高（90%，硬體老化）
   - 風險等級：極高
   - 改善方案：SQL Always On集群（$30-50k）

4. **🟡 SPOF #4: 核心交換機單台**
   - 影響：全網斷網
   - 機率：低（2年新設備）
   - 風險等級：中
   - 改善方案：堆疊交換機（$5-8k）

**實作練習**：  
在白板上繪製當前架構，標註所有SPOF。

---

### 模組1.6：Day 1總結與作業 (1小時)
### Module 1.6: Day 1 Summary & Homework

#### 關鍵知識點回顧 Key Takeaways

✅ **RTO = 停機時間目標**（業務連續性）  
✅ **RPO = 數據損失目標**（數據完整性）  
✅ **BIA = 影響分析**（設定目標的依據）  
✅ **SPOF = 單點故障**（必須消除）  
✅ **ISO 27001 A17 = 合規要求**（計劃+實施+測試）

#### Day 1作業 Homework

**任務1：完成RTO/RPO初稿** (2小時)
- 為本公司10個主要系統設定RTO/RPO
- 使用提供的Excel模板
- 說明設定理由與業務影響

**任務2：繪製詳細SPOF清單** (1小時)
- 識別所有單點故障（硬體+軟體+流程）
- 評估風險等級（高/中/低）
- 提出改善優先序

**任務3：閱讀資料** (1小時)
- ISO 27001:2022 Annex A.17（3頁）
- 災難復原案例研究（Colonial Pipeline）

**提交截止**：Day 2上課前

---

## 第二天：高可用性架構設計
## Day 2: High Availability Architecture

### 模組2.1：HA基礎概念 (1.5小時)
### Module 2.1: HA Fundamentals

#### 可用性計算 Availability Calculation

**可用性公式**：
```
可用性 % = (總時間 - 停機時間) / 總時間 × 100%
Availability = (Total Time - Downtime) / Total Time × 100%

範例：
年度總時間 = 365天 × 24小時 = 8,760小時
停機時間 = 24小時
可用性 = (8,760 - 24) / 8,760 × 100% = 99.73%
```

**可用性等級對照表**：

| 等級 | 可用性 % | 年度停機時間 | 適用系統 |
|------|---------|-------------|---------|
| **2個9** | 99% | 3.65天 (87.6小時) | 非關鍵 |
| **3個9** | 99.9% | 8.76小時 | 一般業務 |
| **4個9** | 99.99% | 52.56分鐘 | 重要業務 |
| **5個9** | 99.999% | 5.26分鐘 | 關鍵任務 |

**本公司目標**（初稿）：
- 核心業務系統：99.5%（≤44小時/年）
- 客戶資料庫：99.5%
- AD/郵件：99%（≤88小時/年）

---

#### HA架構類型 HA Architecture Types

**1. 主備配置 (Active-Passive)**

```
          負載均衡器
          Load Balancer
               │
        ┌──────┴──────┐
        │              │
    ┌───▼───┐      ┌──▼───┐
    │主節點  │      │備節點 │
    │Active │◄────►│Passive│
    │  🟢   │心跳   │  ⚫   │
    └───┬───┘      └──────┘
        │
    共享儲存
```

**特點**：
- ✅ 成本較低（備機平時閒置）
- ✅ 簡單易實施
- ❌ 資源利用率低（50%）
- ❌ 切換時間較長（1-5分鐘）

**適用場景**：  
資料庫、AD域控、關鍵應用伺服器

---

**2. 雙活配置 (Active-Active)**

```
          負載均衡器
          Load Balancer
               │
        ┌──────┴──────┐
        │              │
    ┌───▼───┐      ┌──▼───┐
    │節點1  │      │節點2  │
    │Active │◄────►│Active │
    │  🟢   │同步   │  🟢   │
    └───┬───┘      └───┬───┘
        └──────┬───────┘
            共享儲存
```

**特點**：
- ✅ 資源利用率高（100%）
- ✅ 效能提升（負載分散）
- ✅ 切換時間極短（<1秒）
- ❌ 成本較高
- ❌ 配置複雜（需數據同步）

**適用場景**：  
Web伺服器、應用伺服器群集、高流量系統

---

**3. N+1冗餘 (N+1 Redundancy)**

```
    負載均衡器
         │
    ┌────┼────┬────┐
    │    │    │    │
  ┌─▼─┐┌─▼─┐┌─▼─┐┌─▼─┐
  │ 1 ││ 2 ││ 3 ││備用│
  │🟢 ││🟢 ││🟢 ││ ⚫ │
  └───┘└───┘└───┘└───┘
  處理100%   處理33%負載
```

**特點**：
- ✅ 高可用性（任一台故障仍正常）
- ✅ 可承受多台同時故障
- ❌ 成本最高
- 📊 常見配比：2+1、3+1、4+2

**適用場景**：  
大型網站、SaaS平台、電信級系統

---

### 模組2.2：Proxmox VE HA實作 (3小時)
### Module 2.2: Proxmox VE HA Implementation

#### Proxmox VE集群架構 Cluster Architecture

**最小HA配置**（本公司適用）：

```
┌──────────────────────────────────────┐
│         Proxmox VE Cluster           │
├──────────────────────────────────────┤
│                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐
│  │ Node 1  │  │ Node 2  │  │ Node 3  │
│  │ pve01   │  │ pve02   │  │ pve03   │
│  │ (投票)   │  │ (投票)   │  │ (QDevice)│
│  └────┬────┘  └────┬────┘  └────┬────┘
│       │            │            │
│       └────────────┴────────────┘
│              集群網路
│            Cluster Network
│                                      │
│  共享儲存: Ceph / NFS / iSCSI        │
└──────────────────────────────────────┘
```

**硬體需求**：
- 節點1 & 2：各$15,000（生產節點）
  - CPU: 8核心以上
  - RAM: 64GB+
  - 儲存: 1TB SSD（系統） + 4TB HDD（VM）
  - 網路: 雙10G網卡

- 節點3：$5,000（QDevice輕量級）
  - CPU: 4核心
  - RAM: 16GB
  - 儲存: 256GB SSD
  - 網路: 1G網卡

**總預算**: ~$35,000（硬體）+ $0（Proxmox開源免費）

---

#### 實作步驟 Implementation Steps

**階段1：安裝Proxmox VE** (30分鐘/節點)

1. 下載Proxmox VE ISO: https://www.proxmox.com/en/downloads
2. 製作USB開機碟
3. 安裝系統（選擇ZFS RAID1用於系統碟）
4. 配置網路（管理IP、集群IP）

**網路配置範例**：
```bash
# /etc/network/interfaces (Node 1)
auto vmbr0
iface vmbr0 inet static
    address 192.168.1.101/24
    gateway 192.168.1.1
    bridge-ports eno1
    bridge-stp off

auto vmbr1
iface vmbr1 inet static
    address 10.0.0.101/24  # 集群專用網路
    bridge-ports eno2
    bridge-stp off
```

---

**階段2：建立Proxmox集群** (30分鐘)

在Node 1執行：
```bash
# 建立集群
pvecm create production-cluster

# 查看狀態
pvecm status
```

在Node 2 & 3執行：
```bash
# 加入集群（從Node 1取得join資訊）
pvecm add 192.168.1.101
```

驗證集群：
```bash
# 查看所有節點
pvecm nodes

# 查看仲裁狀態（Quorum）
pvecm expected 3
```

---

**階段3：配置共享儲存** (1小時)

**選項A：Ceph（推薦，內建於Proxmox）**

```bash
# 安裝Ceph（在所有節點）
pveceph install

# 建立Ceph OSD（在Node 1 & 2，各使用4TB HDD）
pveceph osd create /dev/sdb

# 建立Ceph Pool
pveceph pool create vm-storage --size 2
```

**選項B：NFS（較簡單，需額外NAS）**

```bash
# 在Proxmox WebUI:
# Datacenter → Storage → Add → NFS
# Server: 192.168.1.10
# Export: /mnt/proxmox-storage
# Content: VZDump, Disk Image, ISO
```

---

**階段4：啟用HA功能** (30分鐘)

```bash
# WebUI操作:
# Datacenter → HA → Add
# 選擇要保護的VM
# 設定優先級（高/中/低）
```

**HA策略配置**：
```yaml
# /etc/pve/ha/resources.cfg
vm: 100
    state started
    group production
    max_restart 3
    max_relocate 2
```

**測試故障轉移**：
```bash
# 模擬Node 1故障（拔網路線或關機）
# 觀察VM自動遷移至Node 2（約2-3分鐘）

# 查看HA日誌
ha-manager status
```

---

### 模組2.3：SQL Server Always On實作 (2.5小時)
### Module 2.3: SQL Server Always On Implementation

#### Always On架構 Architecture

```
┌────────────────────────────────────────┐
│    SQL Server Always On AG             │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────┐      ┌──────────┐       │
│  │ Primary  │◄────►│Secondary │       │
│  │ Replica  │ 同步  │ Replica  │       │
│  │ (Node1)  │      │ (Node2)  │       │
│  └────┬─────┘      └────┬─────┘       │
│       │                  │             │
│       └──────┬───────────┘             │
│              │                         │
│      ┌───────▼────────┐                │
│      │ Availability   │                │
│      │ Group Listener │                │
│      │ (Virtual IP)   │                │
│      └────────────────┘                │
│                                        │
│  應用程式連線至Listener，自動切換      │
└────────────────────────────────────────┘
```

**優點**：
- ✅ RPO = 0（同步模式零數據損失）
- ✅ RTO ≤ 5分鐘（自動故障轉移）
- ✅ 可讀次要副本（分散查詢負載）

**前置需求**：
- Windows Server 2019+ Enterprise / Datacenter
- SQL Server 2019+ Enterprise / Standard
- Windows Server Failover Clustering (WSFC)
- 共享儲存（或每節點獨立儲存）

---

#### 實作步驟 Implementation Steps

**階段1：準備Windows Server環境** (30分鐘)

兩台VM配置：
```
VM1 (Primary):
- OS: Windows Server 2022
- CPU: 4核心
- RAM: 16GB
- 儲存: 100GB (OS) + 500GB (數據)
- IP: 192.168.1.111

VM2 (Secondary):
- 同VM1規格
- IP: 192.168.1.112

Listener VIP: 192.168.1.110
```

安裝Failover Clustering功能：
```powershell
# 在兩台伺服器執行
Install-WindowsFeature -Name Failover-Clustering `
    -IncludeManagementTools

# 驗證集群準備度
Test-Cluster -Node SQL01, SQL02
```

---

**階段2：建立Windows Failover Cluster** (20分鐘)

```powershell
# 在Node 1執行
New-Cluster -Name SQLCluster `
    -Node SQL01, SQL02 `
    -StaticAddress 192.168.1.100

# 驗證集群
Get-ClusterNode
```

---

**階段3：安裝SQL Server** (40分鐘)

在兩台伺服器安裝SQL Server：
- 版本：SQL Server 2022 Standard（$3,000/節點）
- 功能：Database Engine, Management Tools
- 實例名稱：MSSQLSERVER（預設實例）

**重要**：啟用Always On功能
```powershell
# SQL Server Configuration Manager
# SQL Server服務屬性 → Always On高可用性 → ✅ 啟用
```

---

**階段4：建立Always On Availability Group** (40分鐘)

使用SQL Server Management Studio (SSMS)：

1. **備份資料庫**：
```sql
-- 在Primary執行
BACKUP DATABASE [CustomerDB] 
TO DISK = 'C:\Backup\CustomerDB.bak'

BACKUP LOG [CustomerDB] 
TO DISK = 'C:\Backup\CustomerDB.trn'
```

2. **在Secondary還原**：
```sql
-- 在Secondary執行
RESTORE DATABASE [CustomerDB] 
FROM DISK = '\\SQL01\Backup\CustomerDB.bak'
WITH NORECOVERY

RESTORE LOG [CustomerDB] 
FROM DISK = '\\SQL01\Backup\CustomerDB.trn'
WITH NORECOVERY
```

3. **建立AG**：
```sql
-- 在Primary執行
CREATE AVAILABILITY GROUP [AG_Production]
FOR DATABASE [CustomerDB]
REPLICA ON 
    'SQL01' WITH (
        ENDPOINT_URL = 'TCP://SQL01.domain.local:5022',
        AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
        FAILOVER_MODE = AUTOMATIC,
        SECONDARY_ROLE(ALLOW_CONNECTIONS = READ_ONLY)
    ),
    'SQL02' WITH (
        ENDPOINT_URL = 'TCP://SQL02.domain.local:5022',
        AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
        FAILOVER_MODE = AUTOMATIC,
        SECONDARY_ROLE(ALLOW_CONNECTIONS = READ_ONLY)
    );

-- 建立Listener
ALTER AVAILABILITY GROUP [AG_Production]
ADD LISTENER 'AG-Listener' (
    WITH IP ((N'192.168.1.110', N'255.255.255.0')),
    PORT = 1433
);
```

4. **加入Secondary到AG**：
```sql
-- 在SQL02執行
ALTER AVAILABILITY GROUP [AG_Production] JOIN;
ALTER DATABASE [CustomerDB] SET HADR AVAILABILITY GROUP = [AG_Production];
```

---

**階段5：測試故障轉移** (20分鐘)

```sql
-- 查看AG狀態
SELECT 
    ag.name AS AGName,
    ar.replica_server_name AS ReplicaName,
    ar.availability_mode_desc AS AvailabilityMode,
    ars.role_desc AS Role,
    ars.synchronization_health_desc AS SyncHealth
FROM sys.availability_groups ag
JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
JOIN sys.dm_hadr_availability_replica_states ars ON ar.replica_id = ars.replica_id;

-- 手動故障轉移測試
ALTER AVAILABILITY GROUP [AG_Production] FAILOVER;

-- 觀察角色切換（Primary ↔ Secondary）
```

**應用程式連線字串**：
```
Server=AG-Listener,1433;Database=CustomerDB;...
```
自動連線至當前Primary，故障時自動切換。

---

### 模組2.4：負載均衡器配置 (1小時)
### Module 2.4: Load Balancer Configuration

#### HAProxy配置範例 (開源方案)

**安裝HAProxy**（在獨立VM或容器）：
```bash
# Ubuntu/Debian
apt-get install haproxy

# 配置檔: /etc/haproxy/haproxy.cfg
```

**配置Web應用負載均衡**：
```
global
    log /dev/log local0
    maxconn 4096
    user haproxy
    group haproxy
    daemon

defaults
    log global
    mode http
    option httplog
    option dontlognull
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

# 前端設定
frontend http-in
    bind *:80
    default_backend web-servers

# 後端伺服器池
backend web-servers
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    
    server web1 192.168.1.201:80 check inter 2000 rise 2 fall 3
    server web2 192.168.1.202:80 check inter 2000 rise 2 fall 3
    server web3 192.168.1.203:80 check backup  # 備用伺服器
```

**健康檢查機制**：
- `check inter 2000`: 每2秒檢查一次
- `rise 2`: 連續2次成功視為UP
- `fall 3`: 連續3次失敗視為DOWN

**測試**：
```bash
# 查看狀態
echo "show stat" | socat stdio /var/lib/haproxy/stats

# 模擬web1故障（停止web1服務）
# 觀察流量自動轉向web2 & web3
```

---

### 模組2.5：Day 2總結與作業 (30分鐘)
### Module 2.5: Day 2 Summary & Homework

#### 關鍵知識點 Key Takeaways

✅ **可用性 = 減少停機時間**  
✅ **主備配置 = 簡單+成本低**（適合本公司）  
✅ **雙活配置 = 高效能+零停機**（未來目標）  
✅ **Proxmox HA = VM層級保護**  
✅ **SQL Always On = 資料庫HA**（RPO=0）

#### Day 2作業 Homework

**任務1：設計HA方案** (3小時)
- 為本公司3個SPOF系統設計HA方案
- 繪製架構圖
- 估算成本與實施時間

**任務2：安裝測試環境** (2小時)
- 在筆電/工作站安裝VirtualBox
- 建立2台Proxmox VE虛擬機
- 嘗試組成最小集群（2節點）

**任務3：閱讀資料** (1小時)
- Proxmox VE HA官方文檔（第4章）
- SQL Server Always On最佳實踐

---

## 第三天：災難復原計劃制定
## Day 3: Disaster Recovery Planning

### 模組3.1：DR計劃框架 (1.5小時)
### Module 3.1: DR Plan Framework

#### DR計劃結構 DR Plan Structure

```
災難復原計劃 Disaster Recovery Plan
├── 1. 執行摘要 Executive Summary
│   ├── 計劃目的與範疇
│   ├── RTO/RPO總覽
│   └── 關鍵聯絡人
│
├── 2. 災難定義與分類 Disaster Classification
│   ├── 硬體故障
│   ├── 軟體故障
│   ├── 人為錯誤
│   ├── 自然災害
│   └── 網路攻擊
│
├── 3. 角色與責任 Roles & Responsibilities
│   ├── DR指揮官
│   ├── 技術團隊
│   ├── 溝通協調
│   └── 業務聯絡人
│
├── 4. 系統清單與優先級 System Inventory
│   ├── Tier 1系統（優先復原）
│   ├── Tier 2系統
│   └── Tier 3系統
│
├── 5. 復原程序 Recovery Procedures
│   ├── 宣告災難流程
│   ├── 系統復原SOP（每個系統獨立章節）
│   ├── 數據還原步驟
│   └── 服務驗證清單
│
├── 6. DR站點與資源 DR Site & Resources
│   ├── 異地備份位置
│   ├── 備援硬體清單
│   ├── 網路配置
│   └── 供應商聯絡資訊
│
├── 7. 溝通計劃 Communication Plan
│   ├── 內部通報流程
│   ├── 客戶通知範本
│   └── 媒體應對（如適用）
│
└── 8. 測試與維護 Testing & Maintenance
    ├── 年度演練計劃
    ├── 計劃更新流程
    └── 訓練需求
```

---

### 模組3.2：異地備份策略 (2小時)
### Module 3.2: Offsite Backup Strategy

#### 3-2-1-1-0備份黃金法則 (進階版)

```
3 份數據副本 3 Copies
2 種不同媒體 2 Different Media
1 份異地儲存 1 Offsite
1 份離線備份 1 Offline (Air-gapped)
0 個錯誤驗證 0 Errors in Verification
```

**本公司實施方案**：

```
┌─────────────────────────────────────────┐
│         備份拓撲 Backup Topology        │
├─────────────────────────────────────────┤
│                                         │
│  生產系統 Production (副本 #1)          │
│  ├─ SQL Server                          │
│  ├─ 檔案伺服器                          │
│  └─ VM映像                              │
│        │                                │
│        ▼ (每日完整 + 每小時增量)        │
│                                         │
│  本地備份 Local Backup (副本 #2)        │
│  📦 NAS/Backup Server                   │
│  儲存媒體: SSD (快速還原)               │
│  保留期: 30天                           │
│        │                                │
│        ▼ (每日同步)                     │
│                                         │
│  異地雲端 Offsite Cloud (副本 #3)       │
│  ☁️ Backblaze B2 / AWS S3 Glacier      │
│  儲存媒體: 雲端物件儲存                 │
│  保留期: 90天                           │
│        │                                │
│        ▼ (每週)                         │
│                                         │
│  離線備份 Offline (Air-gapped)          │
│  💾 外接硬碟（實體隔離）                │
│  儲存位置: 銀行保險箱                   │
│  保留期: 1年（月度）                    │
└─────────────────────────────────────────┘
```

---

#### 異地備份選項比較

| 方案 | 成本/月 | RPO | 還原時間 | 優點 | 缺點 |
|------|---------|-----|----------|------|------|
| **Backblaze B2** | $50-200 | 24h | 6-12h | 便宜、簡單 | 還原慢 |
| **AWS S3 Glacier** | $100-300 | 24h | 12-48h | 可靠性高 | 還原非常慢 |
| **Azure Backup** | $150-400 | 24h | 4-8h | 整合性佳 | 貴 |
| **實體異地** | $200-500 | 24h | 2-4h | 還原快 | 需維護 |

**本公司推薦**：Backblaze B2（成本效益最佳）

---

#### Veeam Backup & Replication配置

**備份任務配置範例**：

```
┌────────────────────────────────────┐
│ Veeam Backup Job: Production-Daily │
├────────────────────────────────────┤
│                                    │
│ 來源 Source:                       │
│  ☑ VM: ERP-Server                  │
│  ☑ VM: SQL-Server                  │
│  ☑ VM: AD-DC01                     │
│                                    │
│ 目的地 Destination:                │
│  📦 Local: \\NAS\Backup\           │
│  ☁️ Cloud: Backblaze B2 Bucket     │
│                                    │
│ 排程 Schedule:                     │
│  ⏰ 每日 23:00                     │
│  🔄 增量: 每小時（工作時間）       │
│                                    │
│ 保留 Retention:                    │
│  Local: 30天                       │
│  Cloud: 90天                       │
│                                    │
│ 選項 Options:                      │
│  ✅ 應用感知處理（VSS）             │
│  ✅ 備份驗證（自動還原測試）        │
│  ✅ 壓縮與加密                      │
└────────────────────────────────────┘
```

**PowerShell自動化腳本**：
```powershell
# 每月完整備份至外接硬碟（離線備份）
$date = Get-Date -Format "yyyy-MM"
$source = "\\NAS\Backup\Production"
$dest = "E:\Offline-Backup\$date"  # E: = 外接硬碟

# 複製最新完整備份
robocopy $source $dest /MIR /R:3 /W:10 /LOG:backup.log

# 驗證檔案完整性
$sourceHash = Get-FileHash "$source\*.vbk"
$destHash = Get-FileHash "$dest\*.vbk"

if ($sourceHash.Hash -eq $destHash.Hash) {
    Write-Host "✅ 離線備份驗證成功" -ForegroundColor Green
    
    # 拔除硬碟，送至異地保管
    Write-Host "🔒 請將硬碟標示 '$date' 並送至保險箱" -ForegroundColor Yellow
} else {
    Write-Host "❌ 備份驗證失敗！" -ForegroundColor Red
}
```

---

### 模組3.3：復原程序設計 (2.5小時)
### Module 3.3: Recovery Procedure Design

#### 系統復原SOP範本

**範例：SQL Server資料庫復原程序**

```markdown
# SQL Server災難復原程序
# SQL Server Disaster Recovery Procedure

## 前置條件 Prerequisites
- [ ] DR站點硬體已準備（或替代伺服器）
- [ ] 最新備份可存取
- [ ] 網路連線正常
- [ ] SQL Server已安裝（相同版本）

## 復原步驟 Recovery Steps

### 階段1：評估與準備 (15分鐘)
1. 確認災難類型與範圍
   - 硬體故障？軟體損壞？數據損毀？
   - 影響哪些資料庫？

2. 確定復原點
   - 使用最新備份？或特定時間點？
   - RPO: 15分鐘 → 查找最接近的備份

3. 通知利害關係人
   - 通知: IT經理、業務主管
   - 預估復原時間: RTO 4小時

### 階段2：備份檔案取得 (30分鐘)
4. 從本地備份還原（優先）
   ```powershell
   # 複製備份檔至復原伺服器
   robocopy \\NAS\Backup\SQL D:\Restore\ /MIR
   ```

5. 若本地備份不可用，從雲端下載
   ```bash
   # 從Backblaze B2下載
   b2 sync b2://backup-bucket/sql-backup/ D:\Restore\
   ```

6. 驗證備份檔案完整性
   ```powershell
   # 檢查檔案大小與雜湊值
   Get-ChildItem D:\Restore\*.bak | 
       Get-FileHash -Algorithm SHA256
   ```

### 階段3：資料庫還原 (1-2小時)
7. 停止應用程式連線
   ```sql
   -- 設定資料庫為單使用者模式
   ALTER DATABASE CustomerDB 
   SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
   ```

8. 還原完整備份
   ```sql
   RESTORE DATABASE CustomerDB
   FROM DISK = 'D:\Restore\CustomerDB_Full_20260130.bak'
   WITH NORECOVERY,
        MOVE 'CustomerDB_Data' TO 'D:\Data\CustomerDB.mdf',
        MOVE 'CustomerDB_Log' TO 'D:\Data\CustomerDB_log.ldf',
        STATS = 10;
   ```

9. 還原差異備份（如有）
   ```sql
   RESTORE DATABASE CustomerDB
   FROM DISK = 'D:\Restore\CustomerDB_Diff_20260130_2200.bak'
   WITH NORECOVERY,
        STATS = 10;
   ```

10. 還原交易日誌備份（達到RPO目標）
    ```sql
    RESTORE LOG CustomerDB
    FROM DISK = 'D:\Restore\CustomerDB_Log_20260130_2300.trn'
    WITH NORECOVERY;
    
    -- 重複直到最後一個日誌備份
    
    -- 最後一個日誌，使用RECOVERY恢復線上
    RESTORE LOG CustomerDB
    FROM DISK = 'D:\Restore\CustomerDB_Log_20260130_2345.trn'
    WITH RECOVERY;
    ```

11. 恢復多使用者模式
    ```sql
    ALTER DATABASE CustomerDB 
    SET MULTI_USER;
    ```

### 階段4：驗證與測試 (30分鐘)
12. 資料庫完整性檢查
    ```sql
    DBCC CHECKDB(CustomerDB) 
    WITH NO_INFOMSGS, ALL_ERRORMSGS;
    ```

13. 驗證關鍵數據
    ```sql
    -- 檢查記錄數量
    SELECT COUNT(*) FROM Customers;
    SELECT COUNT(*) FROM Orders;
    
    -- 檢查最後交易時間
    SELECT MAX(OrderDate) FROM Orders;
    -- 應接近災難發生時間
    ```

14. 測試應用程式連線
    - 從測試機連線資料庫
    - 執行基本查詢
    - 測試CRUD操作

### 階段5：服務恢復 (30分鐘)
15. 更新連線字串（如IP變更）
    ```
    舊: Server=192.168.1.111,1433;...
    新: Server=192.168.1.199,1433;...  # DR伺服器
    ```

16. 啟動應用程式服務
    - 重啟IIS應用程式池
    - 啟動Windows服務
    - 驗證前端可正常存取

17. 監控系統狀態
    - 觀察CPU/記憶體使用
    - 檢查錯誤日誌
    - 測試關鍵交易

### 階段6：通知與文檔 (15分鐘)
18. 通知服務恢復
    - Email通知: 業務單位、客戶（如需要）
    - 更新狀態頁面

19. 記錄復原過程
    - 填寫災難復原報告
    - 記錄實際RTO/RPO
    - 記錄問題與改善建議

## 驗收標準 Acceptance Criteria
✅ 資料庫可正常查詢與寫入
✅ 應用程式功能正常
✅ 效能符合基準（與災難前比較）
✅ 無數據損毀或遺失（在RPO範圍內）
✅ 實際RTO ≤ 4小時

## 回滾計劃 Rollback Plan
若復原失敗，啟動Plan B:
1. 嘗試從更早的備份還原
2. 聯絡SQL Server供應商技術支援
3. 若無法復原，啟動手動作業流程（紙本程序）

## 聯絡資訊 Contacts
- DR指揮官: IT經理 (手機: XXX)
- DBA: 資料庫管理員 (手機: XXX)
- 應用程式負責人: 開發主管 (手機: XXX)
- 供應商: Microsoft Support (1-800-XXX-XXXX)
```

---

### 模組3.4：DR站點規劃 (1.5小時)
### Module 3.4: DR Site Planning

#### DR站點類型 DR Site Types

**1. 冷站 (Cold Site)**
```
設施：空機房 + 基礎設施（電力、網路、空調）
設備：無IT設備（災難時才採購或調度）
數據：異地備份（需還原）
RTO：1-4週
成本：$500-2,000/月（租金）

適用：非關鍵業務、可接受長時間中斷
```

**2. 溫站 (Warm Site)**
```
設施：機房 + 基礎設施
設備：部分IT設備已安裝（但未運行）
數據：定期同步（每日/每週）
RTO：1-3天
成本：$5,000-15,000/月

適用：中等關鍵業務、本公司當前最適合
```

**3. 熱站 (Hot Site)**
```
設施：完整機房
設備：與生產環境相同（已運行）
數據：即時同步（Always On、複寫）
RTO：<1小時
成本：$20,000-50,000/月

適用：關鍵任務、金融、電商、無法中斷
```

---

#### 本公司DR站點建議方案

**混合DR策略**（成本最優）：

```
┌────────────────────────────────────────┐
│    本公司DR架構 Hybrid DR Strategy    │
├────────────────────────────────────────┤
│                                        │
│  生產站點（台北辦公室）                │
│  ┌──────────────────────┐              │
│  │ 生產系統 Production   │              │
│  │ • ERP/SQL Server     │              │
│  │ • AD DC01            │              │
│  │ • 檔案伺服器          │              │
│  └───────┬──────────────┘              │
│          │                             │
│          ▼ (即時同步 Real-time)        │
│                                        │
│  雲端DR（Azure/AWS - 熱站模式）        │
│  ┌──────────────────────┐              │
│  │ ☁️ SQL Always On AG  │ ◄─ 關鍵系統  │
│  │ • Secondary Replica  │    RTO: 1h   │
│  │ • 自動故障轉移        │              │
│  └──────────────────────┘              │
│          +                             │
│                                        │
│  異地辦公室（新竹/台中 - 溫站模式）    │
│  ┌──────────────────────┐              │
│  │ 備援硬體（待命）      │ ◄─ 次要系統  │
│  │ • 備用伺服器(已安裝)  │    RTO: 24h  │
│  │ • 每日備份同步        │              │
│  └──────────────────────┘              │
│          +                             │
│                                        │
│  離線備份（銀行保險箱 - 冷備份）       │
│  ┌──────────────────────┐              │
│  │ 💾 月度完整備份       │ ◄─ 最後防線  │
│  │ • 外接硬碟            │    保留: 1年 │
│  │ • 實體隔離            │              │
│  └──────────────────────┘              │
└────────────────────────────────────────┘
```

**預算估算**：
- 雲端DR（Azure SQL MI）: ~$800/月
- 異地辦公室硬體: $15,000（一次性）+ $200/月（電費網路）
- 離線備份: $100/月（保險箱租金）
- **總計**: $1,100/月 + $15,000初期投入

---

### 模組3.5：Day 3實作練習 (2小時)
### Module 3.5: Day 3 Hands-on Exercise

#### 練習：撰寫DR計劃初稿

**分組作業**（2-3人一組）：

**任務**：為以下系統撰寫DR計劃（使用提供的範本）

1. **Group A**: AD域控制器DR計劃
2. **Group B**: 檔案伺服器DR計劃
3. **Group C**: 郵件系統DR計劃

**包含章節**：
- 系統描述與依賴關係
- RTO/RPO目標
- 備份策略
- 復原程序（至少10個步驟）
- 驗收標準
- 聯絡清單

**時間**：90分鐘  
**發表**：每組10分鐘簡報

---

### 模組3.6：Day 3總結與作業 (30分鐘)
### Module 3.6: Day 3 Summary & Homework

#### 關鍵知識點 Key Takeaways

✅ **3-2-1-1-0備份法則**  
✅ **異地備份 ≠ DR**（還需要硬體+流程）  
✅ **DR站點分級**（冷/溫/熱）  
✅ **復原程序必須詳細且可執行**  
✅ **定期測試才能驗證有效性**

#### Day 3作業 Homework

**任務1：完成本公司DR計劃** (5小時)
- 使用今日學習的範本
- 涵蓋所有Tier 1 & 2系統
- 至少30頁完整文件

**任務2：DR成本效益分析** (2小時)
- 比較3種DR方案（雲端/自建/混合）
- 計算ROI（投資回報）
- 建議最終方案

**任務3：準備Day 4實作** (1小時)
- 確認實驗環境正常
- 準備測試數據
- 閱讀Proxmox HA文檔

---

## 第四天：實作演練
## Day 4: Hands-on Implementation

### 模組4.1：實驗環境建置 (1小時)
### Module 4.1: Lab Environment Setup

#### 實驗拓撲 Lab Topology

```
┌────────────────────────────────────────┐
│          實驗環境架構圖                 │
│          Lab Architecture              │
├────────────────────────────────────────┤
│                                        │
│  物理主機 Physical Host                │
│  • Windows 10/11 or Linux              │
│  • VMware Workstation / VirtualBox    │
│  • CPU: 8核心 RAM: 32GB+               │
│                                        │
│  ┌────────────────────────────────┐   │
│  │   虛擬機 Virtual Machines      │   │
│  │                                │   │
│  │  ┌──────┐  ┌──────┐  ┌──────┐ │   │
│  │  │PVE-01│  │PVE-02│  │PVE-03│ │   │
│  │  │      │  │      │  │      │ │   │
│  │  │4C/8GB│  │4C/8GB│  │2C/4GB│ │   │
│  │  └───┬──┘  └───┬──┘  └───┬──┘ │   │
│  │      └─────────┴─────────┘    │   │
│  │         Cluster Network        │   │
│  │         (10.0.0.0/24)         │   │
│  │                                │   │
│  │  共享儲存 Shared Storage:      │   │
│  │  • NFS (模擬)                  │   │
│  │  • or Ceph (3節點)             │   │
│  └────────────────────────────────┘   │
│                                        │
│  測試VM Test Workloads:                │
│  • Ubuntu Web Server                  │
│  • Windows File Server                │
└────────────────────────────────────────┘
```

**下載資源**：
- Proxmox VE ISO: https://www.proxmox.com/en/downloads
- Ubuntu Server: https://ubuntu.com/download/server
- Windows Server評估版: https://www.microsoft.com/evalcenter

---

### 模組4.2：Proxmox HA實作（實際操作）(3小時)
### Module 4.2: Proxmox HA實作（實際操作）(3小時)
### Module 4.2: Proxmox HA Hands-on (3 hours)

#### 實作目標 Lab Objectives

完成後學員將能夠：
- ✅ 建立3節點Proxmox VE集群
- ✅ 配置共享儲存（NFS或Ceph）
- ✅ 建立測試VM並啟用HA
- ✅ 模擬故障並驗證自動復原

---

#### 步驟1：安裝Proxmox VE節點 (45分鐘)

**每位學員操作**（或分組共用環境）：

1. 在VMware/VirtualBox建立3台VM：
   ```
   VM: pve01
   - CPU: 4核心（啟用虛擬化VT-x/AMD-V）
   - RAM: 8GB
   - 磁碟1: 32GB（系統）
   - 磁碟2: 50GB（Ceph OSD，可選）
   - 網卡1: NAT（連接外網）
   - 網卡2: Host-Only (10.0.0.101/24，集群網路)
   
   VM: pve02
   - 同pve01配置
   - 網卡2: 10.0.0.102/24
   
   VM: pve03（輕量QDevice）
   - CPU: 2核心
   - RAM: 4GB
   - 磁碟1: 20GB
   - 網卡2: 10.0.0.103/24
   ```

2. 使用Proxmox ISO安裝系統：
   - 選擇國家/時區
   - 設定root密碼
   - 網路配置（使用網卡2的IP）
   - 完成安裝並重啟

3. 瀏覽器登入Proxmox WebUI：
   - URL: https://10.0.0.101:8006
   - 帳號: root
   - 密碼: (安裝時設定)

---

#### 步驟2：建立Proxmox集群 (30分鐘)

**在pve01執行**：

1. 開啟Shell（WebUI → pve01 → Shell）：
   ```bash
   # 建立集群
   pvecm create production-cluster
   
   # 驗證
   pvecm status
   ```

2. 取得加入資訊：
   ```bash
   # 產生join token
   pvecm add --use_ssh
   # 複製顯示的join指令
   ```

**在pve02 & pve03執行**：

```bash
# 加入集群（貼上從pve01取得的指令）
pvecm add 10.0.0.101 --use_ssh

# 輸入pve01的root密碼
```

**驗證集群狀態**：

```bash
# 在任一節點執行
pvecm nodes
# 應顯示3個節點

pvecm status
# Quorum應為3
```

**截圖檢查點** 📸：  
請截圖`pvecm status`輸出，確認3節點都online。

---

#### 步驟3：配置共享儲存 (45分鐘)

**選項A：NFS共享儲存（較簡單，推薦新手）**

1. 在pve01建立NFS Server：
   ```bash
   # 安裝NFS
   apt-get update
   apt-get install nfs-kernel-server -y
   
   # 建立共享目錄
   mkdir -p /mnt/pve-storage
   chmod 777 /mnt/pve-storage
   
   # 配置NFS輸出
   cat >> /etc/exports <<EOF
   /mnt/pve-storage 10.0.0.0/24(rw,sync,no_subtree_check,no_root_squash)
   EOF
   
   # 啟動NFS
   exportfs -rav
   systemctl restart nfs-kernel-server
   ```

2. 在Proxmox WebUI加入NFS儲存：
   - Datacenter → Storage → Add → NFS
   - ID: `nfs-shared`
   - Server: `10.0.0.101`
   - Export: `/mnt/pve-storage`
   - Content: 勾選 `Disk image`, `ISO image`, `VZDump backup file`
   - Nodes: 選擇所有節點
   - 按下Add

3. 驗證：所有節點應能看到`nfs-shared`儲存。

---

**選項B：Ceph分散式儲存（進階，高可用性）**

```bash
# 在所有節點安裝Ceph
pveceph install --repository no-subscription

# 在pve01初始化Ceph
pveceph init --network 10.0.0.0/24

# 建立Ceph Monitor（在所有節點）
pveceph mon create

# 建立Ceph OSD（在pve01 & pve02，使用磁碟2）
pveceph osd create /dev/sdb

# 建立Ceph Pool
pveceph pool create vm-storage --size 2

# 在WebUI: Datacenter → Storage → Add → RBD
# - ID: ceph-storage
# - Pool: vm-storage
# - Content: Disk image
```

**截圖檢查點** 📸：  
請截圖儲存配置頁面，確認共享儲存已加入。

---

#### 步驟4：建立測試VM並啟用HA (30分鐘)

1. 上傳ISO映像：
   - Storage → local → ISO Images → Upload
   - 上傳Ubuntu Server ISO（或使用下載URL）

2. 建立測試VM：
   ```
   WebUI → 右上角 Create VM
   - General:
     - Node: pve01
     - VM ID: 100
     - Name: web-server-01
   
   - OS:
     - ISO: ubuntu-22.04-server.iso
   
   - System:
     - 預設設定
   
   - Disks:
     - Storage: nfs-shared (重要！必須使用共享儲存)
     - Size: 10GB
   
   - CPU:
     - Cores: 2
   
   - Memory:
     - 2048 MB
   
   - Network:
     - 預設設定
   ```

3. 安裝Ubuntu（快速安裝，最小化選項）

4. 啟用HA保護：
   ```
   WebUI → Datacenter → HA → Add
   - Resource: vm:100 (web-server-01)
   - Request State: started
   - Group: (留空，使用預設)
   - Max restart: 3
   - Max relocate: 2
   ```

**驗證**：
- Datacenter → HA → Resources
- 應看到web-server-01，狀態為started

---

#### 步驟5：故障模擬與驗證 (30分鐘)

**測試1：節點斷電（模擬硬體故障）**

1. 確認web-server-01當前運行在哪個節點（假設pve01）

2. 模擬pve01故障：
   ```bash
   # 在pve01執行（或在VMware中直接強制關機）
   shutdown -h now
   ```

3. 觀察HA Manager行為：
   ```
   在pve02或pve03的WebUI觀察:
   - Datacenter → HA → Status
   - 應看到：
     ⏰ T+0秒: 偵測到pve01不可達
     ⏰ T+60秒: 決定故障轉移
     ⏰ T+90秒: 在pve02啟動web-server-01
     ⏰ T+120秒: VM完全運行
   ```

4. 驗證VM仍可連線：
   ```bash
   # 從任一節點ping VM
   ping <VM-IP>
   
   # SSH連線VM
   ssh user@<VM-IP>
   ```

**預期結果**：
- ✅ VM自動遷移至健康節點
- ✅ 停機時間：2-3分鐘
- ✅ 數據無損失

**截圖檢查點** 📸：  
請截圖故障轉移後的HA Status頁面。

---

**測試2：儲存故障（模擬SAN故障）**

1. 模擬NFS中斷：
   ```bash
   # 在pve01執行（NFS Server）
   systemctl stop nfs-kernel-server
   ```

2. 觀察行為：
   - VM應暫停（Paused狀態）
   - HA Manager嘗試在其他節點重啟
   - 因儲存不可用，重啟失敗

3. 恢復儲存：
   ```bash
   # 在pve01執行
   systemctl start nfs-kernel-server
   
   # HA Manager應自動恢復VM
   ```

**教訓**：
- ⚠️ **共享儲存本身也是SPOF！**
- ✅ 解決方案：使用Ceph（分散式儲存）或儲存HA

---

**測試3：VM應用程式異常（模擬軟體故障）**

1. 在VM內模擬crash：
   ```bash
   # SSH至VM
   ssh user@<VM-IP>
   
   # 觸發kernel panic（模擬系統崩潰）
   sudo sh -c "echo c > /proc/sysrq-trigger"
   ```

2. 觀察HA Manager行為：
   - 偵測到VM異常關機
   - 自動重啟VM（在同一節點或遷移至其他節點）

**預期結果**：
- ✅ VM自動重啟
- ✅ 停機時間：<1分鐘

---

### 模組4.3：SQL Server Always On實作 (2小時)
### Module 4.3: SQL Server Always On Hands-on

#### 實作環境準備

**VM配置**：

```
VM: SQL01 (Primary Replica)
- OS: Windows Server 2022 Datacenter（評估版）
- CPU: 4核心
- RAM: 8GB
- 磁碟: 60GB（C:系統）+ 100GB（D:資料庫）
- IP: 10.0.0.111

VM: SQL02 (Secondary Replica)
- 同SQL01配置
- IP: 10.0.0.112

AG Listener VIP: 10.0.0.110
```

**軟體準備**：
- Windows Server 2022 ISO
- SQL Server 2022 Developer Edition（免費）：https://www.microsoft.com/sql-server/sql-server-downloads

---

#### 步驟1：Windows Server與網域配置 (30分鐘)

**省略步驟**（實驗環境簡化）：
- 兩台伺服器使用Workgroup模式（不加入網域）
- 建立相同的本地管理員帳戶
- 設定主機名稱：SQL01、SQL02
- 配置防火牆例外（SQL、WSFC、Always On端口）

```powershell
# 在兩台伺服器執行
# 設定主機名稱
Rename-Computer -NewName "SQL01"  # 或SQL02
Restart-Computer

# 防火牆規則
New-NetFirewallRule -DisplayName "SQL Server" `
    -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow
New-NetFirewallRule -DisplayName "WSFC" `
    -Direction Inbound -Protocol TCP -LocalPort 3343 -Action Allow
New-NetFirewallRule -DisplayName "Always On" `
    -Direction Inbound -Protocol TCP -LocalPort 5022 -Action Allow
```

---

#### 步驟2：安裝Failover Clustering功能 (15分鐘)

```powershell
# 在兩台伺服器執行
Install-WindowsFeature -Name Failover-Clustering `
    -IncludeManagementTools `
    -Restart
```

**建立WSFC集群**（在SQL01）：

```powershell
# 驗證集群準備度
Test-Cluster -Node SQL01, SQL02 -Include "Inventory", "Network", "System Configuration"

# 建立集群（無共享儲存模式）
New-Cluster -Name "SQLCluster" `
    -Node SQL01, SQL02 `
    -StaticAddress 10.0.0.100 `
    -NoStorage

# 驗證
Get-ClusterNode
```

---

#### 步驟3：安裝SQL Server (30分鐘)

**在兩台伺服器執行相同安裝**：

1. 掛載SQL Server ISO，執行`setup.exe`

2. 選擇功能：
   - ✅ Database Engine Services
   - ✅ SQL Server Replication（可選）
   - ✅ Management Tools - Complete

3. 實例配置：
   - Instance: Default (MSSQLSERVER)
   - Service Accounts: 使用NT AUTHORITY\SYSTEM（簡化）

4. 資料庫引擎配置：
   - Authentication: Mixed Mode
   - SA密碼: (設定強密碼)
   - 添加當前使用者為管理員

5. **重要**：資料檔案路徑
   - 系統資料庫: C:\Program Files\Microsoft SQL Server\...
   - 使用者資料庫: D:\SQLData\（預先建立此目錄）

6. 完成安裝

---

#### 步驟4：啟用Always On功能 (10分鐘)

**在兩台伺服器執行**：

1. 開啟SQL Server Configuration Manager

2. 左側選擇`SQL Server Services`

3. 右鍵點擊`SQL Server (MSSQLSERVER)` → Properties

4. 切換至`AlwaysOn High Availability`標籤

5. ✅ 勾選`Enable AlwaysOn Availability Groups`

6. 按下OK，重啟SQL Server服務

```powershell
# PowerShell驗證
Enable-SqlAlwaysOn -ServerInstance "SQL01" -Force
Enable-SqlAlwaysOn -ServerInstance "SQL02" -Force

# 重啟服務
Restart-Service MSSQLSERVER
```

---

#### 步驟5：建立測試資料庫與AG (35分鐘)

**在SQL01執行**（使用SSMS）：

1. 建立測試資料庫：
   ```sql
   CREATE DATABASE TestDB
   ON PRIMARY (
       NAME = TestDB_Data,
       FILENAME = 'D:\SQLData\TestDB.mdf',
       SIZE = 100MB,
       FILEGROWTH = 10MB
   )
   LOG ON (
       NAME = TestDB_Log,
       FILENAME = 'D:\SQLData\TestDB_log.ldf',
       SIZE = 50MB,
       FILEGROWTH = 5MB
   );
   GO
   
   -- 插入測試數據
   USE TestDB;
   CREATE TABLE TestData (
       ID INT IDENTITY(1,1) PRIMARY KEY,
       Message NVARCHAR(100),
       CreatedDate DATETIME DEFAULT GETDATE()
   );
   
   INSERT INTO TestData (Message) 
   VALUES ('Record created before AG setup');
   GO
   ```

2. 切換至完整復原模式：
   ```sql
   ALTER DATABASE TestDB SET RECOVERY FULL;
   GO
   
   -- 完整備份（Always On必需）
   BACKUP DATABASE TestDB 
   TO DISK = 'D:\Backup\TestDB.bak';
   GO
   
   -- 交易日誌備份
   BACKUP LOG TestDB 
   TO DISK = 'D:\Backup\TestDB.trn';
   GO
   ```

3. 建立Availability Group：
   ```sql
   -- 建立Database Mirroring Endpoint
   CREATE ENDPOINT Hadr_endpoint
       STATE = STARTED
       AS TCP (LISTENER_PORT = 5022)
       FOR DATABASE_MIRRORING (
           ROLE = ALL,
           AUTHENTICATION = WINDOWS NEGOTIATE,
           ENCRYPTION = REQUIRED ALGORITHM AES
       );
   GO
   
   -- 建立AG
   CREATE AVAILABILITY GROUP [AG_Test]
   FOR DATABASE [TestDB]
   REPLICA ON 
       'SQL01' WITH (
           ENDPOINT_URL = 'TCP://SQL01:5022',
           AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
           FAILOVER_MODE = AUTOMATIC,
           BACKUP_PRIORITY = 50,
           SECONDARY_ROLE(ALLOW_CONNECTIONS = READ_ONLY)
       ),
       'SQL02' WITH (
           ENDPOINT_URL = 'TCP://SQL02:5022',
           AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
           FAILOVER_MODE = AUTOMATIC,
           BACKUP_PRIORITY = 50,
           SECONDARY_ROLE(ALLOW_CONNECTIONS = READ_ONLY)
       );
   GO
   
   -- 建立Listener
   ALTER AVAILABILITY GROUP [AG_Test]
   ADD LISTENER 'AG-Listener' (
       WITH IP ((N'10.0.0.110', N'255.255.255.0')),
       PORT = 1433
   );
   GO
   ```

---

**在SQL02執行**：

```sql
-- 還原資料庫（NORECOVERY模式）
RESTORE DATABASE TestDB 
FROM DISK = '\\SQL01\Backup\TestDB.bak'
WITH NORECOVERY,
     MOVE 'TestDB_Data' TO 'D:\SQLData\TestDB.mdf',
     MOVE 'TestDB_Log' TO 'D:\SQLData\TestDB_log.ldf';
GO

RESTORE LOG TestDB 
FROM DISK = '\\SQL01\Backup\TestDB.trn'
WITH NORECOVERY;
GO

-- 加入AG
ALTER AVAILABILITY GROUP [AG_Test] JOIN;
GO

-- 將資料庫加入AG
ALTER DATABASE TestDB SET HADR AVAILABILITY GROUP = [AG_Test];
GO
```

---

#### 步驟6：測試故障轉移 (20分鐘)

**驗證AG狀態**：

```sql
-- 在SQL01或SQL02執行
SELECT 
    ag.name AS AGName,
    ar.replica_server_name AS Replica,
    ars.role_desc AS Role,
    ar.availability_mode_desc AS SyncMode,
    ars.synchronization_health_desc AS SyncHealth
FROM sys.availability_groups ag
JOIN sys.availability_replicas ar ON ag.group_id = ar.group_id
JOIN sys.dm_hadr_availability_replica_states ars ON ar.replica_id = ars.replica_id;
GO

-- 預期輸出:
-- AGName   | Replica | Role      | SyncMode          | SyncHealth
-- AG_Test  | SQL01   | PRIMARY   | SYNCHRONOUS_COMMIT| HEALTHY
-- AG_Test  | SQL02   | SECONDARY | SYNCHRONOUS_COMMIT| HEALTHY
```

---

**測試1：手動故障轉移**

```sql
-- 在SQL02執行（切換Secondary → Primary）
ALTER AVAILABILITY GROUP [AG_Test] FAILOVER;
GO

-- 驗證角色已切換
SELECT @@SERVERNAME AS CurrentServer, 
       ar.role_desc AS Role
FROM sys.dm_hadr_availability_replica_states ars
JOIN sys.availability_replicas ar ON ars.replica_id = ar.replica_id
WHERE ar.replica_server_name = @@SERVERNAME;
GO
```

**測試2：測試應用程式連線**

```sql
-- 使用Listener連線字串:
-- Server=AG-Listener,1433;Database=TestDB;...

-- 新增測試資料
INSERT INTO TestData (Message) 
VALUES ('Record created after failover');

-- 驗證數據同步至兩個Replica
SELECT * FROM TestData;
GO
```

**測試3：模擬Primary故障（自動故障轉移）**

```powershell
# 在SQL01（當前Primary）執行
Stop-Service MSSQLSERVER -Force
```

觀察：
- ✅ AG自動偵測到Primary故障（約10秒）
- ✅ 自動提升SQL02為新Primary（約30秒）
- ✅ 應用程式連線透過Listener自動切換
- ✅ 總停機時間：<1分鐘

恢復SQL01：
```powershell
Start-Service MSSQLSERVER

# SQL01自動重新加入AG作為Secondary
```

**截圖檢查點** 📸：
- AG Dashboard截圖（SSMS → Always On High Availability → Show Dashboard）
- 故障轉移前後的角色變化

---

### 模組4.4：Day 4總結 (30分鐘)
### Module 4.4: Day 4 Summary

#### 實作成果檢視 Lab Achievements

✅ **Proxmox HA集群**：
- 3節點集群運作正常
- 共享儲存配置完成
- HA自動故障轉移驗證成功

✅ **SQL Server Always On**：
- 雙節點AG建立完成
- 同步複寫零數據損失（RPO=0）
- 自動故障轉移<1分鐘（RTO<1min）

#### 實際環境差異 Production vs Lab

| 項目 | 實驗環境 | 生產環境 |
|------|---------|---------|
| **節點數** | 3節點 | 3-5節點（建議） |
| **硬體** | 虛擬機嵌套 | 實體伺服器 |
| **網路** | 單網卡 | 雙網卡（管理+集群） |
| **儲存** | 本地磁碟/NFS | SAN / Ceph / 高階NAS |
| **電源** | 共用主機 | UPS + 雙電源供應器 |
| **網域** | Workgroup | Active Directory |
| **監控** | 手動檢查 | Zabbix/Prometheus監控 |

#### 下一步行動 Next Actions

**本公司生產環境實施**：
- [ ] 週一：向管理層簡報HA方案（使用今日成果）
- [ ] 週二：採購硬體（3台Proxmox伺服器，預算$35k）
- [ ] 週三-四：安裝與配置生產集群
- [ ] 週五：遷移第一個測試VM（非關鍵系統）
- [ ] 下週：逐步遷移Tier 2系統
- [ ] 2週後：核心業務系統HA上線

---

## 第五天：桌面演練與考核
## Day 5: Tabletop Exercise & Assessment

### 模組5.1：災難情境桌面演練 (3小時)
### Module 5.1: Disaster Scenario Tabletop Exercise

#### 演練目標 Exercise Objectives

- 驗證DR計劃可執行性
- 測試團隊協作與決策能力
- 識別計劃中的缺口
- 建立應對災難的信心

---

#### 情境A：機房火災 (60分鐘)

**情境描述**：
```
時間: 週三凌晨02:30
事件: 機房空調故障導致過熱，引發小型火災
影響: 
- 所有伺服器緊急關機
- 部分硬體燻損（初步評估20%損壞）
- 機房需48小時清理與修復
- 數據中心不可進入

當前狀態:
- 最後完整備份: 週二 23:00 (3.5小時前)
- 異地備份: 可存取
- 團隊: IT經理、系統管理員已到場
- 業務: 週三08:00須恢復核心系統（5.5小時剩餘）
```

**演練問題討論**：

1. **T+0 (02:30) - 初期評估階段**
   - 誰負責宣告災難？使用什麼標準？
   - 第一通電話打給誰？通知順序？
   - 如何快速評估損害程度？

   **團隊討論** (10分鐘)  
   **參考答案**：
   - IT經理宣告災難（依據：機房不可用>4小時）
   - 通知順序：CISO → CEO → 業務主管 → 全員
   - 評估方法：目視檢查 + 系統ping測試

---

2. **T+30分鐘 (03:00) - 決策階段**
   - 啟動DR站點？還是等待機房修復？
   - 優先恢復哪些系統？（給出Top 3）
   - 需要哪些資源？（人力、硬體、雲端）

   **團隊討論** (15分鐘)  
   **參考答案**：
   - 立即啟動DR（機房48小時無法使用）
   - 優先順序：
     1. AD域控（其他系統依賴）
     2. 核心業務系統/資料庫
     3. 郵件系統
   - 資源需求：
     - 人力：召集所有IT團隊（含外包）
     - 硬體：使用異地辦公室備援伺服器
     - 雲端：臨時租用Azure VM（加速復原）

---

3. **T+1小時 (03:30) - 執行階段**
   - 如何從異地備份還原數據？（步驟）
   - AD域控復原需多久？
   - 資料庫復原需多久？
   - 能趕上08:00業務開始嗎？

   **團隊討論** (15分鐘)  
   **白板實作**：繪製復原時間線

   **參考時間線**：
   ```
   03:30-04:00 (30min): 從雲端下載最新備份
   04:00-04:30 (30min): 還原AD域控
   04:30-06:00 (90min): 還原SQL Server資料庫
   06:00-06:30 (30min): 還原ERP應用伺服器
   06:30-07:30 (60min): 測試與驗證
   07:30-08:00 (30min): 緩衝時間
   ────────────────────────────────────
   總計: 4.5小時（可趕上08:00）✅
   ```

---

4. **T+4小時 (06:30) - 驗證階段**
   - 如何驗證系統正常？（檢查清單）
   - 發現部分數據遺失（03:00-02:30之間交易），如何處理？
   - 何時通知使用者系統已恢復？

   **團隊討論** (10分鐘)  
   **參考答案**：
   - 驗證清單：
     ✅ AD登入正常
     ✅ 資料庫可查詢與寫入
     ✅ ERP前端可存取
     ✅ 測試交易流程（下單→確認）
   - 數據遺失處理：
     - 通知業務單位：約30分鐘交易需重新輸入
     - 檢查交易日誌是否可手動補償
   - 通知時機：完成驗證後立即通知

---

5. **T+5.5小時 (08:00) - 營運階段**
   - DR站點效能是否足夠？
   - 預期DR模式運作多久？
   - 何時切回原機房？如何切回？

   **團隊討論** (10分鐘)

---

#### 情境B：勒索軟體攻擊 (60分鐘)

**情境描述**：
```
時間: 週五下午14:00
事件: 員工點擊釣魚郵件，勒索軟體感染擴散
影響:
- 檔案伺服器所有檔案已加密（.locked副檔名）
- 部分員工電腦也被加密
- 資料庫伺服器未受影響（網路隔離）
- 勒索信要求支付$50,000 Bitcoin

當前狀態:
- 檔案伺服器最後備份: 當日凌晨00:00（14小時前）
- 資料損失: 當日上午工作檔案
- 攻擊者: 威脅若不在48小時內支付，公開資料
```

**演練問題討論**：

1. **立即行動**（T+0）
   - 第一時間該做什麼？（隔離、通報、評估）
   - 是否支付贖金？決策依據？

2. **復原策略**（T+1小時）
   - 從備份還原可行嗎？
   - 如何防止二次感染？
   - 需要外部資安專家協助嗎？

3. **法律與溝通**（T+4小時）
   - 是否需要報警？
   - 是否需要通知客戶？（GDPR/個資法）
   - 如何對外說明？

**團隊討論與決策記錄** (60分鐘)

---

#### 情境C：資料庫損毀 (60分鐘)

**情境描述**：
```
時間: 週一上午10:30
事件: SQL Server資料庫突然進入"Recovery Pending"狀態
影響:
- 客戶資料庫無法存取
- ERP系統全面停擺
- 初步診斷：儲存陣列硬碟故障，數據頁損毀

當前狀態:
- 最後完整備份: 週日晚上 23:00（11.5小時前）
- 最後交易日誌備份: 當日 10:00（30分鐘前）
- RPO目標: 15分鐘（可能無法達成）
- RTO目標: 4小時
```

**演練挑戰**：
- 如何最大化還原數據？（日誌鏈還原）
- 若部分日誌損毀無法還原，如何決定還原點？
- 業務可接受多少數據損失？

**實戰模擬** (60分鐘)：  
在實驗環境實際操作還原流程。

---

### 模組5.2：知識考核 (1.5小時)
### Module 5.2: Knowledge Assessment

#### 筆試 Written Exam (60分鐘)

**考試形式**：
- 題目數：50題
- 題型：選擇題（40題）+ 簡答題（10題）
- 及格分數：70分

**範例題目**：

**選擇題**：
```
1. RTO是指？
   A. 數據損失目標
   B. 復原時間目標
   C. 備份保留期限
   D. 可用性百分比
   
正確答案: B

2. 以下哪種HA配置資源利用率最高？
   A. Active-Passive
   B. Active-Active
   C. N+1
   D. Cold Standby
   
正確答案: B

3. SQL Server Always On同步模式（SYNCHRONOUS_COMMIT）的RPO是？
   A. 0（零數據損失）
   B. 15分鐘
   C. 1小時
   D. 取決於網路延遲
   
正確答案: A
```

**簡答題**：
```
1. 解釋3-2-1備份法則，並說明為何"1"（異地）很重要？
   （限100字）

2. 列出建立Proxmox VE HA集群的5個關鍵步驟。

3. 描述一個完整的DR測試應包含哪些階段？

4. 如何計算系統可用性？請舉例說明99.9%可用性對應的年度停機時間。

5. 什麼是單點故障（SPOF）？請列舉本公司當前3個主要SPOF。
```

---

#### 實作考核 Practical Assessment (30分鐘)

**任務**：在30分鐘內完成以下操作

**Task 1** (10分鐘): Proxmox HA配置
- 在實驗集群中建立新VM
- 啟用HA保護
- 模擬故障並驗證自動恢復

**Task 2** (10分鐘): SQL Server備份與還原
- 對TestDB進行完整備份
- 修改數據（新增5筆記錄）
- 進行交易日誌備份
- 還原至時間點（剛好在新增記錄之前）

**Task 3** (10分鐘): DR計劃撰寫
- 為"郵件系統故障"撰寫簡化版DR程序
- 至少包含10個步驟
- 定義RTO/RPO

---

### 模組5.3：培訓總結與證書頒發 (30分鐘)
### Module 5.3: Training Summary & Certification

#### 5天培訓回顧 5-Day Review

**Day 1**: 業務連續性基礎
- ✅ RTO/RPO概念
- ✅ BIA業務影響分析
- ✅ ISO 27001 A17要求

**Day 2**: 高可用性架構
- ✅ 主備/雙活配置
- ✅ Proxmox VE HA
- ✅ SQL Always On

**Day 3**: 災難復原計劃
- ✅ DR計劃框架
- ✅ 異地備份策略
- ✅ 復原程序設計

**Day 4**: 實作演練
- ✅ Proxmox HA實作
- ✅ SQL Always On實作
- ✅ 故障測試驗證

**Day 5**: 桌面演練與考核
- ✅ 災難情境模擬
- ✅ 知識與技能考核

---

#### 關鍵知識總結 Key Takeaways

🎯 **業務連續性 = RTO + RPO + DR**  
🎯 **HA ≠ DR**（HA解決可用性，DR解決災難）  
🎯 **備份是最後一道防線**（3-2-1-1-0法則）  
🎯 **測試才是王道**（未測試的DR計劃 = 沒有計劃）  
🎯 **文檔與流程**（危機時無法依賴記憶）

---

#### 證書頒發 Certification

**恭喜完成「DR/BCP業務連續性專業培訓」！**

您已具備以下能力：
- ✅ 定義與計算RTO/RPO
- ✅ 進行業務影響分析（BIA）
- ✅ 設計HA架構（Proxmox VE, SQL Always On）
- ✅ 撰寫災難復原計劃
- ✅ 執行DR測試與演練
- ✅ 符合ISO 27001 A17要求

**證書編號**: DR-BCP-2026-[編號]  
**有效期限**: 2年（建議每年進行複訓）

---

## 附錄A：快速參考 Quick Reference

### RTO/RPO速查表

| 業務關鍵性 | 建議RTO | 建議RPO | 技術方案 |
|-----------|---------|---------|---------|
| 極高 | ≤1小時 | 0 | 雙活+Always On |
| 高 | ≤4小時 | ≤15分鐘 | 主備+日誌傳送 |
| 中 | ≤24小時 | ≤1小時 | 每日備份+還原 |
| 低 | ≤72小時 | ≤24小時 | 週備份 |

---

### 常用命令參考

#### Proxmox VE
```bash
# 集群狀態
pvecm status
pvecm nodes

# HA管理
ha-manager status
ha-manager set vm:100 --state started

# 儲存管理
pvesm status
pveceph status

# VM操作
qm list
qm start 100
qm migrate 100 pve02
```

#### SQL Server
```sql
-- AG狀態
SELECT * FROM sys.dm_hadr_availability_group_states;
SELECT * FROM sys.dm_hadr_database_replica_states;

-- 故障轉移
ALTER AVAILABILITY GROUP [AG_Name] FAILOVER;

-- 備份
BACKUP DATABASE [DB] TO DISK = 'path';
BACKUP LOG [DB] TO DISK = 'path';

-- 還原
RESTORE DATABASE [DB] FROM DISK = 'path' WITH NORECOVERY;
RESTORE LOG [DB] FROM DISK = 'path' WITH RECOVERY;
```

---

### ISO 27001 A17控制項檢查清單

- [ ] A17.1.1 規劃資訊安全連續性
  - [ ] BIA已完成
  - [ ] RTO/RPO已定義
  - [ ] BCP/DR計劃已文件化

- [ ] A17.1.2 實施資訊安全連續性
  - [ ] 備份機制已建立
  - [ ] HA架構已實施（關鍵系統）
  - [ ] 異地備份已配置

- [ ] A17.1.3 驗證、審查與評估
  - [ ] 年度DR演練已排程
  - [ ] 備份還原測試≥1次/月
  - [ ] 計劃每年審查更新

- [ ] A17.2.1 資訊處理設施的可用性
  - [ ] 冗餘配置（電源、網路）
  - [ ] UPS/發電機
  - [ ] 監控與告警

---

## 附錄B：推薦學習資源

### 線上課程
- **Udemy**: "Disaster Recovery Planning for IT"
- **Pluralsight**: "SQL Server Always On Availability Groups"
- **Linux Academy**: "Proxmox VE Administration"

### 書籍
- 📖 "Disaster Recovery Planning" by Jon Toigo
- 📖 "SQL Server 2022 Always On" by Microsoft Press
- 📖 "Site Reliability Engineering" by Google

### 認證
- 🎓 ISO 22301 Lead Implementer（業務連續性管理）
- 🎓 DRII CBCP（Certified Business Continuity Professional）
- 🎓 Microsoft Certified: Azure Solutions Architect

### 工具與軟體
- Proxmox VE: https://www.proxmox.com/
- Veeam Backup: https://www.veeam.com/
- SQL Server Developer: https://www.microsoft.com/sql-server/

---

## 附錄C：聯絡資訊與支援

### 培訓講師
- **主講師**: [姓名]
- **Email**: training@company.com
- **Office Hours**: 每週三 14:00-16:00

### 技術支援
- **Proxmox論壇**: https://forum.proxmox.com/
- **SQL Server社群**: https://dba.stackexchange.com/
- **本公司IT支援**: it-support@company.com

### 緊急聯絡
- **DR指揮官**: IT經理 (手機: XXX)
- **24/7 Hotline**: +886-XXX-XXX

---

## 文件更新記錄 Document History

| 版本 | 日期 | 變更內容 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-01-30 | 初版建立 | IT部門 |
| v1.1 | 待更新 | 實際培訓後修訂 | - |

---

## 合規證據產出 Compliance Evidence Output

完成本培訓後，應產出以下ISO 27001稽核證據：

1. **A17.1.1 證據**:
   - ✅ BIA報告
   - ✅ RTO/RPO定義文件
   - ✅ DR計劃v1.0

2. **A17.1.2 證據**:
   - ✅ HA架構設計圖
   - ✅ 備份配置文件
   - ✅ 復原程序SOP

3. **A17.1.3 證據**:
   - ✅ Day 5桌面演練報告
   - ✅ 培訓簽到表
   - ✅ 考核成績單

4. **記錄範本對應**:
   - [備份執行紀錄](../../記錄與證據/備份與復原/備份執行紀錄_Template.md)
   - [備份還原測試報告](../../記錄與證據/備份與復原/備份還原測試報告_Template.md)
   - [內部稽核報告](../../記錄與證據/合規與稽核/內部稽核報告_Template.md)

---

**培訓結束，祝各位學員在實際工作中成功應用所學知識，保障企業業務連續性！** 🎓✨
