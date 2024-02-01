import json
import os
import shutil
from typing import Dict

import requests

try:
    from uploaded_file import UploadedFile
except ImportError:
    from .uploaded_file import UploadedFile
try:
    from my_tools import (
        convert_csv_to_excel,
        files_to_csv,
        list_local_files_and_directories,
        list_mega_files_and_directories,
        merge_local_and_mega_files,
    )
except ImportError:
    from .my_tools import (
        convert_csv_to_excel,
        files_to_csv,
        list_local_files_and_directories,
        list_mega_files_and_directories,
        merge_local_and_mega_files,
    )

BANNER = r"""
 _______    _     _                 ______                   
(_______)  | |   | |               / _____)                  
 _____ ___ | | __| |_____  ____   ( (____  _   _ ____   ____ 
|  ___) _ \| |/ _  | ___ |/ ___)   \____ \| | | |  _ \ / ___)
| |  | |_| | ( (_| | ____| |       _____) ) |_| | | | ( (___ 
|_|   \___/ \_)____|_____)_|      (______/ \__  |_| |_|\____)
                                          (____/             
"""
__version__ = "1.0.0"
latest_version_url = "https://raw.githubusercontent.com/PhunkyBob/folder_sync/master/VERSION"
latest_binary = "https://github.com/PhunkyBob/folder_sync/releases/latest"
git_repo = "https://github.com/PhunkyBob/folder_sync"

CONFIG_FILE = "config.json"


def check_version(version: str) -> str:
    latest_version = ""
    res = requests.get(latest_version_url)
    if res.status_code != 200:
        print(f"Version {version} (can't check official version)")
    else:
        latest_version = res.text.strip()
        if latest_version == version:
            print(f"Version {version} (official version)")
        else:
            print(f"Version {version} (official version is different: {latest_version})")
            print(f"Please check {latest_binary}")
    print()
    return latest_version


def config_exists() -> bool:
    if not os.path.exists(CONFIG_FILE):
        print(f'[ERROR] Config file "{CONFIG_FILE}" not found!')
        if os.path.exists(f"{CONFIG_FILE}.sample"):
            print("[INFO] Creating config file from sample. Please edit it and run the program again...")
            shutil.copy(f"{CONFIG_FILE}.sample", CONFIG_FILE)
        return False
    return True


def read_config(config_file: str) -> dict:
    with open(config_file) as f:
        return json.load(f)


def main():
    print(BANNER)
    print(f"Folder Sync ({git_repo})")
    check_version(__version__)

    if not config_exists():
        return
    config_file = os.path.join(os.getcwd(), CONFIG_FILE)
    config = read_config(config_file)
    local_files: Dict[str, UploadedFile] = {}
    mega_files: Dict[str, UploadedFile] = {}
    # Get local files
    print("[INFO] Getting local files...")
    for folder in config["local_folders"]:
        print(f"[INFO] Getting local files in \"{folder['path']}\"...")
        local_files |= list_local_files_and_directories(folder["path"], folder["label"])
        print(f"[INFO] Items found: {len(local_files)}")

    # Get Mega files
    print("[INFO] Getting Mega files...")
    for account in config["mega_accounts"]:
        print(f"[INFO] Getting Mega files in account \"{account['login']}\"...")
        mega_files |= list_mega_files_and_directories(account["login"], account["password"], account["path"])
        print(f"[INFO] Items found: {len(mega_files)}")

    # Merge local and Mega files
    print("[INFO] Merging local and Mega files...")
    merged_files = merge_local_and_mega_files(local_files, mega_files)
    print(f"[INFO] Total merged files: {len(merged_files)}")

    # Convrert to CSV
    print("[INFO] Exporting to temporary CSV...")
    csv_file = files_to_csv(merged_files)
    # And to Excel
    print("[INFO] Converting to Excel...")
    excel_file = convert_csv_to_excel(csv_file)
    print(f"[INFO] Result file: {excel_file}")
    os.remove(csv_file)
    input("Job's done! \nPress [Enter] to exit...")


if __name__ == "__main__":
    main()
