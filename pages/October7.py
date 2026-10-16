from datetime import datetime
import os
import re
import pandas as pd
import streamlit as st
import yt_dlp

# הגדרת עמוד ב-Streamlit
st.set_page_config(
    page_title="October 7 - The last day of my life",
    page_icon="📊",
    layout="wide",
)

# עיצוב מקיף מימין לשמאל (RTL), יישור למרכז ומראה מקצועי
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

    /* עיצוב כותרות וקישורים */
    h1, h2, h3, h4, p {
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


def clean_title(title):
  """ניקוי כותרת הסרטון מהצגת נתונים כמו צפיות ולייקים מתוך המחרוזת"""
  if not title:
    return "ללא כותרת"
  # אם יש תו מפריד כמו |, לוקחים לרוב את החלק הנקי של הכותרת שאחריו
  if "|" in title:
    parts = title.split("|")
    title = parts[-1].strip()
  # הסרת תבניות נפוצות של צפיות ותגובות בתחילת המחרוזת
  title = re.sub(
      r"^[\d\.,]+[KkMm]?\s*(views|reactions|shares|comments).*?(?:\||$)",
      "",
      title,
      flags=re.IGNORECASE,
  )
  return title.strip() or "ללא כותרת"


def fetch_social_data():
  data = []
  ydl_opts = {"quiet": True, "skip_download": True}
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for url in URLS:
      try:
        info = ydl.extract_info(url, download=False)
        ext = info.get("extractor_key", "").lower()

        if "facebook" in ext:
          platform = "פייסבוק"
        elif "instagram" in ext:
          platform = "אינסטגרם"
        elif "tiktok" in ext:
          platform = "טיקטוק"
        elif "twitter" in ext or "x" in ext:
          platform = "X (טוויטר)"
        elif "youtube" in ext:
          platform = "יוטיוב"
        else:
          platform = info.get("extractor_key", "אחר")

        raw_title = info.get("title", "ללא כותרת")
        title = clean_title(raw_title)
        thumbnail = info.get("thumbnail", "")
        views = info.get("view_count", 0) or 0
        likes = info.get("like_count", 0) or 0
        comments = info.get("comment_count", 0) or 0
        shares = (
            info.get("repost_count", 0)
            or info.get("share_count", 0)
            or 0
        )

        data.append({
            "פלטפורמה": platform,
            "כותרת": title,
            "קישור": url,
            "תמונה": thumbnail,
            "צפיות": views,
            "לייקים": likes,
            "תגובות": comments,
            "שיתופים": shares,
        })
      except Exception:
