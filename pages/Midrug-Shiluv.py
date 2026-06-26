import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# 1. הגדרת פריסה רחבה
st.set_page_config(layout="wide")

# 2. הזרקת CSS עדכני וחסין שמתאים בדיוק למבנה החדש של סטרימליט
st.markdown("""
    <style>
        /* כיוון כללי לימין לכל האפליקציה */
        .stApp {
            direction: rtl !important;
            text-align: right !important;
            background-color: #f8fafc !important; /* רקע אפור-בהיר יוקרתי */
        }
        
        /* כרטיסים לבנים מובלטים עם פדינג וצל מודרני */
        div[data-testid="stBlock"] {
            background-color: #ffffff !important;
            padding: 24px 30px !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            margin-bottom: 20px !important;
        }
        
        /* יישור קשיח של תיבות הבחירה (Dropdowns) והטקסט בתוכן לימין */
        div[data-baseline="select"] *, div[data-testid="stSelectbox"] *, .stSelectbox div {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* סידור רדיו השאלות בצד ימין עם מרווח נקי */
        div[data-testid="stRadio"] label {
            direction: rtl !important;
            text-align: right !important;
            justify-content: flex-start !important;
            padding: 6px 0 !important;
        }
        
        /* תיקון כותרות הפילטרים */
        div[data-testid="stWidgetLabel"] p {
            text-align: right !important;
            direction: rtl !important;
            font-weight: 600 !important;
            color: #475569 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. טעינת הנתונים מהאקסל
path = os.path.join(os.path.dirname(__file__), "השוואות.xlsx")
df_m = pd.read_excel(path, sheet_name="מדרוג", header=None)
df_s = pd.read_excel(path, sheet_name="שילוב", header=None)

# מיפוי השאלות
questions = {str(r[0]): i for i, r in df_s.iterrows() if "q" in str(r[0]).lower() or ":" in str(r[0])}

# בניית פילוח דמוגרפי
cats = [str(x).strip() if pd.notna(x) else "" for x in df_s.iloc[0]]
for i in range(1, len(cats)): 
    if not cats[i]: cats[i] = cats[i-1]

demo = {"כללי": 3}
for idx in range(4, df_s.shape[1]):
    sub = df_s.iloc[1, idx]
    if pd.notna(sub): demo[f"{cats[idx]} - {str(sub).strip()}"] = idx

# 4. כותרת הדשבורד
st.markdown("<h2 style='color: #0f172a; font-weight: 700; margin-bottom: 25px;'>📊 השוואת מדרוג מול סקר שילוב</h2>", unsafe_allow_html=True)

# 5. אזור הפילטרים העליון
col_f1, col_f2, _, _ = st.columns([1.5, 1.5, 1, 1])
with col_f1:
    wave = st.selectbox("גל מחקר:", ["חיבור שניהם", "גל 19 במאי", "גל 25 במאי"])
with col_f2:
    if wave == "חיבור שניהם":
        t_col = demo.get(st.selectbox("פילוח דמוגרפי:", list(demo.keys())), 3)
    else:
        t_col = 1 if wave == "גל 19 במאי" else 2

# 6. חלוקה לטורים (שאלות מימין, גרף משמאל)
col_side, col_chart = st.columns([1, 2.2], gap="large")

with col_side:
    st.markdown("<p style='font-weight: 600; color: #475569; margin-bottom: 10px;'>בחר שאלה לניתוח:</p>", unsafe_allow_html=True)
    sel_q = st.radio("", list(questions.keys()), label_visibility="collapsed")

with col_chart:
    labels, s_vals, m_vals = [], [], []
    start_row = questions[sel_q] + 1
    
    # עיבוד וסינון הנתונים מהאקסל
    for i in range(start_row, len(df_s)):
        row_s = df_s.iloc[i]
        if pd.isna(row_s[0]) or "q" in str(row_s[0]).lower(): 
            break
            
        txt = str(row_s[0]).lower().replace(" ", "")
        if "total" in txt or "סהכ" in txt or "מדגם" in txt: 
            continue
        
        row_m = df_m.iloc[i] if i < len(df_m) else [0.0]*20
        
        s_val = pd.to_numeric(row_s[t_col], errors='coerce')
        m_val = pd.to_numeric(row_m[t_col], errors='coerce')
        
        labels.append(str(row_s[0]))
        s_vals.append(float(s_val) if pd.notna(s_val) else 0.0)
        m_vals.append(float(m_val) if pd.notna(m_val) else 0.0)

    if not labels:
        st.info("לא נמצאו נתונים כמותיים להצגה עבור שאלה זו בפילוח שנבחר.")
    else:
        fig = go.Figure()
        
        # הוספת קווי רקע מחברים (Dumbbell)
        for lbl, s_v, m_v in zip(labels, s_vals, m_vals):
            if m_v > 0 or "עיקרי" not in sel_q:
                fig.add_trace(go.Scatter(
                    x=[m_v, s_v], y=[lbl, lbl], mode="lines", 
                    line=dict(color="#f1f5f9", width=6), hoverinfo="skip", showlegend=False
                ))

        # סקר שילוב (נקודות כחולות)
        fig.add_trace(go.Scatter(
            x=s_vals, y=labels, mode="markers+text", name='סקר שילוב', 
            marker=dict(color='#2563eb', size=12, line=dict(color='white', width=2)),
            text=[f"{x:.1f}%" for x in s_vals], 
            textfont=dict(size=11, color="#2563eb", weight="bold"), 
            textposition="top center"
        ))
        
        # הוועדה למדרוג (נקודות כתומות)
        fig.add_trace(go.Scatter(
            x=m_vals, y=labels, mode="markers+text", name='הוועדה למדרוג', 
            marker=dict(color='#f97316', size=12, line=dict(color='white', width=2)),
            text=[f"{x:.1f}%" if x > 0 else "" for x in m_vals], 
            textfont=dict(size=11, color="#f97316", weight="bold"), 
            textposition="bottom center"
        ))

        # עיצוב הפריסה בצורה חסינת קריסות (ללא שימוש ב-autorange="reversed" על ציר ה-Y שגרם לשגיאה)
        fig.update_layout(
            margin=dict(l=40, r=260, t=50, b=60), # שומר מקום ענק בצד ימין לשמות הערוצים
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=max(400, len(labels) * 45), # גובה דינמי כדי למנוע דחיסה ויזואלית בשאלות ארוכות
            
            legend=dict(
                orientation="h", y=-0.15, x=0.5, xanchor="center", 
                font=dict(size=12, color="#475569")
            ),
            
            # ציר X עליון הפוך בצורה תקנית ומותאמת לטווחי אחוזים
            xaxis=dict(
                showgrid=True, gridcolor="#f1f5f9", side="top",
                range=[max(max(s_vals or [100]), max(m_vals or [100])) + 5, 0], # הפיכת הציר באמצעות הגדרת טווח מהגבוה לנמוך
                ticksuffix="%", tickfont=dict(size=11, color="#64748b")
            ),
            
            # ציר Y ימני יציב ללא פקודות הפוכות שגורמות לשגיאות ב-Plotly החדש
            yaxis=dict(
                side="right", 
                categoryorder="array",
                categoryarray=labels[::-1], # הפיכת סדר הרשימה בצורה ידנית בפייתון כדי שהשורה הראשונה תהיה למעלה
                tickfont=dict(size=13, color="#0f172a"),
                pad=20
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
