import streamlit as st

# 1. Configuração da Página Mestra (Tela Cheia)
st.set_page_config(page_title="JP Client Vault - Limpa Nome", layout="wide", initial_sidebar_state="expanded")

# 2. Estrutura do Menu Lateral (Sidebar)
with st.sidebar:
    st.title("🛡️ JP Client Vault")
    st.write("---")
    
    # Roteamento de Navegação
    menu_selecionado = st.radio(
        "Navegação do Sistema",
        ["🏠 Home", "📝 Enviar Limpa Nome", "📋 Minhas Listas", "💲 Financeiro", "📊 Orçamento"]
    )

# 3. Renderização das Telas Baseadas no Menu
if menu_selecionado == "🏠 Home":
    st.title("Bem-vindo ao Portal de Reabilitação de Crédito")
    st.write("Este é o seu ambiente seguro para envio e acompanhamento de processos.")

elif menu_selecionado == "📝 Enviar Limpa Nome":
    st.header("Cadastrar Nomes (Ação Limpa Nome)")
    st.info("O formulário de injeção de CPFs/CNPJs será acoplado aqui.")

elif menu_selecionado == "📋 Minhas Listas":
    st.header("Histórico de Listas e Status")
    st.info("A tabela de acompanhamento de status em tempo real será acoplada aqui.")

elif menu_selecionado == "💲 Financeiro":
    st.header("Painel Financeiro")
    st.info("Os quadros de valores pagos, pendentes e upload de comprovantes PIX serão acoplados aqui.")

elif menu_selecionado == "📊 Orçamento":
    st.header("Calculadora de Orçamento")
    st.info("O gerador de orçamentos e exportador de PDF será acoplado aqui.")
