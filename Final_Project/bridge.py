import pandas as pd
# import chardet
import os
import re
import json

# patient_df = pd.read_csv('AI_分析報告 (2).csv')
# first_result = patient_df[patient_df["source"] == "assistant"]['content']
# first_result = patient_df['content']
def first_result_process(first_result):
    text = first_result.iloc[0]
    print('!!!', text)
    if 'json' not in text:
        def extract_field(pattern, text, default=""):
            match = re.search(pattern, text)
            return match.group(1).strip() if match else default

        # 抽取多行內容（如疫情摘要、參考來源）
        def extract_list(start_pattern, text):
            block = re.search(start_pattern + r"(.*?)\n\s*\*", text, re.DOTALL)
            if not block:
                block = re.search(start_pattern + r"(.*)", text, re.DOTALL)
            if block:
                return [line.strip("* ").strip() for line in block.group(1).splitlines() if line.strip().startswith("*")]
            return []

        def extract_list_section(start_marker, end_marker, text):
            pattern = re.escape(start_marker) + r"(.*?)(?=" + re.escape(end_marker) + r"|\Z)"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                lines = match.group(1).splitlines()
                return [line.strip("* ").strip() for line in lines if line.strip().startswith("*")]
            return []
        
        patient_row = {
        "病人姓名": extract_field(r"\*\*病人姓名：(.+?)\*\*", text),
        "症狀": extract_field(r"\*\*症狀：\*\* (.+)", text),
        "個人病史": extract_field(r"\*\*個人病史：\*\* (.+)", text),
        "家族病史": extract_field(r"\*\*家族病史：\*\* (.+)", text),
        "旅遊史": extract_field(r"\*\*旅遊史：\*\* (.+)", text),
        "可能疾病名稱": extract_field(r"\*\*疾病名稱：\*\* (.+)", text),
        "可能疾病分析依據": extract_field(r"\*\*分析依據：\*\* (.+)", text),
        "疫情新聞摘要": "\n".join(extract_list_section("**疫情新聞重點摘要：**", "**是否與症狀或疾病有關聯：**", text)),
        "旅遊史影響": extract_field(r"\*\*是否與症狀或疾病有關聯：\*\* (.+)", text),
        "參考來源": "\n".join(extract_list_section("**參考來源：**", "TERMINATE", text))
        }
        organized_df = pd.DataFrame([patient_row])
        
        return organized_df
    else:
        print('有json')
        def extract_json_block(text):
            match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                return match.group(1)
            return None

        def clean_json_string(json_str):
            # 清除 key 前後的 *、空格和全形標點
            json_str = re.sub(r'"\*+\s*\*?\*?\s*(.*?)\s*：\s*\**\**\*?"', r'"\1"', json_str)
            json_str = re.sub(r'"(.*?)："', r'"\1"', json_str)  # 移除中文冒號
            return json_str
            
        json_str = extract_json_block(text)
        if not json_str:
            raise ValueError("❌ 找不到 JSON 區塊")
        
        cleaned_str = clean_json_string(json_str)

        try:
            data = json.loads(cleaned_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ JSON 格式錯誤：{e}")

        # 兼容 dict 或 list 格式的疫情新聞
        if "旅遊史相關疫情/傳染病新聞" in data.keys():
            epidemic_news_raw = data.get("旅遊史相關疫情/傳染病新聞", {})
        else:
            epidemic_news_raw = data.get("可能疾病", {}).get("旅遊史相關疫情/傳染病新聞", [])
        if isinstance(epidemic_news_raw, list) and epidemic_news_raw:
            first_news = epidemic_news_raw[0]
        elif isinstance(epidemic_news_raw, dict):
            first_news = epidemic_news_raw
        else:
            first_news = {}

            # 組成資料列
        patient_row = {
            "病人姓名": data.get("病人姓名", ""),
            "症狀": data.get("症狀", ""),
            "個人病史": data.get("個人病史", ""),
            "家族病史": data.get("家族病史", ""),
            "旅遊史": data.get("旅遊史", ""),
            "可能疾病名稱": data.get("可能疾病", {}).get("疾病名稱", ""),
            "可能疾病分析依據": data.get("可能疾病", {}).get("分析依據", ""),
            "疫情新聞摘要": first_news.get("疫情新聞重點摘要", ""),
            "是否與症狀有關聯": first_news.get("是否與症狀或疾病有關聯", ""),
            "參考來源": first_news.get("參考來源", "")
        }

        return pd.DataFrame([patient_row])
    
def extract_recommendation_fields(second_result):
    text = second_result.iloc[0]
    # 嚴重程度評估
    # severity = re.search(r"\*\*嚴重程度評估：\*\*\n\n(.+?)\n\n\*\*", text, re.DOTALL)
    severity = re.search(r"\*\*嚴重程度評估：\*\*\s*(.+?)\s*\*\*", text, re.DOTALL)
    severity_text = severity.group(1).strip() if severity else ""

    # 是否需立即就醫
    # need_visit = re.search(r"\*\*是否需立即就醫：\*\*\n\n(.+?)\n\n\*\*", text, re.DOTALL)
    need_visit = re.search(r"\*\*是否需立即就醫：\*\*\s*(.+?)\s*\*\*", text, re.DOTALL)
    need_visit_text = need_visit.group(1).strip() if need_visit else ""

    # 看診科別建議/藥品購買建議
    # dept_med = re.search(r"\*\*看診科別建議/藥品購買建議：\*\*\n\n(.+?)\n\n\*\*", text, re.DOTALL)
    # dept_med = re.search(r"\*\*看診科別建議/藥品購買建議：\*\*\s*(.+)", text, re.DOTALL)
    dept_med = re.search(r"\*\*看診科別建議.*?(?=TERMINATE)", text, re.DOTALL)
    dept_med_text = dept_med.group(1).strip() if dept_med else ""

    return pd.DataFrame([{
        "嚴重程度評估": severity_text,
        "是否需立即就醫": need_visit_text,
        "看診科別建議/藥品購買建議": dept_med_text
    }])