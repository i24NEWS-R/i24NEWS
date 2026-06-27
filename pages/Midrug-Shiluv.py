import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide", page_title="השוואת מדרוג ושילוב")

# הוספת עיצוב ליישור RTL וריווח כפתורי הרדיו (Radio buttons)
st.markdown("""
<style>
    * {
        direction: rtl !important;
        text-align: right !important;
    }
    /* ריווח כפתורי הבחירה בתפריט */
    div.row-widget.stRadio > div {
        gap: 1.5rem; 
        padding-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv(os.path.join(os.path.dirname(__file__), "Midrug-Shiluv.csv"))

df = load_data()
st.title("📊 השוואת מדרוג מול סקר שילוב")

# אזור הפילטרים
with st.container(border=True):
    cols = st.columns([1.5, 1, 2.5, 1, 2.5, 1.5, 3])
    cols[0].markdown("### 🎯 סינון נתונים")
    cols[1].write("ימי מדידה:")
    sel_p = cols[2].selectbox("", ["אמצע שבוע", "סוף שבוע"], label_visibility="collapsed")
    cols[3].write("גל מחקר:")
    waves = ["גל 19 במאי", "גל 25 במאי", "חיבור שני הגלים"] if sel_p == "אמצע שבוע" else ["גל 17 במאי", "גל 31 במאי", "חיבור שני הגלים"]
    sel_w = cols[4].selectbox("", waves, index=2, label_visibility="collapsed")
    
    cols[5].write("פילוח דמוגרפי:")
    if sel_w == "חיבור שני הגלים":
        opts = df[df['wave'] == "חיבור שני הגלים"].apply(lambda x: "כללי" if x['demo_category'] == "כללי" else f"{x['demo_category']} - {x['demo_value']}", axis=1).unique()
        sel_d = cols[6].selectbox("", opts, index=list(opts).index("כללי") if "כללי" in opts else 0, label_visibility="collapsed")
        cat, val = ("כללי", "סהכ") if sel_d == "כללי" else sel_d.split(" - ", 1)
    else:
        cols[6].selectbox("", ["כללי (זמין בחיבור הגלים)"], disabled=True, label_visibility="collapsed")
        cat, val = "כללי", "סהכ"

df_f = df[(df['period'] == sel_p) & (df['wave'] == sel_w) & (df['demo_category'] == cat) & (df['demo_value'] == val)]
st.divider()

# אזור התצוגה - תפריט לצד גרף
q_list = df_f['question_text'].unique().tolist()
if not q_list: 
    st.warning("אין נתונים עבור הסינון שנבחר.")
    st.stop()

menu_col, chart_col = st.columns([1.3, 2.5], gap="large")

with menu_col:
    with st.container(border=True):
        st.markdown("### 📋 בחר שאלה לניתוח:")
        sel_q = st.radio("", q_list)

plot_df = df_f[df_f['question_text'] == sel_q]
labels = plot_df['answer_text'].drop_duplicates().tolist()

with chart_col:
    # עטיפת אזור התרשים בתוך container עם מסגרת
    with st.container(border=True):
        if labels:
            fig = go.Figure()
            s_vals, m_vals = [], []
            
            for ans in labels:
                s_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]
                m_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]
                
                s_v = s_row['percentage'].values[0] if not s_row.empty else None
                m_v = m_row['percentage'].values[0] if not m_row.empty else None
                s_vals.append(s_v)
                m_vals.append(m_v)

                if s_v is not None and m_v is not None:
                    fig.add_trace(go.Scatter(x=[m_v, s_v], y=[ans, ans], mode="lines", line=dict(color="#d1d5db", width=2, dash="dot"), showlegend=False))
                    
            def add_points(vals, name, color, is_left):
                fig.add_trace(go.Scatter(
                    x=vals, y=labels, mode="markers+text", name=name,
                    marker=dict(color=color, size=14, line=dict(color='white', width=2)),
                    text=[f"<b>{x}%</b>" if x is not None else "" for x in vals],
                    textfont=dict(size=13, color=color, family="Assistant"),
                    textposition="middle left" if is_left else "middle right"
                ))

            add_points(s_vals, 'סקר שילוב', '#2563eb', True)
            add_points(m_vals, 'הוועדה למדרוג', '#ea580c', False)

            mx = max([v for v in s_vals + m_vals if v is not None], default=100)
            fig.update_layout(
                margin=dict(l=10, r=200, t=10, b=50), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=max(350, len(labels)*50), legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
                xaxis=dict(range=[mx*1.15, -(mx*0.3)], showgrid=True, gridcolor="#f3f4f6", zeroline=False, ticksuffix="%"),
                yaxis=dict(side="right", categoryorder="array", categoryarray=labels[::-1], tickfont=dict(size=14, weight="bold"))
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("אין נתונים להצגת תרשים עבור שאלה זו.")
