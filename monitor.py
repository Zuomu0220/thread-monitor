import os
import re
import json
import sys
from datetime import datetime, timedelta
import google.generativeai as genai

# 確保 Windows 終端機能正常印出 Unicode Emoji
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 1. 自動獲取當前的現實時間
today = datetime.now()
six_days_ago = today - timedelta(days=6)

today_str = today.strftime("%Y/%m/%d")
cutoff_str = six_days_ago.strftime("%Y/%m/%d")

print(f"🔄 正在執行 Thread 炎上留言觀測站更新...")
print(f"🕒 當前現實時間：{today_str} (將自動刪除 {cutoff_str} 之前的舊內容)")

# 2. 檢查 API Key 狀態
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ 錯誤：找不到環境變數 GEMINI_API_KEY，請先在終端機設定。")
    exit(1)

genai.configure(api_key=api_key)

# 3. 智慧動態時間指令
system_instruction = f"""
You are a professional social media trend observer.
Today's real-world date is {today_str}.
Your task is to extract ongoing "flame wars" or controversial topics from the user's input into "### 🎮 實況主區" or "### 🔮 VTuber 區".

CRITICAL TIME RULES:
- You ONLY accept and format events that happened between {cutoff_str} and {today_str}.
- Any events older than 7 days (before {cutoff_str}) MUST be completely ignored and deleted from the output.
- Format each entry EXACTLY like this: * **[MM/DD]** [Event Brief]: Summary.
- If there is a relevant official image URL, insert <img class="event-image" src="URL"> right below the text item.
- Return ONLY the raw markdown content list. No introductory or concluding remarks.
"""

# 4. 讀取 raw_threads.txt 的留言內容
txt_path = "C:/Users/User/.gemini/antigravity/scratch/threads_monitor/raw_threads.txt"
html_path = "C:/Users/User/.gemini/antigravity/scratch/threads_monitor/index.html"
db_path = "C:/Users/User/.gemini/antigravity/scratch/threads_monitor/events.json"

# 確保檔案與資料夾存在
os.makedirs(os.path.dirname(txt_path), exist_ok=True)
if not os.path.exists(txt_path):
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("請在此處貼上最新的 Threads 留言內容...")

with open(txt_path, "r", encoding="utf-8") as f:
    raw_content = f.read().strip()

# 載入歷史資料庫
existing_events = []
if os.path.exists(db_path):
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            existing_events = json.load(f)
    except Exception as e:
        print(f"⚠️ 載入資料庫失敗：{e}，將初始化新資料庫。")

new_extracted_events = []

