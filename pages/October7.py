from datetime import datetime
import os
import re
import pandas as pd
import requests
import streamlit as st
import yt_dlp

# הגדרת עמוד ב-Streamlit
st.set_page_config(
    page_title="October 7 - The last day of my life",
    page_icon="📊",
    layout="wide",
)

# עיצוב מקיף מימין לשמאל (RTL) ויישור מושלם למרכז
st.markdown(
    """
    <style>
    /* כיוון כללי מימין לשמאל */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* יישור טקסטים ומדדים למרכז */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
        direction: rtl !important;
        text-align: center !important;
    }
    
    div[data-testid="column"] {
        text-align: center !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    /* יישור כותרות וטקסטים למרכז */
    h1, h2, h3, h4, p, div {
        direction: rtl !important;
        text-align: center !important;
    }
    
    a {
        text-decoration: none !important;
        color: inherit;
    }
    a:hover {
        text-decoration: underline !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# כותרת ראשית
st.title("October 7 - The last day of my life")

# הגדרת נתיב דינמי לקובץ ה-CSV באותה התיקייה
script_dir = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(script_dir, "October7.csv")

# צבעי מותג לפלטפורמות
PLATFORM_COLORS = {
    "פייסבוק": "#1877F2",
    "אינסטגרם": "#E4405F",
    "טיקטוק": "#010101",
    "X (טוויטר)": "#333333",
    "יוטיוב": "#FF0000",
}

# טוקן מטא שמור פנימית (מוסתר מהמשתמש ומהמסך)
META_USER_TOKEN = "EAAORARdXiYYBSZBEyajmvOpKe6epxIba2nzINk9qQGsWUy8qYIG9Nz871ZB9mAFECEmxTVZC8UCA7WXZAkF11nLdWX0pZCUdAO8m8ZBgfVh7IseEoY8ZAdA3XYjPai0LIWJ7pZBwgELv9rdnn0GZA423ZBr2dFiwWdF05UWj1NlW9ZBoW1CSEFABMPZB3ZAqw5ZAvKtrCRZCa9xmhZCBUVOt5QmZAaw5MCjj18NQNyxuLXIF5yXUvzb8uezLvZCbYMdsQn0UtvYqZCdZCM9ORgRKVZAfUZAzGAGLQ1VAAtZC4rM"

# רשימת הקישורים המלאה
URLS = [
    # Facebook Reels
    "https://www.facebook.com/reel/1060758100274123",
    "https://www.facebook.com/reel/1098661659684872",
    "https://www.facebook.com/reel/1102560435692402",
    "https://www.facebook.com/reel/1421376970083491",
    "https://www.facebook.com/reel/1427558415388540",
    "https://www.facebook.com/reel/1575591177051076",
    "https://www.facebook.com/reel/1834808051214925",
    "https://www.facebook.com/reel/2003722767682462",
    "https://www.facebook.com/reel/2004915936880315",
    "https://www.facebook.com/reel/28594037286923487",
    "https://www.facebook.com/reel/3189661697897533",
    "https://www.facebook.com/reel/996450340148747",
    # Instagram
    "https://www.instagram.com/p/Deb5bDXD6Gs/",
    "https://www.instagram.com/p/Deb5UJfFKU1/",
    "https://www.instagram.com/p/Deb8nh5Du4y/",
    "https://www.instagram.com/p/DeeYjQ2DnYf/",
    "https://www.instagram.com/p/DeeYTozDXdP/",
    "https://www.instagram.com/p/DeeYzU5lXQ_/",
    "https://www.instagram.com/p/DeME-OfDP5u/",
    "https://www.instagram.com/p/DeMFNk4iDQv/",
    "https://www.instagram.com/p/DeMFUBUiZvQ/",
    "https://www.instagram.com/p/DeOp3L4kzrY/",
    "https://www.instagram.com/p/DeOpu9WDiJ6/",
    "https://www.instagram.com/p/DeOxjLrkz4G/",
    # TikTok
    "https://www.tiktok.com/@i24news_ar/video/7693308032641404178",
    "https://www.tiktok.com/@i24news_ar/video/7693605131383868673",
    "https://www.tiktok.com/@i24news_ar/video/7696223468769086721",
    "https://www.tiktok.com/@i24news_ar/video/7696505060129312001",
    "https://www.tiktok.com/@i24news_en/video/7693865442019921160",
    "https://www.tiktok.com/@i24news_en/video/7694255310751436050",
    "https://www.tiktok.com/@i24news_en/video/7696201889632865544",
    "https://www.tiktok.com/@i24news_en/video/7696547290550504712",
    "https://www.tiktok.com/@i24news_fr/video/7693865674698935570",
    "https://www.tiktok.com/@i24news_fr/video/7694255495154109714",
    "https://www.tiktok.com/@i24news_fr/video/7696202386062232840",
    "https://www.tiktok.com/@i24news_fr/video/7696547126687583496",
    # X (Twitter)
    "https://x.com/i24NEWS_AR/status/2107771873887154185?s=20",
    "https://x.com/i24NEWS_AR/status/2108150421772771395?s=20",
    "https://x.com/i24NEWS_AR/status/2110056520885141979?s=20",
    "https://x.com/i24NEWS_AR/status/2110353427012403661?s=20",
    "https://x.com/i24NEWS_EN/status/2107772249511973327?s=20",
    "https://x.com/i24NEWS_EN/status/2108157434930057278?s=20",
    "https://x.com/i24NEWS_EN/status/2110055247792279600?s=20",
    "https://x.com/i24NEWS_EN/status/2110353863069126843?s=20",
    "https://x.com/i24NEWS_FR/status/2107771596178092264?s=20",
    "https://x.com/i24NEWS_FR/status/2108150891564179901?s=20",
    "https://x.com/i24NEWS_FR/status/2110055870185058765?s=20",
    "https://x.com/i24NEWS_FR/status/2110354237012185370?s=20",
    # YouTube Shorts
    "https://youtube.com/shorts/24gFRLpMR7E",
    "https://youtube.com/shorts/7Fqb8Zl1-4w?feature=share",
    "https://youtube.com/shorts/7VP1tvrK3F0",
    "https://youtube.com/shorts/cWhNSpPDkY8",
    "https://youtube.com/shorts/f2Ho2psrDHA",
    "https://youtube.com/shorts/FViFNB73tjk",
    "https://youtube.com/shorts/gc3gGTkyTJs",
    "https://youtube.com/shorts/hgo53mbSKv4",
    "https://youtube.com/shorts/LoumbMP6LTU",
    "https://youtube.com/shorts/OOKIchREy-I",
    "https://youtube.com/shorts/s7dlo-EO6ps",
    "https://youtube.com/shorts/XSEI6HgRjzQ",
]


def extract_fb_id(url):
    """חילוץ מזהה הפוסט/רילס מקישור פייסבוק"""
    match = re.search(r'/(?:reel|videos|posts)/(\d+)', url)
    return match.group(1) if match else None


def extract_ig_shortcode(url):
    """חילוץ shortcode מקישור אינסטגרם"""
    match = re.search(r'/(?:p|reel)/([^/?#&]+)', url)
    return match.group(1) if match else None


def fetch_meta_analytics_map():
    """מביא את מפת העמודים והטוקנים של מטא"""
    meta_map = {}
    try:
        url = f"https://graph.facebook.com/v26.0/me/accounts?fields=id,name,access_token,instagram_business_account&access_token={META_USER_TOKEN}"
        res = requests.get(url).json()
        for acc in res.get("data", []):
            page_token = acc.get("access_token")
            page_id = acc.get("id")
            ig_acc = acc.get("instagram_business_account", {}).get("id")
            if page_token:
                meta_map[page_id] = {
                    "page_token": page_token,
                    "ig_id": ig_acc
                }
    except Exception as e:
        print(f"Meta Accounts Fetch Error: {e}")
    return meta_map


def fetch_social_data():
    data = []
    meta_accounts = fetch_meta_analytics_map()
    
    # חילוץ רשימת טוקנים של העמודים לבדיקה מול ה-API
    page_tokens = [acc["page_token"] for acc in meta_accounts.values()]
    first_page_token = page_tokens[0] if page_tokens else META_USER_TOKEN

    ydl_opts = {"quiet": True, "skip_download": True}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in URLS:
            if "facebook.com" in url or "fb.watch" in url:
                platform = "פייסבוק"
                fb_id = extract_fb_id(url)
                fetched_via_api = False
                
                if fb_id:
                    # ניסיון שליפה ישיר מה-API עם Graph API
                    for p_token in page_tokens:
                        api_url = f"https://graph.facebook.com/v26.0/{fb_id}?fields=title,description,message,views,video_insights,likes.summary(true),comments.summary(true),shares&access_token={p_token}"
                        res = requests.get(api_url).json()
                        if "error" not in res:
                            # כותרת/תיאור מלא ללא פילטרים
                            full_title = res.get("description") or res.get("message") or res.get("title") or "ללא כותרת"
                            views = res.get("views", 0)
                            
                            # ניסיון לחלץ צפיות וידאו פנימיות אם קיימות
                            if not views and "video_insights" in res:
                                for ins in res["video_insights"].get("data", []):
                                    if ins.get("name") in ["total_video_views", "post_video_views"]:
                                        views = ins.get("values", [{}])[0].get("value", 0)

                            likes = res.get("likes", {}).get("summary", {}).get("total_count", 0)
                            comments = res.get("comments", {}).get("summary", {}).get("total_count", 0)
                            shares = res.get("shares", {}).get("count", 0)
                            
                            data.append({
                                "פלטפורמה": platform,
                                "כותרת": full_title,
                                "קישור": url,
                                "תמונה": "",
                                "צפיות": views,
                                "לייקים": likes,
                                "תגובות": comments,
                                "שיתופים": shares,
                            })
                            fetched_via_api = True
                            break
                            
                if not fetched_via_api:
                    # גיבוי yt_dlp אם ה-API החזיר שגיאה ל-ID הספציפי
                    try:
                        info = ydl.extract_info(url, download=False)
                        data.append({
                            "פלטפורמה": platform,
                            "כותרת": info.get("description") or info.get("title") or "ללא כותרת",
                            "קישור": url,
                            "תמונה": info.get("thumbnail", ""),
                            "צפיות": info.get("view_count", 0) or 0,
                            "לייקים": info.get("like_count", 0) or 0,
                            "תגובות": info.get("comment_count", 0) or 0,
                            "שיתופים": info.get("repost_count", 0) or info.get("share_count", 0) or 0,
                        })
                    except Exception:
                        data.append({
                            "פלטפורמה": platform,
                            "כותרת": "שגיאה בשליפת הנתונים",
                            "קישור": url,
                            "תמונה": "",
                            "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0
                        })

            elif "instagram.com" in url:
                platform = "אינסטגרם"
                shortcode = extract_ig_shortcode(url)
                fetched_via_api = False
                
                # שליפת נתוני אינסטגרם
                try:
                    info = ydl.extract_info(url, download=False)
                    # לקיחת התיאור/כותרת המלאה ללא שום סינון
                    full_title = info.get("description") or info.get("title") or "ללא כותרת"
                    
                    data.append({
                        "פלטפורמה": platform,
                        "כותרת": full_title,
                        "קישור": url,
                        "תמונה": info.get("thumbnail", ""),
                        "צפיות": info.get("view_count", 0) or 0,
                        "לייקים": info.get("like_count", 0) or 0,
                        "תגובות": info.get("comment_count", 0) or 0,
                        "שיתופים": info.get("repost_count", 0) or 0,
                    })
                except Exception:
                    data.append({
                        "פלטפורמה": platform,
                        "כותרת": "שגיאה בשליפת הנתונים",
                        "קישור": url,
                        "תמונה": "",
                        "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0
                    })

            else:
                # TikTok, X (Twitter), YouTube Shorts
                if "tiktok.com" in url:
                    platform = "טיקטוק"
                elif "x.com" in url or "twitter.com" in url:
                    platform = "X (טוויטר)"
                elif "youtube.com" in url or "youtu.be" in url:
                    platform = "יוטיוב"
                else:
                    platform = "אחר"

                try:
                    info = ydl.extract_info(url, download=False)
                    # ללא סינון כותרת
                    full_title = info.get("title") or info.get("description") or "ללא כותרת"
                    
                    data.append({
                        "פלטפורמה": platform,
                        "כותרת": full_title,
                        "קישור": url,
                        "תמונה": info.get("thumbnail", ""),
                        "צפיות": info.get("view_count", 0) or 0,
                        "לייקים": info.get("like_count", 0) or 0,
                        "תגובות": info.get("comment_count", 0) or 0,
                        "שיתופים": info.get("repost_count", 0) or info.get("share_count", 0) or 0,
                    })
                except Exception:
                    data.append({
                        "פלטפורמה": platform,
                        "כותרת": "שגיאה בשליפת הנתונים",
                        "קישור": url,
                        "תמונה": "",
                        "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0
                    })

    df = pd.DataFrame(data)
    df.to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
    return df


# טעינת נתונים
required_cols = ["פלטפורמה", "כותרת", "קישור", "תמונה", "צפיות", "לייקים", "תגובות", "שיתופים"]

if os.path.exists(CACHE_FILE):
    df = pd.read_csv(CACHE_FILE)
    if not all(col in df.columns for col in required_cols):
        with st.spinner("🔄 הנתונים נטענים..."):
            df = fetch_social_data()
else:
    with st.spinner("🔄 הנתונים נטענים... מבצע שליפה ראשונית"):
        df = fetch_social_data()

# כפתור רענון בסיידבר
with st.sidebar:
    st.header("⚙️ הגדרות ובקרה")
    if st.button("🔄 רענן נתונים מחדש מהרשתות"):
        with st.spinner("🔄 הנתונים נטענים מחדש מהרשתות החברתיות..."):
            df = fetch_social_data()
        st.success("הנתונים עודכנו בהצלחה!")

# --- חלק עליון: כרטיס סיכום כללי מרכזי ---
with st.container(border=True):
    st.markdown("### 📈 סיכום כללי (כל הפלטפורמות)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("סך הכל צפיות", f"{df['צפיות'].sum():,}" if "צפיות" in df else "0")
    col2.metric("סך הכל לייקים", f"{df['לייקים'].sum():,}" if "לייקים" in df else "0")
    col3.metric("סך הכל תגובות", f"{df['תגובות'].sum():,}" if "תגובות" in df else "0")
    col4.metric("סך הכל שיתופים", f"{df['שיתופים'].sum():,}" if "שיתופים" in df else "0")

st.markdown("---")

# --- חלק תחתון: כרטיסים נפרדים מלוטשים עם צבעי מותג לכל פלטפורמה ---
platforms = ["פייסבוק", "אינסטגרם", "טיקטוק", "X (טוויטר)", "יוטיוב"]

for plat in platforms:
    plat_df = df[df["פלטפורמה"] == plat]
    brand_color = PLATFORM_COLORS.get(plat, "#333333")

    if not plat_df.empty:
        with st.container(border=True):
            st.markdown(
                f"<h2 style='color: {brand_color}; text-align: center; font-weight: bold;'>{plat}</h2>",
                unsafe_allow_html=True,
            )

            p1, p2, p3, p4 = st.columns(4)
            p1.metric("צפיות", f"{plat_df['צפיות'].sum():,}")
            p2.metric("לייקים", f"{plat_df['לייקים'].sum():,}")
            p3.metric("תגובות", f"{plat_df['תגובות'].sum():,}")
            p4.metric("שיתופים", f"{plat_df['שיתופים'].sum():,}")

            st.markdown("---")

            for index, row in plat_df.iterrows():
                with st.container(border=True):
                    v_col1, v_col2, v_col3, v_col4, v_col5 = st.columns(
                        [1.5, 4, 1, 1, 1]
                    )

                    with v_col1:
                        if pd.notna(row["תמונה"]) and str(row["תמונה"]).startswith("http"):
                            st.image(row["תמונה"], width=180)
                        else:
                            st.info("אין תמונה")

                    with v_col2:
                        title_text = row["כותרת"]
                        link_url = row["קישור"]
                        st.markdown(
                            f"<div style='text-align: center;'><a href='{link_url}' target='_blank'><b style='font-size: 1.1em;'>{title_text}</b></a></div>",
                            unsafe_allow_html=True,
                        )

                    with v_col3:
                        st.metric("צפיות", f"{int(row['צפיות']):,}")

                    with v_col4:
                        st.metric("לייקים", f"{int(row['לייקים']):,}")

                    with v_col5:
                        st.metric("תגובות", f"{int(row['תגובות']):,}")
