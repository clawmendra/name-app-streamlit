import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import requests
import zipfile
from io import BytesIO
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from my_plots import *

st.title('Names From Social Security Data')

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data
data = load_name_data()


tab1, tab2 = st.tabs(['Names', 'Year'])

with tab1:
    st.write("Can't think of a name? Generate one here.")
    random_name = np.random.choice(data['name'])
    if st.button("Give me a name!", type='primary'):
        st.write(f"Try entering the name, {random_name}.")
    else:
        st.write('')

    input_name = st.text_input('Enter a name:', 'Mary')
    name_data = data[data['name'] == input_name].copy()
    fig1 = name_trend_plot(df=name_data, name=input_name)
    st.plotly_chart(fig1)
    with st.expander("See explanation"):
        st.write('''
        In the graph, "Sex Balance Ratio Over Time," 0 indicates no names
                 were listed while 1 indicates all names were listed under
                 that gender.
                 ''')
    
    
with tab2:
    st.sidebar.header('Source to Names Data')
    st.sidebar.markdown('[Link to Data](https://www.ssa.gov/oact/babynames/background.html)')
    year_input = st.slider('Year', min_value=1880, max_value=2023, value=2000)
    n_names = st.radio('Number of Names per Sex', [3, 5, 10])
    fig2 = top_names_plot(df=data, year=year_input, n=n_names)
    st.plotly_chart(fig2)
    st.write(f"Unique Names in {year_input}")
    fig3 = unique_names_summary(df=data, year=year_input)
    st.dataframe(fig3)
    
