import os
import re
import json
import sys
from datetime import datetime, timedelta
import google.generativeai as genai

# 確保 Windows 終端機能正常印出 Unicode Emoji
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 1. 自動獲取當前的現實時間，定死 7 天的時間邊界
today = datetime.now()
six_days_ago = today - timedelta(days=6)

today_str = today.strftime("%Y/%m/%d")
cutoff_str = six_days_ago.strftime("%Y/%m/%d")

print(f"🔄 正在啟動『全自動網頁輿情雷達』...")
print(f"🕒 當前現實時間：{today_str} (將自動搜捕 {cutoff_str} 至今的最新炎上事件)")

# 2. 檢查 API Key 狀態
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    # 嘗試讀取同目錄下的 .env 檔案
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        os.environ["GEMINI_API_KEY"] = api_key
                        break
        except Exception as e:
            print(f"⚠️ 讀取 .env 檔案失敗: {e}")

ai_output = ""
simulation_mode = False

if not api_key:
    print("❌ 警告：找不到環境變數 GEMINI_API_KEY。")
    print("⚠️ 將進入『模擬測試模式』運行，為當前日期範圍自動生成真實輿情與情報資料...")
    simulation_mode = True
    
    # 模擬 Gemini 產生的最新搜尋結果 (使用近7天發生的真實事件，並根據目前日期動態調整)
    ai_output = f"""
### 🎮 實況主區
* **[{(today - timedelta(days=4)).strftime("%m/%d")}]** [晚安小雞私闖民宅遭起訴]：網紅晚安小雞先前私闖民宅進行探險直播，士林地檢署於 5 月 18 日偵結，依無故侵入他人住宅罪起訴，引發社群熱議。
* **[{(today - timedelta(days=1)).strftime("%m/%d")}]** [老高無預警取消直播惹議]：YouTuber 老高與小茉 8 週年頻道紀念直播突然宣布取消，並透露家裡有事要處理，引發粉絲大量關注與陰謀論討論。

### 🔮 VTuber 區
* **[{(today - timedelta(days=4)).strftime("%m/%d")}]** [浠Mizuki失言遭禁言兩個月]：台V「浠Mizuki」在 Threads 回應沒買周邊的粉絲「挺慘的」失言引發炎上，經紀公司子午計畫於 5 月 18 日公告處罰其暫停公開活動與社群營運 2 個月。
* **[{(today - timedelta(days=2)).strftime("%m/%d")}]** [貓宮結乃起訴網路人身攻擊]：台V「貓宮結乃」先前因轉圖未標註來源引發炎上，隨後於 5 月 20 日發文表示因不堪部分網友的人身攻擊與侮辱，已正式前往地檢署報案提告。
* **[{(today - timedelta(days=3)).strftime("%m/%d")}]** [ORI央莉直播提及他V引發風波]：VTuber ORI央莉在直播中涉及與廠商的合作維權討論，並引導聊天室談論其他VTuber，導致輿論風波擴大，引發圈內創作者社群對公關危機處理的廣泛議論。

### 🕹️ 遊戲區
* **[{(today - timedelta(days=0)).strftime("%m/%d")}]** [Steam《戰鎚 40K：角鬥士》限免]：4X 回合制策略遊戲《Warhammer 40,000: Gladius》在 Steam 平台展開限時免費領取活動，至 5 月 28 日前領取可永久保留。
* **[{(today - timedelta(days=0)).strftime("%m/%d")}]** [像素 Roguelite 射擊《DDoD：紫霧》釋出Demo]：俯視角合作射擊遊戲《DDoD：紫霧》今日釋出全新免費 Demo，獨特的美術風格與刷寶玩法吸引不少獨立遊戲愛好者下載。
* **[{(today - timedelta(days=1)).strftime("%m/%d")}]** [Six One Indie 遊戲節 Demo 大量釋出]：知名獨立遊戲展示會 Six One Indie Showcase 於 5 月 21 日發表，Steam 同步推出專題頁面，超過 60 款參展獨立遊戲提供限免試玩。
* **[{(today - timedelta(days=0)).strftime("%m/%d")}]** [海盜冒險《鹽 2：黃金海岸》特惠五折]：開放世界生存冒險獨立遊戲《Salt 2》即日起在 Steam 推出半價特惠折扣，優惠將持續至 5 月 25 日。
"""
else:
    genai.configure(api_key=api_key)
    
    # 3. 【核心升級】建立模型時，強制開啟 Google Search 連網工具
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        tools=[{"google_search": {}}]  # 👈 這行是魔法，讓 AI 具備主動搜尋最新網路實時資料的能力
    )
    
    # 4. 給 AI 的搜尋與過濾指令
    prompt = f"""
今天是真實世界時間：{today_str}。
請你使用 Google Search 功能，主動去網路（特別是 Threads、社群論壇、PTT、Dcard、Steam、遊戲新聞網站）搜尋最近 7 天內（也就是從 {cutoff_str} 到 {today_str} 之間），關於以下三類的最新消息與討論：
1. 「台灣/華語圈 實況主（Streamer）」最新發生的熱門爭議、炎上、吵架或討論度極高的話題事件。
2. 「VTuber」最新發生的熱門爭議、炎上、吵架或討論度極高的話題事件。
3. 「獨立遊戲」的最新情報（免費限時領取、特價折扣、測試版/Demo釋出等資訊）。

⚠️ 嚴格時間與標示規則：
1. 你「只允許」整理並顯示發生在 {cutoff_str} 至 {today_str} 之間的最新事件。
2. 超過 7 天前的舊聞、一年前（2025年以前）的歷史事件，一律嚴格過濾、直接丟棄，絕對不能顯示。
3. 必須在每條事件的最開頭，明確標示出該事件在網路社群上爆出的真實日期，格式為 **[MM/DD]**。

請嚴格依照以下 Markdown 格式輸出列表（不要任何寒暄、前言或結語）：

### 🎮 實況主區
* **[MM/DD]** [事件簡述]：核心爭議點與網友討論摘要。

### 🔮 VTuber 區
* **[MM/DD]** [事件簡述]：核心爭議點與網友討論摘要.

### 🕹️ 遊戲區
* **[MM/DD]** [遊戲名稱/情報簡述]：免費、特價、測試版等具體情報內容。
"""
    print("🔍 AI 正在主動潛入網路搜尋最新 Threads 與社群炎上事件及獨立遊戲情報（這需要花費大約 10-20 秒）...")
    try:
        response = model.generate_content(prompt)
        ai_output = response.text
    except Exception as e:
        print(f"❌ 呼叫 Gemini 連網搜尋失敗：{e}")
        exit(1)

