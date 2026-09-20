
import streamlit as st
from google import genai
from supabase import create_client
import os
import json
import time
import requests
from datetime import datetime

st.set_page_config(
    page_title="Assistente Operacional",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: #f6f9ff;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f4f8ff 100%);
        border-right: 1px solid #e5ecf7;
    }
    [data-testid="stSidebar"] h1 {
        color: #0b1739;
        font-size: 1.75rem;
        letter-spacing: -0.04em;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: #60708f;
    }
    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    h1, h2, h3 {
        color: #0b1739;
        letter-spacing: -0.025em;
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e4ebf6;
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 6px 22px rgba(27, 63, 122, 0.06);
    }
    div[data-testid="stMetric"] label {
        color: #637392 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #155eef;
    }
    div[data-testid="stExpander"] {
        background: white;
        border: 1px solid #e4ebf6;
        border-radius: 16px;
        box-shadow: 0 5px 18px rgba(27, 63, 122, 0.05);
        overflow: hidden;
    }
    .stButton > button {
        border-radius: 12px;
        min-height: 42px;
        font-weight: 650;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #1769ff 0%, #3157f5 100%);
        border: 0;
    }
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        border-radius: 12px !important;
    }
    .dops-hero {
        display:flex;
        justify-content:space-between;
        gap:24px;
        align-items:center;
        margin: 4px 0 22px 0;
    }
    .dops-hero h1 {
        font-size: 2.6rem;
        margin:0;
    }
    .dops-hero p {
        color:#657493;
        font-size:1.08rem;
        margin:.35rem 0 0 0;
    }
    .dops-banner {
        background: linear-gradient(90deg,#e8f0ff,#eadcff);
        border-radius:16px;
        padding:18px 24px;
        color:#18328f;
        font-weight:700;
        min-width:340px;
    }
    .dops-flow {
        display:grid;
        grid-template-columns: repeat(5, 1fr);
        gap:12px;
        margin: 20px 0 28px 0;
    }
    .dops-step {
        background:#fff;
        border:1px solid #e4ebf6;
        border-radius:16px;
        padding:16px;
        min-height:155px;
        box-shadow:0 5px 18px rgba(27,63,122,.05);
    }
    .dops-step .num {
        display:inline-flex;
        width:30px;height:30px;
        align-items:center;justify-content:center;
        border-radius:50%;
        background:#edf3ff;
        color:#155eef;
        font-weight:800;
        margin-bottom:10px;
    }
    .dops-step b {
        display:block;
        color:#0b1739;
        margin-bottom:7px;
    }
    .dops-step span {
        color:#657493;
        font-size:.92rem;
        line-height:1.35;
    }
    .dops-beta {
        background:#eaf4ff;
        border:1px solid #d6e9ff;
        color:#245a9b;
        border-radius:14px;
        padding:13px 16px;
        margin-top:24px;
    }
    @media (max-width: 900px) {
        .dops-hero {display:block;}
        .dops-banner {margin-top:14px;min-width:0;}
        .dops-flow {grid-template-columns:1fr;}
    }

    /* V6 - acabamento visual */
    [data-testid="stSidebar"] {
        min-width: 245px;
    }
    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 7px;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background: transparent;
        border-radius: 12px;
        padding: 9px 10px;
        transition: all .18s ease;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: #eef4ff;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg,#1769ff,#3157f5);
        color: white !important;
        box-shadow: 0 6px 16px rgba(31,91,255,.20);
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
        color: white !important;
        font-weight: 700;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
        display: none;
    }
    .stMainBlockContainer {
        max-width: 1380px;
    }
    div[data-testid="stMetric"] {
        min-height: 122px;
        display: flex;
        justify-content: center;
        border-radius: 20px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 800;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px;
    }
    .stAlert {
        border-radius: 14px;
    }
    hr {
        border-color: #e7edf7 !important;
    }


    /* V7 - acabamento final */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 10px 12px !important;
        margin-bottom: 3px;
        border: 1px solid transparent;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(90deg,#1769ff,#3157f5) !important;
        border-color: transparent !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] > label:not(:has(input:checked)):hover {
        border-color:#dce7f7;
        background:#f3f7ff !important;
    }
    .dops-empty {
        background:#fff;
        border:1px dashed #cfdaeb;
        border-radius:18px;
        padding:30px 24px;
        text-align:center;
        color:#64748b;
        margin: 8px 0 20px 0;
    }
    .dops-empty b {
        display:block;
        color:#17233f;
        font-size:1.05rem;
        margin-bottom:5px;
    }
    .dops-request {
        background:#fff;
        border:1px solid #e1e9f5;
        border-radius:18px;
        padding:16px 18px 7px 18px;
        margin-bottom:10px;
        box-shadow:0 5px 16px rgba(27,63,122,.045);
    }

