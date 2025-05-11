import streamlit as st
import pandas as pd
import asyncio
import os
# from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from bridge import first_result_process, extract_recommendation_fields
from agent_runner import run_agent_diaginosis, run_agent_recommendation
from playwright_application import search_medication_location
from pdf_generation import create_pdf

# import subprocess
# subprocess.run(["playwright", "install"])

# 載入 .env 檔的環境變數（如 API 金鑰）
# load_dotenv()
gemini_api_key = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title="AI 醫療智能診斷系統", layout="centered")
st.title("🤖 AI 醫療智能診斷系統")

# --- 使用者選擇輸入模式 ---
# mode = st.radio("請選擇資料來源：", ["📤 上傳 Excel", "📝 手動輸入"], horizontal=True)
st.subheader("📝 請輸入下列資料:")

user_df = None

# --- 模式一：上傳 Excel 檔案 ---
# if mode == "📤 上傳 Excel":
#     uploaded_file = st.file_uploader("上傳病人資料（支援 xlsx）", type=["xlsx"])
#     if uploaded_file:
#         try:
#             user_df = pd.read_excel(uploaded_file)
#             st.success("成功讀取資料！以下是上傳的內容：")
#             st.dataframe(user_df)
#         except Exception as e:
#             st.error(f"讀取檔案錯誤：{e}")

# --- 模式二：手動輸入表單 ---
# if mode == "📝 手動輸入":
with st.form("user_input_form"):
    name = st.text_input("病人姓名")
    symptoms = st.text_area("症狀（用逗號分隔）", placeholder="例如：發燒, 咳嗽, 喉嚨痛")
    personal_history = st.text_area("個人病史", placeholder="例如：糖尿病、高血壓")
    family_history = st.text_area("家族病史", placeholder="例如：心臟病")
    travel_history = st.text_area("旅遊史", placeholder="例如：最近去過日本")
    address = st.text_area("地址", placeholder="請輸入您的所在地之地址")

    submitted = st.form_submit_button("提交資料")
    if submitted:
        user_df = pd.DataFrame([{
            "姓名": name,
            "症狀": symptoms,
            "個人病史": personal_history,
            "家族病史": family_history,
            "旅遊史": travel_history,
            "地址": address
        }])
        st.session_state["user_df"] = user_df
        st.success("資料已建立！")

        st.dataframe(user_df)

# --- 按鈕觸發 AI 分析 ---
if "user_df" in st.session_state and not st.session_state["user_df"].empty:
    
    if st.button("🚀 開始 AI 分析"):
        with st.spinner("AI 分析中，請稍候..."):
            # loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(loop)
            user_df = st.session_state["user_df"]
            # diaginosis_log = loop.run_until_complete(run_agent_diaginosis(user_df))
            diaginosis_log = asyncio.run(run_agent_diaginosis(user_df))
            assistant_rows = diaginosis_log[diaginosis_log["source"] == "assistant"]
            mask = assistant_rows["content"].str.contains("病人姓名", na=False) & assistant_rows["content"].str.contains("可能疾病", na=False)

            if not assistant_rows.empty and mask.any():
                diaginosis_result = assistant_rows["content"]
                print('Data from assistant')
            else:
                diaginosis_result = diaginosis_log.loc[diaginosis_log["source"] == "data_agent", "content"]
            diaginosis_df = first_result_process(diaginosis_result)
            # second_log = loop.run_until_complete(run_agent_recommendation(diaginosis_df))
            second_log = asyncio.run(run_agent_recommendation(diaginosis_df))

            if 'assistant' in second_log["source"].values:
                recommend_result = second_log.loc[diaginosis_log["source"] == "assistant", "content"]
            else:
                recommend_result = second_log.loc[diaginosis_log["source"] == "data_agent", "content"]
            recommend_df = extract_recommendation_fields(recommend_result)

            patient_location = user_df["地址"]
            location_results = search_medication_location(patient_location)
            final_result = pd.concat([diaginosis_df, recommend_df, location_results], axis=1)


        st.success("✅ 分析完成！以下為 AI 診斷結果與建議：")
        st.dataframe(final_result)
        pdf_output = create_pdf(final_result)
        # 下載結果
        st.download_button(
            label="💾 下載分析結果 PDF",
            # data=final_result.to_csv(index=False),
            data = pdf_output,
            file_name="AI_分析報告.pdf",
            mime="application/pdf"
        )
        st.stop()
        # os._exit(0)

# 台北市大安區敦化南路二段218號
# 發燒, 咳嗽, 喉嚨痛