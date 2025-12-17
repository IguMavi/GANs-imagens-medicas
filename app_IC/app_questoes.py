import streamlit as st
import os
import random
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# CONFIGURAÇÕES DO GOOGLE SHEETS
# -----------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

client = gspread.authorize(credentials)

SHEET_ID = "1w-wGrOZSTltGHEIxijO8zpwbKI2l0H3dqzpwUYJAcfI"
sheet = client.open_by_key(SHEET_ID).sheet1


# -----------------------------
# CONFIGURAÇÕES DAS PASTAS
# -----------------------------
PASTAS = {
    "Reais com filtro": "app_IC/reais_com_filtro",
    "Reais sem filtro": "app_IC/reais_sem_filtro",
    "Geradas com filtro": "app_IC/fake_com_filtro",
    "Geradas sem filtro": "app_IC/fake_sem_filtro",
}


# -----------------------------
# FUNÇÃO PARA CARREGAR IMAGENS
# -----------------------------
def carregar_imagens():
    listas = {
        nome: sorted(Path(c).glob("*"))
        for nome, c in PASTAS.items()
        if os.path.exists(c)
    }
    num_questoes = min(len(lst) for lst in listas.values())
    return listas, num_questoes


# -----------------------------
# ESTADOS INICIAIS
# -----------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"

if "indice_q" not in st.session_state:
    st.session_state.indice_q = 0

if "respostas" not in st.session_state:
    st.session_state.respostas = {}

if "dados_participante" not in st.session_state:
    st.session_state.dados_participante = {}


# -----------------------------
# TELA INICIAL (FORMULÁRIO)
# -----------------------------
if st.session_state.fase == "inicio":
    st.title("🦷 Teste de Identificação de Imagens Médicas")

    st.subheader("📝 Informações do Participante")
    nome = st.text_input("Nome")
    idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
    profissao = st.text_input("Profissão")
    tempo = st.text_input("Tempo de atuação (anos)")

    st.markdown("---")
    st.write("""
    Este teste avalia a capacidade de identificar imagens **reais sem filtro**.

    - Cada questão contém **4 imagens**
    - Apenas **1** é real sem filtro
    - Escolha a que você acha ser a real
    """)

    st.markdown("---")
    st.subheader("📄 Termo de Consentimento")

    termos = st.checkbox(
        "Declaro estar ciente e de acordo com o uso das informações fornecidas neste formulário "
        "para fins exclusivamente acadêmicos e científicos, vinculados ao projeto de Iniciação "
        "Científica do INATEL intitulado “Geração de Imagens Médicas Artificiais com Redes Generativas "
        "Adversariais para Expansão de Datasets Diagnósticos de Visão Computacional” "
        "(orientação: Prof. José Andery Carneiro).\n\n"
        "Os dados coletados serão utilizados apenas para avaliar a qualidade e a fidelidade "
        "diagnóstica das imagens sintéticas geradas pela pesquisa, sem qualquer tentativa de "
        "identificação dos participantes. Não haverá divulgação individualizada de respostas, "
        "e todo o processamento será feito de forma agregada, em conformidade com a Lei Geral "
        "de Proteção de Dados (LGPD – Lei 13.709/2018).\n\n"
        "As informações fornecidas serão armazenadas somente durante a vigência da pesquisa "
        "e eliminadas após sua conclusão.\n\n"
        "Ao marcar esta opção, confirmo que li, compreendi e concordo com os termos acima."
    )

    iniciar = st.button(
        "🚀 Começar Teste",
        disabled=(nome == "" or not termos)
    )

    if iniciar:
        st.session_state.dados_participante = {
            "nome": nome,
            "idade": idade,
            "profissao": profissao,
            "tempo": tempo,
            "consentimento": True
        }
        st.session_state.fase = "teste"
        st.session_state.indice_q = 0
        st.session_state.respostas = {}
        st.rerun()


# -----------------------------
# FASE DO TESTE
# -----------------------------
elif st.session_state.fase == "teste":
    listas, num_questoes = carregar_imagens()
    i = st.session_state.indice_q

    st.title(f"🔍 Questão {i+1} de {num_questoes}")

    imagens_q = [listas[pasta][i] for pasta in listas]

    random.seed(i)
    random.shuffle(imagens_q)

    correta = listas["Reais sem filtro"][i]

    cols = st.columns(4)
    for idx, col in enumerate(cols):
        with col:
            st.image(imagens_q[idx], use_container_width=True)

    opcoes = [f"Imagem {j+1}" for j in range(4)]

    escolha = st.radio(
        "Selecione a imagem **real sem filtro**:",
        options=opcoes,
        index=None,
        key=f"radio_{i}"
    )

    if escolha:
        idx_escolha = int(escolha.split()[-1]) - 1
        st.session_state.respostas[i] = {
            "escolha": imagens_q[idx_escolha],
            "correta": correta
        }

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("⬅️ Anterior", disabled=i == 0):
            st.session_state.indice_q -= 1
            st.rerun()

    with col2:
        if st.button("➡️ Próxima", disabled=i == num_questoes - 1):
            st.session_state.indice_q += 1
            st.rerun()

    with col3:
        if st.button("📤 Enviar Respostas", disabled=len(st.session_state.respostas) < num_questoes):
            st.session_state.fase = "resultado"
            st.rerun()


# -----------------------------
# RESULTADO FINAL
# -----------------------------
elif st.session_state.fase == "resultado":
    st.title("📊 Resultado Final")

    respostas = st.session_state.respostas
    listas, num_questoes = carregar_imagens()

    acertos = 0

    for i, dados in respostas.items():
        escolha = dados["escolha"]
        correta = dados["correta"]
        acertou = escolha == correta

        if acertou:
            acertos += 1
            st.success(f"✅ Questão {i+1}: Correta!")
        else:
            st.error(f"❌ Questão {i+1}: Errada.")
            st.image([escolha, correta], caption=["Sua escolha", "Correta"], width=300)

    st.markdown(f"### 🏁 Pontuação final: **{acertos} / {num_questoes}**")
    st.divider()

    dados = st.session_state.dados_participante

    sheet.append_row([
        dados["nome"],
        dados["idade"],
        dados["profissao"],
        dados["tempo"],
        dados["consentimento"],
        acertos,
        num_questoes
    ])

    st.success("✔️ Resultado salvo com sucesso!")

    if st.button("🔁 Reiniciar Teste"):
        st.session_state.fase = "inicio"
        st.session_state.indice_q = 0
        st.session_state.respostas = {}
        st.rerun()
