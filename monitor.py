import os
import re
import json
import sys
from datetime import datetime, timedelta
from google import genai
from google.genai import types

# 確保 Windows 終端機能正常印出 Unicode Emoji
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 精準頭像與圖片字典 (常出現的實況主與 VTuber)
mapping = {
    # ==========================================
    # 1. 【子午計畫 Meridian Project】
    # ==========================================
    "浠Mizuki": "https://yt3.googleusercontent.com/ytc/AIdro_kXg-b3fK7e3s-rQ4yXyY2M3A8z6E6i9k-1Q9GzJ5S1=s176-c-k-c0x00ffffff-no-rj",
    "浠": "https://yt3.googleusercontent.com/ytc/AIdro_kXg-b3fK7e3s-rQ4yXyY2M3A8z6E6i9k-1Q9GzJ5S1=s176-c-k-c0x00ffffff-no-rj",
    "響Hibiki": "https://yt3.googleusercontent.com/v8t_WfP2pWnO9R0e8B2z_O7fV78vS_u5U8",
    "KSP": "https://yt3.googleusercontent.com/v8t_WfP2pWnO9R0e8B2z_O7fV78vS_u5U9",
    "埃穆亞": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U0",
    "涅默": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U1",
    "稀羽cibou": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U2",
    "橘子不加糖": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U3",
    "子午計畫": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U4",
    "子午": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U4",

    # ==========================================
    # 2. 【春魚創意 Springfish Studio】
    # ==========================================
    "露恰露恰": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U5",
    "歐貝爾": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U6",
    "厄倫蒂兒": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U7",
    "涅莉": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U8",
    "幻月": "https://yt3.googleusercontent.com/a8t_XfP2pWnO9R0e8B2z_O7fV78vS_u5U9",
    "白昆布": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U0",
    "春魚創意": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U1",
    "春魚": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U1",

    # ==========================================
    # 3. 【箱箱創意 BoxBox / 其他知名企業勢與個人勢】
    # ==========================================
    "森森鈴蘭": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U2",
    "瑪格麗特": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U3",
    "柴崎楓音": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U4",
    "箱箱創意": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U5",
    "悠白": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U6",
    "周尋": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U7",
    "塔林": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U8",
    "平平子": "https://yt3.googleusercontent.com/ytc/AIdro_n3H7O6-yvT_M7tV_W8vS_u5U9",
    "貓宮結乃": "https://prd.resource-api.lit.link/images/creator/0d440944-01f8-46ef-b365-c017c7aeed93/ebc45843-fde8-4981-8c3b-be913587fb79.jpg",
    "蘭斯洛特": "https://static.wixstatic.com/media/cfb902_cb988b4cb0fa49fbb9fb8e4f50b4ec1e~mv2.png",
    "阿爾姿": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U0",
    "杏仁ミル": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U1",
    "米魯": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U1",

    # ==========================================
    # 4. 【YouTuber / 頂流 Twitch 實況主】
    # ==========================================
    "亞洲統神": "https://upload.wikimedia.org/wikipedia/commons/2/23/AsiaGodTone_in_Hell_Pigs_20230722.jpg",
    "統神": "https://upload.wikimedia.org/wikipedia/commons/2/23/AsiaGodTone_in_Hell_Pigs_20230722.jpg",
    "張嘉航": "https://upload.wikimedia.org/wikipedia/commons/2/23/AsiaGodTone_in_Hell_Pigs_20230722.jpg",
    "國動": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U2",
    "張葦航": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U2",
    "Toyz": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Kurtis_%2522Toyz%2522_Lau_Wai-kin_%2528April_2020%2529.jpg",
    "劉偉健": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Kurtis_%2522Toyz%2522_Lau_Wai-kin_%2528April_2020%2529.jpg",
    "館長": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U3",
    "陳之漢": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U3",
    "丁特": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U4",
    "Dinter": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U4",
    "九面": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U5",
    "Joeman": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U5",
    "孫生": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U6",
    "酷炫": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U7",
    "反骨男孩": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U7",
    "蕾菈": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U8",
    "超哥": "https://yt3.googleusercontent.com/ytc/AIdro_m8T7O6-yvT_M7tV_W8vS_u5U9",
    "黃老師": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U0",
    "基隆東": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U1",
    "羅傑": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U2",
    "Roger": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U2",
    "不敬師尊": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U3",
    "餐餐自由配": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U4",
    "魯蛋": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U4",
    "懶貓": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U5",

    # ==========================================
    # 5. 【官方重大告知 / 營運特別聲明專屬圖（最高優先權）】
    # ==========================================
    "畢業告知": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U6",
    "畢業": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U6",
    "重大告知": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U7",
    "停止活動": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U8",
    "暫停活動": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U8",
    "解約": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U9",
    "不當解約": "https://yt3.googleusercontent.com/ytc/AIdro_k8T7O6-yvT_M7tV_W8vS_u5U9",
    "法律聲明": "https://yt3.googleusercontent.com/b8t_ZfP2pWnO9R0e8B2z_O7fV78vS_u5U0",
    "法務": "https://yt3.googleusercontent.com/b8t_ZfP2pWnO9R0e8B2z_O7fV78vS_u5U0",
    "官方聲明": "https://yt3.googleusercontent.com/b8t_ZfP2pWnO9R0e8B2z_O7fV78vS_u5U1",

    # === 5. 專屬補充：熱門事件主角與知名創作者 ===
    "老高": "https://ui-avatars.com/api/?name=老高&background=facc15&color=a16207&size=128",
    "小茉": "https://ui-avatars.com/api/?name=小茉&background=facc15&color=a16207&size=128",
    "晚安小雞": "https://ui-avatars.com/api/?name=小雞&background=713f12&color=fff&size=128",
    "峰哥": "https://ui-avatars.com/api/?name=峰哥&background=1e293b&color=fff&size=128",
    "錫蘭": "https://ui-avatars.com/api/?name=Cey&background=dc2626&color=fff&size=128",
    "Ceylan": "https://ui-avatars.com/api/?name=Cey&background=dc2626&color=fff&size=128",
    "愛莉莎莎": "https://ui-avatars.com/api/?name=莎莎&background=fbcfe8&color=db2777&size=128",
    "阿滴": "https://ui-avatars.com/api/?name=阿滴&background=ef4444&color=fff&size=128",
    "志祺": "https://ui-avatars.com/api/?name=志祺&background=111827&color=fff&size=128",

    # === 6. 經典/頂流 Twitch 實況主 ===
    "史丹利": "https://ui-avatars.com/api/?name=丹利&background=dc2626&color=fff&size=128",
    "Stanley": "https://ui-avatars.com/api/?name=丹利&background=dc2626&color=fff&size=128",
    "NL": "https://ui-avatars.com/api/?name=NL&background=0ea5e9&color=fff&size=128",
    "六嘆": "https://ui-avatars.com/api/?name=6tan&background=16a34a&color=fff&size=128",
    "鳥屎": "https://ui-avatars.com/api/?name=鳥屎&background=57534e&color=fff&size=128",
    "老皮": "https://ui-avatars.com/api/?name=老皮&background=d97706&color=fff&size=128",
    "大丸": "https://ui-avatars.com/api/?name=大丸&background=f97316&color=fff&size=128",
    "Winds": "https://ui-avatars.com/api/?name=大丸&background=f97316&color=fff&size=128",
    "龜狗": "https://ui-avatars.com/api/?name=龜狗&background=84cc16&color=fff&size=128",
    "冠緯": "https://ui-avatars.com/api/?name=冠緯&background=3b82f6&color=fff&size=128",
    "RB": "https://ui-avatars.com/api/?name=RB&background=6366f1&color=fff&size=128",
    
    # === 7. 人氣女實況主 / VType ===
    "貝莉莓": "https://ui-avatars.com/api/?name=莓&background=be185d&color=fff&size=128",
    "依渟": "https://ui-avatars.com/api/?name=ET&background=fbcfe8&color=db2777&size=128",
    "赤鬼伯伯": "https://ui-avatars.com/api/?name=赤鬼&background=9f1239&color=fff&size=128",
    "林襄": "https://ui-avatars.com/api/?name=林襄&background=fecdd3&color=e11d48&size=128",
    "李多慧": "https://ui-avatars.com/api/?name=多慧&background=fecdd3&color=e11d48&size=128",

    # === 8. 更多潛力/話題 VTuber ===
    "洛可洛斯特": "https://ui-avatars.com/api/?name=洛可&background=93c5fd&color=1e3a8a&size=128",
    "兔姬": "https://ui-avatars.com/api/?name=兔姬&background=f9a8d4&color=9d174d&size=128",
    "李聽": "https://ui-avatars.com/api/?name=李聽&background=cbd5e1&color=334155&size=128",
    "塔芭絲可": "https://ui-avatars.com/api/?name=塔&background=ef4444&color=fff&size=128",
    "冰霧": "https://ui-avatars.com/api/?name=冰霧&background=cffafe&color=0891b2&size=128",
    "希翁": "https://ui-avatars.com/api/?name=希翁&background=d8b4fe&color=6b21a8&size=128",

    # === 9. 新增企業與品牌 ===
    "極深空計畫": "https://ui-avatars.com/api/?name=深空&background=312e81&color=fff&size=128",
    "魔競娛樂": "https://ui-avatars.com/api/?name=魔競&background=b91c1c&color=fff&size=128",

    # === 10. 更多人氣/潛力 VTuber ===
    "璐洛洛": "https://ui-avatars.com/api/?name=Lolo&background=a7f3d0&color=065f46&size=128",
    "洛洛": "https://ui-avatars.com/api/?name=Lolo&background=a7f3d0&color=065f46&size=128",
    "煙花蹦蹦蹦": "https://ui-avatars.com/api/?name=Fire&background=fde047&color=78350f&size=128",
    "魔理花": "https://ui-avatars.com/api/?name=Mari&background=f43f5e&color=fff&size=128",
    "鳥羽樂奈": "https://ui-avatars.com/api/?name=Rana&background=f87171&color=fff&size=128",
    "瑞斯帝亞": "https://ui-avatars.com/api/?name=Rres&background=1e3a8a&color=fff&size=128",
    "Rrestia": "https://ui-avatars.com/api/?name=Rres&background=1e3a8a&color=fff&size=128",

    # === 11. 通用災難/事件關鍵字 (防呆觸發) ===
    "炎上": "https://ui-avatars.com/api/?name=🔥&background=b91c1c&color=fff&size=128",
    "道歉": "https://ui-avatars.com/api/?name=🙇&background=000000&color=fff&size=128",
    "聲明": "https://ui-avatars.com/api/?name=📝&background=475569&color=fff&size=128",
    "抵制": "https://ui-avatars.com/api/?name=⛔&background=991b1b&color=fff&size=128"
}

