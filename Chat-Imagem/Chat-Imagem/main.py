import streamlit as st
from PIL import Image
import io
import requests
from datetime import datetime
from googletrans import Translator
import base64
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

AVATAR_ANIMATED_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExN3lxeGY1MnV2OG0yaGQxcDhxcWNib3N0aG8ydGt1bHp4eTdoaDJicyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mlvseq9yvZhba/giphy.gif"
ASSISTANT_NAME = "AI Image Generator"
USER_AVATAR_EMOJI = "👤"
BACKGROUND_IMAGE_URL = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjduZ2l2MmhjaWx4OWE5eXdvcjBvcWlianYxY2w5NTc4eW91YXlrZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3ov9jJuT2pEVMRMas0/giphy.gif"

# Configuração da página
st.set_page_config(
    page_title=ASSISTANT_NAME,
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Dimensões permitidas para SDXL
ALLOWED_DIMENSIONS = [
    (1024, 1024), 
    (1152, 896), (896, 1152),
    (1216, 832), (832, 1216),
    (1344, 768), (768, 1344),
    (1536, 640), (640, 1536)
]

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
        color: #000000;
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
    
    /* Sidebar styling */
    .stSidebar {{
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }}
    
    /* Button styling */
    .stDownloadButton button {{
        background-color: #9C27B0 !important;
        color: white !important;
        border-radius: 18px !important;
        border: none !important;
        padding: 8px 16px !important;
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

    # Sidebar para configurações
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Tenta pegar a API key dos secrets ou variáveis de ambiente
        if 'STABILITY_API_KEY' in st.secrets:
            api_key = st.secrets['STABILITY_API_KEY']
            st.success("API Key loaded automatically!")
        elif os.getenv('STABILITY_API_KEY'):
            api_key = os.getenv('STABILITY_API_KEY')
            st.success("API Key loaded from environment!")
        else:
            api_key = st.text_input("Enter your Stability AI API Key", type="password")
            if not api_key:
                st.warning("You can set a permanent key in app settings")
        
        st.markdown("[Get API Key](https://platform.stability.ai/)")
        
        st.divider()
        st.markdown("Made with ❤️ using [Stability AI](https://stability.ai/) and [Streamlit](https://streamlit.io/)")

    # Inicializa o histórico de chat
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Describe the image you want to create and I'll generate it for you!"}]

    # Container para as mensagens com barra de rolagem
    with st.container():
        chat_container = st.markdown('<div class="chat-messages-container" id="chat-container">', unsafe_allow_html=True)
        
        # Exibe o histórico de mensagens
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            avatar_display = AVATAR_ANIMATED_URL if role == "assistant" else USER_AVATAR_EMOJI
            with st.chat_message(role, avatar=avatar_display):
                if "type" in message and message["type"] == "image":
                    st.image(content)
                else:
                    st.markdown(content)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Função para traduzir para inglês
    def translate_to_english(text):
        try:
            translator = Translator()
            translation = translator.translate(text, dest='en')
            return translation.text
        except:
            return text  # Se falhar, retorna o texto original

    # Função para gerar imagens usando a API do Stability AI
    def generate_image_with_stability(prompt, api_key, cfg_scale, steps, width, height, sampler):
        engine_id = "stable-diffusion-xl-1024-v1-0"
        api_host = "https://api.stability.ai"
        
        # Garante que o prompt está em inglês
        english_prompt = translate_to_english(prompt)
        
        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "text_prompts": [{"text": english_prompt}],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "samples": 1,
                "steps": steps,
                "sampler": sampler,
            },
        )

        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")
        
        data = response.json()
        
        # Corrige o tratamento da imagem base64
        image_data = base64.b64decode(data["artifacts"][0]["base64"])  # Decodifica a string base64 para bytes
        return Image.open(io.BytesIO(image_data))

    # Input do usuário
    if prompt := st.chat_input("Describe the image you want to create..."):
        # Adiciona a mensagem do usuário ao histórico
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "type": "text"
        })
        
        with st.chat_message("user", avatar=USER_AVATAR_EMOJI):
            st.markdown(prompt)
        
        # Verifica se a API key foi fornecida
        if not api_key:
            st.error("Please enter your Stability AI API Key")
            st.stop()
        
        # Resposta do assistente
        with st.chat_message("assistant", avatar=AVATAR_ANIMATED_URL):
            with st.spinner("Generating your image..."):
                try:
                    # Gera a imagem
                    generated_image = generate_image_with_stability(
                        prompt=prompt,
                        api_key=api_key,
                        cfg_scale=cfg_scale,
                        steps=steps,
                        width=width,
                        height=height,
                        sampler=sampler
                    )
                    
                    # Exibe a imagem
                    st.image(generated_image, use_column_width=True)
                    
                    # Adiciona ao histórico
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": generated_image,
                        "type": "image"
                    })
                    
                    # Opção para baixar a imagem
                    img_byte_arr = io.BytesIO()
                    generated_image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    st.download_button(
                        label="Download Image",
                        data=img_byte_arr,
                        file_name=f"generated_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        key=f"download_{datetime.now().timestamp()}"
                    )
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"Sorry, an error occurred: {str(e)}",
                        "type": "text"
                    })
        
        # Javascript para rolar para a última mensagem
        st.markdown('<script>var chatContainer = document.getElementById("chat-container"); chatContainer.scrollTop = chatContainer.scrollHeight;</script>', unsafe_allow_html=True)

    # Seção de exemplos
    st.divider()
    st.markdown("### 📌 Prompt Examples")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Portrait**")
        st.code("A realistic portrait of an elderly woman with wise eyes, intricate facial details, soft studio lighting")

    with col2:
        st.markdown("**Landscape**")
        st.code("A futuristic landscape of a floating city over the ocean at sunset, cyberpunk style, vibrant colors")

    with col3:
        st.markdown("**Concept Art**")
        st.code("A golden mechanical dragon with energy wings, complex details, snowy mountain background, game concept art style")

if __name__ == "__main__":
    main()  