import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 0. System Functions
# ---------------------------------------------------------
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except AttributeError:
            st.error("Please refresh the page.")

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
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# ---------------------------------------------------------
# 2. Ultra-Luxury CSS (Awwwards Style)
# ---------------------------------------------------------
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;800&family=Lato:wght@300;400&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
    /* --- 1. Global Reset & Typography --- */
    .stApp {
        background: radial-gradient(circle at 50% 30%, #1a1a1a 0%, #000000 100%) !important;
        color: #e0e0e0;
        font-family: 'Lato', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Cinzel', serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase;
        color: #D4AF37 !important; /* Metallic Gold */
        text-shadow: 0px 4px 20px rgba(212, 175, 55, 0.4);
    }
    
    p, div, label {
        font-family: 'Lato', sans-serif;
        letter-spacing: 0.05em;
    }

    /* --- 2. Stealth Mode (Hide Streamlit Elements) --- */
    header, footer, #MainMenu, [data-testid="stToolbar"], [data-testid="stHeader"], [data-testid="stStatusWidget"], .stDeployButton, .viewerBadge_container__1QSob {
        display: none !important;
    }
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 5rem !important;
        max-width: 1000px !important; /* Center content elegantly */
    }

    /* --- 3. Glassmorphism Containers --- */
    /* Login Form & Data Area */
    div[data-testid="stForm"], div.stDataFrame {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 2px;
        padding: 40px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }

    /* --- 4. Inputs & Buttons (Custom Styling) --- */
    /* Input Fields */
    .stTextInput input {
        background-color: transparent !important;
        border: none !important;
        border-bottom: 1px solid #555 !important;
        color: #fff !important;
        border-radius: 0px !important;
        font-family: 'Cinzel', serif;
        letter-spacing: 0.1em;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-bottom: 1px solid #D4AF37 !important;
        box-shadow: none !important;
    }
    
    /* Select Boxes */
    div[data-baseweb="select"] > div {
        background-color: rgba(20, 20, 20, 0.8) !important;
        border: 1px solid #333 !important;
        color: #fff !important;
    }

    /* Buttons (Enter, Logout) */
    .stButton button {
        background: transparent !important;
        border: 1px solid #D4AF37 !important;
        color: #D4AF37 !important;
        font-family: 'Cinzel', serif !important;
        letter-spacing: 0.2em;
        padding: 10px 30px !important;
        transition: all 0.5s ease !important;
        border-radius: 0px !important;
    }
    .stButton button:hover {
        background: #D4AF37 !important;
        color: #000 !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.6);
        transform: translateY(-2px);
    }
    
    /* --- 5. Data Table Styling --- */
    div[data-testid="stDataFrame"] {
        border: none !important;
    }
    /* Hide index if possible via CSS (backup) */
    table tbody th { display: none; }
    
    /* --- 6. Animations --- */
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .stApp > div {
        animation: fadeIn 1.5s ease-out;
    }
    
    /* Custom Logo Text */
    .logo-text {
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
        -webkit-background-clip: text;
        color: transparent;
        font-family: 'Cinzel', serif;
        font-weight: 800;
        letter-spacing: 0.2em;
    }
    .sub-logo {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        letter-spacing: 0.4em;
        margin-bottom: 3rem;
        font-family: 'Lato', sans-serif;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Application Logic
# ---------------------------------------------------------

# Header Section (Logo)
st.markdown('<div class="logo-text">HORSEMEN</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-logo">The Art of Prediction</div>', unsafe_allow_html=True)

# Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- Login Screen ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form(key='login_form'):
            st.markdown("<div style='text-align: center; margin-bottom: 20px; color: #888; font-family: Cinzel;'>MEMBERS ONLY</div>", unsafe_allow_html=True)
            # Label is hidden via CSS or empty, utilizing placeholder
            password = st.text_input("", type="password", placeholder="ENTER PASSWORD")
            
            # Centered Button
            b_col1, b_col2, b_col3 = st.columns([1,1,1])
            with b_col2:
                submit_btn = st.form_submit_button("ENTER")
            
            if submit_btn:
                if password == "seiba2025":
                    st.session_state.logged_in = True
                    safe_rerun()
                else:
                    st.error("ACCESS DENIED")

# --- Dashboard Screen ---
else:
    df = None
    if os.path.exists('data.csv'):
        df = load_data('data.csv')
    
    if df is not None:
        try:
            # Layout for filters
            st.markdown("<br>", unsafe_allow_html=True)
            f_col1, f_col2 = st.columns(2)
            
            with f_col1:
                locations = df['場所'].unique()
                selected_location = st.selectbox("LOCATION", locations)
            
            with f_col2:
                df_loc = df[df['場所'] == selected_location]
                races = sorted(df_loc['R'].unique())
                selected_race = st.selectbox("RACE", races, format_func=lambda x: f"{x}R")
            
            # Data Processing
            df_display = df_loc[df_loc['R'] == selected_race].copy()
            race_name = df_display['レース名'].iloc[0] if 'レース名' in df_display.columns else ""
            
            # Race Title Display
            st.markdown(f"""
                <div style="text-align: center; margin: 30px 0; border-top: 1px solid #333; border-bottom: 1px solid #333; padding: 15px;">
                    <span style="font-family: 'Cinzel'; font-size: 1.5rem; color: #fff;">{selected_location} {selected_race}R</span><br>
                    <span style="font-family: 'Lato'; color: #888; letter-spacing: 0.1em;">{race_name}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Columns Configuration
            cols = ['AI順位', '印', '枠', '番', '馬名', '騎手', 'AI指数']
            show_cols = [c for c in cols if c in df_display.columns]
            
            if '印' in df_display.columns: df_display['印'] = df_display['印'].fillna('')
            if 'AI順位' in df_display.columns: df_display = df_display.sort_values('AI順位')
            
            # Display Table
            st.dataframe(
                df_display[show_cols],
                use_container_width=True,
                hide_index=True
            )
            
        except Exception as e:
            st.error(f"System Error: {e}")
    else:
        st.info("Awaiting Data Update...")
    
    # Footer Area
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        safe_rerun()
