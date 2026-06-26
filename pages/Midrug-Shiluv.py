import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. הגדרת עמוד והזרקת RTL ועיצוב כרטיסים אגרסיבי
st.set_page_config(layout="wide")

st.markdown("""
    <style>
        /* כיוון RTL גורף לכל ה-DOM כולל טקסטים, קלטים וכפתורים */
        .stApp, .stApp * {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
        }
        
        /* רקע כללי של המערכת - אפור בהיר נקי */
        .stApp {
            background-color: #f8fafc !important;
        }
        
        /* יצירת כרטיסים לבנים מובלטים עם מרווחים פנימיים וחיצוניים גדולים */
        div[data-testid="stBlock"], div[data-testid="stVerticalBlockBorder"] {
            background-color: #ffffff !important;
            padding: 35px 40px !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            margin-bottom: 30px !important;
            border: none !important;
        }
        
        /* יישור קשיח של תיבות הפילטרים (Selectbox) ותתי-התפריטים שלהן לימין */
        div[data-baseweb="select"] *, div[data-testid="stSelectbox"] *, .stSelectbox div {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* מניעת עיוות של פקדי הרדיו ויצירת ריווח נקי ביניהם */
        div[data-testid="stRadio"] label {
            direction: rtl !important;
            text-align: right !important;
            justify-content: flex-start !important;
            padding: 8px 0 !important;
        }
        
        /* כותרות הפילטרים והווידג'טים */
        div[data-testid="stWidgetLabel"] p {
            font-weight: 600 !important;
            color: #475569 !important;
            margin-bottom: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. טעינת הנתונים מהאקסל
path = os.path.join(os.path.dirname(__file__), "השוואות.xlsx")
df_m = pd.read_excel(path, sheet_name="מדרוג", header=None)
df_s = pd.read_excel(path, sheet_name="שילוב", header=None)

# מיפוי השאלות
questions = {str(r[0]): i for i, r in df_s.iterrows() if "q" in str(r[0]).lower() or ":" in str(r[0])}

# בניית פילוח דמוגרפי דינמי
cats = [str(x).strip() if pd.notna(x) else "" for x in df_s.iloc[0]]
for i in range(1, len(cats)): 
    if not cats[i]: cats[i] = cats[i-1]

demo = {"כללי": 3}
for idx in range(4, df_s.shape[1]):
    sub = df_s.iloc[1, idx]
    if pd.notna(sub): demo[f"{cats[idx]} - {str(sub).strip()}"] = idx

# 3. כותרת עליונה
st.markdown("<h2 style='color: #0f172a; font-weight: 700; margin-bottom: 25px;'>📊 השוואת מדרוג מול סקר שילוב</h2>", unsafe_allow_html
