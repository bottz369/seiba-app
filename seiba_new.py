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
# 1. ページ設定（Horsemen仕様）
# ---------------------------------------------------------
st.set_page_config(
    page_title="Horsemen - Premium Prediction", # タブ名も変更
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# ---------------------------------------------------------
# 2. デザイン設定（ステルスモード維持）
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 全体の配色（黒×金） */
    .stApp { background-color: #050505 !important; color: #D4AF37 !important; }
    h1, h2, h3, h4, h5 { font-family: serif !important; color: #D4AF37 !important; }
    .stDataFrame { border: 1px solid #333; }

    /* --- NUCLEAR STEALTH MODE (徹底消去) --- */
    header, footer, #MainMenu, [data-testid="stToolbar"], [data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        visibility: hidden !important;
        display: none !important;
        height: 0px !important;
        width: 0px !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    .stDeployButton, div[class*="stDeployButton"], .viewerBadge_container__1QSob {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* レイアウト調整 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }
    
    /* リンク色 */
    a { color: #D4AF37 !important; text-decoration: none; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. アプリケーション本体
# ---------------------------------------------------------

# タイトル（Horsemenロゴ風）
st.markdown("<br>", unsafe_allow_html=True)
st.title("Horsemen")
st.markdown("##### The Art of Prediction")
st.markdown("---")

# ログイン管理
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.form(key='login_form'):
            st.write("Enter Password") # 英語表記でクールに
            password = st.text_input("Member Password", type="password")
            if st.form_submit_button("ENTER"):
                if password == "seiba2025": # パスワードはそのまま（変更可）
                    st.session_state.logged_in = True
                    safe_rerun()
                else:
                    st.error("Invalid Password")
else:
    # ログイン後
    df = None
    if os.path.exists('data.csv'):
        df = load_data('data.csv')
    
    if df is not None:
        try:
            locations = df['場所'].unique()
            col1, col2 = st.columns(2)
            with col1:
                selected_location = st.selectbox("LOCATION", locations) # 英語ラベル
            
            df_loc = df[df['場所'] == selected_location]
            races = sorted(df_loc['R'].unique())
            with col2:
                selected_race = st.selectbox("RACE", races, format_func=lambda x: f"{x}R") # 英語ラベル
            
            df_display = df_loc[df_loc['R'] == selected_race].copy()
            race_name = df_display['レース名'].iloc[0] if 'レース名' in df_display.columns else ""
            
            st.subheader(f"{selected_location} {selected_race}R : {race_name}")
            
            cols = ['AI順位', '印', '枠', '番', '馬名', '騎手', 'AI指数']
            show_cols = [c for c in cols if c in df_display.columns]
            
            if '印' in df_display.columns: df_display['印'] = df_display['印'].fillna('')
            if 'AI順位' in df_display.columns: df_display = df_display.sort_values('AI順位')
            
            st.dataframe(df_display[show_cols], use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Data is being updated. Please wait.")
    
    st.markdown("---")
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        safe_rerun()
