import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import io

# --- 1. CONFIGURAZIONE PAGINA E STATO ---
st.set_page_config(
    page_title="Fritto FM Cover Generator",
    page_icon="🍟",
    layout="centered"
)

if 'lang' not in st.session_state:
    st.session_state.lang = 'IT'

# --- 2. TRADUZIONI ---
TEXTS = {
    'IT': {
        'title_desc': "**1. Dati -> 2. Foto -> 3. Scarica**",
        'when_label': "📅 Che giorno?",
        'appears_as': "Apparirà come:",
        'where_label': "📍 Dove?",
        'other_city': "Scrivi città:",
        'time_label': "⏰ A che ora?",
        'who_label': "Chi?",
        'who_placeholder': "Es. Dj Fritto",
        'photo_header': "📸 Carica foto",
        'upload_label': "Carica la tua foto",
        'crop_info': "💡 Seleziona l'area. Il formato è fisso (Quadrato).",
        'btn_generate': "✨ CREA LA COVER",
        'btn_download': "⬇️ SCARICA COPERTINA HD",
        'spinner': "Friggendo pixels... 🍟",
        'success_caption': "Ecco la cover pronta",
        'error_template': "⚠️ Errore: Manca il template!",
        'info_upload': "👆 Carica una foto per sbloccare l'editor."
    },
    'EN': {
        'title_desc': "**1. Data -> 2. Photo -> 3. Download**",
        'when_label': "📅 When? (Date)",
        'appears_as': "Will appear as:",
        'where_label': "📍 Where?",
        'other_city': "Type city:",
        'time_label': "⏰ What time? (CET)",
        'who_label': "😎 Who?",
        'who_placeholder': "E.g. Mat",
        'photo_header': "📸 Upload your photo",
        'upload_label': "Upload your photo",
        'crop_info': "💡 Select area. Aspect ratio is locked (Square).",
        'btn_generate': "✨ CREATE COVER",
        'btn_download': "⬇️ DOWNLOAD HD COVER",
        'spinner': "Frying pixels... 🍟",
        'success_caption': "Cover ready!",
        'error_template': "⚠️ Error: Template missing!",
        'info_upload': "👆 Upload a photo to unlock editor."
    }
}

T = TEXTS[st.session_state.lang]

