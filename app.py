import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. SET CONFIG (Harus di bagian paling atas) ---
st.set_page_config(page_title="Pastel Financial Dashboard", layout="wide")

# --- 2. CUSTOM CSS UNTUK TAMPILAN PASTEL ---
st.markdown("""
    <style>
    .main { background-color: #FDFEFF; }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.02);
        border-left: 5px solid #FFB7B2;
    }
    .stPlotlyChart { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOAD DATA (DENGAN PENGECEKAN PATH) ---
@st.cache_data
def load_data():
    # Mencari file di direktori saat ini
    file_name = "Financial Sample.xlsx"
    if not os.path.exists(file_name):
        return None
    
    df = pd.read_excel(file_name)
    # Standarisasi kolom
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    
    # Pembersihan data finansial (menghapus $, koma, dan kurung)
    cols_to_clean = ['sales', 'profit', 'gross_sales', 'cogs', 'discounts']
    for col in cols_to_clean:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(r'[\$,]', '', regex=True)
            df[col] = df[col].str.replace(r'\(', '-', regex=True).str.replace(r'\)', '', regex=True).astype(float)
    
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# --- 4. VALIDASI DATA ---
if df is None:
    st.error(f"❌ File 'Financial Sample.xlsx' tidak ditemukan di root folder GitHub Anda!")
    st.info("Pastikan nama file di GitHub sama persis (Besar/Kecil hurufnya) dan berada di luar folder (root).")
    st.stop()

# --- 5. DASHBOARD UI ---
st.title("🌸 Financial Intelligence Dashboard")
st.write("Visualisasi data finansial dengan palet warna lembut.")

# Filter di Sidebar
with st.sidebar:
    st.header("Filter Data")
    country = st.multiselect("Pilih Negara", df['country'].unique(), default=df['country'].unique())
    segment = st.multiselect("Pilih Segmen", df['segment'].unique(), default=df['segment'].unique())

df_filtered = df[(df['country'].isin(country)) & (df['segment'].isin(segment))]

# Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${df_filtered['sales'].sum():,.0f}")
col2.metric("Total Profit", f"${df_filtered['profit'].sum():,.0f}")
col3.metric("Units Sold", f"{df_filtered['units_sold'].sum():,.0f}")

# Charts Row
c1, c2 = st.columns(2)
with c1:
    fig_line = px.line(df_filtered.groupby('date')['sales'].sum().reset_index(), 
                       x='date', y='sales', title="Tren Penjualan",
                       color_discrete_sequence=['#B2CEE0'])
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    fig_pie = px.pie(df_filtered, values='profit', names='product', 
                     title="Profit per Produk",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("🌍 Peta Penjualan Global")

fig_map = px.choropleth(df_filtered.groupby('country')['sales'].sum().reset_index(),
                        locations="country", locationmode='country names',
                        color="sales", color_continuous_scale="Pastel")
st.plotly_chart(fig_map, use_container_width=True)
