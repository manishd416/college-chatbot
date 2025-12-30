import streamlit as st
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ---------- NLP SETUP ----------
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

# ---------- KNOWLEDGE BASE (multi-word support, loaded once) ----------
import json
from pathlib import Path

kb_path = Path(__file__).parent / "knowledge.json"
_kb_entries = {}  # maps tuple(key_tokens) -> response
_kb_max_key_len = 1

# Load KB once at startup
try:
    with kb_path.open(encoding="utf-8") as kb_file:
        responses = json.load(kb_file)
except FileNotFoundError:
    responses = {}

entries = {}
max_len = 1
for k, v in responses.items():
    # tokenize the key, lemmatize and keep only alnum tokens
    key_tokens = [lemmatizer.lemmatize(t) for t in word_tokenize(k.lower()) if t.isalnum() and t not in stop_words]
    if not key_tokens:
        continue
    key_tuple = tuple(key_tokens)
    entries[key_tuple] = v
    max_len = max(max_len, len(key_tuple))

_kb_entries = entries
_kb_max_key_len = max_len

# ---------- FUNCTIONS ----------
def preprocess(text):
    tokens = word_tokenize(text.lower())
    return [
        lemmatizer.lemmatize(w)
        for w in tokens
        if w.isalnum() and w not in stop_words
    ]

def chatbot_response(user_input):
    tokens = preprocess(user_input)
    if not tokens:
        return "Sorry, I don't have information about that. Please contact the admin office.", 0.0

    # Try to find the longest matching n-gram in the KB entries
    # prioritize longer matches (more specific)
    match = None
    match_len = 0
    for n in range(_kb_max_key_len, 0, -1):
        if n > len(tokens):
            continue
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i : i + n])
            if ngram in _kb_entries:
                match = (_kb_entries[ngram], n)
                match_len = n
                break
        if match:
            break

    if match:
        response_text, matched_tokens = match
        confidence = round(matched_tokens / len(tokens), 2)
        return response_text, confidence

    # fallback: no match
    return "Sorry, I don't have information about that. Please contact the admin office.", 0.0

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="College Chatbot", layout="centered")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
.chat-header {
    background: linear-gradient(90deg, #003366, #0059b3);
    padding: 20px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}

.welcome-box {
    background-color: #1f3c88;
    color: #ffffff;
    padding: 18px;
    border-radius: 10px;
    margin-bottom: 20px;
    font-size: 15px;
    line-height: 1.6;
}

.welcome-box strong {
    font-size: 17px;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER (LOGO FIXED) ----------
st.markdown('<div class="chat-header">', unsafe_allow_html=True)
st.image("logo.png", width=90)   # ✅ CORRECT WAY
st.markdown("""
<h2>Sri Venkateswara College Chatbot</h2>
<p>Your virtual assistant for college enquiries</p>
</div>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.welcome_shown = False

# ---------- WELCOME MESSAGE ----------
if not st.session_state.welcome_shown:
    st.markdown("""
    <div class="welcome-box">
        <strong>Welcome!</strong><br>
        I’m your college virtual assistant.<br>
        You can ask me about admissions, fees, courses, placements,
        hostel facilities, library timings, and more.
    </div>
    """, unsafe_allow_html=True)
    st.session_state.welcome_shown = True

# ---------- CHAT HISTORY ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- CHAT INPUT ----------
user_input = st.chat_input("Type your question here...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    reply, confidence = chatbot_response(user_input)
    bot_reply = f"{reply}\n\n**Confidence:** {confidence}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })

    with st.chat_message("assistant"):
        st.markdown(bot_reply)
