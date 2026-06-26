import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="דשבורד השוואת נתוני צפייה")

# הזרקת עיצוב פרימיום מבוסס כרטיסים נפרדים ומרווחים
st.markdown("""
    <style>
        .stApp { background-color: #f8fafc !important; }
        .main *, .stRadio *, .stSelectbox *, h1, h2, h3, h4 { 
            direction: rtl !important; 
            text-align: right !important; 
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        div[data-testid="stHorizontalBlock"] { direction: rtl !important; }
        
        /* כרטיס עליון מובלט למסננים */
        div[data-testid="stForm"], .stHorizontalBlock > div {
            background-color: white; padding: 25px; border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.04);
            border: 1px solid #f1f5f9;
        }
        
        /* כרטיס ימני מובלט לתפריט השאלות */
        div[data-testid="column"]:nth-of-type(1) > div {
            background-color: white; padding: 30px; border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.04);
            border: 1px solid #f1f5f9; margin-left: 15px;
        }
        
        /* כרטיס שמאלי מובלט לתרשים */
        div[data-testid="column"]:nth-of-type(2) > div {
            background-color: white; padding: 30px; border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.04);
            border: 1px solid #f1f5f9; margin-right: 15px;
        }
        
        .stSelectbox { margin-bottom: 5px; }
        .stRadio div[role="radiogroup"] { gap: 14px; }
        hr { border: none !important; margin: 20px 0 !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    m = pd.read_excel("השוואות.xlsx", sheet_name="מדרוג", header=None)
    s = pd.read_excel("השוואות.xlsx", sheet_name="שילוב", header=None)
    return m, s

df_m, df_s = load_data()
questions = {str(r[0]): i for i, r in df_s.iterrows() if "q" in str(r[0]).lower() or ":" in str(r[0])}

# בניית מילוי חכם לקטגוריות העליונות (מגדר, גיל וכו') כדי לחבר אותן לתתי-הקטגוריות
categories = list(df_s.iloc[0])
current_cat = ""
filled_categories = []
for cat in categories:
    if pd.notna(cat) and str(cat).strip() != "":
        current_cat = str(cat).strip()
    filled_categories.append(current_cat)

# יצירת רשימת פילטרים משולבת: "קטגוריה - ערך" עם מיפוי לאינדקס העמוד המקורי
demo_mapping = {"כללי": 3}  # ברירת מחדל לחיבור שניהם (עמוד 3 באקסל)
for col_idx in range(4, df_s.shape[1]):
    sub_cat = df_s.iloc[1, col_idx]
    if pd.notna(sub_cat) and str(sub_cat).strip() != "":
        main_cat = filled_categories[col_idx]
        display_name = f"{main_cat} - {str(sub_cat).strip()}"
        demo_mapping[display_name] = col_idx

st.markdown("<h1 style='color: #0f172a; margin-bottom: 25px; font-weight: 800; font-size: 2.3rem;'>📊 דשבורד השוואת נתוני צפייה</h1>", unsafe_allow_html=True)

with st.container():
    col_f1, col_f2 = st.columns(2)
    with col_f1: 
        wave = st.selectbox("בחרו גל:", ["חיבור שניהם", "גל 19 במאי", "גל 25 במאי"])
    with col_f2:
        if wave == "חיבור שניהם":
            # הצגת הרשימה המשולבת החדשה ("מגדר - גברים" וכו')
            selected_demo_display = st.selectbox("בחרו פילטר דמוגרפי:", list(demo_mapping.keys()))
            t_col = demo_mapping[selected_demo_display]
        else:
            st.selectbox("בחרו פילטר דמוגרפי:", ["נעול - פעיל רק בגל מאוחד"], disabled=True)
            t_col = 1 if wave == "גל 19 במאי" else 2

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

col_side, col_chart = st.columns([1, 2.6])

with col_side:
    st.markdown("<h3 style='color: #0f172a; margin-bottom: 20px; font-weight: 700; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px;'>📋 תפריט שאלות</h3>", unsafe_allow_html=True)
    sel_q = st.radio("בחרו שאלה מהרשימה:", list(questions.keys()))
    start = questions[sel_q]

labels, s_vals, m_vals = [], [], []
for i in range(start + 1, len(df_s)):
    row_s, row_m = df_s.iloc[i], df_m.iloc[i]
    if pd.isna(row_s[0]) or str(row_s[0]).strip() == "" or "q" in str(row_s[0]).lower(): 
        break
    if any(x in str(row_s[0]).lower() for x in ["total", "סה\"כ"]): 
        continue
    labels.append(str(row_s[0]))
    s_vals.append(pd.to_numeric(row_s[t_col], errors='coerce') or 0.0)
    m_vals.append(pd.to_numeric(row_m[t_col], errors='coerce') or 0.0)

with col_chart:
    q_code = sel_q.split(':')[0]
    q_text = sel_q.split(':', 1)[1] if ':' in sel_q else ""
    
    st.markdown(f"""
        <div style='border-bottom: 2px solid #f1f5f9; padding-bottom: 12px; margin-bottom: 25px;'>
            <h3 style='color: #0f172a; margin: 0; font-weight: 700;'>📈 תרשים השוואתי: {q_code}</h3>
            <p style='color: #64748b; margin: 6px 0 0 0; font-size: 0.95rem; line-height: 1.5;'>{q_text}</p>
        </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure()
    
    for lbl, s_v, m_v in zip(labels, s_vals, m_vals):
        if m_v > 0 or "עיקרי" not in sel_q:
            fig.add_trace(go.Scatter(
                x=[m_v, s_v], y=[lbl, lbl], 
                mode="lines", 
                line=dict(color="#e2e8f0", width=4), 
                showlegend=False
            ))
    
    fig.add_trace(go.Scatter(
        x=s_vals, y=labels, mode="markers+text", 
        name='סקר שילוב (דיווח)', 
        marker=dict(color='#2563eb', size=14), 
        text=[f"{x:.1f}%" for x in s_vals], 
        textposition="top center", 
        textfont=dict(size=11, weight="bold")
    ))
    
    fig.add_trace(go.Scatter(
        x=m_vals, y=labels, mode="markers+text", 
        name='הוועדה למדרוג (פאנל)', 
        marker=dict(color='#ea580c', size=14), 
        text=[f"{x:.1f}%" if x > 0 else "" for x in m_vals], 
        textposition="bottom center", 
        textfont=dict(size=11, weight="bold")
    ))
    
    fig.update_layout(height=520)
    fig.update_layout(margin=dict(l=10, r=20, t=20, b=10))
    fig.update_layout(paper_bgcolor='white', plot_bgcolor='white')
    fig.update_layout(legend=dict(orientation="h", y=-0.14, x=0.5, xanchor="center", font=dict(size=12)))
    
    fig.update_layout(xaxis=dict(
        side="top", 
        gridcolor="#f8fafc", 
        autorange="reversed", 
        tickfont=dict(size=11, color="#64748b")
    ))
    
    fig.update_layout(yaxis=dict(
        autorange="reversed", 
        side="right", 
        tickfont=dict(size=13, weight="bold", color="#1e293b")
    ))
    
    st.plotly_chart(fig, use_container_width=True)
