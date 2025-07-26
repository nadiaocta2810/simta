import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import json

# ---------- LOGIN STATE PERSISTENCE ----------
STATE_FILE = "login_state.json"

def load_login_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("logged_in", False)
    return False

def save_login_state(status: bool):
    with open(STATE_FILE, "w") as f:
        json.dump({"logged_in": status}, f)

# ---------- STREAMLIT CONFIG ----------
st.set_page_config(page_title="Dashboard Sistem Informasi Manajemen Tugas Akhir", layout="wide")

# ---------- INIT LOGIN STATE ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = load_login_state()

# ---------- STYLES ----------
st.markdown("""
    <style>
    div[data-testid="stForm"] {
        background-color: #f9f9f9;
        padding: 2em;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        width: 90%;
        max-width: 500px;
        margin: auto;
    }
    @media (max-width: 480px) {
        div[data-testid="stForm"] {
            padding: 1em;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ---------- LOGIN FORM ----------
def login():
    show_logos_centered()
    st.markdown("<h2 style='text-align:center; color:#005691;'>LOGIN SIM-TA</h2>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Masukkan username")
        password = st.text_input("Password", type="password", placeholder="Masukkan password")
        submit = st.form_submit_button("Login")

        if submit:
            if username == "admin" and password == "admin":
                st.session_state.logged_in = True
                save_login_state(True)
                st.success("Berhasil login!")
                st.experimental_rerun()
            else:
                st.error("Username atau password salah!")

# ---------- LOGO CENTER ----------
def show_logos_centered():
    with st.container():
        spacer1, logos, spacer2 = st.columns([1.5, 1, 1.5])
        with logos:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image("asset/logoti.png", width=40)
            with col2:
                st.image("asset/logoub.png", width=60)
            with col3:
                st.image("asset/logodampak.png", width=60)

# ---------- HIDE SIDEBAR WHEN LOGOUT ----------
def hide_sidebar():
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            [data-testid="stSidebarNav"] {
                display: none;
            }
            [data-testid="collapsedControl"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

# ---------- LOAD DATA ----------
def load_data():
    tahun = ['2019', '2020', '2021']
    jumlah_lulus = [90, 115, 125]
    total_mhs = [177, 155, 164]
    persentase = [round((l/t)*100, 2) for l, t in zip(jumlah_lulus, total_mhs)]
    return pd.DataFrame({
        'Tahun': tahun,
        'Lulus': jumlah_lulus,
        'Total': total_mhs,
        'Persentase': persentase
    })

# ---------- LOGO AT TOP DASHBOARD ----------
def logo_dashboard():
    col1, col2, col3 = st.columns([8, 1, 2.5])
    with col1:
        st.markdown("<h1 style='color:#005691'>Dashboard SIM-TA</h1>", unsafe_allow_html=True)
    with col3:
        subcol1, subcol2, subcol3 = st.columns(3)
        with subcol1:
            st.image("asset/logoti.png", width=35)
        with subcol2:
            st.image("asset/logoub.png", width=50)
        with subcol3:
            st.image("asset/logodampak.png", width=50)

# ---------- MAIN DASHBOARD ----------
def dashboard():
    logo_dashboard()

    with st.sidebar:
        if st.button("Logout"):
            st.session_state.logged_in = False
            save_login_state(False)
            st.success("Berhasil logout.")
            st.experimental_rerun()

    df = load_data()
    df["Tahun"] = df["Tahun"].astype(str)

    # ---------- TABEL ----------
    data = {
        "Angkatan": [2019, 2020, 2021],
        "Jumlah Total Mahasiswa": [177, 155, 164],
        "Ganjil 22/23": [1, None, None],
        "Genap 22/23": [89, None, None],
        "Ganjil 23/24": [None, 11, None],
        "Genap 23/24": [None, 104, None],
        "Ganjil 24/25": [None, None, 11],
        "Genap 24/25": [None, None, 114],
        "% KTW (≤ 4 Tahun)": ["51%", "75%", "76%"]
    }
    df_tabel = pd.DataFrame(data)
    for col in df_tabel.columns[1:-1]:
        df_tabel[col] = df_tabel[col].apply(lambda x: f"{int(x)}" if pd.notna(x) else "-")

    st.subheader("Tabel Kelulusan Tepat Waktu Mahasiswa")
    st.table(df_tabel)

    # ---------- GRAFIK ----------
    fig = go.Figure(data=[
        go.Bar(
            x=df["Tahun"],
            y=df["Lulus"],
            text=[f"{p}%" for p in df["Persentase"]],
            textposition="auto",
            marker_color="#005691"
        )
    ])
    fig.update_layout(
        title="Jumlah Mahasiswa Lulus per Angkatan",
        xaxis_title="Angkatan",
        yaxis_title="Jumlah Lulus",
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#f9f9f9",
        height=400
    )
    fig.update_xaxes(type='category')
    st.subheader("Grafik Kelulusan Mahasiswa")
    st.plotly_chart(fig, use_container_width=True)

# ---------- MAIN ----------
if not st.session_state.logged_in:
    hide_sidebar()
    login()
else:
    dashboard()