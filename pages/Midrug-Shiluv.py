import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import math

# ==========================================
# 1. הגדרת עמוד והזרקת עיצוב פרימיום
# ==========================================
st.set_page_config(layout="wide", page_title="השוואת מדרוג ושילוב")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;800&display=swap');
        
        .stApp, .stApp * {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Assistant', sans-serif !important;
        }
        
        .stApp {
            background-color: #f0f2f6 !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff !important;
            padding: 20px 25px !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important;
            border: 1px solid #e2e8f0 !important;
        }
        
        h2 {
            color: #0f172a !important;
            font-weight: 800 !important;
            margin-bottom: 20px !important;
            padding-right: 15px;
        }
        
        div[data-testid="column"] {
            background-color: transparent !important;
            padding: 0 !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        div[data-baseweb="select"], div[data-baseweb="select"] > div { direction: rtl !important; }
        div[data-baseweb="popover"], ul[role="listbox"] { direction: rtl !important; text-align: right !important; }
        ul[role="listbox"] li { text-align: right !important; direction: rtl !important; padding-right: 15px !important; }
        
        div[data-testid="stRadio"] label {
            padding: 10px 15px !important;
            border-radius: 8px !important;
            background-color: transparent !important;
            margin-bottom: 4px !important;
            border: none !important;
            transition: background 0.2s ease;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #f1f5f9 !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. טעינת נתונים חכמה (עם Caching לביצועים)
# ==========================================
@st.cache_data
def load_data():
    try:
        path = os.path.join(os.path.dirname(__file__), "Midrug-Shiluv.csv")
        return pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"שגיאה: הקובץ Midrug-Shiluv.csv לא נמצא. ודא שהוא ממוקם בתיקייה הנכונה.")
        st.stop()

df = load_data()

st.markdown("<h2>📊 השוואת מדרוג מול סקר שילוב</h2>", unsafe_allow_html=True)

# ==========================================
# 3. פילטרים דינמיים (נבנים אוטומטית מהדאטה)
# ==========================================
with st.container(border=True):
    st.markdown("<p style='font-weight: 700; color: #1e293b; margin-bottom: 5px;'>🎯 סינון נתונים</p>", unsafe_allow_html=True)
    col_f1, col_f2, col_spacer = st.columns([1.5, 1.5, 4])
    
    with col_f1:
        # שליפת הגלים הקיימים
        waves = df['wave'].unique().tolist()
        selected_wave = st.selectbox("גל מחקר:", waves)
    
    with col_f2:
        # יצירת אפשרויות הדמוגרפיה רק עבור הגל הנבחר (למנוע בחירות ריקות)
        df_wave = df[df['wave'] == selected_wave].copy()
        
        # בניית רשימת התצוגה, למשל: "מגדר - נשים"
        df_wave['demo_display'] = df_wave['demo_category'] + " - " + df_wave['demo_value']
        demo_options = df_wave['demo_display'].unique().tolist()
        
        # קביעת ברירת המחדל ל"כללי - סהכ" אם קיים
        default_idx = demo_options.index("כללי - סהכ") if "כללי - סהכ" in demo_options else 0
        selected_demo = st.selectbox("פילוח דמוגרפי:", demo_options, index=default_idx)

# חיתוך הדאטה פריים לפי הפילוח שנבחר
sel_cat, sel_val = selected_demo.split(" - ", 1)
df_filtered = df_wave[(df_wave['demo_category'] == sel_cat) & (df_wave['demo_value'] == sel_val)]

# ==========================================
# 4. מבנה מרכזי (תפריט ימין ותרשים שמאל)
# ==========================================
col_side, col_chart = st.columns([1.2, 2.5], gap="large")

with col_side:
    with st.container(border=True):
        st.markdown("<p style='font-weight: 700; color: #334155; margin-bottom: 10px; padding-right:10px;'>📋 בחר שאלה לניתוח:</p>", unsafe_allow_html=True)
        # שאיבת השאלות הזמינות בפילוח הנוכחי
        questions = df_filtered['question_text'].unique().tolist()
        if not questions:
            st.warning("אין נתונים לפילוח זה.")
            st.stop()
        sel_q = st.radio("", questions, label_visibility="collapsed")

with col_chart:
    with st.container(border=True):
        # סינון סופי רק לשאלה שנבחרה
        plot_df = df_filtered[df_filtered['question_text'] == sel_q]
        
        # שמירה על סדר התשובות המקורי
        answers = plot_df['answer_text'].drop_duplicates().tolist()
        
        labels, s_vals, m_vals, s_ns = [], [], [], []
        
        # בניית הרשימות עבור Plotly
        for ans in answers:
            ans_data = plot_df[plot_df['answer_text'] == ans]
            s_row = ans_data[ans_data['source'] == 'שילוב']
            m_row = ans_data[ans_data['source'] == 'מדרוג']
            
            s_val = s_row['percentage'].values[0] if not s_row.empty and pd.notna(s_row['percentage'].values[0]) else None
            m_val = m_row['percentage'].values[0] if not m_row.empty and pd.notna(m_row['percentage'].values[0]) else None
            s_n = s_row['n_size'].values[0] if not s_row.empty and pd.notna(s_row['n_size'].values[0]) else None
            
            if s_val is not None or m_val is not None:
                labels.append(ans)
                s_vals.append(s_val)
                m_vals.append(m_val)
                s_ns.append(s_n)

        if not labels:
            st.info("לא נמצאו נתונים להצגה עבור השאלה בפילוח זה.")
        else:
            fig = go.Figure()
            
            # בניית הטקסטים שיוצגו ב-Hover, כולל גודל המדגם N
            s_hover_texts = []
            for v, n in zip(s_vals, s_ns):
                if v is not None:
                    n_txt = f"<br><b>גודל מדגם (N):</b> {int(n)}" if n is not None and not math.isnan(n) else ""
                    s_hover_texts.append(f"<b>סקר שילוב:</b> {v}%{n_txt}<extra></extra>")
                else:
                    s_hover_texts.append("")
                    
            m_hover_texts = [f"<b>מדרוג:</b> {v}%<extra></extra>" if v is not None else "" for v in m_vals]

            # 1. קווים מחברים
            for lbl, s_v, m_v in zip(labels, s_vals, m_vals):
                if s_v is not None and m_v is not None:
                    fig.add_trace(go.Scatter(
                        x=[m_v, s_v], y=[lbl, lbl], mode="lines", 
                        line=dict(color="#cbd5e1", width=2, dash="dot"), hoverinfo="skip", showlegend=False
                    ))

            # 2. נקודות סקר שילוב
            fig.add_trace(go.Scatter(
                x=s_vals, y=labels, mode="markers+text", name='סקר שילוב', 
                marker=dict(color='#3b82f6', size=14, line=dict(color='white', width=3)),
                text=[f"<b>{x}%</b>" if x is not None else "" for x in s_vals], 
                textfont=dict(size=13, color="#2563eb", family="Assistant"), 
                textposition="top center",
                hovertemplate=s_hover_texts
            ))
            
            # 3. נקודות מדרוג
            fig.add_trace(go.Scatter(
                x=m_vals, y=labels, mode="markers+text", name='הוועדה למדרוג', 
                marker=dict(color='#f97316', size=14, line=dict(color='white', width=3)),
                text=[f"<b>{x}%</b>" if x is not None else "" for x in m_vals], 
                textfont=dict(size=13, color="#ea580c", family="Assistant"), 
                textposition="bottom center",
                hovertemplate=m_hover_texts
            ))

            # חישוב טווח דינמי ונקי (מניעת חפיפת טקסט על ציר ה-Y ומניעת מספרים שליליים)
            valid_vals = [v for v in s_vals + m_vals if v is not None]
            max_val = max(valid_vals) if valid_vals else 100
            
            safe_max = max_val + (max_val * 0.15)
            safe_min = -(max_val * 0.3)
            
            step = 5 if max_val <= 30 else 10
            clean_ticks = [i for i in range(0, int(safe_max) + step, step)]

            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=40), 
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=max(450, len(labels) * 55), 
                font=dict(family="Assistant"),
                
                legend=dict(
                    orientation="h", y=-0.1, x=0.5, xanchor="center", 
                    font=dict(size=14, color="#64748b")
                ),
                
                xaxis=dict(
                    range=[safe_max, safe_min],
                    tickvals=clean_ticks,
                    showgrid=True, 
                    gridcolor="#f1f5f9", 
                    zeroline=False,
                    side="top",
                    ticksuffix="%", 
                    tickfont=dict(size=12, color="#94a3b8")
                ),
                
                yaxis=dict(
                    side="right", 
                    categoryorder="array",
                    categoryarray=labels[::-1], 
                    tickfont=dict(size=14, color="#334155", weight="bold"),
                    showgrid=False
                )
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
