import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import random

st.set_page_config(layout="wide", page_title="השוואת מדרוג ושילוב")

# סגנון קבוע, דריסת כיווניות לתרשים וריווח אפשרויות הרדיו
st.markdown("""
<style>
    * {direction: rtl!important; text-align: right!important;}

    /* הגדלת הטקסט באפשרויות הרדיו בתפריט השאלות */
    .stRadio label div[data-testid="stMarkdownContainer"] p {
        font-size: 15px !important;
    }
    
    /* מרווח וקו תחתון בין אפשרויות הרדיו */
    .stRadio label {
        padding: 15px 0 !important;
        border-bottom: 1px solid #f3f4f6;
        display: flex !important;
        align-items: center !important;
        flex-direction: row !important; /* כפתור הרדיו מימין, הטקסט משמאלו */
        justify-content: flex-start !important;
    }
    
    /* ריווח כפתור הבחירה העגול והרחקתו שמאלה מהטקסט שצמוד אליו */
    .stRadio label input[type="radio"] {
        margin-left: 0 !important;
        margin-right: 5px !important;
    }
    
    /* הוספת מרווח מפורש בין כפתור הרדיו לבין הטקסט בלייבל */
    .stRadio label div[data-testid="stMarkdownContainer"] {
        margin-right: 15px !important;
    }
    
    /* הרחקת כותרת/נוסח השאלה מכפתור הבחירה הראשון ברשימה */
    div.row-widget.stRadio > div > label:first-of-type {
        margin-bottom: 10px;
    }

    /* דריסת כיווניות עבור אזור התרשים בלבד למניעת בריחת טקסטים */
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

# אזור הפילטרים - שימוש בתוויות מובנות ליישור גובה מושלם
with st.container(border=True):
    title_col, filters_col = st.columns([1.1, 2.7])
    
    with title_col:
        st.markdown("### 🎯 סינון נתונים")
        
    with filters_col:
        # פריסת הפילטרים כך שיישבו זה לצד זה באותה השורה בצורה מרווחת
        f1, f2, f3 = st.columns([1, 1, 1.2])
        
        with f1:
            sel_p = st.selectbox("ימי מדידה:", ["אמצע שבוע", "סוף שבוע"])
            
        with f2:
            waves = ["גל 19 במאי", "גל 25 במאי", "חיבור שני הגלים"] if sel_p == "אמצע שבוע" else ["גל 17 במאי", "גל 31 במאי", "חיבור שני הגלים"]
            sel_w = st.selectbox("גל מחקר:", waves, index=2)
            
        with f3:
            if sel_w == "חיבור שני הגלים":
                opts = df[df['wave'] == "חיבור שני הגלים"].apply(lambda x: "כללי" if x['demo_category'] == "כללי" else f"{x['demo_category']} - {x['demo_value']}", axis=1).unique()
                sel_d = st.selectbox("פילוח דמוגרפי:", opts, index=list(opts).index("כללי") if "כללי" in opts else 0)
                cat, val = ("כללי", "סהכ") if sel_d == "כללי" else sel_d.split(" - ", 1)
            else:
                st.selectbox("פילוח דמוגרפי:", ["כללי (זמין בחיבור הגלים)"], disabled=True)
                cat, val = "כללי", "סהכ"

df_f = df[(df['period'] == sel_p) & (df['wave'] == sel_w) & (df['demo_category'] == cat) & (df['demo_value'] == val)]

# אזור התצוגה - תפריט לצד הגרף
q_list = df_f['question_text'].unique().tolist()
if not q_list: 
    st.warning("אין נתונים עבור הסינון שנבחר.")
    st.stop()

menu_col, chart_col = st.columns([1.1, 2.7], gap="small")

with menu_col:
    with st.container(border=True):
        st.markdown("### 📋 בחירת שאלה:")
        st.write("")
        sel_q = st.radio("", q_list, index=0, label_visibility="collapsed")

plot_df = df_f[df_f['question_text'] == sel_q]
labels = plot_df['answer_text'].drop_duplicates().tolist()

with chart_col:
    with st.container(border=True):
        if labels:
            # מראה מיקום בטקסט קטן ובולד מעל התשובה שמעל התרשים
            demo_display = sel_d if 'sel_d' in locals() and sel_w == "חיבור שני הגלים" else "כללי"
            st.markdown(f"<p style='font-size:12px; font-weight:bold; color:#6b7280; margin-bottom:4px;'>{sel_p} &nbsp; &gt; &nbsp; {sel_w} &nbsp; &gt; &nbsp; {demo_display}</p>", unsafe_allow_html=True)
            
            st.markdown(f"### {sel_q}")
            st.write("")
            
            # --- בניית נתוני הטבלה ---
            table_data = []
            for ans in labels:
                s_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]
                m_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]
                
                s_v = s_row['percentage'].values[0] if not s_row.empty else None
                m_v = m_row['percentage'].values[0] if not m_row.empty else None
                
                if s_v is not None and m_v is not None:
                    diff = m_v - s_v
                    table_data.append((ans, diff))
            
            # --- הזרקת טבלת HTML מעוצבת וממורכזת דרך CSS ---
            if table_data:
                st.markdown("##### עד כמה הנתונים נמוכים/גבוהים ביחס למדרוג")
                
                html_code = """
                <style>
                    .custom-table {
                        width: 100% !important;
                        border-collapse: collapse !important;
                        margin-bottom: 25px !important;
                        font-family: inherit !important;
                    }
                    .custom-th, .custom-td {
                        border: 1px solid #e5e7eb !important;
                        padding: 12px 8px !important;
                        text-align: center !important;
                        vertical-align: middle !important;
                    }
                    .custom-th {
                        background-color: #f3f4f6 !important;
                        font-weight: bold !important;
                        color: #1f2937 !important;
                        font-size: 14px !important;
                    }
                    .pos-val {
                        color: green !important;
                        font-weight: bold !important;
                        font-size: 14px !important;
                    }
                    .neg-val {
                        color: red !important;
                        font-weight: bold !important;
                        font-size: 14px !important;
                    }
                    .zero-val {
                        color: #374151 !important;
                        font-weight: bold !important;
                        font-size: 14px !important;
                    }
                </style>
                <table class="custom-table">
                    <thead>
                        <tr>
                """
                
                # שורה 1: התשובות
                for ans, _ in table_data:
                    html_code += f'<th class="custom-th">{ans}</th>'
                    
                html_code += """
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                """
                
                # שורה 2: הפערים
                for _, diff in table_data:
                    if diff > 0:
                        val_str = f"+{diff:.1f}%"
                        html_code += f'<td class="custom-td pos-val">{val_str}</td>'
                    elif diff < 0:
                        val_str = f"{diff:.1f}%"
                        html_code += f'<td class="custom-td neg-val">{val_str}</td>'
                    else:
                        val_str = f"{diff:.1f}%"
                        html_code += f'<td class="custom-td zero-val">{val_str}</td>'
                        
                html_code += """
                        </tr>
                    </tbody>
                </table>
                """
                
                st.markdown(html_code, unsafe_allow_html=True)
                st.write("")
            # --------------------------------------------------------
            
            fig = go.Figure()
            
            wrapped_labels = [f"<span style='display: inline-block; width: 260px; white-space: normal; text-align: right;'>{lbl}</span>" for lbl in labels]
            
            for i, ans in enumerate(labels):
                s_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]
                m_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]
                
                s_v = s_row['percentage'].values[0] if not s_row.empty else None
                m_v = m_row['percentage'].values[0] if not m_row.empty else None
                
                if s_v is not None and m_v is not None:
                    fig.add_trace(go.Scatter(
                        x=[m_v, s_v], y=[wrapped_labels[i], wrapped_labels[i]], mode="lines", 
                        line=dict(color="#000", width=2), showlegend=False, hoverinfo="skip"
                    ))
            
            def add_points(source_filter, source_name):
                x_vals, y_vals, hover_vals, txt_vals, txt_pos = [], [], [], [], []
                
                for i, ans in enumerate(labels):
                    row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == source_filter)]
                    val = row['percentage'].values[0] if not row.empty else None
                    
                    if val is not None:
                        val = round(val, 1)
                    
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
                                rand_pos = random.choice(["middle left", "middle right"])
                                if source_filter == "שילוב":
                                    txt_pos.append(rand_pos)
                                else:
                                    txt_pos.append("middle right" if rand_pos == "middle left" else "middle left")
                            elif val < min(s_val, m_val) or val == min(s_val, m_val):
                                txt_pos.append("middle left")
                            else:
                                txt_pos.append("middle right")
                        else:
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
                height=max(450, len(labels)*75),
                legend=dict(
                    orientation="h", 
                    y=1.25,
                    x=0.5, 
                    xanchor="center"
                ),
               xaxis=dict(
                    side="top", 
                    range=[-2, mx * 1.15], 
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
