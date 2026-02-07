import streamlit as st
import pandas as pd
import os
from pathlib import Path

# 常數定義
PREVIEW_LENGTH = 500  # 文件預覽長度

# 1. 基礎配置
st.set_page_config(page_title="Kausan IT-Ops Dashboard", layout="wide")
ROOT_DIR = Path(__file__).parent.parent  # 橫向定位到 Kausan-IT-ISO 根目錄

# 2. 側邊欄：據點狀態 (模擬連動 Zabbix)
with st.sidebar:
    st.title("🌐 據點實體狀態")
    locations = ["總部", "ILC 倉庫", "Kausan 辦公室", "據點 D", "據點 E"]
    for loc in locations:
        st.success(f"● {loc} - 正常") # 未來此處對接 Zabbix API
    
    st.divider()
    st.info("系統角色：IT 主管 (Admin)")

# 3. 中央區塊：ISO 紀錄與日誌整合
col_main, col_ai = st.columns([0.6, 0.4])

with col_main:
    st.header("📋 IT 維運實時紀錄")
    
    tab1, tab2 = st.tabs(["備份日誌", "資產概覽"])
    
    with tab1:
        # 橫向讀取 ISO27001_文檔體系/06_備份與復原記錄 下的最新 Markdown
        log_path = ROOT_DIR / "ISO27001_文檔體系" / "06_備份與復原記錄"
        st.subheader("最近備份狀態 (HPE G9/G10)")
        # 範例：讀取檔案列表並顯示
        if log_path.exists():
            files = [f.name for f in log_path.glob("*.md")]
            if files:
                selected_file = st.selectbox("選擇日誌查看", files)
                # 讀取選中的文件內容
                file_content_path = log_path / selected_file
                if file_content_path.exists():
                    with open(file_content_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # 顯示文件預覽
                    if len(content) > PREVIEW_LENGTH:
                        preview = content[:PREVIEW_LENGTH] + "..."
                    else:
                        preview = content
                    st.code(f"讀取自：{selected_file}\n\n{preview}", language="markdown")
            else:
                st.warning("未找到備份日誌文件")
        else:
            st.error("備份日誌路徑不存在")

    with tab2:
        st.subheader("關鍵資產依賴圖")
        st.graphviz_chart('''
            digraph {
                SQL_Server -> MWS_System
                SQL_Server -> Video_System
                SQL_Server -> ERP
                Core_Switch -> SQL_Server
                Fortigate_60F -> Core_Switch
            }
        ''')
        
        # 顯示資產清單
        st.subheader("IT 資產清單")
        asset_path = ROOT_DIR / "ISO27001_文檔體系" / "04_資產管理記錄"
        if asset_path.exists():
            files = [f.name for f in asset_path.glob("*.md")]
            if files:
                selected_asset = st.selectbox("選擇資產文件查看", files, key="asset_select")
                asset_file_path = asset_path / selected_asset
                if asset_file_path.exists():
                    with open(asset_file_path, 'r', encoding='utf-8') as f:
                        asset_content = f.read()
                    # 顯示文件預覽
                    if len(asset_content) > 400:
                        asset_preview = asset_content[:400] + "..."
                    else:
                        asset_preview = asset_content
                    st.code(asset_preview, language="markdown")

# 4. 右側 AI 區：診斷助手
with col_ai:
    st.header("🤖 AI 診斷中樞")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 顯示對話紀錄
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 對話輸入
    if prompt := st.chat_input("請描述 IT 異常 (如：MWS 連線錯誤)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 這裡就是「橫向視野」的展現：自動附加上下文
        context = "當前環境：ILC 據點, SQL Server 運行中, 最近備份正常。" 
        
        # 呼叫 Gemini / Dify API (示意)
        response = f"根據您的描述與 {context} 的背景，建議檢查 VLAN 20 的防火牆規則。"
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# 5. 特殊行動按鈕 (Action Buttons)
st.divider()
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("⚡ 執行 Exchange Log 抓取 (PowerShell)"):
        st.warning("正在透過系統介面抓取 joe.chung@dradvice.com 的郵件日誌...")
        # 這裡串接 subprocess 執行你的腳本

with col_btn2:
    if st.button("📊 生成月度備份報告"):
        st.info("正在生成月度備份統計報告...")
        # 未來整合數據分析

with col_btn3:
    if st.button("🔍 掃描資產變更"):
        st.info("正在掃描最近7天的資產變更紀錄...")
        # 未來整合 git log 或文件變更檢測
