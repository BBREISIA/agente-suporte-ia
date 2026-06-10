# ═══════════════════════════════════════════════════
#   AGENTE DE SUPORTE IA
#   Bruno Reis | Impulza Digital
#   Stack: Streamlit + LangChain + Groq (grátis)
#   Modelo: Llama 3.3 70B via Groq API
# ═══════════════════════════════════════════════════

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Carrega a GROQ_API_KEY do arquivo .env
load_dotenv()

# ── CONFIGURAÇÃO DA PÁGINA ─────────────────────────
st.set_page_config(
    page_title="Agente de Suporte IA",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── ESTILO VISUAL ──────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0c0c14; color: #dde1f0; }
    .stChatMessage { border-radius: 12px; margin-bottom: 6px; }
    .stChatInput input {
        background: #13131f;
        border: 1px solid #252538;
        color: #dde1f0;
        border-radius: 10px;
    }
    h1 { color: #f55036 !important; font-weight: 900; }
    .stButton > button {
        background: #f55036;
        color: #fff;
        font-weight: 700;
        border-radius: 8px;
        border: none;
        transition: all .15s;
    }
    .stButton > button:hover { background: #d43e26; }
    .stSelectbox label { color: #636380 !important; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Painel do Agente")
    st.markdown("""
    **🤖 Agente de Suporte IA**

    🦙 Modelo: Llama 3.3 70B  
    ⚡ Powered by Groq (grátis)  
    🔗 Orquestrado por LangChain  
    🎨 Interface: Streamlit

    ---
    Agente com memória de conversa,
    3 personalidades configuráveis
    e deploy 100% gratuito na nuvem.
    ---
    """)

    # Seletor de personalidade
    persona = st.selectbox(
        "🎭 Personalidade",
        ["Suporte Formal", "Suporte Amigável", "Especialista Técnico"]
    )

    st.markdown("---")
    st.caption("Desenvolvido por git initBruno Reis | Impulza Digital")

# ── SYSTEM PROMPTS ─────────────────────────────────
PERSONAS = {
    "Suporte Formal": """
Você é um agente de suporte profissional e formal.
Use linguagem respeitosa e objetiva. Trate o cliente como "senhor(a)".
Resolva problemas de forma clara e estruturada em etapas numeradas.
Responda sempre em português do Brasil.
Quando não souber, seja honesto e ofereça escalar para um humano.
""",
    "Suporte Amigável": """
Você é um agente de suporte jovem, amigável e descontraído.
Use linguagem leve, emojis moderados e crie conexão com o cliente.
Seja empático e resolutivo. Responda em português do Brasil.
Quando não souber, seja honesto e proponha alternativas criativas.
""",
    "Especialista Técnico": """
Você é um especialista técnico de suporte avançado.
Forneça explicações detalhadas, passos numerados e soluções técnicas precisas.
Use terminologia correta sem ser pedante. Responda em português do Brasil.
Ofereça múltiplas soluções quando possível, da mais simples à mais robusta.
"""
}

# ── INICIALIZAR MODELO GROQ ────────────────────────
@st.cache_resource
def get_model():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ GROQ_API_KEY não encontrada. Verifique o arquivo .env")
        st.stop()
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=api_key
    )

# ── HISTÓRICO DE MENSAGENS ─────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_persona" not in st.session_state:
    st.session_state.current_persona = persona

# Reinicia conversa ao trocar de personalidade
if st.session_state.current_persona != persona:
    st.session_state.messages = []
    st.session_state.current_persona = persona

# ── INTERFACE PRINCIPAL ────────────────────────────
st.title("🤖 Agente de Suporte IA")
st.caption(f"Modo: {persona}  |  Modelo: Llama 3.3 70B via Groq  |  Impulza Digital")
st.divider()

# Boas-vindas na primeira mensagem
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.write("👋 Olá! Sou seu agente de suporte com IA. Como posso ajudar?")

# Exibir histórico da conversa
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── INPUT DO USUÁRIO ───────────────────────────────
if prompt := st.chat_input("Digite sua mensagem..."):

    # Salva e exibe mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Monta histórico para o LangChain
    lc_messages = [SystemMessage(content=PERSONAS[persona])]
    for m in st.session_state.messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))

    # Gera resposta via Groq
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            model = get_model()
            response = model.invoke(lc_messages)
            st.write(response.content)

    # Salva resposta no histórico
    st.session_state.messages.append({
        "role": "assistant",
        "content": response.content
    })

# ── BOTÃO LIMPAR CONVERSA ──────────────────────────
st.divider()
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🗑️ Limpar"):
        st.session_state.messages = []
        st.rerun()