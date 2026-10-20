import os
import re
import requests
import pandas as pd
import streamlit as st
import yt_dlp

st.set_page_config(page_title="October 7", page_icon="📊", layout="wide")

# עיצוב CSS מתקדם לדשבורד יוקרתי, ממורכז לחלוטין, כרטיסים מעוגלים עם קו מקווקו
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
META_USER_TOKEN = "EAAORARdXiYYBS9qNAtINW7KnKzvAOObamroZA1ZBqsS9U4OsiPv5iKNtK6rulafegvF4Xy8lZA3ZA0W3McOPrjLi0zDQypwUVgnSinhHvtwjOE8COktwJWVlZAhnknlb8z4zzLHU4CNkNU1SlX6ZCAqrw5wTO0R6ZAuxolZBeQxFRdAnlZAqSkQOCYA3tZCjERQk3XQiaCvh4ehdq5WeoLFTfwolyISwUhaelXcwO6tKyJxZCJlSU0LS2wAPAAUuZCpzerXdMgC0eVvk9PNyjnhndFJgEtcbg9O2"

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
        api_url = f"https://graph.facebook.com/v26.0/{fb_id}?fields=description,views,from{{name}},picture,video_insights.metric(post_video_likes_by_reaction_type,post_video_social_actions)&access_token={META_USER_TOKEN}"
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
  """שליפת נתוני אינסטגרם דרך ה-Graph API עם מיפוי אוטומטי מהפיד"""
  ig_data = []
  ig_accounts = []

  # שלב 1: איתור חשבונות האינסטגרם העסקיים המקושרים
  try:
    accounts_url = f"https://graph.facebook.com/v26.0/me/accounts?fields=instagram_business_account{{id,username}},name&access_token={META_USER_TOKEN}"
    res = requests.get(accounts_url).json()
    for acc in res.get("data", []):
      ig_acc = acc.get("instagram_business_account")
      if ig_acc:
        ig_accounts.append({
            "id": ig_acc.get("id"),
            "username": ig_acc.get("username", "i24NEWS"),
        })
  except Exception:
    pass

  # שלב 2: בניית מילון מיפוי מקישורי הפיד
  media_map = {}
  for ig in ig_accounts:
    ig_id = ig["id"]
    default_uname = ig["username"]
    try:
      media_url = f"https://graph.facebook.com/v26.0/{ig_id}/media?fields=id,permalink,caption,thumbnail_url,total_views_count,total_like_count,total_comments_count,shares_count&limit=100&access_token={META_USER_TOKEN}"
      media_res = requests.get(media_url).json()
      for post in media_res.get("data", []):
        p_link = post.get("permalink")
        if p_link:
          clean_link = p_link.strip().rstrip("/")
          media_map[clean_link] = {
              "username": default_uname,
              "caption": post.get("caption") or "ללא כותרת",
              "thumbnail_url": post.get("thumbnail_url", ""),
              "total_views_count": post.get("total_views_count", 0) or 0,
              "total_like_count": post.get("total_like_count", 0) or 0,
              "total_comments_count": post.get("total_comments_count", 0) or 0,
              "shares_count": post.get("shares_count", 0) or 0,
          }
    except Exception:
      pass

  # שלב 3: התאמת הלינקים ברשימה לנתונים שנשלפו
  for url in URLS:
    if "instagram.com" in url:
      clean_target_url = url.strip().rstrip("/")
      matched_post = media_map.get(clean_target_url)

      if matched_post:
        ig_data.append({
            "פלטפורמה": "אינסטגרם",
            "שם משתמש": matched_post["username"],
            "תמונה": matched_post["thumbnail_url"],
            "שם סרטון": matched_post["caption"],
            "קישור": url,
            "צפיות": matched_post["total_views_count"],
            "לייקים": matched_post["total_like_count"],
            "תגובות": matched_post["total_comments_count"],
            "שיתופים": matched_post["shares_count"],
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
          plat = "אחר"

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


def fetch_all_social_data():
  df = pd.DataFrame(
      fetch_facebook_data() + fetch_instagram_data() + fetch_ytdlp_data()
  )
  df.to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
  return df


if os.path.exists(CACHE_FILE):
  df = pd.read_csv(CACHE_FILE)
  if "שיתופים" not in df.columns or "שם משתמש" not in df.columns:
    with st.spinner("מעדכן מבנה נתונים..."):
      df = fetch_all_social_data()
else:
  with st.spinner("טוען נתונים..."):
    df = fetch_all_social_data()

with st.sidebar:
  if st.button("🔄 רענן נתונים"):
    with st.spinner("מרענן מול ה-API והרשתות..."):
      df = fetch_all_social_data()

# כרטיסי סיכום עליונים מעוצבים במרכז עם קו מקווקו
col1, col2, col3, col4 = st.columns(4)
with col1:
  st.markdown(
      f"""
        <div class="metric-card">
            <div class="metric-title">סך הכל צפיות</div>
            <div class="metric-value">{int(df['צפיות'].sum()):,}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )
with col2:
  st.markdown(
      f"""
        <div class="metric-card">
            <div class="metric-title">סך הכל לייקים</div>
            <div class="metric-value">{int(df['לייקים'].sum()):,}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )
with col3:
  st.markdown(
      f"""
        <div class="metric-card">
            <div class="metric-title">סך הכל תגובות</div>
            <div class="metric-value">{int(df['תגובות'].sum()):,}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )
with col4:
  st.markdown(
      f"""
        <div class="metric-card">
            <div class="metric-title">סך הכל שיתופים</div>
            <div class="metric-value">{int(df['שיתופים'].sum()):,}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("<br>", unsafe_allow_html=True)

# בניית טבלה שטוחה לחלוטין (ללא רווחים מיותרים)
table_html = '<table class="custom-table"><thead><tr><th style="width: 8%;">פלטפורמה</th><th style="width: 12%;">שם משתמש</th><th style="width: 6%;">תמונה</th><th style="width: 54%;">שם סרטון</th><th style="width: 5%;">צפיות</th><th style="width: 5%;">לייקים</th><th style="width: 5%;">תגובות</th><th style="width: 5%;">שיתופים</th></tr></thead><tbody>'

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

  table_html += (
      f"<tr><td>{plat}</td><td>{user}</td><td>{thumb_tag}</td><td><a"
      f' href="{link}" target="_blank" class="video-link">{title}</a></td><td>{views}</td><td>{likes}</td><td>{comments}</td><td>{shares}</td></tr>'
  )

table_html += "</tbody></table>"

st.markdown(table_html, unsafe_allow_html=True)
