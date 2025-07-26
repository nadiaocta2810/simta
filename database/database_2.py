import pandas as pd
import re
from sqlalchemy import create_engine
from datetime import datetime
import locale

# Fungsi membersihkan nama tabel (tanpa spasi, simbol)
def clean_sheet_name(name):
    name = name.strip().lower()
    name = re.sub(r'\s+', '_', name)  # Ganti spasi jadi underscore
    name = re.sub(r'[^\w_]', '', name)  # Hapus karakter aneh
    return name

# Set locale Indonesia (menyesuaikan OS)
try:
    locale.setlocale(locale.LC_TIME, 'id_ID.utf8')  # Linux/macOS
except:
    try:
        locale.setlocale(locale.LC_TIME, 'ind')  # Windows
    except:
        locale.setlocale(locale.LC_TIME, '')  # fallback default

# 🔧 Format tanggal
def format_tanggal(tgl):
    try:
        if pd.isna(tgl):
            return ""
        tgl = pd.to_datetime(tgl, errors="coerce")
        if pd.isna(tgl):
            return ""
        return tgl.strftime("%A, %d %B %Y")
    except:
        return str(tgl)


# 🔧 Format jam
def format_jam(jam):
    try:
        if pd.isna(jam):
            return ""
        if isinstance(jam, str):
            jam = pd.to_datetime(jam, errors="coerce")
        return jam.strftime("%H.%M") + " WIB"
    except:
        return str(jam)


# Fungsi untuk mendeteksi header secara otomatis (berdasarkan kolom 'No')
def detect_and_read_sheet(path_file, sheet_name):
    df_raw = pd.read_excel(path_file, sheet_name=sheet_name, header=None)

    # Cari baris header yang mengandung 'No'
    header_row = None
    for i, row in df_raw.iterrows():
        if row.astype(str).str.contains(r'\bno\b', case=False, na=False).any():
            header_row = i
            break

    if header_row is None:
        raise ValueError(f"❌ Tidak ditemukan header 'No' di sheet '{sheet_name}'")

    # Baca ulang dengan header yang benar
    df = pd.read_excel(path_file, sheet_name=sheet_name, header=header_row)

    # Normalisasi nama kolom
    df.columns = [str(col).strip() for col in df.columns]

    # Hapus kolom "No" asli jika ada
    for col in df.columns:
        if col.strip().lower() == "no":
            df.drop(columns=[col], inplace=True)
            break

    # Hapus kolom Unnamed
    df = df.loc[:, ~df.columns.str.contains("Unnamed", case=False, na=False)]

    # Hapus baris tanpa NIM
    for col in df.columns:
        if col.lower() == "nim":
            df = df[df[col].notna()]
            df = df[~df[col].astype(str).str.strip().eq("")]
            break

    # Tambah kolom "No" baru dari 1
    df.insert(0, "No", range(1, len(df) + 1))

    # for col in df.columns:
    #     col_lower = col.lower()
    #     if "tanggal" in col_lower:
    #         print(f"📅 Memformat kolom TANGGAL: {col}")
    #         df[col] = df[col].apply(format_tanggal)
    #     if "jam" in col_lower:
    #         print(f"🕒 Memformat kolom JAM: {col}")
    #         df[col] = df[col].apply(format_jam)


    # # # Format tanggal dan jam
    # # for col in df.columns:
    # #     col_lower = col.lower()
    # #     if "tanggal" in col_lower:
    # #         df[col] = df[col].apply(format_tanggal)
    # #     if "jam" in col_lower:
    # #         df[col] = df[col].apply(format_jam)

    return df

# 🔗 Koneksi ke database SQLite
engine = create_engine("sqlite:///database\data_mahasiswa2.db")

# 📄 File Excel
excel_file = "database\_TAS-16 Daftar Calon Peserta SemHas dan Penguji.xlsx"
xls = pd.ExcelFile(excel_file)

# 🔁 Loop semua sheet
for sheet_name in xls.sheet_names:
    print(f"📥 Memproses sheet: {sheet_name}")
    try:
        # Deteksi dan ambil data dari baris header yang benar
        df = detect_and_read_sheet(excel_file, sheet_name)

        # 💡 Bersihkan baris kosong
        df.dropna(how='all', inplace=True)

        # 💡 Bersihkan kolom jika ada
        for col in df.columns:
            if "nim" in col.lower():
                df[col] = df[col].astype(str).str.replace(",", "").str.strip()
            if "nama" in col.lower():
                df[col] = df[col].astype(str).str.title().str.strip()

        # 🧼 Hapus kolom 'index' atau 'no' (jika mau disusun ulang nanti)
        for unwanted in ["No"]:
            if unwanted in df.columns:
                df.drop(columns=[unwanted], inplace=True)
                print(f"   🧹 Menghapus kolom '{unwanted}'")

        # 🏷️ Buat nama tabel SQL dari nama sheet
        table_name = clean_sheet_name(sheet_name)

        # 🗃️ Simpan ke database
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"✅ Tabel '{table_name}' berhasil disimpan ({len(df)} baris).")

    except Exception as e:
        print(f"⚠️ Gagal memproses sheet '{sheet_name}': {e}")

print("📦 Semua sheet berhasil dimigrasikan ke database.")
