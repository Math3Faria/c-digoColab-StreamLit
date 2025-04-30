import streamlit as st
from PIL import Image
import io
import requests
from datetime import datetime
from googletrans import Translator
import base64  # Adicionado para decodificação base64

# Configuração da página
st.set_page_config(
    page_title="AI Image Generator - Stability AI",
    page_icon="🎨",
    layout="wide"
)

# Dimensões permitidas para SDXL
ALLOWED_DIMENSIONS = [
    (1024, 1024), 
    (1152, 896), (896, 1152),
    (1216, 832), (832, 1216),
    (1344, 768), (768, 1344),
    (1536, 640), (640, 1536)
]

# Sidebar para configurações
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Enter your Stability AI API Key", type="password")
    st.markdown("[Get API Key](https://platform.stability.ai/)")
    
    st.divider()
    st.markdown("### Generation Parameters")
    cfg_scale = st.slider("Creativity (CFG Scale)", 1.0, 20.0, 7.0)
    steps = st.slider("Steps", 10, 150, 30)
    
    # Selecionador de dimensões permitidas
    dimension_options = [f"{w}×{h}" for w, h in ALLOWED_DIMENSIONS]
    selected_dim = st.selectbox("Dimensions", dimension_options, index=0)
    width, height = map(int, selected_dim.split('×'))
    
    sampler = st.selectbox("Sampling Method", [
        "DDIM", "DDPM", "K_DPMPP_2M", "K_DPMPP_2S_ANCESTRAL", 
        "K_DPM_2", "K_DPM_2_ANCESTRAL", "K_EULER", 
        "K_EULER_ANCESTRAL", "K_HEUN", "K_LMS"
    ], index=6)
    
    st.divider()
    st.markdown("Made with ❤️ using [Stability AI](https://stability.ai/) and [Streamlit](https://streamlit.io/)")

# Interface principal
st.title("🎨 AI Image Generator with Stability AI")
st.caption("Describe the image you want and Stable Diffusion XL will generate it for you!")

# Inicializa o histórico de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "image":
            st.image(message["content"])

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
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Verifica se a API key foi fornecida
    if not api_key:
        st.error("Please enter your Stability AI API Key")
        st.stop()
    
    # Resposta do assistente
    with st.chat_message("assistant"):
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
                    mime="image/png"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Sorry, an error occurred: {str(e)}",
                    "type": "text"
                })

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