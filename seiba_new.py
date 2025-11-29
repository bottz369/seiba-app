import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 0. 便利関数
# ---------------------------------------------------------
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except AttributeError:
            st.error("画面を更新してください")

def load_data(file_path):
    """GitHub上のデータを読み込む関数"""
    df = None
    encodings = ['utf-8', 'cp932', 'shift_jis']
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            return None
    return df

# ---------------------------------------------------------
# 1. ページ設定
# ---------------------------------------------------------
st.set_page_config(page_title="聖馬AI - SEIBA Premium", layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# 2. デザイン設定（強力な隠蔽設定）
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 全体の配色（黒×金） */
    .stApp { background-color: #050505; color: #D4AF37; }
    
    /* フォント設定 */
    h1, h2, h3, h4, h5 { font-family: serif !important; color: #D4AF37 !important; }
    
    /* データテーブルのデザイン */
    .stDataFrame { border: 1px solid #333; }

    /* --- ここから強力な「隠す」設定 --- */
    
    /* 1. ヘッダーバー（右上のメニューなど）を領域ごと完全に消す */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* 2. フッター（右下のStreamlit/GitHubアイコン）を領域ごと完全に消す */
    footer[data-testid="stFooter"] {
        display: none !important;
    }
    /* 念の為、古い仕様のクラス名でも非表示指定 */
    .stFooter {
        display: none !important;
    }
    
    /* 3. 全体の余白を調整して画面を広く使う */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    
    /* 4. リンクのホバー時の色なども調整 */
    a { color: #D4AF37 !important; text-decoration: none; }
    a:hover { text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. アプリケーション本体
# ---------------------------------------------------------

# タイトル
st.title("聖馬AI")
st.markdown("##### The Art of Prediction - 究極の競馬予測")
st.markdown("---")

# ログイン管理
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- ログイン画面 ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form(key='login_form'):
            st.write("会員パスワードを入力してください")
            password = st.text_input("Member Password", type="password")
            if st.form_submit_button("ENTER"):
                if password == "seiba2025":
                    st.session_state.logged_in = True
                    safe_rerun()
                else:
                    st.error("パスワードが違います")
else:
    # --- ログイン後のダッシュボード ---
    
    # GitHub上の 'data.csv' を読みに行く
    df = None
    if os.path.exists('data.csv'):
        df = load_data('data.csv')
    
    if df is not None:
        try:
            # 場所の選択
            locations = df['場所'].unique()
            col1, col2 = st.columns(2)
            with col1:
                selected_location = st.selectbox("開催場所", locations)
            
            # レースの選択
            df_loc = df[df['場所'] == selected_location]
            races = sorted(df_loc['R'].unique())
            with col2:
                selected_race = st.selectbox("レース", races, format_func=lambda x: f"{x}R")
            
            # データ抽出
            df_display = df_loc[df_loc['R'] == selected_race].copy()
            race_name = df_display['レース名'].iloc[0] if 'レース名' in df_display.columns else ""
            
            st.subheader(f"{selected_location} {selected_race}R : {race_name}")
            
            # 表示する列の制御
            cols = ['AI順位', '印', '枠', '番', '馬名', '騎手', 'AI指数']
            show_cols = [c for c in cols if c in df_display.columns]
            
            # データの整形
            if '印' in df_display.columns: df_display['印'] = df_display['印'].fillna('')
            if 'AI順位' in df_display.columns: df_display = df_display.sort_values('AI順位')
            
            # テーブル表示
            st.dataframe(df_display[show_cols], use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"データ表示エラー: {e}")
    else:
        # データがない場合の表示
        st.info("現在、最新の予測データを準備中です。更新をお待ちください。")
    
    st.markdown("---")
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        safe_rerun()
