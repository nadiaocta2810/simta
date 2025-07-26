import streamlit as st
import pandas as pd
import plotly.express as px
# from auth import protect_page, logout_button

# protect_page()  # Wajib untuk ngecek login
# logout_button() # Optional, munculkan tombol logout

st.set_page_config(page_title="Plotting Dosen Skripsi", layout="wide")
def logo_dashboard():
    col1, col2, col3 = st.columns([8.5, 0.5, 2.5])
    with col1:
        st.markdown("<h1 style='color:#005691'>Plotting Dosen Pembimbing</h1>", unsafe_allow_html=True)
    with col3:
        subcol1, subcol2, subcol3 = st.columns(3)
        with subcol1:
            st.image("asset/logoti.png", width=30)
        with subcol2:
            st.image("asset/logoub.png", width=50)
        with subcol3:
            st.image("asset/logodampak.png", width=50)

logo_dashboard()

st.markdown(
    "[Raw Data Plotting Dosen Pembimbing dapat diakses di sini](https://docs.google.com/spreadsheets/d/1NWFZBmooPlRMOTqMLVMhCSPWVGKkpfJc/edit?usp=sharing&ouid=110142004031170661916&rtpof=true&sd=true)",
    unsafe_allow_html=True
)
# --- Load data skripsi ---
df = pd.read_excel("database/Skripsi Genap 24-25.xlsx", sheet_name=0)

df.drop(index=[0, 1, 2], inplace=True)
df.reset_index(drop=True, inplace=True)

# --- Tentukan kolom tetap (data utama) dan kolom dosen (centang 'v') ---
data_cols = ["ANGKATAN", "NAMA MAHASISWA", "KOMPARTEMEN", "TOPIK", "OBJEK"]
kolom_dosen = [col for col in df.columns if col not in data_cols and df[col].isin(["v", "V", "✓", "✔"]).any()]

# --- Salin data dan ekstrak pembimbing ---
df_plot = df[data_cols + kolom_dosen].copy()

def ambil_dosen(row):
    return [dosen for dosen in kolom_dosen if str(row[dosen]).strip().lower() == 'v']

df_plot["Dosen Pembimbing"] = df_plot.apply(ambil_dosen, axis=1)

# --- Buat tab ---
tab1, tab2, tab3 = st.tabs(["REKAP JUMLAH PLOTTING", "DATA MAHASISWA", "PLOTTING DOSEN"])

with tab1:
    st.subheader("Grafik Jumlah Mahasiswa per Dosen")
    df_dosen = df_plot[["NAMA MAHASISWA", "Dosen Pembimbing"]].explode("Dosen Pembimbing")
    dosen_counts = df_dosen["Dosen Pembimbing"].value_counts().reset_index()
    dosen_counts.columns = ["Dosen", "Jumlah Mahasiswa"]

    fig = px.bar(
        dosen_counts.sort_values(by="Jumlah Mahasiswa"),
        x="Jumlah Mahasiswa",
        y="Dosen",
        orientation="h",
        color="Jumlah Mahasiswa",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Data Mahasiswa & Pembimbing")
    st.dataframe(
        df_plot[["NAMA MAHASISWA", "TOPIK", "OBJEK", "Dosen Pembimbing"]],
        use_container_width=True
    )

df_dosen_map = pd.read_excel("database/Skripsi Genap 24-25.xlsx", sheet_name="DAFTAR DOSEN", usecols="A:B")
kode_to_nama = dict(zip(df_dosen_map["Kode Dosen"], df_dosen_map["Nama Dosen"]))
with tab3:
    st.subheader("Daftar Mahasiswa Per Dosen")

    # explode data
    df_exploded = df_plot[["NAMA MAHASISWA", "TOPIK", "OBJEK", "Dosen Pembimbing"]].explode("Dosen Pembimbing")

    for kode_dosen in sorted(df_exploded["Dosen Pembimbing"].dropna().unique()):
        nama_lengkap = kode_to_nama.get(kode_dosen, kode_dosen)
        with st.expander(f"{nama_lengkap} ({kode_dosen})", expanded=False):
            df_per_dosen = df_exploded[df_exploded["Dosen Pembimbing"] == kode_dosen]
            st.dataframe(df_per_dosen[["NAMA MAHASISWA", "TOPIK", "OBJEK"]], use_container_width=True)
