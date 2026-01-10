# 競馬予想AI
競馬予想AIを構築するためのリポジトリです。

## モデル設計
長期的に回収率を高めることが目的のため、払戻率が高く かつ 試行回数が多く収束しやすい単勝を予測するモデルを作成します。

## 手順

### 0.データ収集
JRDBから、競走馬のデータと過去のレース結果を取得します。
- KYI：競走馬データ
- SED：レースデータ

それぞれ、1999年度から2024年度までのデータを取得します。
2023年度までのデータは学習用、2024年度のデータはテスト用とします。

収集したデータは、以下に格納します。
- KYI：data\00_zipped_data\kyi.zip
- SED：data\00_zipped_data\sed.zip

### 1.データ解凍
src\01_unzip_data.pyを実行することで、データ解凍と解凍したデータの保存を行います。

解凍したデータは、以下に格納します。
- KYI：data\01_unzipped_data\KYI(競走馬データ)
- SED：data\01_unzipped_data\SED(レースデータ)

### 2.データ整形
フォーマットルールに従って、KYIとSEDのデータを整形します。
- KYIフォーマットルール：data\02_formatted_data\format_info\kyi_info.json
- SEDフォーマットルール：data\02_formatted_data\format_info\sed_info.json

src\02_format_data.pyを実行することで、データ整形と整形したデータの保存を行います。

整形したデータは、以下の形式で保存します。
- KYI：data\02_formatted_data\df_kyi.pkl
- SED：data\02_formatted_data\df_sed.pkl

### 3.データ前処理
最初はすべてのカラムがObject型になっているため、整数についてはint型に変換しています。
また、欠損値についても0に変換する処理を行っています。

src\03_preprocess_data.pyを実行することで、データ前処理と前処理したデータの保存を行います。

前処理したデータは、以下の形式で保存します。
- KYI：data\03_preprocessed_data\df_kyi.pkl
- SED：data\03_preprocessed_data\df_sed.pkl

### 4.データ結合
機械学習に使用するため、前処理を実施したデータを結合し、1つのデータにまとめます。

src\04_merge_data.pyを実行することで、データ結合と結合したデータの保存を行います。

結合したデータは、以下の形式で保存します。
- data\04_merged_data\df_merged.pkl

### 5.目的変数と説明変数の抽出
結合したデータから、目的変数と説明変数を抽出します。

まず、データに含まれるカラムの一覧を作成し、Json形式で出力します。
その時に各カラムに対して以下のように”usage”という値を持たせます。

"usage"の値の意味：
- "target"：目的変数として使用
- "feature"：説明変数として使用
- null：学習に使用しない

この"usage"の値を参照して抽出処理を実行します。

↓生成されるJsonファイルの先頭部分
{
    "KYI_レースキー": {
        "dtype": "object",
        "nunique": 82829,
        "usage": null
    },
    "KYI_馬番": {
        "dtype": "int64",
        "nunique": 18,
        "usage": "feature"
    },
    "KYI_血統登録番号": {
        "dtype": "object",
        "nunique": 114141,
        "usage": null
    },
    "KYI_馬名": {
        "dtype": "object",
        "nunique": 112067,
        "usage": null
    },
    "KYI_IDM": {
        "dtype": "float64",
        "nunique": 777,
        "usage": "feature"
    },
    "KYI_騎手指数": {
        "dtype": "float64",
        "nunique": 42,
        "usage": "feature"
    },
    "KYI_情報指数": {
        "dtype": "float64",
        "nunique": 84,
        "usage": "feature"
    },
    "KYI_予備1": {
        "dtype": "object",
        "nunique": 1,
        "usage": null
    },

"usage"の値の自動生成ルール：
- 引数 target_columns で指定したカラムは"target"が入ります
- 型がobjectのカラムはnullが入ります
- 型がそれ以外のカラムは"feature"が入ります

Jsonファイルに定義した情報に従って、目的変数と説明変数を抽出します。
なお、目的変数について、馬が3着以内に入るか、入らないか、といういわゆる2値分類の問題を解こうとしています。
そのため、「着順」カラムを参照し、3着以内であれば1, それ以外であれば0の値を取るカラム「3着以内」を新しく作成しています。これを目的変数とします。

注意：
3着以内であれば上記の目的変数でいいですが、今回の機械学習では、「3着以内」のほかに「1着」と「2着以内」の指数も予測結果として出力したいです。
そのため、目的変数を3つに分けるなど、工夫が必要です。

src\05_extract_features.pyを実行することで、目的変数と説明変数の抽出と抽出したデータの保存を行います。

抽出したデータは、以下の形式で保存します。
- 目的変数：data\05_extracted_features\target.pkl
- 説明変数：data\05_extracted_features\features.pkl

#### 特徴量作成
人気やオッズの情報は特徴量に使わない方針です。

[学習させる特徴量]
- 馬能力指数
- レース適正
- 血統
- 馬場適性
- 過去レースの結果
- 騎手
- 騎手×馬の相性
- 馬番の優位性
- 馬性別による成長差
- 調教師
- 輸送距離
- PCI
など

### 6.データの分割
抽出した目的変数と説明変数のデータを学習用、テスト用に分割します。
- 学習用データ：2年前以前のデータ（2023年度以前のデータ）
- テスト用データ：1年前のデータ（2024年度のデータ）

src\06_split_data.pyを実行することで、データの分割と分割したデータの保存を行います。

分割したデータは、以下の形式で保存します。
- 学習用データ：data\06_split_data\df_train.pkl
- テスト用データ：data\06_split_data\df_test.pkl

### 7.モデルの学習
機械学習モデルはLightGBMを使用します。
予測結果として、以下の3つの値を出力します。
- 1着指数
- 2着以内指数
- 3着以内指数

src\07_train_model.pyを実行することで、モデルの学習と学習したモデルの保存を行います。

学習したモデルは、以下の形式で保存します。
- 学習したモデル：data\07_trained_model\model.pkl

### 8.テスト予測と評価
評価には以下の指標を使用します。
- 単勝的中率：1位と予想して的中した数 / 1位と予想した数
- 単勝回収率：1年間購入し続けた場合の回収率（払戻金額 / 購入金額）

src\08_predict_test_results.pyを実行することで、テスト予測と評価を行います。

評価結果は、以下の形式で保存します。
- 評価結果：data\08_predicted_test_results\test_result.json

### 9.本番予測（まずは8まで実装、9は将来的に実装予定）
モデルが完成したら、実際にレースの予測を実施します。
レース当日の最新データを取得し、モデルを用いて予測を行います。（テスト予測と同じ工程）

src\09_predict_live_results.pyを実行することで、本番予測を行います。

予測結果は、以下の形式で保存します。
- 予測結果：data\09_predicted_live_results\live_result.json