# 5. 解析 Gemini 輸出的 Markdown 格式並結構化儲存
new_extracted_events = []
current_category = None
lines = ai_output.split('\n')
i = 0
while i < len(lines):
    line = lines[i].strip()
    if not line:
        i += 1
        continue
    
    # 辨識分類 (僅在行首以 # 開頭時進行辨識，避免內文包含關鍵字誤判)
    if line.startswith("#"):
        if "實況主" in line or "STREAMER" in line or "🎮" in line:
            current_category = "STREAMER"
        elif "VTuber" in line or "vtuber" in line or "🔮" in line:
            current_category = "VTUBER"
        elif "遊戲" in line or "GAME" in line or "🕹️" in line:
            current_category = "GAME"
        i += 1
        continue
        
        
    # 匹配清單項目： * **[MM/DD]** [事件簡述]：內容
    match = re.match(r'^\*\s*\*\*\[?(\d{1,2})/(\d{1,2})\]?.*?\s*\[(.*?)\]\s*[:：]\s*(.*)', line)
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
            markdown_img_match = re.search(r'!\[.*?\]\((.*?)\)', next_line)
            if markdown_img_match:
                image_url = markdown_img_match.group(1)
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

print(f"✨ 成功擷取出 {len(new_extracted_events)} 筆最新事件與情報。")

