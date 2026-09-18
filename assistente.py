
import streamlit as st
from google import genai
from supabase import create_client
import os
import json
import time
from datetime import datetime

st.set_page_config(
    page_title="Assistente Operacional",
    page_icon="⚡",
    layout="wide"
)

# ==================================================
# CONFIGURAÇÕES
# ==================================================

gemini_key = os.environ.get("GEMINI_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

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
        supabase
        .table("atendimentos")
        .select(
            "id,data,cliente,servico,"
            "localizacao,valor_total,status"
        )
        .order(
            "id",
            desc=True
        )
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

st.sidebar.title("⚡ Assistente")

pagina = st.sidebar.radio(
    "Menu",
    [
        "🏠 Dashboard",
        "📱 Nova solicitação",
        "📚 Histórico"
    ]
)

st.sidebar.caption("Beta 0.6 • Supabase")


# ==================================================
# DASHBOARD
# ==================================================

if pagina == "🏠 Dashboard":

    st.title("⚡ Assistente Operacional")

    st.caption(
        "Atendimento e orçamento assistidos por IA"
    )

    st.divider()

    total = contar_status()

    em_revisao = contar_status(
        "Em revisão"
    )

    aguardando = contar_status(
        "Aguardando retorno"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Solicitações registradas",
            total
        )

    with col2:
        st.metric(
            "Orçamentos em revisão",
            em_revisao
        )

    with col3:
        st.metric(
            "Aguardando retorno",
            aguardando
        )

    st.divider()

    st.subheader("👋 Olá, Patrick")

    st.write(
        "Aqui você acompanha as solicitações "
        "recebidas e os orçamentos preparados."
    )

    st.info(
        "Use o menu lateral para registrar "
        "uma nova solicitação."
    )


# ==================================================
# NOVA SOLICITAÇÃO
# ==================================================

elif pagina == "📱 Nova solicitação":

    st.title("📱 Nova solicitação")

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

                except Exception:

                    st.error(
                        "Não foi possível salvar o "
                        "atendimento. Tente novamente."
                    )


# ==================================================
# HISTÓRICO
# ==================================================

elif pagina == "📚 Histórico":

    st.title(
        "📚 Histórico de atendimentos"
    )

    try:

        atendimentos = (
            buscar_atendimentos()
        )

        if not atendimentos:

            st.info(
                "Nenhum atendimento registrado ainda."
            )

        else:

            for atendimento in atendimentos:

                id_atendimento = atendimento["id"]

                data = atendimento.get(
                    "data",
                    ""
                )

                cliente_nome = atendimento.get(
                    "cliente",
                    ""
                )

                servico = atendimento.get(
                    "servico",
                    ""
                )

                localizacao = atendimento.get(
                    "localizacao",
                    ""
                )

                valor_total = float(
                    atendimento.get(
                        "valor_total",
                        0
                    ) or 0
                )

                status = atendimento.get(
                    "status",
                    "Em revisão"
                )

                with st.expander(
                    f"#{id_atendimento} — "
                    f"{cliente_nome} — {servico}"
                ):

                    st.write(
                        "**Data:**",
                        data
                    )

                    st.write(
                        "**Localização:**",
                        localizacao
                    )

                    st.write(
                        "**Valor:**",
                        f"R$ {valor_total:,.2f}"
                    )

                    opcoes_status = [
                        "Em revisão",
                        "Enviado",
                        "Aguardando retorno",
                        "Aprovado",
                        "Recusado"
                    ]

                    indice = (
                        opcoes_status.index(status)
                        if status in opcoes_status
                        else 0
                    )

                    novo_status = st.selectbox(
                        "Status",
                        opcoes_status,
                        index=indice,
                        key=(
                            f"status_"
                            f"{id_atendimento}"
                        )
                    )

                    if novo_status != status:

                        atualizar_status(
                            id_atendimento,
                            novo_status
                        )

                        st.success(
                            "Status atualizado!"
                        )

                        st.rerun()

    except Exception:

        st.error(
            "Não foi possível carregar o histórico."
        )
