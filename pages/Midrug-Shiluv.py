import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import random

st.set_page_config(layout="wide", page_title="השוואת מדרוג ושילוב")

st.markdown("""
<style>
    h3 {margin-bottom:15px!important;}
    * { direction: rtl!important; text-align: right!important; }
    .stRadio label div[data-testid="stMarkdownContainer"] p { font-size: 15px !important; }
    .stRadio label { padding: 15px 0 !important; border-bottom: 1px solid #f3f4f6; display: flex !important; align-items: center !important; flex-direction: row !important; justify-content: flex-start !important; }
    .stRadio label input[type="radio"] { margin-left: 0 !important; margin-right: 5px !important; }
    .stRadio label div[data-testid="stMarkdownContainer"] { margin-right: 15px !important; }
    div.row-widget.stRadio > div > label:first-of-type { margin-bottom: 10px; }
    div[data-testid="stPlotlyChart"] *, div[data-testid="stPlotlyChart"] { direction: ltr !important; text-align: left !important; unicode-bidi: isolate !important; }
    .custom-table { width: 100% !important; border-collapse: collapse !important; margin-top: 15px !important; margin-bottom: 10px !important; font-family: inherit !important; direction: ltr !important; table-layout: fixed !important; }
    .custom-th, .custom-td { border: 1px solid #e5e7eb !important; padding: 12px 8px !important; text-align: center !important; vertical-align: middle !important; direction: ltr !important; box-sizing: border-box !important; overflow: visible !important; word-wrap: break-word !important; white-space: normal !important; }
    .custom-th { background-color: #f3f4f6 !important; font-weight: bold !important; color: #1f2937 !important; font-size: 14px !important; }
    .pos-val { color: green !important; font-weight: bold !important; }
    .neg-val { color: red !important; font-weight: bold !important; }
    .zero-val { color: #374151 !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv(os.path.join(os.path.dirname(__file__), "Midrug-Shiluv.csv"))

df = load_data()

menu_col, chart_col = st.columns([1, 5], gap="small")

with menu_col:

    #########################################
    # תפריט צדדי - סינון נתונים
    #########################################
    with st.container(border=True):
        st.markdown("### 📺 סינון נתונים")
        sel_p = st.selectbox("ימי מדידה", ["אמצע שבוע", "סוף שבוע"])
        waves = ["גל 19 במאי", "גל 25 במאי", "ממוצע שני הגלים"] if sel_p == "אמצע שבוע" else ["גל 17 במאי", "גל 31 במאי", "ממוצע שני הגלים"]
        sel_w = st.selectbox("גל מחקר", waves, index=2)
        if sel_w == "ממוצע שני הגלים":
            opts = df[df['wave'] == "ממוצע שני הגלים"].apply(lambda x: "כללי" if x['demo_category'] == "כללי" else f"{x['demo_category']} - {x['demo_value']}", axis=1).unique()
            sel_d = st.selectbox("פילוח דמוגרפי:", opts, index=list(opts).index("כללי") if "כללי" in opts else 0)
            cat, val = ("כללי", "סהכ") if sel_d == "כללי" else sel_d.split(" - ", 1)
        else:
            st.selectbox("פילוח דמוגרפי", ["כללי (זמין רק בבחירת ממוצע שני הגלים ביחד)"], disabled=True)
            cat, val = "כללי", "סהכ"
    df_f = df[(df['period'] == sel_p) & (df['wave'] == sel_w) & (df['demo_category'] == cat) & (df['demo_value'] == val)]
    q_list = df_f['question_text'].unique().tolist()
    if not q_list: 
        st.warning("אין נתונים עבור הסינון שנבחר.")
        st.stop()

    #########################################
    # תפריט צדדי - בחירת שאלה
    #########################################
    with st.container(border=True):
        st.markdown("### 📋 בחירת שאלה")
        sel_q = st.radio("", q_list, index=0, label_visibility="collapsed")
plot_df = df_f[df_f['question_text'] == sel_q]
labels = plot_df['answer_text'].drop_duplicates().tolist()

with chart_col:

    #########################################
    # כרטיס ראשון - סקר מול מדרוג: תרשים
    #########################################
    with st.container(border=True):
        if labels:
            st.markdown(f"### 📈 סקר מכון שילוב מול נתוני ועדת המדרוג")
            st.write("")
            
            table_data = []
            for ans in labels:
                s_val = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]['percentage'].values
                m_val = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]['percentage'].values
                if len(s_val) and len(m_val):
                    table_data.append((ans, m_val[0] - s_val[0]))

            fig = go.Figure()
            wrapped_labels = [f"<span style='display: inline-block; width: 100%; white-space: normal; text-align: center;'>{lbl}</span>" for lbl in labels]
            
            for i, ans in enumerate(labels):
                s_val = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]['percentage'].values
                m_val = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]['percentage'].values
                if len(s_val) and len(m_val):
                    fig.add_trace(go.Scatter(x=[wrapped_labels[i], wrapped_labels[i]], y=[m_val[0], s_val[0]], mode="lines", line=dict(color="#000", width=2), showlegend=False, hoverinfo="skip"))
            
            def add_points(source_filter, source_name):
                x_vals, y_vals, hover_vals, txt_vals, txt_pos = [], [], [], [], []
                color_map = {'סקר שילוב': '#2563eb', 'הוועדה למדרוג': '#ea580c'}
                
                for i, ans in enumerate(labels):
                    r_s = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'שילוב')]['percentage'].values
                    r_m = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == 'מדרוג')]['percentage'].values
                    r_src = plot_df[(plot_df['answer_text'] == ans) & (plot_df['source'] == source_filter)]['percentage'].values
                    
                    if len(r_s) and len(r_m) and len(r_src):
                        s, m, val = round(r_s[0], 1), round(r_m[0], 1), round(r_src[0], 1)
                        x_vals.append(wrapped_labels[i]); y_vals.append(val)
                        hover_vals.append(f"<b>{source_name}</b><br>אחוז: {val}%<extra></extra>")
                        txt_vals.append(f"<b>{val}%</b>")
                        txt_pos.append("top center" if s == m else "bottom center" if val <= min(s, m) else "top center")
                        
                if x_vals:
                    fig.add_trace(go.Scatter(
                        x=x_vals, y=y_vals, mode="markers+text", name=source_name,
                        marker=dict(color=color_map.get(source_name, '#000'), size=14, line=dict(color='white', width=2)),
                        text=txt_vals, textfont=dict(size=12, color=color_map.get(source_name, '#000'), weight="bold"),
                        textposition=txt_pos, hovertemplate=hover_vals
                    ))

            add_points('שילוב', 'סקר שילוב')
            add_points('מדרוג', 'הוועדה למדרוג')

            all_vals = [val for trace in fig.data if trace.y for val in trace.y if val is not None and val >= 0]
            my = max(all_vals, default=100) * 1.15
            
            fig.update_layout(
                margin=dict(l=250, r=50, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=380, legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", yanchor="top"),
                xaxis=dict(side="bottom", showticklabels=False, showgrid=False, zeroline=False),
                yaxis=dict(side="left", range=[-1, my], showticklabels=False, showgrid=True, gridcolor="#f3f4f6", zeroline=False)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            #########################################
            # כרטיס ראשון - סקר מול מדרוג: טבלה
            #########################################
            if table_data:
                col_count = len(table_data) + 1 
                all_diffs = [diff for _, diff in table_data]
                mean_diff = sum(all_diffs) / len(all_diffs) if all_diffs else 0
                
                html_code = f'<table class="custom-table"><thead><tr>'
                html_code += f'<th class="custom-th">פרמטר</th>' 
                for ans, _ in table_data: 
                    html_code += f'<th class="custom-th">{ans}</th>'
                html_code += "</tr></thead><tbody>"
                
                html_code += "<tr>"
                html_code += f'<td class="custom-td" style="font-weight: bold; background-color: #f9fafb;">שינוי אבסולוטי</td>'
                for _, diff in table_data:
                    cls = "pos-val" if diff > 0 else "neg-val" if diff < 0 else "zero-val"
                    html_code += f'<td class="custom-td {cls}">{"+" if diff > 0 else ""}{diff:.1f}%</td>'
                html_code += "</tr>"
                
                html_code += "<tr>"
                html_code += f'<td class="custom-td" style="font-weight: bold; background-color: #f9fafb;">שינוי מחושב</td>'
                for _, diff in table_data:
                    adj_diff = diff - mean_diff
                    cls = "pos-val" if adj_diff > 0 else "neg-val" if adj_diff < 0 else "zero-val"
                    html_code += f'<td class="custom-td {cls}">{"+" if adj_diff > 0 else ""}{adj_diff:.1f}%</td>'
                html_code += "</tr></tbody></table>"
                
                st.markdown(html_code, unsafe_allow_html=True)
        else:
            st.info("אין נתונים להצגת תרשים עבור שאלה זו.")

    target_channels = ["ערוץ כאן 11", "ערוץ קשת 12", "ערוץ רשת 13", "ערוץ עכשיו 14", "ערוץ i24news (אפיק 15)"]
    channel_colors = {
        "ערוץ כאן 11": "#AAAAAA", "ערוץ קשת 12": "#FAA046", "ערוץ רשת 13": "#82BE64",
        "ערוץ עכשיו 14": "#DC5050", "ערוץ i24news (אפיק 15)": "#5A96D2"
    }
    available_channels = [c for c in target_channels if c in labels]

    if len(available_channels) > 1:
        st.write("")
        #########################################
        # כרטיס שני - נתח שוק: תרשים
        #########################################
        with st.container(border=True):
            st.markdown("### 📊 נתח שוק יחסי מתוך ערוצי הברודקאסט")
            st.write("")
            fig_sov = go.Figure()
            
            for idx, (s_name, s_key) in enumerate([("הוועדה למדרוג", "מדרוג"), ("סקר שילוב", "שילוב")]):
                s_data = plot_df[plot_df['source'] == s_key]
                c_vals = [s_data[s_data['answer_text'] == c]['percentage'].values[0] if not s_data[s_data['answer_text'] == c].empty else 0 for c in available_channels]
                sum_5 = sum(c_vals)
                
                if sum_5 > 0:
                    for i, c in enumerate(available_channels):
                        norm = (c_vals[i] / sum_5) * 100
                        fig_sov.add_trace(go.Bar(
                            name=c, legendgroup=c, showlegend=(idx == 0), y=[s_name], x=[norm], orientation='h',
                            marker=dict(color=channel_colors.get(c, "#000"), line=dict(color='white', width=2)),
                            hovertemplate=f"{c}<br>נתח מתוך הברודקאסט: %{{x:.1f}}%<extra></extra>",
                            text=f"{norm:.1f}%" if norm > 4.5 else "", textposition='inside', insidetextanchor="middle",
                            textfont=dict(color="white", weight="bold", size=12)
                        ))
            
            fig_sov.update_layout(
                barmode='stack', height=200, autosize=True, bargap=0.25, margin=dict(l=125, r=20, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True,
                legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", font=dict(size=11)),
                xaxis=dict(showticklabels=False, showgrid=False, range=[0, 100]),
                yaxis=dict(tickfont=dict(weight="bold", size=14))
            )
            st.plotly_chart(fig_sov, use_container_width=True, config={'displayModeBar': False})

        #########################################
        # כרטיס שני - נתח שוק: טבלה
        #########################################
        sov_table_data = []
        s_data_full = plot_df[plot_df['source'] == 'שילוב']
        m_data_full = plot_df[plot_df['source'] == 'מדרוג']
        
        sum_s_vals = sum([s_data_full[s_data_full['answer_text'] == c]['percentage'].values[0] if not s_data_full[s_data_full['answer_text'] == c].empty else 0 for c in available_channels])
        sum_m_vals = sum([m_data_full[m_data_full['answer_text'] == c]['percentage'].values[0] if not m_data_full[m_data_full['answer_text'] == c].empty else 0 for c in available_channels])

        if sum_s_vals > 0 and sum_m_vals > 0:
            for c in available_channels:
                s_pct = s_data_full[s_data_full['answer_text'] == c]['percentage'].values[0] if not s_data_full[s_data_full['answer_text'] == c].empty else 0
                m_pct = m_data_full[m_data_full['answer_text'] == c]['percentage'].values[0] if not m_data_full[m_data_full['answer_text'] == c].empty else 0
                
                s_norm = (s_pct / sum_s_vals) * 100
                m_norm = (m_pct / sum_m_vals) * 100
                sov_diff = m_norm - s_norm
                sov_table_data.append((c, sov_diff))

        if sov_table_data:
            html_sov_code = f'<table class="custom-table"><thead><tr>'
            html_sov_code += f'<th class="custom-th">פרמטר</th>'
            for c, _ in sov_table_data:
                html_sov_code += f'<th class="custom-th">{c}</th>'
            html_sov_code += "</tr></thead><tbody>"
            
            html_sov_code += "<tr>"
            html_sov_code += f'<td class="custom-td" style="font-weight: bold; background-color: #f9fafb;">פער (מדרוג פחות סקר)</td>'
            for _, diff in sov_table_data:
                cls = "pos-val" if diff > 0 else "neg-val" if diff < 0 else "zero-val"
                html_sov_code += f'<td class="custom-td {cls}">{"+" if diff > 0 else ""}{diff:.1f}%</td>'
            html_sov_code += "</tr></tbody></table>"
            
            st.markdown(html_sov_code, unsafe_allow_html=True)

    has_i24 = any("i24" in ans for ans in labels)
    if sel_w == "ממוצע שני הגלים" and has_i24:
        st.write("") 
        #########################################
        # כרטיס שלישי - פירוט i24 (תרשים בלבד)
        #########################################
        with st.container(border=True):
            i24_ans = next((ans for ans in labels if "i24" in ans), None)
            st.markdown(f"### 👨‍👩‍👧‍👦 {sel_q} &nbsp;–&nbsp; i24news")
            st.write("")
            
            d_table, d_wrap, d_s_vals, d_m_vals = [], [], [], []
            all_demo = df[df['wave'] == "ממוצע שני הגלים"].apply(lambda x: "כללי" if x['demo_category'] == "כללי" else f"{x['demo_category']} - {x['demo_value']}", axis=1).unique()
            
            for d_opt in all_demo:
                d_cat, d_val = ("כללי", "סהכ") if d_opt == "כללי" else d_opt.split(" - ", 1)
                d_df = df[(df['period'] == sel_p) & (df['wave'] == sel_w) & (df['demo_category'] == d_cat) & (df['demo_value'] == d_val)]
                d_plot = d_df[(d_df['question_text'] == sel_q) & (d_df['answer_text'] == i24_ans)]
                
                if not d_plot.empty:
                    s_v = d_plot[d_plot['source'] == 'שילוב']['percentage'].values
                    m_v = d_plot[d_plot['source'] == 'מדרוג']['percentage'].values
                    if len(s_v) and len(m_v):
                        d_table.append((d_opt, m_v[0] - s_v[0]))
                        d_wrap.append(f"<span style='display: inline-block; width: 100%; white-space: normal; text-align: center;'>{d_opt}</span>")
                        d_s_vals.append(round(s_v[0], 1)); d_m_vals.append(round(m_v[0], 1))

            if d_table:
                fig_d = go.Figure()
                for idx, d_lbl in enumerate(d_wrap):
                    fig_d.add_trace(go.Scatter(x=[d_s_vals[idx], d_m_vals[idx]], y=[d_lbl, d_lbl], mode="lines", line=dict(color="#000", width=2), showlegend=False, hoverinfo="skip"))
                
                fig_d.add_trace(go.Scatter(
                    x=d_s_vals, y=d_wrap, mode="markers+text", name="סקר שילוב", marker=dict(color='#2563eb', size=14, line=dict(color='white', width=2)),
                    text=[f"<b>{val}%</b>" for val in d_s_vals], textfont=dict(size=12, color='#2563eb', weight="bold"),
                    textposition=["middle left" if s <= m else "middle right" for s, m in zip(d_s_vals, d_m_vals)], hovertemplate="<b>סקר שילוב</b><br>אחוז: %{x}%<extra></extra>"
                ))
                fig_d.add_trace(go.Scatter(
                    x=d_m_vals, y=d_wrap, mode="markers+text", name="הוועדה למדרוג", marker=dict(color='#ea580c', size=14, line=dict(color='white', width=2)),
                    text=[f"<b>{val}%</b>" for val in d_m_vals], textfont=dict(size=12, color='#ea580c', weight="bold"),
                    textposition=["middle right" if m >= s else "middle left" for s, m in zip(d_s_vals, d_m_vals)], hovertemplate="<b>הוועדה למדרוג</b><br>אחוז: %{x}%<extra></extra>"
                ))
                
                mx_d = max(d_s_vals + d_m_vals, default=100) * 1.15
                fig_d.update_layout(
                    margin=dict(l=125, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    height=max(250, len(d_table) * 65), legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center", yanchor="top"),
                    xaxis=dict(side="top", range=[-1, mx_d], showgrid=True, gridcolor="#f3f4f6", zeroline=False, ticksuffix="%"),
                    yaxis=dict(side="left", categoryorder="array", categoryarray=d_wrap[::-1], showticklabels=True, tickfont=dict(size=11, weight="bold"))
                )
                st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
