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
    [data-testid="stFileUploader"] button {{
        background-color: #0040e8 !important;
        color: white !important;
        border: none !important;
    }}
    
    /* --- BOTTONE "GENERATE" --- */
    div.stButton > button {{
        background-color: #fbe219 !important;
        color: #0040e8 !important;           
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
    div.stButton > button p {{ color: #0040e8 !important; }}

    /* --- BOTTONI BANDIERE (SOLO EMOJI) --- */
    div[data-testid="stHorizontalBlock"]:first-child button {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
        min-height: 0px !important;
        height: auto !important;
        width: auto !important;
        font-size: 35px !important; /* Grandezza Emoji */
        margin: 0px !important;
        line-height: 1 !important;
    }}
    
    div[data-testid="stHorizontalBlock"]:first-child button:hover {{
        background-color: transparent !important;
        transform: scale(1.2) !important;
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

# --- 7. HEADER (LAYOUT A DUE RIGHE) ---

# RIGA 1: LOGO (Sinistra) .................... BANDIERE (Destra)
top_c1, top_c2, top_c3 = st.columns([2, 6, 2])

with top_c1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=80)

with top_c3:
    # Bandiere affiancate
    f1, f2 = st.columns([1, 1])
    with f1:
        if st.button("🇮🇹", key="it_btn"):
            st.session_state.lang = 'IT'
            st.rerun()
    with f2:
        if st.button("🇬🇧", key="en_btn"):
            st.session_state.lang = 'EN'
            st.rerun()

# RIGA 2: TITOLO (Sotto, al centro, indisturbato)
st.markdown(f"<h1 class='main-title'>{T['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='sub-title'><b>{T['desc']}</b></p>", unsafe_allow_html=True)

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
