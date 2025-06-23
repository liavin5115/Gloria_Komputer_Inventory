from app.src import create_app, db
from app.src.models.inventory import Inventory
from app.src.models.user import User
import random
import os

# Ensure /data directory exists if using Railway volume
db_path = os.environ.get('DATABASE_URL', '/data/inventory.db')
data_dir = os.path.dirname(db_path)
os.makedirs(data_dir, exist_ok=True)

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
                admin.set_password('Admin123!')  # Meets all password policy requirements
                db.session.add(admin)
                db.session.commit()
                print("Created default admin user (username: admin)")
              # Add sample data if database is empty
            if not Inventory.query.first():
                # Product data pools
                processors = [
                    ("AMD Ryzen 9 7950X", "16-Core Processor", (8500000, 9500000)),
                    ("AMD Ryzen 7 7700X", "8-Core Processor", (5500000, 6500000)),
                    ("AMD Ryzen 5 7600X", "6-Core Processor", (3500000, 4500000)),
                    ("Intel Core i9-13900K", "24-Core Processor", (9000000, 10000000)),
                    ("Intel Core i7-13700K", "16-Core Processor", (6000000, 7000000)),
                    ("Intel Core i5-13600K", "14-Core Processor", (4000000, 5000000))
                ]
                
                graphics_cards = [
                    ("NVIDIA RTX 4090", "24GB GDDR6X Graphics Card", (25000000, 30000000)),
                    ("NVIDIA RTX 4080", "16GB GDDR6X Graphics Card", (18000000, 20000000)),
                    ("NVIDIA RTX 4070 Ti", "12GB GDDR6X Graphics Card", (12000000, 15000000)),
                    ("AMD RX 7900 XTX", "24GB GDDR6 Graphics Card", (20000000, 23000000)),
                    ("AMD RX 7900 XT", "20GB GDDR6 Graphics Card", (15000000, 18000000)),
                    ("AMD RX 7800 XT", "16GB GDDR6 Graphics Card", (10000000, 12000000))
                ]
                
                ram_kits = [
                    ("Corsair Vengeance RGB", "32GB DDR5-6000", (2500000, 3000000)),
                    ("G.Skill Trident Z5", "32GB DDR5-6400", (2800000, 3300000)),
                    ("Kingston Fury Beast", "32GB DDR5-5600", (2200000, 2700000)),
                    ("Corsair Dominator", "64GB DDR5-6000", (5000000, 6000000)),
                    ("G.Skill Ripjaws S5", "32GB DDR5-5200", (2000000, 2500000)),
                    ("Crucial RAM", "16GB DDR4-3200", (800000, 1000000))
                ]
                
                storage = [
                    ("Samsung 990 PRO", "2TB NVMe SSD", (3500000, 4000000)),
                    ("WD Black SN850X", "2TB NVMe SSD", (3200000, 3700000)),
                    ("Crucial P5 Plus", "1TB NVMe SSD", (1800000, 2200000)),
                    ("Seagate FireCuda", "2TB NVMe SSD", (3000000, 3500000)),
                    ("Samsung 870 EVO", "1TB SATA SSD", (1500000, 1800000)),
                    ("WD Blue", "2TB HDD 7200RPM", (800000, 1000000))
                ]
                
                motherboards = [
                    ("ASUS ROG X670E", "AMD AM5 Motherboard", (7000000, 8000000)),
                    ("MSI MPG X670E", "AMD AM5 Motherboard", (6000000, 7000000)),
                    ("Gigabyte X670E", "AMD AM5 Motherboard", (5500000, 6500000)),
                    ("ASUS ROG Z790", "Intel LGA1700 Motherboard", (7500000, 8500000)),
                    ("MSI MPG Z790", "Intel LGA1700 Motherboard", (6500000, 7500000)),
                    ("Gigabyte Z790", "Intel LGA1700 Motherboard", (6000000, 7000000))
                ]
                
                cases = [
                    ("Lian Li O11", "Dynamic EVO", (2500000, 3000000)),
                    ("Fractal Design", "Torrent RGB", (3000000, 3500000)),
                    ("NZXT H7 Flow", "ATX Mid Tower", (2000000, 2500000)),
                    ("Corsair 5000D", "Airflow", (2800000, 3300000)),
                    ("Phanteks P500A", "DRGB", (2200000, 2700000)),
                    ("be quiet! 500DX", "ATX Mid Tower", (2000000, 2500000))
                ]
                
                power_supplies = [
                    ("Corsair RM1000x", "1000W 80+ Gold", (3000000, 3500000)),
                    ("EVGA SuperNOVA", "850W 80+ Gold", (2500000, 3000000)),
                    ("be quiet! Dark Power", "1200W 80+ Platinum", (4000000, 4500000)),
                    ("Seasonic Focus GX", "750W 80+ Gold", (2000000, 2500000)),
                    ("MSI MPG A850G", "850W 80+ Gold", (2300000, 2800000)),
                    ("Thermaltake Toughpower", "1000W 80+ Platinum", (3500000, 4000000))
                ]
                
                # Generate 100 random inventory items
                inventory_items = []
                categories = [
                    (processors, "Processor"),
                    (graphics_cards, "Graphics Card"),
                    (ram_kits, "RAM"),
                    (storage, "Storage"),
                    (motherboards, "Motherboard"),
                    (cases, "Case"),
                    (power_supplies, "Power Supply")
                ]
                
                for _ in range(100):
                    products, category = random.choice(categories)
                    product_name, desc, price_range = random.choice(products)
                    
                    purchase_price = random.randint(price_range[0], price_range[1])
                    selling_price = int(purchase_price * random.uniform(1.1, 1.25))  # 10-25% markup
                    quantity = random.randint(1, 20)
                    
                    item = Inventory(
                        product_name=product_name,
                        description=desc,
                        quantity=quantity,
                        purchase_price=purchase_price,
                        selling_price=selling_price,
                        category=category
                    )
                    db.session.add(item)
                
                db.session.commit()
                print("Added 100 sample products to inventory")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise

if __name__ == "__main__":
    init_db()
