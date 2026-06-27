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

# אזור הפילטרים - שימוש בתוויות מובנות ליישור גובה מושלם
with st.container(border=True):
    title_col, filters_col = st.columns([1.1, 2.7])
    
    with title_col:
        st.markdown("### 📊 השוואת מדרוג מול סקר שילוב")
        
    with filters_col:
        # פריסת הפילטרים כך שיישבו זה לצד זה באותה השורה בצורה מרווחת
        f1, f2, f3 = st.columns([1, 1, 1.2])
        
        with f1:
            sel_p = st.selectbox("ימי מדידה:", ["אמצע שבוע", "סוף שבוע"])
            
        with f2:
            waves = ["גל 19 במאי", "גל 25 במאי", "ממוצע שני הגלים"] if sel_p == "אמצע שבוע" else ["גל 17 במאי", "גל 31 במאי", "ממוצע שני הגלים"]
            sel_w = st.selectbox("גל מחקר:", waves, index=2)
            
        with f3:
            if sel_w == "ממוצע שני הגלים":
                opts = df[df['wave'] == "ממוצע שני הגלים"].apply(lambda x: "כללי" if x['demo_category'] == "כללי" else f"{x['demo_category']} - {x['demo_value']}", axis=1).unique()
                sel_d = st.selectbox("פילוח דמוגרפי:", opts, index=list(opts).index("כללי") if "כללי" in opts else 0)
                cat, val = ("כללי", "סהכ") if sel_d == "כללי" else sel_d.split(" - ", 1)
            else:
                st.selectbox("פילוח דמוגרפי:", ["כללי (זמין רק בבחירת ממוצע שני הגלים ביחד)"], disabled=True)
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
            # מראה מיקום בטקסט קטן ובולד בראש הקונטיינר
            demo_display = sel_d if 'sel_d' in locals() and sel_w == "ממוצע שני הגלים" else "כללי"
            st.markdown(f"<p style='font-size:12px; font-weight:bold; color:#6b7280; margin-bottom:4px;'>{sel_p} &nbsp; &gt; &nbsp; {sel_w} &nbsp; &gt; &nbsp; {demo_display}</p>", unsafe_allow_html=True)
            
            st.markdown(f"### {sel_q}")
            st.write("")
            
            # --- הכנת נתוני הטבלה (לשימוש בהמשך מתחת לתרשים) ---
            table_data = []
            for ans in labels:
                s_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]
                m_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]
                
                s_v = s_row['percentage'].values[0] if not s_row.empty else None
                m_v = m_row['percentage'].values[0] if not m_row.empty else None
                
                if s_v is not None and m_v is not None:
                    diff = m_v - s_v
                    table_data.append((ans, diff))

            # --- בניית התרשים האנכי ---
            fig = go.Figure()
            
            # עטיפת התשובות כך שיפרסו 100% לרוחב ללא הגבלת פיקסלים קשיחה
            wrapped_labels = [f"<span style='display: inline-block; width: 100%; white-space: normal; text-align: center;'>{lbl}</span>" for lbl in labels]
            
            # שרטוט הקווים המחברים (אנכיים) רק לתשובות שקיימות בשני המקורות
            for i, ans in enumerate(labels):
                s_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]
                m_row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]
                
                s_v = s_row['percentage'].values[0] if not s_row.empty else None
                m_v = m_row['percentage'].values[0] if not m_row.empty else None
                
                if s_v is not None and m_v is not None:
                    fig.add_trace(go.Scatter(
                        x=[wrapped_labels[i], wrapped_labels[i]], y=[m_v, s_v], mode="lines", 
                        line=dict(color="#000", width=2), showlegend=False, hoverinfo="skip"
                    ))
            
            def add_points(source_filter, source_name):
                x_vals, y_vals, hover_vals, txt_vals, txt_pos = [], [], [], [], []
                
                for i, ans in enumerate(labels):
                    row = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == source_filter)]
                    val = row['percentage'].values[0] if not row.empty else None
                    
                    s_val = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]['percentage'].values[0] if not plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')].empty else None
                    m_val = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]['percentage'].values[0] if not plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')].empty else None
                    
                    if s_val is not None and m_val is not None:
                        if val is not None:
                            val = round(val, 1)
                        
                        x_vals.append(wrapped_labels[i])
                        y_vals.append(val)
                        
                        hover_vals.append(f"<b>{source_name}</b><br>אחוז: {val}%<extra></extra>")
                        txt_vals.append(f"<b>{val}%</b>")
                        
                        s_val = round(s_val, 1)
                        m_val = round(m_val, 1)
                        
                        if s_val == m_val:
                            if source_filter == "שילוב":
                                txt_pos.append("top center")
                            else:
                                txt_pos.append("bottom center")
                        elif val < min(s_val, m_val) or val == min(s_val, m_val):
                            txt_pos.append("bottom center")
                        else:
                            txt_pos.append("top center")
                            
                color_map = {'סקר שילוב': '#2563eb', 'הוועדה למדרוג': '#ea580c'}
                if x_vals:
                    fig.add_trace(go.Scatter(
                        x=x_vals, y=y_vals, mode="markers+text", name=source_name,
                        marker=dict(color=color_map.get(source_name, '#000'), size=14, line=dict(color='white', width=2)),
                        text=txt_vals, textfont=dict(size=12, color=color_map.get(source_name, '#000'), weight="bold"),
                        textposition=txt_pos, hovertemplate=hover_vals
                    ))

            add_points('שילוב', 'סקר שילוב')
            add_points('מדרוג', 'הוועדה למדרוג')

            # חישוב דינמי של התקרה
            all_plotted_values = []
            for trace in fig.data:
                if trace.y:
                    valid_y = [val for val in trace.y if val is not None and val >= 0]
                    if valid_y:
                        all_plotted_values.extend(valid_y)
            
            true_max = max(all_plotted_values, default=100)
            my = true_max * 1.15
            
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20), # שוליים צדדיים מורחבים לפריסה מלאה ב-100% רוחב
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                height=380, 
                legend=dict(
                    orientation="h", 
                    y=1.1, 
                    x=0.5, 
                    xanchor="center",
                    yanchor="top"
                ),
                xaxis=dict(
                    side="bottom",
                    showticklabels=False,
                    showgrid=False,
                    zeroline=False
                ),
                yaxis=dict(
                    side="left", 
                    range=[-1, my],
                    showticklabels=False, 
                    showgrid=True,
                    gridcolor="#f3f4f6",
                    zeroline=False
                )
            )
            
            # הצגת התרשים
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # --- הזרקת טבלת HTML (מתחת לתרשים) ---
            if table_data:
                col_count = len(table_data)
                
                # חישוב ממוצע הפערים לצורך מציאת הפער המחקרי האמיתי
                all_diffs = [diff for _, diff in table_data]
                mean_diff = sum(all_diffs) / len(all_diffs) if all_diffs else 0
                
                html_code = f"""
                <style>
                    .custom-table {{
                        width: 100% !important;
                        border-collapse: collapse !important;
                        margin-top: 15px !important;
                        margin-bottom: 10px !important;
                        font-family: inherit !important;
                        direction: ltr !important;
                    }}
                    .custom-th, .custom-td {{
                        border: 1px solid #e5e7eb !important;
                        padding: 12px 8px !important;
                        text-align: center !important;
                        vertical-align: middle !important;
                        direction: ltr !important;
                        width: calc(100% / {col_count}) !important;
                        box-sizing: border-box !important;
                    }}
                    .custom-th {{
                        background-color: #f3f4f6 !important;
                        font-weight: bold !important;
                        color: #1f2937 !important;
                        font-size: 14px !important;
                    }}
                    .pos-val {{
                        color: green !important;
                        font-weight: bold !important;
                    }}
                    .neg-val {{
                        color: red !important;
                        font-weight: bold !important;
                    }}
                    .zero-val {{
                        color: #374151 !important;
                        font-weight: bold !important;
                    }}
                </style>
                <table class="custom-table">
                    <thead>
                        <tr>
                """
                for ans, _ in table_data:
                    html_code += f'<th class="custom-th">{ans}</th>'
                
                # שורה 1: פער אבסולוטי
                html_code += "</tr></thead><tbody><tr>"
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

                # שורה 2: הפער המחקרי האמיתי (הפער האבסולוטי בניכוי ממוצע פערים שוק) ללא כותרת
                html_code += "</tr><tr>"
                for _, diff in table_data:
                    adj_diff = diff - mean_diff
                    if adj_diff > 0:
                        val_str = f"+{adj_diff:.1f}%"
                        html_code += f'<td class="custom-td pos-val">{val_str}</td>'
                    elif adj_diff < 0:
                        val_str = f"{adj_diff:.1f}%"
                        html_code += f'<td class="custom-td neg-val">{val_str}</td>'
                    else:
                        val_str = f"{adj_diff:.1f}%"
                        html_code += f'<td class="custom-td zero-val">{val_str}</td>'
                        
                html_code += "</tr></tbody></table>"
                
                st.markdown(html_code, unsafe_allow_html=True)

        else:
            st.info("אין נתונים להצגת תרשים עבור שאלה זו.")

