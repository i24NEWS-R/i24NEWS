import os, re
import datetime
import io
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
    
    ig_start_date = None
    if platform == "אינסטגרם":
        st.markdown("---")
        ig_start_date = st.date_input("📅 שלוף פוסטים מתאריך (כולל):", value=datetime.date(datetime.date.today().year, 5, 10))
    
    st.markdown("---")
    
    if platform in ["טיקטוק", "טוויטר"]:
        st.warning("⚠️ **הכנס לינקים מלאים כולל שם משתמש ואכניס** (כל שורה לינק מלא).")
        placeholder_text = "https://www.tiktok.com/@username/video/123456...\nhttps://www.tiktok.com/@another_user/video/78910..."
    else:
        st.info("ℹ️ הכנס מזהי ID בלבד (כל שורה ID חדש).")
        placeholder_text = "ID1\nID2\nID3"

    ids_input = st.text_area("הזן נתונים לפי ההנחיות:", height=220, placeholder=placeholder_text)
    fetch_btn = st.button("שלוף נתונים", use_container_width=True, type="primary")
    
    download_placeholder = st.empty()

def get_full_url(plat, line):
    line = line.strip()
    if plat == "יוטיוב":
        return f"https://youtube.com/shorts/{line}"
    elif plat == "פייסבוק":
        return f"https://www.facebook.com/reel/{line}"
    elif plat == "אינסטגרם":
        return f"https://www.instagram.com/p/{line}"
    elif plat in ["טיקטוק", "טוויטר"]:
        return line
    return line

def format_date(date_str):
    if not date_str:
        return ""
    try:
        s = str(date_str)
        if "T" in s:
            s = s.split("T")[0]
        
        if "-" in s and len(s) >= 10:
            parts = s[:10].split("-")
            if len(parts) == 3:
                y, m, d = parts
                return f"{d}/{m}/{y}"
        
        if len(s) == 8 and s.isdigit():
            y, m, d = s[:4], s[4:6], s[6:]
            return f"{d}/{m}/{y}"
            
        dt = pd.to_datetime(date_str, errors='coerce')
        if pd.notna(dt):
            return dt.strftime("%d/%m/%Y")
    except:
        pass
    return str(date_str)

def get_ig_map(target_date):
    if not META_USER_TOKEN: return {}
    try:
        res = requests.get(f"https://graph.facebook.com/v26.0/me/accounts?fields=instagram_business_account{{id,username}},name&access_token={META_USER_TOKEN}").json()
        ig_accounts = [{"id": a["instagram_business_account"]["id"], "username": a["instagram_business_account"].get("username", "i24NEWS")} for a in res.get("data", []) if a.get("instagram_business_account")]
    except: return {}
    
    sc_map = {}
    for ig in ig_accounts:
        next_url = f"https://graph.facebook.com/v26.0/{ig['id']}/media?fields=id,permalink,caption,thumbnail_url,timestamp,total_views_count,total_like_count,total_comments_count,shares_count&limit=100&access_token={META_USER_TOKEN}"
        
        stop_fetching = False
        while next_url and not stop_fetching:
            try:
                m_res = requests.get(next_url).json()
                posts = m_res.get("data", [])
                if not posts: break
                
                for post in posts:
                    ts_str = post.get("timestamp", "")
                    post_date = None
                    if ts_str:
                        try:
                            post_date = pd.to_datetime(ts_str).date()
                        except:
                            pass
                    
                    if target_date and post_date and post_date < target_date:
                        stop_fetching = True
                        break
                    
                    if not target_date or (post_date and post_date >= target_date):
                        m = re.search(r"/(?:p|reel)/([^/]+)", post.get("permalink", ""))
                        if m: 
                            sc_map[m.group(1)] = {
                                "username": ig["username"], 
                                "caption": post.get("caption") or "ללא כותרת", 
                                "thumbnail_url": post.get("thumbnail_url", ""), 
                                "date": format_date(ts_str),
                                "views": post.get("total_views_count", 0) or 0, 
                                "likes": post.get("total_like_count", 0) or 0, 
                                "comments": post.get("total_comments_count", 0) or 0, 
                                "shares": post.get("shares_count", 0) or 0
                            }
                
                if stop_fetching:
                    break
                    
                next_url = m_res.get("paging", {}).get("next")
            except:
                break
    return sc_map

