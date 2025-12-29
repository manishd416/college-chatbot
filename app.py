import streamlit as st
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ---------- NLP SETUP ----------
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

# ---------- KNOWLEDGE BASE ----------
responses = {
    "admission": "Admissions start in May every year. Visit the official website for online applications.",
    "fee": "The annual fee for the AI & ML department is ₹1,50,000.",
    "principal": "Our principal is Dr. K. Venkatesh.",
    "college": "This is Sri Venkateswara College of Engineering and Technology.",
    "placement": "Our placement cell partners with TCS, Infosys, and Wipro.",
    "courses": "We offer B.Tech, M.Tech, and MBA programs.",
    "ai": "The AI lab is located in Block B, 2nd floor with GPU systems.",
    "library": "The library is open from 8 AM to 8 PM on weekdays.",
    "canteen": "The canteen is open from 9 AM to 5 PM.",
    "hostel": "Hostel facilities are available with Wi-Fi and 24/7 security."
}

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
    matches = [k for k in responses if k in tokens]

    if matches:
        confidence = round(len(matches) / len(tokens), 2)
        return responses[matches[0]], confidence
    else:
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
