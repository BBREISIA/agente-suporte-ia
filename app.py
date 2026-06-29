# ═══════════════════════════════════════════════════
#   AGENTE DE SUPORTE IA — VISUAL PREMIUM v4
#   Bruno Reis | Impulza Digital
#   Stack: Streamlit + LangChain + Groq + Tavily
#   Novidade: Painel de cotação do dólar em tempo real
# ═══════════════════════════════════════════════════

import streamlit as st
import os
import requests
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

* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #080810 !important; }
section[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 1px solid #1a1a2e;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── CORRIGIR ÍCONES MATERIAL QUEBRADOS (fonte pode falhar offline) ── */
/* Esconde qualquer texto cru de ícone de fonte que não carregou */
span[class*="material-icons"],
span[class*="material-symbols"],
[data-testid="stIconMaterial"] {
    font-size: 0 !important;
    line-height: 0 !important;
    color: transparent !important;
}
span[class*="material-icons"]::before,
span[class*="material-symbols"]::before {
    content: "" !important;
}
/* Botão de colapsar a sidebar - usa um símbolo simples sem depender de fonte externa */
[data-testid="collapsedControl"] button {
    font-size: 0 !important;
}
[data-testid="collapsedControl"] button::after {
    content: "☰";
    font-size: 18px !important;
    color: #f55036;
}

/* ── EVITAR CORTE DE TEXTO/EMOJI NOS BADGES ── */
.badge, .fh-badge, .rank-name, .rank-company {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
}
.stDeployButton { display: none; }

/* ── CABEÇALHO FIXO ── */
.fixed-header {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 999;
    background: rgba(8,8,16,0.97);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid #1a1a2e;
    padding: 12px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.fh-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.fh-logo { font-size: 22px; line-height: 1; }

.fh-title {
    font-size: 16px !important;
    font-weight: 800 !important;
    color: #fff !important;
    margin: 0 !important;
    letter-spacing: -0.3px;
}

.fh-title span { color: #f55036; }

.fh-sub {
    font-size: 10px !important;
    color: #3a3a5a !important;
    margin: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.fh-right { display: flex; align-items: center; gap: 8px; }

.fh-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid;
}

.fh-online { background: rgba(34,211,165,0.08); border-color: rgba(34,211,165,0.25); color: #22d3a5; }
.fh-model  { background: rgba(245,80,54,0.08);  border-color: rgba(245,80,54,0.2);  color: #f55036; }
.fh-msgs   { background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.08); color: #6b6b8a; }

.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22d3a5;
    animation: pulse 2s infinite;
    display: inline-block;
}

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

.main-spacer { height: 68px; }

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
    padding: 14px;
    margin-bottom: 16px;
    text-align: center;
}

.sidebar-logo h2 {
    font-size: 15px !important;
    font-weight: 800 !important;
    color: #fff !important;
    margin: 6px 0 2px 0 !important;
}

.sidebar-logo p {
    font-size: 10px !important;
    color: #4a4a6a !important;
    margin: 0 !important;
}

.stat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 6px;
}

.stat-number {
    font-size: 20px;
    font-weight: 800;
    color: #f55036;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}

.stat-label { font-size: 10px; color: #4a4a6a; margin-top: 2px; }

/* ── RANKING ── */
.rank-title {
    font-size: 11px !important;
    font-weight: 700 !important;
    color: #6b6b8a !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px !important;
}

.rank-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255,255,255,0.02);
    border: 1px solid #1a1a2e;
    border-radius: 8px;
    padding: 8px 10px;
    margin-bottom: 5px;
}

.rank-left { display: flex; align-items: center; gap: 8px; }
.rank-pos { font-size: 13px; line-height: 1; }
.rank-name { font-size: 12px; font-weight: 700; color: #c8cce8; line-height: 1.2; }
.rank-company { font-size: 9px; color: #3a3a5a; }
.rank-pct { font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

/* ── BADGE ── */
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
    margin-bottom: 5px;
    width: 100%;
    box-sizing: border-box;
}

.badge-green { border-color: rgba(34,211,165,0.2); color: #22d3a5; background: rgba(34,211,165,0.06); }
.badge-orange { border-color: rgba(245,80,54,0.2); color: #f55036; background: rgba(245,80,54,0.06); }
.badge-blue { border-color: rgba(91,141,238,0.2); color: #5b8dee; background: rgba(91,141,238,0.06); }

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
    transition: all 0.15s !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: rgba(245,80,54,0.1) !important;
    border-color: #f55036 !important;
}

hr { border-color: #1a1a2e !important; margin: 12px 0 !important; }
.stSpinner > div { border-top-color: #f55036 !important; }

/* ── WELCOME CARD ── */
.welcome-card {
    background: linear-gradient(135deg, #0d0d1a, #111128);
    border: 1px solid #1e1e3a;
    border-radius: 14px;
    padding: 28px 32px;
    text-align: center;
    margin-bottom: 20px;
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
    margin-bottom: 0 !important;
}

/* ── PAINEL DO DÓLAR ── */
.dolar-panel {
    background: linear-gradient(135deg, rgba(34,211,165,0.08), rgba(34,211,165,0.02));
    border: 1px solid rgba(34,211,165,0.2);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 18px auto;
    max-width: 280px;
}

.dolar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: #6b6b8a;
    font-weight: 600;
    margin-bottom: 8px;
}

.dolar-date {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #3a3a5a;
}

.dolar-value {
    font-size: 28px;
    font-weight: 800;
    color: #22d3a5;
    font-family: 'JetBrains Mono', monospace;
    text-align: center;
    margin: 6px 0;
}

.dolar-details {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #4a4a6a;
    font-family: 'JetBrains Mono', monospace;
}

.suggestions-row {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 16px;
}

.suggestion-chip {
    background: rgba(255,255,255,0.04);
    border: 1px solid #1e1e3a;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 12px;
    color: #6b6b8a;
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
}

/* ── FONTES CONSULTADAS ── */
.fontes-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    padding: 10px 14px;
    margin-top: 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.fontes-label {
    font-size: 10px;
    font-weight: 700;
    color: #4a4a6a;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
}

.fonte-link {
    font-size: 12px;
    color: #5b8dee !important;
    text-decoration: none !important;
    display: block;
    padding: 4px 8px;
    background: rgba(91,141,238,0.06);
    border-radius: 6px;
    border: 1px solid rgba(91,141,238,0.12);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.fonte-link:hover {
    background: rgba(91,141,238,0.12) !important;
    border-color: rgba(91,141,238,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ── ESTADO ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "web_searches" not in st.session_state:
    st.session_state.web_searches = 0

# ── DADOS DO RANKING ───────────────────────────────
RANKING_IAS = [
    {"pos": "🥇", "nome": "ChatGPT",  "empresa": "OpenAI",    "cor": "#10a37f", "uso": "92%"},
    {"pos": "🥈", "nome": "Gemini",   "empresa": "Google",    "cor": "#4285f4", "uso": "78%"},
    {"pos": "🥉", "nome": "Copilot",  "empresa": "Microsoft", "cor": "#0078d4", "uso": "65%"},
    {"pos": "4️⃣", "nome": "Claude",   "empresa": "Anthropic", "cor": "#f55036", "uso": "54%"},
    {"pos": "5️⃣", "nome": "Llama",    "empresa": "Meta",      "cor": "#0866ff", "uso": "41%"},
    {"pos": "6️⃣", "nome": "Grok",     "empresa": "xAI",       "cor": "#a0a0b0", "uso": "28%"},
]

# ── SIDEBAR ────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:28px">🤖</div>
        <h2>Impulza Digital</h2>
        <p>Agente de Suporte com IA</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📊 Sessão atual**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.messages)}</div>
            <div class="stat-label">Mensagens</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:#22d3a5">{st.session_state.web_searches}</div>
            <div class="stat-label">Buscas web</div>
        </div>
        """, unsafe_allow_html=True)

    # ── RANKING ──
    st.markdown("---")
    st.markdown('<div class="rank-title">🏆 Ranking IAs — 2025</div>', unsafe_allow_html=True)

    for ia in RANKING_IAS:
        st.markdown(f"""
        <div class="rank-item" style="border-left: 3px solid {ia['cor']}">
            <div class="rank-left">
                <span class="rank-pos">{ia['pos']}</span>
                <div>
                    <div class="rank-name">{ia['nome']}</div>
                    <div class="rank-company">{ia['empresa']}</div>
                </div>
            </div>
            <div class="rank-pct" style="color:{ia['cor']}">{ia['uso']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:9px;color:#2a2a4a;text-align:right;margin-top:4px;font-family:'JetBrains Mono',monospace">
        📊 Dados de adoção · 2025
    </div>
    """, unsafe_allow_html=True)

    # ── STACK TÉCNICA ──
    st.markdown("---")
    st.markdown("**⚙️ Stack técnica**")
    st.markdown("""
    <div style="display:flex;flex-direction:column;gap:4px;margin-top:8px">
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
    <div style="margin-top:12px;padding:10px;background:rgba(255,255,255,0.02);border-radius:8px;border:1px solid #1a1a2e;text-align:center">
        <div style="font-size:10px;color:#2a2a4a">
            Desenvolvido por<br>
            <span style="color:#f55036;font-weight:700">Bruno Reis</span>
            <span style="color:#2a2a4a"> · Impulza Digital</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── DOMÍNIOS DE ATENDIMENTO (detectados automaticamente) ──
DOMINIOS = {
    "Bancário": {
        "icone": "🏦",
        "cor": "#f5c518",
        "prompt": """
Você é um agente de suporte especializado em produtos bancários e financeiros da Impulza Digital.
Domine assuntos como: conta corrente, cartão de crédito, empréstimos, investimentos, Pix, taxas e tarifas.
Use linguagem clara e precisa sobre termos financeiros. Trate o cliente como "senhor(a)".
Resolva problemas em etapas numeradas. Responda em português do Brasil.
Quando tiver informações da web, use-as para respostas atualizadas.
"""
    },
    "E-commerce": {
        "icone": "🛒",
        "cor": "#5b8dee",
        "prompt": """
Você é um agente de suporte especializado em e-commerce da Impulza Digital.
Domine assuntos como: rastreamento de pedidos, prazos de entrega, trocas, devoluções e reembolsos.
Seja prático e resolutivo, com linguagem acessível. Responda em português do Brasil.
Quando tiver informações da web, use-as para respostas atualizadas.
"""
    },
    "Técnico": {
        "icone": "💻",
        "cor": "#22d3a5",
        "prompt": """
Você é um especialista técnico de suporte avançado da Impulza Digital.
Domine assuntos como: bugs, erros de API, integrações, configuração de sistemas e troubleshooting.
Forneça explicações detalhadas, passos numerados e soluções precisas.
Responda em português do Brasil.
Quando tiver informações da web, use-as para respostas atualizadas.
"""
    },
    "Geral": {
        "icone": "🤖",
        "cor": "#6b6b8a",
        "prompt": """
Você é um agente de suporte geral da Impulza Digital, atencioso e resolutivo.
Responda com clareza qualquer tipo de pergunta. Responda em português do Brasil.
Quando tiver informações da web, use-as para respostas atualizadas.
"""
    }
}

def detectar_dominio(pergunta):
    """Detecta automaticamente qual domínio de atendimento a pergunta pertence"""
    p = pergunta.lower()

    palavras_bancario = [
        "conta", "cartão", "cartao", "empréstimo", "emprestimo", "investimento",
        "pix", "taxa", "tarifa", "banco", "saldo", "extrato", "fatura",
        "cdb", "poupança", "poupanca", "financiamento", "crédito", "credito"
    ]
    palavras_ecommerce = [
        "pedido", "entrega", "troca", "devolução", "devolucao", "reembolso",
        "rastreio", "rastreamento", "comprei", "comprar", "frete", "produto",
        "cancelar pedido", "nota fiscal"
    ]
    palavras_tecnico = [
        "erro", "bug", "api", "integração", "integracao", "código", "codigo",
        "configurar", "instalar", "não funciona", "nao funciona", "travou",
        "sistema", "servidor", "deploy", "função", "funcao"
    ]

    if any(p2 in p for p2 in palavras_bancario):
        return "Bancário"
    elif any(p2 in p for p2 in palavras_ecommerce):
        return "E-commerce"
    elif any(p2 in p for p2 in palavras_tecnico):
        return "Técnico"
    return "Geral"

# ── FUNÇÕES ────────────────────────────────────────
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

def buscar_web(pergunta):
    """Busca na web e retorna texto + lista de fontes (título + url)"""
    try:
        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key:
            return None, []
        client = TavilyClient(api_key=tavily_key)
        resultado = client.search(pergunta, max_results=3)
        textos = []
        fontes = []
        for r in resultado.get("results", []):
            textos.append(f"- {r['title']}: {r['content'][:300]}")
            fontes.append({
                "titulo": r.get("title", "Fonte"),
                "url": r.get("url", "")
            })
        return "\n".join(textos), fontes
    except Exception:
        return None, []

def precisa_busca_web(pergunta):
    """
    Usa o próprio modelo de IA para decidir se a pergunta precisa de
    informações atuais da web. Muito mais confiável que lista de palavras-chave,
    pois entende o CONTEXTO da pergunta, não só termos exatos.
    """
    # Lista de gatilhos óbvios primeiro (resposta instantânea, sem gastar chamada de API)
    gatilhos_obvios = [
        "hoje", "agora", "atual", "atualmente", "recente", "última", "ultima",
        "2024", "2025", "2026", "notícia", "noticia", "resultado", "jogo",
        "placar", "copa", "campeonato", "preço", "preco", "cotação", "cotacao",
        "dólar", "dolar", "bitcoin", "aconteceu", "ocorreu", "quem ganhou",
        "score", "temperatura", "clima", "eleição", "eleicao", "presidente",
        "governo", "mercado", "bolsa", "quem é", "quem e", "o que é",
        "quando foi", "quando será", "quando sera", "data de", "lançamento",
        "lancamento", "versão", "versao", "última versão", "ultima versao"
    ]
    if any(g in pergunta.lower() for g in gatilhos_obvios):
        return True

    # Para perguntas que não bateram com nenhum gatilho óbvio,
    # pergunta ao próprio modelo se ele tem certeza da resposta
    try:
        classificador = get_model()
        resposta = classificador.invoke([
            SystemMessage(content=(
                "Responda APENAS 'SIM' ou 'NAO' (sem pontuação, sem explicação). "
                "Responda SIM se a pergunta do usuário exigir informação atual, "
                "recente, específica de fatos do mundo real, dados numéricos exatos, "
                "versões de software, eventos, preços ou qualquer coisa que possa "
                "ter mudado ou que você não tenha certeza absoluta de saber. "
                "Responda NAO se for uma pergunta conceitual, atemporal, de "
                "conhecimento geral estável, ou conversa casual."
            )),
            HumanMessage(content=pergunta)
        ])
        return "SIM" in resposta.content.upper()
    except Exception:
        # Em caso de falha na classificação, prefere buscar (mais seguro)
        return False

@st.cache_data(ttl=300)  # Atualiza no máximo a cada 5 minutos
def buscar_cotacao_dolar():
    """Busca cotação atual do dólar — tenta 2 fontes diferentes (fallback)"""
    # Fonte 1: AwesomeAPI
    try:
        resposta = requests.get(
            "https://economia.awesomeapi.com.br/json/last/USD-BRL",
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if resposta.status_code == 200:
            dados = resposta.json()
            valor = dados["USDBRL"]
            return {
                "compra": float(valor["bid"]),
                "venda": float(valor["ask"]),
                "variacao": float(valor["pctChange"]),
            }
    except Exception:
        pass

    # Fonte 2: exchangerate-api (fallback gratuito, sem necessidade de key)
    try:
        resposta = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=8
        )
        if resposta.status_code == 200:
            dados = resposta.json()
            taxa = dados["rates"]["BRL"]
            return {
                "compra": float(taxa) - 0.01,
                "venda": float(taxa),
                "variacao": 0.0,
            }
    except Exception:
        pass

    return None

def buscar_cotacao(moeda="USD"):
    """Busca cotação de qualquer moeda suportada via API gratuita"""
    try:
        resposta = requests.get(
            f"https://economia.awesomeapi.com.br/json/last/{moeda}-BRL",
            timeout=5
        )
        dados = resposta.json()
        chave = f"{moeda}BRL"
        if chave in dados:
            valor = dados[chave]
            return {
                "moeda": moeda,
                "compra": valor["bid"],
                "venda": valor["ask"],
                "variacao": valor["pctChange"],
                "hora": valor["create_date"]
            }
        return None
    except:
        return None

def detectar_moeda(pergunta):
    """Detecta qual moeda o usuário está perguntando"""
    p = pergunta.lower()
    if "dólar" in p or "dolar" in p or "usd" in p:
        return "USD"
    elif "euro" in p or "eur" in p:
        return "EUR"
    elif "bitcoin" in p or "btc" in p:
        return "BTC"
    elif "libra" in p or "gbp" in p:
        return "GBP"
    return None

# ── ESTADO DO DOMÍNIO ATUAL (atualizado a cada pergunta) ──
if "dominio_atual" not in st.session_state:
    st.session_state.dominio_atual = "Geral"

dominio_info = DOMINIOS[st.session_state.dominio_atual]

# ── CABEÇALHO FIXO ─────────────────────────────────
num_msgs = len(st.session_state.messages)
st.markdown(f"""
<div class="fixed-header">
    <div class="fh-left">
        <div class="fh-logo">🤖</div>
        <div>
            <div class="fh-title">Agente de <span>Suporte IA</span></div>
            <div class="fh-sub">Impulza Digital · Llama 3.3 70B · Groq · LangChain</div>
        </div>
    </div>
    <div class="fh-right">
        <span class="fh-badge fh-online"><span class="status-dot"></span> Online</span>
        <span class="fh-badge fh-model" style="color:{dominio_info['cor']};border-color:{dominio_info['cor']}40;background:{dominio_info['cor']}14">{dominio_info['icone']} Modo: {st.session_state.dominio_atual}</span>
        <span class="fh-badge fh-msgs">💬 {num_msgs} msgs</span>
    </div>
</div>
<div class="main-spacer"></div>
""", unsafe_allow_html=True)

# ── BOAS-VINDAS COM PAINEL DO DÓLAR ────────────────
if not st.session_state.messages:

    cotacao_dolar = buscar_cotacao_dolar()
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    if cotacao_dolar:
        cor_variacao = "#22d3a5" if cotacao_dolar["variacao"] >= 0 else "#ef233c"
        sinal = "▲" if cotacao_dolar["variacao"] >= 0 else "▼"
        painel_dolar = (
            '<div class="dolar-panel">'
            '<div class="dolar-header">'
            '<span>💵 Dólar Comercial</span>'
            f'<span class="dolar-date">{data_hoje}</span>'
            '</div>'
            f'<div class="dolar-value">R$ {cotacao_dolar["venda"]:.2f}</div>'
            '<div class="dolar-details">'
            f'<span>Compra: R$ {cotacao_dolar["compra"]:.2f}</span>'
            f'<span style="color:{cor_variacao}">{sinal} {abs(cotacao_dolar["variacao"]):.2f}%</span>'
            '</div>'
            '</div>'
        )
    else:
        painel_dolar = (
            '<div class="dolar-panel">'
            '<div class="dolar-header">'
            '<span>💵 Dólar Comercial</span>'
            f'<span class="dolar-date">{data_hoje}</span>'
            '</div>'
            '<div class="dolar-value" style="color:#4a4a6a;font-size:16px">Indisponível no momento</div>'
            '</div>'
        )

    welcome_html = (
        '<div class="welcome-card">'
        '<h3>👋 Olá! Como posso ajudar?</h3>'
        '<p>Sou um agente de suporte com IA e acesso à internet em tempo real.<br>'
        'Faça qualquer pergunta — suporte técnico, informações atuais ou curiosidades.</p>'
        + painel_dolar +
        '<div class="suggestions-row">'
        '<span class="suggestion-chip">⚽ Resultados do futebol</span>'
        '<span class="suggestion-chip">🤖 O que é IA?</span>'
        '<span class="suggestion-chip">📱 Como te contratar?</span>'
        '</div>'
        '</div>'
    )

    st.markdown(welcome_html, unsafe_allow_html=True)

# ── HISTÓRICO ──────────────────────────────────────
for msg in st.session_state.messages:
    avatar_icon = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.write(msg["content"])
        if "fontes" in msg and msg["fontes"]:
            fontes_html = '<div class="fontes-box"><div class="fontes-label">🔗 Fontes consultadas</div>'
            for f in msg["fontes"]:
                fontes_html += f'<a href="{f["url"]}" target="_blank" class="fonte-link">{f["titulo"][:60]}</a>'
            fontes_html += '</div>'
            st.markdown(fontes_html, unsafe_allow_html=True)
        if "time" in msg:
            st.markdown(
                f'<div class="msg-time">{msg["time"]}</div>',
                unsafe_allow_html=True
            )

# ── INPUT ──────────────────────────────────────────
if prompt := st.chat_input("Digite sua mensagem..."):
    now = datetime.now().strftime("%H:%M")

    # Adiciona mensagem do usuário
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": now
    })

    with st.chat_message("user", avatar="🧑"):
        st.write(prompt)
        st.markdown(
            f'<div class="msg-time">{now}</div>',
            unsafe_allow_html=True
        )

    # Detecta automaticamente o domínio do atendimento
    dominio_detectado = detectar_dominio(prompt)
    st.session_state.dominio_atual = dominio_detectado
    info_dominio = DOMINIOS[dominio_detectado]

    st.markdown(
        f'<div class="search-indicator" style="color:{info_dominio["cor"]};background:{info_dominio["cor"]}14;border-color:{info_dominio["cor"]}33">'
        f'{info_dominio["icone"]} Modo detectado: {dominio_detectado}</div>',
        unsafe_allow_html=True
    )

    # Detecta moeda ou busca web genérica
    contexto_web = ""
    fontes_consultadas = []
    moeda_detectada = detectar_moeda(prompt)

    if moeda_detectada:
        st.markdown(
            f'<div class="search-indicator">💰 Buscando cotação de {moeda_detectada}...</div>',
            unsafe_allow_html=True
        )
        cotacao = buscar_cotacao(moeda_detectada)
        if cotacao:
            contexto_web = f"""
Cotação atual de {cotacao['moeda']} em Reais (BRL):
- Compra: R$ {float(cotacao['compra']):.2f}
- Venda: R$ {float(cotacao['venda']):.2f}
- Variação: {cotacao['variacao']}%
- Atualizado em: {cotacao['hora']}

Use esses dados exatos na resposta.
"""
            fontes_consultadas = [{"titulo": "AwesomeAPI — Cotações em tempo real", "url": "https://docs.awesomeapi.com.br/api-de-moedas"}]
            st.session_state.web_searches += 1
    elif precisa_busca_web(prompt):
        st.markdown(
            '<div class="search-indicator">🌐 Buscando informações atuais na web...</div>',
            unsafe_allow_html=True
        )
        resultado, fontes = buscar_web(prompt)
        if resultado:
            contexto_web = f"\n\nInformações atuais da web:\n{resultado}\n\nUse essas informações na resposta."
            fontes_consultadas = fontes
            st.session_state.web_searches += 1

    # Monta histórico para LangChain
    lc_messages = [SystemMessage(content=info_dominio["prompt"] + contexto_web)]
    for m in st.session_state.messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))

    # Streaming da resposta
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""
        for chunk in get_model().stream(lc_messages):
            full_response += chunk.content
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

        # Exibe as fontes consultadas, se houver
        if fontes_consultadas:
            fontes_html = '<div class="fontes-box"><div class="fontes-label">🔗 Fontes consultadas</div>'
            for f in fontes_consultadas:
                fontes_html += f'<a href="{f["url"]}" target="_blank" class="fonte-link">{f["titulo"][:60]}</a>'
            fontes_html += '</div>'
            st.markdown(fontes_html, unsafe_allow_html=True)

        resp_time = datetime.now().strftime("%H:%M")
        st.markdown(
            f'<div class="msg-time">{resp_time}</div>',
            unsafe_allow_html=True
        )

    # Salva resposta no histórico (incluindo fontes, para persistir após rerun)
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "time": resp_time,
        "fontes": fontes_consultadas
    })

    st.rerun()