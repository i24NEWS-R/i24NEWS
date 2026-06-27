import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import math

st.set_page_config(layout="wide", page_title="השוואת מדרוג ושילוב")

# ==========================================
# 1. יישור RTL גורף (מוטמע ב-Streamlit בדרך טבעית)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. לוגיקת נתונים
# ==========================================
@st.cache_data
def load_data():
    try:
        path = os.path.join(os.path.dirname(__file__), "Midrug-Shiluv.csv")
        return pd.read_csv(path)
    except FileNotFoundError:
        st.error("שגיאה: הקובץ Midrug-Shiluv.csv לא נמצא.")
        st.stop()

df = load_data()

st.title("📊 השוואת מדרוג מול סקר שילוב")

# ==========================================
# 3. אזור הפילטרים בשורה אחת אופקית (פייתון טהור)
# ==========================================
with st.container(border=True):
    # פריסה בשורה אחת באמצעות חלוקה מדויקת של טורים
    f_title, c1, c2, c3 = st.columns([1.5, 3.5, 3.5, 3.5], gap="medium")
    
    with f_title:
        st.markdown("### 🎯 סינון נתונים")
    
    with c1:
        sel_period = st.selectbox("ימי מדידה:", ["אמצע שבוע", "סוף שבוע"], index=0)
    
    with c2:
        if sel_period == "אמצע שבוע":
            waves = ["גל 19 במאי", "גל 25 במאי", "חיבור שני הגלים"]
        else:
            waves = ["גל 17 במאי", "גל 31 במאי", "חיבור שני הגלים"]
        sel_wave = st.selectbox("גל מחקר:", waves, index=2)
    
    with c3:
        if sel_wave == "חיבור שני הגלים":
            df_w = df[(df['period'] == sel_period) & (df['wave'] == sel_wave)]
            opts = df_w.apply(
                lambda x: "כללי" if x['demo_category'] == "כללי" and x['demo_value'] == "סהכ" else f"{x['demo_category']} - {x['demo_value']}", axis=1
            ).unique()
            
            default_idx = list(opts).index("כללי") if "כללי" in opts else 0
            sel_demo = st.selectbox("פילוח דמוגרפי:", opts, index=default_idx)
            
            if sel_demo == "כללי":
                cat, val = "כללי", "סהכ"
            else:
                cat, val = sel_demo.split(" - ", 1)
        else:
            st.selectbox("פילוח דמוגרפי:", ["כללי (פילוח זמין בחיבור גלים)"], disabled=True)
            cat, val = "כללי", "סהכ"

df_filtered = df[(df['period'] == sel_period) & (df['wave'] == sel_wave) & (df['demo_category'] == cat) & (df['demo_value'] == val)]

st.divider()

# ==========================================
# 4. אזור התרשים והשאלות
# ==========================================
col_side, col_chart = st.columns([1.3, 2.5], gap="large")

with col_side:
    with st.container(border=True):
        st.markdown("### 📋 בחר שאלה לניתוח:")
        questions = df_filtered['question_text'].unique().tolist()
        if not questions:
            st.warning("אין נתונים לחיתוך זה.")
            st.stop()
        sel_q = st.radio("", questions, index=0, label_visibility="collapsed")

with col_chart:
    with st.container(border=True):
        st.markdown(f"### 📋 {sel_q}")
        
        plot_df = df_filtered[df_filtered['question_text'] == sel_q]
        labels = plot_df['answer_text'].drop_duplicates().tolist()
        
        if not labels:
            st.info("אין נתונים להצגה.")
        else:
            fig = go.Figure()
            s_vals, m_vals, s_ns = [], [], []
            
            for ans in labels:
                ans_data = plot_df[plot_df['answer_text'] == ans]
                s_row = ans_data[ans_data['source'] == 'שילוב']
                m_row = ans_data[ans_data['source'] == 'מדרוג']
                
                s_vals.append(s_row['percentage'].values[0] if not s_row.empty else None)
                m_vals.append(m_row['percentage'].values[0] if not m_row.empty else None)
                s_ns.append(s_row['n_size'].values[0] if not s_row.empty else None)

            # קווים מחברים
            for lbl, s, m in zip(labels, s_vals, m_vals):
                if s is not None and m is not None:
                    fig.add_trace(go.Scatter(
                        x=[m, s], y=[lbl, lbl], mode="lines", 
                        line=dict(color="#d1d5db", width=2, dash="dot"), showlegend=False
                    ))
                    
            # פונקציה להוספת נקודות
            def add_points(vals, name, color, is_left, ns=None):
                texts = [f"<b>{v}%</b>" if v is not None else "" for v in vals]
                hover = []
                for v, n in zip(vals, ns or [None]*len(vals)):
                    if v is None: hover.append("")
                    else: hover.append(f"<b>{name}:</b> {v}%" + (f"<br><b>N:</b> {int(n)}" if n and not math.isnan(n) else "") + "<extra></extra>")
                    
                fig.add_trace(go.Scatter(
                    x=vals, y=labels, mode="markers+text", name=name,
                    marker=dict(color=color, size=14, line=dict(color='white', width=2)),
                    text=texts, textposition="middle left" if is_left else "middle right",
                    hovertemplate=hover, textfont=dict(size=14, color=color, family="Assistant")
                ))

            add_points(s_vals, 'סקר שילוב', '#2563eb', True, s_ns)
            add_points(m_vals, 'הוועדה למדרוג', '#ea580c', False)

            # חישוב שוליים לגרף
            v_all = [v for v in s_vals + m_vals if v is not None]
            mx = max(v_all) if v_all else 100
            
            fig.update_layout(
                margin=dict(l=10, r=200, t=10, b=50),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=max(350, len(labels)*50),
                legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
                xaxis=dict(
                    range=[mx*1.15, -(mx*0.3)], showgrid=True, gridcolor="#f3f4f6", 
                    zeroline=False, ticksuffix="%"
                ),
                yaxis=dict(
                    side="right", categoryorder="array", categoryarray=labels[::-1], 
                    tickfont=dict(size=14, weight="bold")
                )
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
