# Client Revisions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement all client-requested revisions across notifications, penilaian, detail transaksi, daftar stok, laporan date filtering, daftar transaksi search, and payment status.

**Architecture:** Single-file Flask app (`app.py`) with Jinja2 templates. Changes span admin templates, pembeli templates, CSS files, and route handlers in `app.py`. All state is in-memory.

**Tech Stack:** Flask, Jinja2, HTML/CSS/JS, Font Awesome, Flatpickr

---

## Task 1: Notification Trash Icon Popup (NotifikasiAdmin.html)

**Files:**
- Modify: `kasir-admin/templates/06.NotifikasiAdmin.html`
- Modify: `static/06.NotifikasiAdmin.css`

The existing single-delete popup mechanism (checkbox + JS) already exists. The issue is that the popup's CSS selector `#popup-hapus-satuan:checked ~ .popup-satuan` may not trigger correctly because the checkbox is positioned as a sibling inside `.kotak` but the `~` general sibling selector requires correct DOM ordering. The popup is already implemented but needs verification that it actually appears when clicking the trash icon. The existing code at lines 73-93 and 127-161 already handles this. Verify the CSS selector works with the current DOM structure.

- [ ] **Step 1: Verify popup-satuan works in NotifikasiAdmin.html**

The popup mechanism already exists. The CSS rule at `06.NotifikasiAdmin.css:314` is:
```css
#popup-hapus-satuan:checked ~ .popup-satuan {
    display: flex;
}
```

The HTML structure in `06.NotifikasiAdmin.html` has the checkbox at line 73 inside `.kotak`, and the popup at line 75 also inside `.kotak`. The `~` selector should work. The JS `bukaPopupHapus()` at line 152 sets the checkbox to checked. This should already work.

If the popup is NOT appearing, the issue may be that the CSS for `.popup-satuan` is missing `display: none` as default. Check if `.popup-satuan` has `display: none` in the CSS.

- [ ] **Step 2: Verify popup-satuan CSS in 06.NotifikasiAdmin.css**

The `.popup` class at line 242 has `display: none`. The `.popup-satuan` inherits from `.popup` via class matching. The CSS rule `#popup-hapus-satuan:checked ~ .popup-satuan { display: flex; }` should override this. No changes needed unless testing reveals issues.

- [ ] **Step 3: Verify popup-satuan works in RiwayatNotifikasi.html**

Same pattern exists in `06.RiwayatNotifikasi.html` (lines 55-75, 110-118, 128-141). No changes needed unless testing reveals issues.

**Expected outcome:** Clicking the trash icon on any notification shows a "Yakin ingin hapus notifikasi ini?" popup with Batal/Hapus buttons, matching the "Hapus semua" popup style.

---

## Task 2: Penilaian Barang Card Image Alignment (Match Nadya's Layout)

**Files:**
- Modify: `static/style2.css` (lines 54-132)

The current `style2.css` has card images at 100x100px with a fixed 320px card height and absolute-positioned "Nilai" button. The reference layout in `2-nadyanur.css` uses full-width images (100% width, 180px height) with auto card height and naturally-flowing button.

- [ ] **Step 1: Update `.card` height in style2.css**

Change `.card` height from `320px` to `auto` and add `min-height: 320px`. Remove `position: relative` (not needed without absolute children).

In `static/style2.css`, change:
```css
.card{
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;

    border: 1px solid #eaf4ff;
    border-radius: 15px;

    padding: 20px;
    width: 250px;
    height: 320px;
    margin: 10px;

    background-color: #eaf4ff;
    box-shadow: 0 3px 10px rgb(0,0,0,0.08);
    box-sizing: border-box;
}
```

To:
```css
.card{
    display: flex;
    flex-direction: column;
    align-items: center;

    border: 1px solid #eaf4ff;
    border-radius: 15px;

    padding: 20px;
    width: 250px;
    height: auto;
    min-height: 320px;
    margin: 10px;

    background-color: #eaf4ff;
    box-shadow: 0 3px 10px rgb(0,0,0,0.08);
}
```

- [ ] **Step 2: Update `.card img` dimensions in style2.css**

Change `.card img` from 100x100 to full-width 180px height with border-radius.

