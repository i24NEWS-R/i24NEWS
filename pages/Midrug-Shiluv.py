import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide", page_title="השוואת מדרוג ושילוב")

# סגנון קבוע בלבד
st.markdown("""
<style>
    * {direction: rtl!important; text-align: right!important;}
    .stRadio > div {padding:1.5rem;}
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
        sel_q = st.radio("", q_list, label_visibility="collapsed")

plot_df = df_f[df_f['question_text'] == sel_q]
labels = plot_df['answer_text'].drop_duplicates().tolist()

with chart_col:
    with st.container(border=True):
        if labels:
            fig = go.Figure()
            
            # עטיפת לייבלים ארוכים למספר שורות באמצעות <br> או הגדרת חלוקה מובנית ב-Plotly
            wrapped_labels = [f"<span style='display: inline-block; width: 220px; white-space: normal;'>{lbl}</span>" for lbl in labels]

            # קווים מקווקווים
            for i, ans in enumerate(labels):
                s_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]
                m_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]
                
                s_v = s_row['percentage'].values[0] if not s_row.empty else None
                m_v = m_row['percentage'].values[0] if not m_row.empty else None
                
                if s_v is not None and m_v is not None:
                    fig.add_trace(go.Scatter(
                        x=[m_v, s_v], y=[wrapped_labels[i], wrapped_labels[i]], mode="lines", 
                        line=dict(color="#d1d5db", width=2, dash="dot"), showlegend=False
                    ))
            
            # פונקציה להוספת נקודות עם מספרים ו-Hover מדויק
            def add_points(source_filter, source_name, color, is_first_source):
                x_vals, y_vals, hover_vals, txt_vals, txt_pos = [], [], [], [], []
                
                for i, ans in enumerate(labels):
                    row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == source_filter)]
                    val = row['percentage'].values[0] if not row.empty else None
                    
                    x_vals.append(val)
                    y_vals.append(wrapped_labels[i])
                    
                    if val is not None:
                        hover_vals.append(f"<b>{source_name}</b><br>אחוז: {val}%<extra></extra>")
                        txt_vals.append(f"<b>{val}%</b>")
                        
                        # לוגיקת מיקום המספרים: הנמוך תמיד מימין לבולט, הגבוה משמאל לבולט
                        s_val = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]['percentage'].values[0] if not plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')].empty else -1
                        m_val = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]['percentage'].values[0] if not plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')].empty else -1
                        
                        if s_val != -1 and m_val != -1:
                            if val == min(s_val, m_val):
                                txt_pos.append("middle right")
                            else:
                                txt_pos.append("middle left")
                        else:
                            txt_pos.append("middle center")
                    else:
                        hover_vals.append("")
                        txt_vals.append("")
                        txt_pos.append("middle center")
                        
                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_vals, mode="markers+text", name=source_name,
                    marker=dict(color=color, size=14, line=dict(color='white', width=2)),
                    text=txt_vals, textfont=dict(size=13, color=color),
                    textposition=txt_pos, hovertemplate=hover_vals
                ))

            add_points('שילוב', 'סקר שילוב', '#2563eb', True)
            add_points('מדרוג', 'הוועדה למדרוג', '#ea580c', False)

            v_all = plot_df['percentage'].dropna().tolist()
            mx = max(v_all, default=100)
            
            fig.update_layout(
                margin=dict(l=20, r=220, t=30, b=100), # מרווחים נדיבים למניעת חיתוך ודחיקת המקרא למטה
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                height=max(450, len(labels)*90), # הגדלה משמעותית של גובה התרשים והכרטיס
                legend=dict(
                    orientation="h", 
                    y=-0.35, # מיקום המקרא הרחק מהתשובות בתחתית
                    x=0.5, 
                    xanchor="center"
                ),
                xaxis=dict(
                    range=[0, mx*1.2], # מתחיל תמיד מ-0 בצורה קשיחה
                    showgrid=True, 
                    gridcolor="#f3f4f6", 
                    zeroline=False, 
                    ticksuffix="%"
                ),
                yaxis=dict(
                    side="left", # התשובות מוצגות כעת בבטחה מצד שמאל
                    categoryorder="array", 
                    categoryarray=wrapped_labels[::-1], 
                    tickfont=dict(size=13, weight="bold")
                )
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("אין נתונים להצגת תרשים עבור שאלה זו.")
