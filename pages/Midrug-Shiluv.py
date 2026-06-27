import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import math

# ==========================================
# 1. הגדרת עמוד והזרקת עיצוב Material Design
# ==========================================
st.set_page_config(layout="wide", page_title="השוואת מדרוג ושילוב")

st.markdown("""
    <style>
        /* יבוא פונט - Assistant הוא ה"מקביל" העברי של Roboto מבית גוגל */
        @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;500;700&display=swap');
        
        .stApp, .stApp * {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Assistant', sans-serif !important;
        }
        
        /* רקע Google סטנדרטי */
        .stApp {
            background-color: #f8f9fa !important;
        }
        
        /* Material Cards - שימוש ב-Elevation 1 (הצללה קלה וחדה) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff !important;
            padding: 24px !important;
            border-radius: 12px !important; /* MD3 משתמש בפינות מעוגלות של 12-16px */
            border: none !important;
            box-shadow: 0px 2px 1px -1px rgba(0,0,0,0.2), 0px 1px 1px 0px rgba(0,0,0,0.14), 0px 1px 3px 0px rgba(0,0,0,0.12) !important;
        }
        
        /* כותרת ראשית (Google Typography - Headline) */
        h2 {
            color: #202124 !important;
            font-weight: 500 !important;
            margin-bottom: 24px !important;
            padding-right: 15px;
            letter-spacing: -0.2px !important;
        }
        
        div[data-testid="column"] {
            background-color: transparent !important;
            padding: 0 !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        /* תפריטים וטפסים - Material Outlined */
        div[data-baseweb="select"], div[data-baseweb="select"] > div { direction: rtl !important; }
        div[data-baseweb="popover"], ul[role="listbox"] { direction: rtl !important; text-align: right !important; }
        ul[role="listbox"] li { text-align: right !important; direction: rtl !important; padding-right: 15px !important; }
        
        /* כפתורי רדיו דמויי Material List Items */
        div[data-testid="stRadio"] label {
            padding: 12px 16px !important;
            border-radius: 8px !important;
            background-color: transparent !important;
            margin-bottom: 2px !important;
            border: none !important;
            transition: background 0.2s ease;
            color: #3c4043 !important;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #f1f3f4 !important; /* Material Gray 100 */
        }
        
        /* כותרות קטנות בכרטיסיות (Subtitle) */
        p {
            color: #5f6368 !important;
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
    st.markdown("<p style='font-weight: 700; color: #202124; margin-bottom: 5px; font-size: 1.1em;'>🎯 סינון נתונים</p>", unsafe_allow_html=True)
    col_f1, col_f2, col_spacer = st.columns([1.5, 1.5, 4])
    
    with col_f1:
        waves = df['wave'].unique().tolist()
        selected_wave = st.selectbox("גל מחקר:", waves)
    
    with col_f2:
        df_wave = df[df['wave'] == selected_wave].copy()
        df_wave['demo_display'] = df_wave['demo_category'] + " - " + df_wave['demo_value']
        demo_options = df_wave['demo_display'].unique().tolist()
        
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
        st.markdown("<p style='font-weight: 700; color: #202124; margin-bottom: 12px; padding-right:10px;'>📋 בחר שאלה לניתוח:</p>", unsafe_allow_html=True)
        questions = df_filtered['question_text'].unique().tolist()
        if not questions:
            st.warning("אין נתונים לפילוח זה.")
            st.stop()
        sel_q = st.radio("", questions, label_visibility="collapsed")

with col_chart:
    with st.container(border=True):
        plot_df = df_filtered[df_filtered['question_text'] == sel_q]
        answers = plot_df['answer_text'].drop_duplicates().tolist()
        
        labels, s_vals, m_vals, s_ns = [], [], [], []
        
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
            
            s_hover_texts = []
            for v, n in zip(s_vals, s_ns):
                if v is not None:
                    n_txt = f"<br><b>גודל מדגם (N):</b> {int(n)}" if n is not None and not math.isnan(n) else ""
                    s_hover_texts.append(f"<b>סקר שילוב:</b> {v}%{n_txt}<extra></extra>")
                else:
                    s_hover_texts.append("")
                    
            m_hover_texts = [f"<b>מדרוג:</b> {v}%<extra></extra>" if v is not None else "" for v in m_vals]

            # 1. קווים מחברים (Material Grey 400)
            for lbl, s_v, m_v in zip(labels, s_vals, m_vals):
                if s_v is not None and m_v is not None:
                    fig.add_trace(go.Scatter(
                        x=[m_v, s_v], y=[lbl, lbl], mode="lines", 
                        line=dict(color="#bdc1c6", width=2, dash="dot"), hoverinfo="skip", showlegend=False
                    ))

            # 2. נקודות סקר שילוב (Material Blue)
            fig.add_trace(go.Scatter(
                x=s_vals, y=labels, mode="markers+text", name='סקר שילוב', 
                marker=dict(color='#1a73e8', size=14, line=dict(color='white', width=2)),
                text=[f"<b>{x}%</b>" if x is not None else "" for x in s_vals], 
                textfont=dict(size=13, color="#1a73e8", family="Assistant"), 
                textposition="top center",
                hovertemplate=s_hover_texts
            ))
            
            # 3. נקודות מדרוג (Material Orange/Amber)
            fig.add_trace(go.Scatter(
                x=m_vals, y=labels, mode="markers+text", name='הוועדה למדרוג', 
                marker=dict(color='#fb8c00', size=14, line=dict(color='white', width=2)),
                text=[f"<b>{x}%</b>" if x is not None else "" for x in m_vals], 
                textfont=dict(size=13, color="#fb8c00", family="Assistant"), 
                textposition="bottom center",
                hovertemplate=m_hover_texts
            ))

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
                font=dict(family="Assistant", color="#3c4043"),
                
                legend=dict(
                    orientation="h", y=-0.1, x=0.5, xanchor="center", 
                    font=dict(size=14, color="#5f6368")
                ),
                
                xaxis=dict(
                    range=[safe_max, safe_min],
                    tickvals=clean_ticks,
                    showgrid=True, 
                    gridcolor="#e8eaed", /* Material Grey 200 */
                    zeroline=False,
                    side="top",
                    ticksuffix="%", 
                    tickfont=dict(size=12, color="#80868b")
                ),
                
                yaxis=dict(
                    side="right", 
                    categoryorder="array",
                    categoryarray=labels[::-1], 
                    tickfont=dict(size=14, color="#202124", weight="bold"),
                    showgrid=False
                )
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
