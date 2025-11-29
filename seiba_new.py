import streamlit as st
import pandas as pd

# バージョン判定してリロード
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except AttributeError:
            st.error("F5キーで更新してください")

st.set_page_config(page_title="聖馬AI - SEIBA Premium", layout="wide", initial_sidebar_state="collapsed")

# デザイン設定
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #D4AF37; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #333; }
    h1, h2, h3, h4, h5 { font-family: serif !important; color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

# ★タイトルでバージョン確認
st.title("聖馬AI (Ver 2.4 New)") 
st.markdown("##### The Art of Prediction - 究極の競馬予測")
st.markdown("---")

# サイドバー
with st.sidebar:
    st.header("Admin Menu")
    admin_password = st.text_input("管理者パスワード", type="password")
    uploaded_file = None
    if admin_password == "admin123":
        st.success("管理者認証 成功")
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

# メインエリア
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form(key='login_form'):
        password = st.text_input("Member Password", type="password")
        if st.form_submit_button("ENTER"):
            if password == "seiba2025":
                st.session_state.logged_in = True
                safe_rerun()
            else:
                st.error("パスワードが違います")
else:
    # ログイン後
    if uploaded_file is not None:
        # ★最強読み込みロジック
        df = None
        encodings = ['utf-8', 'cp932', 'shift_jis']
        for enc in encodings:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        
        if df is not None:
            # 表示処理
            locations = df['場所'].unique()
            selected_location = st.selectbox("開催場所", locations)
            df_loc = df[df['場所'] == selected_location]
            selected_race = st.selectbox("レース", sorted(df_loc['R'].unique()), format_func=lambda x: f"{x}R")
            
            df_display = df_loc[df_loc['R'] == selected_race].copy()
            st.subheader(f"{selected_location} {selected_race}R")
            
            # 必要な列だけ表示
            cols = ['AI順位', '印', '枠', '番', '馬名', '騎手', 'AI指数']
            available_cols = [c for c in cols if c in df_display.columns]
            
            if '印' in df_display.columns: df_display['印'] = df_display['印'].fillna('')
            if 'AI順位' in df_display.columns: df_display = df_display.sort_values('AI順位')
            
            st.dataframe(df_display[available_cols], use_container_width=True, hide_index=True)
        else:
            st.error("ファイル読み込み失敗")
    else:
        st.warning("データをアップロードしてください")
    
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        safe_rerun()