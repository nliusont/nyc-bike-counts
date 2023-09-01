import pandas as pd
import altair as alt
import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import numpy as np
import pickle
import random

st.set_page_config(page_title="NYC Biking Data", layout="wide")


# read files
with open('data/retrieval_date.pkl', 'rb') as f:
    retrieval_date = pickle.load(f)
hr = pd.read_pickle('data/by_hour.pkl')
geo = pd.read_pickle('data/counters.pkl')
count_per_day = hr[['name', 'counts']].groupby('name').sum()


# colors
cat_20 = ['#1f77b4',
    '#aec7e8',
    '#ff7f0e',
    '#ffbb78',
    '#2ca02c',
    '#98df8a',
    '#d62728',
    '#ff9896',
    '#9467bd',
    '#c5b0d5',
    '#8c564b',
    '#c49c94',
    '#e377c2',
    '#f7b6d2',
    '#7f7f7f',
    '#c7c7c7',
    '#bcbd22',
    '#dbdb8d',
    '#17becf',
    '#9edae5'
    ]

# map all counters to colors randomly
counters = list(geo['name'].unique())
num_counters = len(counters)
color_indices = np.linspace(0, len(cat_20)-1, num_counters, dtype=int)
colors = [cat_20[x] for x in color_indices]
color_dict = dict(zip(counters, colors))
#create color column
geo['color'] = geo['name'].map(color_dict)
hr['color'] = hr['name'].map(color_dict)

### line chart
chart = alt.Chart(hr).mark_line().encode(
    x='hr:O',
    y=alt.Y('counts:Q', title='counts'),
    color=alt.Color('color:N', scale=None) # Color by series_name
)

### map
m = folium.Map(location=[40.720, -74.0060], zoom_start=12)

for i, c in geo.iterrows():
    # establish params
    lat = c['latitude']
    long = c['longitude']
    name = c['name']
    count = count_per_day.loc[name]
    color = color_dict[name]

    # create tooltip
    tooltip_content = f"""
    <p style="font-family: monospace;"><strong>{name}<br>
     {int(np.round(count[0],0))}</strong> daily riders</p>
"""
    # create markers
    folium.CircleMarker(
        location=(lat,long),
        tooltip=folium.Tooltip(tooltip_content),
        radius=count[0] * 0.025,
        color=color,
        fill=True,
        fill_color=color
    ).add_to(m)

# Add a customized TileLayer to the map
folium.TileLayer('cartodbdark_matter').add_to(m)
    

# render
col1, col2= st.columns(2)
with col1:
    st_data = st_folium(m, use_container_width=True)
col2.altair_chart(chart, use_container_width=True,)