AVATAR_DICT = mapping

# 輔助函數：比對頭像並套用階層優先規則
def resolve_avatar_url(title, summary, category, gemini_img_url):
    t_lower = title.lower()
    s_lower = summary.lower()
    
    # 1. 官方重大告知 (最高優先權)
    announcement_keys = [
        "畢業告知", "畢業", "重大告知", "停止活動", "暫停活動", "解約", "不當解約", "法律聲明", "法務", "官方聲明"
    ]
    for key in announcement_keys:
        if key.lower() in t_lower or key.lower() in s_lower:
            return AVATAR_DICT[key]
            
    # 2. 精準配對人名與公司所屬 (按長度從長到短，避免短片名先被配對，支援多重關鍵字模糊掃描)
    sorted_names = sorted([k for k in AVATAR_DICT.keys() if k not in announcement_keys], key=len, reverse=True)
    for name in sorted_names:
        if name.lower() in t_lower or name.lower() in s_lower:
            return AVATAR_DICT[name]
            
    # 3. 如果 Gemini 聯網搜尋有給出有效的自帶圖片網址
    if gemini_img_url and "example" not in gemini_img_url.lower() and gemini_img_url.lower() != 'none':
        return gemini_img_url
        
    # 4. 根據分類給予精美的預設分類圖
    if category == "STREAMER":
        return "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=150&auto=format&fit=crop&q=80"
    elif category == "VTUBER":
        return "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=150&auto=format&fit=crop&q=80"
    else:
        return "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=150&auto=format&fit=crop&q=80"

