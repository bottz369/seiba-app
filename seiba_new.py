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

def load_data(file_path_or_buffer):
    """どんな文字コードでも頑張って読み込む関数"""
    df = None
    encodings = ['utf-8', 'cp932', 'shift_jis']
    
    # バッファ（アップロードされたファイル）の場合と、パス（GitHub上のファイル）の場合で処理を分ける
    is_buffer = hasattr(file_path_or_buffer, 'seek')
    
    for enc in encodings:
        try:
            if is_buffer:
                file_path_or_buffer.seek(0)
            df = pd.read_csv(file_path_or_buffer, encoding=enc)
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
# 2. デザイン設定
# ---------------------------------------------------------
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #D4AF37; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #333; }
    h1, h2, h3, h4, h5 { font-family: serif !important; color: #D4AF37 !important; }
    .stDataFrame { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("聖馬AI (Ver 3.0)")
st.markdown("##### The Art of Prediction - 究極の競馬予測")
st.markdown("---")

# ---------------------------------------------------------
# 3. サイドバー（管理者用）
# ---------------------------------------------------------
uploaded_file = None
with st.sidebar:
    st.header("Admin Menu")
    admin_password = st.text_input("管理者パスワード", type="password")
    
    if admin_password == "admin123":
        st.success("管理者認証 成功")
        st.write("▼ 一時的な確認用（全会員には反映されません）")
        uploaded_file = st.file_uploader("Test Upload CSV", type=['csv'])
        st.info("※本番データを更新するには、GitHubの 'data.csv' を上書きしてください。")

# ---------------------------------------------------------
# 4. メインエリア
# ---------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # ログイン画面
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
    
    # データの読み込みロジック（ここがVer3.0の肝！）
    df = None
    
    if uploaded_file is not None:
        # 管理者がサイドバーでテストアップロードした場合
        df = load_data(uploaded_file)
        st.caption("※管理者によるテストデータを表示中")
    else:
        # 何もアップされていない場合、GitHubにある 'data.csv' を探す
        if os.path.exists('data.csv'):
            df = load_data('data.csv')
        else:
            st.warning("現在、公開されている予測データはありません。")
    
    # データの表示
    if df is not None:
        try:
            locations = df['場所'].unique()
            col1, col2 = st.columns(2)
            with col1:
                selected_location = st.selectbox("開催場所", locations)
            
            df_loc = df[df['場所'] == selected_location]
            races = sorted(df_loc['R'].unique())
            with col2:
                selected_race = st.selectbox("レース", races, format_func=lambda x: f"{x}R")
            
            df_display = df_loc[df_loc['R'] == selected_race].copy()
            race_name = df_display['レース名'].iloc[0] if 'レース名' in df_display.columns else ""
            
            st.subheader(f"{selected_location} {selected_race}R : {race_name}")
            
            # 列フィルタリング
            cols = ['AI順位', '印', '枠', '番', '馬名', '騎手', 'AI指数']
            show_cols = [c for c in cols if c in df_display.columns]
            
            if '印' in df_display.columns: df_display['印'] = df_display['印'].fillna('')
            if 'AI順位' in df_display.columns: df_display = df_display.sort_values('AI順位')
            
            st.dataframe(df_display[show_cols], use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"データ表示エラー: {e}")
    
    st.markdown("---")
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        safe_rerun()