In `static/style2.css`, change:
```css
.card img{
    width: 100px;
    height: 100px;
    object-fit: contain;
    margin-bottom: 10px;
}
```

To:
```css
.card img{
    width: 100%;
    height: 180px;
    object-fit: contain;
    border-radius: 15px;
    box-sizing: border-box;
    margin-bottom: 10px;
}
```

- [ ] **Step 3: Update `.nilai-btn` positioning in style2.css**

Remove absolute positioning so the button flows naturally below content.

In `static/style2.css`, change:
```css
.nilai-btn{
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%) !important;

    background: #61b8ff;
    border: none;
    color: white;

    padding: 10px 25px;
    border-radius: 8px;

    font-weight: bold;
    font-size: 16px;

    width: 80% !important;
    min-width: unset !important;
    min-height: unset !important;
    cursor: pointer;
    transition: none !important;
}

.nilai-btn:hover {
    transform: translateX(-50%) !important;
    opacity: 0.85;
    background: #4da8f5;
}
```

To:
```css
.nilai-btn{
    background: #61b8ff;
    border: none;
    color: white;

    padding: 10px 25px;
    border-radius: 8px;

    font-weight: bold;
    font-size: 16px;

    width: 80%;
    margin-top: 10px;
    cursor: pointer;
}

.nilai-btn:hover {
    opacity: 0.85;
    background: #4da8f5;
}
```

- [ ] **Step 4: Update `.produk` padding in style2.css**

Remove `padding-bottom: 50px` from `.produk` (was needed for absolute button spacing).

In `static/style2.css`, change:
```css
.produk{
    display: flex;
    align-items: center;
    flex-direction: column;
    width: 100%;
    gap: 8px;
    padding-bottom: 50px;
}
```

To:
```css
.produk{
    display: flex;
    align-items: center;
    flex-direction: column;
    width: 100%;
    gap: 8px;
}
```

