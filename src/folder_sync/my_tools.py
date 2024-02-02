import csv
import datetime
from typing import Any, Dict, List, Optional
import os
import pandas as pd

try:
    from mega.mega import Mega
    from mega.crypto import a32_to_base64
except ImportError:
    from .mega.mega import Mega
    from .mega.crypto import a32_to_base64
try:
    from uploaded_file import PathType, SharedStatus, UploadedFile
except ImportError:
    from .uploaded_file import PathType, SharedStatus, UploadedFile


def remove_unnecessary_slashes(path: str) -> str:
    path = path.replace("\\", "/")
    while path and path[0] == "/":
        path = path[1:]
    while path and path[-1] == "/":
        path = path[:-1]
    while "//" in path:
        path = path.replace("//", "/")

    return path


def list_local_files_and_directories(directory: str, local_label: Optional[str] = None) -> Dict[str, UploadedFile]:
    content_list: Dict[str, UploadedFile] = {}
    if not local_label:
        local_label = directory

    for root, directories, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            name = remove_unnecessary_slashes(file_path.replace(directory, ""))
            path_type = PathType.FILE
            local_full_path = file_path
            local_size = os.path.getsize(file_path)
            local_date = datetime.datetime.fromtimestamp(int(os.path.getmtime(file_path)))

            content_list[name] = UploadedFile(
                name=name,
                local_label=local_label,
                local_path_type=path_type,
                local_full_path=local_full_path,
                local_size=local_size,
                local_date=local_date,
            )

        for cur_dir in directories:
            directory_path = os.path.join(root, cur_dir)
            name = remove_unnecessary_slashes(directory_path.replace(directory, ""))
            path_type = PathType.FOLDER
            local_full_path = directory_path
            local_size = 0
            local_date = datetime.datetime.fromtimestamp(int(os.path.getmtime(directory_path)))
            content_list[name] = UploadedFile(
                name=name,
                local_label=local_label,
                local_path_type=path_type,
                local_full_path=local_full_path,
                local_size=local_size,
                local_date=local_date,
            )

    return content_list


def get_path(file_id: str, mega_files: dict) -> str:
    path_elems = []
    elem_id = file_id
    while elem_id:
        if elem_id not in mega_files:
            path_elems.extend(("???", "???"))
            break
        if mega_files[elem_id]["t"] == 4:
            # Rubbish Bin
            return ""
        path_elems.append(mega_files[elem_id]["a"]["n"])
        elem_id = mega_files[elem_id]["p"]
    return "/" + "/".join(reversed(path_elems))


def list_mega_files_and_directories(login: str, password: str, path: str = "") -> Dict[str, UploadedFile]:
    while path and path[0] in ("/", "\\"):
        path = path[1:]
    mega = Mega()
    try:
        m = mega.login(login, password)
    except Exception as e:
        print(f"[ERROR] Can't login to Mega: {e}")
        return {}
    files = m.get_files()
    all_files: Dict[str, UploadedFile] = {}
    for mega_id, elem in files.items():
        # print(files[mega_id])
        mega_account = login
        mega_full_path = get_path(mega_id, files)
        mega_full_path = mega_full_path.encode("latin1").decode("utf-8")
        if elem["t"] > 1 or mega_full_path == "":
            continue
        mega_path_type = PathType.FILE if elem["t"] == 0 else PathType.FOLDER
        name = "/".join(mega_full_path.split("/")[2:])
        if not name.lower().startswith(path.lower()):
            continue
        name = name[len(path) :]
        name = remove_unnecessary_slashes(name)
        if not name:
            continue
        mega_size = elem["s"] if mega_path_type == PathType.FILE else 0
        mega_date = datetime.datetime.fromtimestamp(int(elem["ts"]))
        mega_link = ""
        mega_shared = SharedStatus.NOT_SHARED
        if "h" in elem and "k" in elem and "shared" in elem:
            public_handle = elem["shared"]
            decrypted_key = a32_to_base64(elem["key"])
            mega_link = f"{m.schema}://{m.domain}" f"/#!{public_handle}!{decrypted_key}"
            # TODO: Get correct decrypted key for shared folders
            if mega_path_type == PathType.FOLDER:
                mega_link = ""
            mega_shared = SharedStatus.SHARED
        all_files[name] = UploadedFile(
            name=name,
            mega_account=mega_account,
            mega_path_type=mega_path_type,
            mega_full_path=mega_full_path,
            # mega_id=mega_id,
            mega_size=mega_size,
            mega_date=mega_date,
            mega_link=mega_link,
            mega_shared=mega_shared,
        )

    return all_files


def merge_local_and_mega_files(
    local_files: Dict[str, UploadedFile], mega_files: Dict[str, UploadedFile]
) -> List[UploadedFile]:
    all_keys = set(local_files.keys()).union(set(mega_files.keys()))
    merged_files = []
    for key in all_keys:
        elem = UploadedFile()
        elem.name = key
        if local_file := local_files.get(key):
            elem.local_label = local_file.local_label
            elem.local_path_type = local_file.local_path_type
            elem.local_full_path = local_file.local_full_path
            elem.local_size = local_file.local_size
            elem.local_date = local_file.local_date
            elem.status = "Local only"

        if mega_file := mega_files.get(key):
            elem.mega_account = mega_file.mega_account
            # elem.mega_id = mega_file.mega_id
            elem.mega_path_type = mega_file.mega_path_type
            elem.mega_full_path = mega_file.mega_full_path
            elem.mega_size = mega_file.mega_size
            elem.mega_date = mega_file.mega_date
            elem.mega_link = mega_file.mega_link
            elem.mega_shared = mega_file.mega_shared
            elem.status = "Mega only"
        if local_file and mega_file:
            elem.status = "Synced"
            if elem.local_size != elem.mega_size:
                elem.status = "Different size"
            if elem.local_path_type != elem.mega_path_type:
                elem.status = "Different type"

        merged_files.append(elem)

    merged_files.sort(key=lambda x: x.name)
    return merged_files


def files_to_csv(merged_files, filename: Optional[str] = None) -> str:
    if not filename:
        filename = "export " + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        fields = UploadedFile.get_fields()
        writer.writerow(fields)
        for elem in merged_files:
            writer.writerow([elem.__dict__[field] for field in fields])
    return filename


def convert_csv_to_excel(csv_file: str, excel_file: Optional[str] = None) -> str:
    if not excel_file:
        excel_file = csv_file.replace(".csv", ".xlsx")
    df = pd.read_csv(csv_file, sep=";", encoding="utf-8")
    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        sheet_name = "Merge Sync"
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        sheet = writer.sheets[sheet_name]
        for col in sheet.columns:
            sheet.auto_filter.ref = sheet.dimensions
        sheet.freeze_panes = sheet["A2"]
    return excel_file
