import os, re, requests, pandas as pd, streamlit as st, yt_dlp

st.set_page_config(page_title="October 7", page_icon="📊", layout="wide")
st.markdown("<style>html, body { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)

st.title("October 7 - The last day of my life")

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "October7.csv")
META_USER_TOKEN = "EAAORARdXiYYBSZBEyajmvOpKe6epxIba2nzINk9qQGsWUy8qYIG9Nz871ZB9mAFECEmxTVZC8UCA7WXZAkF11nLdWX0pZCUdAO8m8ZBgfVh7IseEoY8ZAdA3XYjPai0LIWJ7pZBwgELv9rdnn0GZA423ZBr2dFiwWdF05UWj1NlW9ZBoW1CSEFABMPZB3ZAqw5ZAvKtrCRZCa9xmhZCBUVOt5QmZAaw5MCjj18NQNyxuLXIF5yXUvzb8uezLvZCbYMdsQn0UtvYqZCdZCM9ORgRKVZAfUZAzGAGLQ1VAAtZC4rM"

URLS = [
    # Facebook Reels
    "https://www.facebook.com/reel/1060758100274123", "https://www.facebook.com/reel/1098661659684872",
    "https://www.facebook.com/reel/1102560435692402", "https://www.facebook.com/reel/1421376970083491",
    "https://www.facebook.com/reel/1427558415388540", "https://www.facebook.com/reel/1575591177051076",
    "https://www.facebook.com/reel/1834808051214925", "https://www.facebook.com/reel/2003722767682462",
    "https://www.facebook.com/reel/2004915936880315", "https://www.facebook.com/reel/28594037286923487",
    "https://www.facebook.com/reel/3189661697897533", "https://www.facebook.com/reel/996450340148747",
    # Instagram
    "https://www.instagram.com/p/Deb5bDXD6Gs/", "https://www.instagram.com/p/Deb5UJfFKU1/",
    "https://www.instagram.com/p/Deb8nh5Du4y/", "https://www.instagram.com/p/DeeYjQ2DnYf/",
    "https://www.instagram.com/p/DeeYTozDXdP/", "https://www.instagram.com/p/DeeYzU5lXQ_/",
    "https://www.instagram.com/p/DeME-OfDP5u/", "https://www.instagram.com/p/DeMFNk4iDQv/",
    "https://www.instagram.com/p/DeMFUBUiZvQ/", "https://www.instagram.com/p/DeOp3L4kzrY/",
    "https://www.instagram.com/p/DeOpu9WDiJ6/", "https://www.instagram.com/p/DeOxjLrkz4G/",
    # TikTok
    "https://www.tiktok.com/@i24news_ar/video/7693308032641404178", "https://www.tiktok.com/@i24news_ar/video/7693605131383868673",
    "https://www.tiktok.com/@i24news_ar/video/7696223468769086721", "https://www.tiktok.com/@i24news_ar/video/7696505060129312001",
    "https://www.tiktok.com/@i24news_en/video/7693865442019921160", "https://www.tiktok.com/@i24news_en/video/7694255310751436050",
    "https://www.tiktok.com/@i24news_en/video/7696201889632865544", "https://www.tiktok.com/@i24news_en/video/7696547290550504712",
    "https://www.tiktok.com/@i24news_fr/video/7693865674698935570", "https://www.tiktok.com/@i24news_fr/video/7694255495154109714",
    "https://www.tiktok.com/@i24news_fr/video/7696202386062232840", "https://www.tiktok.com/@i24news_fr/video/7696547126687583496",
    # X (Twitter)
    "https://x.com/i24NEWS_AR/status/2107771873887154185?s=20", "https://x.com/i24NEWS_AR/status/2108150421772771395?s=20",
    "https://x.com/i24NEWS_AR/status/2110056520885141979?s=20", "https://x.com/i24NEWS_AR/status/2110353427012403661?s=20",
    "https://x.com/i24NEWS_EN/status/2107772249511973327?s=20", "https://x.com/i24NEWS_EN/status/2108157434930057278?s=20",
    "https://x.com/i24NEWS_EN/status/2110055247792279600?s=20", "https://x.com/i24NEWS_EN/status/2110353863069126843?s=20",
    "https://x.com/i24NEWS_FR/status/2107771596178092264?s=20", "https://x.com/i24NEWS_FR/status/2108150891564179901?s=20",
    "https://x.com/i24NEWS_FR/status/2110055870185058765?s=20", "https://x.com/i24NEWS_FR/status/2110354237012185370?s=20",
    # YouTube Shorts
    "https://youtube.com/shorts/24gFRLpMR7E", "https://youtube.com/shorts/7Fqb8Zl1-4w?feature=share",
    "https://youtube.com/shorts/7VP1tvrK3F0", "https://youtube.com/shorts/cWhNSpPDkY8",
    "https://youtube.com/shorts/f2Ho2psrDHA", "https://youtube.com/shorts/FViFNB73tjk",
    "https://youtube.com/shorts/gc3gGTkyTJs", "https://youtube.com/shorts/hgo53mbSKv4",
    "https://youtube.com/shorts/LoumbMP6LTU", "https://youtube.com/shorts/OOKIchREy-I",
    "https://youtube.com/shorts/s7dlo-EO6ps", "https://youtube.com/shorts/XSEI6HgRjzQ"
]