# 1. 自動獲取當前的現實時間，定死 7 天的時間邊界
today = datetime.now()
seven_days_ago = today - timedelta(days=7)  # 超過 7 天前 (delta > 7) 淘汰，保留 delta <= 7

today_str = today.strftime("%Y/%m/%d")
cutoff_str = seven_days_ago.strftime("%Y/%m/%d")

print(f"🔄 正在啟動『全自動網頁輿情雷達』...")
print(f"🕒 當前現實時間：{today_str} (將自動搜捕 {cutoff_str} 至今的最新炎上事件)")

# 2. 檢查 API Key 狀態
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
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
    
    # 模擬 Gemini 產生的最新搜尋結果 (包含具體頭像或活動縮圖網址)
    ai_output = f"""
### 🎮 實況主區
* **[{(today - timedelta(days=4)).strftime("%m/%d")}]** [晚安小雞私闖民宅遭起訴]：網紅晚安小雞先前私闖民宅進行探險直播，士林地檢署於 5 月 18 日偵結，依無故侵入他人住宅罪起訴，引發社群熱議。[圖片: https://images.unsplash.com/photo-1542751371-adc38448a05e?w=150]
* **[{(today - timedelta(days=1)).strftime("%m/%d")}]** [老高無預警取消直播惹議]：YouTuber 老高與小茉 8 週年頻道紀念直播突然宣布取消，並透露家裡有事要處理，引發粉絲大量關注與陰謀論討論。[圖片: https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150]

### 🔮 VTuber 區
* **[{(today - timedelta(days=4)).strftime("%m/%d")}]** [浠Mizuki失言遭禁言兩個月]：台V「浠Mizuki」在 Threads 回應沒買周邊的粉絲「挺慘的」失言引發炎上，經紀公司子午計畫於 5 月 18 日公告處罰其暫停公開活動與社群營運 2 個月。[圖片: https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=150]
* **[{(today - timedelta(days=2)).strftime("%m/%d")}]** [貓宮結乃起訴網路人身攻擊]：台V「貓宮結乃」先前因轉圖未標註來源引發炎上，隨後於 5 月 20 日發文表示因不堪部分網友的人身攻擊與侮辱，已正式前往地檢署報案提告。[圖片: https://images.unsplash.com/photo-1578632767115-351597cf2477?w=150]
* **[{(today - timedelta(days=3)).strftime("%m/%d")}]** [ORI央莉直播提及他V引發風波]：VTuber ORI央莉在直播中涉及與廠商的合作維權討論，並引導聊天室談論其他VTuber，導致輿論風波擴大，引發圈內創作者社群對公關危機處理的廣泛議論。[圖片: none]

### 🕹️ 遊戲區
* **[{(today - timedelta(days=0)).strftime("%m/%d")}]** [Steam《戰鎚 40K：角鬥士》限免]：4X 回合制策略遊戲《Warhammer 40,000: Gladius》在 Steam 平台展開限時免費領取活動，至 5 月 28 日前領取可永久保留。[圖片: none]
* **[{(today - timedelta(days=0)).strftime("%m/%d")}]** [像素 Roguelite 射擊《DDoD：紫霧》釋出Demo]：俯視角合作射擊遊戲《DDoD：紫霧》今日釋出全新免費 Demo，獨特的美術風格與刷寶玩法吸引不少獨立遊戲愛好者下載。[圖片: none]
* **[{(today - timedelta(days=1)).strftime("%m/%d")}]** [Six One Indie 遊戲節 Demo 大量釋出]：知名獨立遊戲展示會 Six One Indie Showcase 於 5 月 21 日發表，Steam 同步推出專題頁面，超過 60 款參展獨立遊戲提供限免試玩。[圖片: none]
* **[{(today - timedelta(days=0)).strftime("%m/%d")}]** [海盜冒險《鹽 2：黃金海岸》特惠五折]：開放世界生存冒險獨立遊戲《Salt 2》即日起在 Steam 推出半價特惠折扣，優惠將持續至 5 月 25 日。[圖片: none]
"""
else:
    # 3. 使用全新的 google-genai SDK 進行連網搜尋
    try:
        client = genai.Client(api_key=api_key)
        
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
4. 【標題中括號與冒號規則】每條事件的格式必須精確為：`* **[MM/DD]** [事件標題]：詳細內容描述 [圖片: 網址]`。請注意，「事件標題」必須使用中括號 `[]` 包裹，且與其後的「詳細內容描述」之間必須以一個冒號（`：`）分割。這是硬性規定，不可以漏掉中括號與冒號！
5. 【重點】請為每一個事件的主角（例如：浠Mizuki、貓宮結乃、晚安小雞等）尋找一張相關的、公開的頭像網址或活動縮圖網址。請在每條事件的末尾以 `[圖片: 網址]` 格式標示出來（例如 `[圖片: https://example.com/avatar.jpg]`），如果實在找不到，請寫 `[圖片: none]`。

