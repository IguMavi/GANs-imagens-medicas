import streamlit as st
import os
import random
from pathlib import Path

st.set_page_config(page_title="Teste de Identificação", layout="wide")

# --- CONFIGURAÇÕES ---
PASTAS = {
    "Reais com filtro": "app_IC/reais_com_filtro",
    "Reais sem filtro": "app_IC/reais_sem_filtro",
    "Geradas com filtro": "app_IC/fake_com_filtro",
    "Geradas sem filtro": "app_IC/fake_sem_filtro",
}


# --- FUNÇÃO PARA CARREGAR IMAGENS ---
def carregar_imagens():
    listas = {nome: sorted(Path(c).glob("*")) for nome, c in PASTAS.items() if os.path.exists(c)}
    num_questoes = min(len(lst) for lst in listas.values())
    return listas, num_questoes

# --- ESTADOS INICIAIS ---
if "fase" not in st.session_state:
    st.session_state.fase = "inicio"
if "indice_q" not in st.session_state:
    st.session_state.indice_q = 0
if "respostas" not in st.session_state:
    st.session_state.respostas = {}
if "corrigir" not in st.session_state:
    st.session_state.corrigir = False

# --- TELA INICIAL ---
if st.session_state.fase == "inicio":
    st.title("🦷 Teste de Identificação de Imagens Médicas")
    st.write("""
    Este teste avalia a capacidade de identificar imagens **reais sem filtro** 
    dentre outras geradas ou filtradas.

    - Cada questão contém **4 imagens** (uma de cada tipo).
    - Você deve escolher qual delas é **real sem filtro**.
    - Após responder todas, o sistema mostrará seus acertos.
    """)
    if st.button("🚀 Começar Teste"):
        st.session_state.fase = "teste"
        st.session_state.indice_q = 0
        st.session_state.respostas = {}
        st.rerun()

# --- FASE DO TESTE ---
elif st.session_state.fase == "teste":
    listas, num_questoes = carregar_imagens()
    i = st.session_state.indice_q

    st.title(f"🔍 Questão {i+1} de {num_questoes}")

    # Pega uma imagem de cada pasta
    imagens_q = [listas[pasta][i] for pasta in listas]
    random.seed(i)  # mantém a ordem embaralhada consistente
    random.shuffle(imagens_q)

    # Define qual é a correta
    correta = listas["Reais sem filtro"][i]

    # Mostra as imagens
    cols = st.columns(4)
    for idx, col in enumerate(cols):
        with col:
            st.image(imagens_q[idx], width="container")

    # Opções de resposta
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

    # Botões de navegação
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

# --- RESULTADO FINAL ---
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
    if st.button("🔁 Reiniciar Teste"):
        st.session_state.fase = "inicio"
        st.session_state.indice_q = 0
        st.session_state.respostas = {}
        st.session_state.corrigir = False
        st.rerun()


