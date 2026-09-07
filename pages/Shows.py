import os
import pandas as pd
import plotly.express as px
import streamlit as st

# הגדרת העמוד
st.set_page_config(page_title="דשבורד תוכניות", layout="wide")

# נתיב לקובץ ה-CSV שנמצא באותה תיקייה (pages)
DATA_PATH = os.path.join(os.path.dirname(__file__), "Shows.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    
    # המרת תאריכים סלחנית שמטפלת גם בפורמט DD/MM/YYYY וערכים ריקים
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    
    # ניקוי שורות עם תאריך לא תקין במידה ויש
    df = df.dropna(subset=['Date'])
    
    # חישוב נתח
    df['Share'] = (df['i24'] / df['Reference'].replace(0, pd.NA)) * 100
    df['Share'] = df['Share'].fillna(0)
    
    return df

df = load_data()

# ===== תפריט בצד ימין (Sidebar) =====
st.sidebar.header("סינון ופרמטרים")

# 1. בחירת תוכנית (ברירת מחדל: המהדורה המרכזית איי 24)
all_titles = sorted(df['Title'].dropna().unique().tolist())
default_title = "המהדורה המרכזית איי 24"
title_index = all_titles.index(default_title) if default_title in all_titles else 0

selected_title = st.sidebar.selectbox(
    "בחר תוכנית:",
    options=all_titles,
    index=title_index
)

# 2. בחירת מדד
metric_option = st.sidebar.radio(
    "בחר מדד להצגה:",
    options=["רייטינג (i24)", "נתח (Share %)"],
    index=0
)

# 3. בחירת תאריכים (ברירת מחדל: מתחילת 2026)
min_date = df['Date'].min()
max_date = df['Date'].max()
default_start = pd.to_datetime("2026-01-01")

start_date = st.sidebar.date_input(
    "תאריך התחלה:",
    value=default_start if default_start >= min_date else min_date,
    min_value=min_date,
    max_value=max_date
)
end_date = st.sidebar.date_input(
    "תאריך סיום:",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

# 4. אופן הצגת נתונים (יומית/שבועית/חודשית)
freq_option = st.sidebar.selectbox(
    "אופן הצגת נתונים:",
    options=["יומית", "שבועית", "חודשית"],
    index=0
)

# ===== סינון והכנת הנתונים =====
col_to_plot = 'i24' if metric_option == "רייטינג (i24)" else 'Share'
y_label = "רייטינג (%)" if metric_option == "רייטינג (i24)" else "נתח (%)"

# סינון לפי תוכנית וטווח תאריכים
filtered_df = df[
    (df['Title'] == selected_title) &
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date))
].sort_values('Date')

# אגרגציה לפי תדירות
if freq_option == "שבועית":
    plot_df = filtered_df.resample('W-MON', on='Date')[col_to_plot].mean().reset_index()
elif freq_option == "חודשית":
    plot_df = filtered_df.resample('MS', on='Date')[col_to_plot].mean().reset_index()
else:  # יומית
    plot_df = filtered_df[['Date', col_to_plot]].copy()

# ===== תרשים בצד שמאל =====
st.title(f"תרשים מגמה - {selected_title}")

if plot_df.empty:
    st.warning("לא נמצאו נתונים עבור הסינון הנבחר.")
else:
    fig = px.line(
        plot_df,
        x='Date',
        y=col_to_plot,
        title=f"{metric_option} - תצוגה {freq_option}",
        labels={'Date': 'תאריך', col_to_plot: y_label},
        markers=True
    )
    
    fig.update_traces(line_color='#1f77b4', line_width=2.5)
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="תאריך",
        yaxis_title=y_label,
        font=dict(size=14)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # כרטיסי סיכום קצרים מתחת לגרף
    c1, c2, c3 = st.columns(3)
    c1.metric("ממוצע בתקופה", f"{plot_df[col_to_plot].mean():.2f}%")
    c2.metric("שיא בתקופה", f"{plot_df[col_to_plot].max():.2f}%")
    c3.metric("מספר ימי שידור / תצפיות", len(plot_df))
