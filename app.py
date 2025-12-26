import streamlit as st # type: ignore
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import os

st.set_page_config(
    page_title="Sistem Perpustakaan SMAN 47 Jakarta",
    layout="wide"
)

DB_PATH = "perpustakaan_final.db"

# ===============================
# DATABASE
# ===============================
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# ===============================
# LOGIN
# ===============================
def login_page():
    st.title("🏫 Sistem Perpustakaan SMAN 47 Jakarta")
    st.subheader("Login Admin")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT id_user, username FROM user WHERE username=? AND password=?",
            (username, password)
        )
        data = cur.fetchone()
        conn.close()

        if data:
            st.session_state.login = True
            st.session_state.admin_id = data[0]
            st.session_state.admin_username = data[1]
            st.success("Login berhasil")
            st.rerun()
        else:
            st.error("Username atau password salah")

# ===============================
# INPUT PEMINJAMAN
# ===============================
def input_peminjaman():
    st.header("📖 Input Peminjaman Buku")

    nama_siswa = st.text_input("Nama Siswa")
    kelas = st.text_input("Kelas (contoh: 11 IPA 1)")
    kode_buku = st.text_input("Kode Buku")

    conn = get_conn()
    cur = conn.cursor()

    buku = None
    if kode_buku:
        cur.execute(
            "SELECT id_buku, nama_buku FROM buku WHERE kode_buku=?",
            (kode_buku,)
        )
        buku = cur.fetchone()
        if buku:
            st.success(f"Buku ditemukan: {buku[1]}")
        else:
            st.warning("Buku tidak ditemukan")

    tanggal_pinjam = st.date_input("Tanggal Pinjam", datetime.now())
    tanggal_kembali = tanggal_pinjam + timedelta(days=3)
    st.info(f"Tanggal Pengembalian: {tanggal_kembali}")

    if st.button("Simpan Peminjaman"):
        if not (nama_siswa and kelas and buku):
            st.error("Data belum lengkap")
            conn.close()
            return

        # Kelas
        cur.execute("SELECT id_kelas FROM kelas WHERE nama_kelas=?", (kelas,))
        row = cur.fetchone()
        if row:
            id_kelas = row[0]
        else:
            cur.execute("INSERT INTO kelas (nama_kelas) VALUES (?)", (kelas,))
            id_kelas = cur.lastrowid

        # Siswa
        cur.execute(
            "SELECT id_siswa FROM siswa WHERE nama_siswa=? AND id_kelas=?",
            (nama_siswa, id_kelas)
        )
        row = cur.fetchone()
        if row:
            id_siswa = row[0]
        else:
            cur.execute(
                "INSERT INTO siswa (nama_siswa, id_kelas) VALUES (?, ?)",
                (nama_siswa, id_kelas)
            )
            id_siswa = cur.lastrowid

        # Peminjaman
        cur.execute(
            """
            INSERT INTO peminjaman
            (id_siswa, id_buku, tanggal_pinjam, tanggal_kembali, status, id_admin)
            VALUES (?, ?, ?, ?, 'dipinjam', ?)
            """,
            (
                id_siswa,
                buku[0],
                tanggal_pinjam.strftime("%Y-%m-%d"),
                tanggal_kembali.strftime("%Y-%m-%d"),
                st.session_state.admin_id
            )
        )

        conn.commit()
        conn.close()
        st.success("Peminjaman berhasil disimpan")

# ===============================
# LIHAT PEMINJAMAN
# ===============================
def lihat_peminjaman():
    st.header("📋 Data Peminjaman")

    conn = get_conn()
    df = pd.read_sql(
        """
        SELECT p.id_peminjaman, s.nama_siswa, b.nama_buku,
               p.tanggal_pinjam, p.tanggal_kembali, p.status
        FROM peminjaman p
        JOIN siswa s ON p.id_siswa = s.id_siswa
        JOIN buku b ON p.id_buku = b.id_buku
        ORDER BY p.id_peminjaman DESC
        """,
        conn
    )
    conn.close()
    st.dataframe(df, use_container_width=True)

# ===============================
# PENGEMBALIAN
# ===============================
def pengembalian():
    st.header("✅ Pengembalian Buku")

    conn = get_conn()
    df = pd.read_sql(
        """
        SELECT p.id_peminjaman, s.nama_siswa, b.nama_buku
        FROM peminjaman p
        JOIN siswa s ON p.id_siswa = s.id_siswa
        JOIN buku b ON p.id_buku = b.id_buku
        WHERE p.status='dipinjam'
        """,
        conn
    )

    if df.empty:
        st.info("Tidak ada buku yang sedang dipinjam")
        conn.close()
        return

    st.dataframe(df, use_container_width=True)

    id_pinjam = st.selectbox("Pilih ID Peminjaman", df["id_peminjaman"])

    if st.button("Kembalikan Buku"):
        conn.execute(
            """
            UPDATE peminjaman
            SET status='dikembalikan'
            WHERE id_peminjaman=?
            """,
            (id_pinjam,)
        )
        conn.commit()
        conn.close()
        st.success("Buku berhasil dikembalikan")
        st.rerun()

# ===============================
# MAIN
# ===============================
def main():
    if "login" not in st.session_state:
        st.session_state.login = False

    if not st.session_state.login:
        login_page()
        return

    st.sidebar.title("📚 Menu")
    st.sidebar.write(f"Admin: {st.session_state.admin_username}")

    menu = st.sidebar.radio(
        "Navigasi",
        [
            "Input Peminjaman",
            "Lihat Peminjaman",
            "Pengembalian",
            "Logout"
        ]
    )

    if menu == "Input Peminjaman":
        input_peminjaman()
    elif menu == "Lihat Peminjaman":
        lihat_peminjaman()
    elif menu == "Pengembalian":
        pengembalian()
    elif menu == "Logout":
        st.session_state.login = False
        st.rerun()

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        st.error("Database tidak ditemukan")
    else:
        main()
