import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Financial Intelligence Dashboard",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. CUSTOM CSS (ESTETIKA PASTEL MODERN) ---
st.markdown("""
    <style>
    /* Mengubah font dan background utama */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #FBFBFE;
    }
    
    /* Styling Card Metrik */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.02);
        border-left: 6px solid #B2E2F2; /* Pastel Blue */
        transition: transform 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }
    
    /* Tombol Sidebar */
    .stMultiSelect div[role="listbox"] {
        border-radius: 10px;
    }
    
    /* Menghilangkan menu Streamlit di atas */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING & ETL ---
@st.cache_data
def load_and_clean_data():
    file_path = "Financial Sample.xlsx"
    
    if not os.path.exists(file_path):
        return None
        
    df = pd.read_excel(file_path)
    
    # Transformasi: Standarisasi Nama Kolom
    df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
    
    # Cleaning: Konversi Tipe Data & Finansial
    df['date'] = pd.to_datetime(df['date'])
    
    cols_finansial = ['sales', 'profit', 'gross_sales', 'discounts', 'cogs']
    for col in cols_finansial:
        if df[col].dtype == 'object':
            # Hilangkan simbol mata uang, koma, dan tangani angka negatif dalam kurung
            df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df[col] = df[col].str.replace('(', '-', regex=False).str.replace(')', '', regex=False).astype(float)
            
    return df

df = load_and_clean_data()

# --- 4. ERROR HANDLING ---
if df is None:
    st.error("⚠️ File 'Financial Sample.xlsx' tidak ditemukan!")
    st.markdown("Pastikan file Excel Anda berada di root folder yang sama dengan `app.py` di GitHub.")
    st.stop()

# --- 5. SIDEBAR FILTERING ---
st.sidebar.markdown("### 🎨 Filter Analisis")
country_list = st.sidebar.multiselect("Pilih Negara", options=df['country'].unique(), default=df['country'].unique())
segment_list = st.sidebar.multiselect("Pilih Segmen", options=df['segment'].unique(), default=df['segment'].unique())

# Filter DataFrame
df_filtered = df[(df['country'].isin(country_list)) & (df['segment'].isin(segment_list))]

# --- 6. HEADER ---
st.title("✨ Financial Intelligence Dashboard")
st.markdown(f"**Ringkasan Performa Bisnis:** {df_filtered['date'].min().strftime('%B %Y')} - {df_filtered['date'].max().strftime('%B %Y')}")

# --- 7. ROW 1: KEY PERFORMANCE INDICATORS (KPI) ---
m1, m2, m3, m4 = st.columns(4)

total_sales = df_filtered['sales'].sum()
total_profit = df_filtered['profit'].sum()
total_units = df_filtered['units_sold'].sum()
avg_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

m1.metric("Total Sales", f"${total_sales/1e6:.2f}M")
m2.metric("Total Profit", f"${total_profit/1e6:.2f}M")
m3.metric("Units Sold", f"{total_units:,.0f}")
m4.metric("Profit Margin", f"{avg_margin:.1f}%")

st.write("") # Spacer

# --- 8. ROW 2: TREND & SEGMENTATION ---
col_trend, col_pie = st.columns([2, 1])

with col_trend:
    st.subheader("📈 Tren Penjualan Bulanan")
    df_monthly = df_filtered.groupby(pd.Grouper(key='date', freq='M'))['sales'].sum().reset_index()
    fig_line = px.area(df_monthly, x='date', y='sales', 
                       color_discrete_sequence=['#B2CEE0']) # Pastel Blue
    fig_line.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="", yaxis_title="Sales ($)"
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_pie:
    st.subheader("🍕 Profit per Produk")
    fig_pie = px.pie(df_filtered, values='profit', names='product',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_pie.update_traces(hole=.5, textinfo='percent+label')
    fig_pie.update_layout(showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 9. ROW 3: GEOGRAPHIC ANALYSIS ---
st.subheader("🌍 Distribusi Penjualan Global")

map_data = df_filtered.groupby('country')['sales'].sum().reset_index()
fig_map = px.choropleth(
    map_data,
    locations="country",
    locationmode='country names',
    color="sales",
    color_continuous_scale=["#F9E1E0", "#FFB7B2", "#B2E2F2", "#B2CEE0"], # Custom Pastel Gradient
    labels={'sales': 'Total Sales ($)'}
)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# --- 10. ROW 4: DATA EXPLORER ---
with st.expander("🔍 Lihat Detail Transaksi"):
    st.dataframe(
        df_filtered.sort_values(by='date', ascending=False),
        use_container_width=True
    )

st.caption("Dashboard Finansial v1.0 | Dibuat dengan Streamlit & Plotly")