# ==============================================================================
# --- כרטיס חדש: תרשים מוטה צירים ממוקד i24news (ללא טבלה, 100% רוחב) ---
# ==============================================================================
has_i24 = any("i24" in ans for ans in labels)

if sel_w == "ממוצע שני הגלים" and has_i24:
    st.write("") 
    with chart_col:
        with st.container(border=True):
            st.markdown(f"<p style='font-size:12px; font-weight:bold; color:#6b7280; margin-bottom:4px;'>{sel_p} &nbsp; &gt; &nbsp; {sel_w} &nbsp; &gt; &nbsp; פילוח דמוגרפי (i24news)</p>", unsafe_allow_html=True)
            
            i24_answer_text = next((ans for ans in labels if "i24" in ans), None)
            st.markdown(f"<h3>{sel_q} &nbsp;–&nbsp; i24news</h3>", unsafe_allow_html=True)
            st.write("")
            
            # איסוף נתונים דמוגרפיים עבור i24news
            demo_table_data = []
            demo_wrapped_labels = []
            demo_y_s_vals = []
            demo_y_m_vals = []
            
            all_demo_opts = df[df['wave'] == "ממוצע שני הגלים"].apply(
                lambda x: "כללי" if x['demo_category'] == "כללי" else f"{x['demo_category']} - {x['demo_value']}", 
                axis=1
            ).unique()
            
            for demo_opt in all_demo_opts:
                if demo_opt == "כללי":
                    d_cat, d_val = "כללי", "סהכ"
                else:
                    d_cat, d_val = demo_opt.split(" - ", 1)
                    
                demo_df_f = df[(df['period'] == sel_p) & (df['wave'] == sel_w) & (df['demo_category'] == d_cat) & (df['demo_value'] == d_val)]
                demo_plot_df = demo_df_f[(demo_df_f['question_text'] == sel_q) & (demo_df_f['answer_text'] == i24_answer_text)]
                
                if not demo_plot_df.empty:
                    s_row = demo_plot_df[demo_plot_df['source'] == 'שילוב']
                    m_row = demo_plot_df[demo_plot_df['source'] == 'מדרוג']
                    
                    s_v = s_row['percentage'].values[0] if not s_row.empty else None
                    m_v = m_row['percentage'].values[0] if not m_row.empty else None
                    
                    if s_v is not None and m_v is not None:
                        diff_val = m_v - s_v
                        demo_table_data.append((demo_opt, diff_val))
                        demo_wrapped_labels.append(f"<span style='display: inline-block; width: 100%; white-space: normal; text-align: center;'>{demo_opt}</span>")
                        demo_y_s_vals.append(round(s_v, 1))
                        demo_y_m_vals.append(round(m_v, 1))

            if demo_table_data:
                fig_demo = go.Figure()
                
                # קווים מקשרים אופקיים (X משתנה, Y קבוע)
                for idx, demo_lbl in enumerate(demo_wrapped_labels):
                    fig_demo.add_trace(go.Scatter(
                        x=[demo_y_s_vals[idx], demo_y_m_vals[idx]], y=[demo_lbl, demo_lbl], mode="lines", 
                        line=dict(color="#000", width=2), showlegend=False, hoverinfo="skip"
                    ))

                # הוספת נקודות שילוב
                fig_demo.add_trace(go.Scatter(
                    x=demo_y_s_vals, y=demo_wrapped_labels, mode="markers+text", name="סקר שילוב",
                    marker=dict(color='#2563eb', size=14, line=dict(color='white', width=2)),
                    text=[f"<b>{val}%</b>" for val in demo_y_s_vals],
                    textfont=dict(size=12, color='#2563eb', weight="bold"),
                    textposition=[
                        "middle left" if demo_y_s_vals[idx] <= demo_y_m_vals[idx] else "middle right" 
                        for idx in range(len(demo_wrapped_labels))
                    ],
                    hovertemplate="<b>סקר שילוב</b><br>אחוז: %{x}%<extra></extra>"
                ))

                # הוספת נקודות מדרוג
                fig_demo.add_trace(go.Scatter(
                    x=demo_y_m_vals, y=demo_wrapped_labels, mode="markers+text", name="הוועדה למדרוג",
                    marker=dict(color='#ea580c', size=14, line=dict(color='white', width=2)),
                    text=[f"<b>{val}%</b>" for val in demo_y_m_vals],
                    textfont=dict(size=12, color='#ea580c', weight="bold"),
                    textposition=[
                        "middle right" if demo_y_m_vals[idx] >= demo_y_s_vals[idx] else "middle left" 
                        for idx in range(len(demo_wrapped_labels))
                    ],
                    hovertemplate="<b>הוועדה למדרוג</b><br>אחוז: %{x}%<extra></extra>"
                ))

                all_demo_values = demo_y_s_vals + demo_y_m_vals
                demo_max = max(all_demo_values, default=100)
                mx_demo = demo_max * 1.15

                fig_demo.update_layout(
                    margin=dict(l=125, r=20, t=20, b=20), # שוליים צדדיים 20-20
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=max(250, len(demo_table_data) * 65), # מותאם אנכית לכמות הפילוחים
                    legend=dict(
                        orientation="h", 
                        y=1.05, 
                        x=0.5, 
                        xanchor="center",
                        yanchor="top"
                    ),
                    xaxis=dict(
                        side="top", # אחוזים למעלה
                        range=[-1, mx_demo],
                        showgrid=True, 
                        gridcolor="#f3f4f6", 
                        zeroline=False, 
                        ticksuffix="%"
                    ),
                    yaxis=dict(
                        side="left", 
                        categoryorder="array", 
                        categoryarray=demo_wrapped_labels[::-1],
                        showticklabels=True,
                        tickfont=dict(size=11, weight="bold")
                    )
                )

                st.plotly_chart(fig_demo, use_container_width=True, config={'displayModeBar': False})
