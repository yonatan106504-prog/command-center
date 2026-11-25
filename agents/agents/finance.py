import os
import json
import time
from datetime import datetime
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
TASK = os.environ.get("AGENT_TASK", "").strip()
OUTPUT_FILE = "data/results.json"

SYSTEM_PROMPT = """
אתה אנליסט פיננסי ומאקרו-כלכלי. ענה בעברית מדויקת ותכליתית.
התמקד בנתונים, תמחור (P/E, תשואות, מגמות מאקרו), סיכונים ונקודות החלטה מעשיות. הימנע מהמלצות גנריות.
"""

def run_agent(task: str) -> str:
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=task,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,
                ),
            )
            return response.text
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                time.sleep(3)
                continue
            raise e

if __name__ == "__main__":
    if not TASK:
        raise ValueError("לא הוזנה משימה.")

    answer = run_agent(TASK)
    os.makedirs("data", exist_ok=True)

    records = []
    if os.path.isfile(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                records = json.load(f)
            except Exception:
                records = []

    records.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "agent": "finance",
        "agent_label": "פיננסים ושוק ההון",
        "task": TASK,
        "output": answer
    })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
