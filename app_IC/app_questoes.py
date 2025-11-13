import streamlit as st
import os
import random
from pathlib import Path

# --- CONFIGURAÇÕES GERAIS ---
st.set_page_config(page_title="Teste de Identificação", layout="wide")

st.title("🦷 Teste de Identificação de Imagens Médicas")
st.write("Em cada questão, escolha qual imagem você acredita ser **real**.")

# --- PASTAS ---
PASTAS = {
    "Reais com filtro": "reais_com_filtro",
    "Reais sem filtro": "reais_sem_filtro",
    "Geradas com filtro": "fake_com_filtro",
    "Geradas sem filtro": "fake_sem_filtro",
}

# --- CARREGAR IMAGENS COMO LISTAS ---
listas = {}
for nome, caminho in PASTAS.items():
    if not os.path.exists(caminho):
        st.error(f"Pasta não encontrada: {caminho}")
        st.stop()
    imagens = sorted(Path(caminho).glob("*"))
    listas[nome] = imagens

# --- GARANTIR QUE TODAS TENHAM MESMO TAMANHO ---
num_questoes = min(len(lst) for lst in listas.values())
st.info(f"Número total de questões: {num_questoes}")

# --- ARMAZENAR RESPOSTAS ---
if "respostas" not in st.session_state:
    st.session_state.respostas = {}

# --- EXIBIR QUESTÕES ---
for i in range(num_questoes):
    st.subheader(f"Questão {i+1}")
    imagens_q = [listas[pasta][i] for pasta in listas]

    # embaralhar as imagens para não ficarem sempre na mesma posição
    random.shuffle(imagens_q)

    cols = st.columns(4)
    escolha = None
    for idx, col in enumerate(cols):
        with col:
            st.image(imagens_q[idx], width="container")
            if st.button(f"Escolher imagem {idx+1}", key=f"q{i}_{idx}"):
                st.session_state.respostas[i] = str(imagens_q[idx])

# --- EXIBIR RESULTADOS ---
if len(st.session_state.respostas) == num_questoes:
    st.success("✅ Todas as questões foram respondidas!")
    st.subheader("Suas respostas:")
    for i, resp in st.session_state.respostas.items():
        st.write(f"Questão {i+1}: {resp}")
