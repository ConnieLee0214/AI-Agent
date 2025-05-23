# source venv/bin/activate
import os
import asyncio
import pandas as pd
from dotenv import load_dotenv
import io

# 根據你的專案結構調整下列 import
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer

load_dotenv()
# HW1 Prompt change info
async def process_chunk(chunk, start_idx, total_records, model_client, termination_condition):
    """
    處理單一批次資料：
      - 將該批次資料轉成 dict 格式
      - 組出提示，要求各代理人根據資料編號進行分析，
      - 請 MultimodalWebSurfer 代理人利用外部網站搜尋功能，
        搜尋相關新聞或網站獲取最近流行病資訊，
        並將搜尋結果納入分析中。`
      - 收集所有回覆訊息並返回。
    """
    # 將資料轉成 dict 格式
    chunk_data = chunk.to_dict(orient='records')
    prompt = (
        f"目前正在處理第 {start_idx} 至 {start_idx + len(chunk) - 1} 筆資料（共 {total_records} 筆）。\n"
        f"以下為該批次資料:\n{chunk_data}\n\n"
        "請根據以下資料進行分析，只需參考症狀、個人病史、家族病史、旅遊史，提供每位病人的可能疾病、分析依據與參考來源。請整合所有代理人的功能，生成一份完整且具參考價值的建議報告。"
        "其中請特別注意：\n"
        "  1. 針對 CSV 檔案中的每筆病人資料，請分析其症狀，並結合個人病史與家族病史，推論可能的疾病；\n"
        "  2. 請local_web_surfer使用我自己的SerpAPI 金鑰，根據病人的旅遊史，搜尋近期（近三個月內）旅遊當地相關疫情或傳染病新聞。\n"
        "   - 請明確列出實際參考的網站連結。\n"
        "   - 請摘要出重點新聞內容，說明其與症狀或疾病推論是否有關聯。\n"
        "   - 若無旅遊史，則無需搜尋，直接填寫無即可。"
        "  3. 最後，請清楚列出每位病人可能罹患的疾病，並說明判斷依據，若有參考新聞、網站連結請附上。\n"
        "請務必依照以下格式輸出**，以利後續資料解析處理：\n\n"
        "  **病人 1（編號 1）：**\n"
        "   *   **症狀：** 發燒、喉嚨痛、流鼻涕\n"
        "   *   **個人病史：** 無\n"
        "   *   **家族病史：** 高血壓\n"
        "   *   **旅遊史：** 無\n"
        "   *   **可能疾病：**\n"
        "       *   **一般感冒/流感：** 發燒、喉嚨痛、流鼻涕為典型症狀。\n"
        "   *   **分析依據：** 症狀符合一般呼吸道感染。\n"
        "   *   **旅遊史相關疫情/傳染病新聞：** 無\n"
        "   *   **參考來源：** UpToDate, Mayo Clinic\n\n"
        "請各代理人協同合作，提供一份完整且具參考價值的建議。"
    )
    
    # 為每個批次建立新的 agent 與 team 實例
    local_data_agent = AssistantAgent("data_agent", model_client)
    local_web_surfer = MultimodalWebSurfer("web_surfer", model_client)
    local_assistant = AssistantAgent("assistant", model_client)
    local_user_proxy = UserProxyAgent("user_proxy")
    local_team = RoundRobinGroupChat(
        [local_data_agent, local_web_surfer, local_assistant, local_user_proxy],
        termination_condition=termination_condition
    )
    
    messages = []
    async for event in local_team.run_stream(task=prompt):
        if isinstance(event, TextMessage):
            # 印出目前哪個 agent 正在運作，方便追蹤
            print(f"[{event.source}] => {event.content}\n")
            messages.append({
                "batch_start": start_idx,
                "batch_end": start_idx + len(chunk) - 1,
                "source": event.source,
                "content": event.content,
                "type": event.type,
                "prompt_tokens": event.models_usage.prompt_tokens if event.models_usage else None,
                "completion_tokens": event.models_usage.completion_tokens if event.models_usage else None
            })
    return messages

async def main():
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("請檢查 .env 檔案中的 GEMINI_API_KEY。")
        return

    # 初始化模型用戶端 (此處示範使用 gemini-2.0-flash)
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=gemini_api_key,
    )
    
    termination_condition = TextMentionTermination("exit")
    
    # HW1 Data set info
    chunk_size = 1000
    df = pd.read_excel('Patient_data.xlsx', sheet_name='Sheet1')
    chunks = [df[i:i + chunk_size] for i in range(0, df.shape[0], chunk_size)]
    total_records = sum(chunk.shape[0] for chunk in chunks)
    
    # 利用 map 與 asyncio.gather 同時處理所有批次（避免使用傳統 for 迴圈）
    tasks = list(map(
        lambda idx_chunk: process_chunk(
            idx_chunk[1],
            idx_chunk[0] * chunk_size,
            total_records,
            model_client,
            termination_condition
        ),
        enumerate(chunks)
    ))
    
    results = await asyncio.gather(*tasks)
    # 將所有批次的訊息平坦化成一個清單
    all_messages = [msg for batch in results for msg in batch]
    
    # 將對話紀錄整理成 DataFrame 並存成 CSV
    df_log = pd.DataFrame(all_messages)
    print(df_log)
    # 找出哪一列的 Source 是 data_agent
    final_report = df_log[df_log['source'] == 'data_agent']['content']
    print(final_report)
    final_report.to_csv('final_report.csv', index=False, header=True)

    # # 存檔
    # content_data.to_csv('data_agent_content.csv', index=False)

    
    # output_file = "AI_medical_all_conversation_log0419.csv"
    # df_log.to_csv(output_file, index=False, encoding="utf-8-sig")
    # print(f"已將所有對話紀錄輸出為 {output_file}")

if __name__ == '__main__':
    asyncio.run(main())