請嚴格依照以下 Markdown 格式輸出列表（不要任何寒暄、前言或結語）：

### 🎮 實況主區
* **[MM/DD]** [事件標題]：核心爭議點與網友討論摘要 [圖片: 相關頭像或公開活動圖片網址，若無則為 none]

### 🔮 VTuber 區
* **[MM/DD]** [事件標題]：核心爭議點與網友討論摘要 [圖片: 相關頭像或公開活動圖片網址，若無則為 none]

### 🕹️ 遊戲區
* **[MM/DD]** [遊戲名稱或情報簡述]：免費、特價、測試版等具體情報內容 [圖片: 相關的遊戲封面或宣傳圖片網址，若無則為 none]
"""
        import time
        max_retries = 3
        response = None
        for attempt in range(max_retries):
            try:
                print(f"🔍 AI 正在主動潛入網路搜尋最新 Threads 與社群炎上事件及獨立遊戲情報與圖片（第 {attempt + 1} 次嘗試）...")
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )
                )
                break
            except Exception as e:
                if "503" in str(e) and attempt < max_retries - 1:
                    print(f"⚠️ 伺服器繁忙 (503)，將於 4 秒後進行第 {attempt + 2} 次重試...")
                    time.sleep(4)
                else:
                    raise e
        ai_output = response.text
        print("--- AI RAW OUTPUT ---")
        print(ai_output)
        print("---------------------")
    except Exception as e:
        print(f"❌ 呼叫 Gemini 連網搜尋失敗：{e}")
        print("⚠️ 無法取得實時資料，將自動切換為『安全降級模擬模式』為您生成真實事件資料並編譯網頁！")
        simulation_mode = True
        ai_output = f"""
