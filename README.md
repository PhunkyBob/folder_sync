# Folder Sync

This tool allow to compare local files and folders with Mega.io / Mega.nz / Mega.co.nz files and folder.
The result of the comparison is an Excel file.

## Usage

Run

```cmd
python run.py
```

and wait until finished.

## Result

The result is an Excel file with the following columns:

- `name`: The subfolder and name of the folder / file from the root specified in `config.json`. It's the link betwwen Mega and local files.
- `local_label`: The label used in the `config.json` file.
- `local_path_type`: `FILE` or `FOLDER`.
- `local_full_path`: Full path of the local file.
- `local_size`: Size of the file in bytes. Folders don't have a size.
- `local_date`: Date of the file or folder.
- `mega_account`: Login used to connect the Mega account.
- `mega_path_type`: `FILE` or `FOLDER`.
- `mega_full_path`: Full path of the Mega file.
- `mega_size`: Size of the file in bytes. Folders don't have a size.
- `mega_date`: Date of the file or folder.
- `mega_shared`: `SHARED` if the file or folder have a public share link.
- `mega_link`: Public link. Works only for files, not folders (limitation of Mega API).
- `status`: Result of the comparison between local and Mega file.
  - `Synced`: File is present locally and remotely and have the same size.
  - `Different size`: File is present locally and remotely but have a different size.
  - `Different type`: File is present locally and remotely but have a different type (one is a folder whereas the other is a file).
  - `Local only`: The file exists only locally.
  - `Mega only`: The file exists only remotely.

## Configuration

Edit `config.json` file.  
Set all your local folders under `local_folders`.  
Set all your Mega accounts under `mega_accounts`.  

Example:

```json
{
 "local_folders": [
  {
   "label": "Documents",
   "path": "C:/Users/MyName/Documents"
  },
  {
   "label": "Music",
   "path": "D:/MP3/Music"
  }
 ],
 "mega_accounts": [
  {
   "login": "first_account@domain.com",
   "password": "securepassword",
   "path": "/"
  },
  {
   "login": "second_account@domain.com",
   "password": "securepassword",
   "path": "/Backup"
  }
 ]
}
```

Note that you have to use `/` and not `\`, even if you are using Windows.

This configuration will check all files and folders in:

- Mega account `first_account`, under root folder.
- Mega account `second_account`, under `Backup` folder.
- Local `C:/Users/MyName/Documents` folder.
- Local `D:/MP3/Music` folder.

File `D:/MP3/Music/Artist_name/Track_name.mp3` will match with file `/Cloud Drive/Backup/Artist_name/Track_name.mp3` on Mega `second_account` account, identified as `Artist_name/Track_name.mp3`.

## Installation

### Prerequisite

- Python 3.11 (not tested with other versions).
- (optionnal) Poetry.

### Install

#### Clone repository

```cmd
git clone https://github.com/PhunkyBob/folder_sync.git
cd folder_sync
```

#### (optional) Create virtual env

With venv module:

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

or with Poetry:

```cmd
poetry shell
```

#### Install dependencies

```cmd
python -m pip install -U pip
python -m pip install -r requirements.txt
```

or

```cmd
poetry install
```

## Todo list

[ ] Find a way to get the correct public link of a folder.

## Credits & thanks

To interact with Mega API, I used <https://github.com/pgp/mega.py>, a fork of <https://github.com/odwyersoftware/mega.py>.
