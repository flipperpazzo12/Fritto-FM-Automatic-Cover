import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image, ImageDraw, ImageFont
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

# --- 5. CSS FIX (UI & BRANDING) ---
st.markdown(f"""
    <style>
    {font_face_css}
    
    .stApp {{ background-color: #0040e8; }}
    
    /* FONT BRAND GIALLO */
    h1, h2, h3, h4, p, label, .stMarkdown, .stSelectbox label, .stDateInput label, .stTextInput label, .stCaption, .stAlert {{
        color: #fbe219 !important;
        font-family: 'FrittoBrand', 'Helvetica', sans-serif !important;
    }}
    
    /* TITOLO SU UNA RIGA (Ridotto per stare nei bordi) */
    .main-title {{
        text-align: center;
        font-size: 32px; /* Ridotto da 38px a 32px */
        white-space: nowrap; /* FORZA UNA RIGA */
        overflow: visible;
        margin-bottom: 0px;
        padding-bottom: 0px;
        color: #fbe219;
    }}
    .sub-title {{
        text-align: center;
        font-size: 14px;
        margin-top: 0px;
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
    
    /* --- FILE UPLOADER STYLE (FIX COLORI & DARK MODE) --- */
    [data-testid="stFileUploader"] {{
        background-color: white !important; /* Forza sfondo BIANCO */
        border: 2px dashed #fbe219;
        border-radius: 10px;
        padding: 20px;
    }}
    
    /* Testo "Drag and drop..." -> GRIGIO SCURO */
    [data-testid="stFileUploader"] section > div {{
        color: #666666 !important; 
        font-weight: normal !important;
    }}
    /* Testo piccolo "Limit 200MB..." -> GRIGIO SCURO */
    [data-testid="stFileUploader"] small {{
        color: #666666 !important;
    }}
    /* Icona Upload -> GRIGIO */
    [data-testid="stFileUploader"] span {{
        color: #666666 !important;
    }}
    /* Tasto "Browse files" -> BLU */
    [data-testid="stFileUploader"] button {{
        background-color: #0040e8 !important;
        color: white !important;
        border: none !important;
    }}
    
    /* ERROR BOX STYLE */
    .stAlert {{
        background-color: white !important;
        color: #ff2b2b !important;
        border: 2px solid #ff2b2b !important;
        border-radius: 10px;
        font-weight: bold;
    }}
    
    /* --- TASTO CREA COVER (Visibile!) --- */
    div.stButton > button {{
        background-color: #fbe219 !important; /* Giallo Pieno */
        color: #0040e8 !important;           /* Testo Blu */
        font-weight: 900 !important;
        border: 3px solid #fbe219 !important;
        padding: 0.8rem 2rem;
        font-size: 22px !important;
        text-transform: uppercase;
        width: 100%;
        border-radius: 10px;
        box-shadow: 0px 4px 0px #b8a612 !important;
        transition: all 0.2s ease-in-out;
        font-family: 'FrittoBrand', sans-serif !important;
    }}
    div.stButton > button:hover {{
        background-color: #ffffff !important; 
        color: #0040e8 !important; 
        border-color: #fbe219 !important;
        transform: translateY(-2px);
        box-shadow: 0px 6px 0px #b8a612 !important;
    }}
    div.stButton > button:active {{
        transform: translateY(2px);
        box-shadow: 0px 0px 0px #b8a612 !important;
    }}
    /* Fix per il testo interno del bottone */
    div.stButton > button p {{ color: #0040e8 !important; }}

    /* --- FIX BANDIERE (Trasparenti e Separate) --- */
    /* Targettiamo i bottoni nella colonna di destra */
    [data-testid="column"]:nth-of-type(3) button {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
        font-size: 26px !important; /* Più piccole */
        margin-top: 5px !important;
    }}
    [data-testid="column"]:nth-of-type(3) button:hover {{
        transform: scale(1.2) !important;
    }}
    [data-testid="column"]:nth-of-type(3) button:focus {{
        outline: none !important;
        border: none !important;
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# --- 6. FUNZIONI ---
def get_english_date(d):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return f"{days[d.weekday()]}, {d.strftime('%d.%m.%y')}"

def wrap_text(text, font, max_chars=15):
    import textwrap
    return textwrap.wrap(text, width=max_chars)

# --- 7. HEADER (Layout Migliorato) ---
# Colonne: [Logo] [Titolo] [Bandiere]
# Bandiere ha width 1.5 per dare spazio
c_left, c_center, c_right = st.columns([1, 5, 1.5])

with c_left:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=90)

with c_center:
    st.markdown(f"<h1 class='main-title'>{T['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-title'><b>{T['desc']}</b></p>", unsafe_allow_html=True)

with c_right:
    # Sotto-colonne per separare le bandiere
    # [Spazio vuoto] [Bandiera IT] [Spazio] [Bandiera UK]
    f0, f1, f2, f3 = st.columns([0.2, 1, 0.2, 1])
    with f1:
        if st.button("🇮🇹", key="it_btn"):
            st.session_state.lang = 'IT'
            st.rerun()
    with f3:
        if st.button("🇬🇧", key="en_btn"):
            st.session_state.lang = 'EN'
            st.rerun()

st.markdown("---")

# --- 8. FORM DATI ---
c1, c2 = st.columns(2)
with c1:
    d = st.date_input(T['when_label'], datetime.date.today())
    formatted_date = get_english_date(d)
    st.caption(f"{T['appears_as']} {formatted_date}")

with c2:
    locations = ["Milan, IT (Default)", "London, UK", "Berlin, DE", "Paris, FR", "New York, US", "Tokyo, JP", "Altro..."]
    loc_choice = st.selectbox(T['where_label'], locations)
    
    if loc_choice == "Altro...": 
        location = st.text_input(T['other_city'], "Rome, IT")
    elif "Default" in loc_choice:
        location = "Milan, IT"
    else: 
        location = loc_choice

c3, c4 = st.columns(2)
with c3:
    times_list = [f"{h}.00" for h in range(10, 25)]
    time_slot = st.selectbox(T['time_label'], times_list)

with c4:
    artist_name = st.text_input(T['who_label'], placeholder=T['who_placeholder'])

st.markdown("---")
st.subheader(T['photo_header'])

uploaded_file = st.file_uploader(label=T['upload_label'], type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")

if uploaded_file:
    template_name = f"{time_slot[:2]}.png"
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    
    if os.path.exists(template_path):
        template = Image.open(template_path).convert("RGBA")
        W_tmpl, H_tmpl = template.size
        
        st.info(T['crop_info'])
        img_source = Image.open(uploaded_file).convert("RGBA")
        
        # --- CROPPER (QUADRATO) ---
        cropped_img = st_cropper(
            img_source,
            realtime_update=True,
            box_color='#fbe219',
            aspect_ratio=(1, 1), 
            should_resize_image=True
        )

        st.markdown("---")

        if st.button(T['btn_generate']):
            if not artist_name or artist_name.strip() == "":
                st.error(T['error_missing_name'])
            else:
                with st.spinner(T['spinner']):
                    
                    # Resize finale
                    img_fitted = cropped_img.resize((W_tmpl, H_tmpl), Image.LANCZOS)
                    
                    canvas = Image.new("RGBA", (W_tmpl, H_tmpl))
                    canvas.paste(img_fitted, (0, 0))
                    canvas.alpha_composite(template)
                    
                    draw = ImageDraw.Draw(canvas)
                    try:
                        font = ImageFont.truetype(FONT_PATH, 33)
                    except:
                        font = ImageFont.load_default()
                    
                    Y_POS = 1868
                    PADDING = 25
                    
                    lines = wrap_text(artist_name, font, 15)
                    ascent, descent = font.getmetrics()
                    lh = ascent + descent + 5
                    cy = Y_POS - (len(lines) * lh / 2)
                    
                    for line in lines:
                        draw.text((200 + PADDING, cy), line, font=font, fill="white")
                        cy += lh
                    
                    draw.text((833 + PADDING, Y_POS), location, font=font, fill="white", anchor="lm")
                    draw.text((1441 + PADDING, Y_POS), formatted_date, font=font, fill="white", anchor="lm")
                    
                    final_rgb = canvas.convert("RGB")
                    
                    st.balloons()
                    st.image(final_rgb, caption=T['success_caption'], width=400)
                    
                    buf = io.BytesIO()
                    final_rgb.save(buf, format="JPEG", quality=95)
                    byte_im = buf.getvalue()
                    
                    filename = f"{time_slot.replace(':','')}_{artist_name}.jpg"
                    
                    st.download_button(
                        label=T['btn_download'],
                        data=byte_im,
                        file_name=filename,
                        mime="image/jpeg"
                    )
    else:
        st.error(f"{T['error_template']} (Cercavo: {template_name})")

elif not uploaded_file:
    st.info(T['info_upload'])
