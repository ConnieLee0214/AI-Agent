from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer

async def auto_diaginosis(df, model_client):
    # 將資料轉成 dict 格式
    patient_data = df.to_dict(orient='records')[0]
    prompt = (
        f"以下為該病人資料:\n{patient_data}\n\n"
        "請根據提供的症狀、個人病史、家族病史與旅遊史，為每位病人提供：\n"
        "  1. 針對病人提供的資料，分析其症狀，並結合個人病史與家族病史，推論可能的疾病；\n"
        "  2. 若有旅遊史，請 local_web_surfer 搜尋近三個月該地區的疫情或傳染病新聞，並提供：\n"
        "   - 疫情新聞重點摘要\n"
        "   - 是否與症狀或疾病有關聯\n"
        "   - 參考網站連結（實際網址）\n"
        "   - 若無旅遊史，請填寫「無」\n"
        "請務必依照以下格式輸出**，以利後續資料解析處理：\n\n"
        "  **病人姓名：**\n"
        "   *   **症狀：\n"
        "   *   **個人病史：** \n"
        "   *   **家族病史：** \n"
        "   *   **旅遊史：** \n"
        "   *   **可能疾病：**\n"
        "   *   **疾病名稱：** \n"
        "   *   **分析依據：** \n"
        "   *   **旅遊史相關疫情/傳染病新聞：** （若無請寫「無」）\n"
        "   *   **參考來源：** \n\n"
        "請各代理人協同合作，最後請提供一份完整且具參考價值的建議（務必使用繁體中文）。\n"

    )
    
    # 為每個批次建立新的 agent 與 team 實例
    local_data_agent = AssistantAgent("data_agent", model_client)
    local_web_surfer = MultimodalWebSurfer("web_surfer", model_client)
    local_assistant = AssistantAgent("assistant", model_client)
    local_user_proxy = UserProxyAgent("user_proxy")
    local_team = RoundRobinGroupChat(
        [local_data_agent, local_web_surfer, local_assistant, local_user_proxy],
        # termination_condition=termination_condition
        termination_condition=None
    )
    
    messages = []
    async for event in local_team.run_stream(task=prompt):
        if isinstance(event, TextMessage):
            # 印出目前哪個 agent 正在運作，方便追蹤
            print(f"[{event.source}] => {event.content}\n")
            messages.append({
                "source": event.source,
                "content": event.content,
                "type": event.type,
                "prompt_tokens": event.models_usage.prompt_tokens if event.models_usage else None,
                "completion_tokens": event.models_usage.completion_tokens if event.models_usage else None
            })
        if (
                "TERMINATE" in event.content
            ):
                print("✅ 偵測到關鍵詞，自動結束")
                break
    return messages

async def auto_recommendation(df, model_client):
    patient_result = df.to_dict(orient='records')[0]
    prompt = (
        f"以下為該病人可能疾病:\n{patient_result}\n\n"
        "請根據病人的可能疾病、判斷嚴重程度，如需就醫請提供看診科別建議，若暫時不需要就醫，請提供藥品購買建議。\n"
        "其中請特別注意：\n"
        "請提供以下欄位並依照以下格式輸出：\n"
        "  **嚴重程度評估：**\n"
        "  **是否需立即就醫：**\n"
        "  **看診科別建議/藥品購買建議：**\n"
        "請各代理人協同合作，提供一份完整且具參考價值的建議。"
    )
    local_data_agent = AssistantAgent("data_agent", model_client)
    # local_assistant = AssistantAgent("assistant", model_client)
    # local_user_proxy = UserProxyAgent("user_proxy")
    local_team = RoundRobinGroupChat(
        [local_data_agent],
        # termination_condition=termination_condition
        termination_condition=None
    )
    
    messages = []
    async for event in local_team.run_stream(task=prompt):
        if isinstance(event, TextMessage):
            # 印出目前哪個 agent 正在運作，方便追蹤
            print(f"[{event.source}] => {event.content}\n")
            messages.append({
                "source": event.source,
                "content": event.content,
                "type": event.type,
                "prompt_tokens": event.models_usage.prompt_tokens if event.models_usage else None,
                "completion_tokens": event.models_usage.completion_tokens if event.models_usage else None
            })
        if (
                "TERMINATE" in event.content
            ):
                print("✅ 偵測到關鍵詞，自動結束")
                break

    return messages