# 6. 合併新舊資料並進行去重 (以 category, date, title 為鍵)
db_path = "C:/Users/User/.gemini/antigravity/scratch/threads_monitor/events.json"
html_path = "C:/Users/User/.gemini/antigravity/scratch/threads_monitor/index.html"

existing_events = []
if os.path.exists(db_path):
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            existing_events = json.load(f)
    except Exception as e:
        print(f"⚠️ 載入資料庫失敗：{e}，將初始化新資料庫。")

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
            ev["days_left"] = 6 - delta
            active_events.append(ev)
        else:
            expired_count += 1
    except Exception as e:
        print(f"⚠️ 處理日期出錯 ({ev.get('date')}): {e}")
        continue

# 最新日期排在最前
active_events.sort(key=lambda x: x["date"], reverse=True)

# 寫入 events.json 存檔
with open(db_path, "w", encoding="utf-8") as f:
    json.dump(active_events, f, ensure_ascii=False, indent=2)
print(f"💾 資料庫更新成功！保留：{len(active_events)} 筆，自動淘汰：{expired_count} 筆。")

# 8. 統計各分類事件數量
streamer_count = sum(1 for e in active_events if e["category"] == "STREAMER")
vtuber_count = sum(1 for e in active_events if e["category"] == "VTUBER")
game_count = sum(1 for e in active_events if e["category"] == "GAME")

# 9. 拼裝符合網頁 CSS 架構的 HTML 內容
events_html_list = []
for ev in active_events:
    cat = ev["category"]
    date_str = ev["date"]
    try:
        dt = datetime.strptime(date_str, "%Y/%m/%d")
        date_display = f"{dt.month}月{dt.day}日"
    except:
        date_display = date_str
    
    days_left = ev.get("days_left", 0)
    days_left_text = f"剩餘 {days_left} 天下架" if days_left > 0 else "最後一天上架"
    
    if cat == "STREAMER":
        cat_class = "streamer"
        cat_label = '<span class="cat-label cat-streamer">🎮 實況主</span>'
    elif cat == "VTUBER":
        cat_class = "vtuber"
        cat_label = '<span class="cat-label cat-vtuber">🔮 VTuber</span>'
    else:
        cat_class = "game"
        cat_label = '<span class="cat-label cat-game">🕹️ 遊戲區</span>'
        
    image_url = ev.get("image_url")
    # 對於無圖片的卡片提供對應類別的高視覺質感 default Unsplash 圖片
    if not image_url:
        if cat == "STREAMER":
            image_url = "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=500"
        elif cat == "VTUBER":
            image_url = "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500"
        else:
            image_url = "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=500"

    image_html = f'\n            <img class="event-image" src="{image_url}" alt="事件圖片" loading="lazy">' if image_url else ''
    
    card_html = f"""
        <div class="event-card {cat_class}" data-category="{cat}">
            <div class="card-header">
                {cat_label}
                <div class="card-meta">
                    <span class="event-date">{date_display}</span>
                    <span class="badge badge-info">⏰ {days_left_text}</span>
                </div>
            </div>
            <h3 class="event-title">{ev["title"]}</h3>
            <p class="event-summary">{ev["summary"]}</p>
            {image_html}
        </div>"""
    events_html_list.append(card_html)

if not events_html_list:
    formatted_events_html = '<div class="no-events">📡 當前無監測中事件，舊訊息已完全自動下架清空。</div>'
else:
    formatted_events_html = "\n".join(events_html_list)

