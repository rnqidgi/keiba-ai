import pandas as pd
import os

def preprocess_data():
    """
    KYIとSEDのデータを前処理する関数
    - 欠損値を0で埋める
    - オブジェクト型の数値を数値型に変換する
    """
    input_dir = 'data/02_formatted_data'
    output_dir = 'data/03_preprocessed_data'
    
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    files = {
        'kyi': ('df_kyi.pkl', 'df_kyi.pkl'),
        'sed': ('df_sed.pkl', 'df_sed.pkl')
    }
    
    for key, (input_file, output_file) in files.items():
        input_path = os.path.join(input_dir, input_file)
        output_path = os.path.join(output_dir, output_file)
        
        print(f"Processing {input_file}...")
        
        if not os.path.exists(input_path):
            print(f"Error: {input_path} not found.")
            continue
            
        # データの読み込み
        df = pd.read_pickle(input_path)
        print(f"Loaded {input_file} with shape {df.shape}")
        
        # 欠損値を0で埋める
        print("Filling missing values with 0...")
        df.fillna(0, inplace=True)
        
        # 数値型への変換
        print("Converting columns to numeric...")
        for col in df.columns:
            try:
                # ignore: 変換できない場合は元のまま（文字列など）
                # coerceではないので、数値に変換できるものだけが変換される
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except Exception as e:
                print(f"Could not convert {col}: {e}")
        
        # 保存
        print(f"Saving to {output_path}...")
        df.to_pickle(output_path)
        print("Done.")

if __name__ == "__main__":
    preprocess_data()