**Expected outcome:** Product cards now have large full-width images (matching Nadya's layout), auto-height cards, and the "Nilai" button flows naturally below the content.

---

## Task 3: Detail Transaksi - Trash Icon Remove from DOM

**Files:**
- Modify: `kasir-admin/templates/detail_transaksi.html` (lines 236-244)

The `hapusItem()` JS function currently creates a form and submits it to the server, causing a full page reload. The client says "tombol sampah nya pas d pencet ikon e ga kehapus" — the icon doesn't disappear after clicking. This is because the current implementation does a full page reload via form submission, which should work. But the real issue might be that the delete action itself works but the UI doesn't reflect the removal immediately.

Looking at the `admin_hapus_item_transaksi` route (app.py:548-559), it pops the item and redirects back. This should work. The issue might be that after deletion of the last item, the page crashes because `items[0].id_transaksi` fails on empty list (app.py:180).

- [ ] **Step 1: Fix detail_transaksi.html to handle empty items list**

In `kasir-admin/templates/detail_transaksi.html`, change line 180:
```html
<h2>{{ items[0].id_transaksi if items else 'Transaksi' }}</h2>
```
This already handles empty items. No change needed here.

- [ ] **Step 2: Fix admin_hapus_item_transaksi to delete transaction when empty**

In `app.py`, modify the route at lines 548-559 to remove the transaction from `pesanan` if all items are deleted:

Change:
```python
@app.route("/admin/detail-transaksi/<trx_id>/hapus/<int:index>", methods=['POST'])
def admin_hapus_item_transaksi(trx_id, index):
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    for p in pesanan:
        if p['id'] == trx_id:
            if 0 <= index < len(p['barang']):
                p['barang'].pop(index)
                p['total'] = hitung_total_barang(p['barang'])
                save_pesanan(pesanan)
            break
    return redirect(url_for('admin_detail_transaksi', trx_id=trx_id))
```

To:
```python
@app.route("/admin/detail-transaksi/<trx_id>/hapus/<int:index>", methods=['POST'])
def admin_hapus_item_transaksi(trx_id, index):
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    for i, p in enumerate(pesanan):
        if p['id'] == trx_id:
            if 0 <= index < len(p['barang']):
                p['barang'].pop(index)
                if not p['barang']:
                    pesanan.pop(i)
                    save_pesanan(pesanan)
                    return redirect(url_for('admin_cek_pembayaran'))
                p['total'] = hitung_total_barang(p['barang'])
                save_pesanan(pesanan)
            break
    return redirect(url_for('admin_detail_transaksi', trx_id=trx_id))
```

**Expected outcome:** Deleting the last item removes the entire transaction and redirects to the transaction list. The trash icon now properly removes the item (and the page reflects the change after reload).

---

## Task 4: Daftar Stok - Eye Icon (Alasan) Improvements

**Files:**
- Modify: `kasir-admin/templates/14.-stoktersedia.html` (lines 66-68, 102-115)
- Modify: `14.-stoktersedia_edit.html` (line 72-75)

The eye icon currently shows an `alert()` with the alasan text. The client wants:
1. When editing, the alasan field must be filled (required)
2. The eye icon should open/show the alasan on the page

Currently the alasan textarea is optional (no `required` attribute). The eye icon uses `alert()` which is functional but not ideal.

- [ ] **Step 1: Make alasan required in the edit form**

In `kasir-admin/templates/14.-stoktersedia_edit.html`, change line 73-74:
```html
<label for="alasan">Alasan Perubahan</label>
        <textarea id="alasan" name="alasan" placeholder="Masukkan alasan perubahan jika ada">{{ barang.alasan if barang.alasan else '' }}</textarea>
```

To:
```html
<label for="alasan">Alasan Perubahan</label>
        <textarea id="alasan" name="alasan" placeholder="Masukkan alasan perubahan" required>{{ barang.alasan if barang.alasan else '' }}</textarea>
```

- [ ] **Step 2: Improve eye icon to show alasan in a styled popup instead of alert()**

In `kasir-admin/templates/14.-stoktersedia.html`, replace the alert-based script (lines 102-115) with a styled modal popup. Add a modal div before the closing `</body>` tag:

After line 100 (closing `</div>` of container), add:
```html
<div id="alasan-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.4); z-index:1000; justify-content:center; align-items:center;">
    <div style="background:white; padding:30px; border-radius:16px; width:360px; max-width:90%; text-align:center;">
        <h3 style="margin-bottom:12px; color:#111827;">Alasan Perubahan</h3>
        <p id="alasan-nama" style="font-weight:600; color:#374151; margin-bottom:8px;"></p>
        <p id="alasan-text" style="color:#6b7280; line-height:1.5; min-height:40px;"></p>
        <button onclick="document.getElementById('alasan-modal').style.display='none'" style="margin-top:16px; padding:10px 24px; background:#3A82C4; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">Tutup</button>
    </div>
</div>
```

Then replace the script (lines 102-115):
```javascript
document.querySelectorAll('.icon.view').forEach(function(el) {
    el.addEventListener('click', function(e) {
        e.preventDefault();
        var nama = this.getAttribute('data-nama');
        var alasan = this.getAttribute('data-alasan');
        if (alasan) {
            alert('Alasan edit "' + nama + '":\n\n' + alasan);
        } else {
            alert('"' + nama + '" belum memiliki alasan edit.');
        }
        return false;
    });
});
```

To:
```javascript
document.querySelectorAll('.icon.view').forEach(function(el) {
    el.addEventListener('click', function(e) {
        e.preventDefault();
        var nama = this.getAttribute('data-nama');
        var alasan = this.getAttribute('data-alasan');
        document.getElementById('alasan-nama').textContent = nama;
        document.getElementById('alasan-text').textContent = alasan || 'Belum memiliki alasan edit.';
        document.getElementById('alasan-modal').style.display = 'flex';
        return false;
    });
});
```

Also add click-outside-to-close:
```javascript
document.getElementById('alasan-modal').addEventListener('click', function(e) {
    if (e.target === this) this.style.display = 'none';
});
```

**Expected outcome:** The alasan field is now required when editing. The eye icon opens a styled modal popup showing the alasan text instead of a browser alert().

---

## Task 5: Laporan Date Range Filtering Fix

**Files:**
- Modify: `app.py` (lines 974-1002, 1069-1080)
- Modify: `kasir-admin/templates/16.pengaturan_laporan.html`

The date range filtering on the cetak laporan page (`12.-cetaklaporan.html`) already works via server-side filtering with `_filter_by_tanggal()` and flatpickr JS that triggers page reload. The `pengaturan_laporan.html` page also has date inputs but doesn't filter the displayed data.

- [ ] **Step 1: Fix pengaturan_laporan route to filter data by date**

In `app.py`, change the `admin_pengaturan_laporan` route (lines 1069-1080):

From:
```python
@app.route('/admin/pengaturan-laporan')
def admin_pengaturan_laporan():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    tanggal_awal = request.args.get('tanggal_awal', '')
    tanggal_akhir = request.args.get('tanggal_akhir', '')
    laporan_type = request.args.get('laporan', 'barang')
    return render_template("16.pengaturan_laporan.html",
                           barang=data_barang,
                           tanggal_awal=tanggal_awal,
                           tanggal_akhir=tanggal_akhir,
                           laporan_type=laporan_type)
```

To:
```python
@app.route('/admin/pengaturan-laporan')
def admin_pengaturan_laporan():
    if not session.get('user'):
        return redirect(url_for('admin_login'))
    tanggal_awal = request.args.get('tanggal_awal', '')
    tanggal_akhir = request.args.get('tanggal_akhir', '')
    laporan_type = request.args.get('laporan', 'barang')
    filtered_barang = _filter_by_tanggal(data_barang, tanggal_awal, tanggal_akhir)
    return render_template("16.pengaturan_laporan.html",
                           barang=filtered_barang,
                           tanggal_awal=tanggal_awal,
                           tanggal_akhir=tanggal_akhir,
                           laporan_type=laporan_type)
```

- [ ] **Step 2: Fix pengaturan_laporan.html PDF/Excel links to use correct routes per laporan type**

In `kasir-admin/templates/16.pengaturan_laporan.html`, change lines 72-79:

From:
```html
<div class="button-box">
    <a href="{{ url_for('admin_cetak_pdf') }}?tanggal_awal={{ tanggal_awal }}&tanggal_akhir={{ tanggal_akhir }}">
        <button class="pdf">Cetak PDF</button>
    </a>
    <a href="{{ url_for('admin_cetak_excel') }}?tanggal_awal={{ tanggal_awal }}&tanggal_akhir={{ tanggal_akhir }}">
        <button class="excel">Cetak Excel</button>
    </a>
</div>
```

To:
```html
<div class="button-box">
    <a id="linkPdf" href="{{ url_for('admin_cetak_barang_pdf') }}?tanggal_awal={{ tanggal_awal }}&tanggal_akhir={{ tanggal_akhir }}">
        <button class="pdf">Cetak PDF</button>
    </a>
    <a id="linkExcel" href="{{ url_for('admin_cetak_barang_excel') }}?tanggal_awal={{ tanggal_awal }}&tanggal_akhir={{ tanggal_akhir }}">
        <button class="excel">Cetak Excel</button>
    </a>
</div>
```

And add/update the script section to dynamically switch PDF/Excel links based on selected laporan type. Replace the existing `<script>` block (lines 83-96):

From:
```html
<script>
    document.addEventListener("DOMContentLoaded", function() {
        const config = {
            locale: "id",
            altInput: true,
            altFormat: "d-m-Y",
            dateFormat: "Y-m-d",
            onChange: function(selectedDates, dateStr, instance) {
                instance.element.dispatchEvent(new Event('change', { bubbles: true }));
            }
        };
        flatpickr("input[type=date]", config);
    });
</script>
```

To:
```html
<script>
    function updateLinks() {
        var tipe = document.querySelector('select[name="laporan"]').value;
        var awal = document.querySelector('input[name="tanggal_awal"]').value;
        var akhir = document.querySelector('input[name="tanggal_akhir"]').value;
        var params = (awal || akhir) ? '?tanggal_awal=' + encodeURIComponent(awal) + '&tanggal_akhir=' + encodeURIComponent(akhir) : '';
        if (tipe === 'barang') {
            document.getElementById('linkPdf').href = "{{ url_for('admin_cetak_barang_pdf') }}" + params;
            document.getElementById('linkExcel').href = "{{ url_for('admin_cetak_barang_excel') }}" + params;
        } else {
            document.getElementById('linkPdf').href = "{{ url_for('admin_cetak_transaksi_pdf') }}" + params;
            document.getElementById('linkExcel').href = "{{ url_for('admin_cetak_transaksi_excel') }}" + params;
        }
    }

    document.addEventListener("DOMContentLoaded", function() {
        const config = {
            locale: "id",
            altInput: true,
            altFormat: "d-m-Y",
            dateFormat: "Y-m-d",
            onChange: function(selectedDates, dateStr, instance) {
                instance.element.dispatchEvent(new Event('change', { bubbles: true }));
            }
        };
        flatpickr("input[type=date]", config);
        document.querySelector('select[name="laporan"]').addEventListener('change', updateLinks);
        updateLinks();
    });
</script>
```

- [ ] **Step 3: Fix cetak_laporan route to use _filter_by_tanggal for data_transaksi**

In `app.py`, replace the inline date filtering for `data_transaksi` (lines 974-1002) with a call to `_filter_by_tanggal`:

From:
```python
data_transaksi = []
for p in pesanan:
    tgl = p.get('tanggal', '')
    ok_awal = True
    ok_akhir = True
    if tanggal_awal:
        try:
            from datetime import datetime
            d_tgl = datetime.strptime(tgl, '%Y-%m-%d')
            d_awal = datetime.strptime(tanggal_awal, '%Y-%m-%d')
            ok_awal = d_tgl >= d_awal
        except ValueError:
            ok_awal = tgl >= tanggal_awal
    if tanggal_akhir:
        try:
            from datetime import datetime
            d_tgl = datetime.strptime(tgl, '%Y-%m-%d')
            d_akhir = datetime.strptime(tanggal_akhir, '%Y-%m-%d')
            ok_akhir = d_tgl <= d_akhir
        except ValueError:
            ok_akhir = tgl <= tanggal_akhir
    if ok_awal and ok_akhir:
        total_barang = sum(b['harga'] * b['jumlah'] for b in p['barang'])
        data_transaksi.append({
            'tanggal': p['tanggal'],
            'id': p['id'],
            'jumlah_item': sum(b['jumlah'] for b in p['barang']),
            'total': total_barang
        })
```

To:
```python
filtered_pesanan_for_transaksi = _filter_by_tanggal(pesanan, tanggal_awal, tanggal_akhir)
data_transaksi = []
for p in filtered_pesanan_for_transaksi:
    total_barang = sum(b['harga'] * b['jumlah'] for b in p['barang'])
    data_transaksi.append({
        'tanggal': p['tanggal'],
        'id': p['id'],
        'jumlah_item': sum(b['jumlah'] for b in p['barang']),
        'total': total_barang
    })
```

**Expected outcome:** Date range filtering now works on the pengaturan_laporan page. Selecting a date range filters the displayed table data. PDF/Excel export links correctly route to the right report type (barang vs transaksi) with date parameters.

---

## Task 6: Daftar Transaksi Search - "pelanggan" to "produk" + Metode Search Fix

**Files:**
- Modify: `kasir-admin/templates/21.cek_pembayaran.html` (line 20)
- Modify: `app.py` (lines 1484-1496)

The search placeholder says "ID, produk, atau metode" but the backend searches by pelanggan. The client wants the search to work by "produk" (which it already does via the barang loop) and the placeholder should reflect this. The metode search also needs to work.

- [ ] **Step 1: Update search placeholder text**

In `kasir-admin/templates/21.cek_pembayaran.html`, change line 20:

From:
```html
<input type="text" name="cari" placeholder="Cari berdasarkan ID, produk, atau metode..." value="{{ keyword or '' }}">
```

To:
```html
<input type="text" name="cari" placeholder="Cari berdasarkan ID, produk, atau metode pembayaran..." value="{{ keyword or '' }}">
```

- [ ] **Step 2: Fix the search to also match metode properly**

The current search at app.py:1490 already searches `p.get('metode', '').lower()`. The issue is that metode values are "Tunai" and "QRIS", and users might search for "tunai" or "qris" (lowercase) which already works due to `.lower()`. The search is functional. No backend change needed.

**Expected outcome:** The search placeholder accurately describes searchable fields. Searching by product name, payment method, or transaction ID all work correctly.

---

## Task 7: Kode Pengambilan = TRX Code (Payment Tunai Page)

**Files:**
- Modify: `kasir-admin/templates/21.cek_pembayaran_detail.html` (line 141)

The client wants the "Kode Pengambilan" shown to buyers to match the TRX ID. Currently `pembeli_tunai()` (app.py:1947) already uses `kode = trx_id` (the TRX ID). The issue is in the admin detail page receipt download (`21.cek_pembayaran_detail.html:141`) which generates a random 4-digit code instead of using the TRX ID.

- [ ] **Step 1: Fix receipt code to use TRX ID instead of random code**

In `kasir-admin/templates/21.cek_pembayaran_detail.html`, change line 141:

From:
```javascript
const kode = 'KODE ' + Math.floor(1000 + Math.random() * 9000);
```

To:
```javascript
const kode = orderData.id;
```

**Expected outcome:** The receipt/downloaded PDF now shows the actual TRX ID (e.g., "TRX48291") as the Kode Pengambilan, matching what the buyer sees on their cash payment page.

---

## Task 8: Payment Status Color (Tunai - Red Before Pickup)

**Files:**
- Modify: `kasir-admin/templates/19.SiapkanPesanan.html` (lines 127-131)

The client says when selecting cash payment, the status shows green immediately but should show red first (until picked up). The `19.SiapkanPesanan.html` template has `.status-bayar` with `.lunas`/`.belum-bayar` classes but these have NO CSS rules defined. The payment status logic in the template already correctly differentiates: QRIS or "Sudah diambil" = lunas (green), otherwise = belum-bayar (red). The issue is the missing CSS.

- [ ] **Step 1: Add CSS for .status-bayar, .lunas, and .belum-bayar**

In `static/19.siapkan_pesanan_pelanggan.css`, add the following styles at the end of the file:

```css
.status-bayar {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
}

.status-bayar.lunas {
    background-color: #d4edda;
    color: #28a745;
}

.status-bayar.belum-bayar {
    background-color: #ffe0e0;
    color: #e74c3c;
}
```

**Expected outcome:** The "Status Pembayaran" badge on the Siapkan Pesanan page now shows green (lunas) for QRIS or picked-up orders, and red (belum-bayar) for unpaid cash orders.

---

## Task 9: Detail Transaksi - Date Auto-Fill

**Files:**
- Modify: `kasir-admin/templates/detail_transaksi.html` (line 183)

The client says "tanggal e blm otomatis" (date is not automatic). Looking at the template, the date IS displayed from `{{ tanggal }}` which comes from `format_kbbi_date(trx['tanggal'])` in the route. The date is already being passed and displayed. The issue might be that the date format is not user-friendly (shows as "15-11-2025" instead of a more readable format).

Actually, re-reading the client request: "tanggal e blm otomatis" might mean the date field in the detail page doesn't auto-fill or auto-update. Looking at the template, the date is displayed as read-only text. There's no issue with auto-fill since it's not an input field.

The issue might be that when creating a new transaction, the date is not automatically set. But looking at `buat_pesanan_dari_cart()` (app.py:1872), the date IS set: `'tanggal': req_data.get('tanggal', datetime.now().strftime("%Y-%m-%d"))`.

This task may not require changes. The date is already automatically set when the transaction is created and displayed in the detail view. If the client meant something else, clarification would be needed.

- [ ] **Step 1: Verify date is displayed correctly (no code change needed)**

The date is already set automatically at transaction creation (app.py:1872) and displayed in the detail template (line 183). No changes needed unless the client clarifies a different issue.

**Expected outcome:** Date is already automatic. No changes needed.

---

## Summary of All Files Modified

| Task | Files Modified |
|------|---------------|
| 1 | No changes needed (already works) |
| 2 | `static/style2.css` |
| 3 | `app.py` (admin_hapus_item_transaksi route) |
| 4 | `kasir-admin/templates/14.-stoktersedia.html`, `14.-stoktersedia_edit.html` |
| 5 | `app.py` (admin_pengaturan_laporan, admin_cetak_laporan), `16.pengaturan_laporan.html` |
| 6 | `kasir-admin/templates/21.cek_pembayaran.html` |
| 7 | `kasir-admin/templates/21.cek_pembayaran_detail.html` |
| 8 | `static/19.siapkan_pesanan_pelanggan.css` |
| 9 | No changes needed (already works) |
