import pandas as pd
import re
from sqlalchemy import create_engine

# Fungsi membersihkan nama tabel (tanpa spasi, simbol)
def clean_sheet_name(name):
    name = name.strip().lower()
    name = re.sub(r'\s+', '_', name)  # Ganti spasi jadi underscore
    name = re.sub(r'[^\w_]', '', name)  # Hapus karakter aneh
    return name

# Fungsi untuk mendeteksi header secara otomatis (berdasarkan kolom 'No')
def detect_and_read_sheet(path_file, sheet_name):
    df_raw = pd.read_excel(path_file, sheet_name=sheet_name, header=None)

    # Deteksi baris yang mengandung 'No' sebagai header
    header_row = None
    for i, row in df_raw.iterrows():
        if row.astype(str).str.contains(r'\bno\b', case=False, na=False).any():
            header_row = i
            break

    if header_row is None:
        raise ValueError(f"❌ Tidak ditemukan header 'No' di sheet '{sheet_name}'")

    # Baca ulang dengan header yang benar
    df = pd.read_excel(path_file, sheet_name=sheet_name, header=header_row)

    # 🔍 Normalisasi nama kolom (untuk deteksi kolom 'nim')
    df.columns = [col.strip().lower() for col in df.columns]

    # 🚫 Hapus baris yang kolom 'nim'-nya kosong
    if "nim" in df.columns:
        df.dropna(subset=["nim"], inplace=True)
        # (Opsional) juga hapus yang kosong secara visual
        df = df[~df["nim"].astype(str).str.strip().eq("")]

    return df

# 🔗 Koneksi ke database SQLite
engine = create_engine("sqlite:///database\data_mahasiswa4.db")

# 📄 File Excel
excel_file = "database\Skripsi Genap 24-25.xlsx"
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
        for unwanted in ["index"]:
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
