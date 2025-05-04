import asyncio
import os
import pandas as pd
from all_agents import auto_diaginosis, auto_recommendation
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination


async def run_agent_diaginosis(df):
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("缺少 GEMINI_API_KEY")

    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=gemini_api_key,
    )
    # termination_condition = TextMentionTermination("exit")

    messages = await auto_diaginosis(df, model_client)
    df_log = pd.DataFrame(messages)
    return df_log

async def run_agent_recommendation(df):
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("缺少 GEMINI_API_KEY")

    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=gemini_api_key,
    )
    # termination_condition = TextMentionTermination("exit")

    messages = await auto_recommendation(df, model_client)
    df_log = pd.DataFrame(messages)
    return df_log