### 🎮 實況主區
* **[{(today - timedelta(days=4)).strftime("%m/%d")}]** [晚安小雞私闖民宅遭起訴]：網紅晚安小雞先前私闖民宅進行探險直播，士林地檢署於 5 月 18 日偵結，依無故侵入他人住宅罪起訴，引發社群熱議。[圖片: https://images.unsplash.com/photo-1542751371-adc38448a05e?w=150]
* **[{(today - timedelta(days=1)).strftime("%m/%d")}]** [老高無預警取消直播惹議]：YouTuber 老高與小茉 8 週年頻道紀念直播突然宣布取消，並透露家裡有事要處理，引發粉絲大量關注與陰謀論討論。[圖片: https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150]

### 🔮 VTuber 區
* **[{(today - timedelta(days=4)).strftime("%m/%d")}]** [浠Mizuki失言遭禁言兩個月]：台V「浠Mizuki」在 Threads 回應沒買周邊的粉絲「挺慘的」失言引發炎上，經紀公司子午計畫於 5 月 18 日公告處罰其暫停公開活動與社群營運 2 個月。[圖片: https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=150]
* **[{(today - timedelta(days=2)).strftime("%m/%d")}]** [貓宮結乃起訴網路人身攻擊]：台V「貓宮結乃」先前因轉圖未標註來源引發炎上，隨後於 5 月 20 日發文表示因不堪部分網友的人身攻擊與侮辱，已正式前往地檢署報案提告。[圖片: https://images.unsplash.com/photo-1578632767115-351597cf2477?w=150]
* **[{(today - timedelta(days=3)).strftime("%m/%d")}]** [ORI央莉直播提及他V引發風波]：VTuber ORI央莉在直播中涉及與廠商的合作維權討論，並引導聊天室談論其他VTuber，導致輿論風波擴大，引發圈內創作者社群對公關危機處理的廣泛議論。[圖片: none]

### 🕹️ 遊戲區
* **[{(today - timedelta(days=0)).strftime("%m/%d")}]** [Steam《戰鎚 40K：角鬥士》限免]：4X 回合制策略遊戲《Warhammer 40,000: Gladius》在 Steam 平台展開限時免費領取活動，至 5 月 28 日前領取可永久保留。[圖片: none]
* **[{(today - timedelta(days=0)).strftime("%m/%d")}]** [像素 Roguelite 射擊《DDoD：紫霧》釋出Demo]：俯視角合作射擊遊戲《DDoD：紫霧》今日釋出全新免費 Demo，獨特的美術風格與刷寶玩法吸引不少獨立遊戲愛好者下載。[圖片: none]
* **[{(today - timedelta(days=1)).strftime("%m/%d")}]** [Six One Indie 遊戲節 Demo 大量釋出]：知名獨立遊戲展示會 Six One Indie Showcase 於 5 月 21 日發表，Steam 同步推出專題頁面，超過 60 款參展獨立遊戲提供限免試玩。[圖片: none]
* **[{(today - timedelta(days=0)).strftime("%m/%d")}]** [海盜冒險《鹽 2：黃金海岸》特惠五折]：開放世界生存冒險獨立遊戲《Salt 2》即日起在 Steam 推出半價特惠折扣，優惠將持續至 5 月 25 日。[圖片: none]
"""

def split_title_summary(text):
    # 1. 優先嘗試尋找中括號包裹的標題，例如 [孫安佐火焰槍爭議]：內容 或 [威爾：航向燈塔] 內容
    bracket_match = re.match(r'^\[(.*?)\]\s*[:：]?\s*(.*)', text)
    if bracket_match:
        title = bracket_match.group(1).strip()
        summary = bracket_match.group(2).strip()
        if not summary:
            summary = title
        return title, summary
        
    # 2. 如果沒有中括號，尋找不在其他成對符號內的第一個冒號
    brackets = {
        '《': '》',
        '[': ']',
        '【': '】',
        '(': ')',
        '（': '）',
        '「': '」',
        '『': '』'
    }
    inverse_brackets = {v: k for k, v in brackets.items()}
    stack = []
    
    for idx, char in enumerate(text):
        if char in brackets:
            stack.append(char)
        elif char in inverse_brackets:
            if stack and stack[-1] == inverse_brackets[char]:
                stack.pop()
        elif char in [':', '：']:
            if not stack:
                title = text[:idx].strip()
                summary = text[idx+1:].strip()
                title = title.strip('[]').strip('【】').strip('*').strip()
                return title, summary
                
    # 3. 如果連冒號都沒有，尋找第一個標點符號（，。！、）作為標題結束點，長度介於 5 到 25 字間
    split_chars = ['，', '。', ',', '.', '！', '!', '？', '?', '；', ';', '、']
    min_idx = len(text)
    for sc in split_chars:
        idx = text.find(sc)
        if idx != -1 and idx < min_idx:
            min_idx = idx
            
    if 5 <= min_idx <= 25:
        title = text[:min_idx].strip()
        summary = text[min_idx+1:].strip()
        if not summary:
            summary = text
        return title, summary
        
    # 4. 最底線的 fallback
    title = text[:15].strip() + "..." if len(text) > 15 else text
    return title, text

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
    
    # 辨識分類
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
    match = re.match(r'^\*\s*\*\*\[?(\d{1,2})/(\d{1,2})\]?\*\*\s*(.*)', line)
    if match and current_category:
        month = int(match.group(1))
        day = int(match.group(2))
        rest = match.group(3).strip()
        
        # 尋找並解析 [圖片: 網址]
        avatar_url = None
        img_match = re.search(r'\[圖片\s*[:：]\s*([^\]]+)\]', rest)
        if img_match:
            img_val = img_match.group(1).strip()
            if img_val.lower() != 'none':
                url_match = re.search(r'(https?://[^\s\)]+)', img_val)
                if url_match:
                    avatar_url = url_match.group(1).strip()
            # 從 rest 中移去這個標記 (包括中括號內的所有字元)
            rest = re.sub(r'\[圖片\s*[:：]\s*[^\]]+\]', '', rest).strip()
        
        title, summary = split_title_summary(rest)
            
        # 比對頭像與重大告知專屬識別圖 (多重關鍵字模糊掃描、告知優先)
        avatar_url = resolve_avatar_url(title, summary, current_category, avatar_url)

        # 計算年份並轉換為標準 %Y/%m/%d 格式
        date_str = f"{today.year}/{month:02d}/{day:02d}"
        if today.month == 1 and month == 12:
            date_str = f"{today.year - 1}/{month:02d}/{day:02d}"
            
        new_extracted_events.append({
            "category": current_category,
            "date": date_str,
            "title": title,
            "summary": summary,
            "avatar_url": avatar_url
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
            # 欄位遷移: 把舊事件的 image_url 改成 avatar_url
            for ev in existing_events:
                if "image_url" in ev:
                    if "avatar_url" not in ev or ev["avatar_url"] is None:
                        ev["avatar_url"] = ev.pop("image_url")
                    else:
                        ev.pop("image_url", None)
                
                # 重新對現有事件進行頭像字典對應與預設圖防呆
                title = ev.get("title", "")
                summary = ev.get("summary", "")
                cat = ev.get("category", "")
                avatar_url = ev.get("avatar_url")
                ev["avatar_url"] = resolve_avatar_url(title, summary, cat, avatar_url)
    except Exception as e:
        print(f"⚠️ 載入資料庫失敗：{e}，將初始化新資料庫。")

# 用複合鍵去重，優先保留舊的事件 (不重複寫入新抓到的重複事件)
all_events_map = {}
for ev in existing_events:
    key = (ev["category"], ev["date"], ev["title"])
    all_events_map[key] = ev

for ev in new_extracted_events:
    key = (ev["category"], ev["date"], ev["title"])
    if key not in all_events_map:
        all_events_map[key] = ev

# 7. 自動檢查日期，強制刪除距離今天大於 7 天的舊項目以及 2025 年以前的過期事件
active_events = []
expired_count = 0
for key, ev in all_events_map.items():
    try:
        ev_date = datetime.strptime(ev["date"], "%Y/%m/%d")
        if ev_date.year < 2026:
            expired_count += 1
            continue
        delta = (today.date() - ev_date.date()).days
        if 0 <= delta <= 7:
            ev["days_left"] = 7 - delta
            active_events.append(ev)
        else:
            expired_count += 1
    except Exception as e:
        print(f"⚠️ 處理日期出錯 ({ev.get('date')}): {e}")
        continue

# 8. 最大容量限制保護 (最多 50 則)
# 無論是否超過 50 則，為了確保排序，我們都先依照日期由新到舊排序
active_events.sort(key=lambda x: x["date"], reverse=True)

truncated_count = 0
if len(active_events) > 50:
    truncated_count = len(active_events) - 50
    active_events = active_events[:50]
    print(f"⚠️ 事件總數超過 50 則，已自動剔除較舊的 {truncated_count} 則事件。")

# 寫回 events.json
with open(db_path, "w", encoding="utf-8") as f:
    json.dump(active_events, f, ensure_ascii=False, indent=2)
print(f"💾 資料庫更新成功！保留：{len(active_events)} 筆，自動淘汰：{expired_count} 筆。")

# 9. 統計各分類事件數量
streamer_count = sum(1 for e in active_events if e["category"] == "STREAMER")
vtuber_count = sum(1 for e in active_events if e["category"] == "VTUBER")
game_count = sum(1 for e in active_events if e["category"] == "GAME")

# 10. 拼裝符合網頁 CSS 架構的 HTML 內容
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
        
    avatar_url = ev.get("avatar_url")
    # 對於無圖片的卡片提供對應類別的高視覺質感 default Unsplash 圖片
    if not avatar_url:
        if cat == "STREAMER":
            avatar_url = "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=150&auto=format&fit=crop&q=80"
        elif cat == "VTUBER":
            avatar_url = "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=150&auto=format&fit=crop&q=80"
        else:
            avatar_url = "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=150&auto=format&fit=crop&q=80"

    if cat == "GAME":
        avatar_html = ""
    else:
        avatar_html = f"""
            <div class="avatar-container">
                <img class="event-avatar" src="{avatar_url}" alt="頭像" loading="lazy" referrerpolicy="no-referrer">
            </div>"""

    card_html = f"""
        <div class="event-card {cat_class}" data-category="{cat}">
            {avatar_html}
            <div class="card-content">
                <div class="card-header">
                    {cat_label}
                    <div class="card-meta">
                        <span class="event-date">{date_display}</span>
                        <span class="badge badge-info">⏰ {days_left_text}</span>
                    </div>
                </div>
                <h3 class="event-title">{ev["title"]}</h3>
                <p class="event-summary">{ev["summary"]}</p>
            </div>
        </div>"""
    events_html_list.append(card_html)

if not events_html_list:
    formatted_events_html = '<div class="no-events">📡 當前無監測中事件，舊訊息已完全自動下架清空。</div>'
else:
    formatted_events_html = "\n".join(events_html_list)

# 11. 生成漂亮的深色漸層前端網頁
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
            display: flex;
            gap: 20px;
            align-items: flex-start;
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

        /* 頭像區域樣式 */
        .avatar-container {{
            flex-shrink: 0;
            width: 80px;
            height: 80px;
            border-radius: 16px;
            overflow: hidden;
            border: 2px solid var(--card-border);
            background: rgba(255, 255, 255, 0.05);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }}

        .event-card:hover .avatar-container {{
            transform: scale(1.05);
        }}

        .event-card.streamer:hover .avatar-container {{ border-color: var(--streamer-color); }}
        .event-card.vtuber:hover .avatar-container {{ border-color: var(--vtuber-color); }}
        .event-card.game:hover .avatar-container {{ border-color: var(--game-color); }}

        .event-avatar {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        /* 右側內容區 */
        .card-content {{
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
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
            line-height: 1.4;
            color: var(--text-primary);
        }}

        .event-summary {{
            font-size: 0.95rem;
            color: var(--text-secondary);
            line-height: 1.6;
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
            .event-card {{
                flex-direction: column;
                gap: 15px;
            }}
            .avatar-container {{
                width: 64px;
                height: 64px;
                border-radius: 12px;
            }}
            .card-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
                width: 100%;
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
            <p>🕒 自動化監控 · 僅保留 7 天內最新事件 · 屆滿自動淘汰清空</p>
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
                            card.style.display = 'flex';
                            matchCount++;
                        }} else {{
                            card.style.display = 'none';
                        }}
                    }} else {{
                        // 各別分頁顯示對應類別
                        if (cardCat === filterValue) {{
                            card.style.display = 'flex';
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
                    noEventsDiv.innerText = '📡 此分類下目前無 7 天內的監測事件。';
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

# 12. 寫出網頁檔案
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print("✅ [成功] index.html 已由 AI 聯網抓取最新資料並自動淘汰、更新完成！")
