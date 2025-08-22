# Gloria Komputer Inventory System

Sistem inventaris modern untuk toko komputer dengan fitur manajemen stok, riwayat transaksi, dan analisis penjualan.

## Fitur Utama

- 📦 Manajemen Inventaris
  - Pencatatan stok barang
  - Kategori produk
  - Upload foto produk
  - Barcode scanning (upcoming)

- 💰 Transaksi
  - Pencatatan penjualan
  - Riwayat stok masuk/keluar
  - Sistem keranjang belanja
  - Cetak nota (upcoming)

- 📊 Analisis & Laporan
  - Dashboard statistik
  - Laporan penjualan
  - Analisis profit
  - Export data

- 🔒 Keamanan
  - Login system
  - Role-based access
  - Activity logging
  - Backup database

## Teknologi

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: Bootstrap 5, JavaScript
- **Authentication**: Flask-Login
- **ORM**: SQLAlchemy

## Persyaratan Sistem

- Python 3.8+
- pip (Python package installer)
- Virtual environment (recommended)

## Instalasi

1. Clone repository:
```bash
git clone https://github.com/yourusername/Gloria_Komputer_Inventory.git
cd Gloria_Komputer_Inventory
```

2. Buat virtual environment:
```bash
python -m venv venv
```

3. Aktifkan virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r app/requirements.txt
```

5. Inisialisasi database:
```bash
python init_db.py
```

6. Jalankan aplikasi:
```bash
python run.py
```

## Penggunaan

1. Buka browser dan akses `http://localhost:5000`
2. Login dengan kredensial default:
   - Username: admin
   - Password: admin123
3. Ubah password default setelah login pertama

## Struktur Direktori

```
Gloria_Komputer_Inventory/
├── app/
│   ├── src/
│   │   ├── models/        # Database models
│   │   ├── routes/        # Route handlers
│   │   ├── static/        # Static files (CSS, JS, images)
│   │   └── templates/     # HTML templates
│   ├── requirements.txt   # Python dependencies
│   └── README.md         # Project documentation
├── instance/             # Database file
├── migrations/          # Database migrations
├── backup/             # Database backups
├── init_db.py         # Database initialization
├── run.py            # Application entry point
└── wsgi.py          # WSGI entry point
```

## Development

1. Create new branch:
```bash
git checkout -b feature/nama-fitur
```

2. Run tests:
```bash
python -m pytest
```

3. Check code coverage:
```bash
coverage run -m pytest
coverage report
```

## Deployment

### Local Server

1. Set environment variables:
```bash
export FLASK_APP=run.py
export FLASK_ENV=production
```

2. Run with gunicorn:
```bash
gunicorn -b 0.0.0.0:5000 wsgi:app
```

### Railway Deployment

1. Connect to Railway
2. Set environment variables:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `FLASK_ENV=production`

3. Deploy:
```bash
railway up
```

## Backup & Restore

### Manual Backup
```bash
python backup_db.py
```

### Scheduled Backup
Set up in application settings

## Troubleshooting

1. Database errors:
```bash
flask db stamp head
flask db migrate
flask db upgrade
```

2. Clear cache:
```bash
flask clear_cache
```

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Open pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

Untuk bantuan dan pertanyaan:
- Email: support@gloriakomputer.com
- WhatsApp: +62 812-3456-7890

## Authors

- Liavin5115 - Initial work - [GitHub](https://github.com/liavin5115)

## Acknowledgments

- Bootstrap team
- Flask community
- All contributors
