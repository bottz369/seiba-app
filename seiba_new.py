import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client

# ---------------------------------------------------------
# 0. System Functions
# ---------------------------------------------------------
def init_connection():
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            return None
        return create_client(url, key)
    except:
        return None

supabase = init_connection()

def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except AttributeError:
            st.error("Please refresh.")

def load_data(file_path):
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
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Horsemen | Premium Prediction",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'About': None}
)

# ---------------------------------------------------------
# 2. Design (CSS) - 最終調整版
# ---------------------------------------------------------
custom_css = """
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;800&family=Playfair+Display:wght@400;500;700&family=Lato:wght@300;400&display=swap" rel="stylesheet">
<style>
    /* --- 全体設定 --- */
    .stApp { 
        background: radial-gradient(circle at 50% 30%, #111133 0%, #000000 100%) !important; 
        color: #E0C582; 
        font-family: 'Lato', sans-serif; 
    }
    
    /* --- フォント変更 (Playfair Display) --- */
    h1, h2, h3, h4, h5 { 
        font-family: 'Playfair Display', serif !important; 
        font-weight: 500 !important; /* 細めに変更 */
        letter-spacing: 0.15em !important;
        color: #E0C582 !important; 
        text-shadow: 0 4px 15px rgba(224, 197, 130, 0.4); 
    }
    
    /* --- 不要な要素の削除 & 枠線削除 --- */
    header, footer, #MainMenu, [data-testid="stToolbar"], .stDeployButton { display: none !important; }
    
    /* ガラス効果 */
    .glass-box { 
        background: rgba(255,255,255,0.03); 
        backdrop-filter: blur(15px); 
        border: none !important; /* 枠線を完全に削除 */
        box-shadow: 0 0 40px rgba(0,0,0,0.8);
    }
    
    /* --- 入力フォーム (小文字表示 & 枠線修正) --- */
    /* SelectboxやTextInputの外側のコンテナの枠線と背景を消去 */
    div[data-testid*="stSelectbox"], div[data-testid*="stTextInput"] {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
    }
    
    /* 入力フォームの実際のフィールド */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background: transparent !important; 
        border: none !important; 
        border-bottom: 1px solid #777 !important;
        color: #fff !important; 
        text-align: center; 
        font-family: 'Lato', sans-serif; /* 入力文字のフォントをシンプルなものに戻す */
        text-transform: none !important; /* ← ★小文字表示の修正★ */
        letter-spacing: 0.1em;
        border-radius: 0px !important;
    }
    
    /* --- サブタイトルの修正 --- */
    .sub-logo { 
        text-align: center; /* 中央揃えの再確認 */
        color: #888; 
        letter-spacing: 0.4em; 
        font-size: 0.8rem; 
        margin-bottom: 3rem; 
        text-transform: uppercase; 
    }
    
    /* --- テーブルの枠線とタイトルの仕切りを削除 --- */
    div[data-testid="stDataFrame"] { border: none !important; }
    .stDataFrame table { border: none !important; }
    
    /* レースタイトル上下の仕切りを削除 */
    .race-title-separator { display: none !important; }
    .stApp div[style*="border-top"] { border-top: none !important; }
    .stApp div[style*="border-bottom"] { border-bottom: none !important; }

    /* その他ボタン設定 */
    .stButton button {
        background: transparent !important; border: 1px solid #E0C582 !important; color: #E0C582 !important;
        font-family: 'Playfair Display', serif !important; letter-spacing: 0.2em; transition: 0.3s;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Application Logic
# ---------------------------------------------------------
st.markdown('<div class="logo-text">HORSEMEN</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-logo">The Art of Prediction</div>', unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = None

# --- AUTHENTICATION ---
if not st.session_state.user:
    if not supabase:
        st.warning("Maintenance Mode: Database connecting...")
        st.stop()
        
    tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
    
    # LOGIN
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("USERNAME")
                password = st.text_input("PASSWORD", type="password")
                btn = st.form_submit_button("ENTER")
                
                if btn:
                    if username and password:
                        try:
                            res = supabase.table('users').select("*").eq('username', username).eq('password', password).execute()
                            if len(res.data) > 0:
                                user_data = res.data[0]
                                if user_data['status'] == 'approved':
                                    st.session_state.user = user_data
                                    safe_rerun()
                                elif user_data['status'] == 'pending':
                                    st.warning("Account pending approval.")
                                else:
                                    st.error("Access Denied.")
                            else:
                                st.error("Invalid credentials.")
                        except Exception as e:
                            st.error(f"Login Error: {e}")
                    else:
                        st.error("Please enter both username and password.")

    # REGISTER
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("reg_form"):
                new_user = st.text_input("NEW USERNAME")
                new_pass = st.text_input("NEW PASSWORD", type="password")
                reg_btn = st.form_submit_button("APPLY")
                
                if reg_btn:
                    if new_user and new_pass:
                        try:
                            check = supabase.table('users').select("*").eq('username', new_user).execute()
                            if len(check.data) > 0:
                                st.error("Username already taken.")
                            else:
                                supabase.table('users').insert({
                                    "username": new_user,
                                    "password": new_pass,
                                    "status": "pending",
                                    "role": "member"
                                }).execute()
                                st.success("Application Sent.")
                        except Exception as e:
                            st.error(f"Register Error: {e}")
                    else:
                        st.warning("Please fill all fields.")

# --- DASHBOARD ---
else:
    user = st.session_state.user
    
    # --- ADMIN PANEL ---
    if user['role'] == 'admin':
        with st.expander("ADMIN DASHBOARD (Member Management)", expanded=False):
            st.write("##### ⚠️ Pending Requests")
            try:
                pending_users = supabase.table('users').select("*").eq('status', 'pending').execute().data
                if pending_users:
                    for p_user in pending_users:
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.info(f"User: {p_user['username']}")
                        if c2.button("APPROVE", key=f"app_{p_user['id']}"):
                            supabase.table('users').update({"status": "approved"}).eq("id", p_user['id']).execute()
                            safe_rerun()
                        if c3.button("REJECT", key=f"rej_{p_user['id']}"):
                            supabase.table('users').delete().eq("id", p_user['id']).execute()
                            safe_rerun()
                else:
                    st.caption("No pending requests.")
            except:
                st.error("Error fetching data.")
            
            st.markdown("---")
            
            st.write("##### 👥 Active Members")
            try:
                active_users = supabase.table('users').select("*").eq('status', 'approved').neq('role', 'admin').execute().data
                if active_users:
                    for a_user in active_users:
                        col_u, col_p, col_btn = st.columns([2, 2, 1])
                        with col_u:
                            st.write(f"👤 **{a_user['username']}**")
                        with col_p:
                            st.caption(f"Pass: {a_user['password']}")
                        with col_btn:
                            if st.button("REMOVE", key=f"del_{a_user['id']}"):
                                supabase.table('users').delete().eq("id", a_user['id']).execute()
                                st.warning(f"Removed {a_user['username']}")
                                safe_rerun()
                        st.divider()
                else:
                    st.info("No active members.")
            except:
                st.error("Error fetching active members.")

    # --- DATA DISPLAY ---
    df = None
    if os.path.exists('data.csv'):
        df = load_data('data.csv')
    
    if df is not None:
        try:
            # --- START FILTER BOX ---
            st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
            f_col1, f_col2 = st.columns(2)
            
            locations = df['場所'].unique()
            selected_location = f_col1.selectbox("LOCATION", locations)
            df_loc = df[df['場所'] == selected_location]
            races = sorted(df_loc['R'].unique())
            selected_race = f_col2.selectbox("RACE", races, format_func=lambda x: f"{x}R")
            st.markdown("</div>", unsafe_allow_html=True)
            # --- END FILTER BOX ---

            df_display = df_loc[df_loc['R'] == selected_race].copy()
            
            # --- DATA CHECK ---
            if df_display.empty:
                st.info(f"{selected_location} {selected_race}R のデータは現在用意されていません。")
            else:
                # --- DISPLAY LOGIC ---
                race_name = df_display['レース名'].iloc[0] if 'レース名' in df_display.columns else ""
                
                st.markdown(f"""
                    <div class="race-title-separator" style="text-align: center; margin: 30px 0; padding: 15px;">
                        <span style="font-family: 'Playfair Display'; font-weight: 500; font-size: 1.5rem; color: #fff;">{selected_location} {selected_race}R</span><br>
                        <span style="font-family: 'Lato'; color: #888; letter-spacing: 0.1em;">{race_name}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                cols = ['AI順位', '印', '枠', '番', '馬名', '騎手', 'AI指数']
                show_cols = [c for c in cols if c in df_display.columns]
                
                if '印' in df_display.columns: df_display['印'] = df_display['印'].fillna('')
                if 'AI順位' in df_display.columns: df_display = df_display.sort_values('AI順位')
                
                st.markdown("<div class='glass-box'>", unsafe_allow_html=True)
                st.dataframe(df_display[show_cols], use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"System Error: {e}")
    else:
        st.info("Awaiting Data Update...")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("LOGOUT"):
        st.session_state.user = None
        safe_rerun()
