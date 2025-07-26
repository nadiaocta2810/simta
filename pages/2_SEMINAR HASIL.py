import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
# from auth import protect_page, logout_button

# protect_page()  # Wajib untuk ngecek login
# logout_button() # Optional, munculkan tombol logout

def logo_dashboard():
    col1, col2, col3 = st.columns([8.5, 0.5, 2.5])
    with col1:
        st.markdown("<h1 style='color:#005691'>Data Seminar Hasil</h1>", unsafe_allow_html=True)
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
    "[Raw Data Seminar Hasil dapat diakses di sini](https://docs.google.com/spreadsheets/d/1kbE5OxKPfMRnIVrfbc4C74r_XlZ0AMcC/edit?usp=sharing&ouid=110142004031170661916&rtpof=true&sd=true)",
    unsafe_allow_html=True
)

# Koneksi ke database
engine = create_engine("sqlite:///database/data_mahasiswa2.db")

# Fungsi untuk ambil nama-nama tabel (sheet)
def get_table_names():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        return [row[0] for row in result]

# Fungsi untuk load data dari setiap tabel
@st.cache_data
def load_table(table_name):
    df = pd.read_sql_table(table_name, con=engine)
    return df

# Buat tab berdasarkan nama tabel
table_names = get_table_names()
nama_tabel = ['Calon SEMHAS Genap 24/25', 'Calon SEMHAS Ganjil 24/25',
        'Calon SEMHAS Genap 23/24', 'Calon SEMHAS Ganjil 23/24',
         'Calon SEMHAS Genap 22/23', 'Calon SEMHAS Ganjil 22/23'
        ]


tabs = st.tabs([name.upper() for name in nama_tabel])

for tab, name, nama in zip(tabs, table_names, nama_tabel):
    with tab:
        st.subheader(f"Data Mahasiswa {nama.upper()}")
        df = load_table(name)
        df = df.reset_index(drop=True)  # Reset index agar rapi
        df.insert(0, "No", range(1, len(df) + 1))  # Tambahkan kolom nomor urut
        st.dataframe(df, use_container_width=True, hide_index=True)





