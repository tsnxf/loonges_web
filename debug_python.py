import os
import glob
import sys

def hex_dump(data):
    return " ".join(f"{b:02x}" for b in data)

def inspect_directory(path):
    print(f"\n--- Inspecting: {path} ---")
    if not os.path.exists(path):
        print("Path does not exist.")
        return

    try:
        all_files = os.listdir(path)
        pth_files = [f for f in all_files if f.endswith(".pth")]
        
        if not pth_files:
             print("No .pth files found.")
             return

        for f in pth_files:
            full_path = os.path.join(path, f)
            print(f"Found: {f}")
            try:
                with open(full_path, 'rb') as file_obj:
                    raw_data = file_obj.read()
                    try:
                        decoded = raw_data.decode('utf-8')
                        print("UTF-8: OK")
                    except UnicodeDecodeError as e:
                        print(f"UTF-8: FAILED ({e})")
                        print("!!! CORRUPTED FILE !!!")
                        print(f"Hex: {hex_dump(raw_data[:50])}")
                        print(f"ACTION: rm \"{full_path}\"")
            except Exception as e:
                print(f"Error reading {f}: {e}")

    except PermissionError:
        print("Permission denied.")

def main():
    print(f"Sys Prefix: {sys.prefix}")
    print(f"Base Prefix: {getattr(sys, 'base_prefix', 'N/A')}")
    
    # 1. Check current Sys Path (where Python ACTUALLY looks)
    print("\n--- Checking sys.path ---")
    distinct_paths = set(sys.path)
    for p in distinct_paths:
        if "site-packages" in p:
             inspect_directory(p)

    # 2. Check local venv explicitly (just in case sys.path is weird in -S mode)
    # Assuming script is run from project root and venv is 'loonges_venv'
    cwd = os.getcwd()
    venv_site = os.path.join(cwd, "loonges_venv", "lib", "python3.9", "site-packages")
    if os.path.exists(venv_site):
        inspect_directory(venv_site)
    else:
        # try 3.10, 3.11 etc just in case
        wildcard = os.path.join(cwd, "loonges_venv", "lib", "python3.*", "site-packages")
        matches = glob.glob(wildcard)
        for m in matches:
            inspect_directory(m)

if __name__ == "__main__":
    main()
