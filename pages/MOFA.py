import os, re
import pandas as pd
import requests
import streamlit as st
import yt_dlp

st.set_page_config(page_title="October 7", page_icon="📊", layout="wide")

st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    .main-title { text-align: center; font-size: 2.2rem; font-weight: 700; color: #1e293b; margin-bottom: 2rem; }
    .metric-card { background-color: #f8f9fa; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px; }
    .metric-title { font-size: 0.95rem; color: #64748b; margin-bottom: 8px; font-weight: 600; text-align: center; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #0f172a; text-align: center; }
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 10px; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .custom-table th { background-color: #f1f5f9; color: #334155; padding: 12px 16px; text-align: center !important; font-weight: 600; font-size: 0.9rem; border-bottom: 2px solid #e2e8f0; }
    .custom-table td { padding: 12px 16px; text-align: center !important; vertical-align: middle !important; color: #475569; font-size: 0.9rem; border-bottom: 1px solid #f1f5f9; }
    .custom-table tr:hover { background-color: #f8fafc; }
    .video-link { color: #2563eb; text-decoration: none; font-weight: 500; }
    .video-link:hover { text-decoration: underline; }
    @keyframes shimmer { 0% { background-position: -400px 0; } 100% { background-position: 400px 0; } }
    .skeleton { background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%); background-size: 800px 100%; animation: shimmer 1.5s infinite linear; border-radius: 4px; display: inline-block; }
    .skeleton-text { width: 70%; height: 14px; }
    .skeleton-box { width: 36px; height: 36px; border-radius: 4px; }
    .sidebar-icon { display: flex; align-items: center; height: 38px; justify-content: center; font-size: 1.2rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">October 7 - The last day of my life</div>', unsafe_allow_html=True)

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "October7.csv")
META_USER_TOKEN = st.secrets["META_USER_TOKEN"]

ITEMS = [
    # YouTube Shorts
    {"platform": "יוטיוב", "id": "24gFRLpMR7E"}, {"platform": "יוטיוב", "id": "7Fqb8Zl1-4w"}, {"platform": "יוטיוב", "id": "7VP1tvrK3F0"}, {"platform": "יוטיוב", "id": "cWhNSpPDkY8"},
    {"platform": "יוטיוב", "id": "f2Ho2psrDHA"}, {"platform": "יוטיוב", "id": "FViFNB73tjk"}, {"platform": "יוטיוב", "id": "gc3gGTkyTJs"}, {"platform": "יוטיוב", "id": "hgo53mbSKv4"},
    {"platform": "יוטיוב", "id": "LoumbMP6LTU"}, {"platform": "יוטיוב", "id": "OOKIchREy-I"}, {"platform": "יוטיוב", "id": "s7dlo-EO6ps"}, {"platform": "יוטיוב", "id": "XSEI6HgRjzQ"},
    # TikTok
    {"platform": "טיקטוק", "username": "i24news_ar", "id": "7693308032641404178"}, {"platform": "טיקטוק", "username": "i24news_ar", "id": "7693605131383868673"}, {"platform": "טיקטוק", "username": "i24news_ar", "id": "7696223468769086721"}, {"platform": "טיקטוק", "username": "i24news_ar", "id": "7696505060129312001"},
    {"platform": "טיקטוק", "username": "i24news_en", "id": "7693865442019921160"}, {"platform": "טיקטוק", "username": "i24news_en", "id": "7694255310751436050"}, {"platform": "טיקטוק", "username": "i24news_en", "id": "7696201889632865544"}, {"platform": "טיקטוק", "username": "i24news_en", "id": "7696547290550504712"},
    {"platform": "טיקטוק", "username": "i24news_fr", "id": "7693865674698935570"}, {"platform": "טיקטוק", "username": "i24news_fr", "id": "7694255495154109714"}, {"platform": "טיקטוק", "username": "i24news_fr", "id": "7696202386062232840"}, {"platform": "טיקטוק", "username": "i24news_fr", "id": "7696547126687583496"},
    # Twitter
    {"platform": "טוויטר", "username": "i24NEWS_AR", "id": "2107771873887154185"}, {"platform": "טוויטר", "username": "i24NEWS_AR", "id": "2108150421772771395"}, {"platform": "טוויטר", "username": "i24NEWS_AR", "id": "2110056520885141979"}, {"platform": "טוויטר", "username": "i24NEWS_AR", "id": "2110353427012403661"},
    {"platform": "טוויטר", "username": "i24NEWS_EN", "id": "2107772249511973327"}, {"platform": "טוויטר", "username": "i24NEWS_EN", "id": "2108157434930057278"}, {"platform": "טוויטר", "username": "i24NEWS_EN", "id": "2110055247792279600"}, {"platform": "טוויטר", "username": "i24NEWS_EN", "id": "2110353863069126843"},
    {"platform": "טוויטר", "username": "i24NEWS_FR", "id": "2107771596178092264"}, {"platform": "טוויטר", "username": "i24NEWS_FR", "id": "2108150891564179901"}, {"platform": "טוויטר", "username": "i24NEWS_FR", "id": "2110055870185058765"}, {"platform": "טוויטר", "username": "i24NEWS_FR", "id": "2110354237012185370"},
    # Facebook
    {"platform": "פייסבוק", "id": "1060758100274123"}, {"platform": "פייסבוק", "id": "1098661659684872"}, {"platform": "פייסבוק", "id": "1102560435692402"}, {"platform": "פייסבוק", "id": "1421376970083491"},
    {"platform": "פייסבוק", "id": "1427558415388540"}, {"platform": "פייסבוק", "id": "1575591177051076"}, {"platform": "פייסבוק", "id": "1834808051214925"}, {"platform": "פייסבוק", "id": "2003722767682462"},
    {"platform": "פייסבוק", "id": "2004915936880315"}, {"platform": "פייסבוק", "id": "28594037286923487"}, {"platform": "פייסבוק", "id": "3189661697897533"}, {"platform": "פייסבוק", "id": "996450340148747"},
    # Instagram
    {"platform": "אינסטגרם", "id": "Deb5bDXD6Gs"}, {"platform": "אינסטגרם", "id": "Deb5UJfFKU1"}, {"platform": "אינסטגרם", "id": "Deb8nh5Du4y"}, {"platform": "אינסטגרם", "id": "DeeYjQ2DnYf"},
    {"platform": "אינסטגרם", "id": "DeeYTozDXdP"}, {"platform": "אינסטגרם", "id": "DeeYzU5lXQ_"}, {"platform": "אינסטגרם", "id": "DeME-OfDP5u"}, {"platform": "אינסטגרם", "id": "DeMFNk4iDQv"},
    {"platform": "אינסטגרם", "id": "DeMFUBUiZvQ"}, {"platform": "אינסטגרם", "id": "DeOp3L4kzrY"}, {"platform": "אינסטגרם", "id": "DeOpu9WDiJ6"}, {"platform": "אינסטגרם", "id": "DeOxjLrkz4G"}
]

def get_full_url(item):
    p, i, u = item["platform"], item["id"], item.get("username", "")
    return {"יוטיוב": f"https://youtube.com/shorts/{i}", "טיקטוק": f"https://www.tiktok.com/@{u}/video/{i}", "טוויטר": f"https://x.com/{u}/status/{i}", "פייסבוק": f"https://www.facebook.com/reel/{i}", "אינסטגרם": f"https://www.instagram.com/p/{i}"}.get(p, "")

with st.sidebar:
    st.markdown("### 🔄 ניהול ורענון נתונים")
    refresh_all = st.button("🔄 רענן את כל הפלטפורמות", use_container_width=True)
    st.markdown("---")
    
    def sidebar_button(icon_html, label, key):
        c1, c2 = st.columns([0.15, 0.85])
        with c1: st.markdown(icon_html, unsafe_allow_html=True)
        with c2: return st.button(label, key=key, use_container_width=True)

    refresh_yt = sidebar_button('<div class="sidebar-icon"><i class="fa-brands fa-youtube" style="color: #ff0000;"></i></div>', "רענן יוטיוב", "btn_yt")
    refresh_tt = sidebar_button('<div class="sidebar-icon"><i class="fa-brands fa-tiktok"></i></div>', "רענן טיקטוק", "btn_tt")
    refresh_tw = sidebar_button('<div class="sidebar-icon"><i class="fa-brands fa-twitter" style="color: #1da1f2;"></i></div>', "רענן טוויטר", "btn_tw")
    refresh_fb = sidebar_button('<div class="sidebar-icon"><i class="fa-brands fa-facebook" style="color: #1877f2;"></i></div>', "רענן פייסבוק", "btn_fb")
    refresh_ig = sidebar_button('<div class="sidebar-icon"><i class="fa-brands fa-instagram" style="color: #e4405f;"></i></div>', "רענן אינסטגרם", "btn_ig")

if refresh_all and os.path.exists(CACHE_FILE): os.remove(CACHE_FILE)

metrics_placeholder, controls_placeholder, table_placeholder = st.empty(), st.empty(), st.empty()

def render_dashboard(df):
    cols = metrics_placeholder.columns(4)
    for col, title, key in zip(cols, ["סך הכל צפיות", "סך הכל לייקים", "סך הכל תגובות", "סך הכל שיתופים"], ["צפיות", "לייקים", "תגובות", "שיתופים"]):
        numeric_vals = pd.to_numeric(df[key], errors="coerce").fillna(0)
        col.markdown(f'<div class="metric-card"><div class="metric-title">{title}</div><div class="metric-value">{int(numeric_vals.sum()):,}</div></div>', unsafe_allow_html=True)
    
    t_html = '<table class="custom-table"><thead><tr><th style="width: 8%;">פלטפורמה</th><th style="width: 12%;">שם משתמש</th><th style="width: 6%;">תמונה</th><th style="width: 54%;">שם סרטון</th><th style="width: 5%;">צפיות</th><th style="width: 5%;">לייקים</th><th style="width: 5%;">תגובות</th><th style="width: 5%;">שיתופים</th></tr></thead><tbody>'
    
    icon_mapping = {
        "יוטיוב": '<div style="text-align: center;"><i class="fa-brands fa-youtube" style="color: #ff0000; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">יוטיוב</span></div>',
        "טיקטוק": '<div style="text-align: center;"><i class="fa-brands fa-tiktok" style="font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">טיקטוק</span></div>',
        "טוויטר": '<div style="text-align: center;"><i class="fa-brands fa-twitter" style="color: #1da1f2; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">טוויטר</span></div>',
        "X (טוויטר)": '<div style="text-align: center;"><i class="fa-brands fa-twitter" style="color: #1da1f2; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">טוויטר</span></div>',
        "פייסבוק": '<div style="text-align: center;"><i class="fa-brands fa-facebook" style="color: #1877f2; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">פייסבוק</span></div>',
        "אינסטגרם": '<div style="text-align: center;"><i class="fa-brands fa-instagram" style="color: #e4405f; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">אינסטגרם</span></div>'
    }

    for _, row in df.iterrows():
        plat, user, title, link = row["פלטפורמה"], row["שם משתמש"], row["שם סרטון"], row["קישור"]
        plat_display = icon_mapping.get(plat, f'<div style="text-align: center;">{plat}</div>')
        
        if title == "טוען נתונים...":
            thumb_tag, user_cell, title_cell, views, likes, comments, shares = '<div class="skeleton skeleton-box"></div>', '<div class="skeleton skeleton-text" style="width: 60%;"></div>', '<div class="skeleton skeleton-text" style="width: 85%;"></div>', *(['<div class="skeleton skeleton-text" style="width: 30px;"></div>'] * 4)
        else:
            thumb = row["תמונה"]
            thumb_tag = f'<img src="{thumb}" style="width: 36px; height: 36px; object-fit: cover; border-radius: 4px;" />' if pd.notna(thumb) and str(thumb).startswith("http") else ""
            user_cell, title_cell = user, f'<a href="{link}" target="_blank" class="video-link">{title}</a>'
            views = f"{int(pd.to_numeric(row['צפיות'], errors='coerce') or 0):,}"
            likes = f"{int(pd.to_numeric(row['לייקים'], errors='coerce') or 0):,}"
            comments = f"{int(pd.to_numeric(row['תגובות'], errors='coerce') or 0):,}"
            shares = f"{int(pd.to_numeric(row['שיתופים'], errors='coerce') or 0):,}"
        t_html += f"<tr><td>{plat_display}</td><td>{user_cell}</td><td>{thumb_tag}</td><td>{title_cell}</td><td>{views}</td><td>{likes}</td><td>{comments}</td><td>{shares}</td></tr>"
    table_placeholder.markdown(t_html + "</tbody></table>", unsafe_allow_html=True)

df_cached = pd.read_csv(CACHE_FILE) if os.path.exists(CACHE_FILE) else None
any_refresh = any([refresh_all, refresh_yt, refresh_tt, refresh_tw, refresh_fb, refresh_ig])

all_rows = []
for item in ITEMS:
    url = get_full_url(item)
    if df_cached is not None and not any_refresh:
        matched = df_cached[df_cached["קישור"] == url]
        if not matched.empty:
            all_rows.append(matched.iloc[0].to_dict())
            continue
    all_rows.append({"פלטפורמה": item["platform"], "שם משתמש": "טוען...", "תמונה": "", "שם סרטון": "טוען נתונים...", "קישור": url, "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0})

current_df = pd.DataFrame(all_rows)

# הוספת פקדי מיון מעל הטבלה
c_col1, c_col2 = controls_placeholder.columns([3, 1])
with c_col1:
    sort_by = st.selectbox("מיון לפי עמודה:", ["צפיות", "לייקים", "תגובות", "שיתופים", "פלטפורמה", "שם משתמש"], index=0, key="sort_column_select")
with c_col2:
    sort_ascending = st.checkbox("סדר עולה (Ascending)", value=False, key="sort_ascending_checkbox")

# המרת עמודות מספריות לצורך מיון נכון
for col in ["צפיות", "לייקים", "תגובות", "שיתופים"]:
    current_df[col] = pd.to_numeric(current_df[col], errors="coerce").fillna(0)

# ביצוע המיון
current_df = current_df.sort_values(by=sort_by, ascending=sort_ascending)

render_dashboard(current_df)

if df_cached is not None and not any_refresh: st.stop()

target_plat = {"יוטיוב": refresh_yt, "טיקטוק": refresh_tt, "טוויטר": refresh_tw, "פייסבוק": refresh_fb, "אינסטגרם": refresh_ig}
active_refresh = next((k for k, v in target_plat.items() if v), None)

def get_ig_map():
    try:
        res = requests.get(f"https://graph.facebook.com/v26.0/me/accounts?fields=instagram_business_account{{id,username}},name&access_token={META_USER_TOKEN}").json()
        ig_accounts = [{"id": a["instagram_business_account"]["id"], "username": a["instagram_business_account"].get("username", "i24NEWS")} for a in res.get("data", []) if a.get("instagram_business_account")]
    except: return {}
    sc_map = {}
    for ig in ig_accounts:
        next_url = f"https://graph.facebook.com/v26.0/{ig['id']}/media?fields=id,permalink,caption,thumbnail_url,total_views_count,total_like_count,total_comments_count,shares_count&limit=100&access_token={META_USER_TOKEN}"
        for _ in range(5):
            if not next_url: break
            try:
                m_res = requests.get(next_url).json()
                for post in m_res.get("data", []):
                    m = re.search(r"/(?:p|reel)/([^/]+)", post.get("permalink", ""))
                    if m: sc_map[m.group(1)] = {"username": ig["username"], "caption": post.get("caption") or "ללא כותרת", "thumbnail_url": post.get("thumbnail_url", ""), "views": post.get("total_views_count", 0) or 0, "likes": post.get("total_like_count", 0) or 0, "comments": post.get("total_comments_count", 0) or 0, "shares": post.get("shares_count", 0) or 0}
                next_url = m_res.get("paging", {}).get("next")
            except: break
    return sc_map

ig_map = get_ig_map() if (not active_refresh or active_refresh == "אינסטגרם" or not df_cached) else {}

with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
    for idx, item in enumerate(ITEMS):
        plat, url = item["platform"], get_full_url(item)
        if active_refresh and plat != active_refresh: continue
        if df_cached is not None and not active_refresh and current_df.loc[idx, "שם סרטון"] != "טוען נתונים...": continue

        if plat == "פייסבוק":
            try:
                res = requests.get(f"https://graph.facebook.com/v26.0/{item['id']}?fields=description,views,from%7Bname%7D,picture,video_insights.metric(post_video_likes_by_reaction_type,post_video_social_actions)&access_token={META_USER_TOKEN}").json()
                if "error" not in res:
                    likes, comments, shares = 0, 0, 0
                    for ins in res.get("video_insights", {}).get("data", []):
                        vals = ins.get("values", [{}])[0].get("value", {})
                        if ins.get("name") == "post_video_likes_by_reaction_type": likes = sum(vals.values())
                        elif ins.get("name") == "post_video_social_actions": comments, shares = vals.get("COMMENT", 0), vals.get("SHARE", 0)
                    updated = {"פלטפורמה": "פייסבוק", "שם משתמש": res.get("from", {}).get("name", "i24NEWS"), "תמונה": res.get("picture", ""), "שם סרטון": res.get("description") or "ללא כותרת", "קישור": url, "צפיות": res.get("views", 0) or 0, "לייקים": likes, "תגובות": comments, "שיתופים": shares}
                else: raise Exception()
            except: updated = {"פלטפורמה": "פייסבוק", "שם משתמש": "i24NEWS", "תמונה": "", "שם סרטון": "שגיאה בשליפת API", "קישור": url, "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0}
        elif plat == "אינסטגרם":
            matched = ig_map.get(item["id"])
            if matched: updated = {"פלטפורמה": "אינסטגרם", "שם משתמש": matched["username"], "תמונה": matched["thumbnail_url"], "שם סרטון": matched["caption"], "קישור": url, "צפיות": matched["views"], "לייקים": matched["likes"], "תגובות": matched["comments"], "שיתופים": matched["shares"]}
            else: updated = {"פלטפורמה": "אינסטגרם", "שם משתמש": "i24NEWS", "תמונה": "", "שם סרטון": "לא נמצא בפיד המקושר", "קישור": url, "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0}
        else:
            try:
                info = ydl.extract_info(url, download=False)
                updated = {"פלטפורמה": "טוויטר" if plat in ["טוויטר", "X (טוויטר)"] else plat, "שם משתמש": info.get("uploader") or info.get("channel") or info.get("uploader_id") or "לא ידוע", "תמונה": info.get("thumbnail", ""), "שם סרטון": info.get("description") or info.get("title") or "ללא כותרת", "קישור": url, "צפיות": info.get("view_count", 0) or 0, "לייקים": info.get("like_count", 0) or 0, "תגובות": info.get("comment_count", 0) or 0, "שיתופים": info.get("repost_count", 0) or info.get("share_count", 0) or 0}
            except: updated = {"פלטפורמה": "טוויטר" if plat in ["טוויטר", "X (טוויטר)"] else plat, "שם משתמש": "שגיאה בשליפה", "תמונה": "", "שם סרטון": "שגיאה בשליפה", "קישור": url, "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0}

        all_rows[idx] = updated
        current_df = pd.DataFrame(all_rows)
        for col in ["צפיות", "לייקים", "תגובות", "שיתופים"]:
            current_df[col] = pd.to_numeric(current_df[col], errors="coerce").fillna(0)
        current_df = current_df.sort_values(by=sort_by, ascending=sort_ascending)
        render_dashboard(current_df)

current_df.to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
