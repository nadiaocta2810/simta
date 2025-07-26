import streamlit as st
import pandas as pd

# Konfigurasi halaman
st.set_page_config(page_title="Data Ujian Sarjana", layout="wide")
def logo_dashboard():
    col1, col2, col3 = st.columns([8.5, 0.5, 2.5])
    with col1:
        st.markdown("<h1 style='color:#005691'>Data Ujian Sarjana</h1>", unsafe_allow_html=True)
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
    "[Raw Data Ujian Sarjana dapat diakses di sini](https://docs.google.com/spreadsheets/d/1FF0d1s4MVRf7L2VSRtuL27cIaeuME1_0/edit?usp=sharing&ouid=110142004031170661916&rtpof=true&sd=true)",
    unsafe_allow_html=True
)
# Load file Excel
try:
    df_raw = pd.read_excel("database/Rekap peserta Kompre.xlsx", sheet_name="Kompre 20242025", header=2)
    df_raw["NIM"] = df_raw["NIM"].astype(str)
except FileNotFoundError:
    st.error("❌ File tidak ditemukan.")
    st.stop()
except Exception as e:
    st.error(f"❌ Gagal membaca file: {e}")
    st.stop()

# Normalisasi kolom
df_raw.columns = [str(col).strip().upper().replace("\n", " ") for col in df_raw.columns]

# Rename kolom agar mudah diakses
df_raw.rename(columns={
    "NAMA": "Nama Mahasiswa",
    "NIM": "NIM",
    "JUDUL SKRIPSI": "Judul",
    "DOSEN PEMBIMBING SKRIPSI": "Pembimbing",
    "DOSEN PEMBIMBING AKADEMIK": "Akademik",
    "PENGUJI": "Penguji",
    "UNNAMED: 5": "Pembimbing 2"  # 👉 rename kolom di sini
}, inplace=True)

# Hapus kolom Judul jika ada
if "Judul" in df_raw.columns:
    df_raw = df_raw.drop(columns=["Judul"])

# Potong kolom sampai "Penguji"
if "Penguji" in df_raw.columns:
    idx_peng = df_raw.columns.get_loc("Penguji")
    df_raw = df_raw.iloc[:, :idx_peng + 1]

# Reset index
df_raw = df_raw.reset_index(drop=True)

# Temukan semua baris yang mengandung "Majelis"
majelis_rows = df_raw[df_raw["Nama Mahasiswa"].astype(str).str.upper().str.contains("MAJELIS", na=False)].index.tolist()

# Ambil 3 baris setelah setiap majelis
majelis_groups = {}
for i, idx in enumerate(majelis_rows):
    label = df_raw.at[idx, "Nama Mahasiswa"].strip().title()
    start = idx + 1
    end = start + 3
    group_df = df_raw.iloc[start:end].dropna(subset=["Nama Mahasiswa", "NIM"], how="all")
    
    # Bikin label unik agar urutannya tetap sesuai Excel
    label_unik = f"{label} - Grup ke-{i+1}"
    majelis_groups[label_unik] = group_df

# Gabungkan semua data
gabungan_df = pd.concat(majelis_groups.values(), ignore_index=True)

# Tampilkan ekspander untuk setiap grup majelis
st.markdown("### Daftar Mahasiswa per Majelis")
for label_majelis, df_majelis in majelis_groups.items():
    with st.expander(f"{label_majelis}", expanded=False):
        st.dataframe(df_majelis.reset_index(drop=True), use_container_width=True,hide_index=True)
