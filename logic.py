# logic.py
import pandas as pd
import joblib
import os

def execute_prediction(input_df, model_dir):
    """
    受け取ったDataFrameと、指定されたモデルフォルダを使って予測を行い、
    結果のDataFrameを返します。
    """
    
    # ---------------------------------------------------------
    # 1. モデルファイルのパス設定
    # ---------------------------------------------------------
    # 指定されたフォルダ(model_dir)の中にあるファイルを読みに行きます
    try:
        model = joblib.load(os.path.join(model_dir, "jra_3y_model.pkl"))
        sire_stats = joblib.load(os.path.join(model_dir, "jra_sire_stats_3y.pkl"))
        bms_stats = joblib.load(os.path.join(model_dir, "jra_bms_stats_3y.pkl"))
        jockey_stats = joblib.load(os.path.join(model_dir, "jra_jockey_stats_3y.pkl"))
        trainer_stats = joblib.load(os.path.join(model_dir, "jra_trainer_stats_3y.pkl"))
        breeder_stats = joblib.load(os.path.join(model_dir, "jra_breeder_stats_3y.pkl"))
        cf_stats = joblib.load(os.path.join(model_dir, "jra_course_frame_stats_3y.pkl"))
        cf_counts = joblib.load(os.path.join(model_dir, "jra_course_frame_counts_3y.pkl"))
    except FileNotFoundError as e:
        return None, f"モデルファイルが見つかりません: {e}"
    except Exception as e:
        return None, f"モデル読み込みエラー: {e}"

    # ---------------------------------------------------------
    # 2. データの前処理
    # ---------------------------------------------------------
    df_all = input_df.copy()

    # カラム名のマッピング（jra1217.csv形式対応）
    rename_map = {
        1: '開催', 2: 'Ｒ', 3: '馬番', 4: 'レース名',
        5: '芝ダート', 6: '距離', 7: '馬名',
        8: '性別', 9: '年齢', 10: '騎手',
        12: '調教師', 15: '生産者',
        16: '種牡馬', 20: '母父馬',
        22: '枠番'
    }
    
    # カラム名が番号(0,1,2...)の場合のみリネームを実行
    if isinstance(df_all.columns[0], int) or df_all.columns[0].isdigit():
        df_all = df_all.rename(columns=rename_map)
    
    # 文字列のクリーニング
    if '馬名' in df_all.columns:
        df_all['馬名'] = df_all['馬名'].astype(str).str.strip()

    # ---------------------------------------------------------
    # 3. 予測計算ループ
    # ---------------------------------------------------------
    all_results = []
    
    if '開催' not in df_all.columns or 'Ｒ' not in df_all.columns:
         return None, "CSVの形式が正しくありません（開催・R列不足）"

    grouped = df_all.groupby(['開催', 'Ｒ'])

    for (place, race_num), df in grouped:
        # レース情報の取得
        race_name = str(df['レース名'].iloc[0]) if 'レース名' in df.columns else ""
        track_type = str(df['芝ダート'].iloc[0]) if '芝ダート' in df.columns else ""
        distance = str(df['距離'].iloc[0]) if '距離' in df.columns else ""
        
        # コースID作成
        track_clean = "芝" if "芝" in track_type else ("ダ" if "ダ" in track_type else "障")
        COURSE_ID = f"{track_clean}{distance}"
        
        # 特徴量エンジニアリング
        df['性別コード'] = df['性別'].map({'牡': 0, '牝': 1, 'セ': 2}).fillna(0)
        df['年齢'] = pd.to_numeric(df['年齢'], errors='coerce').fillna(3)
        df['枠番'] = pd.to_numeric(df['枠番'], errors='coerce').fillna(0).astype(int)

        # スコア取得関数
        def get_score(name, stats): return stats.get(name, 0.2)

        df['父スコア'] = df['種牡馬'].apply(lambda x: get_score(x, sire_stats))
        df['母父スコア'] = df['母父馬'].apply(lambda x: get_score(x, bms_stats))
        df['騎手スコア'] = df['騎手'].apply(lambda x: get_score(x, jockey_stats))
        df['調教師スコア'] = df['調教師'].apply(lambda x: get_score(x, trainer_stats))
        df['生産者スコア'] = df['生産者'].apply(lambda x: get_score(x, breeder_stats))
        
        # コース枠スコア
        def get_cf_score(waku):
            try:
                count = cf_counts.loc[(COURSE_ID, waku)]
                if count < 5: return 0.2
                return cf_stats.loc[(COURSE_ID, waku)]
            except: return 0.2

        df['コース枠スコア'] = df['枠番'].apply(get_cf_score)

        df['血統総合'] = df['父スコア'] * df['母父スコア']
        df['チーム総合'] = df['騎手スコア'] * df['調教師スコア'] * df['生産者スコア']

        # 予測に必要なカラムを準備
        features = ['コース枠スコア', '性別コード', '年齢', '父スコア', '母父スコア', '血統総合', '騎手スコア', '調教師スコア', '生産者スコア', 'チーム総合']
        for f in features: 
            if f not in df.columns: df[f] = 0
            df[f] = df[f].fillna(0)

        # AI予測実行
        probs = model.predict_proba(df[features])
        df['AI指数'] = [p[1] * 100 for p in probs]

        # 順位付け
        df = df.sort_values('AI指数', ascending=False)
        
        # 整形してリストに追加
        rank = 1
        for _, r in df.iterrows():
            mark = "⭐" if r['AI指数'] >= 50 else ""
            
            w_val = r['コース枠スコア']
            if w_val > 0.25: w_mark = "◎"
            elif w_val > 0.22: w_mark = "○"
            elif w_val < 0.15: w_mark = "▼"
            else: w_mark = "-"

            all_results.append({
                '場所': place,
                'R': race_num,
                'レース名': race_name,
                'AI順位': rank,
                '印': mark,
                '枠': r['枠番'],
                '番': r['馬番'],
                '馬名': r['馬名'],
                '騎手': r['騎手'],
                'AI指数': round(r['AI指数'], 1),
                '枠評': w_mark,
                '種牡馬': r['種牡馬']
            })
            rank += 1

    # 結果をDataFrame化
    result_df = pd.DataFrame(all_results)
    return result_df, None
