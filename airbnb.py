#Importing
import pandas as pd
import pymongo
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from PIL import Image
import geopandas as gpd
import plotly.graph_objs as go
#Set Page Configurations
st.set_page_config(page_title= "Airbnb Analysis",
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                  )
st.sidebar.header(":wave: :black[**Hello! Welcome to the dashboard**]")
# Creating option menu in the side bar
with st.sidebar:     # Navbar
        selected = option_menu(
                                menu_title="Airbnb",
                                options=['Home',"Analysis","Map","SWOT Analysis","Tableau Dashboard"],
                                icons = ['mic-fill','cash-stack','map','geo-alt-fill'],
                                menu_icon='alexa',
                                default_index=0,
                              )
        
#Converting csv file to dataframes
df=pd.read_csv('sample_airbnb.csv')
df=pd.DataFrame(df)

# Convert specific columns to numeric data types
numeric_columns = ['bedrooms', 'beds', 'number_of_reviews', 'bathrooms', 'price', 'cleaning_fee']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

#Home Page
if selected == "Home":
    st.title("Airbnb Analysis")
    col1,col2 = st.columns(2,gap= 'medium')
    col1.markdown("## :blue[Domain] : Travel Industry, Property Management and Tourism")
    col1.markdown("## :blue[Technologies used] : Python, Pandas, Plotly, Streamlit, MongoDB")
    col1.markdown("## :blue[Overview] : To analyze Airbnb data using MongoDB Atlas, perform data cleaning and preparation, develop interactive visualizations, and create dynamic plots to gain insights into pricing variations, availability patterns, and location-based trends. ")
    col2.markdown("#   ")
    col2.markdown("#   ")



# Analysis PAGE
elif selected == "Analysis":
    with st.sidebar:
        countries = df['address.country'].unique()
        country = st.multiselect(label='Select a Country', options=countries)
    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        all = st.checkbox('All Host_neighbourhood')
    with col2:
        cities = df[df['address.country'].isin(country)]['host.host_neighbourhood'].unique()
        city = st.selectbox(label='Select a Host_neighbourhood', options=cities, disabled=all)
    with col3:
        property_type = st.selectbox(label="Select a Property",options=['property_type', 'room_type', 'bed_type'])
    with col4:
        measure = st.selectbox(label='Select a Measure',options=numeric_columns)
    with col5:
        metric = st.radio(label="Select One",options=['Sum','Avg'])
    
    # Perform aggregation based on user selection
    if metric == 'Avg':
        a = df.groupby(['host.host_neighbourhood', property_type])[numeric_columns].mean().reset_index()
    else:
        a = df.groupby(['host.host_neighbourhood', property_type])[numeric_columns].sum().reset_index()

    if not all:
        b = a[a['host.host_neighbourhood'] == city] 
    else:
        if metric == 'Avg':
            a = df.groupby(['address.country', property_type])[numeric_columns].mean().reset_index()
        else:
            a = df.groupby(['address.country', property_type])[numeric_columns].sum().reset_index()
        b = a[a['address.country'].isin(country)] 

    # Display result
    st.header(f"{metric} of {measure}")
    with st.expander('View Dataframe'):
        st.write(b.style.background_gradient(cmap="Reds"))

    try:
        b['text'] = b['address.country'] + '<br>' + b[measure].astype(str)
        fig = px.bar(b, x=property_type, y=measure, color='address.country', text='text')
    except:
        b['text'] = b['host.host_neighbourhood'].astype(str) + '<br>' + b[measure].fillna(0).astype(str)
        fig = px.bar(b, x=property_type, y=measure, color=property_type, text='text')
    st.plotly_chart(fig, use_container_width=True)
    
    # donut chart
    fig = px.pie(b, names=property_type, values=measure, color=measure,hole=0.5)
    fig.update_traces(textposition='outside', textinfo='label+percent')
    st.plotly_chart(fig, use_container_width=True)

