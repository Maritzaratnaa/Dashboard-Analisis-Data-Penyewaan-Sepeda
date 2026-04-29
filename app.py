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
    # Mapping untuk label
    season_map = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}
    df['season_name'] = df['season'].map(season_map)
    df['year_label'] = df['year'].map({0: '2011', 1: '2012'})
    return df

df = load_data()

# Sidebar
with st.sidebar:
    st.header("Filter Data")
    
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    # Error handling input tanggal
    try:
        date_range = st.date_input(
            "Pilih Rentang Tanggal",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        start_date, end_date = date_range
    except ValueError:
        st.error("Silakan pilih rentang tanggal (Tanggal Mulai & Tanggal Selesai)")
        st.stop()
    
    season_options = df['season_name'].unique().tolist()
    options_with_all = ["Pilih Semua"] + season_options
    
    sel_seasons_raw = st.multiselect(
        "Pilih Musim", 
        options=options_with_all, 
        default=["Pilih Semua"]
    )

# Filter
if "Pilih Semua" in sel_seasons_raw or not sel_seasons_raw:
    final_seasons = season_options
else:
    final_seasons = sel_seasons_raw

dff = df[
    (df['date'] >= pd.to_datetime(start_date)) & 
    (df['date'] <= pd.to_datetime(end_date)) &
    (df['season_name'].isin(final_seasons))
]

st.title("Dashboard Analisis Penyewaan Sepeda")

# Jika data tidak ditemukan
if dff.empty:
    st.warning("Data tidak ditemukan untuk rentang waktu atau musim yang dipilih.")
    st.stop()

# Jika data ditemukan
col1, col2, col3 = st.columns(3)
col1.metric("Total Penyewaan", f"{dff['total_users'].sum():,}")
col2.metric("Total Casual", f"{dff['casual'].sum():,}")
col3.metric("Total Registered", f"{dff['registered'].sum():,}")

st.markdown("---")

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
        summary_cat = cat_df.groupby(['season_name', 'Tipe'])['Jumlah'].sum().reset_index()
        fig = px.bar(summary_cat, x='season_name', y='Jumlah', color='Tipe', barmode='group')
        st.plotly_chart(fig, use_container_width=True)
with c4:
    with st.container(border=True):
        st.subheader("Distribusi Tahun & Musim")
        fig = px.sunburst(dff, path=['year_label', 'season_name'], values='total_users')
        st.plotly_chart(fig, use_container_width=True)
    
st.divider()
st.caption("Maritza Ratnamaya Nugroho - CDCC011D6X0609")