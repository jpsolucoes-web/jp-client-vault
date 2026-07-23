import streamlit as st
from supabase import create_client, Client

# 1. Configuração da Página Mestra (Tela Cheia)
st.set_page_config(page_title="JP Client Vault - Limpa Nome", layout="wide", initial_sidebar_state="expanded")

# 2. Inicialização do Motor de Banco de Dados (Supabase)
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# 3. Gerenciamento de Estado (Memória RAM da Sessão)
if 'usuario_autenticado' not in st.session_state:
    st.session_state['usuario_autenticado'] = False
if 'dados_usuario' not in st.session_state:
    st.session_state['dados_usuario'] = None

# 4. Módulo de Autenticação (A Porta de Aço)
def tela_login():
    # Centralizando o formulário matematicamente na tela
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🛡️ JP Client Vault")
        st.write("Área de Acesso Restrito. Insira suas credenciais.")
        
        with st.form("login_form"):
            email = st.text_input("E-mail Cadastrado")
            senha = st.text_input("Senha de Acesso", type="password")
            submit = st.form_submit_button("Autenticar Conexão", use_container_width=True)
            
            if submit:
                try:
                    # Executa a equação de verificação no servidor Supabase
                    resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                    st.session_state['usuario_autenticado'] = True
                    st.session_state['dados_usuario'] = resposta.user
                    st.success("Autenticação validada! Redirecionando...")
                    st.rerun()
                except Exception as e:
                    st.error("Falha na autenticação. E-mail ou senha inválidos.")

# 5. Renderização da Interface Interna (Apenas para Autenticados)
def tela_principal():
    with st.sidebar:
        st.title("🛡️ JP Client Vault")
        st.success(f"Logado: {st.session_state['dados_usuario'].email}")
        
        # Botão de Logout (Zera a variável booleana)
        if st.button("Desconectar (Sair)", use_container_width=True):
            st.session_state['usuario_autenticado'] = False
            st.session_state['dados_usuario'] = None
            st.rerun()
            
        st.write("---")
        
        # Roteamento de Navegação
        menu_selecionado = st.radio(
            "Navegação do Sistema",
            ["🏠 Home", "📝 Enviar Limpa Nome", "📋 Minhas Listas", "💲 Financeiro", "📊 Orçamento"]
        )

    # Lógica de Telas
    if menu_selecionado == "🏠 Home":
        st.title("Bem-vindo ao Portal de Reabilitação de Crédito")
        st.write("Este é o seu ambiente seguro para envio e acompanhamento de processos.")

    elif menu_selecionado == "📝 Enviar Limpa Nome":
        st.header("Cadastrar Nomes (Ação Limpa Nome)")
        st.info("Fase 5: O formulário de injeção de CPFs/CNPJs será acoplado aqui.")

    elif menu_selecionado == "📋 Minhas Listas":
        st.header("Histórico de Listas e Status")
        st.info("Fase 5: A tabela de acompanhamento de status em tempo real será acoplada aqui.")

    elif menu_selecionado == "💲 Financeiro":
        st.header("Painel Financeiro")
        st.info("Fase 5: Os quadros de valores pagos, pendentes e upload PIX serão acoplados aqui.")

    elif menu_selecionado == "📊 Orçamento":
        st.header("Calculadora de Orçamento")
        st.info("Fase 5: O gerador de orçamentos e exportador de PDF será acoplado aqui.")

# 6. Controlador de Fluxo Lógico
if not st.session_state['usuario_autenticado']:
    tela_login()
else:
    tela_principal()
