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
NOME_ASSISTENTE = "Gerador de Imagens com IA"
EMOJI_AVATAR_USUARIO = "👤"
URL_IMAGEM_DE_FUNDO = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjduZ2l2MmhjaWx4OWE5eXdvcjBvcWlianYxY2w5NTc4eW91YXlrZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3ov9jJuT2pEVMRMas0/giphy.gif"

# Configuração da página
st.set_page_config(
    page_title=NOME_ASSISTENTE,
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Dimensões permitidas para SDXL
DIMENSOES_PERMITIDAS = [
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
        {f"background-image: url('{URL_IMAGEM_DE_FUNDO}'); background-size: cover; background-repeat: no-repeat;" if URL_IMAGEM_DE_FUNDO else ""}
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
        <h1>{NOME_ASSISTENTE}</h1>
    </div>
    """, unsafe_allow_html=True)

    # Barra lateral para configurações
    with st.sidebar:
        st.title("⚙️ Configurações")
        chave_api = st.text_input("Insira sua chave da API Stability AI", type="password")
        st.markdown("[Obter Chave da API](https://platform.stability.ai/)")

        st.divider()
        st.markdown("### Parâmetros de Geração")
        escala_cfg = st.slider("Criatividade (Escala CFG)", 1.0, 20.0, 7.0)
        passos = st.slider("Passos", 10, 150, 30)

        # Selecionador de dimensões permitidas
        opcoes_dimensao = [f"{w}×{h}" for w, h in DIMENSOES_PERMITIDAS]
        dimensao_selecionada = st.selectbox("Dimensões", opcoes_dimensao, index=0)
        largura, altura = map(int, dimensao_selecionada.split('×'))

        metodo_amostragem = st.selectbox("Método de Amostragem", [
            "DDIM", "DDPM", "K_DPMPP_2M", "K_DPMPP_2S_ANCESTRAL",
            "K_DPM_2", "K_DPM_2_ANCESTRAL", "K_EULER",
            "K_EULER_ANCESTRAL", "K_HEUN", "K_LMS"
        ], index=6)

        st.divider()
        st.markdown(f"Feito com ❤️ usando [Stability AI](https://stability.ai/) e [Streamlit](https://streamlit.io/) em {datetime.now().year}")

    # Inicializa o histórico de chat
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [{"role": "assistant", "content": "Descreva a imagem que você quer criar e eu a gerarei para você!"}]

    # Container para as mensagens com barra de rolagem
    with st.container():
        container_chat = st.markdown('<div class="chat-messages-container" id="chat-container">', unsafe_allow_html=True)

        # Exibe o histórico de mensagens
        for mensagem in st.session_state.mensagens:
            role = mensagem["role"]
            conteudo = mensagem["content"]
            avatar_exibicao = AVATAR_ANIMATED_URL if role == "assistant" else EMOJI_AVATAR_USUARIO
            with st.chat_message(role, avatar=avatar_exibicao):
                if "type" in mensagem and mensagem["type"] == "image":
                    st.image(conteudo)
                else:
                    st.markdown(conteudo)

        st.markdown('</div>', unsafe_allow_html=True)

    # Função para traduzir para inglês
    def traduzir_para_ingles(texto):
        try:
            tradutor = Translator()
            traducao = tradutor.translate(texto, dest='en')
            return traducao.text
        except:
            return texto  # Se falhar, retorna o texto original

    # Função para gerar imagens usando a API do Stability AI
    def gerar_imagem_com_stability(prompt, chave_api, escala_cfg, passos, largura, altura, metodo_amostragem):
        engine_id = "stable-diffusion-xl-1024-v1-0"
        api_host = "https://api.stability.ai"

        # Garante que o prompt está em inglês
        prompt_ingles = traduzir_para_ingles(prompt)

        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {chave_api}"
            },
            json={
                "text_prompts": [{"text": prompt_ingles}],
                "cfg_scale": escala_cfg,
                "height": altura,
                "width": largura,
                "samples": 1,
                "steps": passos,
                "sampler": metodo_amostragem,
            },
        )

        if response.status_code != 200:
            raise Exception(f"Erro na API: {response.text}")

        data = response.json()

        # Corrige o tratamento da imagem base64
        dados_imagem = base64.b64decode(data["artifacts"][0]["base64"])  # Decodifica a string base64 para bytes
        return Image.open(io.BytesIO(dados_imagem))

    # Input do usuário
    if prompt_usuario := st.chat_input("Descreva a imagem que você quer criar..."):
        # Adiciona a mensagem do usuário ao histórico
        st.session_state.mensagens.append({
            "role": "user",
            "content": prompt_usuario,
            "type": "text"
        })

        with st.chat_message("user", avatar=EMOJI_AVATAR_USUARIO):
            st.markdown(prompt_usuario)

        # Verifica se a chave da API foi fornecida
        if not chave_api:
            st.error("Por favor, insira sua chave da API Stability AI")
            st.stop()

        # Resposta do assistente
        with st.chat_message("assistant", avatar=AVATAR_ANIMATED_URL):
            with st.spinner("Gerando sua imagem..."):
                try:
                    # Gera a imagem
                    imagem_gerada = gerar_imagem_com_stability(
                        prompt=prompt_usuario,
                        chave_api=chave_api,
                        escala_cfg=st.session_state.get('escala_cfg', 7.0),  # Use st.session_state para persistir
                        passos=passos,
                        largura=largura,
                        altura=altura,
                        metodo_amostragem=metodo_amostragem
                    )

                    # Exibe a imagem
                    st.image(imagem_gerada, use_column_width=True)

                    # Adiciona ao histórico
                    st.session_state.mensagens.append({
                        "role": "assistant",
                        "content": imagem_gerada,
                        "type": "image"
                    })

                    # Opção para baixar a imagem
                    buffer_imagem = io.BytesIO()
                    imagem_gerada.save(buffer_imagem, format='PNG')
                    bytes_imagem = buffer_imagem.getvalue()

                    st.download_button(
                        label="Baixar Imagem",
                        data=bytes_imagem,
                        file_name=f"imagem_gerada_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        key=f"download_{datetime.now().timestamp()}"
                    )

                except Exception as e:
                    st.error(f"Ocorreu um erro: {str(e)}")
                    st.session_state.mensagens.append({
                        "role": "assistant",
                        "content": f"Desculpe, ocorreu um erro: {str(e)}",
                        "type": "text"
                    })

        # Javascript para rolar para a última mensagem
        st.markdown('<script>var chatContainer = document.getElementById("chat-container"); chatContainer.scrollTop = chatContainer.scrollHeight;</script>', unsafe_allow_html=True)

    # Seção de exemplos
    st.divider()
    st.markdown("### 📌 Exemplos de Prompt")