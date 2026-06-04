import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BARANG_FILE = os.path.join(BASE_DIR, 'data_barang.json')
PESANAN_FILE = os.path.join(BASE_DIR, 'pesanan.json')
DATA_FILE = os.path.join(BASE_DIR, 'data_koperasi.json')
NOTIFIKASI_FILE = os.path.join(BASE_DIR, 'notifikasi.json')
AKTIVITAS_FILE = os.path.join(BASE_DIR, 'aktivitas.json')
PENJUAL_FILE = os.path.join(BASE_DIR, 'penjual.json')

class Database:
    def __init__(self):
        self.USERS = {'admin': 'admin123', 'pembeli': 'beli123'}
        self.EMAIL_TO_USER = {}
        self.data_barang = []
        self.pesanan = []
        self.notifikasi = []
        self.riwayat = []
        self.data_penjual = []
        self.data_aktivitas = []
        self.cart = {}
        self.otp_storage = {}
        self.produk_belum_dinilai = [
            {"id": 1, "nama": "Roti Aoka", "gambar": "gambar-dan-icon/gambar-roti-aoka.jpeg"},
            {"id": 2, "nama": "Air Mineral Ades", "gambar": "gambar-dan-icon/ades.jpg"},
            {"id": 3, "nama": "Bolpoin", "gambar": "gambar-dan-icon/bulpoin.jpg"},
        ]
        self.penilaian_saya = [
            {"id": 1, "nama": "Roti Aoka", "gambar": "gambar-dan-icon/gambar-roti-aoka.jpeg", "rating": 4, "tanggal": "01-01-2026 11:24"},
            {"id": 2, "nama": "Air Mineral Ades", "gambar": "gambar-dan-icon/ades.jpg", "rating": 5, "tanggal": "20-12-2025 18:22"},
            {"id": 3, "nama": "Bolpoin", "gambar": "gambar-dan-icon/bulpoin.jpg", "rating": 3, "tanggal": "18-12-2025 11:35"},
        ]
        self.CARDS_DATA = [
            {"id": 1, "text": "Rak Makanan Ringan", "icon": "fa-solid fa-cookie", "href": "/admin/denah/makanan_ringan", "width": 300, "height": 160, "left": 100, "top": 80, "image": "images/makanan_ringan/gambar1.jpg"},
            {"id": 2, "text": "Rak Snack", "icon": "fa-solid fa-candy-cane", "href": "/admin/denah/snack", "width": 300, "height": 160, "left": 100, "top": 300, "image": "images/snack/gambar1.jpg"},
            {"id": 3, "text": "Rak Cemilan", "icon": "fa-solid fa-cookie-bite", "href": "/admin/denah/cemilan", "width": 300, "height": 160, "left": 100, "top": 520, "image": "images/cemilan/gambar1.jpg"},
            {"id": 4, "text": "Meja Kasir", "icon": "fa-solid fa-cash-register", "href": "/admin/denah/meja_kasir", "width": 250, "height": 220, "left": 550, "top": 80, "image": "images/meja_kasir/gambar1.jpg"},
            {"id": 5, "text": "Rak Alat Tulis", "icon": "fa-solid fa-book", "href": "/admin/denah/alat_tulis", "width": 200, "height": 300, "left": 950, "top": 80, "image": "images/alat_tulis/gambar1.jpg"},
            {"id": 6, "text": "Rak Makanan", "icon": "fa-solid fa-bowl-food", "href": "/admin/denah/makanan", "width": 200, "height": 300, "left": 950, "top": 420, "image": "images/makanan/gambar1.jpg"},
            {"id": 7, "text": "Rak Minuman", "icon": "fa-solid fa-bottle-water", "href": "/admin/denah/minuman", "width": 180, "height": 650, "left": 1250, "top": 80, "image": "images/minuman/gambar1.jpg"},
        ]
        self.data_koperasi = self.load_koperasi()
        self.load_all()

    def hitung_total_barang(self, barang):
        total = 0
        for b in barang:
            total += b["jumlah"] * b["harga"]
        return total

    def load_data_barang(self):
        if os.path.exists(BARANG_FILE):
            try:
                with open(BARANG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return [
            {"no": 1, "nama": "Roti Aoka", "berat": "60", "satuan": "gr", "stok": 15, "harga": 3000, "kategori": "Makanan", "tanggal_restok": "2025-09-25", "expired": "Mei 2028", "tanggal": "2026-05-06", "gambar": "gambar-dan-icon/gambar-roti-aoka.jpeg", "rating": 5, "emoji": "🍞"},
            {"no": 2, "nama": "Donat", "berat": "50", "satuan": "gr", "stok": 10, "harga": 5000, "kategori": "Makanan", "tanggal_restok": "2025-10-01", "expired": "Mei 2028", "tanggal": "2026-05-05", "gambar": "gambar-dan-icon/donat.jpg", "rating": 4, "emoji": "🍩"},
            {"no": 3, "nama": "Pop Mie", "berat": "85", "satuan": "gr", "stok": 50, "harga": 4000, "kategori": "Makanan", "tanggal_restok": "2025-08-10", "expired": "Mei 2028", "tanggal": "2026-05-03", "gambar": "gambar-dan-icon/pop-mie.png", "rating": 4, "emoji": "🍜"},
            {"no": 4, "nama": "Air Mineral", "berat": "600", "satuan": "ml", "stok": 35, "harga": 3000, "kategori": "Minuman", "tanggal_restok": "2025-11-03", "expired": "Mei 2028", "tanggal": "2026-05-03", "gambar": "gambar-dan-icon/ades.jpg", "rating": 5, "emoji": "💧"},
            {"no": 5, "nama": "Teh Botol", "berat": "350", "satuan": "ml", "stok": 18, "harga": 5000, "kategori": "Minuman", "tanggal_restok": "2025-06-01", "expired": "Desember 2027", "tanggal": "2026-05-10", "gambar": "gambar-dan-icon/teh-botol.png", "rating": 3, "emoji": "🥤"},
            {"no": 6, "nama": "Ultra Milk", "berat": "250", "satuan": "ml", "stok": 12, "harga": 7000, "kategori": "Minuman", "tanggal_restok": "2025-06-01", "expired": "Desember 2027", "tanggal": "2026-05-10", "gambar": "gambar-dan-icon/ultramilk.png", "rating": 4, "emoji": "🧃"},
            {"no": 7, "nama": "Pensil", "berat": "10", "satuan": "gr", "stok": 0, "harga": 2000, "kategori": "Alat Tulis", "tanggal_restok": "2025-06-01", "expired": "-", "tanggal": "2026-05-10", "gambar": "gambar-dan-icon/gambar-pensil.jpeg", "rating": 4, "emoji": "✏️"},
            {"no": 8, "nama": "Buku Tulis", "berat": "100", "satuan": "gr", "stok": 0, "harga": 6000, "kategori": "Alat Tulis", "tanggal_restok": "2025-06-01", "expired": "-", "tanggal": "2026-05-10", "gambar": "gambar-dan-icon/buku-tulis.jpg", "rating": 4, "emoji": "📓"},
            {"no": 9, "nama": "Penghapus", "berat": "20", "satuan": "gr", "stok": 15, "harga": 2000, "kategori": "Alat Tulis", "tanggal_restok": "2025-06-01", "expired": "-", "tanggal": "2026-05-10", "gambar": "gambar-dan-icon/penghapus.png", "rating": 5, "emoji": "🧼"},
            {"no": 10, "nama": "Bolpoin", "berat": "30", "satuan": "gr", "stok": 14, "harga": 8000, "kategori": "Alat Tulis", "tanggal_restok": "2025-06-01", "expired": "-", "tanggal": "2026-05-10", "gambar": "gambar-dan-icon/bulpoin.jpg", "rating": 4, "emoji": "🖋️"}
        ]

    def save_data_barang(self):
        with open(BARANG_FILE, 'w') as f:
            json.dump(self.data_barang, f, indent=4)

    def load_pesanan(self):
        data = []
        if os.path.exists(PESANAN_FILE):
            try:
                with open(PESANAN_FILE, 'r') as f:
                    data = json.load(f)
            except:
                data = self.get_default_pesanan()
        else:
            data = self.get_default_pesanan()
            
        for p in data:
            if "total_awal" not in p:
                p["total_awal"] = self.hitung_total_barang(p["barang"])
            if "total" not in p:
                p["total"] = p["total_awal"]
            if "refund" not in p:
                p["refund"] = 0
        return data

    def get_default_pesanan(self):
        return [
            {"id": "TRX001", "tanggal": "2025-11-15", "pelanggan": "Ahmad Rizki", "metode": "Tunai", "status": "Disiapkan",
             "barang": [{"nama": "Sabun", "jumlah": 2, "harga": 5000, "gambar": "gambar-dan-icon/sabun.jpg"}, {"nama": "Pop Mie", "jumlah": 3, "harga": 4000, "gambar": "gambar-dan-icon/pop-mie.png"}, {"nama": "Air Mineral", "jumlah": 1, "harga": 3000, "gambar": "gambar-dan-icon/ades.jpg"}]},
            {"id": "TRX002", "tanggal": "2025-11-15", "pelanggan": "Siti Nurhazila", "metode": "QRIS", "status": "Disiapkan",
             "barang": [{"nama": "Penggaris", "jumlah": 1, "harga": 4000, "gambar": "gambar-dan-icon/gambar-pensil.jpeg"}, {"nama": "Penghapus", "jumlah": 2, "harga": 3000, "gambar": "gambar-dan-icon/gambar-penghapus.jpeg"}, {"nama": "Pensil", "jumlah": 4, "harga": 10000, "gambar": "gambar-dan-icon/gambar-pensil.jpeg"}]},
            {"id": "TRX003", "tanggal": "2025-11-15", "pelanggan": "Diki Nurhazila", "metode": "Tunai", "status": "Disiapkan",
             "barang": [{"nama": "Penggaris", "jumlah": 1, "harga": 4000, "gambar": "gambar-dan-icon/gambar-pensil.jpeg"}, {"nama": "Penghapus", "jumlah": 2, "harga": 3000, "gambar": "gambar-dan-icon/gambar-penghapus.jpeg"}, {"nama": "Pensil", "jumlah": 4, "harga": 10000, "gambar": "gambar-dan-icon/gambar-pensil.jpeg"}]},
            {"id": "TRX004", "tanggal": "2025-11-15", "pelanggan": "Siti riki", "metode": "QRIS", "status": "Disiapkan",
             "barang": [{"nama": "Penggaris", "jumlah": 1, "harga": 4000, "gambar": "gambar-dan-icon/gambar-pensil.jpeg"}, {"nama": "Penghapus", "jumlah": 2, "harga": 3000, "gambar": "gambar-dan-icon/gambar-penghapus.jpeg"}, {"nama": "Pensil", "jumlah": 4, "harga": 10000, "gambar": "gambar-dan-icon/gambar-pensil.jpeg"}]}
        ]

    def save_pesanan(self):
        with open(PESANAN_FILE, 'w') as f:
            json.dump(self.pesanan, f, indent=4)

    def load_koperasi(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {
            'nama': 'Koperasi Sekolah',
            'deskripsi': 'Koperasi untuk siswa dan guru',
            'alamat': 'Jl. Pendidikan No. 1',
            'telepon': '0341-123456',
            'jam': '07.00 - 15.00',
            'hari': 'Senin - Jumat',
            'logo': 'image/logo_3.png'
        }

    def save_koperasi(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data_koperasi, f)

    def load_notifikasi(self):
        if os.path.exists(NOTIFIKASI_FILE):
            try:
                with open(NOTIFIKASI_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('notifikasi', []), data.get('riwayat', [])
            except:
                pass
        return [
            {"judul": "Pembelian Baru", "isi": "Transaksi #TRX005 oleh Ahmad Rizki senilai 18.000", "waktu": "10 menit lalu", "warna": "biru"},
            {"judul": "Stok Menipis", "isi": "Keripik singkong tersisa 3 unit", "waktu": "15 menit lalu", "warna": "orange"},
            {"judul": "Pembayaran Dikonfirmasi", "isi": "Pembayaran QRIS oleh Putri Amel senilai 10.000 telah divalidasi", "waktu": "20 menit lalu", "warna": "hijau"},
        ], []

    def save_notifikasi(self):
        with open(NOTIFIKASI_FILE, 'w') as f:
            json.dump({
                'notifikasi': self.notifikasi,
                'riwayat': self.riwayat
            }, f, indent=4)

    def tambah_notifikasi(self, judul, isi, warna):
        from datetime import datetime
        waktu_str = datetime.now().strftime("%d-%m-%Y %H:%M")
        self.notifikasi.insert(0, {
            "judul": judul,
            "isi": isi,
            "waktu": waktu_str,
            "warna": warna
        })
        self.save_notifikasi()

    def load_aktivitas(self):
        if os.path.exists(AKTIVITAS_FILE):
            try:
                with open(AKTIVITAS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return [
            {"tipe": "login", "catatan": "Log in system", "status": "Sukses", "admin": "Admin", "waktu": "2026-05-28 08:00"},
            {"tipe": "tambah", "catatan": "Menambahkan pilihan barang: Roti Aoka", "status": "Berhasil", "admin": "Admin", "waktu": "2026-05-28 07:30"},
            {"tipe": "restok", "catatan": "Melakukan restok produk: Air Mineral (+50 unit)", "status": "Berhasil", "admin": "Admin", "waktu": "2026-05-28 07:00"},
            {"tipe": "logout", "catatan": "Log out system", "status": "Sukses", "admin": "Admin", "waktu": "2026-05-27 17:00"},
            {"tipe": "ubah", "catatan": "Mengubah harga: Bolpoin (Rp 3.500 -> Rp 4.000)", "status": "Berhasil", "admin": "Admin", "waktu": "2026-05-27 14:30"},
            {"tipe": "hapus", "catatan": "Menghapus pilihan barang: Kerupuk Bawang", "status": "Berhasil", "admin": "Admin", "waktu": "2026-05-27 11:20"},
            {"tipe": "login", "catatan": "Log in system", "status": "Sukses", "admin": "Admin", "waktu": "2026-05-27 08:00"},
        ]

    def save_aktivitas(self):
        with open(AKTIVITAS_FILE, 'w') as f:
            json.dump(self.data_aktivitas, f, indent=4)

    def tambah_aktivitas(self, tipe, catatan, status="Berhasil", admin="Admin"):
        from datetime import datetime
        waktu_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.data_aktivitas.insert(0, {
            "tipe": tipe,
            "catatan": catatan,
            "status": status,
            "admin": admin,
            "waktu": waktu_str
        })
        self.save_aktivitas()

    def load_penjual(self):
        if os.path.exists(PENJUAL_FILE):
            try:
                with open(PENJUAL_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return [
            {"id": 1, "nama": "Zulfikar Aril", "email": "aril_10@gmail.com", "status": "Aktif", "foto": "profile.png"},
            {"id": 2, "nama": "Nafilah Yasmin", "email": "yasmin18@gmail.com", "status": "Tidak aktif", "foto": "profile.png"},
            {"id": 3, "nama": "Febriyanto", "email": "febri1711@gmail.com", "status": "Aktif", "foto": "profile.png"},
            {"id": 4, "nama": "Shafira Amelia", "email": "shafiramel@gmail.com", "status": "Aktif", "foto": "profile.png"},
        ]

    def save_penjual(self):
        with open(PENJUAL_FILE, 'w') as f:
            json.dump(self.data_penjual, f, indent=4)

    def load_all(self):
        self.data_barang = self.load_data_barang()
        self.pesanan = self.load_pesanan()
        self.notifikasi, self.riwayat = self.load_notifikasi()
        self.data_aktivitas = self.load_aktivitas()
        self.data_penjual = self.load_penjual()

db = Database()
