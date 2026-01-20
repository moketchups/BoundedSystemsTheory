
import os
import shutil

def persist_changes():
    source_dir = '/Users/jamienucho/demerzel'
    backup_dir = os.path.join(source_dir, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    
    for filename in os.listdir(source_dir):
        if filename.endswith('.py'):
            source_file = os.path.join(source_dir, filename)
            backup_file = os.path.join(backup_dir, filename)
            shutil.copy2(source_file, backup_file)
            print(f"[AUTONOMY] Backed up {filename} to {backup_dir}")

if __name__ == '__main__':
    persist_changes()
