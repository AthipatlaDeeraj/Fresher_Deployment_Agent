import os
import shutil
import glob

# Paths
base_dir = r"c:\Users\jonro\Code\Fresher_Deployment_Agent"
fda_dir = os.path.join(base_dir, "fda")
dirs_to_remove = ["config", "core", "data", "engine"]

# Move files to fda/
for d in dirs_to_remove:
    dir_path = os.path.join(fda_dir, d)
    if os.path.exists(dir_path):
        for item in os.listdir(dir_path):
            if item == "__init__.py" or item == "__pycache__":
                continue
            src = os.path.join(dir_path, item)
            dst = os.path.join(fda_dir, item)
            # if dst exists we could overwrite, but usually we just move
            if os.path.isfile(src):
                print(f"Moving {src} -> {dst}")
                shutil.move(src, dst)
        
        # remove the directory now
        shutil.rmtree(dir_path)

# Dictionary of replacements for imports
replacements = {
    "fda.config.settings": "fda.settings",
    "fda.config": "fda",
    "fda.core.logger": "fda.logger",
    "fda.core": "fda",
    "fda.data.ingestion": "fda.ingestion",
    "fda.data.validation": "fda.validation",
    "fda.data": "fda",
    "fda.engine.aggregation": "fda.aggregation",
    "fda.engine.decision": "fda.decision",
    "fda.engine": "fda"
}

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(f"from {old} import", f"from {new} import")
        new_content = new_content.replace(f"import {old}", f"import {new}")
        
    if new_content != content:
        print(f"Updating imports in {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

# Process all py files
py_files = []
for root, _, files in os.walk(base_dir):
    if ".venv" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            py_files.append(os.path.join(root, file))

for py_file in py_files:
    process_file(py_file)

# Specifically fix settings.py CONFIG_DIR
settings_file = os.path.join(fda_dir, "settings.py")
if os.path.exists(settings_file):
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We change CONFIG_DIR = BASE_DIR / "config" to CONFIG_DIR = BASE_DIR
    content = content.replace('CONFIG_DIR = BASE_DIR / "config"', 'CONFIG_DIR = BASE_DIR')
    
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed settings.py CONFIG_DIR")

print("Done restructuring.")
