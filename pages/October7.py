import os
import re
import pandas as pd
import requests
import streamlit as st
import yt_dlp

st.set_page_config(page_title="October 7", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 8px;
        font-weight: 600;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        text-align: center;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
        background-color: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .custom-table th {
        background-color: #f1f5f9;
        color: #334155;
        padding: 12px 16px;
        text-align: center !important;
        font-weight: 600;
        font-size: 0.9rem;
        border-bottom: 2px solid #e2e8f0;
    }
    .custom-table td {
        padding: 12px 16px;
        text-align: center !important;
        vertical-align: middle !important;
        color: #475569;
        font-size: 0.9rem;
        border-bottom: 1px solid #f1f5f9;
    }
    .custom-table tr:hover {
        background-color: #f8fafc;
    }
    .video-link {
        color: #2563eb;
        text-decoration: none;
        font-weight: 500;
    }
    .video-link:hover {
        text-decoration: underline;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">October 7 - The last day of my life</div>',
    unsafe_allow_html=True,
)

CACHE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "October7.csv"
)
META_USER_TOKEN = st.secrets["META_USER_TOKEN"]

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


def fetch_facebook_data():
  fb_data = []
  for url in URLS:
    if "facebook.com" in url or "fb.watch" in url:
      match = re.search(r"/(?:reel|videos|posts)/(\d+)", url)
      fb_id = match.group(1) if match else None

      if fb_id:
        api_url = f"https://graph.facebook.com/v26.0/{fb_id}?fields=description,views,from%7Bname%7D,picture,video_insights.metric(post_video_likes_by_reaction_type,post_video_social_actions)&access_token={META_USER_TOKEN}"
        try:
          res = requests.get(api_url).json()
          if "error" not in res:
            desc = res.get("description") or "ללא כותרת"
            views = res.get("views", 0) or 0
            username = res.get("from", {}).get("name", "i24NEWS")
            picture = res.get("picture", "")

            likes, comments, shares = 0, 0, 0
            for insight in res.get("video_insights", {}).get("data", []):
              m_name = insight.get("name")
              values = insight.get("values", [{}])[0].get("value", {})
              if m_name == "post_video_likes_by_reaction_type":
                likes = sum(values.values())
              elif m_name == "post_video_social_actions":
                comments = values.get("COMMENT", 0)
                shares = values.get("SHARE", 0)

            fb_data.append({
                "פלטפורמה": "פייסבוק",
                "שם משתמש": username,
                "תמונה": picture,
                "שם סרטון": desc,
                "קישור": url,
                "צפיות": views,
                "לייקים": likes,
                "תגובות": comments,
                "שיתופים": shares,
            })
            continue
        except Exception:
          pass

      fb_data.append({
          "פלטפורמה": "פייסבוק",
          "שם משתמש": "i24NEWS",
          "תמונה": "",
          "שם סרטון": "שגיאה בשליפת API",
          "קישור": url,
          "צפיות": 0,
          "לייקים": 0,
          "תגובות": 0,
          "שיתופים": 0,
      })
  return fb_data


