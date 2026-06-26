import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from main import set_rtl

# 1. הגדרת פריסה רספונסיבית רחבה (מתאימה את עצמה אוטומטית למסכי מחשב ונייד)
st.set_page_config(layout="wide")
set_rtl()

# טעינה דינמית ויציבה של קובץ האקסל מאותה התיקייה
path = os.path.join(os.path.dirname(__file__), "השוואות.xlsx")
df_m = pd.read_excel(path, sheet_name="מדרוג", header=None)
df_s = pd.read_excel(path, sheet_name="שילוב", header=None)

# מיפוי חכם של שאלות ופילטרים דמוגרפיים מתוך האקסל
questions = {str(r[0]): i for i, r in df_s.iterrows() if "q" in str(r[0]).lower() or ":" in str(r[0])}
cats = [str(x).strip() if pd.notna(x) else "" for x in df_s.iloc[0]]
for i in range(1, len(cats)): 
    if not cats[i]: cats[i] = cats[i-1]

demo = {"כללי": 3}
for idx in range(4, df_s.shape[1]):
    sub = df_s.iloc[1, idx]
    if pd.notna(sub): demo[f"{cats[idx]} - {str(sub).strip()}"] = idx

# 2. מסננים בשורה אחת - בנייד הם יסתדרו אוטומטית זה תחת זה בצורה אנכית נקייה
col_f1, col_f2 = st.columns(2)
wave = col_f1.selectbox("גל:", ["חיבור שניהם", "גל 19 במאי", "גל 25 במאי"])
t_col = demo[col_f2.selectbox("דמוגרפיה:", list(demo.keys()))] if wave == "חיבור שניהם" else (1 if wave == "גל 19 במאי" else 2)

# 3. פריסת תוכן דו-טורית רספונסיבית (תפריט השאלות והגרף)
col_side, col_chart = st.columns([1, 2.5])
sel_q = col_side.radio("שאלות:", list(questions.keys()))

# חילוץ ועיבוד הנתונים לגרף
labels, s_vals, m_vals = [], [], []
for i in range(questions[sel_q] + 1, len(df_s)):
    row_s, row_m = df_s.iloc[i], df_m.iloc[i]
    if pd.isna(row_s[0]) or "q" in str(row_s[0]).lower(): break
    if "total" in str(row_s[0]).lower() or "סהכ" in str(row_s[0]).lower() or "סה\"כ" in str(row_s[0]).lower(): continue
    labels.append(str(row_s[0]))
    s_vals.append(pd.to_numeric(row_s[t_col], errors='coerce') or 0.0)
    m_vals.append(pd.to_numeric(row_m[t_col], errors='coerce') or 0.0)

# בניית גרף הדאמבל (Dumbbell Chart)
fig = go.Figure()
for lbl, s_v, m_v in zip(labels, s_vals, m_vals):
    if m_v > 0 or "עיקרי" not in sel_q:
        fig.add_trace(go.Scatter(x=[m_v, s_v], y=[lbl, lbl], mode="lines", line=dict(color="#e2e8f0", width=4), showlegend=False))

fig.add_trace(go.Scatter(x=s_vals, y=labels, mode="markers+text", name='סקר שילוב', marker=dict(color='#2563eb', size=12), text=[f"{x:.1f}%" for x in s_vals], textposition="top center"))
fig.add_trace(go.Scatter(x=m_vals, y=labels, mode="markers+text", name='הוועדה למדרוג', marker=dict(color='#ea580c', size=12), text=[f"{x:.1f}%" if x > 0 else "" for x in m_vals], textposition="bottom center"))

# 4. הגדרות רספונסיביות לגרף (גובה אופטימלי ורקע שקוף שמתאים את עצמו לתמה הנבחרת)
fig.update_layout(height=480, margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
fig.update_layout(xaxis=dict(side="top", autorange="reversed", gridcolor="#f1f5f9"), yaxis=dict(autorange="reversed", side="right"))

# 5. הצגת הגרף תוך שימוש במלוא רוחב הדיב הזמין (use_container_width=True)
col_chart.plotly_chart(fig, use_container
