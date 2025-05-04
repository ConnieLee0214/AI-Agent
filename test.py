import pandas as pd
import chardet
import os
import re
import json

df= pd.read_csv("final_report_0426.csv")
report = df['content']
text = report.iloc[0]

# 正規表達式分段取出每位病人的資料
# patient_blocks = re.findall(r"\*\*病人 (\d+).*?：\*\*\n(.*?)(?=\n\*\*病人|\Z)", text, re.DOTALL)
patient_blocks = re.findall(
    r"\*\*病人\s*(\d+)[^：]*：\*\*\n(.*?)(?=\n\*\*病人|\n\*\*注意事項|\n\*\*總結|\Z)",
    text,
    re.DOTALL
)
def search(pattern, text_block):
    match = re.search(pattern, text_block, re.DOTALL)
    return match.group(1).strip() if match else None

def clean_text(block):
    # ✨ 把每個病人的內文中的行首 * 刪掉
    return re.sub(r"^\s*\*\s*", "", block, flags=re.MULTILINE)

def parse_patient(patient_id, block):
    block = clean_text(block)
    disease = search(r"\*\*可能疾病：\*\*\s*(.*?)\n\s*\*", block)
    rationale = search(r"\*\*分析依據：\*\*\s*(.*?)\n\s*\*", block)
    travel = search(r"\*\*旅遊史：\*\*\s*(.*?)\n\s*\*", block)
    # ref = search(r"\*\*參考來源：\*\*\s*(.*?)($|\n)", block)

    epi_news_block = search(r"\*\*旅遊史相關疫情/傳染病新聞：\*\*(.*?)(?=\n\s*\*\*參考來源|\Z)", block)
    
    if epi_news_block:
        epi_news_block = epi_news_block.strip()
    else:
        epi_news_block = "無"

    return {
        "病人編號": int(patient_id),
        "可能疾病": disease,
        "分析依據": rationale,
        "旅遊史": travel,
        "旅遊史相關疫情新聞": epi_news_block
    }


records = [parse_patient(pid, block) for pid, block in patient_blocks]
new_df = pd.DataFrame(records)

def clean_stars(text):
    if isinstance(text, str):
        text = text.replace("**", "")
        text = text.replace("*", "")
        return text.strip()
    return text

# 對整個 DataFrame（除了 '病人編號' 這個欄位）做清理
for col in new_df.columns:
    if col != "病人編號":
        new_df[col] = new_df[col].apply(clean_stars)


location_df = pd.read_csv('location_results.csv')
recommendation_df = pd.read_csv('recommendation.csv')
final_df = pd.concat([new_df, recommendation_df['嚴重程度評估'], recommendation_df['是否需立即就醫'], recommendation_df['看診科別建議/藥品購買建議'], 
                      location_df['診所'], location_df['醫院']], axis=1)
final_df.to_csv('final_result2.csv', index=False)

print(final_df)

# df= pd.read_csv("medication_recommendation.csv")
# content = df['content'].iloc[0].strip()  # 去除前後空白字符

# # 查找 "建議報告" 是否出現
# start = content.find("**建議報告**")
# print(f"找到 '**建議報告**' 的位置：{start}")

# if start != -1:
#     print("找到了 '**建議報告**'，正在提取內容...")
#     # 提取建議報告區塊
#     end = content.find("**注意事項：**")
#     if end != -1:
#         report_content = content[start + len("**建議報告**"): end].strip()
#         print("成功提取建議報告部分：")
#         # print(report_content)
#     else:
#         print("未找到 '注意事項' 部分。")
# else:
#     print("未能找到 '**建議報告**' 區塊。")
# lines = report_content.split('\n')
# # 創建一個清單來存儲資料
# data = []

# # 遍歷每一行，從第二行開始處理（跳過表頭）
# for line in lines[2:]:
#     # 分割欄位
#     columns = line.split('|')
#     # print(columns)
#     # 去除多餘的空格
#     patient_data = {
#         '病人編號': columns[1].strip(),
#         '可能疾病': columns[2].strip(),
#         '嚴重程度評估': columns[3].strip(),
#         '是否需立即就醫': columns[4].strip(),
#         '看診科別建議/藥品購買建議': columns[5].strip()
#     }
    
#     data.append(patient_data)

# # 轉換成 DataFrame
# df_report = pd.DataFrame(data)
# print(df_report)
# df_report.to_csv('recommendation.csv', index=False)