import streamlit as st
from deep_translator import GoogleTranslator
import json
import tempfile
import os

def traduzir_legenda_srt(conteudo, lingua_destino='pt'):
    tradutor = GoogleTranslator(target=lingua_destino)
    linhas = conteudo.splitlines()
    linhas_traduzidas = []

    for linha in linhas:
        if not linha.strip().isdigit() and '-->' not in linha:
            traducao = tradutor.translate(linha.strip())
            linhas_traduzidas.append(traducao)
        else:
            linhas_traduzidas.append(linha)

    return '\n'.join(linhas_traduzidas)

def traduzir_json(conteudo, lingua_destino='pt'):
    tradutor = GoogleTranslator(target=lingua_destino)
    dados = json.loads(conteudo)

    def traduzir_valores(dados):
        if isinstance(dados, dict):
            return {k: traduzir_valores(v) for k, v in dados.items()}
        elif isinstance(dados, list):
            return [traduzir_valores(item) for item in dados]
        elif isinstance(dados, str):
            return tradutor.translate(dados)
        else:
            return dados

    dados_traduzidos = traduzir_valores(dados)
    return json.dumps(dados_traduzidos, ensure_ascii=False, indent=4)

st.title("Tradutor de Legendas")

if 'tradução_em_andamento' not in st.session_state:
    st.session_state.tradução_em_andamento = False

uploaded_file = st.file_uploader("Anexe o arquivo de legenda (.srt ou .json)", type=["srt", "json"], disabled=st.session_state.tradução_em_andamento)

if uploaded_file is not None:
    lingua_destino = st.selectbox("Selecione a língua de destino", ["pt", "en", "es", "fr", "de"], disabled=st.session_state.tradução_em_andamento)
    
    if st.button("Traduzir", disabled=st.session_state.tradução_em_andamento):
        st.session_state.tradução_em_andamento = True
        with st.spinner('Lendo o arquivo...'):
            conteudo = uploaded_file.read().decode("utf-8")

        original_filename = os.path.splitext(uploaded_file.name)[0]
        file_extension = os.path.splitext(uploaded_file.name)[1][1:]

        if file_extension == 'srt':
            with st.spinner('Traduzindo legenda...'):
                conteudo_traduzido = traduzir_legenda_srt(conteudo, lingua_destino)
        else:
            with st.spinner('Traduzindo arquivo JSON...'):
                conteudo_traduzido = traduzir_json(conteudo, lingua_destino)
        
        st.session_state.arquivo_traduzido = (conteudo_traduzido, f"{original_filename}_traduzido.{file_extension}")
        st.session_state.tradução_em_andamento = False

if 'arquivo_traduzido' in st.session_state and st.session_state.arquivo_traduzido is not None:
    conteudo_traduzido, arquivo_traduzido_nome = st.session_state.arquivo_traduzido

    st.success('Tradução concluída!')

    st.download_button(
        label="Baixar arquivo traduzido",
        data=conteudo_traduzido,
        file_name=arquivo_traduzido_nome,
        mime="text/plain" if arquivo_traduzido_nome.endswith("srt") else "application/json"
    )
    
    if st.button("Traduzir outro arquivo"):
        st.session_state.arquivo_traduzido = None
        st.experimental_rerun()