def get_meta_auth_data():
    """שולף את כל העמודים והטוקנים המנוהלים מהטוקן הראשי"""
    pages = []
    ig_accounts = {}
    try:
        url = f"https://graph.facebook.com/v26.0/me/accounts?fields=id,name,access_token,instagram_business_account&access_token={META_USER_TOKEN}"
        res = requests.get(url).json()
        for acc in res.get("data", []):
            p_token = acc.get("access_token")
            p_id = acc.get("id")
            p_name = acc.get("name", "עמוד i24NEWS")
            pages.append({"id": p_id, "token": p_token, "name": p_name})
            
            ig = acc.get("instagram_business_account")
            if ig:
                ig_id = ig.get("id")
                ig_accounts[ig_id] = {"token": p_token, "name": p_name}
    except Exception as e:
        print(f"Meta Auth Error: {e}")
    return pages, ig_accounts

def fetch_social_data():
    data = []
    meta_pages, ig_accounts = get_meta_auth_data()
    
    # איסוף מראש של פוסטים/רילס מפייסבוק דרך ה-API
    fb_cache = {}
    for page in meta_pages:
        try:
            p_id = page["id"]
            p_token = page["token"]
            p_name = page["name"]
            posts_url = f"https://graph.facebook.com/v26.0/{p_id}/posts?fields=id,message,permalink_url,shares,likes.summary(true),comments.summary(true),views&access_token={p_token}"
            res = requests.get(posts_url).json()
            for post in res.get("data", []):
                post_id = post.get("id")
                fb_cache[post_id] = {
                    "username": p_name,
                    "title": post.get("message") or "ללא כותרת",
                    "views": post.get("views", 0),
                    "likes": post.get("likes", {}).get("summary", {}).get("total_count", 0),
                    "comments": post.get("comments", {}).get("summary", {}).get("total_count", 0),
                    "shares": post.get("shares", {}).get("count", 0)
                }
        except Exception:
            pass

    # איסוף מראש של מדיה מאינסטגרם דרך ה-API
    ig_cache = {}
    for ig_id, details in ig_accounts.items():
        try:
            ig_token = details["token"]
            ig_name = details["name"]
            media_url = f"https://graph.facebook.com/v26.0/{ig_id}/media?fields=id,shortcode,caption,like_count,comments_count,play_count,permalink&access_token={ig_token}"
            res = requests.get(media_url).json()
            for m in res.get("data", []):
                code = m.get("shortcode")
                if code:
                    ig_cache[code] = {
                        "username": ig_name,
                        "title": m.get("caption") or "ללא כותרת",
                        "views": m.get("play_count", 0),
                        "likes": m.get("like_count", 0),
                        "comments": m.get("comments_count", 0),
                        "shares": 0 # אינסטגרם API לא חושף שיתופים ישירות לפוסטים בודדים
                    }
        except Exception:
            pass

    # מעבר על הקישורים ושליפה בהתאם לפלטפורמה
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
        for url in URLS:
            if "facebook.com" in url or "fb.watch" in url:
                plat = "פייסבוק"
                match = re.search(r'/(?:reel|videos|posts)/(\d+)', url)
                fb_id = match.group(1) if match else None
                
                # חיפוש במטמון של ה-API
                matched_data = None
                if fb_id and fb_id in fb_cache:
                    matched_data = fb_cache[fb_id]
                else:
                    # חיפוש לפי התאמת מזהה חלקי
                    for k, v in fb_cache.items():
                        if fb_id and fb_id in k:
                            matched_data = v
                            break
                
                if matched_data:
                    data.append({
                        "פלטפורמה": plat,
                        "שם משתמש": matched_data["username"],
                        "תמונה": "",
                        "שם סרטון": matched_data["title"],
                        "קישור": url,
                        "צפיות": matched_data["views"],
                        "לייקים": matched_data["likes"],
                        "תגובות": matched_data["comments"],
                        "שיתופים": matched_data["shares"]
                    })
                else:
                    # ברירת מחדל אם לא נמצא ב-API
                    data.append({
                        "פלטפורמה": plat, "שם משתמש": "i24NEWS", "תמונה": "", 
                        "שם סרטון": "לא נמצא ב-API", "קישור": url, 
                        "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0
                    })

            elif "instagram.com" in url:
                plat = "אינסטגרם"
                match = re.search(r'/(?:p|reel)/([^/?#&]+)', url)
                shortcode = match.group(1) if match else None
                
                matched_data = ig_cache.get(shortcode) if shortcode else None
                
                if matched_data:
                    data.append({
                        "פלטפורמה": plat,
                        "שם משתמש": matched_data["username"],
                        "תמונה": "",
                        "שם סרטון": matched_data["title"],
                        "קישור": url,
                        "צפיות": matched_data["views"],
                        "לייקים": matched_data["likes"],
                        "תגובות": matched_data["comments"],
                        "שיתופים": matched_data["shares"]
                    })
                else:
                    data.append({
                        "פלטפורמה": plat, "שם משתמש": "i24NEWS", "תמונה": "", 
                        "שם סרטון": "לא נמצא ב-API", "קישור": url, 
                        "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0
                    })

            else:
                # טיקטוק, X, יוטיוב נשלפים דרך yt_dlp כרגיל
                if "tiktok.com" in url:
                    plat = "טיקטוק"
                elif "x.com" in url or "twitter.com" in url:
                    plat = "X (טוויטר)"
                elif "youtube.com" in url or "youtu.be" in url:
                    plat = "יוטיוב"
                else:
                    plat = "אחר"

                try:
                    info = ydl.extract_info(url, download=False)
                    uploader = info.get("uploader") or info.get("channel") or info.get("uploader_id") or "לא ידוע"
                    shares = info.get("repost_count", 0) or info.get("share_count", 0) or 0
                    data.append({
                        "פלטפורמה": plat,
                        "שם משתמש": uploader,
                        "תמונה": info.get("thumbnail", ""),
                        "שם סרטון": info.get("description") or info.get("title") or "ללא כותרת",
                        "קישור": url,
                        "צפיות": info.get("view_count", 0) or 0,
                        "לייקים": info.get("like_count", 0) or 0,
                        "תגובות": info.get("comment_count", 0) or 0,
                        "שיתופים": shares
                    })
                except:
                    data.append({
                        "פלטפורמה": plat, "שם משתמש": "שגיאה בשליפה", "תמונה": "", 
                        "שם סרטון": "שגיאה בשליפה", "קישור": url, 
                        "צפיות": 0, "לייקים": 0, "תגובות": 0, "שיתופים": 0
                    })

    df = pd.DataFrame(data)
    df.to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
    return df

