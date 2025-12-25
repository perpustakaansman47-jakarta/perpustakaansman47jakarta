# vps_sync.py
# File ini terpisah dari perpustakaan.py
# Tinggal tempel dan import ke perpustakaan.py

import paramiko
import os
import sqlite3
from datetime import datetime
from pathlib import Path

class VPSSyncManager:
    """Manager untuk sinkronisasi database ke VPS"""
    
    def __init__(self, vps_host, vps_user, vps_pass, vps_port=22):
        self.vps_host = vps_host
        self.vps_user = vps_user
        self.vps_pass = vps_pass
        self.vps_port = vps_port
        self.ssh = None
        self.sftp = None
        self.last_sync = None
        self.sync_count = 0
    
    def connect(self):
        """Buat koneksi SSH/SFTP ke VPS"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=self.vps_host,
                port=self.vps_port,
                username=self.vps_user,
                password=self.vps_pass,
                timeout=10
            )
            self.sftp = self.ssh.open_sftp()
            print(f"✓ [VPS] Koneksi berhasil ke {self.vps_host}")
            return True
        except paramiko.AuthenticationException:
            print(f"✗ [VPS] Username/password salah!")
            return False
        except paramiko.SSHException as e:
            print(f"✗ [VPS] SSH Error: {e}")
            return False
        except Exception as e:
            print(f"✗ [VPS] Koneksi gagal: {e}")
            return False
    
    def disconnect(self):
        """Tutup koneksi SSH/SFTP"""
        try:
            if self.sftp:
                self.sftp.close()
            if self.ssh:
                self.ssh.close()
            print("✓ [VPS] Koneksi ditutup")
        except Exception as e:
            print(f"⚠ [VPS] Error saat disconnect: {e}")
    
    def upload_database(self, local_db_path, remote_db_path):
        """Upload file database SQLite ke VPS"""
        if not os.path.exists(local_db_path):
            print(f"✗ [VPS] File tidak ditemukan: {local_db_path}")
            return False
        
        try:
            # Pastikan folder di VPS ada
            remote_folder = remote_db_path.rsplit('/', 1)[0]
            try:
                self.sftp.stat(remote_folder)
            except IOError:
                # Folder belum ada, buat folder
                self.sftp.mkdir(remote_folder)
                print(f"✓ [VPS] Folder dibuat: {remote_folder}")
            
            # Upload file
            self.sftp.put(local_db_path, remote_db_path)
            self.last_sync = datetime.now()
            self.sync_count += 1
            
            file_size = os.path.getsize(local_db_path) / 1024  # KB
            print(f"✓ [VPS] Upload berhasil ({file_size:.2f} KB) - #{self.sync_count}")
            return True
            
        except Exception as e:
            print(f"✗ [VPS] Upload gagal: {e}")
            return False
    
    def download_database(self, remote_db_path, local_db_path):
        """Download file database SQLite dari VPS"""
        try:
            self.sftp.get(remote_db_path, local_db_path)
            print(f"✓ [VPS] Download berhasil: {local_db_path}")
            return True
        except Exception as e:
            print(f"✗ [VPS] Download gagal: {e}")
            return False
    
    def sync_database(self, local_db_path, remote_db_path):
        """Sinkronisasi database (upload)"""
        if not self.connect():
            return False
        
        result = self.upload_database(local_db_path, remote_db_path)
        self.disconnect()
        return result
    
    def restore_database(self, remote_db_path, local_db_path):
        """Restore database dari VPS"""
        if not self.connect():
            return False
        
        result = self.download_database(remote_db_path, local_db_path)
        self.disconnect()
        return result
    
    def test_connection(self):
        """Test koneksi ke VPS (untuk debugging)"""
        if self.connect():
            try:
                # Coba baca home directory
                home = self.sftp.listdir('.')
                print(f"✓ [VPS] Folder di home: {home[:3]}...")  # Tampilkan 3 item pertama
                self.disconnect()
                return True
            except Exception as e:
                print(f"✗ [VPS] Tidak bisa akses file: {e}")
                self.disconnect()
                return False
        return False
    
    def get_status(self):
        """Dapatkan status sync"""
        status = {
            'last_sync': self.last_sync,
            'sync_count': self.sync_count,
            'last_sync_str': self.last_sync.strftime('%H:%M:%S') if self.last_sync else 'Belum sync'
        }
        return status


# ============================================================
# HELPER FUNCTION - Untuk digunakan di perpustakaan.py
# ============================================================

def create_vps_sync(vps_host, vps_user, vps_pass):
    """
    Buat instance VPSSyncManager
    
    Contoh:
        sync_manager = create_vps_sync(
            vps_host='202.10.41.179',
            vps_user='root',
            vps_pass='password123'
        )
    """
    return VPSSyncManager(vps_host, vps_user, vps_pass)