# 5. 呼叫 Gemini 1.5 Flash 進行整理與時間過濾
if raw_content and raw_content != "請在此處貼上最新的 Threads 留言內容...":
    print("🤖 正在連線 Gemini 進行即時輿情整理與篩選...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
        response = model.generate_content(f"Here is the newly fetched data:\n{raw_content}")
        ai_output = response.text
        
        # 解析 Gemini 輸出的 Markdown 格式並結構化儲存
        current_category = None
        lines = ai_output.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # 辨識分類
            if "實況主" in line or "STREAMER" in line or "🎮" in line:
                current_category = "STREAMER"
                i += 1
                continue
            elif "VTuber" in line or "vtuber" in line or "🔮" in line:
                current_category = "VTUBER"
                i += 1
                continue
                
            # 匹配清單項目： * **[MM/DD]** [事件簡述]：內容
            match = re.match(r'^\*\s*\*\*\[(\d{1,2})/(\d{1,2})\]\*\*\s*\[(.*?)\]：(.*)', line)
            if match and current_category:
                month = int(match.group(1))
                day = int(match.group(2))
                title = match.group(3).strip()
                summary = match.group(4).strip()
                
                # 計算年份並轉換為標準 %Y/%m/%d 格式
                date_str = f"{today.year}/{month:02d}/{day:02d}"
                if today.month == 1 and month == 12:
                    date_str = f"{today.year - 1}/{month:02d}/{day:02d}"
                
                # 檢查下方是否有附隨圖片
                image_url = None
                next_idx = i + 1
                while next_idx < len(lines):
                    next_line = lines[next_idx].strip()
                    if not next_line:
                        next_idx += 1
                        continue
                    if next_line.startswith('*') or next_line.startswith('#'):
                        break
                    img_match = re.search(r'<img\s+[^>]*src=["\']([^"\']+)["\']', next_line)
                    if img_match:
                        image_url = img_match.group(1)
                        i = next_idx
                        break
                    next_idx += 1
                
                new_extracted_events.append({
                    "category": current_category,
                    "date": date_str,
                    "title": title,
                    "summary": summary,
                    "image_url": image_url
                })
            i += 1
        print(f"✨ 成功從新留言中擷取出 {len(new_extracted_events)} 筆事件。")
        
        # 處理完後清空 raw_threads.txt 以免重複擷取
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("")
        print("🧹 raw_threads.txt 已清空，等待下次貼入新內容。")
    except Exception as e:
        print(f"❌ 呼叫 Gemini 或解析過程出錯：{e}")
else:
    print("ℹ️ raw_threads.txt 無新內容，將直接進行時間淘汰與網頁更新...")

# 6. 合併新舊資料並進行去重 (以 category, date, title 為鍵)
all_events_map = {}
for ev in existing_events:
    key = (ev["category"], ev["date"], ev["title"])
    all_events_map[key] = ev

for ev in new_extracted_events:
    key = (ev["category"], ev["date"], ev["title"])
    all_events_map[key] = ev

# 7. 自動檢查日期，強制刪除距離今天大於 6 天的舊項目以及一年前的過期事件
active_events = []
expired_count = 0
for key, ev in all_events_map.items():
    try:
        ev_date = datetime.strptime(ev["date"], "%Y/%m/%d")
        if ev_date.year < 2026:
            expired_count += 1
            continue
        delta = (today.date() - ev_date.date()).days
        if 0 <= delta <= 6:
            active_events.append(ev)
        else:
            expired_count += 1
    except:
        continue

# 最新日期排在最前
active_events.sort(key=lambda x: x["date"], reverse=True)

# 寫入 events.json 存檔
with open(db_path, "w", encoding="utf-8") as f:
    json.dump(active_events, f, ensure_ascii=False, indent=2)
print(f"💾 資料庫更新成功！保留：{len(active_events)} 筆，自動淘汰：{expired_count} 筆。")

# 8. 拼裝符合網頁 CSS 架構的 HTML 內容
ai_output_parts = []
streamer_events = [e for e in active_events if e["category"] == "STREAMER"]
vtuber_events = [e for e in active_events if e["category"] == "VTUBER"]

if streamer_events:
    ai_output_parts.append("### 🎮 實況主區")
    ai_output_parts.append("<ul>")
    for ev in streamer_events:
        try:
            dt = datetime.strptime(ev["date"], "%Y/%m/%d")
            date_display = f"{dt.month:02d}/{dt.day:02d}"
        except:
            date_display = ev["date"]
        img_html = f'\n            <img class="event-image" src="{ev["image_url"]}">' if ev.get("image_url") else ''
        ai_output_parts.append(f'            <li><strong>{date_display}</strong> [{ev["title"]}]：{ev["summary"]}{img_html}</li>')
    ai_output_parts.append("</ul>")

if vtuber_events:
    ai_output_parts.append("### 🔮 VTuber 區")
    ai_output_parts.append("<ul>")
    for ev in vtuber_events:
        try:
            dt = datetime.strptime(ev["date"], "%Y/%m/%d")
            date_display = f"{dt.month:02d}/{dt.day:02d}"
        except:
            date_display = ev["date"]
        img_html = f'\n            <img class="event-image" src="{ev["image_url"]}">' if ev.get("image_url") else ''
        ai_output_parts.append(f'            <li><strong>{date_display}</strong> [{ev["title"]}]：{ev["summary"]}{img_html}</li>')
    ai_output_parts.append("</ul>")

if not active_events:
    formatted_ai_output = '<p style="text-align: center; color: #718096; padding: 20px 0;">📡 當前無監測中事件，舊訊息已完全自動下架清空。</p>'
else:
    formatted_ai_output = "\n".join(ai_output_parts)

# 9. 生成漂亮的深色漸層前端網頁
html_template = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 Thread 炎上留言觀測站</title>
    <style>
        :root {{
            --bg-color: #0d0e12;
            --card-bg: rgba(30, 32, 40, 0.75);
            --text-color: #e2e8f0;
            --streamer-color: #a78bfa;
            --vtuber-color: #f472b6;
            --border-color: rgba(255, 255, 255, 0.08);
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #0f111a 0%, #07080d 100%);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{ width: 100%; max-width: 800px; }}
        header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            backdrop-filter: blur(10px);
        }}
        header h1 {{ margin: 0; font-size: 2.2rem; color: #fff; letter-spacing: 1px; }}
        header p {{ color: #718096; margin: 8px 0 0 0; font-size: 0.95rem; }}
        .time-badge {{
            display: inline-block;
            margin-top: 10px;
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}
        .dashboard {{
            background: var(--card-bg);
            border-radius: 16px;
            border: 1px solid var(--border-color);
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            backdrop-filter: blur(12px);
        }}
        .dashboard h3 {{
            font-size: 1.3rem;
            margin-top: 25px;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid rgba(255,255,255,0.05);
        }}
        .dashboard h3:first-of-type {{ margin-top: 0; }}
        .dashboard ul {{ list-style: none; padding: 0; margin: 0; }}
        .dashboard li {{
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            line-height: 1.6;
        }}
        .dashboard li:last-child {{ border-bottom: none; }}
        .dashboard strong {{ color: #fff; background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 4px; margin-right: 8px; font-size: 0.9rem; }}
        .event-image {{
            display: block;
            max-width: 100%;
            max-height: 300px;
            margin-top: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
            object-fit: contain;
        }}
        .readonly-notice {{ text-align: center; font-size: 0.8rem; color: #4a5568; margin-top: 40px; letter-spacing: 2px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔥 Thread 炎上留言觀測站</h1>
            <p>即時追蹤熱門爭議與社群動態</p>
            <div class="time-badge">🕒 現實流動時間：{today_str} (滿7天自動下架)</div>
        </header>

        <div class="dashboard">
{formatted_ai_output}
        </div>

        <div class="readonly-notice">🔒 BOARD STATUS: READ-ONLY (唯讀模式)</div>
    </div>
</body>
</html>
"""

# 寫出 index.html
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print("✅ [成功] index.html 已重新生成，舊訊息淘汰完成！")