def fetch_instagram_data():
  ig_data = []
  ig_accounts = []

  try:
    acc_url = f"https://graph.facebook.com/v26.0/me/accounts?fields=instagram_business_account{{id,username}},name&access_token={META_USER_TOKEN}"
    res = requests.get(acc_url).json()
    for page in res.get("data", []):
      ig_acc = page.get("instagram_business_account")
      if ig_acc:
        ig_accounts.append({
            "id": ig_acc.get("id"),
            "username": ig_acc.get("username", "i24NEWS"),
        })
  except Exception:
    pass

  shortcode_map = {}
  for ig in ig_accounts:
    ig_id = ig["id"]
    default_uname = ig["username"]

    next_url = f"https://graph.facebook.com/v26.0/{ig_id}/media?fields=id,permalink,caption,thumbnail_url,total_views_count,total_like_count,total_comments_count,shares_count&limit=100&access_token={META_USER_TOKEN}"

    page_count = 0
    max_pages = 5
    posts_scanned = 0
    max_posts = 500

    while next_url and page_count < max_pages and posts_scanned < max_posts:
      try:
        media_res = requests.get(next_url).json()
        data_list = media_res.get("data", [])
        page_count += 1

        for post in data_list:
          posts_scanned += 1
          if posts_scanned > max_posts:
            break

          p_link = post.get("permalink", "")
          sc_match = re.search(r"/(?:p|reel)/([^/]+)", p_link)
          if sc_match:
            code = sc_match.group(1)
            shortcode_map[code] = {
                "username": default_uname,
                "caption": post.get("caption") or "ללא כותרת",
                "thumbnail_url": post.get("thumbnail_url", ""),
                "views": post.get("total_views_count", 0) or 0,
                "likes": post.get("total_like_count", 0) or 0,
                "comments": post.get("total_comments_count", 0) or 0,
                "shares": post.get("shares_count", 0) or 0,
            }

        if posts_scanned >= max_posts:
          break

        next_url = media_res.get("paging", {}).get("next")
      except Exception:
        break

  for url in URLS:
    if "instagram.com" in url:
      sc_match = re.search(r"/(?:p|reel)/([^/]+)", url)
      target_code = sc_match.group(1) if sc_match else None

      matched = shortcode_map.get(target_code) if target_code else None

      if matched:
        ig_data.append({
            "פלטפורמה": "אינסטגרם",
            "שם משתמש": matched["username"],
            "תמונה": matched["thumbnail_url"],
            "שם סרטון": matched["caption"],
            "קישור": url,
            "צפיות": matched["views"],
            "לייקים": matched["likes"],
            "תגובות": matched["comments"],
            "שיתופים": matched["shares"],
        })
      else:
        ig_data.append({
            "פלטפורמה": "אינסטגרם",
            "שם משתמש": "i24NEWS",
            "תמונה": "",
            "שם סרטון": "לא נמצא בפיד המקושר",
            "קישור": url,
            "צפיות": 0,
            "לייקים": 0,
            "תגובות": 0,
            "שיתופים": 0,
        })
  return ig_data


def fetch_ytdlp_data():
  other_data = []
  with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
    for url in URLS:
      if not (
          "facebook.com" in url
          or "fb.watch" in url
          or "instagram.com" in url
      ):
        if "tiktok.com" in url:
          plat = "טיקטוק"
        elif "x.com" in url or "twitter.com" in url:
          plat = "X (טוויטר)"
        elif "youtube.com" in url or "youtu.be" in url:
          plat = "יוטיוב"
        else:
          plat = "platform"

        try:
          info = ydl.extract_info(url, download=False)
          uploader = (
              info.get("uploader")
              or info.get("channel")
              or info.get("uploader_id")
              or "לא ידוע"
          )
          shares = (
              info.get("repost_count", 0)
              or info.get("share_count", 0)
              or 0
          )
          other_data.append({
              "פלטפורמה": plat,
              "שם משתמש": uploader,
              "תמונה": info.get("thumbnail", ""),
              "שם סרטון": (
                  info.get("description")
                  or info.get("title")
                  or "ללא כותרת"
              ),
              "קישור": url,
              "צפיות": info.get("view_count", 0) or 0,
              "לייקים": info.get("like_count", 0) or 0,
              "תגובות": info.get("comment_count", 0) or 0,
              "שיתופים": shares,
          })
        except:
          other_data.append({
              "פלטפורמה": plat,
              "שם משתמש": "שגיאה בשליפה",
              "תמונה": "",
              "שם סרטון": "שגיאה בשליפה",
              "קישור": url,
              "צפיות": 0,
              "לייקים": 0,
              "תגובות": 0,
              "שיתופים": 0,
          })
  return other_data


# הגדרת סרגל צד לניהול רענון
with st.sidebar:
  st.markdown("### 🔄 ניהול ורענון נתונים")
  if st.button("רענן את כל הפלטפורמות"):
    if os.path.exists(CACHE_FILE):
      os.remove(CACHE_FILE)
    st.rerun()

# יצירת מקומות שמורים (Placeholders) דינמיים למדדים ולטבלה
metrics_placeholder = st.empty()
table_placeholder = st.empty()


