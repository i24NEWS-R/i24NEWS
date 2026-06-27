import os
import random
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout="wide", page_title="השוואת מדרוג ושילוב")

# סגנון ודריסת כיווניות מרוכז
st.markdown(
    """
<style>
    * {direction: rtl!important; text-align: right!important;}
    .stRadio label div[data-testid="stMarkdownContainer"] p { font-size: 15px !important; }
    .stRadio label {
        padding: 15px 0 !important; border-bottom: 1px solid #f3f4f6;
        display: flex !important; align-items: center !important;
        flex-direction: row !important; justify-content: flex-start !important;
    }
    .stRadio label input[type="radio"] { margin-left: 0 !important; margin-right: 5px !important; }
    .stRadio label div[data-testid="stMarkdownContainer"] { margin-right: 15px !important; }
    div.row-widget.stRadio > div > label:first-of-type { margin-bottom: 10px; }
    div[data-testid="stPlotlyChart"] *, div[data-testid="stPlotlyChart"] { direction: ltr !important; text-align: left !important; }
    div[data-testid="stPlotlyChart"] * { unicode-bidi: isolate !important; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    return pd.read_csv(os.path.join(os.path.dirname(__file__), "Midrug-Shiluv.csv"))


df = load_data()


# פונקציות עזר לאיסוף נתונים וטבלאות
def get_demo_options(data, wave_val):
    return data[data["wave"] == wave_val].apply(
        lambda x: (
            "כללי" if x["demo_category"] == "כללי" else f"{x['demo_category']} - {x['demo_value']}"
        ),
        axis=1,
    ).unique()


def parse_demo(sel_d_val):
    return ("כללי", "סהכ") if sel_d_val == "כללי" else sel_d_val.split(" - ", 1)


def generate_table_html(table_data):
    col_count = len(table_data)
    html = f"""
    <style>
        .custom-table {{ width: 100% !important; border-collapse: collapse !important; margin-top: 15px !important; margin-bottom: 10px !important; direction: ltr !important; }}
        .custom-th, .custom-td {{ border: 1px solid #e5e7eb !important; padding: 12px 8px !important; text-align: center !important; vertical-align: middle !important; direction: ltr !important; width: calc(100% / {col_count}) !important; box-sizing: border-box !important; }}
        .custom-th {{ background-color: #f3f4f6 !important; font-weight: bold !important; color: #1f2937 !important; font-size: 14px !important; }}
        .pos-val, .neg-val, .zero-val {{ font-weight: bold !important; }}
        .pos-val {{ color: green !important; }} .neg-val {{ color: red !important; }} .zero-val {{ color: #374151 !important; }}
    </style>
    <table class="custom-table">
        <thead><tr>"""
    for ans, _ in table_data:
        html += f'<th class="custom-th">{ans}</th>'
    html += "</tr></thead><tbody><tr>"
    for _, diff in table_data:
        cls = "pos-val" if diff > 0 else "neg-val" if diff < 0 else "zero-val"
        val_str = f"+{diff:.1f}%" if diff > 0 else f"{diff:.1f}%"
        html += f'<td class="custom-td {cls}">{val_str}</td>'
    html += "</tr></tbody></table>"
    return html


# אזור פילטרים
with st.container(border=True):
    title_col, filters_col = st.columns([1.1, 2.7])
    with title_col:
        st.markdown("### 📊 השוואת מדרוג מול סקר שילוב")
    with filters_col:
        f1, f2, f3 = st.columns([1, 1, 1.2])
        with f1:
            sel_p = st.selectbox("ימי מדידה:", ["אמצע שבוע", "סוף שבוע"])
        with f2:
            waves = (
                ["גל 19 במאי", "גל 25 במאי", "ממוצע שני הגלים"]
                if sel_p == "אמצע שבוע"
                else ["גל 17 במאי", "גל 31 במאי", "ממוצע שני הגלים"]
            )
            sel_w = st.selectbox("גל מחקר:", waves, index=2)
        with f3:
            if sel_w == "ממוצע שני הגלים":
                opts = get_demo_options(df, "ממוצע שני הגלים")
                sel_d = st.selectbox("פילוח דמוגרפי:", opts, index=list(opts).index("כללי") if "כללי" in opts else 0)
                cat, val = parse_demo(sel_d)
            else:
                st.selectbox(
                    "פילוח דמוגרפי:",
                    ["כללי (זמין רק בבחירת ממוצע שני הגלים ביחד)"],
                    disabled=True,
                )
                cat, val, sel_d = "כללי", "סהכ", "כללי"

df_f = df[
    (df["period"] == sel_p)
    & (df["wave"] == sel_w)
    & (df["demo_category"] == cat)
    & (df["demo_value"] == val)
]

q_list = df_f["question_text"].unique().tolist()
if not q_list:
    st.warning("אין נתונים עבור הסינון שנבחר.")
    st.stop()

# אזור תצוגה
menu_col, chart_col = st.columns([1.1, 2.7], gap="small")
with menu_col:
    with st.container(border=True):
        st.markdown("### 📋 בחירת שאלה:")
        st.write("")
        sel_q = st.radio("", q_list, index=0, label_visibility="collapsed")

plot_df = df_f[df_f["question_text"] == sel_q]
labels = plot_df["answer_text"].drop_duplicates().tolist()

with chart_col:
    with st.container(border=True):
        if not labels:
            st.info("אין נתונים להצגת תרשים עבור שאלה זו.")
        else:
            demo_display = sel_d if sel_w == "ממוצע שני הגלים" else "כללי"
            st.markdown(
                f"<p style='font-size:12px; font-weight:bold; color:#6b7280; margin-bottom:4px;'>{sel_p} &nbsp; &gt; &nbsp; {sel_w} &nbsp; &gt; &nbsp; {demo_display}</p>",
                unsafe_allow_html=True,
            )
            st.markdown(f"### {sel_q}")
            st.write("")

            table_data = []
            for ans in labels:
                s_row = plot_df[(plot_df["answer_text"] == ans) & (plot_df["source"] == "שילוב")]
                m_row = plot_df[(plot_df["answer_text"] == ans) & (plot_df["source"] == "מדרוג")]
                s_v = s_row["percentage"].values[0] if not s_row.empty else None
                m_v = m_row["percentage"].values[0] if not m_row.empty else None
                if s_v is not None and m_v is not None:
                    table_data.append((ans, m_v - s_v))

            fig = go.Figure()
            wrapped_labels = [
                f"<span style='display: inline-block; width: 100%; white-space: normal; text-align: center;'>{lbl}</span>"
                for lbl in labels
            ]

            for i, ans in enumerate(labels):
                s_v = (
                    plot_df[(plot_df["answer_text"] == ans) & (plot_df["source"] == "שילוב")][
                        "percentage"
                    ].values[0]
                    if not plot_df[(plot_df["answer_text"] == ans) & (plot_df["source"] == "שילוב")].empty
                    else None
                )
                m_v = (
                    plot_df[(plot_df["answer_text"] == ans) & (plot_df["source"] == "מדרוג")][
                        "percentage"
                    ].values[0]
                    if not plot_df[(plot_df["answer_text"] == ans) & (plot_df["source"] == "מדרוג")].empty
                    else None
                )
                if s_v is not None and m_v is not None:
                    fig.add_trace(
                        go.Scatter(
                            x=[wrapped_labels[i], wrapped_labels[i]],
                            y=[m_v, s_v],
                            mode="lines",
                            line=dict(color="#000", width=2),
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )

            def add_points(source_filter, source_name,, color_hex):
                x_vals, y_vals, hover_vals, txt_vals, txt_pos = [], [], [], [], []
                for i, ans in enumerate(labels):
                    row = plot_df[
                        (plot_df["answer_text"] == ans) & (plot_df["source"] == source_filter)
                    ]
                    val = row["percentage"].values[0] if not row.empty else None
                    s_val = (
                        plot_df[(plot_df["answer_text"] == ans) & (plot_df["source"] == "שילוב")][
                            "percentage"
                        ].values[0]
                        if not plot_df[
                            (plot_df["answer_text"] == ans) & (plot_df["source"] == "שילוב")
                        ].empty
                        else None
                    )
                    m_val = (
                        plot_df[(plot_df["answer_text"] == ans) & (plot_df["source"] == "מדרוג")][
                            "percentage"
                        ].values[0]
                        if not plot_df[
                            (plot_df["answer_text"] == ans) & (plot_df["source"] == "מדרוג")
                        ].empty
                        else None
                    )

                    if s_val is not None and m_val is not None and val is not None:
                        val_rnd = round(val, 1)
                        x_vals.append(wrapped_labels[i])
                        y_vals.append(val_rnd)
                        hover_vals.append(
                            f"<b>{source_name}</b><br>אחוז: {val_rnd}%<extra></extra>"
                        )
                        txt_vals.append(f"<b>{val_rnd}%</b>")
                        s_r, m_r = round(s_val, 1), round(m_val, 1)

                        if s_r == m_r:
                            pos = "top center" if source_filter == "שילוב" else "bottom center"
                        elif val_rnd < min(s_r, m_r):
                            pos = "bottom center"
                        else:
                            pos = "top center"
                        txt_pos.append(pos)

                if x_vals:
                    fig.add_trace(
                        go.Scatter(
                            x=x_vals,
                            y=y_vals,
                            mode="markers+text",
                            name=source_name,
                            marker=dict(
                                color=color_hex, size=14, line=dict(color="white", width=2)
                            ),
                            text=txt_vals,
                            textfont=dict(size=12, color=color_hex, weight="bold"),
                            textposition=txt_pos,
                            hovertemplate=hover_vals,
                        )
                    )

            add_points("שילוב", "סקר שילוב", "#2563eb")
            add_points("מדרוג", "הוועדה למדרוג", "#ea580c")

            all_vals = []
            for trace in fig.data:
                if trace.y:
                    valid = [v for v in trace.y if v is not None and v >= 0]
                    if valid:
                        all_vals.extend(valid)

            my = max(all_vals, default=100) * 1.15
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=380,
                legend=dict(
                    orientation="h", y=1.1, x=0.5, xanchor="center", yanchor="top"
                ),
                xaxis=dict(side="bottom", showticklabels=False, showgrid=False, zeroline=False),
                yaxis=dict(
                    side="left",
                    range=[-1, my],
                    showticklabels=False,
                    showgrid=True,
                    gridcolor="#f3f4f6",
                    zeroline=False,
                ),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            if table_data:
                st.markdown(generate_table_html(table_data), unsafe_allow_html=True)

# כרטיס תרשים מוטה צירים ממוקד i24news
has_i24 = any("i24" in ans for ans in labels)
if sel_w == "ממוצע שני הגלים" and has_i24:
    st.write("")
    with chart_col:
        with st.container(border=True):
            st.markdown(
                f"<p style='font-size:12px; font-weight:bold; color:#6b7280; margin-bottom:4px;'>{sel_p} &nbsp; &gt; &nbsp; {sel_w} &nbsp; &gt; &nbsp; פילוח דמוגרפי (i24news)</p>",
                unsafe_allow_html=True,
            )
            i24_ans = next((ans for ans in labels if "i24" in ans), None)
            st.markdown(f"<h3>{sel_q} &nbsp;–&nbsp; i24news</h3>", unsafe_allow_html=True)
            st.write("")

            d_tbl, d_wrap, d_ys, d_ym = [], [], [], []
            all_demo = get_demo_options(df, "ממוצע שני הגלים")

            for d_opt in all_demo:
                d_cat, d_val = parse_demo(d_opt)
                dd_f = df[
                    (df["period"] == sel_p)
                    & (df["wave"] == sel_w)
                    & (df["demo_category"] == d_cat)
                    & (df["demo_value"] == d_val)
                ]
                dp_df = dd_f[(dd_f["question_text"] == sel_q) & (dd_f["answer_text"] == i24_ans)]

                if not dp_df.empty:
                    s_v = dp_df[dp_df["source"] == "שילוב"]["percentage"].values[0]
                    m_v = dp_df[dp_df["source"] == "מדרוג"]["percentage"].values[0]
                    if s_v is not None and m_v is not None:
                        d_tbl.append((d_opt, m_v - s_v))
                        lbl_html = f"<span style='display: inline-block; width: 100%; white-space: normal; text-align: center;'>{d_opt}</span>"
                        d_wrap.append(lbl_html)
                        d_ys.append(round(s_v, 1))
                        d_ym.append(round(m_v, 1))

            if d_tbl:
                fig_d = go.Figure()
                for idx, demo_lbl in enumerate(d_wrap):
                    fig_d.add_trace(
                        go.Scatter(
                            x=[d_ys[idx], d_ym[idx]],
                            y=[demo_lbl, demo_lbl],
                            mode="lines",
                            line=dict(color="#000", width=2),
                            showlegend=False,
                            hoverinfo="skip",
                        )
                    )

                fig_d.add_trace(
                    go.Scatter(
                        x=d_ys,
                        y=d_wrap,
                        mode="markers+text",
                        name="סקר שילוב",
                        marker=dict(color="#2563eb", size=14, line=dict(color="white", width=2)),
                        text=[f"<b>{v}%</b>" for v in d_ys],
                        textfont=dict(size=12, color="#2563eb", weight="bold"),
                        textposition=[
                            (
                                "middle left"
                                if d_ys[idx] <= d_ym[idx]
                                else "middle right"
                            )
                            for idx in range(len(d_wrap))
                        ],
                        hovertemplate="<b>סקר שילוב</b><br>אחוז: %{x}%<extra></extra>",
                    )
                )

                fig_d.add_trace(
                    go.Scatter(
                        x=d_ym,
                        y=d_wrap,
                        mode="markers+text",
                        name="הוועדה למדרוג",
                        marker=dict(color="#ea580c", size=14, line=dict(color="white", width=2)),
                        text=[f"<b>{v}%</b>" for v in d_ym],
                        textfont=dict(size=12, color="#ea580c", weight="bold"),
                        textposition=[
                            (
                                "middle right"
                                if d_ym[idx] >= d_ys[idx]
                                else "middle left"
                            )
                            for idx in range(len(d_wrap))
                        ],
                        hovertemplate="<b>הוועדה למדרוג</b><br>אחוז: %{x}%<extra></extra>",
                    )
                )

                mx_d = max(d_ys + d_ym, default=100) * 1.15
                fig_d.update_layout(
                    margin=dict(l=125, r=20, t=20, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=max(250, len(d_tbl) * 65),
                    legend=dict(
                        orientation="h", y=1.05, x=0.5, xanchor="center", yanchor="top"
                    ),
                    xaxis=dict(
                        side="top",
                        range=[-1, mx_d],
                        showgrid=True,
                        gridcolor="#f3f4f6",
                        zeroline=False,
                        ticksuffix="%",
                    ),
                    yaxis=dict(
                        side="left",
                        categoryorder="array",
                        categoryarray=d_wrap[::-1],
                        showticklabels=True,
                        tickfont=dict(size=11, weight="bold"),
                    ),
                )
                st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})
