import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="מפת בחירות היררכית בישראל", layout="wide")
st.title("מפת בחירות בישראל - תצוגה היררכית (Drill-Down)")

# ---------------------------------------------------------
# 1. ניהול סטיט (Session State) לניווט היררכי
# ---------------------------------------------------------
if 'level' not in st.session_state:
    st.session_state.level = 'מחוזות'  # מחוזות -> נפות -> יישובים -> שכונות
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = None
if 'selected_subdistrict' not in st.session_state:
    st.session_state.selected_subdistrict = None
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = None

# ---------------------------------------------------------
# 2. נתוני הצבעה דמוגרפיים היררכיים (סימולציה מלאה)
# ---------------------------------------------------------
# מפה של מקרא צבעים למפלגות
PARTY_COLORS = {
    'הליכוד': '#2196F3',
    'יש עתיד': '#FF9800',
    'הציונות הדתית': '#00BCD4',
    'המחנה הממלכתי': '#9C27B0',
    'ש"ס': '#795548',
    'יהדות התורה': '#607D8B'
}

# 3. טעינת קובץ GeoJSON גלובלי של גבולות ישראל
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/datasets/geo-boundaries/master/data/ISR.geojson"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            geojson_data = res.json()
            gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
            gdf.crs = "EPSG:4326"
            return geojson_data, gdf
    except Exception:
        pass
    return None, None

geojson_raw, gdf = load_geojson()

# ---------------------------------------------------------
# 4. סרגל הניווט (Breadcrumbs & Selectors)
# ---------------------------------------------------------
st.sidebar.header("ניווט בין רמות מפה")

# כפתור איפוס לרמה הגבוהה ביותר
if st.sidebar.button("reset ↺ חזרה לרמת מחוזות"):
    st.session_state.level = 'מחוזות'
    st.session_state.selected_district = None
    st.session_state.selected_subdistrict = None
    st.session_state.selected_city = None

st.sidebar.markdown("---")

# בורר דרך ה-Sidebar לסימולציית הקליק
districts_list = ["מחוז הצפון", "מחוז חיפה", "מחוז המרכז", "מחוז תל אביב", "מחוז ירושלים", "מחוז הדרום"]

if st.session_state.level == 'מחוזות':
    selected_dist = st.sidebar.selectbox("בחר מחוז להתמקד (Drill-Down):", ["-- בחר מחוז --"] + districts_list)
    if selected_dist != "-- בחר מחוז --":
        st.session_state.selected_district = selected_dist
        st.session_state.level = 'נפות'
        st.rerun()

elif st.session_state.level == 'נפות':
    st.sidebar.write(f"**מחוז נבחר:** {st.session_state.selected_district}")
    subdistricts_dummy = ["נפה א'", "נפה ב'", "נפה ג'"]
    selected_sub = st.sidebar.selectbox("בחר נפה להתמקד:", ["-- בחר נפה --"] + subdistricts_dummy)
    if selected_sub != "-- בחר נפה --":
        st.session_state.selected_subdistrict = selected_sub
        st.session_state.level = 'ערים'
        st.rerun()

elif st.session_state.level == 'ערים':
    st.sidebar.write(f"**מחוז:** {st.session_state.selected_district}")
    st.sidebar.write(f"**נפה:** {st.session_state.selected_subdistrict}")
    cities_dummy = ["עיר א'", "עיר ב'", "עיר ג'"]
    selected_c = st.sidebar.selectbox("בחר עיר להתמקד:", ["-- בחר עיר --"] + cities_dummy)
    if selected_c != "-- בחר עיר --":
        st.session_state.selected_city = selected_c
        st.session_state.level = 'שכונות'
        st.rerun()

elif st.session_state.level == 'שכונות':
    st.sidebar.write(f"**מחוז:** {st.session_state.selected_district}")
    st.sidebar.write(f"**נפה:** {st.session_state.selected_subdistrict}")
    st.sidebar.write(f"**עיר:** {st.session_state.selected_city}")

# ---------------------------------------------------------
# 5. עיבוד הנתונים והצגת המפה לפי הרמה הנוכחית
# ---------------------------------------------------------
st.subheader(f"תצוגת רמה: {st.session_state.level}")

if gdf is not None:
    # יצירת נתונים מותאמים לפי הרמה הנבחרת
    if st.session_state.level == 'מחוזות':
        df_display = pd.DataFrame({
            'id': list(range(len(districts_list))),
            'name': districts_list,
            'מפלגה מובילה': ['הליכוד', 'יש עתיד', 'הליכוד', 'יש עתיד', 'יהדות התורה', 'הליכוד'],
            'אחוז תמיכה': ['34%', '28%', '31%', '35%', '42%', '39%']
        })
        zoom_level = 7
        center_coords = {"lat": 31.5, "lon": 34.75}

    elif st.session_state.level == 'נפות':
        df_display = pd.DataFrame({
            'id': [0, 1, 2],
            'name': [f"{st.session_state.selected_district} - נפה 1", 
                     f"{st.session_state.selected_district} - נפה 2", 
                     f"{st.session_state.selected_district} - נפה 3"],
            'מפלגה מובילה': ['הליכוד', 'המחנה הממלכתי', 'ש"ס'],
            'אחוז תמיכה': ['30%', '25%', '22%']
        })
        zoom_level = 8.5
        center_coords = {"lat": 32.0, "lon": 34.8}

    elif st.session_state.level == 'ערים':
        df_display = pd.DataFrame({
            'id': [0, 1, 2],
            'name': ["עיר מרכזית א'", "יישוב ב'", "מועצה אזורית ג'"],
            'מפלגה מובילה': ['יש עתיד', 'הציונות הדתית', 'הליכוד'],
            'אחוז תמיכה': ['40%', '33%', '37%']
        })
        zoom_level = 10
        center_coords = {"lat": 32.08, "lon": 34.78}

    else:  # שכונות
        df_display = pd.DataFrame({
            'id': [0, 1, 2],
            'name': ["שכונות צפון", "מרכז העיר", "שכונות דרום"],
            'מפלגה מובילה': ['יש עתיד', 'הליכוד', 'ש"ס'],
            'אחוז תמיכה': ['45%', '38%', '41%']
        })
        zoom_level = 12
        center_coords = {"lat": 32.07, "lon": 34.77}

    # התאמת המפה ל-GeoJSON
    gdf_level = gdf.head(len(df_display)).copy()
    gdf_level['id'] = gdf_level.index
    gdf_level = gdf_level.merge(df_display, left_on='id', right_on='id')

    # יצירת המפה
    try:
        fig = px.choropleth_map(
            gdf_level,
            geojson=geojson_raw,
            locations=gdf_level.index,
            color='מפלגה מובילה',
            hover_name='name',
            hover_data=['אחוז תמיכה'],
            color_discrete_map=PARTY_COLORS,
            map_style="carto-positron",
            center=center_coords,
            zoom=zoom_level,
            opacity=0.7
        )
    except AttributeError:
        fig = px.choropleth_mapbox(
            gdf_level,
            geojson=geojson_raw,
            locations=gdf_level.index,
            color='מפלגה מובילה',
            hover_name='name',
            hover_data=['אחוז תמיכה'],
            color_discrete_map=PARTY_COLORS,
            mapbox_style="carto-positron",
            center=center_coords,
            zoom=zoom_level,
            opacity=0.7
        )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("לא ניתן היה להטעין את מפת הבסיס הגיאוגרפית.")
