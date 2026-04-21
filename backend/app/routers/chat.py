import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

router = APIRouter()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# --- 開発用（モデル性能検証向け）---
# 旅行以外の一般的な質問にも回答する
SYSTEM_PROMPT = """あなたは旅行アシスタントAIです。
旅行に関する質問を中心に、日本語で親切・丁寧に答えてください。
旅行以外の一般的な質問にも対応できます。"""

# --- 本番用 ---
# 旅行以外の質問には丁寧に断る（本番切替時は上のSYSTEM_PROMPTをコメントアウトし、こちらを有効化）
# SYSTEM_PROMPT = """あなたは旅行アシスタントAIです。
# 旅行に関する質問に、親切・丁寧・簡潔に日本語で答えてください。
# 旅行先の観光スポット、グルメ、交通手段、宿泊先などについてアドバイスができます。
# 旅行と関係のない質問には「旅行に関するご質問をお待ちしています」と返してください。"""


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        llm = ChatOllama(
            model="qwen2.5:3b",
            base_url=OLLAMA_BASE_URL,
        )
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=request.message),
        ]
        result = await llm.ainvoke(messages)
        return ChatResponse(response=result.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
