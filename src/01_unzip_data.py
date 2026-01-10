
import os
import zipfile
import glob
from pathlib import Path

def unzip_data():
    # ディレクトリの定義
    # プロジェクトルートからの相対パスを使用
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    SRC_DIR = PROJECT_ROOT / 'data' / '00_zipped_data'
    DEST_DIR = PROJECT_ROOT / 'data' / '01_unzipped_data'

    print(f"Source Directory: {SRC_DIR}")
    print(f"Destination Directory: {DEST_DIR}")

    if not SRC_DIR.exists():
        print(f"Error: Source directory {SRC_DIR} does not exist.")
        return

    # SRC_DIR内のサブディレクトリをループ処理
    for subdir_path in SRC_DIR.iterdir():
        if subdir_path.is_dir():
            folder_name = subdir_path.name
            target_dir = DEST_DIR / folder_name
            
            # 保存先ディレクトリが存在することを確認（存在しない場合は作成）
            if not target_dir.exists():
                print(f"Creating directory: {target_dir}")
                target_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"Processing folder: {folder_name}")
            
            # サブディレクトリ内のすべてのzipファイルを検索
            zip_files = list(subdir_path.glob('*.zip'))
            
            if not zip_files:
                print(f"  No zip files found in {folder_name}")
                continue

            for zip_file in zip_files:
                # zipファイル名（拡張子なし）のディレクトリを作成
                extraction_dir = target_dir / zip_file.stem
                if not extraction_dir.exists():
                    extraction_dir.mkdir(parents=True, exist_ok=True)

                print(f"  Unzipping: {zip_file.name} -> {extraction_dir}")
                try:
                    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                        zip_ref.extractall(extraction_dir)
                except zipfile.BadZipFile:
                    print(f"  Error: Bad zip file {zip_file.name}")
                except Exception as e:
                    print(f"  Error unzipping {zip_file.name}: {e}")

    print("Unzipping completed.")

if __name__ == "__main__":
    unzip_data()
