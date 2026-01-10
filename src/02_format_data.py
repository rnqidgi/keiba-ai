import pandas as pd
import json
import os
import glob
from tqdm import tqdm
import gc

# ファイルパスの設定
DATA_DIR = os.path.join("data", "01_unzipped_data")
FORMAT_INFO_DIR = os.path.join("data", "02_formatted_data", "format_info")
OUTPUT_DIR = os.path.join("data", "02_formatted_data")

# 保存先ファイルのパス
KYI_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "df_kyi.pkl")
SED_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "df_sed.pkl")

# フォーマット情報のパス
KYI_JSON_PATH = os.path.join(FORMAT_INFO_DIR, "kyi_info.json")
SED_JSON_PATH = os.path.join(FORMAT_INFO_DIR, "sed_info.json")

def get_col_specs(json_path):
    """
    JSONファイルから列の仕様（column specifications）と列名を取得する関数
    
    Args:
        json_path (str): フォーマット情報が記述されたJSONファイルのパス
        
    Returns:
        col_specs (list): (開始位置, 終了位置) のタプルのリスト
        names (list): 列名のリスト
    """
    with open(json_path, "r", encoding="utf-8") as f:
        format_info = json.load(f)
    
    col_specs = []
    names = []
    name_counts = {}
    
    for item in format_info:
        # JSONのstartは1始まりなので0始まりに変換
        start = item["start"] - 1
        # byteは長さ
        width = item["byte"]
        end = start + width
        col_specs.append((start, end))
        
        original_name = item["item"]
        if original_name in name_counts:
            name_counts[original_name] += 1
            new_name = f"{original_name}_{name_counts[original_name]}"
        else:
            name_counts[original_name] = 1
            new_name = original_name
            
        names.append(new_name)
        
    return col_specs, names

def process_data(data_dir, output_path, json_path, file_pattern_glob):
    """
    指定されたディレクトリのデータを読み込み、整形してpickleファイルとして保存する関数
    メモリ不足を防ぐために、ファイルをバッチ処理するが、
    最終的に1つのDataFrameとして結合して保存する。
    
    Args:
        data_dir (str): データが格納されているルートディレクトリ
        output_path (str): 保存先のpklファイルのパス
        json_path (str): フォーマット情報のJSONファイルのパス
        file_pattern_glob (str): 検索するファイルパターンのglob (例: "KYI*.txt")
    """
    print(f"処理開始: {os.path.basename(output_path)} ...")
    
    # フォーマット情報の取得
    col_specs, names = get_col_specs(json_path)
    
    # 対象ファイルの検索 (再帰的)
    search_path = os.path.join(data_dir, "**", file_pattern_glob)
    files = glob.glob(search_path, recursive=True)
    
    print(f"対象ファイル数: {len(files)}")
    
    if not files:
        print("ファイルが見つかりませんでした。処理をスキップします。")
        return

    # データを格納するリスト
    dfs = []
    
    # ファイルを一つずつ読み込む (tqdmで進捗表示)
    # 大量ファイルを一気にread_fwfするとメモリがきついため、
    # ループ処理を行い、適宜リストに追加する
    for file_path in tqdm(files):
        try:
            # ディレクトリはスキップ
            if os.path.isdir(file_path):
                continue

            # 固定長ファイルの読み込み
            # encodingはcp932 (Shift_JIS拡張)
            df_temp = pd.read_fwf(
                file_path,
                colspecs=col_specs,
                names=names,
                header=None,
                encoding="cp932",
                dtype=str # 型推論による予期せぬエラー防止のため一旦全て文字列として読み込む
            )
            dfs.append(df_temp)
            
        except Exception as e:
            print(f"エラー発生: {file_path}, {e}")
            continue

    if not dfs:
        print("データフレームが作成されませんでした。")
        return

    print("データ結合中...")
    # 全てのDataFrameを結合
    final_df = pd.concat(dfs, ignore_index=True)
    
    print(f"データ保存中: {output_path}")
    # Pickleファイルとして保存
    final_df.to_pickle(output_path)
    
    print(f"完了: {output_path}, 形状: {final_df.shape}")
    
    # メモリ解放
    del dfs
    del final_df
    gc.collect()

def main():
    # データディレクトリの確認
    if not os.path.exists(KYI_JSON_PATH) or not os.path.exists(SED_JSON_PATH):
        print("エラー: フォーマット情報ファイルが見つかりません。")
        return

    # KYI (競走馬データ) の処理
    # ディレクトリ名は "KYI(競走馬データ)" だが、globで再帰探索するのでルート指定でOK
    # ただし、ディレクトリ構成によっては指定を厳密にする必要がある
    # ここでは data/01_unzipped_data/KYI(競走馬データ) 以下を対象とする
    kyi_dir = os.path.join(DATA_DIR, "KYI(競走馬データ)")
    process_data(kyi_dir, KYI_OUTPUT_PATH, KYI_JSON_PATH, "KYI*.txt")
    
    # SED (レースデータ) の処理
    # 2008年以降はCSV、それ以前はTXTなので拡張子を限定せずに取得する
    sed_dir = os.path.join(DATA_DIR, "SED(レースデータ)")
    process_data(sed_dir, SED_OUTPUT_PATH, SED_JSON_PATH, "SED*")

if __name__ == "__main__":
    main()
