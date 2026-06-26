import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from main import set_rtl

st.set_page_config(layout="wide")
set_rtl()

# טעינת נתונים
path = os.path.join(os.path.dirname(__file__), "השוואות.xlsx")
df_m = pd.read_excel(path, sheet_name="מדרוג", header=None)
df_s = pd.read_excel(path, sheet_name="שילוב", header=None)

questions = {str(r[0]): i for i, r in df_s.iterrows() if "q" in str(r[0]).lower() or ":" in str(r[0])}

cats = [str(x).strip() if pd.notna(x) else "" for x in df_s.iloc[0]]
for i in range(1, len(cats)): 
    if not cats[i]: cats[i] = cats[i-1]

demo = {"כללי": 3}
for idx in range(4, df_s.shape[1]):
    sub = df_s.iloc[1, idx]
    if pd.notna(sub): demo[f"{cats[idx]} - {str(sub).strip()}"] = idx

st.markdown("<h2 style='margin-bottom: 25px;'>📊 השוואת מדרוג מול סקר שילוב</h2>", unsafe_allow_html=True)

# כרטיס פילטרים עליון - מוגבל ברוחב (שימוש ב-4 טורים, השניים השמאליים ריקים)
with st.container(border=True):
    col_f1, col_f2, col_empty1, col_empty2 = st.columns([1.2, 1.2, 1, 1])
    wave = col_f1.selectbox("גל מחקר", ["חיבור שניהם", "גל 19 במאי", "גל 25 במאי"])
    if wave == "חיבור שניהם":
        t_col = demo[col_f2.selectbox("פילוח דמוגרפי", list(demo.keys()))]
    else:
        t_col = 1 if wave == "גל 19 במאי" else 2

# גוף הדשבורד
col_side, col_chart = st.columns([1, 2.2], gap="large")

with col_side:
    with st.container(border=True):
        st.markdown("<p style='font-weight: 600; color: #64748b; margin-bottom: 15px; font-size: 15px;'>בחר שאלה לניתוח</p>", unsafe_allow_html=True)
        sel_q = st.radio("", list(questions.keys()), label_visibility="collapsed")

with col_chart:
    with st.container(border=True):
        
        # חילוץ נתונים
        labels, s_vals, m_vals = [], [], []
        for i in range(questions[sel_q] + 1, len(df_s)):
            row_s, row_m = df_s.iloc[i], df_m.iloc[i]
            if pd.isna(row_s[0]) or "q" in str(row_s[0]).lower(): break
            
            txt = str(row_s[0]).lower().replace(" ", "")
            if "total" in txt or "סהכ" in txt or "מדגם" in txt: continue
            
            labels.append(str(row_s[0]))
            s_vals.append(pd.to_numeric(row_s[t_col], errors='coerce') or 0.0)
            m_vals.append(pd.to_numeric(row_m[t_col], errors='coerce') or 0.0)

        # בניית הגרף המעוצב
        fig = go.Figure()
        
        # קווי קישור רחבים אך סופר-עדינים ברקע
        for lbl, s_v, m_v in zip(labels, s_vals, m_vals):
            if m_v > 0 or "עיקרי" not in sel_q:
                fig.add_trace(go.Scatter(x=[m_v, s_v], y=[lbl, lbl], mode="lines", line=dict(color="#f1f5f9", width=8), hoverinfo="skip", showlegend=False))

        # נקודות נתונים - הרחקנו את הטקסטים מהנקודות כדי שלא יעלו על הצירים או על הסימנים
        fig.add_trace(go.Scatter(
            x=s_vals, y=labels, mode="markers+text", name='סקר שילוב', 
            marker=dict(color='#2563eb', size=14, line=dict(color='white', width=2.5)),
            text=[f"{x:.1f}%" for x in s_vals], textfont=dict(size=11, color="#2563eb", weight="bold"), 
            textposition="top center"
        ))
        
        fig.add_trace(go.Scatter(
            x=m_vals, y=labels, mode="markers+text", name='הוועדה למדרוג', 
            marker=dict(color='#f97316', size=14, line=dict(color='white', width=2.5)),
            text=[f"{x:.1f}%" if x > 0 else "" for x in m_vals], textfont=dict(size=11, color="#f97316", weight="bold"), 
            textposition="bottom center"
        ))

        # עיצוב פריסה (Layout) נקי ואקסקלוסיבי
        fig.update_layout(
            # הוספת שוליים רחבים מאוד (margin) בצד ימין כדי לתת לשמות הערוצים או התשובות מקום לנשום מבלי להימחץ
            margin=dict(l=30, r=180, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=480,
            # עיצוב מקרא תחתון מרווח
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(size=13, color="#475569")),
            # ציר ה-X מועבר למעלה ומרווח מקווי הגרף
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9", side="top", autorange="reversed", ticksuffix="%", tickfont=dict(size=11, color="#64748b")),
            # ציר ה-Y מיושר לימין עם שטח ייעודי מוגדר
            yaxis=dict(autorange="reversed", side="right", tickfont=dict(size=13, color="#0f172a"))
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