# --- 3. PERCORSI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "Template")
FONT_PATH = os.path.join(BASE_DIR, "LTe50220.ttf")
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# --- 4. CSS BRANDING ---
st.markdown("""
    <style>
    .stApp { background-color: #0040e8; }
    
    /* TITOLI E TESTI */
    h1, h2, h3, h4, p, label, .stMarkdown, .stSelectbox label, .stDateInput label, .stTextInput label, .stCaption {
        color: #fbe219 !important;
        font-family: 'Helvetica', sans-serif;
    }
    
    /* INPUT FIELDS */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input {
        background-color: white !important;
        color: black !important;
        border-radius: 5px;
        border: 2px solid #fbe219;
    }

    /* PLACEHOLDER & FILE NAMES (Grigio scuro per leggibilità) */
    ::placeholder { color: #666666 !important; opacity: 1; }
    [data-testid="stFileUploader"] div[data-testid="stFileUploaderFile"] div { color: #333333 !important; }
    [data-testid="stFileUploader"] span { color: #333333 !important; }
    [data-testid="stFileUploader"] small { color: #555555 !important; }
    
    /* FILE UPLOADER STYLE */
    [data-testid="stFileUploader"] {
        background-color: white;
        border: 2px dashed #fbe219;
        border-radius: 10px;
        padding: 20px;
    }
    [data-testid="stFileUploader"] section > div { color: #0040e8 !important; }
    [data-testid="stFileUploader"] button {
        background-color: #0040e8 !important;
        color: white !important;
        border: none !important;
    }
    
    /* TASTO CREA COVER */
    div.stButton > button {
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
    }
    div.stButton > button:hover {
        background-color: #ffffff !important; 
        color: #0040e8 !important; 
        border-color: #fbe219 !important;
        transform: translateY(-2px);
        box-shadow: 0px 6px 0px #b8a612 !important;
    }
    div.stButton > button:active {
        transform: translateY(2px);
        box-shadow: 0px 0px 0px #b8a612 !important;
    }
    div.stButton > button p { color: #0040e8 !important; }
    
    div[data-testid="column"] button {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 25px !important;
        padding: 0 !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 5. FUNZIONI ---
def get_english_date(d):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return f"{days[d.weekday()]}, {d.strftime('%d.%m.%y')}"

def wrap_text(text, font, max_chars=15):
    import textwrap
    return textwrap.wrap(text, width=max_chars)

# --- 6. UI ---
top_col1, top_col2, top_col3 = st.columns([1, 3, 1])

with top_col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=100)

with top_col2:
    st.title("Fritto FM Cover Generator")
    st.markdown(T['title_desc'])

with top_col3:
    col_it, col_uk = st.columns(2)
    with col_it:
        if st.button("🇮🇹"):
            st.session_state.lang = 'IT'
            st.rerun()
    with col_uk:
        if st.button("🇬🇧"):
            st.session_state.lang = 'EN'
            st.rerun()

st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    d = st.date_input(T['when_label'], datetime.date.today())
    formatted_date = get_english_date(d)
    st.caption(f"{T['appears_as']} {formatted_date}")

with c2:
    locations = ["Milan, IT", "London, UK", "Berlin, DE", "Paris, FR", "New York, US", "Tokyo, JP", "Altro..."]
    loc_choice = st.selectbox(T['where_label'], locations)
    if loc_choice == "Altro...": 
        location = st.text_input(T['other_city'], "Rome, IT")
    else: 
        location = loc_choice

c3, c4 = st.columns(2)
with c3:
    time_slot = st.selectbox(T['time_label'], ["19.00", "20.00", "21.00"])

with c4:
    artist_name = st.text_input(T['who_label'], placeholder=T['who_placeholder'])

st.markdown("---")
st.subheader(T['photo_header'])

uploaded_file = st.file_uploader(label=T['upload_label'], type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")

if uploaded_file and artist_name:
    template_name = f"{time_slot[:2]}.png"
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    
    if os.path.exists(template_path):
        template = Image.open(template_path).convert("RGBA")
        # Qui prendiamo le dimensioni reali (es. 2000x2000)
        W_tmpl, H_tmpl = template.size
        
        st.info(T['crop_info'])
        img_source = Image.open(uploaded_file).convert("RGBA")
        
        # --- CROPPER CORRETTO ---
        # 1. aspect_ratio=(1, 1) -> Forza un quadrato perfetto.
        # 2. Dato che il template è 2000x2000 (Quadrato), Quadrato su Quadrato = NESSUNA DEFORMAZIONE.
        # 3. La libreria gestisce i bordi: il box non può uscire dall'immagine.
        
        cropped_img = st_cropper(
            img_source,
            realtime_update=True,
            box_color='#fbe219',
            aspect_ratio=(1, 1), # QUADRATO
            should_resize_image=True
        )

        st.markdown("---")

        if st.button(T['btn_generate']):
            with st.spinner(T['spinner']):
                
                # Resize finale: Il ritaglio è quadrato -> Il template è quadrato.
                # Questa operazione è uno ZOOM (Scaling), non uno STRETCH.
                img_fitted = cropped_img.resize((W_tmpl, H_tmpl), Image.LANCZOS)
                
                canvas = Image.new("RGBA", (W_tmpl, H_tmpl))
                canvas.paste(img_fitted, (0, 0))
                canvas.alpha_composite(template)
                
                draw = ImageDraw.Draw(canvas)
                try:
                    font = ImageFont.truetype(FONT_PATH, 33)
                except:
                    font = ImageFont.load_default()
                
                # Coordinate del testo (tieni quelle vecchie se il posizionamento verticale è lo stesso,
                # oppure aggiusta Y_POS se il template 2000x2000 ha il footer più in basso/alto)
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
        st.error(T['error_template'])

elif not uploaded_file:
    st.info(T['info_upload'])
