import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Analisis Penyewaan Sepeda", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df['date'] = pd.to_datetime(df['date'])
    season_map = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}
    df['season_name'] = df['season'].map(season_map)
    df['year_label'] = df['year'].map({0: '2011', 1: '2012'})
    return df

df = load_data()

# Sidebar 
with st.sidebar:
    st.header("Filter Data")
    sel_year = st.radio("Pilih Tahun", ['Semua', '2011', '2012'], key="year_filter")
    all_seasons = df['season_name'].unique().tolist()
    sel_seasons = st.multiselect("Pilih Musim", all_seasons, default=all_seasons, key="season_filter")

# Logika filter
dff = df.copy()
if sel_year != 'Semua':
    dff = dff[dff['year_label'] == sel_year]
dff = dff[dff['season_name'].isin(sel_seasons)]

# Header
st.title("Dashboard Analisis Penyewaan Sepeda")

total_rentals = dff['total_users'].sum()
total_casual = dff['casual'].sum()
total_registered = dff['registered'].sum()
total_semua = dff['total_users'].sum()

k1, k2, k3 = st.columns(3)
k1.metric("Total Penyewaan", f"{total_semua:,}")
k2.metric("Total Penyewaan Pengguna Casual", f"{total_casual:,}")
k3.metric("Total Penyewaan Pengguna Registered", f"{total_registered:,}")

st.markdown("---")

# Tab Navigasi
tab1, tab2 = st.tabs(["Overview & Kategori", "YoY Growth"])


# Isi Tab
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.subheader("Tren Harian")
            daily = dff.groupby('date')['total_users'].sum().reset_index()
            fig = px.area(daily, x='date', y='total_users')
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        with st.container(border=True):
            st.subheader("Penyewaan per Musim")
            season_agg = dff.groupby('season_name')['total_users'].sum().reset_index()
            fig_bar = px.bar(season_agg, x='season_name', y='total_users', color='season_name')
            st.plotly_chart(fig_bar, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        with st.container(border=True):
            st.subheader("User: Casual vs Registered")
            cat_df = dff.melt(id_vars=['season_name'], value_vars=['casual', 'registered'], 
                              var_name='Tipe', value_name='Jumlah')
            fig = px.bar(cat_df.groupby(['season_name', 'Tipe'])['Jumlah'].sum().reset_index(), 
                         x='season_name', y='Jumlah', color='Tipe', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    with c4:
        with st.container(border=True):
            st.subheader("Tren Tahun & Musim")
            fig = px.sunburst(dff, path=['year_label', 'season_name'], values='total_users')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Year-over-Year Growth")
    monthly_growth = df.groupby(['year_label', 'month'])['total_users'].sum().unstack(0)
    monthly_growth['Growth %'] = ((monthly_growth['2012'] - monthly_growth['2011']) / monthly_growth['2011']) * 100
    fig = px.bar(monthly_growth, y='Growth %', title="Persentase Pertumbuhan Bulanan (2011 ke 2012)")
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)
    st.info("YoY Growth: 64.88%")
