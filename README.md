# TPC - Fixed Project

Touchless Presentation Controller (TPC) adalah aplikasi desktop Windows untuk memilih file PowerPoint, menjalankan Slide Show, menampilkan kamera, dan mengontrol slide menggunakan gesture tangan.

## Perbaikan utama pada versi ini

Versi ini secara khusus memperbaiki dua workflow yang sebelumnya bermasalah:

1. **Choose File**
   - Tidak lagi memakai `tkinter.filedialog`.
   - Tidak lagi bergantung pada `window.create_file_dialog()` dari pywebview.
   - Menggunakan native Windows `GetOpenFileNameW` melalui `ctypes`.
   - Hanya menerima `.pptx` dan `.ppt`.

2. **Exit**
   - Membersihkan kamera.
   - Menutup PowerPoint jika sedang terbuka.
   - Menghancurkan window pywebview.
   - Memiliki fallback proses agar aplikasi benar-benar berhenti jika native window tidak menutup.

## Struktur

TPC/
├── assets/
│   └── tutorial/
├── camera/
│   ├── __init__.py
│   └── camera_controller.py
├── models/
│   └── hand_landmarker.task   # dibuat otomatis saat kamera pertama kali dijalankan
├── web/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── main.py
├── requirements.txt
└── README.md

## Jalankan

Buka PowerShell pada folder project:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Pastikan PowerPoint desktop terpasang di Windows.

Model MediaPipe akan diunduh otomatis ketika kamera pertama kali dijalankan.

## Catatan

- Project ini ditujukan untuk Windows.
- Jangan memasukkan folder `venv` ke ZIP project.
- Jangan memasukkan `__pycache__` ke ZIP.
