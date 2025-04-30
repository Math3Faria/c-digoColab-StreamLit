import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
import time

load_dotenv()

AVATAR_ANIMATED_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExN3lxeGY1MnV2OG0yaGQxcDhxcWNib3N0aG8ydGt1bHp4eTdoaDJicyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mlvseq9yvZhba/giphy.gif"
ASSISTANT_NAME = "Assistente Matheus"
USER_AVATAR_EMOJI = "👤"

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
        background-color: #A020F0; /* Roxo */
    }}

    /* --- Container Principal do Chat (Cartão Central) --- */
    .main .block-container {{
        max-width: 750px;
        margin: 2rem auto;
        padding: 1.5rem 2rem 4rem 2rem;
        background-color: #FFFFFF;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid #D1E8D2;
    }}

    /* --- Cabeçalho: Avatar e Título --- */
    .avatar-title-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 1.5rem;
    }}
    .avatar-title-container img.chat-avatar {{
        width: 85px;
        height: 85px;
        border-radius: 50%;
        margin-bottom: 0.8rem;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.08);
        border: 2px solid #FFFFFF;
    }}
    .avatar-title-container h1 {{
        color: #FFFFFF; /* Branco para contraste com o roxo */
        font-weight: 700;
        font-size: 2.1em;
        margin: 0;
        text-align: center;
    }}

    /* --- Balões de Mensagem --- */
    .stChatMessage {{
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.06);
        border: none;
        max-width: 90%;
        word-wrap: break-word;
        color: #111111;
    }}
    .stChatMessage p, .stChatMessage li, .stChatMessage .stMarkdown {{
        color: #111111 !important;
    }}

    /* Mensagens do Assistente */
    [data-testid="chatAvatarIcon-assistant"] + div.stChatMessage {{
        background-color: #E0BBE3; /* Lilás claro */
        margin-right: auto;
        border-left: 5px solid #BB86FC; /* Roxo mais claro */
    }}

    /* Mensagens do Usuário */
    [data-testid="chatAvatarIcon-user"] + div.stChatMessage {{
        background-color: #D1C4E9; /* Lavanda claro */
        margin-left: auto;
        border-right: 5px solid #9575CD; /* Roxo médio */
    }}

    /* --- Área de Input na Base --- */
    .stChatInputContainer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #F3E5F5; /* Rosa bem claro */
        border-top: 1px solid #CE93D8; /* Rosa médio */
        padding: 12px 0;
        box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.05);
    }}
    .stChatInputContainer > div {{
        max-width: 750px;
        margin: 0 auto;
        padding: 0 1rem;
    }}
    .stChatInputContainer textarea {{
        background-color: #FFFFFF;
        border: 1px solid #C5C5C5;
        border-radius: 20px;
        padding: 10px 15px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        color: #111111;
    }}
    .stChatInputContainer button {{
        background-color: #9C27B0; /* Roxo mais escuro */
        color: white;
        border-radius: 50%;
        border: none;
        width: 40px;
        height: 40px;
        transition: background-color 0.2s ease, transform 0.1s ease;
        margin-left: 8px;
    }}
    .stChatInputContainer button:hover {{
        background-color: #7B1FA2; /* Roxo ainda mais escuro */
        transform: scale(1.05);
    }}
    .stChatInputContainer button:active {{
        transform: scale(0.95);
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
        st.session_state.messages = [{"role": "assistant", "content": f"Olá! Como posso te ajudar hoje?"}]

    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        avatar_display = AVATAR_ANIMATED_URL if role == "assistant" else USER_AVATAR_EMOJI
        with st.chat_message(role, avatar=avatar_display):
            st.markdown(content)

    if prompt := st.chat_input("Digite sua mensagem aqui..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR_EMOJI):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=AVATAR_ANIMATED_URL):
            message_placeholder = st.empty()
            message_placeholder.markdown("▌")
            message_placeholder.markdown("Digitando... ▌")

            try:
                api_key = get_api_key()
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(prompt)
                full_response = response.text

                message_placeholder.markdown("")
                if full_response:
                    for i in range(len(full_response)):
                        message_placeholder.markdown(full_response[:i+1] + "▌")
                        time.sleep(0.02)
                    message_placeholder.markdown(full_response)
                else:
                    message_placeholder.markdown("_Resposta vazia._")

            except Exception as e:
                error_msg = f"Desculpe, ocorreu um erro: {str(e)}"
                st.error(error_msg)
                full_response = error_msg
                message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()