</style>
""", unsafe_allow_html=True)

# ==================================================
# CONFIGURAÇÕES
# ==================================================

gemini_key = os.environ.get("GEMINI_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

if not gemini_key:
    st.error("Configuração da IA não encontrada.")
    st.stop()

if not supabase_url or not supabase_key:
    st.error("Configuração do banco de dados não encontrada.")
    st.stop()

client = genai.Client(api_key=gemini_key)

supabase = create_client(
    supabase_url,
    supabase_key
)
# ==================================================
# LOGIN
# ==================================================

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = False

if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = ""

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None

# Restaura a sessão autenticada do Supabase após cada rerun.
if (
    st.session_state.usuario_logado
    and st.session_state.access_token
    and st.session_state.refresh_token
):
    try:
        supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )
    except Exception:
        st.session_state.usuario_logado = False
        st.session_state.usuario_email = ""
        st.session_state.access_token = None
        st.session_state.refresh_token = None

if not st.session_state.usuario_logado:
    st.title("🔐 Acesso ao Assistente")
    st.write("Entre com seu e-mail e senha para continuar.")

    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if not email or not senha:
            st.warning("Informe o e-mail e a senha.")
        else:
            try:
                resposta_login = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": senha
                })

                if resposta_login.user and resposta_login.session:
                    st.session_state.usuario_logado = True
                    st.session_state.usuario_email = email
                    st.session_state.access_token = resposta_login.session.access_token
                    st.session_state.refresh_token = resposta_login.session.refresh_token
                    st.rerun()
                else:
                    st.error("Não foi possível iniciar a sessão.")
            except Exception:
                st.error("E-mail ou senha incorretos.")

    st.stop()

# ==================================================
# SUPABASE
# ==================================================

def contar_status(status=None):

    try:
        query = (
            supabase
            .table("atendimentos")
            .select("id")
        )

        if status:
            query = query.eq("status", status)

        resposta = query.execute()

        return len(resposta.data)

    except Exception:
        return 0


def salvar_atendimento(
    cliente,
    categoria,
    servico,
    localizacao,
    mensagem_original,
    resumo,
    materiais,
    valor_materiais,
    valor_mao_obra,
    valor_total,
    prazo,
    observacoes
):

    dados = {
        "data": datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        ),
        "cliente": cliente,
        "categoria": categoria,
        "servico": servico,
        "localizacao": localizacao,
        "mensagem_original": mensagem_original,
        "resumo": resumo,
        "materiais": materiais,
        "valor_materiais": float(valor_materiais),
        "valor_mao_obra": float(valor_mao_obra),
        "valor_total": float(valor_total),
        "prazo": prazo,
        "observacoes": observacoes,
        "status": "Em revisão"
    }

    resposta = (
        supabase
        .table("atendimentos")
        .insert(dados)
        .execute()
    )

    return resposta


def buscar_atendimentos():
    resposta = (
        supabase.table("atendimentos")
        .select(
            "id,data,cliente,categoria,servico,localizacao,"
            "mensagem_original,resumo,materiais,valor_materiais,"
            "valor_mao_obra,valor_total,prazo,observacoes,status,telegram_chat_id,visualizado"
        )
        .order("id", desc=True).execute()
    )
    return resposta.data


def marcar_visualizado(id_atendimento, visualizado=True):
    return (
        supabase.table("atendimentos")
        .update({"visualizado": bool(visualizado)})
        .eq("id", id_atendimento)
        .execute()
    )


def buscar_novas_solicitacoes():
    resposta = (
        supabase.table("atendimentos")
        .select("id,data,cliente,servico,localizacao,status,telegram_chat_id,visualizado")
        .eq("visualizado", False)
        .order("id", desc=True)
        .execute()
    )
    return resposta.data


def atualizar_status(
    id_atendimento,
    novo_status
):

    resposta = (
        supabase
        .table("atendimentos")
        .update({
            "status": novo_status
        })
        .eq(
            "id",
            id_atendimento
        )
        .execute()
    )

    return resposta


def atualizar_orcamento(id_atendimento, materiais, valor_materiais, valor_mao_obra, valor_total, prazo, observacoes):
    return (
        supabase.table("atendimentos")
        .update({
            "materiais": materiais,
            "valor_materiais": float(valor_materiais),
            "valor_mao_obra": float(valor_mao_obra),
            "valor_total": float(valor_total),
            "prazo": prazo,
            "observacoes": observacoes
        })
        .eq("id", id_atendimento).execute()
    )


def enviar_mensagem_telegram(chat_id, mensagem):
    if not telegram_bot_token:
        raise Exception("TELEGRAM_BOT_TOKEN não encontrado nas configurações do Streamlit.")
    if not chat_id:
        raise Exception("Este atendimento não possui conversa do Telegram vinculada.")

    resposta = requests.post(
        f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
        json={"chat_id": str(chat_id), "text": mensagem},
        timeout=15
    )
    if not resposta.ok:
        try:
            detalhe = resposta.json().get("description", resposta.text)
        except Exception:
            detalhe = resposta.text
        raise Exception(f"Telegram recusou o envio: {detalhe}")
    return resposta.json()


# ==================================================
# GEMINI COM RETRY
# ==================================================

def analisar_com_ia(prompt):

    ultimo_erro = None

    for tentativa in range(3):

        try:

            response = (
                client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )
            )

            return response

        except Exception as erro:

            ultimo_erro = erro
            erro_texto = str(erro)

            if (
                "503" in erro_texto
                or "UNAVAILABLE" in erro_texto
                or "high demand" in erro_texto.lower()
            ):

                if tentativa < 2:
                    time.sleep(3)
                    continue

                raise Exception(
                    "A IA está temporariamente ocupada. "
                    "Aguarde alguns segundos e tente novamente."
                )

            raise erro

    raise ultimo_erro


# ==================================================
# SESSION STATE
# ==================================================

if "analise" not in st.session_state:
    st.session_state.analise = None

if "mensagem_original" not in st.session_state:
    st.session_state.mensagem_original = ""


# ==================================================
# MENU
# ==================================================

st.sidebar.title("🔵 DOPS")
st.sidebar.caption("Assistente Operacional")

opcoes_menu = [
    "🏠 Dashboard",
    "📥 Atendimentos",
    "📚 Histórico"
]

if "pagina_menu" not in st.session_state:
    st.session_state.pagina_menu = "🏠 Dashboard"

pagina = st.sidebar.radio(
    "Menu",
    opcoes_menu,
    key="pagina_menu"
)

st.sidebar.caption("DOPS v6.0 • Beta")
st.sidebar.markdown("---")
st.sidebar.caption("EM DESENVOLVIMENTO")
st.sidebar.caption("👥 Clientes  •  📄 Modelos")
st.sidebar.caption("📅 Agenda  •  📊 Relatórios")
st.sidebar.caption("⚙️ Configurações")

st.sidebar.divider()
st.sidebar.caption(f"Conectado: {st.session_state.get('usuario_email', '')}")

if st.sidebar.button("🚪 Sair"):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.usuario_logado = False
    st.session_state.usuario_email = ""
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.analise = None
    st.session_state.mensagem_original = ""
    st.rerun()


# ==================================================
# DASHBOARD
# ==================================================

if pagina == "🏠 Dashboard":

    total = contar_status()
    em_revisao = contar_status("Em revisão")
    aguardando = contar_status("Aguardando retorno")
    aprovados = contar_status("Aprovado")

    try:
        novas = buscar_novas_solicitacoes()
    except Exception:
        novas = []

    st.markdown("""
    <div class="dops-hero">
        <div>
            <h1>Visão geral da operação</h1>
            <p>Solicitações, orçamentos e retornos em um só lugar.</p>
        </div>
        <div class="dops-banner">
            Menos tempo com burocracia.<br>
            Mais tempo para o que realmente importa.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Novas solicitações", len(novas))
    with col2:
        st.metric("Em revisão", em_revisao)
    with col3:
        st.metric("Aguardando retorno", aguardando)
    with col4:
        st.metric("Aprovados", aprovados)

    st.subheader("📥 Novas solicitações")

    if not novas:
        st.markdown("""
        <div class="dops-empty">
            <b>✓ Tudo em dia por aqui</b>
            Nenhuma nova solicitação aguardando sua visualização.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption(
            "Recebidas pelo Telegram e ainda não visualizadas."
        )

        for item in novas:
            with st.container(border=True):
                c1, c2, c3 = st.columns([2.2, 2.2, 1])
                with c1:
                    st.markdown(
                        f"### {item.get('cliente') or 'Cliente'}\n"
                        f"{item.get('servico') or 'Serviço não informado'}"
                    )
                with c2:
                    st.markdown(
                        f"📍 **{item.get('localizacao') or 'Localização não informada'}**  \\n"
                        f"🕒 {item.get('data') or ''}"
                    )
                with c3:
                    if st.button(
                        "Abrir solicitação →",
                        key=f"abrir_nova_{item['id']}",
                        type="primary",
                        use_container_width=True
                    ):
                        marcar_visualizado(item["id"], True)
                        st.session_state.atendimento_selecionado = item["id"]
                        st.session_state.pagina_menu = "📥 Atendimentos"
                        st.rerun()

    st.markdown("""
    <div class="dops-beta">
        💡 <b>Foco no que importa:</b> as solicitações chegam automaticamente pelo Telegram.
        Revise as informações, prepare o orçamento e envie ao cliente.
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# NOVA SOLICITAÇÃO
# ==================================================

elif pagina == "📱 Nova solicitação manual":

    st.title("📱 Nova solicitação manual")

    st.write(
        "Cole abaixo a mensagem recebida "
        "do cliente."
    )

    mensagem = st.text_area(
        "Mensagem do cliente",
        height=150,
        placeholder=(
            "Ex.: Boa tarde, preciso trocar "
            "meu quadro elétrico..."
        )
    )

    if st.button(
        "✨ Analisar solicitação",
        type="primary"
    ):

        if not mensagem.strip():

            st.warning(
                "Cole uma mensagem antes de analisar."
            )

        else:

            with st.spinner(
                "A IA está organizando a solicitação..."
            ):

                prompt = f"""
Você é um assistente operacional para um
eletricista profissional.

Sua função é organizar solicitações de clientes
e reduzir o trabalho administrativo do profissional.

REGRAS IMPORTANTES:

- Use somente informações fornecidas pelo cliente.
- Não invente informações.
- Não invente preços.
- Não faça diagnóstico técnico definitivo.
- Não determine que equipamentos precisam ser
  substituídos sem avaliação profissional.
- Diferencie o pedido do cliente da conclusão técnica.
- A decisão técnica sempre pertence ao eletricista.
- Se uma informação não estiver presente, não presuma.
- Organize a solicitação de forma objetiva.

Mensagem do cliente:

{mensagem}

Retorne APENAS JSON válido:

{{
    "categoria": "categoria geral",

    "servico":
        "serviço solicitado ou serviço a avaliar",

    "problema":
        "resumo fiel do que o cliente relatou, sem diagnóstico",

    "urgencia":
        "urgência informada ou Não informada",

    "localizacao":
        "localização informada ou Não informada",

    "informacoes_disponiveis": [
        "informação identificada 1",
        "informação identificada 2"
    ],

    "informacoes_faltantes": [
        "informação necessária 1",
        "informação necessária 2"
    ],

    "proxima_acao":
        "próxima ação administrativa sugerida",

    "resposta_cliente":
        "mensagem curta, profissional e natural para solicitar somente as informações faltantes"
}}
"""

                try:

                    response = analisar_com_ia(
                        prompt
                    )

                    texto = response.text.strip()

                    texto = texto.replace(
                        "```json",
                        ""
                    )

                    texto = texto.replace(
                        "```",
                        ""
                    )

                    texto = texto.strip()

                    dados = json.loads(
                        texto
                    )

                    st.session_state.analise = (
                        dados
                    )

                    st.session_state.mensagem_original = (
                        mensagem
                    )

                except json.JSONDecodeError:

                    st.error(
                        "A IA respondeu, mas não foi "
                        "possível organizar a resposta. "
                        "Tente novamente."
                    )

                except Exception as e:

                    if (
                        "temporariamente ocupada"
                        in str(e)
                    ):

                        st.warning(
                            str(e)
                        )

                    else:

                        st.error(
                            "Não foi possível analisar "
                            "a solicitação. Tente novamente "
                            "em alguns instantes."
                        )


    # ==================================================
    # RESULTADO DA IA
    # ==================================================

    if st.session_state.analise:

        dados = st.session_state.analise

        st.success(
            "Solicitação analisada com sucesso!"
        )

        st.subheader(
            "🧠 Análise da IA"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                "**Categoria:**",
                dados.get(
                    "categoria",
                    "Não informado"
                )
            )

            st.write(
                "**Serviço solicitado / a avaliar:**",
                dados.get(
                    "servico",
                    "Não informado"
                )
            )

            st.write(
                "**Urgência:**",
                dados.get(
                    "urgencia",
                    "Não informada"
                )
            )

        with col2:

            st.write(
                "**Localização:**",
                dados.get(
                    "localizacao",
                    "Não informada"
                )
            )

            st.write(
                "**Relato do cliente:**",
                dados.get(
                    "problema",
                    "Não informado"
                )
            )

        st.subheader(
            "✅ Informações identificadas"
        )

        informacoes = dados.get(
            "informacoes_disponiveis",
            []
        )

        if informacoes:

            for item in informacoes:
                st.write(
                    "✓",
                    item
                )

        else:

            st.write(
                "Nenhuma informação adicional "
                "identificada."
            )

        st.subheader(
            "❓ Informações faltantes"
        )

        faltantes = dados.get(
            "informacoes_faltantes",
            []
        )

        if faltantes:

            for item in faltantes:
                st.write(
                    "•",
                    item
                )

        else:

            st.success(
                "As principais informações iniciais "
                "já foram fornecidas."
            )

        st.subheader(
            "➡️ Próxima ação sugerida"
        )

        st.info(
            dados.get(
                "proxima_acao",
                "Aguardar avaliação do profissional."
            )
        )

        st.subheader(
            "💬 Resposta sugerida ao cliente"
        )

        st.text_area(
            "Mensagem para revisar e copiar:",
            value=dados.get(
                "resposta_cliente",
                ""
            ),
            height=120
        )

        st.caption(
            "A IA prepara a resposta. "
            "O profissional revisa antes do envio."
        )

        st.divider()

        # ==================================================
        # ORÇAMENTO
        # ==================================================

        st.subheader(
            "📋 Preparar orçamento"
        )

        st.write(
            "A IA organizou a solicitação. "
            "Os valores e decisões técnicas são "
            "definidos pelo profissional."
        )

        cliente_nome = st.text_input(
            "Nome do cliente"
        )

        col1, col2 = st.columns(2)

        with col1:

            materiais = st.text_area(
                "Materiais previstos",
                height=100
            )

            valor_materiais = (
                st.number_input(
                    "Valor dos materiais (R$)",
                    min_value=0.0,
                    step=10.0,
                    format="%.2f"
                )
            )

        with col2:

            prazo = st.text_input(
                "Prazo estimado"
            )

            valor_mao_obra = (
                st.number_input(
                    "Valor da mão de obra (R$)",
                    min_value=0.0,
                    step=10.0,
                    format="%.2f"
                )
            )

        observacoes = st.text_area(
            "Observações do profissional",
            value=(
                "Orçamento sujeito à avaliação "
                "técnica no local."
            )
        )

        valor_total = (
            valor_materiais
            + valor_mao_obra
        )

        st.metric(
            "Valor total do orçamento",
            f"R$ {valor_total:,.2f}"
        )

        st.caption(
            "Os preços são definidos pelo "
            "profissional. A IA não determina valores."
        )

        # ==================================================
        # PROPOSTA
        # ==================================================

        if cliente_nome.strip():

            proposta = f"""
ORÇAMENTO DE SERVIÇO

Cliente:
{cliente_nome}

Serviço solicitado / a avaliar:
{dados.get("servico", "")}

Localização:
{dados.get("localizacao", "")}

Materiais previstos:
{materiais if materiais else "A definir após avaliação."}

Valor dos materiais:
R$ {valor_materiais:,.2f}

Valor da mão de obra:
R$ {valor_mao_obra:,.2f}

VALOR TOTAL:
R$ {valor_total:,.2f}

Prazo estimado:
{prazo if prazo else "A definir."}

Observação técnica:
{observacoes}
"""

            st.subheader(
                "📄 Orçamento pronto para revisão"
            )

            st.text_area(
                "Revise antes de enviar ao cliente:",
                value=proposta,
                height=350
            )

            st.warning(
                "A decisão técnica e a aprovação "
                "final pertencem ao profissional."
            )

            if st.button(
                "💾 Salvar atendimento",
                type="primary"
            ):

                try:

                    salvar_atendimento(
                        cliente_nome,
                        dados.get(
                            "categoria",
                            ""
                        ),
                        dados.get(
                            "servico",
                            ""
                        ),
                        dados.get(
                            "localizacao",
                            ""
                        ),
                        st.session_state.mensagem_original,
                        dados.get(
                            "problema",
                            ""
                        ),
                        materiais,
                        valor_materiais,
                        valor_mao_obra,
                        valor_total,
                        prazo,
                        observacoes
                    )

                    st.success(
                        "Atendimento salvo no "
                        "banco permanente! ✅"
                    )

                    st.session_state.analise = None
                    st.session_state.mensagem_original = ""

                except Exception as e:
                    st.error("Não foi possível salvar o atendimento.")
                    st.code(str(e))


# ==================================================
# HISTÓRICO
# ==================================================

elif pagina == "📥 Atendimentos":

    st.title("📥 Atendimentos")
    st.caption("Abra uma solicitação, revise os dados e prepare o orçamento.")

    try:
        atendimentos = buscar_atendimentos()

        if not atendimentos:
            st.info("Nenhum atendimento registrado ainda.")
        else:
            for atendimento in atendimentos:
                id_atendimento = atendimento["id"]
                data = atendimento.get("data", "")
                cliente_nome = atendimento.get("cliente", "") or "Cliente"
                categoria = atendimento.get("categoria", "") or ""
                servico = atendimento.get("servico", "") or ""
                localizacao = atendimento.get("localizacao", "") or ""
                mensagem_original = atendimento.get("mensagem_original", "") or ""
                resumo = atendimento.get("resumo", "") or ""
                observacoes_banco = atendimento.get("observacoes", "") or ""
                telegram_chat_id = atendimento.get("telegram_chat_id")
                status = atendimento.get("status", "Em revisão") or "Em revisão"
                valor_total_atual = float(atendimento.get("valor_total", 0) or 0)

                atendimento_selecionado = st.session_state.get("atendimento_selecionado")
                abrir_automaticamente = (atendimento_selecionado == id_atendimento)

                with st.expander(
                    f"#{id_atendimento} — {cliente_nome} — {servico}",
                    expanded=abrir_automaticamente
                ):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**Data:**", data)
                        st.write("**Categoria:**", categoria or "Não informada")
                        st.write("**Serviço:**", servico or "Não informado")
                    with c2:
                        st.write("**Localização:**", localizacao or "Não informada")
                        st.write("**Status:**", status)
                        st.write("**Valor atual:**", f"R$ {valor_total_atual:,.2f}")

                    if resumo:
                        st.write("**Resumo da solicitação:**")
                        st.info(resumo)
                    if mensagem_original:
                        st.write("**Mensagem recebida:**")
                        st.write(mensagem_original)

                    if telegram_chat_id and observacoes_banco:
                        with st.expander("💬 Histórico interno da conversa no Telegram"):
                            st.text(observacoes_banco)

                    if telegram_chat_id:
                        st.success("📨 Atendimento conectado ao Telegram.")
                    else:
                        st.info("Atendimento antigo/manual: sem conversa do Telegram vinculada.")

                    st.divider()
                    st.subheader("📋 Preparar orçamento")

                    materiais = st.text_area(
                        "Materiais previstos",
                        value=atendimento.get("materiais", "") or "",
                        height=100,
                        key=f"materiais_{id_atendimento}"
                    )

                    c1, c2 = st.columns(2)
                    with c1:
                        valor_materiais = st.number_input(
                            "Valor dos materiais (R$)",
                            min_value=0.0,
                            value=float(atendimento.get("valor_materiais", 0) or 0),
                            step=10.0,
                            format="%.2f",
                            key=f"valor_materiais_{id_atendimento}"
                        )
                        prazo = st.text_input(
                            "Prazo estimado",
                            value=atendimento.get("prazo", "") or "",
                            key=f"prazo_{id_atendimento}"
                        )
                    with c2:
                        valor_mao_obra = st.number_input(
                            "Valor da mão de obra (R$)",
                            min_value=0.0,
                            value=float(atendimento.get("valor_mao_obra", 0) or 0),
                            step=10.0,
                            format="%.2f",
                            key=f"valor_mao_obra_{id_atendimento}"
                        )
                        valor_total = valor_materiais + valor_mao_obra
                        st.metric("Valor total", f"R$ {valor_total:,.2f}")

                    observacao_padrao = "Orçamento sujeito à avaliação técnica no local."
                    observacoes = st.text_area(
                        "Observações do orçamento",
                        value=observacao_padrao if telegram_chat_id else (observacoes_banco or observacao_padrao),
                        key=f"observacoes_orcamento_{id_atendimento}",
                        help="Somente este texto poderá aparecer no orçamento enviado ao cliente."
                    )

                    proposta = f"""ORÇAMENTO DE SERVIÇO

Olá, {cliente_nome}!

Serviço:
{servico or "A definir"}

Localização:
{localizacao or "Não informada"}

Materiais previstos:
{materiais if materiais.strip() else "A definir após avaliação."}

Valor dos materiais:
R$ {valor_materiais:,.2f}

Valor da mão de obra:
R$ {valor_mao_obra:,.2f}

VALOR TOTAL:
R$ {valor_total:,.2f}

Prazo estimado:
{prazo if prazo.strip() else "A definir."}

Observação:
{observacoes if observacoes.strip() else "Sem observações adicionais."}

Se quiser confirmar o serviço ou tirar alguma dúvida, pode responder por aqui."""

                    st.subheader("📄 Mensagem que será enviada")

                    chave_msg = f"mensagem_orcamento_{id_atendimento}"
                    chave_base = f"base_orcamento_{id_atendimento}"

                    if (
                        chave_msg not in st.session_state
                        or st.session_state.get(chave_base) != proposta
                    ):
                        st.session_state[chave_msg] = proposta
                        st.session_state[chave_base] = proposta

                    mensagem_final = st.text_area(
                        "Revise e edite antes do envio:",
                        key=chave_msg,
                        height=330
                    )

                    st.caption(
                        "O orçamento é gerado com os dados acima, mas o profissional "
                        "pode ajustar a mensagem antes de aprovar o envio."
                    )

                    cs, ce = st.columns(2)
                    with cs:
                        if st.button("💾 Salvar orçamento", key=f"salvar_{id_atendimento}", use_container_width=True):
                            try:
                                atualizar_orcamento(
                                    id_atendimento, materiais, valor_materiais,
                                    valor_mao_obra, valor_total, prazo, observacoes
                                )
                                st.success("Orçamento salvo com sucesso!")
                            except Exception as e:
                                st.error("Não foi possível salvar o orçamento.")
                                st.code(str(e))

                    with ce:
                        if telegram_chat_id:
                            if st.button(
                                "📤 Aprovar e enviar ao cliente",
                                type="primary",
                                key=f"enviar_{id_atendimento}",
                                use_container_width=True
                            ):
                                try:
                                    atualizar_orcamento(
                                        id_atendimento, materiais, valor_materiais,
                                        valor_mao_obra, valor_total, prazo, observacoes
                                    )
                                    enviar_mensagem_telegram(telegram_chat_id, mensagem_final)
                                    atualizar_status(id_atendimento, "Aguardando retorno")
                                    st.success("Orçamento enviado ao cliente pelo Telegram! ✅")
                                    st.rerun()
                                except Exception as e:
                                    st.error("O orçamento não foi enviado. O status não foi alterado.")
                                    st.code(str(e))
                        else:
                            st.button(
                                "📤 Enviar pelo Telegram",
                                disabled=True,
                                key=f"sem_telegram_{id_atendimento}",
                                use_container_width=True
                            )

                    st.divider()
                    opcoes_status = ["Em revisão", "Enviado", "Aguardando retorno", "Aprovado", "Recusado"]
                    indice = opcoes_status.index(status) if status in opcoes_status else 0
                    novo_status = st.selectbox(
                        "Alterar status manualmente",
                        opcoes_status,
                        index=indice,
                        key=f"status_{id_atendimento}"
                    )
                    if novo_status != status:
                        atualizar_status(id_atendimento, novo_status)
                        st.success("Status atualizado!")
                        st.rerun()

    except Exception as e:
        st.error("Não foi possível carregar o histórico.")
        st.code(str(e))


# ==================================================
# HISTÓRICO RESUMIDO
# ==================================================

elif pagina == "📚 Histórico":

    st.title("📚 Histórico")
    st.caption("Visão rápida de todos os atendimentos registrados.")

    try:
        atendimentos = buscar_atendimentos()

        if not atendimentos:
            st.info("Nenhum atendimento registrado ainda.")
        else:
            for atendimento in atendimentos:
                c1, c2, c3, c4 = st.columns([0.7, 2.2, 2.2, 1.3])
                with c1:
                    st.write(f"**#{atendimento['id']}**")
                with c2:
                    st.write(atendimento.get("cliente") or "Cliente")
                    st.caption(atendimento.get("servico") or "Serviço não informado")
                with c3:
                    st.write(atendimento.get("localizacao") or "Localização não informada")
                    st.caption(atendimento.get("data") or "")
                with c4:
                    st.write(atendimento.get("status") or "Em revisão")
                st.divider()

    except Exception as e:
        st.error("Não foi possível carregar o histórico.")
        st.code(str(e))
