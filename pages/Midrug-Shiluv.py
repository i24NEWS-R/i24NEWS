import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import math

# ==========================================
# 1. הגדרת עמוד והזרקת עיצוב מתוקן (RTL + Sticky + Wrap)
# ==========================================
st.set_page_config(layout="wide", page_title="השוואת מדרוג ושילוב")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;500;700&display=swap');
        
        /* יישור RTL גורף */
        .stApp, .stApp * {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Assistant', sans-serif !important;
        }
        
        .stApp {
            background-color: #f8f9fa !important;
        }
        
        /* פתרון בעיית הסטיקי: דריסה של חסימות Streamlit */
        div[data-testid="stMain"] > div {
            overflow: visible !important;
        }
        
        /* כרטיסים לבנים נקיים */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff !important;
            padding: 24px !important;
            border-radius: 12px !important; 
            border: none !important;
            box-shadow: 0px 2px 1px -1px rgba(0,0,0,0.05), 0px 1px 1px 0px rgba(0,0,0,0.03), 0px 1px 3px 0px rgba(0,0,0,0.03) !important;
        }
        
        /* קיבוע הכרטיס הראשון (הפילטרים) בגלילה */
        div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type {
            position: -webkit-sticky !important;
            position: sticky !important;
            top: 2.875rem !important; /* ממקם את זה בדיוק מתחת לסרגל העליון של סטרים ליט */
            z-index: 99999 !important;
            background-color: rgba(255, 255, 255, 0.98) !important;
            backdrop-filter: blur(8px);
            padding: 12px 24px !important;
            border-bottom: 1px solid #e8eaed !important;
        }
        
        h2 {
            color: #202124 !important;
            font-weight: 700 !important;
            margin-bottom: 20px !important;
            padding-right: 15px;
        }
        
        div[data-testid="column"] {
            background-color: transparent !important;
            padding: 0 !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        /* שאלות תפריט הצד - גודל 14px */
        div[data-testid="stRadio"] label {
            padding: 8px 12px !important;
            border-radius: 8px !important;
            margin-bottom: 2px !important;
        }
        div[data-testid="stRadio"] label * {
            font-size: 14px !important;
            color: #3c4043 !important;
            font-weight: 400 !important;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #f1f3f4 !important; 
        }
        
        /* כותרות הפילטרים בשורה אחת */
        .filter-title {
            font-size: 1.25em !important;
            font-weight: 700 !important;
            color: #202124 !important;
            margin: 0 !important;
            display: flex;
            align-items: center;
            height: 100%;
            white-space: nowrap !important;
        }
        
        /* פתרון בעיית חריגת הטקסט של השאלה: מעבר שורות נקי */
        .question-title {
            font-size: 1.25em !important;
            font-weight: 700 !important;
            color: #202124 !important;
            margin-bottom: 25px !important;
            line-height: 1.5 !important;
            white-space: normal !important; 
            word-wrap: break-word !important;
            display: block !important;
        }
        
        /* כותרות התיבות מימין אליהן */
        div[data-testid="stSelectbox"] {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 10px !important;
            width: 100% !important;
        }
        div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] {
            min-width: fit-content !important;
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p {
            font-weight: 600 !important;
            color: #5f6368 !important;
            font-size: 14px !important;
            margin: 0 !important;
            white-space: nowrap !important;
        }
        div[data-testid="stSelectbox"] > div:nth-of-type(2) {
            flex-grow: 1 !important;
            width: 100% !important;
        }
        
        /* יישור הרשימות הנפתחות */
        div[data-baseweb="select"] *, div[data-testid="stSelectbox"] * {
            text-align: right !important;
            direction: rtl !important;
        }
        div[data-baseweb="popover"], ul[role="listbox"], li[role="option"] {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* פתרון מוחלט: חסימת כתיבה לתיבות ע"י העלמת סמן ההקלדה מהטור השני והשלישי */
        div[data-testid="column"]:nth-child(2) [data-baseweb="select"] input,
        div[data-testid="column"]:nth-child(3) [data-baseweb="select"] input {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        path = os.path.join(os.path.dirname(__file__), "Midrug-Shiluv.csv")
        return pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"שגיאה: הקובץ Midrug-Shiluv.csv לא נמצא.")
        st.stop()

df = load_data()

st.markdown("<h2>📊 השוואת מדרוג מול סקר שילוב</h2>", unsafe_allow_html=True)

# ==========================================
# פילטרים
# ==========================================
with st.container(border=True):
    col_title, col_f1, col_f2, col_f3 = st.columns([1.0, 1.8, 2.0, 2.8], gap="medium")
    
    with col_title:
        st.markdown("<p class='filter-title'>🎯 סינון נתונים</p>", unsafe_allow_html=True)
        
    with col_f1:
        selected_period = st.selectbox("ימי מדידה:", ["אמצע שבוע", "סוף שבוע"], index=0)
    
    with col_f2:
        if selected_period == "אמצע שבוע":
            wave_options = ["גל 19 במאי", "גל 25 במאי", "חיבור שני הגלים"]
        else:
            wave_options = ["גל 17 במאי", "גל 31 במאי", "חיבור שני הגלים"]
        selected_wave = st.selectbox("גל מחקר:", wave_options, index=2)
        
    with col_f3:
        if selected_wave == "חיבור שני הגלים":
            df_demo_src = df[(df['period'] == selected_period) & (df['wave'] == "חיבור שני הגלים")].copy()
            
            df_demo_src['demo_display'] = df_demo_src.apply(
                lambda x: "כללי" if x['demo_category'] == "כללי" and x['demo_value'] == "סהכ" else f"{x['demo_category']} - {x['demo_value']}", axis=1
            )
            demo_options = df_demo_src['demo_display'].unique().tolist()
            
            default_idx = demo_options.index("כללי") if "כללי" in demo_options else 0
            selected_demo = st.selectbox("פילוח דמוגרפי:", demo_options, index=default_idx)
            
            if selected_demo == "כללי":
                sel_cat, sel_val = "כללי", "סהכ"
            else:
                sel_cat, sel_val = selected_demo.split(" - ", 1)
        else:
            st.selectbox("פילוח דמוגרפי:", ["כללי (זמין בחיבור הגלים)"], disabled=True)
            sel_cat, sel_val = "כללי", "סהכ"

df_filtered = df[(df['period'] == selected_period) & (df['wave'] == selected_wave) & (df['demo_category'] == sel_cat) & (df['demo_value'] == sel_val)]

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

col_side, col_chart = st.columns([1.3, 2.5], gap="large")

with col_side:
    with st.container(border=True):
        st.markdown("<p class='filter-title' style='margin-bottom: 20px !important;'>📋 בחר שאלה לניתוח:</p>", unsafe_allow_html=True)
        questions = df_filtered['question_text'].unique().tolist()
        if not questions:
            st.warning("אין נתונים זמינים לחיתוך זה.")
            st.stop()
        sel_q = st.radio("", questions, index=0, label_visibility="collapsed")

with col_chart:
    with st.container(border=True):
        # שימוש במחלקה החדשה שמאפשרת ירידת שורה
        st.markdown(f"<p class='question-title'>📋 {sel_q}</p>", unsafe_allow_html=True)
        
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
            st.info("לא נמצאו נתונים להצגה.")
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

            for lbl, s_v, m_v in zip(labels, s_vals, m_vals):
                if s_v is not None and m_v is not None:
                    fig.add_trace(go.Scatter(
                        x=[m_v, s_v], y=[lbl, lbl], mode="lines", 
                        line=dict(color="#bdc1c6", width=2, dash="dot"), hoverinfo="skip", showlegend=False
                    ))

            fig.add_trace(go.Scatter(
                x=s_vals, y=labels, mode="markers+text", name='סקר שילוב', 
                marker=dict(color='#1a73e8', size=14, line=dict(color='white', width=2)),
                text=[f"<b>{x}%</b>" if x is not None else "" for x in s_vals], 
                textfont=dict(size=13, color="#1a73e8", family="Assistant"), 
                textposition="middle left",
                hovertemplate=s_hover_texts
            ))
            
            fig.add_trace(go.Scatter(
                x=m_vals, y=labels, mode="markers+text", name='הוועדה למדרוג', 
                marker=dict(color='#fb8c00', size=14, line=dict(color='white', width=2)),
                text=[f"<b>{x}%</b>" if x is not None else "" for x in m_vals], 
                textfont=dict(size=13, color="#fb8c00", family="Assistant"), 
                textposition="middle right",
                hovertemplate=m_hover_texts
            ))

            valid_vals = [v for v in s_vals + m_vals if v is not None]
            max_val = max(valid_vals) if valid_vals else 100
            safe_max = max_val + (max_val * 0.15)
            safe_min = -(max_val * 0.3)
            
            step = 5 if max_val <= 30 else 10
            clean_ticks = [i for i in range(0, int(safe_max) + step, step)]

            fig.update_layout(
                margin=dict(l=10, r=200, t=10, b=80), 
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=max(400, len(labels) * 55), 
                font=dict(family="Assistant", color="#3c4043"),
                
                legend=dict(
                    orientation="h", y=-0.15, x=0.5, xanchor="center", yanchor="top",
                    font=dict(size=14, color="#5f6368")
                ),
                
                xaxis=dict(
                    range=[safe_max, safe_min],
                    tickvals=clean_ticks,
                    showgrid=True, 
                    gridcolor="#e8eaed", 
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