def fetch_single_item(plat, line, url, ig_map):
    if plat == "פייסבוק":
        try:
            res = requests.get(f"https://graph.facebook.com/v26.0/{line}?fields=description,views,created_time,from%7Bname%7D,picture,video_insights.metric(post_video_likes_by_reaction_type,post_video_social_actions)&access_token={META_USER_TOKEN}").json()
            if "error" not in res:
                likes, comments, shares = 0, 0, 0
                for ins in res.get("video_insights", {}).get("data", []):
                    vals = ins.get("values", [{}])[0].get("value", {})
                    if ins.get("name") == "post_video_likes_by_reaction_type": likes = sum(vals.values())
                    elif ins.get("name") == "post_video_social_actions": comments, shares = vals.get("COMMENT", 0), vals.get("SHARE", 0)
                
                return {
                    "פלטפורמה": "פייסבוק", 
                    "שם משתמש": res.get("from", {}).get("name", "i24NEWS"), 
                    "תמונה": res.get("picture", ""), 
                    "שם סרטון": res.get("description") or "ללא כותרת", 
                    "תאריך": format_date(res.get("created_time", "")),
                    "קישור": url, 
                    "צפיות": res.get("views", 0) or 0, 
                    "לייקים": likes, 
                    "תגובות": comments, 
                    "שיתופים": shares,
                    "מזהה_מקור": line
                }
            else: raise Exception()
        except:
            return {"פלטפורמה": "פייסבוק", "שם משתמש": "i24NEWS", "תמונה": "", "שם סרטון": "שגיאה בשליפת API", "תאריך": "", "קישור": url, "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0, "מזהה_מקור": line}
            
    elif plat == "אינסטגרם":
        matched = ig_map.get(line)
        if matched:
            return {
                "פלטפורמה": "אינסטגרם", 
                "שם משתמש": matched["username"], 
                "תמונה": matched["thumbnail_url"], 
                "שם סרטון": matched["caption"], 
                "תאריך": matched["date"],
                "קישור": url, 
                "צפיות": matched["views"], 
                "לייקים": matched["likes"], 
                "תגובות": matched["comments"], 
                "שיתופים": matched["shares"],
                "מזהה_מקור": line
            }
        else:
            return {"פלטפורמה": "אינסטגרם", "שם משתמש": "i24NEWS", "תמונה": "", "שם סרטון": "לא נמצא (ייתכן וישן ממועד ההתחלה)", "תאריך": "", "קישור": url, "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0, "מזהה_מקור": line}
            
    else:
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
                info = ydl.extract_info(url, download=False)
            raw_date = info.get("upload_date") or info.get("release_date") or ""
            if not raw_date and info.get("timestamp"):
                raw_date = datetime.datetime.fromtimestamp(info.get("timestamp")).strftime("%Y%m%d")

            return {
                "פלטפורמה": plat,
                "שם משתמש": info.get("uploader") or info.get("channel") or info.get("uploader_id") or "לא ידוע",
                "תמונה": info.get("thumbnail", ""),
                "שם סרטון": info.get("description") or info.get("title") or "ללא כותרת",
                "תאריך": format_date(raw_date),
                "קישור": url,
                "צפיות": info.get("view_count", 0) or 0,
                "לייקים": info.get("like_count", 0) or 0,
                "תגובות": info.get("comment_count", 0) or 0,
                "שיתופים": info.get("repost_count", 0) or info.get("share_count", 0) or 0,
                "מזהה_מקור": line
            }
        except:
            return {
                "פלטפורמה": plat,
                "שם משתמש": "שגיאה בשליפה",
                "תמונה": "",
                "שם סרטון": "שגיאה בשליפה",
                "תאריך": "",
                "קישור": url,
                "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0,
                "מזהה_מקור": line
            }

if "df_data" not in st.session_state:
    st.session_state.df_data = None

if fetch_btn:
    raw_lines = [line.strip() for line in ids_input.splitlines() if line.strip()]
    if not raw_lines:
        st.warning("נא להזין לפחות ערך אחד בתיבת הטקסט.")
    else:
        initial_rows = []
        for line in raw_lines:
            url = get_full_url(platform, line)
            initial_rows.append({
                "פלטפורמה": platform,
                "שם משתמש": "טוען...",
                "תמונה": "",
                "שם סרטון": "טוען נתונים...",
                "תאריך": "",
                "קישור": url,
                "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0,
                "מזהה_מקור": line
            })
        st.session_state.df_data = pd.DataFrame(initial_rows)

metrics_placeholder = st.empty()
table_placeholder = st.container()

if st.session_state.df_data is not None and not st.session_state.df_data.empty:
    df = st.session_state.df_data
    
    if fetch_btn and (df["שם סרטון"] == "טוען נתונים...").any():
        raw_lines = df["מזהה_מקור"].tolist()
        ig_map = get_ig_map(ig_start_date) if platform == "אינסטגרם" else {}
        
        for idx, line in enumerate(raw_lines):
            url = get_full_url(platform, line)
            updated = fetch_single_item(platform, line, url, ig_map)
            st.session_state.df_data.iloc[idx] = updated
            df = st.session_state.df_data
            
        st.success("השליפה הסתיימה בהצלחה!")

    # הצגת מטריקות ראשיות
    cols_m = metrics_placeholder.columns(4)
    for col, title, key in zip(cols_m, ["סך הכל צפיות", "סך הכל לייקים", "סך הכל תגובות", "סך הכל שיתופים"], ["צפיות", "לייקים", "תגובות", "שיתופים"]):
        numeric_vals = pd.to_numeric(df[key], errors="coerce").fillna(0)
        col.markdown(f'<div class="metric-card"><div class="metric-title">{title}</div><div class="metric-value">{int(numeric_vals.sum()):,}</div></div>', unsafe_allow_html=True)

    with table_placeholder:
        st.markdown("### 📋 תוצאות השליפה")
        
        # שורת בקרת מיון
        col_title, col_sort = st.columns([2, 2])
        with col_sort:
            sort_option = st.selectbox(
                "מיון טבלה לפי:", 
                ["ללא מיון (סדר מקורי)", "צפיות (מהגבוה לנמוך)", "לייקים (מהגבוה לנמוך)", "תגובות (מהגבוה לנמוך)", "שיתופים (מהגבוה לנמוך)"],
                key="table_sort_select"
            )

        # ביצוע מיון ל-DataFrame המוצג בלבד מבלי לשבש את האינדקסים המקוריים
        display_df = df.copy()
        if sort_option == "צפיות (מהגבוה לנמוך)":
            display_df["צפיות_num"] = pd.to_numeric(display_df["צפיות"], errors="coerce").fillna(0)
            display_df = display_df.sort_values(by="צפיות_num", ascending=False).drop(columns=["צפיות_num"])
        elif sort_option == "לייקים (מהגבוה לנמוך)":
            display_df["לייקים_num"] = pd.to_numeric(display_df["לייקים"], errors="coerce").fillna(0)
            display_df = display_df.sort_values(by="לייקים_num", ascending=False).drop(columns=["לייקים_num"])
        elif sort_option == "תגובות (מהגבוה לנמוך)":
            display_df["תגובות_num"] = pd.to_numeric(display_df["תגובות"], errors="coerce").fillna(0)
            display_df = display_df.sort_values(by="תגובות_num", ascending=False).drop(columns=["תגובות_num"])
        elif sort_option == "שיתופים (מהגבוה לנמוך)":
            display_df["שיתופים_num"] = pd.to_numeric(display_df["שיתופים"], errors="coerce").fillna(0)
            display_df = display_df.sort_values(by="שיתופים_num", ascending=False).drop(columns=["שיתופים_num"])

        # כותרות הטבלה
        header_cols = st.columns([1, 1.5, 0.6, 4.4, 1.2, 0.8, 0.8, 0.8, 0.8, 0.6])
        headers = ["פלטפורמה", "משתמש", "תמונה", "כותרת / סרטון", "תאריך", "צפיות", "לייקים", "תגובות", "שיתופים", "פעולה"]
        for hc, h in zip(header_cols, headers):
            hc.markdown(f"**{h}**")
        st.markdown("---")

        # אייקונים רשמיים של FontAwesome כמו שביקשת
        icon_mapping = {
            "יוטיוב": '<div style="text-align: center;"><i class="fa-brands fa-youtube" style="color: #ff0000; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">יוטיוב</span></div>',
            "טיקטוק": '<div style="text-align: center;"><i class="fa-brands fa-tiktok" style="font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">טיקטוק</span></div>',
            "טוויטר": '<div style="text-align: center;"><i class="fa-brands fa-twitter" style="color: #1da1f2; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">טוויטר</span></div>',
            "פייסבוק": '<div style="text-align: center;"><i class="fa-brands fa-facebook" style="color: #1877f2; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">פייסבוק</span></div>',
            "אינסטגרם": '<div style="text-align: center;"><i class="fa-brands fa-instagram" style="color: #e4405f; font-size: 1.2rem;"></i><br><span style="font-size: 0.8rem; color: #334155;">אינסטגרם</span></div>'
        }

        ig_map_global = get_ig_map(ig_start_date) if platform == "אינסטגרם" else {}

        for original_idx, row in display_df.iterrows():
            r_cols = st.columns([1, 1.5, 0.6, 4.4, 1.2, 0.8, 0.8, 0.8, 0.8, 0.6])
            
            plat = row["פלטפורמה"]
            user = row["שם משתמש"]
            thumb = row["תמונה"]
            title = row["שם סרטון"]
            link = row["קישור"]
            date_val = row["תאריך"]
            
            # הצגת האייקון הרשמי המעוצב באמצעות HTML
            r_cols[0].markdown(icon_mapping.get(plat, f'<div style="text-align: center;">{plat}</div>'), unsafe_allow_html=True)
            r_cols[1].write(user if user != "טוען..." else "⏳ טוען...")
            
            if pd.notna(thumb) and str(thumb).startswith("http"):
                r_cols[2].image(thumb, width=32)
            else:
                r_cols[2].write("-")
                
            if title == "טוען נתונים...":
                r_cols[3].write("⏳ טוען נתונים...")
            else:
                r_cols[3].markdown(f'<a href="{link}" target="_blank" class="video-link">{title}</a>', unsafe_allow_html=True)
                
            r_cols[4].write(date_val if pd.notna(date_val) else "")
            r_cols[5].write(f"{int(pd.to_numeric(row['צפיות'], errors='coerce') or 0):,}")
            r_cols[6].write(f"{int(pd.to_numeric(row['לייקים'], errors='coerce') or 0):,}")
            r_cols[7].write(f"{int(pd.to_numeric(row['תגובות'], errors='coerce') or 0):,}")
            r_cols[8].write(f"{int(pd.to_numeric(row['שיתופים'], errors='coerce') or 0):,}")
            
            # לחצן רענון לשורה הספציפית לפי האינדקס האמיתי שלה בסטייט
            if r_cols[9].button("🔄", key=f"refresh_row_{original_idx}", help="רענן שורה זו"):
                with st.spinner("מעדכן..."):
                    line_id = row.get("מזהה_מקור", "")
                    updated_row = fetch_single_item(plat, line_id, link, ig_map_global)
                    st.session_state.df_data.iloc[original_idx] = updated_row
                    st.rerun()

    # ייצוא לאקסל
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        export_df = st.session_state.df_data.drop(columns=["מזהה_מקור"], errors="ignore")
        export_df.to_excel(writer, index=False, sheet_name='MOFA Data')
    excel_data = buffer.getvalue()

    download_placeholder.download_button(
        label="📥 ייצא קובץ Excel",
        data=excel_data,
        file_name="mofa_extracted_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

else:
    st.info("👈 בחר פלטפורמה בסיידבר, הזן את הנתונים ולץ על **שלוף נתונים**.")
