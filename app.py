import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

# Custom CSS untuk tampilan Pastel & UI Modern
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.02);
    }
    h1, h2, h3 { color: #6D8299; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# Palet Warna Pastel
PASTEL_PALETTE = ['#AEC6CF', '#FFB7B2', '#B2E2F2', '#FFDAC1', '#E2F0CB', '#B5EAD7']

# --- 2. ETL & DATA CLEANING ---
@st.cache_data
def load_and_clean_data():
    file_path = 'WA_Fn-UseC_-Telco-Customer-Churn.csv'
    try:
        df = pd.read_csv(file_path)
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        df.dropna(subset=['TotalCharges'], inplace=True)
        df['PaymentMethod'] = df['PaymentMethod'].str.replace(' (automatic)', '', regex=False)
        return df
    except FileNotFoundError:
        return None

df = load_and_clean_data()

if df is not None:
    # --- 3. SIDEBAR FILTER ---
    st.sidebar.header("⚙️ Filter Dashboard")
    contract_filter = st.sidebar.multiselect(
        "Pilih Tipe Kontrak:",
        options=df['Contract'].unique(),
        default=df['Contract'].unique()
    )
    
    filtered_df = df[df['Contract'].isin(contract_filter)]

    # --- 4. HEADER & KPI METRICS ---
    st.title("📊 Customer Churn Business Intelligence")
    st.markdown("Dashboard analisis untuk mendeteksi profil pelanggan dan risiko churn.")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Pelanggan", len(filtered_df))
    with m2:
        churn_rate = (filtered_df['Churn'] == 'Yes').mean() * 100
        st.metric("Churn Rate", f"{churn_rate:.1f}%")
    with m3:
        st.metric("Rata-rata Tenure", f"{filtered_df['tenure'].mean():.1f} Bln")
    with m4:
        st.metric("Total Revenue", f"${filtered_df['TotalCharges'].sum()/1e3:.1f}K")

    st.divider()

    # --- 5. VISUALISASI BARIS ATAS (Layanan & Kontrak) ---
    col_top1, col_top2 = st.columns(2)

    with col_top1:
        st.subheader("📶 Layanan Internet")
        service_churn = filtered_df.groupby(['InternetService', 'Churn']).size().reset_index(name='Jumlah')
        fig_service = px.bar(service_churn, x="InternetService", y="Jumlah", color="Churn",
                             barmode="group", color_discrete_sequence=[PASTEL_PALETTE[2], PASTEL_PALETTE[1]])
        fig_service.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_service, use_container_width=True)

    with col_top2:
        st.subheader("📝 Tipe Kontrak")
        fig_bar = px.histogram(filtered_df, x="Contract", color="Churn",
                               barmode="group", color_discrete_sequence=[PASTEL_PALETTE[0], PASTEL_PALETTE[1]])
        fig_bar.update_layout(height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- 6. VISUALISASI BARIS TENGAH (Pie Chart Ukuran Kecil) ---
    st.divider()
    col_mid1, col_mid2 = st.columns([1, 1]) # Dibagi dua agar ukuran Pie tidak melebar

    with col_mid1:
        st.subheader("💳 Metode Pembayaran")
        fig_pie = px.pie(filtered_df, names='PaymentMethod', hole=0.5, 
                         color_discrete_sequence=PASTEL_PALETTE)
        # Mengatur ukuran (height) agar sama dengan bar chart di atas
        fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        fig_pie.update_traces(textinfo='percent', textposition='inside')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_mid2:
        st.subheader("ℹ️ Informasi Tambahan")
        st.write("Distribusi metode pembayaran menunjukkan bagaimana pelanggan menyelesaikan tagihan mereka.")
        st.write("- **Electronic Check** seringkali berkorelasi dengan angka churn yang lebih tinggi.")
        st.write("- **Credit Card** dan **Bank Transfer** cenderung digunakan oleh pelanggan yang lebih stabil.")

    st.divider()

    # --- 7. DATA MINING (CLUSTERING) ---
    st.subheader("🎯 Segmentasi Pelanggan")
    X = filtered_df[['tenure', 'MonthlyCharges']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=3, random_state=42)
    filtered_df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    fig_cluster = px.scatter(filtered_df, x="tenure", y="MonthlyCharges", 
                             color=filtered_df['Cluster'].astype(str), 
                             symbol="Churn",
                             color_discrete_sequence=PASTEL_PALETTE)
    fig_cluster.update_layout(height=450)
    st.plotly_chart(fig_cluster, use_container_width=True)

    # --- 8. TABEL DATA ---
    with st.expander("🔍 Lihat Detail Data Mentah"):
        st.dataframe(filtered_df.head(100), use_container_width=True)

else:
    st.error("File 'WA_Fn-UseC_-Telco-Customer-Churn.csv' tidak ditemukan.")
