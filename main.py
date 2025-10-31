import streamlit as st
from deep_translator import GoogleTranslator
import json
import os
from io import StringIO

# --- CONFIGURAÇÕES GERAIS ---
st.set_page_config(page_title="Tradutor de Legendas", page_icon="🌍", layout="centered")
st.title("🌍 Tradutor de Legendas e Arquivos JSON")

# Cacheia instâncias do tradutor para evitar chamadas repetidas e lentas
@st.cache_resource
def get_translator(target_lang):
    return GoogleTranslator(source='auto', target=target_lang)

# --- FUNÇÕES AUXILIARES ---
def traduzir_legenda_srt(conteudo: str, lingua_destino: str) -> str:
    """Traduz legendas no formato .srt linha a linha, preservando timestamps."""
    tradutor = get_translator(lingua_destino)
    linhas = conteudo.splitlines()
    resultado = []

    for linha in linhas:
        if not linha.strip() or linha.strip().isdigit() or '-->' in linha:
            resultado.append(linha)
        else:
            try:
                traducao = tradutor.translate(linha.strip())
                resultado.append(traducao)
            except Exception:
                resultado.append(linha)  # Em caso de falha, mantém o texto original

    return "\n".join(resultado)


def traduzir_json(conteudo: str, lingua_destino: str) -> str:
    """Traduz recursivamente todos os valores de um arquivo JSON."""
    tradutor = get_translator(lingua_destino)
    dados = json.loads(conteudo)

    def traduzir_valores(obj):
        if isinstance(obj, dict):
            return {k: traduzir_valores(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [traduzir_valores(v) for v in obj]
        elif isinstance(obj, str):
            try:
                return tradutor.translate(obj)
            except Exception:
                return obj
        else:
            return obj

    traduzido = traduzir_valores(dados)
    return json.dumps(traduzido, ensure_ascii=False, indent=4)


# --- INTERFACE PRINCIPAL ---
uploaded_file = st.file_uploader("📂 Envie um arquivo de legenda ou JSON", type=["srt", "json"])

if uploaded_file:
    lingua_destino = st.selectbox(
        "🌐 Escolha o idioma de destino",
        options={
            "pt": "Português",
            "en": "Inglês",
            "es": "Espanhol",
            "fr": "Francês",
            "de": "Alemão",
            "it": "Italiano",
        }.items(),
        format_func=lambda x: x[1],
    )[0]

    if st.button("🚀 Traduzir"):
        with st.spinner("Traduzindo... Isso pode levar alguns segundos ⏳"):
            conteudo = uploaded_file.read().decode("utf-8", errors="ignore")
            extensao = os.path.splitext(uploaded_file.name)[1].lower()
            nome_base = os.path.splitext(uploaded_file.name)[0]

            try:
                if extensao == ".srt":
                    traduzido = traduzir_legenda_srt(conteudo, lingua_destino)
                    mime = "text/plain"
                else:
                    traduzido = traduzir_json(conteudo, lingua_destino)
                    mime = "application/json"

                nome_saida = f"{nome_base}_traduzido{extensao}"

                st.success("✅ Tradução concluída com sucesso!")
                st.download_button(
                    label="⬇️ Baixar arquivo traduzido",
                    data=traduzido,
                    file_name=nome_saida,
                    mime=mime,
                )

            except Exception as e:
                st.error(f"Ocorreu um erro durante a tradução: {e}")
else:
    st.info("👆 Envie um arquivo .srt ou .json para começar.")