if os.path.exists(CACHE_FILE):
    df = pd.read_csv(CACHE_FILE)
    if "שיתופים" not in df.columns or "שם משתמש" not in df.columns:
        with st.spinner("מעדכן מבנה נתונים..."):
            df = fetch_social_data()
else:
    with st.spinner("טוען נתונים..."):
        df = fetch_social_data()

with st.sidebar:
    if st.button("🔄 רענן נתונים"):
        with st.spinner("מרענן מול ה-API והרשתות..."):
            df = fetch_social_data()

# כרטיסי סיכום עליונים
c1, c2, c3, c4 = st.columns(4)
c1.metric("סך הכל צפיות", f"{df['צפיות'].sum():,}")
c2.metric("סך הכל לייקים", f"{df['לייקים'].sum():,}")
c3.metric("סך הכל תגובות", f"{df['תגובות'].sum():,}")
c4.metric("סך הכל שיתופים", f"{df['שיתופים'].sum():,}")

st.markdown("---")

# תצוגת הטבלה
st.dataframe(
    df[["פלטפורמה", "שם משתמש", "תמונה", "שם סרטון", "קישור", "צפיות", "לייקים", "תגובות", "שיתופים"]],
    column_config={
        "פלטפורמה": "פלטפורמה",
        "שם משתמש": "שם משתמש",
        "תמונה": st.column_config.ImageColumn("תמונה", width="small"),
        "שם סרטון": "שם סרטון",
        "קישור": st.column_config.LinkColumn("קישור לסרטון", display_text="🔗 פתח סרטון"),
        "צפיות": st.column_config.NumberColumn("צפיות", format="%d"),
        "לייקים": st.column_config.NumberColumn("לייקים", format="%d"),
        "תגובות": st.column_config.NumberColumn("תגובות", format="%d"),
        "שיתופים": st.column_config.NumberColumn("שיתופים", format="%d"),
    },
    use_container_width=True,
    hide_index=True
)