def render_dashboard(df):
  # עידכון כרטיסי המדדים
  c1, c2, c3, c4 = metrics_placeholder.columns(4)
  with c1:
    st.markdown(
        f"""
            <div class="metric-card">
                <div class="metric-title">סך הכל צפיות</div>
                <div class="metric-value">{int(df['צפיות'].sum()):,}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c2:
    st.markdown(
        f"""
            <div class="metric-card">
                <div class="metric-title">סך הכל לייקים</div>
                <div class="metric-value">{int(df['לייקים'].sum()):,}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c3:
    st.markdown(
        f"""
            <div class="metric-card">
                <div class="metric-title">סך הכל תגובות</div>
                <div class="metric-value">{int(df['תגובות'].sum()):,}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )
  with c4:
    st.markdown(
        f"""
            <div class="metric-card">
                <div class="metric-title">סך הכל שיתופים</div>
                <div class="metric-value">{int(df['שיתופים'].sum()):,}</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

  # בניית הטבלה
  t_html = '<table class="custom-table"><thead><tr><th style="width: 8%;">פלטפורמה</th><th style="width: 12%;">שם משתמש</th><th style="width: 6%;">תמונה</th><th style="width: 54%;">שם סרטון</th><th style="width: 5%;">צפיות</th><th style="width: 5%;">לייקים</th><th style="width: 5%;">תגובות</th><th style="width: 5%;">שיתופים</th></tr></thead><tbody>'
  for _, row in df.iterrows():
    plat = row["פלטפורמה"]
    user = row["שם משתמש"]
    thumb = row["תמונה"]
    thumb_tag = (
        f'<img src="{thumb}" style="width: 36px; height: 36px; object-fit:'
        ' cover; border-radius: 4px;" />'
        if pd.notna(thumb) and str(thumb).startswith("http")
        else ""
    )
    title = row["שם סרטון"]
    link = row["קישור"]
    views = f"{int(row['צפיות']):,}"
    likes = f"{int(row['לייקים']):,}"
    comments = f"{int(row['תגובות']):,}"
    shares = f"{int(row['שיתופים']):,}"

    # הוספת סימון ויזואלי (אנימציית טעינה/שורה בהמתנה) אם הנתונים טרם נטענו
    is_loading = (
        user == "שגיאה בשליפה"
        or user == "שגיאה בשליפת API"
        or title == "טוען נתונים..."
    )
    row_style = (
        ' style="background-color: #fef3c7; animation: pulse 1.5s infinite;"'
        if is_loading
        else ""
    )

    t_html += (
        f"<tr{row_style}><td>{plat}</td><td>{user}</td><td>{thumb_tag}</td><td><a"
        f' href="{link}" target="_blank" class="video-link">{title}</a></td><td>{views}</td><td>{likes}</td><td>{comments}</td><td>{shares}</td></tr>'
    )
  t_html += "</tbody></table>"
  table_placeholder.markdown(t_html, unsafe_allow_html=True)


# --- לוגיקת טעינה הדרגתית (Progressive Loading) ---
all_rows = []

# שלב א': יצירת שלד ראשוני לכל הלינקים (כדי שהטבלה תופיע מיד עם אנימציית טעינה)
for url in URLS:
  if "facebook.com" in url or "fb.watch" in url:
    plat = "פייסבוק"
  elif "instagram.com" in url:
    plat = "אינסטגרם"
  elif "tiktok.com" in url:
    plat = "טיקטוק"
  elif "x.com" in url or "twitter.com" in url:
    plat = "X (טוויטר)"
  else:
    plat = "יוטיוב"

  all_rows.append({
      "פלטפורמה": plat,
      "שם משתמש": "טוען...",
      "תמונה": "",
      "שם סרטון": "טוען נתונים...",
      "קישור": url,
      "צפיות": 0,
      "לייקים": 0,
      "תגובות": 0,
      "שיתופים": 0,
  })

current_df = pd.DataFrame(all_rows)
render_dashboard(current_df)

# שלב ב': שליפת יוטיוב, טיקטוק ו-X (yt-dlp) - הכי מהר
with st.spinner("שולף נתונים מ-YouTube, TikTok ו-X..."):
  ytdlp_res = fetch_ytdlp_data()
  for item in ytdlp_res:
    for idx, row in enumerate(all_rows):
      if row["קישור"] == item["קישור"]:
        all_rows[idx] = item

current_df = pd.DataFrame(all_rows)
render_dashboard(current_df)  # עדכון מיידי של המסך!

# שלב ג': שליפת פייסבוק
with st.spinner("שולף נתונים מפייסבוק..."):
  fb_res = fetch_facebook_data()
  for item in fb_res:
    for idx, row in enumerate(all_rows):
      if row["קישור"] == item["קישור"]:
        all_rows[idx] = item

current_df = pd.DataFrame(all_rows)
render_dashboard(current_df)  # עדכון מיידי נוסף של המסך!

# שלב ד': שליפת אינסטגרם (שלוקח הכי הרבה זמן)
with st.spinner("שולף נתונים מאינסטגרם (עשוי לקחת מספר שניות)..."):
  ig_res = fetch_instagram_data()
  for item in ig_res:
    for idx, row in enumerate(all_rows):
      if row["קישור"] == item["קישור"]:
        all_rows[idx] = item

current_df = pd.DataFrame(all_rows)
render_dashboard(current_df)  # סיום טעינה מלאה!

# שמירה בקובץ מטמון בסיום התהליך
current_df.to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
