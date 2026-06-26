import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. הגדרת עמוד והזרקת RTL
st.set_page_config(layout="wide")

st.markdown("""
    <style>
        /* כיוון RTL גורף */
        .stApp, .stApp * {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif !important;
        }
        
        .stApp {
            background-color: #f8fafc !important;
        }
        
        /* עיצוב כרטיסים נקי */
        div[data-testid="stBlock"], div[data-testid="stVerticalBlockBorder"] {
            background-color: #ffffff !important;
            padding: 30px !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            margin-bottom: 25px !important;
            border: none !important;
        }
        
        div[data-baseweb="select"] *, div[data-testid="stSelectbox"] *, .stSelectbox div {
            direction: rtl !important;
            text-align: right !important;
        }
        
        div[data-testid="stRadio"] label {
            direction: rtl !important;
            text-align: right !important;
            justify-content: flex-start !important;
            padding: 8px 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. טעינת הנתונים מהאקסל (עם טיפול בשגיאות אם הקובץ לא נמצא)
try:
    path = os.path.join(os.path.dirname(__file__), "השוואות.xlsx")
    df_m = pd.read_excel(path, sheet_name="מדרוג", header=None)
    df_s = pd.read_excel(path, sheet_name="שילוב", header=None)
except Exception as e:
    st.error(f"שגיאה בטעינת הקובץ: {e}")
    st.stop()

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
st.markdown("<h2 style='color: #0f172a; margin-bottom: 25px;'>📊 השוואת מדרוג מול סקר שילוב</h2>", unsafe_allow_html=True)

# 4. אזור פילטרים עליון
col_f1, col_f2, _, _ = st.columns([1.5, 1.5, 1, 1])
with col_f1:
    wave = st.selectbox("גל מחקר:", ["חיבור שניהם", "גל 19 במאי", "גל 25 במאי"])
with col_f2:
    if wave == "חיבור שניהם":
        t_col = demo.get(st.selectbox("פילוח דמוגרפי:", list(demo.keys())), 3)
    else:
        t_col = 1 if wave == "גל 19 במאי" else 2

# 5. מבנה טורים
col_side, col_chart = st.columns([1, 2.2], gap="large")

with col_side:
    st.markdown("<p style='font-weight: 600; color: #475569;'>בחר שאלה לניתוח:</p>", unsafe_allow_html=True)
    sel_q = st.radio("", list(questions.keys()), label_visibility="collapsed")

with col_chart:
    labels, s_vals, m_vals = [], [], []
    start_row = questions[sel_q] + 1
    
    # חילוץ נתונים
    for i in range(start_row, len(df_s)):
        row_s = df_s.iloc[i]
        if pd.isna(row_s[0]) or "q" in str(row_s[0]).lower(): 
            break
            
        txt = str(row_s[0]).lower().replace(" ", "")
        if any(x in txt for x in ["total", "סהכ", "מדגם"]): 
            continue
        
        # הבטחת חילוץ בטוח ללא קריסות אינדקס
        s_val_raw = row_s[t_col] if t_col < len(row_s) else None
        
        # טיפול במצב שלוח ה-df_m קצר יותר באורך העמודות או השורות
        if i < len(df_m) and t_col < len(df_m.iloc[i]):
            m_val_raw = df_m.iloc[i, t_col]
        else:
            m_val_raw = None
        
        s_val = pd.to_numeric(s_val_raw, errors='coerce')
        m_val = pd.to_numeric(m_val_raw, errors='coerce')
        
        # הוספה רק אם יש לפחות נתון אחד קיים - שימוש ב-None במקום 0 כדי למנוע עיוות
        labels.append(str(row_s[0]))
        s_vals.append(float(s_val) if pd.notna(s_val) else None)
        m_vals.append(float(m_val) if pd.notna(m_val) else None)

    if not labels or (all(x is None for x in s_vals) and all(x is None for x in m_vals)):
        st.info("לא נמצאו נתונים כמותיים להצגה עבור שאלה זו בפילוח שנבחר.")
    else:
        fig = go.Figure()
        
        # קווי רקע מחברים עדינים
        for lbl, s_v, m_v in zip(labels, s_vals, m_vals):
            if s_v is not None and m_v is not None:
                fig.add_trace(go.Scatter(
                    x=[m_v, s_v], y=[lbl, lbl], mode="lines", 
                    line=dict(color="#e2e8f0", width=4), hoverinfo="skip", showlegend=False
                ))

        # נקודות סקר שילוב (כחול) - שימוש ב-HTML להדגשה
        fig.add_trace(go.Scatter(
            x=s_vals, y=labels, mode="markers+text", name='סקר שילוב', 
            marker=dict(color='#2563eb', size=12, line=dict(color='white', width=2)),
            text=[f"<b>{x:.1f}%</b>" if x is not None else "" for x in s_vals], 
            textfont=dict(size=12, color="#2563eb"), 
            textposition="top center"
        ))
        
        # נקודות הוועדה למדרוג (כתום)
        fig.add_trace(go.Scatter(
            x=m_vals, y=labels, mode="markers+text", name='הוועדה למדרוג', 
            marker=dict(color='#f97316', size=12, line=dict(color='white', width=2)),
            text=[f"<b>{x:.1f}%</b>" if x is not None else "" for x in m_vals], 
            textfont=dict(size=12, color="#ea580c"), 
            textposition="bottom center"
        ))

# פריסה יציבה
        fig.update_layout(
            margin=dict(l=40, r=220, t=50, b=60), 
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=max(400, len(labels) * 55), 
            
            legend=dict(
                orientation="h", y=-0.15, x=0.5, xanchor="center", 
                font=dict(size=13, color="#475569")
            ),
            
            xaxis=dict(
                autorange="reversed", showgrid=True, gridcolor="#f1f5f9", side="top",
                ticksuffix="%", tickfont=dict(size=11, color="#64748b")
            ),
            
            yaxis=dict(
                side="right", 
                categoryorder="array",
                categoryarray=labels[::-1], 
                tickfont=dict(size=13, color="#0f172a")
                # השורה הבעייתית הוסרה לחלוטין
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
