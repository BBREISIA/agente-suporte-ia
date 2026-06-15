# ═══════════════════════════════════════════════════
#   AGENTE DE SUPORTE IA — VISUAL PREMIUM
#   Bruno Reis | Impulza Digital
#   Stack: Streamlit + LangChain + Groq + Tavily
# ═══════════════════════════════════════════════════

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from tavily import TavilyClient
from datetime import datetime

load_dotenv()

st.set_page_config(
    page_title="Agente de Suporte IA | Impulza Digital",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── BASE ── */
* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #080810 !important; }
section[data-testid="stSidebar"] { background: #0d0d1a !important; border-right: 1px solid #1a1a2e; }

/* ── ESCONDER ELEMENTOS PADRÃO ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── HERO HEADER ── */
.hero-header {
    background: linear-gradient(135deg, #0d0d1a 0%, #111128 50%, #0a0a18 100%);
    border: 1px solid #1e1e3a;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}

.hero-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(245,80,54,0.12) 0%, transparent 70%);
    pointer-events: none;
}

.hero-header::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 100px;
    width: 150px; height: 150px;
    background: radial-gradient(circle, rgba(34,211,165,0.08) 0%, transparent 70%);
    pointer-events: none;
}

.hero-title {
    font-size: 28px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    margin: 0 0 6px 0 !important;
    letter-spacing: -0.5px;
    line-height: 1.2;
}

.hero-title span { color: #f55036; }

.hero-sub {
    color: #4a4a6a;
    font-size: 13px;
    font-weight: 400;
    margin: 0;
}

.hero-badges {
    display: flex;
    gap: 8px;
    margin-top: 16px;
    flex-wrap: wrap;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 500;
    color: #6b6b8a;
}

.badge-green { border-color: rgba(34,211,165,0.2); color: #22d3a5; background: rgba(34,211,165,0.06); }
.badge-orange { border-color: rgba(245,80,54,0.2); color: #f55036; background: rgba(245,80,54,0.06); }
.badge-blue { border-color: rgba(91,141,238,0.2); color: #5b8dee; background: rgba(91,141,238,0.06); }

/* ── CHAT MESSAGES ── */
.stChatMessage {
    background: #0d0d1a !important;
    border: 1px solid #1a1a2e !important;
    border-radius: 14px !important;
    padding: 16px !important;
    margin-bottom: 12px !important;
}

.stChatMessage[data-testid="chat-message-user"] {
    background: #111128 !important;
    border-color: #1e1e3a !important;
}

.stChatMessage p {
    color: #c8cce8 !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    margin: 0 !important;
}

/* ── INPUT ── */
.stChatInput {
    background: #0d0d1a !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 12px !important;
    padding: 4px !important;
}

.stChatInput textarea {
    background: transparent !important;
    color: #c8cce8 !important;
    font-size: 14px !important;
    border: none !important;
}

.stChatInput button {
    background: #f55036 !important;
    border-radius: 8px !important;
    border: none !important;
}

/* ── SIDEBAR ── */
.sidebar-logo {
    background: linear-gradient(135deg, rgba(245,80,54,0.1), rgba(34,211,165,0.05));
    border: 1px solid rgba(245,80,54,0.2);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
    text-align: center;
}

.sidebar-logo h2 {
    font-size: 16px !important;
    font-weight: 800 !important;
    color: #fff !important;
    margin: 8px 0 2px 0 !important;
}

.sidebar-logo p {
    font-size: 11px !important;
    color: #4a4a6a !important;
    margin: 0 !important;
}

.stat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.stat-number {
    font-size: 22px;
    font-weight: 800;
    color: #f55036;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}

.stat-label {
    font-size: 11px;
    color: #4a4a6a;
    margin-top: 2px;
}

/* ── SELECTBOX ── */
.stSelectbox > div > div {
    background: #111128 !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 10px !important;
    color: #c8cce8 !important;
}

/* ── BUTTON ── */
.stButton > button {
    background: #111128 !important;
    color: #f55036 !important;
    border: 1px solid rgba(245,80,54,0.3) !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 6px 14px !important;
    transition: all 0.15s !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: rgba(245,80,54,0.1) !important;
    border-color: #f55036 !important;
}

/* ── DIVIDER ── */
hr { border-color: #1a1a2e !important; margin: 16px 0 !important; }

/* ── SPINNER ── */
.stSpinner > div { border-top-color: #f55036 !important; }

/* ── WELCOME CARD ── */
.welcome-card {
    background: linear-gradient(135deg, #0d0d1a, #111128);
    border: 1px solid #1e1e3a;
    border-radius: 14px;
    padding: 32px;
    text-align: center;
    margin: 20px 0;
}

.welcome-card h3 {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #fff !important;
    margin-bottom: 8px !important;
}

.welcome-card p {
    color: #4a4a6a !important;
    font-size: 13px !important;
}

.welcome-suggestions {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 16px;
}

.suggestion {
    background: rgba(255,255,255,0.04);
    border: 1px solid #1e1e3a;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    color: #6b6b8a;
    cursor: pointer;
}

/* ── STATUS BAR ── */
.status-bar {
    background: #0d0d1a;
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    font-size: 12px;
    color: #4a4a6a;
}

.status-online {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #22d3a5;
    font-weight: 600;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #22d3a5;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── TIMESTAMP ── */
.msg-time {
    font-size: 10px;
    color: #2a2a4a;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 6px;
    text-align: right;
}

/* ── SEARCH INDICATOR ── */
.search-indicator {
    background: rgba(34,211,165,0.06);
    border: 1px solid rgba(34,211,165,0.15);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    color: #22d3a5;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}
</style>
""", unsafe_allow_html=True)

# ── INICIALIZAR ESTADO ─────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_msgs" not in st.session_state:
    st.session_state.total_msgs = 0
if "web_searches" not in st.session_state:
    st.session_state.web_searches = 0

# ── SIDEBAR ────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:32px">🤖</div>
        <h2>Impulza Digital</h2>
        <p>Agente de Suporte com IA</p>
    </div>
    """, unsafe_allow_html=True)

    persona = st.selectbox(
        "🎭 Personalidade do Agente",
        ["Suporte Formal", "Suporte Amigável", "Especialista Técnico"],
        help="Cada personalidade tem um estilo diferente de resposta"
    )

    st.markdown("---")
    st.markdown("**📊 Sessão atual**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div>
                <div class="stat-number">{len(st.session_state.messages)}</div>
                <div class="stat-label">Mensagens</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div>
                <div class="stat-number" style="color:#22d3a5">{st.session_state.web_searches}</div>
                <div class="stat-label">Buscas web</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**⚙️ Stack técnica**")
    st.markdown("""
    <div style="display:flex;flex-direction:column;gap:6px;margin-top:8px">
        <div class="badge badge-orange">🦙 Llama 3.3 70B</div>
        <div class="badge badge-orange">⚡ Groq API</div>
        <div class="badge badge-blue">🔗 LangChain</div>
        <div class="badge badge-green">🌐 Tavily Search</div>
        <div class="badge">🎨 Streamlit</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Limpar conversa"):
        st.session_state.messages = []
        st.session_state.web_searches = 0
        st.rerun()

    st.markdown("""
    <div style="margin-top:16px;padding:12px;background:rgba(255,255,255,0.02);border-radius:8px;border:1px solid #1a1a2e">
        <div style="font-size:11px;color:#2a2a4a;text-align:center">
            Desenvolvido por<br>
            <span style="color:#f55036;font-weight:600">Bruno Reis</span><br>
            <span style="color:#2a2a4a">Impulza Digital</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── PERSONAS ───────────────────────────────────────
PERSONAS = {
    "Suporte Formal": """
Você é um agente de suporte profissional e formal da Impulza Digital.
Use linguagem respeitosa e objetiva. Trate o cliente como "senhor(a)".
Resolva problemas de forma clara em etapas numeradas.
Responda sempre em português do Brasil.
Quando tiver informações da web, use-as para respostas atualizadas.
""",
    "Suporte Amigável": """
Você é um agente de suporte jovem, amigável e descontraído da Impulza Digital.
Use linguagem leve, emojis moderados e crie conexão com o cliente.
Seja empático e resolutivo. Responda em português do Brasil.
Quando tiver informações da web, use-as para respostas atualizadas.
""",
    "Especialista Técnico": """
Você é um especialista técnico de suporte avançado da Impulza Digital.
Forneça explicações detalhadas, passos numerados e soluções precisas.
Responda em português do Brasil.
Quando tiver informações da web, use-as para respostas atualizadas.
"""
}

# ── FUNÇÕES ────────────────────────────────────────
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
    palavras = [
        "hoje", "agora", "atual", "atualmente", "recente", "último", "ultima",
        "2024", "2025", "2026", "notícia", "noticia", "resultado", "jogo",
        "placar", "copa", "campeonato", "preço", "cotação", "dólar", "bitcoin",
        "aconteceu", "ocorreu", "quem ganhou", "score", "temperatura", "clima"
    ]
    return any(p in pergunta.lower() for p in palavras)

# ── VERIFICAR MUDANÇA DE PERSONA ───────────────────
if "current_persona" not in st.session_state:
    st.session_state.current_persona = persona
if st.session_state.current_persona != persona:
    st.session_state.messages = []
    st.session_state.current_persona = persona

# ── HERO HEADER ────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
    <p class="hero-title">🤖 Agente de <span>Suporte IA</span></p>
    <p class="hero-sub">Powered by Llama 3.3 70B · Groq · LangChain · Busca web em tempo real</p>
    <div class="hero-badges">
        <span class="badge badge-green">● Online</span>
        <span class="badge badge-orange">⚡ {persona}</span>
        <span class="badge badge-blue">🌐 Busca web ativa</span>
        <span class="badge">💬 {len(st.session_state.messages)} mensagens</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── BOAS-VINDAS ────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <h3>👋 Olá! Como posso ajudar?</h3>
        <p>Sou um agente de suporte com IA e acesso à internet em tempo real.<br>
        Faça qualquer pergunta — sobre produtos, suporte técnico ou informações atuais.</p>
        <div class="welcome-suggestions">
            <span class="suggestion">💰 Qual a cotação do dólar?</span>
            <span class="suggestion">⚽ Resultados do futebol</span>
            <span class="suggestion">🤖 O que é inteligência artificial?</span>
            <span class="suggestion">📱 Como posso te contratar?</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── HISTÓRICO ──────────────────────────────────────
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "time" in msg:
            st.markdown(f'<div class="msg-time">{msg["time"]}</div>', unsafe_allow_html=True)

# ── INPUT ──────────────────────────────────────────
if prompt := st.chat_input("Digite sua mensagem..."):
    now = datetime.now().strftime("%H:%M")

    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": now
    })

    with st.chat_message("user"):
        st.write(prompt)
        st.markdown(f'<div class="msg-time">{now}</div>', unsafe_allow_html=True)

    # Busca web se necessário
    contexto_web = ""
    if precisa_busca_web(prompt):
        st.markdown('<div class="search-indicator">🌐 Buscando informações atuais na web...</div>', unsafe_allow_html=True)
        resultado = buscar_web(prompt)
        if resultado:
            contexto_web = f"\n\nInformações atuais da web:\n{resultado}\n\nUse essas informações."
            st.session_state.web_searches += 1

    # Monta histórico para LangChain
    lc_messages = [SystemMessage(content=PERSONAS[persona] + contexto_web)]
    for m in st.session_state.messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))

    # Streaming da resposta
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        for chunk in get_model().stream(lc_messages):
            full_response += chunk.content
            response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
        resp_time = datetime.now().strftime("%H:%M")
        st.markdown(f'<div class="msg-time">{resp_time}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "time": resp_time
    })

    st.rerun()