import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
import time

load_dotenv()

AVATAR_ANIMATED_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExN3lxeGY1MnV2OG0yaGQxcDhxcWNib3N0aG8ydGt1bHp4eTdoaDJicyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mlvseq9yvZhba/giphy.gif"
ASSISTANT_NAME = "Assistente Matheus"
USER_AVATAR_EMOJI = "👤"

# *** COLE O LINK DA IMAGEM DE FUNDO AQUI: ***
BACKGROUND_IMAGE_URL = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjduZ2l2MmhjaWx4OWE5eXdvcjBvcWlianYxY2w5NTc4eW91YXlrZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3ov9jJuT2pEVMRMas0/giphy.gif"

st.set_page_config(
    page_title=ASSISTANT_NAME,
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def get_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🚨 Erro Crítico: A variável de ambiente GEMINI_API_KEY não foi definida! Verifique seu arquivo `.env` ou as configurações de ambiente.")
        st.stop()
    return api_key

st.markdown(f"""
<style>
    /* --- Fundo Geral --- */
    .stApp {{
        background-color: #A020F0;
        {f"background-image: url('{BACKGROUND_IMAGE_URL}'); background-size: cover; background-repeat: no-repeat;" if BACKGROUND_IMAGE_URL else ""}
        font-size: 0.95rem;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        margin: 0;
    }}

    /* --- Container Principal do Chat --- */
    .block-container {{
        max-width: 580px;
        margin: 2rem auto;
        padding: 1rem 1.5rem 1.5rem 1.5rem;
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid #D1E8D2;
        display: flex;
        flex-direction: column;
        align-items: stretch;
    }}

    /* --- Área de Mensagens --- */
    .chat-messages-container {{
        overflow-y: auto;
        max-height: 500px;
        padding-bottom: 1rem;
    }}

    /* Estilização da barra de rolagem */
    .chat-messages-container::-webkit-scrollbar {{
        width: 8px;
    }}
    .chat-messages-container::-webkit-scrollbar-track {{
        background: rgba(241, 241, 241, 0.5);
    }}
    .chat-messages-container::-webkit-scrollbar-thumb {{
        background: #888;
        border-radius: 4px;
    }}
    .chat-messages-container::-webkit-scrollbar-thumb:hover {{
        background: #555;
    }}
    .chat-messages-container {{
        scrollbar-width: thin;
        scrollbar-color: #888 rgba(241, 241, 241, 0.5);
    }}

    /* --- Cabeçalho: Avatar e Título --- */
    .avatar-title-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 1rem;
        width: 100%;
        padding-top: 1rem;
    }}
    .avatar-title-container img.chat-avatar {{
        width: 75px;
        height: 75px;
        border-radius: 50%;
        margin-bottom: 0.6rem;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.08);
        border: 2px solid #FFFFFF;
    }}
    .avatar-title-container h1 {{
        color: #000000;
        font-weight: 700;
        font-size: 1.8em;
        margin: 0;
        text-align: center;
    }}

    /* --- Balões de Mensagem --- */
    .stChatMessage {{
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.06);
        border: none;
        word-wrap: break-word;
        color: #111111;
        font-size: 0.9rem;
        align-self: flex-start;
        width: 100%;
        display: block;
    }}
    [data-testid="chatAvatarIcon-user"] + div.stChatMessage {{
        align-self: flex-end;
    }}
    [data-testid="chatAvatarIcon-assistant"] + div.stChatMessage {{
        background-color: #E0BBE3;
        margin-right: auto;
        border-left: 4px solid #BB86FC;
    }}
    .stChatMessage p, .stChatMessage li, .stChatMessage .stMarkdown {{
        color: #111111 !important;
    }}
    [data-testid="chatAvatarIcon-user"] + div.stChatMessage {{
        background-color: #D1C4E9;
        margin-left: auto;
    }}

    /* --- Área de Input do Usuário --- */
    .stChatInputContainer {{
        background-color: white;
        padding: 8px 1rem;
        display: flex;
        align-items: center;
        border-top: 1px solid #D1E8D2;
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 15px;
    }}
    .stChatInputContainer textarea {{
        flex-grow: 1;
        background-color: #FFFFFF;
        border: 1px solid #C5C5C5;
        border-radius: 18px;
        padding: 8px 12px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        color: #000000; /* Garante que o texto seja preto */
        font-size: 0.9rem;
        margin-right: 6px;
        height: 30px;
        resize: none;
    }}
    .stChatInputContainer button {{
        background-color: #9C27B0;
        color: white;
        border-radius: 50%;
        border: none;
        width: 35px;
        height: 35px;
        transition: background-color 0.2s ease, transform 0.1s ease;
    }}
    .stChatInputContainer button:hover {{
        background-color: #7B1FA2;
        transform: scale(1.03);
    }}
    .stChatInputContainer button:active {{
        transform: scale(0.97);
    }}
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown(f"""
    <div class="avatar-title-container">
        <img src="{AVATAR_ANIMATED_URL}" alt="Avatar Animado" class="chat-avatar">
        <h1>{ASSISTANT_NAME}</h1>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": f"Oii meu querido, fala comigo, tem alguma pergunta?"}]

    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        avatar_display = AVATAR_ANIMATED_URL if role == "assistant" else USER_AVATAR_EMOJI
        with st.chat_message(role, avatar=avatar_display):
            st.markdown(content)

    prompt = st.chat_input("Digite sua mensagem aqui...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR_EMOJI):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=AVATAR_ANIMATED_URL):
            message_placeholder = st.empty()
            message_placeholder.markdown("Digitando... ▌")

            try:
                api_key = get_api_key()
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(prompt)
                full_response = response.text

                message_placeholder.markdown(full_response)
            except Exception as e:
                error_msg = f"Desculpe, ocorreu um erro: {str(e)}"
                st.error(error_msg)
                full_response = error_msg
                message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        # Javascript para rolar para a última mensagem (opcional, pois st.chat_input já faz isso)
        # st.markdown('<script>var chatContainer = document.getElementById("chat-container"); chatContainer.scrollTop = chatContainer.scrollHeight;</script>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()