import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Fritto FM Artist Tool",
    page_icon="🍟",
    layout="centered"
)

# --- PERCORSI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "Template")
FONT_PATH = os.path.join(BASE_DIR, "LTe50220.ttf")
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# --- CSS BRANDING (BLU & GIALLO) ---
st.markdown("""
    <style>
    /* Sfondo Blu Fritto */
    .stApp {
        background-color: #0040e8;
    }
    /* Testi Gialli */
    h1, h2, h3, p, label, .stMarkdown, .stSelectbox label, .stDateInput label, .stTextInput label {
        color: #fbe219 !important;
        font-family: 'Helvetica', sans-serif;
    }
    /* Input Box Bianche (per leggibilità) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stDateInput input {
        background-color: white !important;
        color: black !important;
        border-radius: 5px;
    }
    /* Dropdown menu items text color fix */
    div[role="listbox"] ul {
        background-color: white;
        color: black;
    }
    /* Bottoni Gialli */
    div.stButton > button {
        background-color: #fbe219;
        color: #0040e8;
        font-weight: 800;
        border: none;
        padding: 0.5rem 2rem;
        font-size: 18px;
        width: 100%;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #fff;
        color: #0040e8;
        border: 2px solid #fbe219;
    }
    /* Nascondi footer Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI ---
def get_english_date(d):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return f"{days[d.weekday()]}, {d.strftime('%d.%m.%y')}"

def wrap_text(text, font, max_chars=15):
    import textwrap
    return textwrap.wrap(text, width=max_chars)

# --- UI HEADER ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=110)
with col_title:
    st.title("Fritto FM Cover Generator")
    st.markdown("**1. Dati -> 2. Foto -> 3. Scarica**")

st.markdown("---")

# --- UI FORM DATI ---

# Riga 1: Data e Luogo
c1, c2 = st.columns(2)
with c1:
    d = st.date_input("📅 When? (Date)", datetime.date.today())
    formatted_date = get_english_date(d)
    st.caption(f"Apparirà come: {formatted_date}")

with c2:
    locations = ["Milan, IT", "London, UK", "Berlin, DE", "Paris, FR", "New York, US", "Tokyo, JP"]
    loc_choice = st.selectbox("📍 Where?", locations)
    # Fallback per scrivere a mano se serve
    if loc_choice == "Altro...": 
        location = st.text_input("Scrivi città:", "Milan, IT")
    else: 
        location = loc_choice

# Riga 2: Orario e Nome
c3, c4 = st.columns(2)
with c3:
    time_slot = st.selectbox("⏰ When? (CET Time)", ["19.00", "20.00", "21.00"])

with c4:
    artist_name = st.text_input("😎 Who?", placeholder="Es. Mat")

# --- SEZIONE FOTO ---
st.markdown("---")
st.subheader("📸 Upload your photo")

uploaded_file = st.file_uploader("", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")

if uploaded_file and artist_name:
    # Carica Template
    template_name = f"{time_slot[:2]}.png"
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    
    if os.path.exists(template_path):
        template = Image.open(template_path).convert("RGBA")
        W, H = template.size
        
        # Editor Ritaglio
        st.info("💡 Drag the corners of the yellow box to crop your photo.")
        img_source = Image.open(uploaded_file).convert("RGBA")
        
        # Il widget cropper restituisce l'immagine già tagliata
        cropped_img = st_cropper(
            img_source,
            realtime_update=True,
            box_color='#fbe219',
            aspect_ratio=(W, H),
            should_resize_image=True
        )

        st.markdown("---")

        if st.button("✨ Create Cover! ✨"):
            with st.spinner("Friggendo pixels... 🍟"):
                
                # 1. Resize High Quality
                img_fitted = cropped_img.resize((W, H), Image.LANCZOS)
                
                # 2. Compositing
                canvas = Image.new("RGBA", (W, H))
                canvas.paste(img_fitted, (0, 0))
                canvas.alpha_composite(template)
                
                # 3. Testi
                draw = ImageDraw.Draw(canvas)
                try:
                    font = ImageFont.truetype(FONT_PATH, 33)
                except:
                    font = ImageFont.load_default()
                
                Y_POS = 1868
                PADDING = 25
                
                # Nome a capo
                lines = wrap_text(artist_name, font, 15)
                ascent, descent = font.getmetrics()
                lh = ascent + descent + 5
                cy = Y_POS - (len(lines) * lh / 2)
                
                for line in lines:
                    draw.text((200 + PADDING, cy), line, font=font, fill="white")
                    cy += lh
                
                # Where / When
                draw.text((833 + PADDING, Y_POS), location, font=font, fill="white", anchor="lm")
                draw.text((1441 + PADDING, Y_POS), formatted_date, font=font, fill="white", anchor="lm")
                
                # 4. Output
                final_rgb = canvas.convert("RGB")
                st.image(final_rgb, caption="Ecco la cover pronta", width=400)
                
                # Buffer per download
                buf = io.BytesIO()
                final_rgb.save(buf, format="JPEG", quality=95)
                byte_im = buf.getvalue()
                
                filename = f"{time_slot.replace(':','')}_{artist_name}.jpg"
                
                st.download_button(
                    label="⬇️ Download Cover",
                    data=byte_im,
                    file_name=filename,
                    mime="image/jpeg"
                )
    else:
        st.error(f"Template {template_name} mancante nel sistema!")

elif not uploaded_file:
    st.info("Upload a photo to unlock the editor.")