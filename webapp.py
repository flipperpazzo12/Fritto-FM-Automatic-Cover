import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
import os
import io
import base64

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Fritto FM Cover Generator",
    page_icon="🍟",
    layout="centered"
)

if 'lang' not in st.session_state:
    st.session_state.lang = 'IT'

# --- 2. PERCORSI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "Template")
FONT_PATH = os.path.join(BASE_DIR, "LTe50220.ttf")
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# --- 3. TRADUZIONI ---
TEXTS = {
    'IT': {
        'title': "Fritto FM Cover Generator",
        'desc': "1. Dati → 2. Foto → 3. Scarica",
        'when_label': "📅 Che giorno?",
        'appears_as': "Apparirà come:",
        'where_label': "📍 Dove?",
        'other_city': "Scrivi città:",
        'time_label': "⏰ A che ora?",
        'who_label': "Chi?",
        'who_placeholder': "Es. DJ Fritto",
        'photo_header': "📸 Carica foto",
        'upload_label': "Carica la tua foto",
        'crop_info': "💡 Seleziona l'area. Il formato è fisso (Quadrato).",
        'btn_generate': "✨ CREA LA COVER",
        'btn_download': "⬇️ SCARICA COPERTINA HD",
        'spinner': "Friggendo pixels... 🍟",
        'success_caption': "Ecco la cover pronta",
        'error_template': "⚠️ Errore: Manca il template!",
        'error_missing_name': "⛔️ Devi scrivere il NOME dell'artista!",
        'info_upload': "👆 Carica una foto per sbloccare l'editor."
    },
    'EN': {
        'title': "Fritto FM Cover Generator",
        'desc': "1. Data → 2. Photo → 3. Download",
        'when_label': "📅 When? (Date)",
        'appears_as': "Will appear as:",
        'where_label': "📍 Where?",
        'other_city': "Type city:",
        'time_label': "⏰ What time? (CET)",
        'who_label': "😎 Who?",
        'who_placeholder': "E.g. DJ Fritto",
        'photo_header': "📸 Upload your photo",
        'upload_label': "Upload your photo",
        'crop_info': "💡 Select area. Aspect ratio is locked (Square).",
        'btn_generate': "✨ CREATE COVER",
        'btn_download': "⬇️ DOWNLOAD HD COVER",
        'spinner': "Frying pixels... 🍟",
        'success_caption': "Cover ready!",
        'error_template': "⚠️ Error: Template missing!",
        'error_missing_name': "⛔️ You must enter the artist NAME!",
        'info_upload': "👆 Upload a photo to unlock editor."
    }
}
T = TEXTS[st.session_state.lang]

# --- 4. FONT CUSTOM ---
def get_font_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

font_b64 = get_font_base64(FONT_PATH)
font_face_css = ""
if font_b64:
    font_face_css = f"""
    @font-face {{
        font-family: 'FrittoBrand';
        src: url('data:font/ttf;base64,{font_b64}') format('truetype');
    }}
    """

# --- 5. CSS CHIRURGICO ---
st.markdown(f"""
    <style>
    {font_face_css}
    
    .stApp {{ background-color: #0040e8; }}
    
    /* FONT BRAND GIALLO (ESCLUSO stAlert/stInfo) */
    h1, h2, h3, h4, p, label, .stMarkdown, .stSelectbox label, .stDateInput label, .stTextInput label, .stCaption {{
        color: #fbe219 !important;
        font-family: 'FrittoBrand', 'Helvetica', sans-serif !important;
    }}
    
    /* --- FIX BOX INFORMATIVO (st.info) --- */
    .stAlert {{
        color: #0040e8 !important; 
        background-color: #e6f0ff !important; 
        border: 1px solid #0040e8 !important;
        font-family: 'FrittoBrand', sans-serif !important;
    }}
    .stAlert div[data-testid="stMarkdownContainer"] p {{
        color: #0040e8 !important;
    }}

    /* TITOLO SU UNA RIGA */
    .main-title {{
        text-align: center;
        font-size: 35px;
        white-space: nowrap; 
        margin-bottom: 0px;
        color: #fbe219;
        line-height: 1.2;
    }}
    .sub-title {{
        text-align: center;
        font-size: 14px;
        color: #fbe219;
        font-family: 'Helvetica', sans-serif !important;
    }}
    
    /* INPUT FIELDS (Bianchi) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input {{
        background-color: white !important;
        color: black !important;
        border-radius: 5px;
        border: 2px solid #fbe219;
    }}
    ::placeholder {{ color: #555555 !important; opacity: 1; }}
    
    /* --- FILE UPLOADER (CONTRASTO FIXATO) --- */
    
    /* 1. Il contenitore esterno: Bianco con bordo giallo */
    [data-testid="stFileUploader"] {{
        background-color: white !important;
        border: 2px dashed #fbe219;
        border-radius: 10px;
        padding: 20px;
    }}

    /* 2. La zona interna (Dropzone): Grigio Scuro */
    [data-testid="stFileUploaderDropzone"] {{
        background-color: #262730 !important; /* Grigio Scuro */
        border-radius: 5px;
    }}

    /* 3. Testi dentro la Dropzone: BIANCHI */
    [data-testid="stFileUploaderDropzone"] div, 
    [data-testid="stFileUploaderDropzone"] span, 
    [data-testid="stFileUploaderDropzone"] small {{
        color: white !important; /* BIANCO PER LEGGEBILITÀ */
        font-family: 'Helvetica', sans-serif !important;
    }}

    /* 4. Nome file caricato (quando c'è): Nero (perché sta su sfondo bianco) */
    [data-testid="stFileUploaderFile"] div {{ 
        color: #000000 !important; 
    }}
    
    /* 5. Tasto Browse: Blu */
    [data-testid="stFileUploader"]
