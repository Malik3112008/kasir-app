KASIR APP V2 - Aplikasi Koperasi Siswa (INOMART)
==================================================

Aplikasi kasir gabungan untuk admin dan pembeli.
HTML dan CSS persis dari folder Aplikasi Kasir dan PROYEK RPL 3.

CARA MENJALANKAN:

WINDOWS:
  1. Buka folder kasir-app-v2
  2. Double-click setup.bat (pertama kali saja)
  3. Double-click run.bat untuk menjalankan aplikasi
  4. Buka browser: http://localhost:5000

LINUX/MAC:
  1. Buka terminal, masuk ke folder kasir-app-v2
  2. Jalankan: bash setup.sh (pertama kali saja)
  3. Jalankan: bash run.sh untuk menjalankan aplikasi
  4. Buka browser: http://localhost:5000

FISH SHELL:
  Jalankan: fish run.fish

LOGIN ADMIN:
  Username: admin
  Password: admin123

FOLDER STRUCTURE:
  kasir-app-v2/
  ├── app.py                    # Kode utama aplikasi (gabungan)
  ├── run.bat / run.sh          # Script jalankan
  ├── setup.bat / setup.sh      # Setup venv
  ├── README.txt                # File ini
  ├── static/                   # CSS, gambar, icon (gabungan)
  ├── kasir-admin/templates/    # Template HTML untuk admin
  └── kasir-pembeli/templates/  # Template HTML untuk pembeli

HALAMAN UTAMA:
  /                       - Pilih Admin atau Pembeli

HALAMAN ADMIN (awali dengan /admin):
  /admin                  - Beranda awal admin
  /admin/login            - Login admin
  /admin/register         - Register akun baru
  /admin/forgot           - Lupa password
  /admin/verify           - Verifikasi OTP
  /admin/reset            - Reset password
  /admin/dashboard        - Dashboard admin
  /admin/notifikasi       - Notifikasi
  /admin/riwayat          - Riwayat notifikasi
  /admin/kelola_akun_penjual - Kelola akun penjual
  /admin/pengisian_barang - Pengisian barang
  /admin/cetak_laporan    - Cetak laporan
  /admin/laporan_penjualan - Laporan penjualan
  /admin/siapkan-pesanan  - Siapkan pesanan
  /admin/pengaturan       - Pengaturan koperasi
  /admin/denah            - Denah koperasi (admin edit mode)
  /admin/logout           - Logout

HALAMAN PEMBELI (awali dengan /pembeli):
  /pembeli                - Kategori alat tulis (home pembeli)
  /pembeli/keranjang      - Keranjang belanja
  /pembeli/pilih-pembayaran - Pilih metode pembayaran
  /pembeli/tunai          - Pembayaran tunai
  /pembeli/qris           - Pembayaran QRIS
  /pembeli/struk          - Struk pembayaran
  /pembeli/pesanan        - Status pesanan
  /pembeli/status         - Detail pesanan (dikemas)
  /pembeli/penilaian      - Penilaian produk
  /pembeli/rating         - Input rating
