import os, re
import pandas as pd
import requests
import streamlit as st
import yt_dlp

st.set_page_config(page_title="MOFA - Data Extraction", page_icon="📊", layout="wide")

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
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">MOFA - Social Media Data Extraction Tool</div>', unsafe_allow_html=True)

META_USER_TOKEN = st.secrets.get("META_USER_TOKEN", "")

with st.sidebar:
    st.markdown("### ⚙️ הגדרות שליפה")
    platform = st.selectbox("בחר פלטפורמה:", ["יוטיוב", "טיקטוק", "טוויטר", "פייסבוק", "אינסטגרם"])
    
    st.markdown("---")
    
    # הצגת הודעה מותאמת אישית לפי הפלטפורמה שנבחרה
    if platform in ["טיקטוק", "טוויטר"]:
        st.warning("⚠️ **הכנס לינקים מלאים כולל שם משתמש ואכניס** (כל שורה לינק מלא).")
        placeholder_text = "https://www.tiktok.com/@username/video/123456...\nhttps://www.tiktok.com/@another_user/video/78910..."
    else:
        st.info("ℹ️ הכנס מזהי ID בלבד (כל שורה ID חדש).")
        placeholder_text = "ID1\nID2\nID3"

    ids_input = st.text_area("הזן נתונים לפי ההנחיות:", height=220, placeholder=placeholder_text)
    fetch_btn = st.button("שלוף נתונים", use_container_width=True, type="primary")

def get_full_url(plat, line):
    line = line.strip()
    if plat == "יוטיוב":
        return f"https://youtube.com/shorts/{line}"
    elif plat == "פייסבוק":
        return f"https://www.facebook.com/reel/{line}"
    elif plat == "אינסטגרם":
        return f"https://www.instagram.com/p/{line}"
    elif plat in ["טיקטוק", "טוויטר"]:
        # בטיקטוק וטוויטר המשתמש מכניס ישירות את הלינק המלא
        return line
    return line

def get_ig_map():
    if not META_USER_TOKEN: return {}
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
                    if m: 
                        sc_map[m.group(1)] = {
                            "username": ig["username"], 
                            "caption": post.get("caption") or "ללא כותרת", 
                            "thumbnail_url": post.get("thumbnail_url", ""), 
                            "views": post.get("total_views_count", 0) or 0, 
                            "likes": post.get("total_like_count", 0) or 0, 
                            "comments": post.get("total_comments_count", 0) or 0, 
                            "shares": post.get("shares_count", 0) or 0
                        }
                next_url = m_res.get("paging", {}).get("next")
            except: break
    return sc_map

metrics_placeholder, table_placeholder = st.empty(), st.empty()

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
        "פייסבוק": '<div style="text-align: center;"><i class="fa-brands fa-facebook" style="color: #1877f2; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">פייסבוק</span></div>',
        "אינסטגרם": '<div style="text-align: center;"><i class="fa-brands fa-instagram" style="color: #e4405f; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">אינסטגרם</span></div>'
    }

    for _, row in df.iterrows():
        plat, user, title, link = row["פלטפורמה"], row["שם משתמש"], row["שם סרטון"], row["קישור"]
        plat_display = icon_mapping.get(plat, f'<div style="text-align: center;">{plat}</div>')
        
        if title == "טוען נתונים...":
            thumb_tag = '<div class="skeleton skeleton-box"></div>'
            user_cell = '<div class="skeleton skeleton-text" style="width: 60%;"></div>'
            title_cell = '<div class="skeleton skeleton-text" style="width: 85%;"></div>'
            views, likes, comments, shares = *(['<div class="skeleton skeleton-text" style="width: 30px;"></div>'] * 4),
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

if not fetch_btn:
    st.info("👈 בחר פלטפורמה בסיידבר, הזן את הנתונים ולץ על **שלוף נתונים**.")
