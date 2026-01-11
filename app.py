import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

# Custom CSS untuk warna pastel dan styling
st.markdown("""
    <style>
    .main { background-color: #FDFCF0; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #6D8299; }
    </style>
    """, unsafe_allow_safe_config=True)

# Warna Pastel Palette
PASTEL_COLORS = ['#AEC6CF', '#FFB7B2', '#B2E2F2', '#FFDAC1', '#E2F0CB', '#B5EAD7']

# 2. LOAD & CLEAN DATA
@st.cache_data
def load_data():
    df = pd.read_csv('Customer Churn Analysis.csv')
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df.dropna(inplace=True)
    return df

try:
    df = load_data()

    # SIDEBAR
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2620/2620667.png", width=100)
    st.sidebar.title("Filter Analisis")
    selected_contract = st.sidebar.multiselect("Pilih Tipe Kontrak:", 
                                               options=df['Contract'].unique(), 
                                               default=df['Contract'].unique())
    
    filtered_df = df[df['Contract'].isin(selected_contract)]

    # 3. HEADER & KPI METRICS
    st.title("📊 Customer Churn Analysis Dashboard")
    st.markdown("Dashboard interaktif untuk memantau perilaku pelanggan dan risiko churn.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Pelanggan", len(filtered_df))
    with col2:
        churn_rate = (filtered_df['Churn'] == 'Yes').mean() * 100
        st.metric("Churn Rate", f"{churn_rate:.1f}%", delta_color="inverse")
    with col3:
        avg_monthly = filtered_df['MonthlyCharges'].mean()
        st.metric("Rata-rata Tagihan", f"${avg_monthly:.2f}")
    with col4:
        total_rev = filtered_df['TotalCharges'].sum()
        st.metric("Total Revenue", f"${total_rev/1e6:.2f}M")

    st.divider()

    # 4. VISUALISASI UTAMA
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("💡 Churn Berdasarkan Kontrak")
        fig_contract = px.histogram(filtered_df, x="Contract", color="Churn", 
                                    barmode="group",
                                    color_discrete_sequence=[PASTEL_COLORS[0], PASTEL_COLORS[1]])
        fig_contract.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_contract, use_container_width=True)

    with row1_col2:
        st.subheader("🌐 Layanan Internet vs Churn")
        fig_internet = px.sunburst(filtered_df, path=['InternetService', 'Churn'], 
                                   color='InternetService',
                                   color_discrete_sequence=PASTEL_COLORS[2:])
        st.plotly_chart(fig_internet, use_container_width=True)

    row2_col1, row2_col2 = st.columns([2, 1])

    with row2_col1:
        st.subheader("📈 Hubungan Tenure & Tagihan Bulanan")
        fig_scatter = px.scatter(filtered_df, x="tenure", y="MonthlyCharges", 
                                 color="Churn", size="MonthlyCharges",
                                 color_discrete_sequence=[PASTEL_COLORS[4], PASTEL_COLORS[1]],
                                 opacity=0.6)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with row2_col2:
        st.subheader("💳 Metode Pembayaran")
        payment_counts = filtered_df['PaymentMethod'].value_counts()
        fig_pie = px.pie(values=payment_counts.values, names=payment_counts.index,
                         color_discrete_sequence=PASTEL_COLORS)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    # 5. DATA TABLE
    with st.expander("Lihat Detail Data Mentah"):
        st.dataframe(filtered_df.head(100), use_container_width=True)

except Exception as e:
    st.error(f"Gagal memuat dashboard. Pastikan file CSV tersedia. Error: {e}")
