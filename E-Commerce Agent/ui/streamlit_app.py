# ui/streamlit_app.py
import os
import re
import ast
import sys
import streamlit as st

# Make sure parent dir is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from catalog import PRODUCTS, FEATURED_PRODUCTS, format_price, all_categories
from graph import run_agent

IMG_DIR = os.path.join(os.path.dirname(__file__), "images")

st.set_page_config(page_title="AnyCart", page_icon="🛒", layout="wide")

# ---------- Custom CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero-banner {
    background: linear-gradient(135deg, #232F3E 0%, #37475A 50%, #FF9900 100%);
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero-title { font-size: 42px; font-weight: 800; color: #FFFFFF; margin-bottom: 6px; letter-spacing: -0.5px; }
.hero-sub { color: #FFE0B2; font-size: 16px; margin-top: 0; opacity: 0.9; }

.category-header { font-size: 22px; font-weight: 700; color: #232F3E; margin-bottom: 16px; }

.prod-card {
    border: none;
    border-radius: 16px;
    padding: 22px;
    background: #FFFFFF;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
    height: 280px;
    display: flex;
    flex-direction: column;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    border: 1px solid #F0F2F5;
}
.prod-card:hover { transform: translateY(-6px); box-shadow: 0 12px 32px rgba(0,0,0,0.1); border-color: #FF9900; }
.prod-id { background: linear-gradient(135deg, #FF9900, #FFB84D); color: #FFFFFF; font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 20px; display: inline-block; margin-bottom: 10px; }
.prod-name { font-weight: 700; color: #1B2638; font-size: 17px; margin: 4px 0; line-height: 1.3; }
.prod-category { color: #7A8695; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; font-weight: 600; }
.prod-price { color: #232F3E; font-weight: 800; font-size: 22px; }
.prod-desc { color: #5B6B7F; font-size: 13px; margin-top: auto; padding-top: 10px; line-height: 1.5; }

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid #E0E4EA;
    transition: all 0.2s ease;
}
.stButton > button:hover { background: #FF9900; color: #FFFFFF; border-color: #FF9900; }

[data-testid="stSidebar"] { background: linear-gradient(180deg, #232F3E 0%, #1A2433 100%); }
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1); }

.chat-header {
    font-size: 20px; font-weight: 700; color: #232F3E; margin-bottom: 12px;
    padding-bottom: 12px; border-bottom: 2px solid #FF9900; display: inline-block;
}

[data-testid="stChatInput"] {
    border-radius: 12px;
    border: 1px solid #E0E4EA;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
[data-testid="stChatInput"]:focus-within {
    border-color: #FF9900;
    box-shadow: 0 0 0 3px rgba(255,153,0,0.12);
}

[data-testid="stChatMessage"] { border-radius: 12px; padding: 12px 16px; }
hr { border: none; border-top: 1px solid #F0F2F5; margin: 20px 0; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- Session state ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your AnyCart assistant. Ask me about products, place an order, or track one."}
    ]
if "category" not in st.session_state:
    st.session_state.category = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "streamlit-user-1"

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🛒 AnyCart")
    st.markdown("---")
    st.markdown("### Categories")
    if st.button("All Products", use_container_width=True):
        st.session_state.category = None
    for cat in all_categories():
        if st.button(cat, key=f"side_{cat}", use_container_width=True):
            st.session_state.category = cat
    st.markdown("---")
    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Chat cleared. How can I help?"}]
        st.rerun()

# ---------- Hero ----------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🛒 AnyCart</div>
    <p class="hero-sub">Your AI-powered shopping assistant — find products, place orders, track deliveries.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Layout ----------
left, right = st.columns([2, 1])

# ==================== LEFT: Catalog ====================
with left:
    st.markdown('<div class="category-header">Shop by Category</div>', unsafe_allow_html=True)

    cat_list = all_categories()
    cols = st.columns(len(cat_list))
    for col, cat in zip(cols, cat_list):
        with col:
            img_path = os.path.join(IMG_DIR, f"{cat.lower()}.png")
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            if st.button(cat, key=f"cat_{cat}", use_container_width=True):
                st.session_state.category = cat
                st.rerun()

    st.markdown("---")

    # Product grid
    header = "Featured Picks" if not st.session_state.category else f"{st.session_state.category}"
    st.markdown(f'<div class="category-header">{header}</div>', unsafe_allow_html=True)

    if st.session_state.category:
        shown = [p for p in PRODUCTS if p["category"] == st.session_state.category]
    else:
        shown = FEATURED_PRODUCTS

    per_row = 3
    for i in range(0, len(shown), per_row):
        row = st.columns(per_row)
        for col, p in zip(row, shown[i:i + per_row]):
            with col:
                st.markdown(f"""
                <div class="prod-card">
                    <span class="prod-id">#{p['product_id']}</span>
                    <div class="prod-name">{p['name']}</div>
                    <div class="prod-category">{p['category']}</div>
                    <div class="prod-price">{format_price(p['price'])}</div>
                    <div class="prod-desc">{p['description']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.write("")

# ==================== RIGHT: Chat ====================
with right:
    st.markdown('<span class="chat-header">🤖 AI Assistant</span>', unsafe_allow_html=True)

    chat_box = st.container(height=620)
    with chat_box:
        for msg in st.session_state.messages:
            avatar = "🧑" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                content = msg["content"]
                # Pretty-print order confirmations
                order_match = re.search(r"Order placed.*?Details:\s*(\{.*\})", content, re.DOTALL)
                status_match = re.search(r"Status:\s*(\{.*\})", content, re.IGNORECASE | re.DOTALL)
                if order_match:
                    try:
                        details = ast.literal_eval(order_match.group(1))
                        st.success("Order placed successfully!")
                        st.code(details.get("order_id", "N/A"), language=None)
                        st.caption("Order ID — save this to track your order.")
                    except Exception:
                        st.markdown(content.replace("$", r"\$"))
                elif status_match:
                    try:
                        details = ast.literal_eval(status_match.group(1))
                        lines = [f"**Status:** {details.get('status','Unknown')}",
                                 f"**Order ID:** {details.get('order_id','N/A')}"]
                        if details.get("quantity"):
                            lines.append(f"**Quantity:** {details['quantity']}")
                        st.markdown("\n\n".join(lines))
                    except Exception:
                        st.markdown(content.replace("$", r"\$"))
                else:
                    st.markdown(content.replace("$", r"\$"))

    # Input
    prompt = st.chat_input("Ask about products, place an order, or track one...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_box:
            with st.chat_message("user", avatar="🧑"):
                st.markdown(prompt)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    reply = run_agent(prompt, thread_id=st.session_state.thread_id)
                st.markdown(reply.replace("$", r"\$"))
        st.session_state.messages.append({"role": "assistant", "content": reply})