else:
    raw_lines = [line.strip() for line in ids_input.splitlines() if line.strip()]
    
    if not raw_lines:
        st.warning("נא להזין לפחות ערך אחד בתיבת הטקסט.")
    else:
        all_rows = []
        for line in raw_lines:
            url = get_full_url(platform, line)
            all_rows.append({
                "פלטפורמה": platform,
                "שם משתמש": "טוען...",
                "תמונה": "",
                "שם סרטון": "טוען נתונים...",
                "קישור": url,
                "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0
            })
        
        current_df = pd.DataFrame(all_rows)
        render_dashboard(current_df)

        ig_map = get_ig_map() if platform == "אינסטגרם" else {}

        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            for idx, line in enumerate(raw_lines):
                url = get_full_url(platform, line)
                updated = None

                if platform == "פייסבוק":
                    try:
                        res = requests.get(f"https://graph.facebook.com/v26.0/{line}?fields=description,views,from%7Bname%7D,picture,video_insights.metric(post_video_likes_by_reaction_type,post_video_social_actions)&access_token={META_USER_TOKEN}").json()
                        if "error" not in res:
                            likes, comments, shares = 0, 0, 0
                            for ins in res.get("video_insights", {}).get("data", []):
                                vals = ins.get("values", [{}])[0].get("value", {})
                                if ins.get("name") == "post_video_likes_by_reaction_type": likes = sum(vals.values())
                                elif ins.get("name") == "post_video_social_actions": comments, shares = vals.get("COMMENT", 0), vals.get("SHARE", 0)
                            updated = {"פלטפורמה": "פייסבוק", "שם משתמש": res.get("from", {}).get("name", "i24NEWS"), "תמונה": res.get("picture", ""), "שם סרטון": res.get("description") or "ללא כותרת", "קישור": url, "צפיות": res.get("views", 0) or 0, "לייקים": likes, "תגובות": comments, "שיתופים": shares}
                        else: raise Exception()
                    except:
                        updated = {"פלטפורמה": "פייסבוק", "שם משתמש": "i24NEWS", "תמונה": "", "שם סרטון": "שגיאה בשליפת API", "קישור": url, "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0}
                
                elif platform == "אינסטגרם":
                    matched = ig_map.get(line)
                    if matched:
                        updated = {"פלטפורמה": "אינסטגרם", "שם משתמש": matched["username"], "תמונה": matched["thumbnail_url"], "שם סרטון": matched["caption"], "קישור": url, "צפיות": matched["views"], "לייקים": matched["likes"], "תגובות": matched["comments"], "שיתופים": matched["shares"]}
                    else:
                        updated = {"פלטפורמה": "אינסטגרם", "שם משתמש": "i24NEWS", "תמונה": "", "שם סרטון": "לא נמצא בפיד המקושר", "קישור": url, "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0}
                
                else:
                    try:
                        info = ydl.extract_info(url, download=False)
                        updated = {
                            "פלטפורמה": platform,
                            "שם משתמש": info.get("uploader") or info.get("channel") or info.get("uploader_id") or "לא ידוע",
                            "תמונה": info.get("thumbnail", ""),
                            "שם סרטון": info.get("description") or info.get("title") or "ללא כותרת",
                            "קישור": url,
                            "צפיות": info.get("view_count", 0) or 0,
                            "לייקים": info.get("like_count", 0) or 0,
                            "תגובות": info.get("comment_count", 0) or 0,
                            "שיתופים": info.get("repost_count", 0) or info.get("share_count", 0) or 0
                        }
                    except:
                        updated = {
                            "פלטפורמה": platform,
                            "שם משתמש": "שגיאה בשליפה",
                            "תמונה": "",
                            "שם סרטון": "שגיאה בשליפה",
                            "קישור": url,
                            "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0
                        }

                all_rows[idx] = updated
                current_df = pd.DataFrame(all_rows)
                for col in ["צפיות", "לייקים", "תגובות", "שיתופים"]:
                    current_df[col] = pd.to_numeric(current_df[col], errors="coerce").fillna(0)
                render_dashboard(current_df)

        st.success("השליפה הסתיימה בהצלחה!")
