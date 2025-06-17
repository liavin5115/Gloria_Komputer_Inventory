from app.src import create_app, db
from app.src.models.inventory import Inventory
from app.src.models.user import User

def init_db():
    app = create_app()
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("Database tables created successfully")
            
            # Add admin user if no users exist
            if not User.query.first():
                admin = User(
                    username='admin',
                    name='Administrator',
                    role='admin',
                    is_active=True
                )
                admin.set_password('admin123')  # Change this in production!
                db.session.add(admin)
                db.session.commit()
                print("Created default admin user (username: admin)")
              # Add sample data if database is empty
            if not Inventory.query.first():
                sample_data = [
                    ("AMD Ryzen 5 5600X", "Processor AMD Ryzen 5 6-Core", 10, 3200000, "Processor"),
                    ("Intel Core i5-12400F", "Processor Intel Core i5 12th Gen", 8, 2800000, "Processor"),
                    ("NVIDIA RTX 3060", "VGA Card NVIDIA GeForce RTX 3060 12GB", 5, 5500000, "VGA"),
                    ("RX 6600 XT", "VGA Card AMD Radeon RX 6600 XT 8GB", 4, 4800000, "VGA"),
                    ("Kingston Fury 16GB", "RAM DDR4 3200MHz RGB", 15, 850000, "RAM"),
                    ("Corsair Vengeance 32GB", "RAM DDR4 3600MHz", 12, 1600000, "RAM"),
                    ("Samsung 970 EVO 1TB", "SSD NVMe M.2", 20, 1800000, "Storage"),
                    ("WD Blue 2TB", "HDD SATA 7200RPM", 25, 800000, "Storage"),
                    ("ROG STRIX B550-F", "Motherboard AMD AM4", 7, 2300000, "Motherboard"),
                    ("MSI B660M", "Motherboard Intel LGA1700", 6, 2100000, "Motherboard"),
                    ("Corsair RM750x", "Power Supply 750W Gold", 10, 1750000, "PSU"),
                    ("NZXT H510", "ATX Mid Tower Case", 8, 1200000, "Case"),
                    ("Arctic Freezer 34", "CPU Air Cooler", 12, 600000, "Cooling"),
                    ("Logitech G Pro X", "Gaming Keyboard Mechanical", 15, 1500000, "Peripheral"),
                    ("Razer DeathAdder V2", "Gaming Mouse", 20, 800000, "Peripheral"),
                    ("ViewSonic VX2758", "27\" Gaming Monitor 144Hz", 6, 3500000, "Monitor"),
                    ("Crucial P2 500GB", "SSD NVMe M.2", 18, 800000, "Storage"),
                    ("G.Skill Ripjaws 8GB", "RAM DDR4 3000MHz", 22, 450000, "RAM"),
                    ("ASRock B450M", "Motherboard AMD AM4", 9, 1200000, "Motherboard"),
                    ("Cooler Master TD300", "Micro-ATX Case", 7, 800000, "Case"),
                    ("be quiet! Pure Rock 2", "CPU Air Cooler", 14, 500000, "Cooling"),
                    ("Seagate Barracuda 1TB", "HDD SATA 7200RPM", 30, 600000, "Storage"),
                    ("EVGA 600W", "Power Supply 600W Bronze", 12, 800000, "PSU"),
                    ("AMD Ryzen 7 5800X", "Processor AMD Ryzen 7 8-Core", 6, 4500000, "Processor"),
                    ("Intel Core i7-12700K", "Processor Intel Core i7 12th Gen", 5, 5200000, "Processor"),
                    ("RTX 3070 Ti", "VGA Card NVIDIA GeForce RTX 3070 Ti 8GB", 4, 8500000, "VGA"),
                    ("RX 6700 XT", "VGA Card AMD Radeon RX 6700 XT 12GB", 3, 7200000, "VGA"),
                    ("Corsair 4000D", "ATX Mid Tower Case Airflow", 10, 1400000, "Case"),
                    ("MSI MAG B660", "Motherboard Intel LGA1700", 8, 2400000, "Motherboard"),
                    ("Samsung 980 PRO 2TB", "SSD NVMe M.2 Gen4", 12, 3500000, "Storage"),
                    ("G.Skill Trident Z 32GB", "RAM DDR4 3600MHz RGB", 8, 1800000, "RAM"),
                    ("Seasonic Focus GX-850", "Power Supply 850W Gold", 6, 2100000, "PSU"),
                    ("ARCTIC Liquid Freezer II", "CPU AIO Liquid Cooler 240mm", 7, 1600000, "Cooling"),
                    ("LG 27GL850", "27\" Gaming Monitor 1440p 144Hz", 4, 5500000, "Monitor"),
                    ("Corsair K70 RGB", "Mechanical Gaming Keyboard", 10, 1800000, "Peripheral"),
                    ("Logitech G502 HERO", "Gaming Mouse 16K DPI", 15, 900000, "Peripheral"),
                    ("Intel Core i9-12900K", "Processor Intel Core i9 12th Gen", 3, 8500000, "Processor"),
                    ("AMD Ryzen 9 5950X", "Processor AMD Ryzen 9 16-Core", 2, 9000000, "Processor"),
                    ("RTX 4080", "VGA Card NVIDIA GeForce RTX 4080 16GB", 2, 15000000, "VGA"),
                    ("RX 6800 XT", "VGA Card AMD Radeon RX 6800 XT 16GB", 3, 11000000, "VGA"),
                    ("Lian Li O11 Dynamic", "Premium ATX Case", 5, 2200000, "Case"),
                    ("ASUS ROG CROSSHAIR", "Premium AMD X570 Motherboard", 4, 5500000, "Motherboard"),
                    ("Crucial P5 2TB", "SSD NVMe M.2 Gen3", 10, 2800000, "Storage"),
                    ("Corsair Dominator 64GB", "RAM DDR4 3600MHz Platinum", 4, 3500000, "RAM"),
                    ("be quiet! Dark Power 1000W", "Power Supply 1000W Titanium", 5, 3800000, "PSU"),
                    ("NZXT Kraken X73", "CPU AIO Liquid Cooler 360mm RGB", 6, 2800000, "Cooling"),
                    ("Samsung Odyssey G7", "32\" Curved Gaming Monitor 240Hz", 3, 9500000, "Monitor"),
                    ("Razer Huntsman Elite", "Premium Gaming Keyboard", 8, 2500000, "Peripheral"),
                    ("Logitech G Pro X Superlight", "Wireless Gaming Mouse", 12, 1800000, "Peripheral"),
                    ("Seagate FireCuda 4TB", "SSHD Hybrid Drive", 8, 2000000, "Storage")
                ]
                
                for product_name, desc, qty, price, category in sample_data:
                    item = Inventory(
                        product_name=product_name,
                        description=desc,
                        quantity=qty,
                        price=price,
                        category=category
                    )
                    db.session.add(item)
                db.session.commit()
                print("Added 50 sample products to inventory")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise

if __name__ == "__main__":
    init_db()