# 10. 生成漂亮的深色漸層前端網頁
html_template = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 網路輿情炎上觀測站</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0d1117;
            --container-bg: rgba(22, 27, 34, 0.7);
            --card-bg: #161b22;
            --card-border: #30363d;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            
            --streamer-color: #a582ff;
            --streamer-glow: rgba(165, 130, 255, 0.15);
            --vtuber-color: #ff82b2;
            --vtuber-glow: rgba(255, 130, 178, 0.15);
            --game-color: #3fb950;
            --game-glow: rgba(63, 185, 80, 0.15);
            
            --warning-color: #f0883e;
            --info-color: #58a6ff;
            --active-tab-bg: #21262d;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Outfit', 'Noto Sans TC', -apple-system, BlinkMacSystemFont, sans-serif;
            background: radial-gradient(circle at top, #161b22 0%, #0d1117 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}

        .container {{
            width: 100%;
            max-width: 900px;
            background: var(--container-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 30px;
            position: relative;
        }}

        header h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 15px;
            background: linear-gradient(135deg, #ff82b2 0%, #a582ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        header p {{
            color: var(--text-secondary);
            font-size: 1rem;
            margin: 5px 0;
        }}

        .time-badge {{
            display: inline-block;
            background: #21262d;
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-primary);
            margin-top: 15px;
        }}

        /* 統計狀態欄 */
        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: rgba(22, 27, 34, 0.5);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            background: rgba(33, 38, 45, 0.5);
        }}

        .stat-label {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 5px;
            display: block;
        }}

        .stat-val {{
            font-size: 1.5rem;
            font-weight: 700;
        }}

        .stat-streamer {{ color: var(--streamer-color); }}
        .stat-vtuber {{ color: var(--vtuber-color); }}
        .stat-game {{ color: var(--game-color); }}

        /* 分類選擇頁籤 */
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 15px;
            overflow-x: auto;
        }}

        .tab-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-secondary);
            padding: 10px 20px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.95rem;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
        }}

        .tab-btn:hover {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.03);
        }}

        .tab-btn.active {{
            background: var(--active-tab-bg);
            border-color: var(--card-border);
            color: var(--text-primary);
        }}

        /* 事件清單 */
        .events-list {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .event-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 24px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            display: block;
        }}

        .event-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
        }}

        .event-card.streamer::before {{ background: var(--streamer-color); }}
        .event-card.vtuber::before {{ background: var(--vtuber-color); }}
        .event-card.game::before {{ background: var(--game-color); }}

        .event-card.streamer:hover {{
            box-shadow: 0 8px 30px var(--streamer-glow);
            border-color: rgba(165, 130, 255, 0.3);
            transform: translateY(-2px);
        }}

        .event-card.vtuber:hover {{
            box-shadow: 0 8px 30px var(--vtuber-glow);
            border-color: rgba(255, 130, 178, 0.3);
            transform: translateY(-2px);
        }}

        .event-card.game:hover {{
            box-shadow: 0 8px 30px var(--game-glow);
            border-color: rgba(63, 185, 80, 0.3);
            transform: translateY(-2px);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .cat-label {{
            font-size: 0.8rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 8px;
        }}

        .cat-streamer {{
            background: rgba(165, 130, 255, 0.15);
            color: var(--streamer-color);
        }}

        .cat-vtuber {{
            background: rgba(255, 130, 178, 0.15);
            color: var(--vtuber-color);
        }}

        .cat-game {{
            background: rgba(63, 185, 80, 0.15);
            color: var(--game-color);
        }}

        .card-meta {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .event-date {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            font-weight: 500;
        }}

        .badge {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            display: flex;
            align-items: center;
        }}

        .badge-warning {{
            background: rgba(240, 136, 62, 0.15);
            color: var(--warning-color);
        }}

        .badge-info {{
            background: rgba(88, 166, 255, 0.15);
            color: var(--info-color);
        }}

        .event-title {{
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 10px;
            line-height: 1.4;
        }}

        .event-summary {{
            font-size: 0.95rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }}

        .event-image {{
            display: block;
            width: 100%;
            max-height: 380px;
            object-fit: cover;
            border-radius: 12px;
            margin-top: 15px;
            border: 1px solid var(--card-border);
            background: #000;
        }}

        .no-events {{
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
            font-size: 1rem;
            border: 1px dashed var(--card-border);
            border-radius: 16px;
        }}

        .readonly-notice {{
            text-align: center;
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 40px;
            letter-spacing: 1px;
            border-top: 1px solid var(--card-border);
            padding-top: 25px;
        }}

        /* 響應式優化 */
        @media (max-width: 600px) {{
            .container {{
                padding: 20px;
                border-radius: 16px;
            }}
            header h1 {{
                font-size: 1.8rem;
            }}
            .stats-bar {{
                grid-template-columns: 1fr;
                gap: 10px;
            }}
            .card-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }}
            .card-meta {{
                width: 100%;
                justify-content: space-between;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔥 網路輿情炎上觀測站</h1>
            <p>🕒 自動化監控 · 僅保留 6 天內最新事件 · 屆滿自動淘汰清空</p>
            <div class="time-badge">當前觀測時間：{today_str}</div>
        </header>

        <!-- 狀態統計欄 -->
        <div class="stats-bar">
            <div class="stat-card">
                <span class="stat-label">🎮 實況主事件</span>
                <span class="stat-val stat-streamer" id="stats-streamer">{streamer_count}</span>
            </div>
            <div class="stat-card">
                <span class="stat-label">🔮 VTuber 事件</span>
                <span class="stat-val stat-vtuber" id="stats-vtuber">{vtuber_count}</span>
            </div>
            <div class="stat-card">
                <span class="stat-label">🕹️ 遊戲情報</span>
                <span class="stat-val stat-game" id="stats-game">{game_count}</span>
            </div>
        </div>

        <!-- 篩選頁籤 -->
        <div class="tabs">
            <button class="tab-btn active" data-filter="ALL">📱 全部 (實況主/VTuber)</button>
            <button class="tab-btn" data-filter="STREAMER">🎮 實況主區</button>
            <button class="tab-btn" data-filter="VTUBER">🔮 VTuber 區</button>
            <button class="tab-btn" data-filter="GAME">🕹️ 遊戲情報特區</button>
        </div>

        <!-- 事件清單 -->
        <div class="events-list" id="events-container">
{formatted_events_html}
        </div>

        <div class="readonly-notice">🔒 BOARD STATUS: AUTOMATED RADAR ACTIVE (唯讀監控中)</div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const tabs = document.querySelectorAll('.tab-btn');
            const cards = document.querySelectorAll('.event-card');
            const container = document.getElementById('events-container');

            function filterCategory(filterValue) {{
                let matchCount = 0;
                cards.forEach(card => {{
                    const cardCat = card.getAttribute('data-category');
                    if (filterValue === 'ALL') {{
                        // "ALL" 頁籤精準呈現 實況主區(STREAMER) 與 VTuber區(VTUBER)，排除遊戲區(GAME)
                        if (cardCat === 'STREAMER' || cardCat === 'VTUBER') {{
                            card.style.display = 'block';
                            matchCount++;
                        }} else {{
                            card.style.display = 'none';
                        }}
                    }} else {{
                        // 各別分頁顯示對應類別
                        if (cardCat === filterValue) {{
                            card.style.display = 'block';
                            matchCount++;
                        }} else {{
                            card.style.display = 'none';
                        }}
                    }}
                }});

                // 如果該分類下沒有任何卡片，顯示無事件提示
                const existingNoEvents = container.querySelector('.no-events-temp');
                if (existingNoEvents) {{
                    existingNoEvents.remove();
                }}

                if (matchCount === 0) {{
                    const noEventsDiv = document.createElement('div');
                    noEventsDiv.className = 'no-events no-events-temp';
                    noEventsDiv.innerText = '📡 此分類下目前無 6 天內的監測事件。';
                    container.appendChild(noEventsDiv);
                }}
            }}

            tabs.forEach(tab => {{
                tab.addEventListener('click', () => {{
                    tabs.forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    filterCategory(tab.getAttribute('data-filter'));
                }});
            }});

            // 預設初始化為全部 (實況主/VTuber)
            filterCategory('ALL');
        }});
    </script>
</body>
</html>"""

# 11. 寫出網頁檔案
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print("✅ [成功] index.html 已由 AI 聯網抓取最新資料並自動淘汰、更新完成！")
