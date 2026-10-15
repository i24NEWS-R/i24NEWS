from datetime import datetime
import os
import pandas as pd
import streamlit as st
import yt_dlp

# הגדרת עמוד ב-Streamlit
st.set_page_config(
    page_title="דשבורד צפיות ומעורבות - October 7",
    page_icon="📊",
    layout="wide",
)

# עיצוב מימין לשמאל (RTL)
st.markdown(
    """
    <style>
    body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    .stDataFrame {
        direction: rtl;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📊 דשבורד מעקב צפיות ומעורבות - אירועי 7 באוקטובר")
st.write(
    "דשבורד זה טוען נתונים מקובץ `October7.csv` הנמצא באותה התיקייה. הנתונים"
    " מתעדכנים אך ורק בלחיצה על כפתור הרענון."
)

# הגדרת נתיב דינמי כך שקובץ ה-CSV יישמר בדיוק באותה התיקייה של קובץ הפייתון הנוכחי (pages/)
script_dir = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(script_dir, "October7.csv")

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


def fetch_social_data():
  data = []
  ydl_opts = {"quiet": True, "skip_download": True}
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for url in URLS:
      try:
        info = ydl.extract_info(url, download=False)
        platform = info.get("extractor_key", "Unknown")
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
            "קישור": url,
            "צפיות": views,
            "לייקים": likes,
            "תגובות": comments,
            "שיתופים": shares,
        })
      except Exception:
        data.append({
            "פלטפורמה": "שגיאה",
            "קישור": url,
            "צפיות": 0,
            "לייקים": 0,
            "תגובות": 0,
            "שיתופים": 0,
        })
  df = pd.DataFrame(data)
  # שמירת הקובץ אוטומטית בדיוק באותה התיקייה תחת השם October7.csv
  df.to_csv(CACHE_FILE, index=False, encoding="utf-8-sig")
  return df


# בדיקה האם קיים קובץ October7.csv באותה התיקייה
if os.path.exists(CACHE_FILE):
  df = pd.read_csv(CACHE_FILE)
else:
  with st.spinner(
      "מבצע שליפה ראשונית של הנתונים ושמירה לקובץ October7.csv..."
  ):
    df = fetch_social_data()

# כפתור רענון ידני שמעדכן את הקובץ
if st.button("🔄 רענן נתונים מחדש מהרשתות"):
  with st.spinner("מעדכן נתונים מהרשתות החברתיות..."):
    df = fetch_social_data()
  st.success("הנתונים עודכנו ונשמרו בקובץ October7.csv בהצלחה!")

# הצגת כרטיסי סיכום (Metrics)
col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "סך הכל צפיות", f"{df['צפיות'].sum():,}" if "צפיות" in df else "0"
)
col2.metric(
    "סך הכל לייקים", f"{df['לייקים'].sum():,}" if "לייקים" in df else "0"
)
col3.metric(
    "סך הכל תגובות", f"{df['תגובות'].sum():,}" if "תגובות" in df else "0"
)
col4.metric(
    "סך הכל שיתופים", f"{df['שיתופים'].sum():,}" if "שיתופים" in df else "0"
)

st.markdown("---")
st.subheader("פירוט לפי סרטון")

# טבלה אינטראקטיבית עם קישורים לחיצים
st.dataframe(
    df,
    use_container_width=True,
    column_config={"קישור": st.column_config.LinkColumn("קישור ישיר")},
)
