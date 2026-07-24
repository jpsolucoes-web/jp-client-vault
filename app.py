import streamlit as st
import pandas as pd
from supabase import create_client, Client

# 1. Configuração da Página Mestra
st.set_page_config(page_title="JP Client Vault - Limpa Nome", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# MATRIZ DE ESTILO PROFISSIONAL (CSS)
# ==========================================
def injetar_css_profissional():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #f4f6f9; }
        img { border-radius: 10px; }
        video { border-radius: 10px; }
        /* Ajuste fino para o menu lateral parecer mais profissional */
        [data-testid="stSidebarNav"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

injetar_css_profissional()

# 2. Inicialização do Banco de Dados
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# 3. Gerenciamento de Estado
if 'usuario_autenticado' not in st.session_state:
    st.session_state['usuario_autenticado'] = False
if 'dados_usuario' not in st.session_state:
    st.session_state['dados_usuario'] = None

# 4. Módulo de Autenticação Dual
def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("logo.png", use_container_width=True)
        except: st.title("🛡️ JP Client Vault")
            
        st.markdown("<h3 style='text-align: center;'>Portal do Cliente</h3>", unsafe_allow_html=True)
        
        aba_login, aba_cadastro = st.tabs(["🔐 Já tenho conta", "📝 Criar nova conta"])
        
        with aba_login:
            with st.form("login_form"):
                email = st.text_input("E-mail Cadastrado")
                senha = st.text_input("Senha de Acesso", type="password")
                submit = st.form_submit_button("Autenticar Conexão", use_container_width=True)
                if submit:
                    try:
                        resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                        st.session_state['usuario_autenticado'] = True
                        st.session_state['dados_usuario'] = resposta.user
                        st.rerun()
                    except Exception as e:
                        st.error("Falha na autenticação. E-mail ou senha inválidos.")
                        
        with aba_cadastro:
            with st.form("cadastro_form"):
                st.info("Cadastre-se para iniciar seu processo de reabilitação.")
                novo_email = st.text_input("Seu melhor E-mail")
                nova_senha = st.text_input("Crie uma Senha (mínimo 6 caracteres)", type="password")
                submit_cadastro = st.form_submit_button("Criar Minha Conta", use_container_width=True)
                if submit_cadastro:
                    try:
                        supabase.auth.sign_up({"email": novo_email, "password": nova_senha})
                        st.success("✅ Conta criada com sucesso! Você já pode fazer login na aba 'Já tenho conta'.")
                    except Exception as e:
                        st.error(f"Erro ao criar conta: {e}")

# 5. Renderização da Interface Interna
def tela_principal():
    email_logado = st.session_state['dados_usuario'].email
    is_diretor = (email_logado == "jp.solucoes.sc.diretor@gmail.com")

    with st.sidebar:
        try: st.image("logo.png", use_container_width=True)
        except: st.title("🛡️ JP Client Vault")
            
        if is_diretor:
            st.error("👑 MODO DIRETOR ATIVADO")
        else:
            st.success(f"👤 Cliente: {email_logado}")
        
        if st.button("Desconectar (Sair)", use_container_width=True):
            st.session_state['usuario_autenticado'] = False
            st.session_state['dados_usuario'] = None
            st.rerun()
            
        st.write("---")
        
        # MENU LATERAL COMPLETO (Baseado na Imagem 3)
        opcoes_menu = [
            "🏠 Home", 
            "💼 Serviços", 
            "📅 Eventos",
            "🛡️ Enviar Limpa Nome", 
            "🔄 Reprotocolo", 
            "📖 Manual do Parceiro", 
            "📋 Minhas Listas",
            "💲 Financeiro", 
            "⚠️ Reclame Aqui", 
            "📊 Orçamento", 
            "📝 Contrato Limpa Nome",
            "📄 Documentos de Apoio", 
            "🎓 Academia Limpa Nome",
            "🏢 CNPJ Inapto",
            "🩺 Solicitar Diagnóstico", 
            "📑 Meus Diagnósticos"
        ]
        
        if is_diretor:
            opcoes_menu.append("⚙️ Painel do Diretor")
            
        menu_selecionado = st.radio("Navegação do Sistema", opcoes_menu)

    # -----------------------------------------
    # LÓGICA DE ROTEAMENTO DE PÁGINAS
    # -----------------------------------------
    
    if menu_selecionado == "🏠 Home":
        st.markdown("<h1 style='text-align: center; color: #002244;'>Portal de Reabilitação de Crédito</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #555; font-size: 18px;'>Ambiente blindado para envio e análise dos seus processos.</p>", unsafe_allow_html=True)
        st.write("---")
        
        col_img, col_vid = st.columns([1, 1])
        with col_img:
            try: st.image("valortecpflimpo.png", use_container_width=True)
            except: pass
        with col_vid:
            try: st.video("video1.mp4")
            except: pass
                
        st.write("---")
        try: st.image("RECONSTRUIR.png", use_container_width=True)
        except: pass

    elif menu_selecionado == "🛡️ Enviar Limpa Nome":
        st.header("Cadastrar Nomes (Ação Limpa Nome)")
        try: st.image("nomelimpo.png", use_container_width=True)
        except: pass
        
        with st.form("form_novo_processo"):
            nome_cliente = st.text_input("Nome Completo / Razão Social")
            cpf_cnpj = st.text_input("CPF ou CNPJ (Apenas números)")
            tipo_doc = st.selectbox("Tipo de Documento", ["CPF", "CNPJ"])
            observacao = st.text_area("Observações ou detalhes da dívida (Opcional)")
            
            enviar = st.form_submit_button("🚀 Enviar para Análise", use_container_width=True)
            
            if enviar:
                if nome_cliente != "" and cpf_cnpj != "":
                    try:
                        dados = {
                            "user_id": st.session_state['dados_usuario'].id,
                            "email_cliente": email_logado,
                            "nome": nome_cliente,
                            "cpf_cnpj": cpf_cnpj,
                            "tipo": tipo_doc,
                            "observacao": observacao
                        }
                        supabase.table("processos").insert(dados).execute()
                        st.success("✅ Processo enviado e registrado com sucesso no Cofre!")
                    except Exception as e:
                        st.error(f"Erro no sistema: {e}")
                else:
                    st.warning("⚠️ Atenção: Nome e CPF/CNPJ são obrigatórios.")

    elif menu_selecionado == "📋 Minhas Listas":
        st.header("Minhas Listas")
        st.write("Histórico completo de todos os nomes cadastrados")
        
        try:
            # Puxa APENAS os dados do cliente que está logado no momento
            resposta = supabase.table("processos").select("cpf_cnpj, tipo, status_pagamento, status_serasa, status_boa_vista, status_spc, status_cenprot_br, status_cenprot_sp, data_registro").eq("email_cliente", email_logado).execute()
            
            if resposta.data:
                # Transforma os dados em uma Tabela Profissional idêntica à solicitada
                df = pd.DataFrame(resposta.data)
                
                # Renomeando as colunas matemáticas para leitura humana
                df.columns = ["CPF/CNPJ", "Tipo", "Status", "Serasa", "Boa Vista", "SPC", "Cenprot BR", "Cenprot SP", "Data"]
                
                # Renderiza a tabela na tela ocupando o espaço total
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum processo foi encontrado no seu histórico. Use a aba 'Enviar Limpa Nome' para iniciar.")
        except Exception as e:
            st.error(f"Falha ao sincronizar com o banco de dados: {e}")

    elif menu_selecionado == "⚙️ Painel do Diretor":
        st.header("👑 Central de Comando (Admin)")
        st.write("Visão global de todos os processos cadastrados pelos clientes.")
        try:
            # O Diretor puxa TUDO do banco de dados (sem filtro de email)
            resposta = supabase.table("processos").select("*").execute()
            if resposta.data:
                st.dataframe(resposta.data, use_container_width=True)
            else:
                st.write("Nenhum processo cadastrado no sistema ainda.")
        except Exception as e:
            st.error("Erro ao puxar base de dados.")
            
    else:
        # Gerenciador Automático para as outras opções do menu que ainda não têm tela
        st.header(menu_selecionado[2:])
        st.info("Esta seção está em fase de implantação.")

# 6. Controlador de Fluxo
if not st.session_state['usuario_autenticado']:
    tela_login()
else:
    tela_principal()
