import json
import os

def fix_paths_in_json(file_path):
    """Replace backslashes in all 'path' keys within a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️ Skipping {file_path}: invalid JSON ({e})")
            return

    def fix_dict(d):
        for k, v in d.items():
            if k == "path" and isinstance(v, str):
                new_v = v.replace("\\", "/")
                if new_v != v:
                    d[k] = new_v
            elif isinstance(v, dict):
                fix_dict(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        fix_dict(item)

    if isinstance(data, dict):
        fix_dict(data)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                fix_dict(item)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"✅ Fixed: {file_path}")

def fix_all_jsons(root_folder):
    """Find and process all 'all.json' files under root_folder."""
    for dirpath, _, filenames in os.walk(root_folder):
        for name in filenames:
            if name == "all.json":
                full_path = os.path.join(dirpath, name)
                fix_paths_in_json(full_path)

if __name__ == "__main__":
    fix_all_jsons('dist\\api\\contents')
