import pandas as pd
import altair as alt
import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import pickle

st.set_page_config(page_title="NYC Biking Data", layout="wide")
st.title("Bike ridership in NYC")

### filter dfs func
def filter_df(df, counter_selection):
    new_df = df[df.index.get_level_values('id').isin(counter_selection)].copy()
    return new_df

# read files
with open('data/retrieval_date.pkl', 'rb') as f:
    retrieval_date = pickle.load(f)

hr = pd.read_pickle('data/streamlit_by_hr.pkl')
wk = pd.read_pickle('data/streamlit_by_wk.pkl')
counters = pd.read_pickle('data/streamlit_counters.pkl')
count_per_wk = hr.reset_index()[['id', 'counts']].groupby('id').sum()

all_counters = np.sort(list(counters['name'].unique()))

### SIDEBAR
with st.sidebar:
    selected_counters = st.multiselect("select counters:", 
                                options=all_counters
                                )
    if len(selected_counters)==0:
        selected_counter_ids = counters.index.to_list()
        selected_counters = all_counters
    else:
        selected_counter_ids = counters.loc[counters['name'].isin(selected_counters), :].index

    ## sidebar legend
    num_selected_counters = len(selected_counters)
    selected_counter_mapping = counters.loc[selected_counter_ids]
    selected_counter_mapping['count'] = 1

    # Create an Altair chart using the color encoding
    legend_chart = alt.Chart(selected_counter_mapping).mark_bar().encode(
        y=alt.Y('name:O', axis=alt.Axis(title=None), ),
        x=alt.X('count:Q', axis=alt.Axis(title=None, labels=False)), 
        color=alt.Color('color:N', scale=None)
    )
    legend_chart = legend_chart.configure_legend(disable=True).properties(width=200)
    legend_chart = legend_chart.configure_axis(labelLimit=350)
    st.write('')
    st.altair_chart(legend_chart, use_container_width=False)

### filter dfs
select_counters = filter_df(counters, selected_counter_ids)
select_hr = filter_df(hr, selected_counter_ids)
select_wk = filter_df(wk, selected_counter_ids)

### HOURLY line chart
hr_chart = alt.Chart(select_hr.reset_index()).mark_line().encode(
    x=alt.X('utchoursminutes(display_time):T', axis=alt.Axis(title=None, format='%-I %p')),
    y=alt.Y('counts:Q', title='counts'),
    color=alt.Color('color:N', scale=None),
    tooltip='name'
)

hr_chart = hr_chart.configure_axis(
    labelAngle=-45
)

### WEEKLY line chart
wk_chart = alt.Chart(select_wk.reset_index()).mark_line().encode(
    x=alt.X('display_date:T', axis=alt.Axis(tickCount={"interval": "month", "step": 1}, tickExtra=True, grid=True), title=None),
    y=alt.Y('counts:Q', title='counts'),
    color=alt.Color('color:N', scale=None),
    tooltip='name'
)

wk_chart = wk_chart.configure_axis(
    labelAngle=-45
)

### map
m = folium.Map(location=[40.720, -74.0060], zoom_start=12)
folium.TileLayer('cartodbdark_matter').add_to(m)

for i, c in select_counters.iterrows():
    # establish params
    lat = c['latitude']
    long = c['longitude']
    name = c['name']
    id = i
    count = count_per_wk.loc[id]
    color = c['color']

    # create tooltip
    tooltip_content = f"""
    <p style="font-family: monospace;"><strong>{name}<br>
     {int(np.round(count[0],0))}</strong> daily riders</p>
"""
    # create markers
    circle = folium.CircleMarker(
        location=(lat,long),
        tooltip=folium.Tooltip(tooltip_content),
        radius=count[0] * 0.025,
        color=color,
        fill=True,
        fill_color=color,
        highlight=True
    ).add_to(m)


# render
col1, col2= st.columns(2)

with col1:
    st.markdown("<h4 style='text-align: center;'>avg. ridership throughout the day</h4>", unsafe_allow_html=True)
    st.altair_chart(hr_chart, use_container_width=True)
with col1:
    st.markdown("<h4 style='text-align: center;'>avg. ridership throughout the year</h4>", unsafe_allow_html=True)
    st.altair_chart(wk_chart, use_container_width=True)
with col2:
    st.markdown("<h4 style='text-align: center;'>bike counter locations</h4>", unsafe_allow_html=True)
    st_data = st_folium(m, use_container_width=True)