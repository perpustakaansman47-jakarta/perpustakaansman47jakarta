import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import os

class SistemPerpustakaanGUI:
    def __init__(self, root, db_path, bg_image_path=None, menu_bg_image_path=None):
        self.root = root
        self.db_path = db_path
        self.bg_image_path = bg_image_path
        self.menu_bg_image_path = menu_bg_image_path
        self.conn = None
        self.admin_id = None
        self.admin_username = None
        
        self.root.title("Sistem Perpustakaan SMAN 47 Jakarta")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        self.connect_db()
        self.show_login()
    
    def connect_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal koneksi ke database:\n{e}")
            return False
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def set_background_login(self, frame):
        if self.bg_image_path and os.path.exists(self.bg_image_path):
            try:
                img = Image.open(self.bg_image_path)
                img = img.resize((1500, 950), Image.Resampling.LANCZOS)
                img = img.filter(ImageFilter.GaussianBlur(1.3))
                
                photo = ImageTk.PhotoImage(img)
                bg_label = tk.Label(frame, image=photo)
                bg_label.image = photo
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                return bg_label
            except Exception as e:
                print(f"Warning: {e}")
        return None
    
    def set_background_menu(self, frame):
        if self.menu_bg_image_path and os.path.exists(self.menu_bg_image_path):
            try:
                img = Image.open(self.menu_bg_image_path)
                img = img.resize((1500, 950), Image.Resampling.LANCZOS)
                img = img.filter(ImageFilter.GaussianBlur(1.3))
                
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(0.9)
                
                photo = ImageTk.PhotoImage(img)
                bg_label = tk.Label(frame, image=photo)
                bg_label.image = photo
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                return bg_label
            except Exception as e:
                print(f"Warning: {e}")
        return None
    
    def show_login(self):
        self.clear_window()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        self.set_background_login(main_frame)
        
        login_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="raised")
        login_frame.place(relx=0.5, rely=0.5, anchor="center", width=683, height=465)
        
        header_frame = tk.Frame(login_frame, bg="#1e88e5", height=80)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="🏫 SMAN 47 JAKARTA 🏫", font=("Seagull", 18, "bold"),
                 bg="#1e88e5", fg="white").pack(pady=5)
        tk.Label(header_frame, text="Sistem Perpustakaan", font=("Arial", 12),
                 bg="#1e88e5", fg="white").pack()
        
        form_frame = tk.Frame(login_frame, bg="#ffffff")
        form_frame.pack(pady=40, padx=40, fill="both", expand=True)
        
        tk.Label(form_frame, text="LOGIN ADMIN", font=("Seagull", 16, "bold"),
                 bg="#ffffff", fg="#1e88e5").pack(pady=(0, 30))
        
        tk.Label(form_frame, text="👤 Username:", font=("Arial", 11), bg="#ffffff").pack(anchor="w")
        username_entry = tk.Entry(form_frame, font=("Arial", 11), width=30)
        username_entry.pack(pady=(5, 15), ipady=5)
        username_entry.focus()
        
        tk.Label(form_frame, text="🔑 Password:", font=("Arial", 11), bg="#ffffff").pack(anchor="w")
        password_entry = tk.Entry(form_frame, font=("Arial", 11), width=30, show="●")
        password_entry.pack(pady=(5, 25), ipady=5)
        
        def handle_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if not username or not password:
                messagebox.showwarning("Peringatan", "Username dan password harus diisi!")
                return
            
            cur = self.conn.cursor()
            cur.execute("SELECT id_user, username FROM user WHERE username = ? AND password = ?",
                       (username, password))
            result = cur.fetchone()
            
            if result:
                self.admin_id = result[0]
                self.admin_username = result[1]
                self.show_main_menu()
            else:
                messagebox.showerror("Login Gagal", "Username atau password salah!")
                password_entry.delete(0, tk.END)
        
        password_entry.bind('<Return>', lambda e: handle_login())
        
        tk.Button(form_frame, text="LOGIN", font=("Arial", 12, "bold"), bg="#1e88e5",
                 fg="white", cursor="hand2", command=handle_login, width=20, height=2).pack()
        
        tk.Label(login_frame, text="© 2025 SMAN 47 Jakarta - Created By Pkm Universitas Pamulang",
                font=("Seagull", 9), bg="#ffffff", fg="#666666").pack(side="bottom", pady=10)
    
    def show_main_menu(self):
        self.clear_window()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        self.set_background_menu(main_frame)
        
        header_frame = tk.Frame(main_frame, bg="#1e88e5", height=80)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="🏫 SISTEM PERPUSTAKAAN SMAN 47 JAKARTA",
                font=("Seagull", 18, "bold"), bg="#1e88e5", fg="white").pack(pady=10)
        tk.Label(header_frame, text=f"👤 Admin: {self.admin_username}",
                font=("Arial", 11), bg="#1e88e5", fg="white").pack(pady=(0, 10))
        
        menu_items = [
            ("📖 Input Peminjaman", self.show_input_peminjaman, "#4caf50"),
            ("📋 Lihat Peminjaman", self.show_lihat_peminjaman, "#2196f3"),
            ("✅ Pengembalian Buku", self.show_pengembalian, "#ff9800"),
            ("👥 Data Siswa", self.show_data_siswa, "#9c27b0"),
            ("📚 Data Buku", self.show_data_buku, "#f44336"),
            ("🚪 Logout", self.logout, "#607d8b")
        ]
        positions = [
            (150, 150),   # Input Peminjaman
            (520, 150),   # Lihat Peminjaman
            (150, 320),   # Pengembalian
            (520, 320),   # Data Siswa
            (150, 490),   # Data Buku
            (520, 490)    # Logout
        ]
        
        for i, (text, command, color) in enumerate(menu_items):
            x, y = positions[i]
           
            btn = tk.Button(main_frame, text=text, font=("Arial", 12, "bold"),
                          bg=color, fg="white", cursor="hand2", command=command,
                          width=25, height=4, relief="raised", bd=3)
            btn.place(x=x, y=y)
            
            btn.bind("<Enter>", lambda e, b=btn: b.config(relief="sunken"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(relief="raised"))
            
        
    
    def show_input_peminjaman(self):
        self.clear_window()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        self.create_header(main_frame, "📖 INPUT PEMINJAMAN BUKU")
        self.create_back_button(main_frame)
        
        form_frame = tk.Frame(main_frame, bg="white", bd=2, relief="ridge")
        form_frame.pack(pady=10, padx=65, fill="both", expand=True)
        
        tk.Label(form_frame, text="Form Peminjaman Buku", font=("Seagull", 16, "bold"),
                bg="white", fg="#1e88e5").pack(pady=20)
        
        fields_frame = tk.Frame(form_frame, bg="white")
        fields_frame.pack(pady=10, padx=50, fill="both", expand=True)
        
# Field Nama Siswa
        tk.Label(fields_frame, text="👤 Nama Siswa:", font=("Arial", 11, "bold"),
                bg="white").grid(row=0, column=0, sticky="w", pady=15, padx=10)
        nama_siswa_entry = tk.Entry(fields_frame, font=("Arial", 11), width=50)
        nama_siswa_entry.grid(row=0, column=1, pady=15, padx=10, sticky="ew")

# Field Kelas dengan placeholder
        # Field Kelas dengan placeholder
        tk.Label(fields_frame, text="📚 Kelas:", font=("Arial", 11, "bold"),
                bg="white").grid(row=1, column=0, sticky="w", pady=15, padx=10)
        kelas_entry = tk.Entry(fields_frame, font=("Arial", 11), width=50)
        kelas_entry.grid(row=1, column=1, pady=15, padx=10, sticky="ew")
        kelas_entry.insert(0, "Contoh: 11 IPA 1")
        kelas_entry.config(fg="#999999")

        def on_kelas_focus_in(event):
            if kelas_entry.get() == "Contoh: 11 IPA 1":
                kelas_entry.delete(0, tk.END)
                kelas_entry.config(fg="#000000")

        def on_kelas_focus_out(event):
            if kelas_entry.get() == "":
                kelas_entry.insert(0, "Contoh: 11 IPA 1")
                kelas_entry.config(fg="#999999")

        kelas_entry.bind("<FocusIn>", on_kelas_focus_in)
        kelas_entry.bind("<FocusOut>", on_kelas_focus_out)

        # Field Cari Kode Buku dengan Button Search
        tk.Label(fields_frame, text="🔍 Cari Kode Buku:", font=("Arial", 11, "bold"), 
                bg="white").grid(row=2, column=0, sticky="w", pady=15, padx=10)

        kode_search_entry = tk.Entry(fields_frame, font=("Arial", 11), width=30)
        kode_search_entry.grid(row=2, column=1, sticky="w", pady=15, padx=10)

        # Field Kode Buku (Display) - Deklarasi dulu
        tk.Label(fields_frame, text="📖 Kode Buku:", font=("Arial", 11, "bold"),
                bg="white").grid(row=4, column=0, sticky="w", pady=15, padx=10)
        kode_buku_label = tk.Label(fields_frame, text="(Pilih buku terlebih dahulu)",
                           font=("Arial", 11), bg="white", fg="#666666")
        kode_buku_label.grid(row=4, column=1, sticky="w", pady=15, padx=10)

        # Variabel untuk buku
        buku_var = tk.StringVar()
        buku_combo = ttk.Combobox(fields_frame, textvariable=buku_var, font=("Arial", 11),
                         width=48, state="readonly")

        def cari_buku_kode():
            kode_input = kode_search_entry.get().strip()
            if not kode_input:
                messagebox.showwarning("Peringatan", "Masukkan kode buku!")
                return

            cur = self.conn.cursor()
            cur.execute("SELECT id_buku, kode_buku, nama_buku FROM buku WHERE kode_buku = ?", (kode_input,))
            result = cur.fetchone()

            if result:
                # Jika ditemukan, tampilkan di combobox
                buku_combo['values'] = [f"{result[0]} - {result[1]} - {result[2]}"]
                buku_combo.set(f"{result[0]} - {result[1]} - {result[2]}")
                buku_combo.grid(row=3, column=1, pady=15, padx=10, sticky="ew")
        
                # Update kode buku label
                kode_buku_label.config(text=result[1], fg="#4caf50", font=("Arial", 11, "bold"))
            else:
                # Jika tidak ditemukan
                buku_combo['values'] = ["Buku tidak ditemukan"]
                buku_combo.set("Buku tidak ditemukan")
                buku_combo.grid(row=3, column=1, pady=15, padx=10, sticky="ew")
                kode_buku_label.config(text="(Pilih buku terlebih dahulu)", fg="#666666")
                messagebox.showinfo("Info", "Buku dengan kode tersebut tidak ditemukan!")

        # Button Search
        tk.Button(fields_frame, text="🔍 Search", command=cari_buku_kode,
                font=("Arial", 10, "bold"), bg="#2196F3", fg="white", 
                cursor="hand2").grid(row=2, column=2, pady=15, padx=10)

        # Field Nama Buku (Combobox)
        tk.Label(fields_frame, text="📚 Nama Buku:", font=("Arial", 11, "bold"),
                bg="white").grid(row=3, column=0, sticky="w", pady=15, padx=10)

        # Update kode buku saat combobox dipilih
        def update_kode_buku(event):
            selected = buku_var.get()
            if selected and " - " in selected and "tidak ditemukan" not in selected:
                parts = selected.split(" - ")
                if len(parts) >= 2:
                    kode = parts[1]
                    kode_buku_label.config(text=kode, fg="#4caf50", font=("Arial", 11, "bold"))

        buku_combo.bind("<<ComboboxSelected>>", update_kode_buku)

        # Field Tanggal Pinjam
        tk.Label(fields_frame, text="📅 Tanggal Pinjam:", font=("Arial", 11, "bold"),
                bg="white").grid(row=5, column=0, sticky="w", pady=15, padx=10)

        tanggal_frame = tk.Frame(fields_frame, bg="white")
        tanggal_frame.grid(row=5, column=1, sticky="w", pady=15, padx=10)

        tk.Label(tanggal_frame, text="Tanggal:", font=("Arial", 10), bg="white").pack(side="left", padx=(0, 5))
        tanggal_spinbox = tk.Spinbox(tanggal_frame, from_=1, to=31, width=5, font=("Arial", 10))
        tanggal_spinbox.delete(0, tk.END)
        tanggal_spinbox.insert(0, datetime.now().day)
        tanggal_spinbox.pack(side="left", padx=5)

        tk.Label(tanggal_frame, text="Bulan:", font=("Arial", 10), bg="white").pack(side="left", padx=(10, 5))
        bulan_spinbox = tk.Spinbox(tanggal_frame, from_=1, to=12, width=5, font=("Arial", 10))
        bulan_spinbox.delete(0, tk.END)
        bulan_spinbox.insert(0, datetime.now().month)
        bulan_spinbox.pack(side="left", padx=5)

        tk.Label(tanggal_frame, text="Tahun:", font=("Arial", 10), bg="white").pack(side="left", padx=(10, 5))
        tahun_spinbox = tk.Spinbox(tanggal_frame, from_=2020, to=2030, width=8, font=("Arial", 10))
        tahun_spinbox.delete(0, tk.END)
        tahun_spinbox.insert(0, datetime.now().year)
        tahun_spinbox.pack(side="left", padx=5)

        # Field Tanggal Pengembalian (AUTO 3 HARI)
        tk.Label(fields_frame, text="📅 Tanggal Pengembalian:", font=("Arial", 11, "bold"),
                bg="white").grid(row=6, column=0, sticky="w", pady=15, padx=10)

        tgl_kembali_frame = tk.Frame(fields_frame, bg="white")
        tgl_kembali_frame.grid(row=6, column=1, sticky="w", pady=15, padx=10)

        tk.Label(tgl_kembali_frame, text="Tanggal:", font=("Arial", 10), bg="white").pack(side="left", padx=(0,5))
        tgl_kembali_spin = tk.Spinbox(tgl_kembali_frame, from_=1, to=31, width=5, font=("Arial", 10))
        tgl_kembali_spin.pack(side="left", padx=5)

        tk.Label(tgl_kembali_frame, text="Bulan:", font=("Arial", 10), bg="white").pack(side="left", padx=(10,5))
        bln_kembali_spin = tk.Spinbox(tgl_kembali_frame, from_=1, to=12, width=5, font=("Arial", 10))
        bln_kembali_spin.pack(side="left", padx=5)

        tk.Label(tgl_kembali_frame, text="Tahun:", font=("Arial", 10), bg="white").pack(side="left", padx=(10,5))
        thn_kembali_spin = tk.Spinbox(tgl_kembali_frame, from_=2020, to=2030, width=8, font=("Arial", 10))
        thn_kembali_spin.pack(side="left", padx=5)

        # Set tanggal kembali otomatis 3 hari dari sekarang
        t_kembali = datetime.now() + timedelta(days=3)
        tgl_kembali_spin.delete(0, tk.END)
        tgl_kembali_spin.insert(0, t_kembali.day)
        bln_kembali_spin.delete(0, tk.END)
        bln_kembali_spin.insert(0, t_kembali.month)
        thn_kembali_spin.delete(0, tk.END)
        thn_kembali_spin.insert(0, t_kembali.year)

        # Konfigurasi kolom
        fields_frame.columnconfigure(1, weight=1)

        # Fungsi Submit
        def submit_peminjaman():
            # ============ VALIDASI & AMBIL DATA FORM ============
            nama_siswa = nama_siswa_entry.get().strip()
            nama_kelas = kelas_entry.get().strip()
            buku_selected = buku_var.get()
            kode_buku = kode_buku_label.cget("text").strip()
    
            # Validasi Nama Siswa
            if not nama_siswa:
                messagebox.showwarning("Peringatan", "Nama siswa harus diisi!")
                return
    
            # Validasi Kelas
            if nama_kelas == "Contoh: 11 IPA 1" or not nama_kelas:
                messagebox.showwarning("Peringatan", "Kelas harus diisi!")
                return
    
            # Validasi Buku
            if not buku_selected or "tidak ditemukan" in buku_selected:
                messagebox.showwarning("Peringatan", "Pilih nama buku dari daftar!")
                return
    
            # Validasi Kode Buku
            if kode_buku == "(Pilih buku terlebih dahulu)" or not kode_buku:
                messagebox.showwarning("Peringatan", "Kode buku harus diisi!")
                return
    
            # Ambil Nama Buku dari Combobox
            parts = buku_selected.split(" - ")
            if len(parts) >= 3:
                nama_buku = parts[2]
            else:
                messagebox.showerror("Error", "Format buku tidak valid!")
                return
    
            # Ambil Tanggal Pinjam
            try:
                tgl = int(tanggal_spinbox.get())
                bln = int(bulan_spinbox.get())
                thn = int(tahun_spinbox.get())
                tanggal_pinjam = f"{thn:04d}-{bln:02d}-{tgl:02d}"
            except ValueError:
                messagebox.showerror("Error", "Format tanggal tidak valid!")
                return
    
            # Hitung Tanggal Kembali (3 hari dari tanggal pinjam)
            try:
                t_pinjam = datetime(thn, bln, tgl)
                t_kembali = t_pinjam + timedelta(days=3)
        
                tgl_kembali_spin.delete(0, tk.END)
                tgl_kembali_spin.insert(0, t_kembali.day)
        
                bln_kembali_spin.delete(0, tk.END)
                bln_kembali_spin.insert(0, t_kembali.month)
        
                thn_kembali_spin.delete(0, tk.END)
                thn_kembali_spin.insert(0, t_kembali.year)
            except:
                pass
    
            # ============ PROSES DATABASE ============
            try:
                cur = self.conn.cursor()
        
                # Cek/Insert KELAS
                cur.execute("SELECT id_kelas FROM kelas WHERE nama_kelas = ?", (nama_kelas,))
                kelas_existing = cur.fetchone()
        
                if kelas_existing:
                    id_kelas = kelas_existing[0]
                else:
                    cur.execute("INSERT INTO kelas (nama_kelas) VALUES (?)", (nama_kelas,))
                    id_kelas = cur.lastrowid
        
                # Cek/Insert SISWA
                cur.execute("SELECT id_siswa FROM siswa WHERE nama_siswa = ? AND id_kelas = ?",
                        (nama_siswa, id_kelas))
                siswa_existing = cur.fetchone()
        
                if siswa_existing:
                    id_siswa = siswa_existing[0]
                else:
                    cur.execute("INSERT INTO siswa (nama_siswa, id_kelas) VALUES (?, ?)",
                                (nama_siswa, id_kelas))
                    id_siswa = cur.lastrowid
        
                # Cek/Insert BUKU
                cur.execute("SELECT id_buku FROM buku WHERE kode_buku = ?", (kode_buku,))
                buku_existing = cur.fetchone()
        
                if buku_existing:
                    id_buku = buku_existing[0]
                    cur.execute("UPDATE buku SET nama_buku = ? WHERE id_buku = ?", 
                                (nama_buku, id_buku))
                else:
                    cur.execute("INSERT INTO buku (kode_buku, nama_buku) VALUES (?, ?)",
                            (kode_buku, nama_buku))
                    id_buku = cur.lastrowid
        
                # Insert PEMINJAMAN
                cur.execute("""INSERT INTO peminjaman (id_siswa, id_buku, tanggal_pinjam, status, id_admin)
                            VALUES (?, ?, ?, 'dipinjam', ?)""",
                            (id_siswa, id_buku, tanggal_pinjam, self.admin_id))
        
                self.conn.commit()
                id_peminjaman = cur.lastrowid
        
                # Tampilkan Receipt
                self.show_receipt(id_peminjaman, nama_siswa, nama_kelas, kode_buku, nama_buku, tanggal_pinjam)
        
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Gagal menyimpan data:\n{e}")
                self.conn.rollback()

        # Button Simpan
        tk.Button(form_frame, text="✅ SIMPAN PEMINJAMAN", font=("Arial", 12, "bold"),
                bg="#4caf50", fg="white", cursor="hand2", command=submit_peminjaman,
                width=25, height=2).pack(pady=15)
    
    def show_receipt(self, id_pinjam, nama_siswa, kelas, kode_buku, nama_buku, tanggal):
        win = tk.Toplevel(self.root)
        win.title("Receipt Peminjaman")
        win.geometry("800x750")
        win.resizable(True, True)
        
        frame = tk.Frame(win, bg="white")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="🏫 SMAN 47 JAKARTA 🏫", font=("Seagull", 16, "bold"),
                bg="white", fg="#1e88e5").pack(pady=10)
        tk.Label(frame, text="RECEIPT PEMINJAMAN BUKU", font=("Seagull", 14, "bold"),
                bg="white").pack()
        tk.Label(frame, text="="*50, font=("Courier", 10), bg="white").pack(pady=5)
        
        info_text = f"""
No. Peminjaman  : {id_pinjam}
Tanggal         : {tanggal}
Admin           : {self.admin_username}

{'='*50}
DATA SISWA:
  Nama          : {nama_siswa}
  Kelas         : {kelas}

{'='*50}
DATA BUKU:
  Kode Buku     : {kode_buku}
  Nama Buku     : {nama_buku}

{'='*50}
        """
        
        tk.Label(frame, text=info_text, font=("Courier", 10), bg="white", justify="left").pack(pady=10)
        tk.Label(frame, text="⚠️ Harap kembalikan buku tepat waktu!", font=("Arial", 10, "bold"),
                bg="white", fg="#f44336").pack(pady=10)
        tk.Button(frame, text="TUTUP", font=("Arial", 11, "bold"), bg="#1e88e5",
                 fg="white", cursor="hand2", command=win.destroy, width=15).pack(pady=20)
    
    def show_lihat_peminjaman(self):
        self.clear_window()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        self.create_header(main_frame, "📋 DATA PEMINJAMAN")
        self.create_back_button(main_frame)
        
        filter_frame = tk.Frame(main_frame, bg="white")
        filter_frame.pack(pady=10)
        
        tree_frame = tk.Frame(main_frame, bg="white")
        tree_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Siswa", "Buku", "Tgl Pinjam", "Tgl Kembali", "Status"),
                           show="headings", yscrollcommand=scrollbar.set)
        
        for col in ["ID", "Siswa", "Buku", "Tgl Pinjam", "Tgl Kembali", "Status"]:
            tree.heading(col, text=col.replace("Tgl", "Tanggal"))
        
        tree.column("ID", width=50)
        tree.column("Siswa", width=150)
        tree.column("Buku", width=200)
        tree.column("Tgl Pinjam", width=120)
        tree.column("Tgl Kembali", width=120)
        tree.column("Status", width=120)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=tree.yview)
        
        def load_data(status_filter):
            for item in tree.get_children():
                tree.delete(item)
            
            cur = self.conn.cursor()
            if status_filter == "ALL":
                cur.execute("""SELECT p.id_peminjaman, s.nama_siswa, b.nama_buku,
                             p.tanggal_pinjam, p.tanggal_kembali, p.status
                             FROM peminjaman p
                             JOIN siswa s ON p.id_siswa = s.id_siswa
                             JOIN buku b ON p.id_buku = b.id_buku
                             ORDER BY p.id_peminjaman DESC""")
            else:
                cur.execute("""SELECT p.id_peminjaman, s.nama_siswa, b.nama_buku,
                             p.tanggal_pinjam, p.tanggal_kembali, p.status
                             FROM peminjaman p
                             JOIN siswa s ON p.id_siswa = s.id_siswa
                             JOIN buku b ON p.id_buku = b.id_buku
                             WHERE p.status = ?
                             ORDER BY p.id_peminjaman DESC""", (status_filter,))
            
            for row in cur.fetchall():
                tgl_kembali = row[4] if row[4] else "-"
                tree.insert("", "end", values=(row[0], row[1], row[2], row[3], tgl_kembali, row[5]))
        
        tk.Button(filter_frame, text="Semua", font=("Arial", 10, "bold"), bg="#2196f3",
                 fg="white", cursor="hand2", command=lambda: load_data("ALL"), width=15).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Sedang Dipinjam", font=("Arial", 10, "bold"), bg="#ff9800",
                 fg="white", cursor="hand2", command=lambda: load_data("dipinjam"), width=15).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Sudah Dikembalikan", font=("Arial", 10, "bold"), bg="#4caf50",
                 fg="white", cursor="hand2", command=lambda: load_data("dikembalikan"), width=15).pack(side="left", padx=5)
        
        load_data("ALL")
    
    def show_pengembalian(self):
        self.clear_window()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        self.create_header(main_frame, "✅ PENGEMBALIAN BUKU")
        self.create_back_button(main_frame)
        
        info_frame = tk.Frame(main_frame, bg="white")
        info_frame.pack(pady=10)
        tk.Label(info_frame, text="Pilih peminjaman yang akan dikembalikan:",
                font=("Arial", 12), bg="white").pack(pady=10)
        
        tree_frame = tk.Frame(main_frame, bg="white")
        tree_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Kolom 'Tgl Kembali' ada di sini
        tree = ttk.Treeview(tree_frame, columns=("ID", "Siswa", "Buku", "Tgl Pinjam", "Tgl Kembali"),
                           show="headings", yscrollcommand=scrollbar.set)
        
        tree.heading("ID", text="ID")
        tree.heading("Siswa", text="Nama Siswa")
        tree.heading("Buku", text="Nama Buku")
        tree.heading("Tgl Pinjam", text="Tanggal Pinjam")
        tree.heading("Tgl Kembali", text="Tanggal Kembali") # Diperbarui
        
        tree.column("ID", width=50)
        tree.column("Siswa", width=150) 
        tree.column("Buku", width=250) 
        tree.column("Tgl Pinjam", width=120)
        tree.column("Tgl Kembali", width=120) 
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=tree.yview)
        
        cur = self.conn.cursor()
        # Ambil hanya kolom yang statusnya 'dipinjam'
        cur.execute("""SELECT p.id_peminjaman, s.nama_siswa, b.nama_buku, b.kode_buku, p.tanggal_pinjam
                     FROM peminjaman p
                     JOIN siswa s ON p.id_siswa = s.id_siswa
                     JOIN buku b ON p.id_buku = b.id_buku
                     WHERE p.status = 'dipinjam'
                     ORDER BY p.id_peminjaman DESC""")
        
        for row in cur.fetchall():
            id_pinjam = row[0]
            tgl_pinjam_str = row[4] # Tanggal Pinjam dari database
            
            # 👇 SOLUSI: Hitung Tanggal Pengembalian (3 Hari)
            try:
                # 1. Konversi string tanggal pinjam ("YYYY-MM-DD") ke objek datetime
                tgl_pinjam_obj = datetime.strptime(tgl_pinjam_str, "%Y-%m-%d")
                
                # 2. Tambahkan jeda 3 hari
                tgl_kembali_obj = tgl_pinjam_obj + timedelta(days=3)
                
                # 3. Format kembali ke string untuk ditampilkan
                tgl_kembali_str = tgl_kembali_obj.strftime("%Y-%m-%d")
            except ValueError:
                tgl_kembali_str = "Format Tgl Error" 
            # 👆 SOLUSI SELESAI
            
            # Masukkan data (dengan tanggal kembali yang sudah dihitung) ke Treeview
            tree.insert("", "end", values=(id_pinjam, row[1], f"{row[2]} ({row[3]})", tgl_pinjam_str, tgl_kembali_str)) 
        
        def proses_pengembalian():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Peringatan", "Pilih peminjaman!")
                return
            
            item = tree.item(selected[0])
            id_pinjam = item['values'][0]
            nama_siswa = item['values'][1]
            nama_buku = item['values'][2]
            
            if messagebox.askyesno("Konfirmasi", f"Kembalikan buku?\n\nSiswa: {nama_siswa}\nBuku: {nama_buku}"):
                try:
                    cur = self.conn.cursor()
                    # UPDATE tanggal_kembali di database ke TANGGAL HARI INI saat dikembalikan
                    cur.execute("UPDATE peminjaman SET tanggal_kembali = ?, status = 'dikembalikan' WHERE id_peminjaman = ?",
                               (datetime.now().strftime("%Y-%m-%d"), id_pinjam))
                    self.conn.commit()
                    messagebox.showinfo("Berhasil", "Buku berhasil dikembalikan!")
                    self.show_pengembalian()
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Gagal: {e}")
        
        tk.Button(main_frame, text="✅ KEMBALIKAN BUKU", font=("Arial", 12, "bold"),
                 bg="#4caf50", fg="white", cursor="hand2", command=proses_pengembalian,
                 width=20, height=2).pack(pady=20)
    
    def show_data_siswa(self):
        self.clear_window()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        self.create_header(main_frame, "👥 DATA SISWA")
        self.create_back_button(main_frame)
        
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(pady=10)
        
        tree_frame = tk.Frame(main_frame, bg="white")
        tree_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        tree = ttk.Treeview(tree_frame, columns=("ID", "Nama", "Kelas"),
                           show="headings", yscrollcommand=scrollbar.set)
        
        tree.heading("ID", text="ID")
        tree.heading("Nama", text="Nama Siswa")
        tree.heading("Kelas", text="Kelas")
        
        tree.column("ID", width=80)
        tree.column("Nama", width=400)
        tree.column("Kelas", width=200)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=tree.yview)
        
        def load_siswa():
            for item in tree.get_children():
                tree.delete(item)
            
            cur = self.conn.cursor()
            cur.execute("""SELECT s.id_siswa, s.nama_siswa, k.nama_kelas
                         FROM siswa s
                         LEFT JOIN kelas k ON s.id_kelas = k.id_kelas
                         ORDER BY s.id_siswa""")
            
            for row in cur.fetchall():
                kelas = row[2] if row[2] else "Belum ada kelas"
                tree.insert("", "end", values=(row[0], row[1], kelas))
        
        def tambah_siswa():
            win = tk.Toplevel(self.root)
            win.title("Tambah Siswa Baru")
            win.geometry("400x300")
            win.resizable(True, True)
            
            frame = tk.Frame(win, bg="white")
            frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Label(frame, text="Tambah Siswa Baru", font=("Arial", 14, "bold"),
                    bg="white", fg="#1e88e5").pack(pady=10)
            
            tk.Label(frame, text="Nama Siswa:", font=("Arial", 10), bg="white").pack(anchor="w", pady=(10, 0))
            nama_entry = tk.Entry(frame, font=("Arial", 10), width=40)
            nama_entry.pack(pady=5)
            
            tk.Label(frame, text="Kelas:", font=("Arial", 10), bg="white").pack(anchor="w", pady=(10, 0))
            
            # Frame untuk entry dan tombol
            kelas_frame = tk.Frame(frame, bg="white")
            kelas_frame.pack(pady=5, fill="x")
            
            kelas_entry = tk.Entry(kelas_frame, font=("Arial", 10), width=32)
            kelas_entry.pack(side="left", padx=(0, 5))

            cur = self.conn.cursor()
            cur.execute("SELECT id_kelas, nama_kelas FROM kelas ORDER BY id_kelas")
            kelas_list = cur.fetchall()
            
            kelas_var = tk.StringVar()
            
            # Fungsi untuk refresh dropdown kelas
            def refresh_kelas_list():
                cur = self.conn.cursor()
                cur.execute("SELECT id_kelas, nama_kelas FROM kelas ORDER BY id_kelas")
                updated_list = cur.fetchall()
                
                menu = dropdown['menu']
                menu.delete(0, 'end')
                for kelas in updated_list:
                    kelas_value = f"{kelas[0]} - {kelas[1]}"
                    menu.add_command(label=kelas_value, 
                                   command=lambda v=kelas_value: kelas_var.set(v))
            
            # Fungsi untuk update entry saat pilih dari dropdown
            def on_kelas_select(*args):
                kelas_entry.delete(0, tk.END)
                kelas_entry.insert(0, kelas_var.get())
            
            kelas_var.trace('w', on_kelas_select)
            
            # Fungsi untuk input kelas manual
            def input_kelas_manual():
                win_kelas = tk.Toplevel()
                win_kelas.title("Tambah Kelas Baru")
                win_kelas.geometry("400x350")
                win_kelas.resizable(False, False)
                win_kelas.configure(bg="white")
                win_kelas.transient(win)
                win_kelas.grab_set()
                
                frame_kelas = tk.Frame(win_kelas, bg="white", padx=20, pady=20)
                frame_kelas.pack(fill="both", expand=True)
                
                tk.Label(frame_kelas, text="Tambah Kelas Baru", font=("Arial", 14, "bold"), 
                        bg="white").pack(pady=(0, 20))
                
                tk.Label(frame_kelas, text="ID Kelas:", font=("Arial", 10), bg="white").pack(anchor="w")
                id_entry = tk.Entry(frame_kelas, font=("Arial", 10), width=30)
                id_entry.pack(pady=5)
                
                tk.Label(frame_kelas, text="Nama Kelas:", font=("Arial", 10), bg="white").pack(anchor="w", pady=(10, 0))
                nama_kelas_entry = tk.Entry(frame_kelas, font=("Arial", 10), width=30)
                nama_kelas_entry.pack(pady=5)
                
                def simpan_kelas():
                    id_kelas = id_entry.get().strip()
                    nama_kelas = nama_kelas_entry.get().strip()
                    
                    if not id_kelas or not nama_kelas:
                        messagebox.showwarning("Peringatan", "Semua field harus diisi!")
                        return
                    
                    try:
                        cur = self.conn.cursor()
                        
                        # Cek duplikat ID
                        cur.execute("SELECT id_kelas FROM kelas WHERE id_kelas = ?", (id_kelas,))
                        if cur.fetchone():
                            messagebox.showwarning("Peringatan", f"ID Kelas '{id_kelas}' sudah ada!")
                            return
                        
                        # Simpan ke database
                        cur.execute("INSERT INTO kelas (id_kelas, nama_kelas) VALUES (?, ?)", 
                                   (id_kelas, nama_kelas))
                        self.conn.commit()
                        
                        messagebox.showinfo("Berhasil", f"Kelas '{nama_kelas}' berhasil ditambahkan!")
                        
                        # Set ke entry dan variable
                        kelas_value = f"{id_kelas} - {nama_kelas}"
                        kelas_var.set(kelas_value)
                        kelas_entry.delete(0, tk.END)
                        kelas_entry.insert(0, kelas_value)
                        
                        # Refresh dropdown
                        refresh_kelas_list()
                        
                        win_kelas.destroy()
                        
                    except sqlite3.Error as e:
                        messagebox.showerror("Error", f"Gagal menyimpan: {e}")
                
                btn_frame = tk.Frame(frame_kelas, bg="white")
                btn_frame.pack(pady=20)
                
                tk.Button(btn_frame, text="✅ SIMPAN", font=("Arial", 11, "bold"), 
                         bg="#4caf50", fg="white", cursor="hand2", 
                         command=simpan_kelas, width=12, height=1, padx=10, pady=10).pack(side="left", padx=15)
                
                tk.Button(btn_frame, text="❌ BATAL", font=("Arial", 11, "bold"), 
                         bg="#f44336", fg="white", cursor="hand2", 
                         command=win_kelas.destroy, width=12, height=1, padx=10, pady=10).pack(side="left", padx=15)
                
                id_entry.focus()
            
            # Dropdown kelas (jika ada data)
            if kelas_list:
                dropdown = tk.OptionMenu(kelas_frame, kelas_var, 
                                        *[f"{k[0]} - {k[1]}" for k in kelas_list])
                dropdown.config(font=("Arial", 9), bg="#2196F3", fg="white", 
                               cursor="hand2", width=4)
                dropdown.pack(side="left", padx=(0, 5))
            
            # Tombol tambah kelas manual
            tk.Button(kelas_frame, text="➕", font=("Arial", 10, "bold"), 
                     bg="#FF9800", fg="white", cursor="hand2", width=3,
                     command=input_kelas_manual).pack(side="left")
            
            
            def save():
                nama = nama_entry.get().strip()
                kelas_input = kelas_entry.get().strip()
                
                if not nama or not kelas_input:
                    messagebox.showwarning("Peringatan", "Semua field harus diisi!")
                    return
                
                # Parse ID kelas (support "ID - Nama" atau "ID" saja)
                if " - " in kelas_input:
                    id_kelas = kelas_input.split(" - ")[0]
                else:
                    id_kelas = kelas_input
                
                try:
                    cur = self.conn.cursor()
                    
                    # Validasi kelas ada di database
                    cur.execute("SELECT id_kelas FROM kelas WHERE id_kelas = ?", (id_kelas,))
                    if not cur.fetchone():
                        messagebox.showwarning("Peringatan", 
                                             f"Kelas dengan ID '{id_kelas}' tidak ditemukan!\n" + 
                                             "Gunakan tombol ➕ untuk menambah kelas baru.")
                        return
                    
                    cur.execute("INSERT INTO siswa (nama_siswa, id_kelas) VALUES (?, ?)", (nama, id_kelas))
                    self.conn.commit()
                    messagebox.showinfo("Berhasil", f"Siswa '{nama}' berhasil ditambahkan!")
                    win.destroy()
                    load_siswa()
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Gagal: {e}")
            
            tk.Button(frame, text="✅ SIMPAN", font=("Arial", 11, "bold"), bg="#4caf50",
                     fg="white", cursor="hand2", command=save, width=15).pack(pady=20)
        
        def hapus_siswa():
            selected = tree.selection()
            
            if not selected:
                messagebox.showwarning("Peringatan", "Pilih siswa yang akan dihapus!")
                return
            
            # Ambil data siswa yang dipilih
            item = tree.item(selected[0])
            id_siswa = item['values'][0]
            nama_siswa = item['values'][1]
            
            # Konfirmasi hapus
            konfirmasi = messagebox.askyesno("Konfirmasi Hapus", 
                                             f"Apakah Anda yakin ingin menghapus siswa:\n\n" + 
                                             f"ID: {id_siswa}\n" +
                                             f"Nama: {nama_siswa}?")
            
            if konfirmasi:
                try:
                    cur = self.conn.cursor()
                    cur.execute("DELETE FROM siswa WHERE id_siswa = ?", (id_siswa,))
                    self.conn.commit()
                    
                    messagebox.showinfo("Berhasil", f"Siswa '{nama_siswa}' berhasil dihapus!")
                    load_siswa()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Gagal menghapus: {e}")
        
        def cari_siswa():
            keyword = search_entry.get().strip()
            
            for item in tree.get_children():
                tree.delete(item)
            
            cur = self.conn.cursor()
            if keyword:
                cur.execute("""SELECT s.id_siswa, s.nama_siswa, k.nama_kelas
                             FROM siswa s
                             LEFT JOIN kelas k ON s.id_kelas = k.id_kelas
                             WHERE s.nama_siswa LIKE ?""", (f"%{keyword}%",))
            else:
                cur.execute("""SELECT s.id_siswa, s.nama_siswa, k.nama_kelas
                             FROM siswa s
                             LEFT JOIN kelas k ON s.id_kelas = k.id_kelas
                             ORDER BY s.id_siswa""")
            
            for row in cur.fetchall():
                kelas = row[2] if row[2] else "Belum ada kelas"
                tree.insert("", "end", values=(row[0], row[1], kelas))
        
        # Tombol dan Search dalam satu baris
        tk.Button(button_frame, text="➕ Tambah Siswa", font=("Arial", 10, "bold"), bg="#4caf50",
                 fg="white", cursor="hand2", command=tambah_siswa, width=15).pack(side="left", padx=5)
        tk.Button(button_frame, text="🗑️ Hapus Siswa", font=("Arial", 10, "bold"), bg="#f44336",
                 fg="white", cursor="hand2", command=lambda: hapus_siswa(), width=15).pack(side="left", padx=5)
        tk.Button(button_frame, text="🔄 Refresh", font=("Arial", 10, "bold"), bg="#2196f3",
                 fg="white", cursor="hand2", command=load_siswa, width=15).pack(side="left", padx=5)
        
        # Separator
        tk.Frame(button_frame, width=20, bg="white").pack(side="left")
        
        # Search di sebelah kanan tombol
        tk.Label(button_frame, text="🔍 Cari:", font=("Arial", 10), bg="white").pack(side="left", padx=5)
        search_entry = tk.Entry(button_frame, font=("Arial", 10), width=30)
        search_entry.pack(side="left", padx=5)
        tk.Button(button_frame, text="Cari", font=("Arial", 10, "bold"), bg="#ff9800",
                 fg="white", cursor="hand2", command=cari_siswa, width=10).pack(side="left", padx=5)
        
        load_siswa()
    
    def show_data_buku(self):
        self.clear_window()
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)
        
        self.create_header(main_frame, "📚 DATA BUKU")
        self.create_back_button(main_frame)
        
        # Frame untuk menampung SEMUA tombol dan pencarian (sekarang sejajar)
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(pady=10)
        
        # --- DEFINISI FUNGSI INTERNAL ---
        
        def load_buku():
            # Menggunakan self.tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            cur = self.conn.cursor()
            cur.execute("SELECT id_buku, kode_buku, nama_buku FROM buku ORDER BY id_buku")
            
            for row in cur.fetchall():
                self.tree.insert("", "end", values=(row[0], row[1], row[2]))
        
        def hapus_buku():
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Peringatan", "Pilih buku yang akan dihapus!")
                return
            
            item = self.tree.item(selected[0])
            kode_buku = item['values'][1] # Ambil Kode Buku
            nama_buku = item['values'][2]
            
            if messagebox.askyesno("Konfirmasi", f"Yakin hapus buku ini?\n\nKode: {kode_buku}\nBuku: {nama_buku}"):
                try:
                    cur = self.conn.cursor()
                    cur.execute("DELETE FROM buku WHERE kode_buku = ?", (kode_buku,))
                    self.conn.commit()
                    messagebox.showinfo("Berhasil", "Buku berhasil dihapus!")
                    load_buku()
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Gagal menghapus buku: {e}")

        def cari_buku():
            keyword = search_entry.get().strip()
            
            # Menggunakan self.tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            cur = self.conn.cursor()
            if keyword:
                cur.execute("SELECT id_buku, kode_buku, nama_buku FROM buku WHERE nama_buku LIKE ? OR kode_buku LIKE ?",
                            (f"%{keyword}%", f"%{keyword}%"))
            else:
                cur.execute("SELECT id_buku, kode_buku, nama_buku FROM buku ORDER BY id_buku")
            
            for row in cur.fetchall():
                self.tree.insert("", "end", values=(row[0], row[1], row[2]))
        
        def tambah_buku():
            win = tk.Toplevel(self.root)
            win.title("Tambah Buku Baru")
            win.geometry("400x300") # Ditingkatkan tingginya
            win.resizable(False, False)
            
            frame = tk.Frame(win, bg="white")
            frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Label(frame, text="Tambah Buku Baru", font=("Arial", 14, "bold"),
                    bg="white", fg="#1e88e5").pack(pady=10)
            
            tk.Label(frame, text="Kode Buku:", font=("Arial", 10), bg="white").pack(anchor="w", pady=(5, 0))
            kode_entry = tk.Entry(frame, font=("Arial", 10), width=40)
            kode_entry.pack(pady=5)
            
            tk.Label(frame, text="Nama Buku:", font=("Arial", 10), bg="white").pack(anchor="w", pady=(5, 0))
            nama_entry = tk.Entry(frame, font=("Arial", 10), width=40)
            nama_entry.pack(pady=5)
            
            # Logika save() sudah ada di kode Anda, ini hanya penempatan tombolnya
            def save():
                kode = kode_entry.get().strip()
                nama = nama_entry.get().strip()
                
                if not kode or not nama:
                    messagebox.showwarning("Peringatan", "Semua field harus diisi!")
                    return
                
                try:
                    cur = self.conn.cursor()
                    cur.execute("INSERT INTO buku (kode_buku, nama_buku) VALUES (?, ?)", (kode, nama))
                    self.conn.commit()
                    messagebox.showinfo("Berhasil", f"Buku '{nama}' berhasil ditambahkan!")
                    win.destroy()
                    load_buku()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", f"Kode buku '{kode}' sudah ada!")
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Gagal: {e}")
            
            # ✅ TOMBOL SIMPAN di pop-up Tambah Buku
            tk.Button(frame, text="✅ SIMPAN", font=("Arial", 11, "bold"), bg="#4caf50",
                      fg="white", cursor="hand2", command=save, width=15).pack(pady=20)
        
        # --- PEMASANGAN TOMBOL & PENCARIAN (BARU: Sejajar) ---
        
        # 1. Tombol Tambah Buku
        tk.Button(button_frame, text="➕ Tambah Buku", font=("Arial", 10, "bold"), bg="#4caf50",
                 fg="white", cursor="hand2", command=tambah_buku, width=15).pack(side="left", padx=5)
        
        # 2. Tombol Hapus Buku (BARU)
        tk.Button(button_frame, text="🗑️ Hapus Buku", font=("Arial", 10, "bold"), bg="#f44336", 
                 fg="white", cursor="hand2", command=hapus_buku, width=15).pack(side="left", padx=5)
                 
        # 3. Tombol Refresh
        tk.Button(button_frame, text="🔄 Refresh", font=("Arial", 10, "bold"), bg="#2196f3",
                 fg="white", cursor="hand2", command=load_buku, width=15).pack(side="left", padx=5)
        
        # 4. Label dan Input Pencarian (Sejajar)
        tk.Label(button_frame, text=" | 🔍 Cari:", font=("Arial", 10, "bold"), bg="white").pack(side="left", padx=(15, 5)) 
        
        search_entry = tk.Entry(button_frame, font=("Arial", 10), width=30)
        search_entry.pack(side="left", padx=5)
        
        # 5. Tombol Cari
        tk.Button(button_frame, text="Cari", font=("Arial", 10, "bold"), bg="#ff9800",
                 fg="white", cursor="hand2", command=cari_buku, width=10).pack(side="left", padx=5)
        
        # --- PENGATURAN TREEVIEW (TABEL) ---
        
        tree_frame = tk.Frame(main_frame, bg="white")
        tree_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # PENTING: Mengubahnya menjadi self.tree
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Kode", "Nama"),
                               show="headings", yscrollcommand=scrollbar.set)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Kode", text="Kode Buku")
        self.tree.heading("Nama", text="Nama Buku")
        
        self.tree.column("ID", width=80)
        self.tree.column("Kode", width=150)
        self.tree.column("Nama", width=450)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Muat data saat pertama kali window dibuka
        load_buku()
        
    
    def create_header(self, parent, title):
        header_frame = tk.Frame(parent, bg="#1e88e5", height=60)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text=title, font=("Arial", 16, "bold"),
                bg="#1e88e5", fg="white").pack(pady=15)
    
    def create_back_button(self, parent):
        tk.Button(parent, text="⬅ Kembali", font=("Arial", 10), bg="#607d8b",
                 fg="white", cursor="hand2", command=self.show_main_menu, width=12).pack(anchor="nw", padx=10, pady=10)
    
    def logout(self):
        if messagebox.askyesno("Konfirmasi", "Yakin ingin logout?"):
            self.admin_id = None
            self.admin_username = None
            self.show_login()


def main():
    # GANTI PATH INI SESUAI LOKASI FILE KAMU!
    db_path = "perpustakaan_final.db"
    
    # Path foto background LOGIN
    bg_image_path ="logo1.jpeg"
    
    # Path foto background MENU UTAMA
    menu_bg_image_path ="sman47.jpeg"
    
    if not os.path.exists(db_path):
        print(f"Error: Database tidak ditemukan di: {db_path}")
        return
    
    root = tk.Tk()
    app = SistemPerpustakaanGUI(root, db_path, bg_image_path, menu_bg_image_path)
    root.mainloop()


if __name__ == "__main__":
    main()