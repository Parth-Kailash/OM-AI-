import streamlit as st
import random, time, os, json, requests
from groq import Groq
import gTTS
import PyPDF2
import bcrypt
from io import BytesIO

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
HF_API_KEY = st.secrets["HF_API_KEY"]

st.set_page_config(page_title="Om Pro - Spiritual AI", page_icon="ॐ", layout="wide")
os.makedirs("users", exist_ok=True)

def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Noto+Serif+Devanagari:wght@400;700&display=swap');
.stApp {background: linear-gradient(rgba(244, 228, 188, 0.9), rgba(244, 228, 188, 0.9)), url('https://i.imgur.com/8QZ9p7A.jpg'); background-size: cover;}
    h1, h2, h3 {font-family: 'Cinzel', serif; color: #8B0000; text-align: center; text-shadow: 2px 2px 4px #D4AF37;}
.chat-bubble-user {background: rgba(212, 175, 55, 0.25); border-left: 4px solid #8B0000; padding: 12px; margin: 8px 0; border-radius: 8px;}
.chat-bubble-om {background: rgba(255, 248, 220, 0.95); border-left: 4px solid #D4AF37; padding: 12px; margin: 8px 0; border-radius: 8px;}
.stButton>button {background: linear-gradient(45deg, #8B0000, #D4AF37); color: white; font-family: 'Cinzel'; border-radius: 10px; border: none; padding: 10px 20px; font-size: 16px; width: 100%;}
    </style>
    """, unsafe_allow_html=True)

def hash_password(pwd): return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
def check_password(pwd, hashed): return bcrypt.checkpw(pwd.encode(), hashed.encode())

def save_user(username, data):
    with open(f"users/{username}.json", "w") as f: json.dump(data, f)

def load_user(username):
    if os.path.exists(f"users/{username}.json"):
        with open(f"users/{username}.json", "r") as f: return json.load(f)
    return None

def extract_pdf_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text[:4000]

def speak_text(text):
    tts = gTTS.gTTS(text=text, lang='hi')
    tts.save("response.mp3")
    st.audio("response.mp3", autoplay=True)

def generate_image(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": f"Hindu spiritual art, {prompt}, detailed, 4k, divine lighting"}
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        return None

if "user" not in st.session_state: st.session_state.user = None
if "messages" not in st.session_state: st.session_state.messages = []

load_css()

if st.session_state.user is None:
    st.markdown("<h1>ॐ - Om Pro Login</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user_data = load_user(username)
            if user_data and check_password(password, user_data["password"]):
                st.session_state.user = username
                st.session_state.messages = user_data.get("chat_history", [])
                st.rerun()
            else:
                st.error("Invalid username or password")
    with tab2:
        new_user = st.text_input("New Username", key="new_user")
        new_pass = st.text_input("New Password", type="password", key="new_pass")
        personality = st.text_area("Set Om's personality", placeholder="Ex: Be strict guru, use Sanskrit")
        plan = st.selectbox("Select Plan", ["Free", "Om Pro 99/month"])
        if st.button("Create Account"):
            if load_user(new_user):
                st.error("Username already exists")
            else:
                save_user(new_user, {
                    "password": hash_password(new_pass),
                    "personality": personality if personality else "Be a calm spiritual guru",
                    "plan": plan,
                    "chat_history": []
                })
                st.success("Account created! Login now")
else:
    user_data = load_user(st.session_state.user)
    plan = user_data.get("plan", "Free")
    st.markdown(f"<h1>ॐ Namaste {st.session_state.user}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3>Plan: {plan}</h3>", unsafe_allow_html=True)

    with st.sidebar:
        st.image("https://i.imgur.com/3v2Z8mL.png", width=100)
        st.markdown(f"**User:** {st.session_state.user}")
        st.markdown(f"**Plan:** {plan}")
        new_personality = st.text_area("Om's Personality:", value=user_data["personality"], height=100)
        if st.button("Update Personality"):
            user_data["personality"] = new_personality
            save_user(st.session_state.user, user_data)
            st.success("Personality updated!")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()

    # Chat section
    for role, msg in st.session_state.messages:
        if role == "user":
            st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-om'><b>Om:</b> {msg}</div>", unsafe_allow_html=True)

    user_input = st.text_input("Apni jigyasa likhiye...")
    pdf_file = st.file_uploader("Upload PDF for Om to read", type="pdf")

    if st.button("Send to Om"):
        if user_input or pdf_file:
            full_input = user_input
            if pdf_file:
                with st.spinner("Reading PDF..."):
                    pdf_text = extract_pdf_text(pdf_file)
                    full_input = f"PDF Content: {pdf_text}\n\nUser Question: {user_input}"
                    st.info(f"PDF uploaded: {pdf_file.name}")

            st.session_state.messages.append(("user", user_input if user_input else f"[PDF: {pdf_file.name}]"))

            with st.spinner("Om is meditating..."):
                system_prompt = f"""You are Om, a spiritual AI companion.
User's custom personality: {user_data['personality']}
Rules:
1. Start with 'Vatsa' or 'Vatsale'
2. 2-3 short lines, mix Hindi-English
3. Be wise, calm, practical"""
                chat_history = [{"role": "system", "content": system_prompt}]
                for role, msg in st.session_state.messages[-10:]:
                    chat_history.append({"role": "user" if role == "user" else "assistant", "content": msg})
                chat_history.append({"role": "user", "content": full_input})
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=chat_history,
                    temperature=0.7,
                    max_tokens=200
                )
                reply = completion.choices[0].message.content.strip()
                if not reply.startswith(("Vatsa", "Vatsale")):
                    reply = "Vatsa, " + reply
                st.session_state.messages.append(("om", reply))
                user_data["chat_history"] = st.session_state.messages
                save_user(st.session_state.user, user_data)
                if st.checkbox("🔊 Hear Om's reply", value=True):
                    speak_text(reply)
            st.rerun()

    # IMAGE GENERATION - ONLY FOR OM PRO
    st.markdown("---")
    if plan == "Om Pro 99/month":
        st.markdown("<h2>🎨 Om Image Generator - Pro Feature</h2>", unsafe_allow_html=True)
        img_prompt = st.text_input("Describe image you want from Om", placeholder="Ex: Lord Krishna playing flute under peepal tree")
        if st.button("Generate Image"):
            if img_prompt:
                with st.spinner("Om is painting..."):
                    img_bytes = generate_image(img_prompt)
                    if img_bytes:
                        st.image(img_bytes, caption=img_prompt, use_column_width=True)
                        st.success("Image generated! Right click > Save Image")
                    else:
                        st.error("Image generation failed. Try simpler prompt.")
            else:
                st.warning("Enter image description first")
    else:
        st.info("🎨 Image Generation available only for Om Pro 99/month. Upgrade plan to unlock.")
