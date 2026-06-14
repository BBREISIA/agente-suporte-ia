# ═══════════════════════════════════════════════════
#   AGENTE DE SUPORTE IA COM BUSCA WEB
#   Bruno Reis | Impulza Digital
#   Stack: Streamlit + LangChain + Groq + Tavily
# ═══════════════════════════════════════════════════

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from tavily import TavilyClient

load_dotenv()

st.set_page_config(
    page_title="Agente de Suporte IA",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

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
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Painel do Agente")
    st.markdown("""
    **🤖 Agente de Suporte IA**

    🦙 Modelo: Llama 3.3 70B  
    ⚡ Powered by Groq (grátis)  
    🔗 Orquestrado por LangChain  
    🌐 Busca web: Tavily
    ---
    """)

    persona = st.selectbox(
        "🎭 Personalidade",
        ["Suporte Formal", "Suporte Amigável", "Especialista Técnico"]
    )

    st.markdown("---")
    st.caption("Desenvolvido por Bruno Reis | Impulza Digital")

PERSONAS = {
    "Suporte Formal": """
Você é um agente de suporte profissional e formal.
Use linguagem respeitosa. Trate o cliente como "senhor(a)".
Responda sempre em português do Brasil.
Quando tiver acesso a informações da web, use-as para dar respostas atualizadas.
""",
    "Suporte Amigável": """
Você é um agente de suporte jovem e amigável.
Use linguagem leve e emojis moderados.
Responda em português do Brasil.
Quando tiver acesso a informações da web, use-as para dar respostas atualizadas.
""",
    "Especialista Técnico": """
Você é um especialista técnico de suporte avançado.
Forneça explicações detalhadas e soluções precisas.
Responda em português do Brasil.
Quando tiver acesso a informações da web, use-as para dar respostas atualizadas.
"""
}

@st.cache_resource
def get_model():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ GROQ_API_KEY não encontrada.")
        st.stop()
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=api_key
    )

def buscar_web(pergunta):
    """Busca informações atuais na web via Tavily"""
    try:
        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key:
            return None
        client = TavilyClient(api_key=tavily_key)
        resultado = client.search(pergunta, max_results=3)
        textos = []
        for r in resultado.get("results", []):
            textos.append(f"- {r['title']}: {r['content'][:300]}")
        return "\n".join(textos)
    except:
        return None

def precisa_busca_web(pergunta):
    """Detecta se a pergunta precisa de informações atuais"""
    palavras = [
        "hoje", "agora", "atual", "atualmente", "recente", "último", "ultima",
        "2024", "2025", "2026", "notícia", "noticia", "resultado", "jogo",
        "placar", "copa", "campeonato", "preço", "cotação", "dólar", "bitcoin",
        "aconteceu", "ocorreu", "quem ganhou", "score"
    ]
    pergunta_lower = pergunta.lower()
    return any(p in pergunta_lower for p in palavras)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_persona" not in st.session_state:
    st.session_state.current_persona = persona

if st.session_state.current_persona != persona:
    st.session_state.messages = []
    st.session_state.current_persona = persona

st.title("🤖 Agente de Suporte IA")
st.caption(f"Modo: {persona}  |  Llama 3.3 70B via Groq  |  🌐 Busca web ativa  |  Impulza Digital")
st.divider()

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.write("👋 Olá! Sou seu agente de suporte com IA e busca web em tempo real. Como posso ajudar?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Digite sua mensagem..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Busca na web se necessário
    contexto_web = ""
    if precisa_busca_web(prompt):
        with st.spinner("🌐 Buscando informações atuais..."):
            resultado = buscar_web(prompt)
            if resultado:
                contexto_web = f"\n\nInformações atuais encontradas na web:\n{resultado}\n\nUse essas informações para responder."

    lc_messages = [SystemMessage(content=PERSONAS[persona] + contexto_web)]
    for m in st.session_state.messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        for chunk in get_model().stream(lc_messages):
            full_response += chunk.content
            response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response.content
    })

st.divider()
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🗑️ Limpar"):
        st.session_state.messages = []
        st.rerun()