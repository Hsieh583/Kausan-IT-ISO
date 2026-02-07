# 🤖 AI-Ops-Context | IT 數位孿生與 AI 推理中樞

本目錄為 **Kausan-IT-ISO** 專案的「大腦層」，旨在將靜態的 ISO 27001 合規紀錄轉化為動態的 AI 診斷語境。透過結合自動化腳本與 LLM（如 Gemini/GPT），實現從「救火式維運」轉向「預測式分析」。

---

## 📌 核心使命 (Core Mission)

1. **語境整合**：融合 `/01-資產管理` 與 `/03-維運管理` 的數據，為 AI 提供完整的 IT 環境地圖。
2. **邏輯推理**：將 IT 主管的診斷經驗轉化為結構化 Prompt 與工作流。
3. **即時反應**：透過自動化管線，縮短從「發現異常」到「產出診斷建議」的時間。

---

## 🗺️ 環境地圖 (Environment Context)

### 1. 物理與邏輯依賴 (Dependency Graph)

> [!TIP]
> 此部分用於幫助 AI 理解「牽一髮而動全身」的關聯。

* **核心資料庫 (SQL Server)**:
  * 依賴者：MWS 系統、影資系統、ERP。
  * 存儲位置：ILC 據點 Server Rack A。

* **跨據點網路 (SD-WAN/VPN)**:
  * 總部 <-> ILC/Kausan/據點 X。
  * 關鍵節點：Fortigate 60F (VLAN 10/20)。

### 2. 資料收集管線 (Data Pipelines)

目前已實作的自動化紀錄獲取路徑：

* **[腳本路徑]** -> **[對應紀錄]** -> **[ISO 條款]**
  * `scripts/get-exchange-log.ps1` -> 郵件流異常紀錄 -> 12.4 紀錄日誌。
  * `scripts/check-disk-space.py` -> 儲存容量預警 -> 12.1 作業程序。

---

## 🧠 AI 診斷工作流 (AI-Ops Workflows)

當異常發生時，AI 應遵循以下推理路徑：

1. **偵測層 (Detection)**: 接收來自 Zabbix Webhook 或人工輸入的錯誤代碼。
2. **檢索層 (Retrieval)**:
   * 查詢 `../01-資產管理` 確認受影響設備規格。
   * 查詢 `../03-維運管理` 比對過去 24 小時是否有變更紀錄。

3. **分析層 (Analysis)**: 結合此目錄下的 `Troubleshooting_Logic.md` 進行因果分析。
4. **輸出層 (Action)**: 產出包含「故障原因」、「SOP 對應步驟」與「給維運廠商的指令」之報告。

---

## 🛠️ 目錄結構說明

```text
/AI-Ops-Context
│
├── README.md               # 本文件（AI 的總綱手冊）
├── Knowledge_Graph.md       # 描述設備與服務的關聯（Mermaid 語法）
├── Troubleshooting_Logic.md  # IT 主管的診斷邏輯（If-Then 結構）
├── /Automation/             # 存放銜接 Dify/API 的中間件腳本
└── /Prompts/                # 針對不同情境（郵件、網路、SQL）的優化 Prompt
```

---

## 📖 專家觀點評論 (Expert Review)

> **AI 運作原則**：
> 「這份 README 是 AI 進入本專案的 **System Prompt**。它將原本支離破碎的紀錄，編織成一張有意義的網。當 AI 知道它身處於一個『遵循 ISO 27001 的五據點物流 IT 環境』時，它所給出的任何建議都會具備高度的環境覺察力。」

---

---

## 🚀 IT 主管儀表板 (Streamlit Dashboard)

### 安裝與執行

1. **安裝依賴套件**：
   ```bash
   cd AI-Ops-Context
   pip install -r requirements.txt
   ```

2. **配置環境變數** (可選)：
   ```bash
   cp .env.example .env
   # 編輯 .env 文件，填入你的 API Keys
   ```

3. **啟動儀表板**：
   ```bash
   streamlit run app.py
   ```

4. **訪問儀表板**：
   打開瀏覽器訪問 `http://localhost:8501`

### 功能特性

* **📊 實時狀態監控**：側邊欄顯示各據點的實時狀態（未來對接 Zabbix API）
* **📋 ISO 紀錄整合**：橫向讀取 `ISO27001_文檔體系` 中的資產管理與備份日誌
* **🤖 AI 診斷助手**：聊天室介面，支持自動上下文注入（未來對接 Gemini/Dify API）
* **🔍 資產依賴圖**：視覺化顯示關鍵資產之間的依賴關係
* **⚡ 快速行動按鈕**：一鍵執行 Exchange Log 抓取、生成報告等操作

### 目錄結構

```text
/AI-Ops-Context
├── app.py                 # Streamlit 主程式
├── requirements.txt       # Python 依賴套件
├── .env.example          # 環境變數範例
└── README.md             # 本文件
```

---

## 💡 下一步行動 (Next Steps)

* [x] **建立 Streamlit 儀表板**：實現基礎功能框架。
* [ ] **初始化 `Knowledge_Graph.md`**：使用 Mermaid 語法繪製核心 SQL 與各據點工作站的連線邏輯。
* [ ] **封裝第一條管線**：將你目前最常用的「郵件 Log 查詢腳本」輸出格式標準化。
* [ ] **對接 Zabbix API**：實現真實的據點狀態監控。
* [ ] **整合 AI API**：連接 Gemini 或 Dify 實現智能診斷。
