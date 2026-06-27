import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import random

st.set_page_config(layout="wide", page_title="השוואת מדרוג ושילוב")

# סגנון קבוע, דריסת כיווניות לתרשים וריווח בתפריט הרדיו
st.markdown("""
<style>
    * {direction: rtl!important; text-align: right!important;}
    
    /* מרווח וקו תחתון בין אפשרויות הרדיו, כפתור ימני וטקסט שמאלי */
    .stRadio label {
        padding: 15px 0 !important;
        border-bottom: 1px solid #f3f4f6;
        display: flex !important;
        align-items: center !important;
        flex-direction: row !important; /* כפתור הרדיו יופיע מימין והטקסט משמאלו */
        justify-content: flex-start !important;
    }
    
    /* הוספת מרווח בין כפתור הבחירה העגול לטקסט שמופיע משמאלו */
    .stRadio label input[type="radio"] {
        margin-left: 15px !important; /* מרחיק את העיגול ימינה מהקצה, והטקסט יקבל מרווח ממנו */
        margin-right: 0 !important;
    }
    
    /* הרחקת כותרת/נוסח השאלה מכפתור הבחירה הראשון ברשימה */
    div.row-widget.stRadio > div > label:first-of-type {
        margin-bottom: 10px;
    }
    
    /* דריסת כיווניות עבור אזור התרשים בלבד */
    div[data-testid="stPlotlyChart"] * {
        direction: ltr !important;
        text-align: left !important;
        unicode-bidi: isolate !important;
    }
    div[data-testid="stPlotlyChart"] {
        direction: ltr !important;
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv(os.path.join(os.path.dirname(__file__), "Midrug-Shiluv.csv"))

df = load_data()
st.title("📊 השוואת מדרוג מול סקר שילוב")

# אזור הפילטרים - הקצאת רוחב גדולה יותר לעמודת הכותרת למניעת שבירת שורות
with st.container(border=True):
    cols = st.columns([2.2, 1, 2.5, 1, 2.5, 1.5, 3])
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

# הוסרו הקו המפריד והרווח המיותר מתחתיו

df_f = df[(df['period'] == sel_p) & (df['wave'] == sel_w) & (df['demo_category'] == cat) & (df['demo_value'] == val)]

# אזור התצוגה - תפריט לצד גרף
q_list = df_f['question_text'].unique().tolist()
if not q_list: 
    st.warning("אין נתונים עבור הסינון שנבחר.")
    st.stop()

menu_col, chart_col = st.columns([1.3, 2.5], gap="large")

with menu_col:
    with st.container(border=True):
        st.markdown("### 📋 בחירת שאלה:")
        st.write("") # מרווח קל בין הכותרת לכפתורי הרדיו
        sel_q = st.radio("", q_list, index=0, label_visibility="collapsed")

plot_df = df_f[df_f['question_text'] == sel_q]
labels = plot_df['answer_text'].drop_duplicates().tolist()

with chart_col:
    with st.container(border=True):
        if labels:
            # הצגת השאלה הנבחרה מעל התרשים באותו הגודל של הכותרות בתוספת אייקון
            st.markdown(f"### 📋 {sel_q}")
            st.write("")
            
            fig = go.Figure()
            
            # עטיפה להצגת טקסט ארוך במרווח מימין לתרשים (ללא חיתוך)
            wrapped_labels = [f"<span style='display: inline-block; width: 260px; white-space: normal; text-align: right;'>{lbl}</span>" for lbl in labels]
            
            # קווים מקווקווים המחברים בין הנקודות
            for i, ans in enumerate(labels):
                s_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]
                m_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]
                
                s_v = s_row['percentage'].values[0] if not s_row.empty else None
                m_v = m_row['percentage'].values[0] if not m_row.empty else None
                
                if s_v is not None and m_v is not None:
                    fig.add_trace(go.Scatter(
                        x=[m_v, s_v], y=[wrapped_labels[i], wrapped_labels[i]], mode="lines", 
                        line=dict(color="#d1d5db", width=2, dash="dot"), showlegend=False, hoverinfo="skip"
                    ))
            
            # הוספת הנקודות והטקסטים עם עיגול לספרה עשרונית אחת ויישום הכללים
            def add_points(source_filter, source_name):
                x_vals, y_vals, hover_vals, txt_vals, txt_pos = [], [], [], [], []
                
                for i, ans in enumerate(labels):
                    row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == source_filter)]
                    val = row['percentage'].values[0] if not row.empty else None
                    
                    if val is not None:
                        val = round(val, 1)  # עיגול לספרה אחת אחרי הנקודה
                    
                    x_vals.append(val)
                    y_vals.append(wrapped_labels[i])
                    
                    if val is not None:
                        hover_vals.append(f"<b>{source_name}</b><br>אחוז: {val}%<extra></extra>")
                        txt_vals.append(f"<b>{val}%</b>")
                        
                        s_val = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]['percentage'].values[0] if not plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')].empty else None
                        m_val = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]['percentage'].values[0] if not plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')].empty else None
                        
                        if s_val is not None and m_val is not None:
                            s_val = round(s_val, 1)
                            m_val = round(m_val, 1)
                            
                            if s_val == m_val:
                                # ערכים תואמים לחלוטין -> בחירה אקראית של מיקום (שמאל או ימין) כדי למנוע חפיפה
                                rand_pos = random.choice(["middle left", "middle right"])
                                if source_filter == "שילוב":
                                    txt_pos.append(rand_pos)
                                else:
                                    txt_pos.append("middle right" if rand_pos == "middle left" else "middle left")
                            # שני נתונים שונים -> הנמוך משמאל לבולט, הגבוה מימין לבולט
                            elif val < min(s_val, m_val) or val == min(s_val, m_val):
                                txt_pos.append("middle left")
                            else:
                                txt_pos.append("middle right")
                        else:
                            # נתון בודד יוצג תמיד לימין הבולט
                            txt_pos.append("middle right")
                    else:
                        hover_vals.append("")
                        txt_vals.append("")
                        txt_pos.append("middle center")
                        
                color_map = {'סקר שילוב': '#2563eb', 'הוועדה למדרוג': '#ea580c'}
                fig.add_trace(go.Scatter(
                    x=x_vals, y=y_vals, mode="markers+text", name=source_name,
                    marker=dict(color=color_map.get(source_name, '#000'), size=14, line=dict(color='white', width=2)),
                    text=txt_vals, textfont=dict(size=12, color=color_map.get(source_name, '#000'), weight="bold"),
                    textposition=txt_pos, hovertemplate=hover_vals
                ))

            add_points('שילוב', 'סקר שילוב')
            add_points('מדרוג', 'הוועדה למדרוג')

            v_all = plot_df['percentage'].dropna().tolist()
            mx = max(v_all, default=100)
            
            fig.update_layout(
                margin=dict(l=280, r=40, t=60, b=100), 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                height=max(450, len(labels)*100),
                legend=dict(
                    orientation="h", 
                    y=1.15, # מקרא מעל התרשים
                    x=0.5, 
                    xanchor="center"
                ),
                xaxis=dict(
                    side="top", 
                    range=[-10, mx * 1.3], # מתחיל ממינוס 10 לתת מרווח גם כשהערך קרוב לאפס
                    showgrid=True, 
                    gridcolor="#f3f4f6", 
                    zeroline=False, 
                    ticksuffix="%"
                ),
                yaxis=dict(
                    side="left", 
                    categoryorder="array", 
                    categoryarray=wrapped_labels[::-1],
                    tickfont=dict(size=12, weight="bold")
                )
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("אין נתונים להצגת תרשים עבור שאלה זו.")
