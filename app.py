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
def filter_df_counters(df, counter_selection):
    new_df = df[df.index.get_level_values('id').isin(counter_selection)].copy()
    return new_df

def filter_df_dates(df, start_date, end_date):
    date_idx = df.index.get_level_values('date')
    criteria = (date_idx >= start_date) & (date_idx<=end_date)
    new_df = df.loc[criteria].copy()
    return new_df

# read files
with open('data/retrieval_date.pkl', 'rb') as f:
    retrieval_date = pickle.load(f)

hr = pd.read_pickle('data/streamlit_by_hr.pkl')
wk = pd.read_pickle('data/streamlit_by_wk.pkl')
hist_wk = pd.read_pickle('data/streamlit_hist_by_wk.pkl')
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


    select_hist_wk = filter_df_counters(hist_wk, selected_counter_ids)
    date_list = pd.to_datetime(select_hist_wk.index.get_level_values('date').to_series().dt.strftime('%Y-%m').unique()).to_series()

    selected_dates = st.select_slider('select historical chart dates:',
                                    value=[date_list[0], date_list[-1]],
                                    options=date_list,
                                    label_visibility='collapsed',
                                    format_func=lambda date_list: date_list.strftime('%b-%Y')
                                    ) 
    if len(selected_dates)==0:
        selected_dates = (date_list[0], date_list[-1])
    start_date = selected_dates[0]
    end_date = selected_dates[1]

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
select_counters = filter_df_counters(counters, selected_counter_ids)
select_hr = filter_df_counters(hr, selected_counter_ids)
select_wk = filter_df_counters(wk, selected_counter_ids)
select_hist_wk = filter_df_dates(select_hist_wk, start_date, end_date)

### HOURLY LINE CHART
hr_chart = alt.Chart(select_hr.reset_index()).mark_line().encode(
    x=alt.X('utchoursminutes(display_time):T', axis=alt.Axis(title=None, format='%-I %p', grid=True)),
    y=alt.Y('counts:Q', title='riders per hour'),
    color=alt.Color('color:N', scale=None)
)

# Create a selection that chooses the nearest point & selects based on x-value
nearest_hr = alt.selection_point(nearest=True, on='mouseover',
                        fields=['display_time'], empty=False)

# Transparent selectors across the chart. This is what tells us
# the x-value of the cursor
selectors = alt.Chart(select_hr.reset_index()).mark_point().encode(
    x='utchoursminutes(display_time):T',
    opacity=alt.value(0),
    tooltip=alt.value(None)
).add_params(
    nearest_hr
)

# Draw points on the line, and highlight based on selection
points = hr_chart.mark_point().encode(
    opacity=alt.condition(nearest_hr, alt.value(1), alt.value(0))
)

# Draw text labels near the points, and highlight based on selection
text = hr_chart.mark_text(align='left', dx=10, dy=10).encode(
    text=alt.condition(nearest_hr, alt.Text('counts:Q', format='.0f'), alt.value(' '))
)

# Draw a rule at the location of the selection
rules = alt.Chart(select_hr.reset_index()).mark_rule(color='gray').encode(
    x='utchoursminutes(display_time):T'
).transform_filter(
    nearest_hr
)

# Put the five layers into a chart and bind the data
hr_chart_bound = alt.layer(
    hr_chart, selectors, points, rules, text
)

### WEEKLY LINE CHART
wk_chart = alt.Chart(select_wk.reset_index()).mark_line().encode(
    x=alt.X('display_date:T', axis=alt.Axis(tickCount={"interval": "month", "step": 1}, tickExtra=True, grid=True), title=None),
    y=alt.Y('counts:Q', title='riders per week'),
    color=alt.Color('color:N', scale=None),
    tooltip=['name:O', 'counts:Q', 'display_date:T']
)

# Create a selection that chooses the nearest point & selects based on x-value
nearest_wk = alt.selection_point(nearest=True, on='mouseover',
                        fields=['display_date'], empty=False)

# Transparent selectors across the chart. This is what tells us
# the x-value of the cursor
selectors = alt.Chart(select_wk.reset_index()).mark_point().encode(
    x='display_date:T',
    opacity=alt.value(0),
    tooltip=alt.value(None)
).add_params(
    nearest_wk
)

# Draw points on the line, and highlight based on selection
points = wk_chart.mark_point().encode(
    opacity=alt.condition(nearest_wk, alt.value(1), alt.value(0))
)

# Draw text labels near the points, and highlight based on selection
text = wk_chart.mark_text(align='left', dx=10, dy=10).encode(
    text=alt.condition(nearest_wk, alt.Text('counts:Q', format=',.0f'), alt.value(' '))
)

# Draw a rule at the location of the selection
rules = alt.Chart(select_wk.reset_index()).mark_rule(color='gray').encode(
    x='display_date:T'
).transform_filter(
    nearest_wk
)

# Put the five layers into a chart and bind the data
wk_chart_bound = alt.layer(
    wk_chart, selectors, points, rules, text
)

wk_chart_bound = wk_chart_bound.configure_axis(
    labelAngle=-45
)

### HISTORICAL WEEKLY CHART
hist_wk_chart = alt.Chart(select_hist_wk.reset_index()).mark_line().encode(
    x=alt.X('date:T', axis=alt.Axis(tickCount={'interval':'month', 'step':3}, title=None, format='%b-%Y')),
    y=alt.Y('counts:Q', title='riders per week'),
    color=alt.Color('color:N', scale=None),
    tooltip='name:O'
)



### MAP
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
        radius=count[0] * 0.008,
        color=color,
        fill=True,
        fill_color=color,
        highlight=True
    ).add_to(m)


# render
col1, col2= st.columns(2)

with col1:
    st.markdown("<h4 style='text-align: center;'>avg. ridership per hour of the day</h4>", unsafe_allow_html=True)
    st.altair_chart(hr_chart_bound, use_container_width=True)
with col1:
    st.markdown("<h4 style='text-align: center;'>avg. ridership per week of the year</h4>", unsafe_allow_html=True)
    st.altair_chart(wk_chart_bound, use_container_width=True)
with col2:
    st.markdown("<h4 style='text-align: center;'>bike counter locations</h4>", unsafe_allow_html=True)
    st_data = st_folium(m, use_container_width=True)

st.altair_chart(hist_wk_chart, use_container_width=True)