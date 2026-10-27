import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="מפת בחירות בישראל", layout="wide")
st.title("מפת בחירות בישראל - תצוגה רציפה ללא חורים")

# 1. משיכת קובץ ה-GeoJSON אונליין ממקור יציב
@st.cache_data
def load_geojson():
    urls = [
        "https://raw.githubusercontent.com/datasets/geo-boundaries/master/data/ISR.geojson"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                geojson_data = response.json()
                gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
                gdf.crs = "EPSG:4326"
                return geojson_data, gdf
        except Exception:
            continue
            
    return None, None

geojson_raw, gdf = load_geojson()

if gdf is not None:
    # זיהוי עמודת השמות הקיימת בקובץ ה-GeoJSON
    if 'name' in gdf.columns:
        name_column = 'name'
    elif 'shapeName' in gdf.columns:
        name_column = 'shapeName'
    else:
        name_column = gdf.columns[0]

    regions = gdf[name_column].tolist()
    
    # 2. נתוני הצבעה לדוגמה
    party_mapping = {
        'הליכוד': '#2196F3',
        'יש עתיד': '#FF9800',
        'הציונות הדתית': '#00BCD4',
        'המחנה הממלכתי': '#9C27B0',
        'ש"ס': '#795548'
    }
    
    parties = list(party_mapping.keys())

    # בניית Dataframe עם שיוך מפלגה לכל פוליגון
    df_results = pd.DataFrame([
        {
            'region_id': idx,
            'region_name': region,
            'מפלגה מובילה': parties[idx % len(parties)],
            'color': party_mapping[parties[idx % len(parties)]]
        }
        for idx, region in enumerate(regions)
    ])

    gdf['region_id'] = gdf.index
    gdf = gdf.merge(df_results, on='region_id')

    # 3. יצירת המפה באמצעות Plotly Express
    try:
        fig = px.choropleth_map(
            gdf,
            geojson=geojson_raw,
            locations=gdf.index,
            color='מפלגה מובילה',
            hover_name='region_name',
            map_style="carto-positron",
            center={"lat": 31.5, "lon": 34.75},
            zoom=7,
            opacity=0.65
        )
    except AttributeError:
        fig = px.choropleth_mapbox(
            gdf,
            geojson=geojson_raw,
            locations=gdf.index,
            color='מפלגה מובילה',
            hover_name='region_name',
            mapbox_style="carto-positron",
            center={"lat": 31.5, "lon": 34.75},
            zoom=7,
            opacity=0.65
        )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("לא ניתן היה להוריד את קובץ ה-GeoJSON מכל השרתים. מומלץ לשמור את הקובץ מקומית בתיקיית הפרויקט.")
