import json
import re
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

EXTRACTION_SYSTEM_PROMPT = """あなたは旅行情報を抽出するAIです。
ユーザーのメッセージから旅行に関する情報を抽出し、JSON配列のみで返してください。

抽出するカテゴリ:
- destination: 旅行先（都市・観光地・国）
- accommodation: 宿泊施設（ホテル・旅館など）
- transportation: 交通手段（飛行機・新幹線など）
- food: グルメ・食事（レストラン・料理名など）
- experience: 体験・アクティビティ（観光・レジャーなど）
- schedule: 日程・時期・期間
- budget: 予算・費用
- tip: 旅行のコツ・アドバイス・情報

旅行情報が含まれない場合は [] を返してください。
説明文は不要です。JSON配列のみを返してください。

返答形式:
[
  {"category": "destination", "data": {"name": "京都", "type": "city"}, "confidence": 0.9}
]"""


def extract_travel_data(message: str, ollama_base_url: str) -> list[dict]:
    try:
        llm = ChatOllama(model="qwen2.5:3b", base_url=ollama_base_url, temperature=0)
        result = llm.invoke([
            SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=message),
        ])

        content = result.content.strip()
        json_match = re.search(r"\[.*\]", content, re.DOTALL)
        if not json_match:
            return []

        items = json.loads(json_match.group())
        validated = []
        for item in items:
            if isinstance(item, dict) and "category" in item and "data" in item:
                validated.append({
                    "category": str(item["category"]),
                    "data": item["data"] if isinstance(item["data"], dict) else {},
                    "confidence": float(item.get("confidence", 1.0)),
                })
        return validated
    except Exception:
        return []