elif selected == 'Map':
    with st.sidebar:
        measure = st.selectbox(label='Select a measure', options=['bedrooms', 'beds', 'number_of_reviews', 'bathrooms', 'price', 'cleaning_fee'])

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    merged_data = pd.merge(world, df, left_on='name', right_on='address.country', how='inner')

    a = merged_data.groupby('address.country')[['bedrooms', 'beds', 'number_of_reviews', 'bathrooms', 'price', 'cleaning_fee']].mean().reset_index()
    b = merged_data.groupby('address.country')['iso_a3'].first()
    c = pd.merge(a,b,left_on='address.country', right_on='address.country', how='inner')
    fig = px.choropleth(c,
                        locations='iso_a3',
                        color=measure,
                        hover_name='address.country',
                        projection='natural earth', # 'natural earth','equirectangular', 'mercator', 'orthographic', 'azimuthal equal area'
                        color_continuous_scale='YlOrRd')
    fig.update_layout(
        title=f'Avg {measure}',
        geo=dict(
            showcoastlines=True,
            coastlinecolor='Black',
            showland=True,
            landcolor='white'
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    a = merged_data.groupby('address.country')[['bedrooms', 'beds', 'number_of_reviews', 'bathrooms', 'price', 'cleaning_fee']].sum().reset_index()
    b = merged_data.groupby('address.country')['iso_a3'].first()
    c = pd.merge(a, b, left_on='address.country', right_on='address.country', how='inner')
    fig = px.choropleth(c,
                        locations='iso_a3',
                        color=measure,
                        hover_name='address.country',
                        projection='natural earth',
                        # 'natural earth','equirectangular', 'mercator', 'orthographic', 'azimuthal equal area'
                        color_continuous_scale='YlOrRd')
    fig.update_layout(
        title=f'Total {measure}',
        geo=dict(
            showcoastlines=True,
            coastlinecolor='Black',
            showland=True,
            landcolor='white'
        )
    )
    st.plotly_chart(fig, use_container_width=True)

#SWOT Analysis
swot_data = {
    'Strength': [
        "Airbnb Enjoys First-Mover Advantage",
        "Innovative Business Model",
        "Offers a Unique Traveling Experience"
    ],
    'Weakness': [
        "Some Hosts Charge Inflated Prices",
        "Claims of Fraudulent Activities"
    ],
    'Opportunity': [
        "Expansion Into New Markets",
        "Increased Focus on Luxury Rentals"
    ],
    'Threats': [
        "Increased Competition",
        "Negative Guest Experiences",
        "User Data Security Leaks"
    ]
}

# Function to plot SWOT analysis
def plot_swot(category):
    data = swot_data.get(category, [])
    if data:
        fig = go.Figure(go.Bar(
            x=[1] * len(data),
            y=data,
            orientation='h',
            marker_color='lightskyblue'
        ))
        fig.update_layout(
            title=f"{category} Analysis",
            xaxis=dict(title="Count"),
            yaxis=dict(title="Factors"),
            showlegend=False
        )
        return fig
    else:
        return None

# Display SWOT analysis tabs and plots
if selected == "SWOT Analysis":
    st.title("SWOT Report")
    tab1, tab2, tab3, tab4 = st.tabs(["Strength", "Weakness", "Opportunity", "Threats"])

    with tab1:
        st.header("Strength")
        fig_strength = plot_swot("Strength")
        if fig_strength:
            st.plotly_chart(fig_strength, use_container_width=True)

    with tab2:
        st.header("Weakness")
        fig_weakness = plot_swot("Weakness")
        if fig_weakness:
            st.plotly_chart(fig_weakness, use_container_width=True)

    with tab3:
        st.header("Opportunity")
        fig_opportunity = plot_swot("Opportunity")
        if fig_opportunity:
            st.plotly_chart(fig_opportunity, use_container_width=True)

    with tab4:
        st.header("Threats")
        fig_threats = plot_swot("Threats")
        if fig_threats:
            st.plotly_chart(fig_threats, use_container_width=True)

elif selected == 'Tableau Dashboard':
    st.title("Airbnb Tableau Dashboard")
    st.write('It represent Visualization of Airbnb Database')
    

