import os
import shutil
from datetime import datetime

# Lokasi file database utama
DB_PATH = os.path.join('instance', 'inventory.db')
# Lokasi folder backup
BACKUP_DIR = 'backup'

os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database():
    if not os.path.exists(DB_PATH):
        print('Database file not found!')
        return False
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'inventory_backup_{now}.db')
    shutil.copy2(DB_PATH, backup_file)
    print(f'Database backup created: {backup_file}')
    return True

if __name__ == '__main__':
    backup_database()
