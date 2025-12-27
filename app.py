import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import os
from typing import Optional, Dict, List
import base64

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(
    page_title="Sistem Perpustakaan SMAN 47 Jakarta",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CSS CUSTOM (Mirip Tkinter)
# =====================================================
st.markdown("""
<style>
    /* Header Style */
    .main-header {
        background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Card Style */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 60px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
        background-color: rgba(255, 255, 255, 0.95) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e88e5 0%, #1565c0 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 15px;
        background-color: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* DataFrame */
    .dataframe {
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* Form Container - Background Putih Semi Transparan */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 20px;
        border-radius: 10px;
    }
    
    /* Text Input Background */
    input[type="text"], input[type="password"], input[type="date"], 
    textarea, select {
        background-color: rgba(255, 255, 255, 0.98) !important;
    }
    
    /* Expander Background */
    div[data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# HELPER UNTUK GAMBAR
# =====================================================
def get_base64_image(image_path):
    """Convert image to base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def set_background_image(image_path, opacity=0.15):
    """Set background image halaman login"""
    base64_img = get_base64_image(image_path)
    if base64_img:
        st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(255,255,255,{opacity}), rgba(255,255,255,{opacity})),
                        url("data:image/png;base64,{base64_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)

# =====================================================
# KONFIGURASI DATABASE
# =====================================================
DB_PATH = "perpustakaan_final.db"

# =====================================================
# LAYER 1: DATABASE CONNECTION & MODELS
# =====================================================
class DatabaseConnection:
    """Singleton Database Connection"""
    _instance = None
    
    @classmethod
    def get_connection(cls):
        return sqlite3.connect(DB_PATH, check_same_thread=False)

class BaseModel:
    """Base Model untuk semua entitas"""
    
    @staticmethod
    def execute_query(query: str, params: tuple = (), fetch_one: bool = False):
        conn = DatabaseConnection.get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        
        if query.strip().upper().startswith("SELECT"):
            return cur.fetchone() if fetch_one else cur.fetchall()
        else:
            conn.commit()
            return cur.lastrowid

class UserModel(BaseModel):
    """Model untuk User/Admin"""
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict]:
        result = BaseModel.execute_query(
            "SELECT id_user, username FROM user WHERE username = ? AND password = ?",
            (username, password),
            fetch_one=True
        )
        if result:
            return {"id": result[0], "username": result[1]}
        return None

class KelasModel(BaseModel):
    """Model untuk Kelas"""
    
    @staticmethod
    def get_all() -> List[Dict]:
        results = BaseModel.execute_query(
            "SELECT id_kelas, nama_kelas FROM kelas ORDER BY id_kelas"
        )
        return [{"id": r[0], "nama": r[1]} for r in results]
    
    @staticmethod
    def get_or_create(nama_kelas: str) -> str:
        result = BaseModel.execute_query(
            "SELECT id_kelas FROM kelas WHERE nama_kelas = ?",
            (nama_kelas,),
            fetch_one=True
        )
        if result:
            return result[0]
        else:
            return BaseModel.execute_query(
                "INSERT INTO kelas (nama_kelas) VALUES (?)",
                (nama_kelas,)
            )
    
    @staticmethod
    def create(id_kelas: str, nama_kelas: str) -> int:
        return BaseModel.execute_query(
            "INSERT INTO kelas (id_kelas, nama_kelas) VALUES (?, ?)",
            (id_kelas, nama_kelas)
        )
    
    @staticmethod
    def delete(id_kelas: str) -> bool:
        BaseModel.execute_query(
            "DELETE FROM kelas WHERE id_kelas = ?",
            (id_kelas,)
        )
        return True

class SiswaModel(BaseModel):
    """Model untuk Siswa"""
    
    @staticmethod
    def get_all() -> pd.DataFrame:
        conn = DatabaseConnection.get_connection()
        df = pd.read_sql("""
            SELECT s.id_siswa, s.nama_siswa, k.nama_kelas
            FROM siswa s
            LEFT JOIN kelas k ON s.id_kelas = k.id_kelas
            ORDER BY s.id_siswa
        """, conn)
        return df
    
    @staticmethod
    def search(keyword: str) -> pd.DataFrame:
        conn = DatabaseConnection.get_connection()
        df = pd.read_sql("""
            SELECT s.id_siswa, s.nama_siswa, k.nama_kelas
            FROM siswa s
            LEFT JOIN kelas k ON s.id_kelas = k.id_kelas
            WHERE s.nama_siswa LIKE ?
        """, conn, params=(f"%{keyword}%",))
        return df
    
    @staticmethod
    def get_or_create(nama_siswa: str, id_kelas: str) -> int:
        result = BaseModel.execute_query(
            "SELECT id_siswa FROM siswa WHERE nama_siswa = ? AND id_kelas = ?",
            (nama_siswa, id_kelas),
            fetch_one=True
        )
        if result:
            return result[0]
        else:
            return BaseModel.execute_query(
                "INSERT INTO siswa (nama_siswa, id_kelas) VALUES (?, ?)",
                (nama_siswa, id_kelas)
            )
    
    @staticmethod
    def create(nama_siswa: str, id_kelas: str) -> int:
        return BaseModel.execute_query(
            "INSERT INTO siswa (nama_siswa, id_kelas) VALUES (?, ?)",
            (nama_siswa, id_kelas)
        )
    
    @staticmethod
    def delete(id_siswa: int) -> bool:
        BaseModel.execute_query(
            "DELETE FROM siswa WHERE id_siswa = ?",
            (id_siswa,)
        )
        return True

class BukuModel(BaseModel):
    """Model untuk Buku"""
    
    @staticmethod
    def get_all() -> pd.DataFrame:
        conn = DatabaseConnection.get_connection()
        df = pd.read_sql(
            "SELECT id_buku, kode_buku, nama_buku FROM buku ORDER BY id_buku",
            conn
        )
        return df
    
    @staticmethod
    def get_by_kode(kode_buku: str) -> Optional[Dict]:
        result = BaseModel.execute_query(
            "SELECT id_buku, kode_buku, nama_buku FROM buku WHERE kode_buku = ?",
            (kode_buku,),
            fetch_one=True
        )
        if result:
            return {"id": result[0], "kode": result[1], "nama": result[2]}
        return None
    
    @staticmethod
    def search(keyword: str) -> pd.DataFrame:
        conn = DatabaseConnection.get_connection()
        df = pd.read_sql("""
            SELECT id_buku, kode_buku, nama_buku 
            FROM buku 
            WHERE nama_buku LIKE ? OR kode_buku LIKE ?
        """, conn, params=(f"%{keyword}%", f"%{keyword}%"))
        return df
    
    @staticmethod
    def get_or_create(kode_buku: str, nama_buku: str) -> int:
        result = BaseModel.execute_query(
            "SELECT id_buku FROM buku WHERE kode_buku = ?",
            (kode_buku,),
            fetch_one=True
        )
        if result:
            BaseModel.execute_query(
                "UPDATE buku SET nama_buku = ? WHERE id_buku = ?",
                (nama_buku, result[0])
            )
            return result[0]
        else:
            return BaseModel.execute_query(
                "INSERT INTO buku (kode_buku, nama_buku) VALUES (?, ?)",
                (kode_buku, nama_buku)
            )
    
    @staticmethod
    def create(kode_buku: str, nama_buku: str) -> int:
        return BaseModel.execute_query(
            "INSERT INTO buku (kode_buku, nama_buku) VALUES (?, ?)",
            (kode_buku, nama_buku)
        )
    
    @staticmethod
    def delete(kode_buku: str) -> bool:
        BaseModel.execute_query(
            "DELETE FROM buku WHERE kode_buku = ?",
            (kode_buku,)
        )
        return True

class PeminjamanModel(BaseModel):
    """Model untuk Peminjaman"""
    
    @staticmethod
    def get_all(status_filter: str = "ALL") -> pd.DataFrame:
        conn = DatabaseConnection.get_connection()
        if status_filter == "ALL":
            df = pd.read_sql("""
                SELECT p.id_peminjaman, s.nama_siswa, b.nama_buku,
                       p.tanggal_pinjam, p.tanggal_kembali, p.status
                FROM peminjaman p
                JOIN siswa s ON p.id_siswa = s.id_siswa
                JOIN buku b ON p.id_buku = b.id_buku
                ORDER BY p.id_peminjaman DESC
            """, conn)
        else:
            df = pd.read_sql("""
                SELECT p.id_peminjaman, s.nama_siswa, b.nama_buku,
                       p.tanggal_pinjam, p.tanggal_kembali, p.status
                FROM peminjaman p
                JOIN siswa s ON p.id_siswa = s.id_siswa
                JOIN buku b ON p.id_buku = b.id_buku
                WHERE p.status = ?
                ORDER BY p.id_peminjaman DESC
            """, conn, params=(status_filter,))
        return df
    
    @staticmethod
    def get_active_loans() -> pd.DataFrame:
        conn = DatabaseConnection.get_connection()
        df = pd.read_sql("""
            SELECT p.id_peminjaman, s.nama_siswa, b.nama_buku, b.kode_buku, p.tanggal_pinjam
            FROM peminjaman p
            JOIN siswa s ON p.id_siswa = s.id_siswa
            JOIN buku b ON p.id_buku = b.id_buku
            WHERE p.status = 'dipinjam'
            ORDER BY p.id_peminjaman DESC
        """, conn)
        return df
    
    @staticmethod
    def create(id_siswa: int, id_buku: int, tanggal_pinjam: str, admin_id: int) -> int:
        return BaseModel.execute_query("""
            INSERT INTO peminjaman (id_siswa, id_buku, tanggal_pinjam, status, id_admin)
            VALUES (?, ?, ?, 'dipinjam', ?)
        """, (id_siswa, id_buku, tanggal_pinjam, admin_id))
    
    @staticmethod
    def return_book(id_peminjaman: int) -> bool:
        BaseModel.execute_query("""
            UPDATE peminjaman 
            SET tanggal_kembali = ?, status = 'dikembalikan' 
            WHERE id_peminjaman = ?
        """, (datetime.now().strftime("%Y-%m-%d"), id_peminjaman))
        return True

# =====================================================
# LAYER 2: AUTHENTICATION SERVICE
# =====================================================
class AuthService:
    """Service untuk autentikasi"""
    
    @staticmethod
    def login(username: str, password: str) -> bool:
        user = UserModel.authenticate(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.admin_id = user["id"]
            st.session_state.admin_username = user["username"]
            return True
        return False
    
    @staticmethod
    def logout():
        st.session_state.logged_in = False
        st.session_state.admin_id = None
        st.session_state.admin_username = None
    
    @staticmethod
    def is_authenticated() -> bool:
        return st.session_state.get("logged_in", False)

# =====================================================
# LAYER 3: VIEW COMPONENTS
# =====================================================

def show_header():
    """Header dengan background gambar SMAN 47"""
    
    # Set background image untuk halaman setelah login
    if os.path.exists("sman47.jpeg"):
        set_background_image("sman47.jpeg", opacity=0.85)
    
    # Header tanpa banner gambar (karena udah jadi background)
    st.markdown(f"""
    <div class="main-header" style="padding: 15px;">
        <h2 style="margin: 0;">🏫 SISTEM PERPUSTAKAAN SMAN 47 JAKARTA</h2>
        <p style="margin: 5px 0 0 0; font-size: 14px;">Admin: {st.session_state.get('admin_username', 'Unknown')}</p>
    </div>
    """, unsafe_allow_html=True)

def login_page():
    """Halaman Login dengan Background Library"""
    
    # Background gambar library digital
    if os.path.exists("logo1.jpeg"):
        set_background_image("logo1.jpeg", opacity=0.15)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Header login (sejajar dengan form)
        st.markdown("""
        <div class="main-header" style="padding: 15px; margin-bottom: 30px;">
            <h2 style="margin: 0;">SMAN 47 JAKARTA</h2>
            <p style="margin: 5px 0 0 0; font-size: 16px;">Sistem Perpustakaan</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### LOGIN ADMIN")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submit = st.form_submit_button("LOGIN", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Username dan password harus diisi!")
                elif AuthService.login(username, password):
                    st.success("✅ Login berhasil! Mengalihkan...")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah!")
        
        st.markdown("---")
        st.caption("© 2025 SMAN 47 Jakarta - PKM Universitas Pamulang")

def input_peminjaman_page():
    """Halaman Input Peminjaman"""
    show_header()
    st.markdown("## 📖 INPUT PEMINJAMAN BUKU")
    
    # JavaScript untuk auto-update tanggal pengembalian
    st.markdown("""
    <script>
    // Auto-calculate return date (3 days after loan date)
    function updateReturnDate() {
        const loanDateInput = document.querySelector('input[type="date"]');
        if (loanDateInput && loanDateInput.value) {
            const loanDate = new Date(loanDateInput.value);
            loanDate.setDate(loanDate.getDate() + 3);
            
            const year = loanDate.getFullYear();
            const month = String(loanDate.getMonth() + 1).padStart(2, '0');
            const day = String(loanDate.getDate()).padStart(2, '0');
            
            return `${year}-${month}-${day}`;
        }
        return null;
    }
    
    // Listen for date changes
    setTimeout(() => {
        const loanDateInput = document.querySelector('input[type="date"]');
        if (loanDateInput) {
            loanDateInput.addEventListener('change', updateReturnDate);
        }
    }, 1000);
    </script>
    """, unsafe_allow_html=True)
    
    with st.form("form_peminjaman"):
        col1, col2 = st.columns(2)
        
        with col1:
            nama_siswa = st.text_input("👤 Nama Siswa", placeholder="Masukkan nama siswa")
            kelas = st.text_input("📚 Kelas", placeholder="Contoh: 11 IPA 1")
            
        with col2:
            kode_buku = st.text_input("🔍 Kode Buku", placeholder="Masukkan kode buku")
            tanggal_pinjam = st.date_input("📅 Tanggal Pinjam", datetime.now())
        
        # Info buku
        if kode_buku:
            buku = BukuModel.get_by_kode(kode_buku)
            if buku:
                st.success(f"✅ Buku ditemukan: **{buku['nama']}**")
            else:
                st.warning("⚠️ Buku tidak ditemukan")
        
        # Tanggal kembali otomatis (REAL-TIME UPDATE)
        tanggal_kembali = tanggal_pinjam + timedelta(days=3)
        
        # Tampilkan dengan highlight
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                    padding: 15px; border-radius: 10px; border-left: 4px solid #2196f3;
                    margin: 10px 0;">
            <p style="margin: 0; font-size: 16px; color: #1565c0;">
                📅 <strong>Tanggal Pengembalian :</strong> 
                <span style="font-size: 18px; font-weight: bold; color: #0d47a1;">
                    {tanggal_kembali.strftime('%d-%m-%Y')}
                </span>
                <em style="color: #666; font-size: 14px;"> (3 hari dari tanggal pinjam)</em>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            submit = st.form_submit_button("✅ SIMPAN PEMINJAMAN", use_container_width=True)
        
        if submit:
            if not nama_siswa or not kelas or kelas == "Contoh: 11 IPA 1":
                st.error("❌ Nama siswa dan kelas harus diisi!")
            elif not kode_buku:
                st.error("❌ Kode buku harus diisi!")
            else:
                buku = BukuModel.get_by_kode(kode_buku)
                if not buku:
                    st.error("❌ Buku tidak ditemukan!")
                else:
                    try:
                        # Get or create kelas
                        id_kelas = KelasModel.get_or_create(kelas)
                        
                        # Get or create siswa
                        id_siswa = SiswaModel.get_or_create(nama_siswa, id_kelas)
                        
                        # Get or create buku
                        id_buku = BukuModel.get_or_create(kode_buku, buku['nama'])
                        
                        # Create peminjaman
                        id_peminjaman = PeminjamanModel.create(
                            id_siswa, id_buku, 
                            tanggal_pinjam.strftime("%Y-%m-%d"),
                            st.session_state.admin_id
                        )
                        
                        st.success(f"✅ Peminjaman berhasil! **ID: {id_peminjaman}**")
                        st.balloons()
                        
                        # Show receipt
                        st.markdown("---")
                        st.markdown("### 🧾 RECEIPT PEMINJAMAN BUKU")
                        
                        receipt_col1, receipt_col2 = st.columns(2)
                        
                        with receipt_col1:
                            st.markdown(f"""
                            **INFORMASI PEMINJAMAN**
                            - No. Peminjaman: `{id_peminjaman}`
                            - Tanggal Pinjam: `{tanggal_pinjam.strftime("%d-%m-%Y")}`
                            - Tanggal Kembali: `{tanggal_kembali.strftime("%d-%m-%Y")}`
                            - Admin: `{st.session_state.admin_username}`
                            """)
                        
                        with receipt_col2:
                            st.markdown(f"""
                            **DATA SISWA**
                            - Nama: `{nama_siswa}`
                            - Kelas: `{kelas}`
                            
                            **DATA BUKU**
                            - Kode: `{kode_buku}`
                            - Nama: `{buku['nama']}`
                            """)
                        
                        st.warning("⚠️ **Harap kembalikan buku tepat waktu!**")
                        
                    except Exception as e:
                        st.error(f"❌ Gagal menyimpan: {e}")

def lihat_peminjaman_page():
    """Halaman Lihat Peminjaman"""
    show_header()
    st.markdown("## DATA PEMINJAMAN")
    
    # Filter buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Semua", use_container_width=True):
            st.session_state.filter_status = "ALL"
    with col2:
        if st.button("🔄 Sedang Dipinjam", use_container_width=True):
            st.session_state.filter_status = "dipinjam"
    with col3:
        if st.button("✅ Sudah Dikembalikan", use_container_width=True):
            st.session_state.filter_status = "dikembalikan"
    
    # Default filter
    if "filter_status" not in st.session_state:
        st.session_state.filter_status = "ALL"
    
    # Load data
    df = PeminjamanModel.get_all(st.session_state.filter_status)
    
    if df.empty:
        st.info("📚 Tidak ada data peminjaman")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

def pengembalian_page():
    """Halaman Pengembalian"""
    show_header()
    st.markdown("## ✅ PENGEMBALIAN BUKU")
    
    df = PeminjamanModel.get_active_loans()
    
    if df.empty:
        st.info("📚 Tidak ada buku yang sedang dipinjam")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        id_peminjaman = st.selectbox(
            "Pilih ID Peminjaman untuk dikembalikan:",
            df["id_peminjaman"].tolist()
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ KEMBALIKAN BUKU", use_container_width=True):
                try:
                    PeminjamanModel.return_book(id_peminjaman)
                    st.success(f"✅ Buku ID {id_peminjaman} berhasil dikembalikan!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal mengembalikan buku: {e}")

def data_siswa_page():
    """Halaman Data Siswa"""
    show_header()
    st.markdown("## DATA SISWA")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Tambah Siswa", use_container_width=True):
            st.session_state.show_add_siswa = True
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col3:
        search_keyword = st.text_input("🔍 Cari siswa", key="search_siswa")
    with col4:
        if st.button("Cari", use_container_width=True):
            pass
    
    # Form tambah siswa
    if st.session_state.get("show_add_siswa", False):
        with st.expander("➕ FORM TAMBAH SISWA BARU", expanded=True):
            with st.form("form_tambah_siswa"):
                nama_siswa = st.text_input("Nama Siswa")
                
                kelas_list = KelasModel.get_all()
                kelas_options = [f"{k['id']} - {k['nama']}" for k in kelas_list]
                kelas_selected = st.selectbox("Pilih Kelas", [""] + kelas_options)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submit = st.form_submit_button("✅ SIMPAN", use_container_width=True)
                with col_b:
                    cancel = st.form_submit_button("❌ BATAL", use_container_width=True)
                
                if submit:
                    if not nama_siswa or not kelas_selected:
                        st.error("Semua field harus diisi!")
                    else:
                        try:
                            id_kelas = kelas_selected.split(" - ")[0]
                            SiswaModel.create(nama_siswa, id_kelas)
                            st.success(f"✅ Siswa '{nama_siswa}' berhasil ditambahkan!")
                            st.session_state.show_add_siswa = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal: {e}")
                
                if cancel:
                    st.session_state.show_add_siswa = False
                    st.rerun()
    
    # Load data
    if search_keyword:
        df = SiswaModel.search(search_keyword)
    else:
        df = SiswaModel.get_all()
    
    if df.empty:
        st.info("Tidak ada data siswa")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

def data_buku_page():
    """Halaman Data Buku"""
    show_header()
    st.markdown("## DATA BUKU")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Tambah Buku", use_container_width=True):
            st.session_state.show_add_buku = True
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col3:
        search_keyword = st.text_input("🔍 Cari buku", key="search_buku")
    with col4:
        if st.button("Cari", use_container_width=True):
            pass
    
    # Form tambah buku
    if st.session_state.get("show_add_buku", False):
        with st.expander("➕ FORM TAMBAH BUKU BARU", expanded=True):
            with st.form("form_tambah_buku"):
                kode_buku = st.text_input("Kode Buku")
                nama_buku = st.text_input("Nama Buku")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submit = st.form_submit_button("✅ SIMPAN", use_container_width=True)
                with col_b:
                    cancel = st.form_submit_button("❌ BATAL", use_container_width=True)
                
                if submit:
                    if not kode_buku or not nama_buku:
                        st.error("Semua field harus diisi!")
                    else:
                        try:
                            BukuModel.create(kode_buku, nama_buku)
                            st.success(f"✅ Buku '{nama_buku}' berhasil ditambahkan!")
                            st.session_state.show_add_buku = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal: {e}")
                
                if cancel:
                    st.session_state.show_add_buku = False
                    st.rerun()
    
    # Load data
    if search_keyword:
        df = BukuModel.search(search_keyword)
    else:
        df = BukuModel.get_all()
    
    if df.empty:
        st.info("Tidak ada data buku")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

# =====================================================
# MAIN APPLICATION
# =====================================================
def main():
    """Main application"""
    
    # Check database
    if not os.path.exists(DB_PATH):
        st.error(f"❌ Database tidak ditemukan: {DB_PATH}")
        st.stop()
    
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    # Check authentication
    if not AuthService.is_authenticated():
        login_page()
        return
    
    # Sidebar menu
    with st.sidebar:
        # Hapus gambar di sidebar, cukup teks aja
        st.markdown("# 📚 MENU")
        st.markdown(f"**👤 Admin:** {st.session_state.admin_username}")
        st.markdown("---")
        
        menu = st.radio(
            "Navigasi",
            [
                "Input Peminjaman",
                "Lihat Peminjaman",
                "Pengembalian Buku",
                "Data Siswa",
                "Data Buku",
                "Logout"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.caption("© 2025 SMAN 47 Jakarta")
        st.caption("PKM Universitas Pamulang")
    
    # Route to pages
    if menu == "Input Peminjaman":
        input_peminjaman_page()
    elif menu == "Lihat Peminjaman":
        lihat_peminjaman_page()
    elif menu == "Pengembalian Buku":
        pengembalian_page()
    elif menu == "Data Siswa":
        data_siswa_page()
    elif menu == "Data Buku":
        data_buku_page()
    elif menu == "Logout":
        AuthService.logout()
        st.success("✅ Logout berhasil!")
        st.rerun()

if __name__ == "__main__":
    main()


