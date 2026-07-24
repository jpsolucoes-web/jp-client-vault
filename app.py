import streamlit as st
from supabase import create_client, Client

# 1. Configuração da Página Mestra (Tela Cheia)
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
        </style>
    """, unsafe_allow_html=True)

injetar_css_profissional()

# 2. Inicialização do Motor de Banco de Dados
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

# 4. Módulo de Autenticação Dual (Login e Cadastro)
def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.title("🛡️ JP Client Vault")
            
        st.markdown("<h3 style='text-align: center;'>Portal do Cliente</h3>", unsafe_allow_html=True)
        
        # Criando as abas para separar Login e Cadastro
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
                        # Tenta criar o usuário no banco
                        supabase.auth.sign_up({"email": novo_email, "password": nova_senha})
                        st.success("✅ Conta criada com sucesso! Você já pode fazer login na aba 'Já tenho conta'.")
                    except Exception as e:
                        st.error(f"Erro ao criar conta: {e}")

# 5. Renderização da Interface Interna
def tela_principal():
    # IDENTIFICAÇÃO DO NÍVEL DE ACESSO (DIRETOR VS CLIENTE)
    email_logado = st.session_state['dados_usuario'].email
    is_diretor = (email_logado == "jp.solucoes.sc.diretor@gmail.com")

    with st.sidebar:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.title("🛡️ JP Client Vault")
            
        if is_diretor:
            st.error("👑 MODO DIRETOR ATIVADO")
        else:
            st.success(f"👤 Cliente: {email_logado}")
        
        if st.button("Desconectar (Sair)", use_container_width=True):
            st.session_state['usuario_autenticado'] = False
            st.session_state['dados_usuario'] = None
            st.rerun()
            
        st.write("---")
        
        # Construção Dinâmica do Menu
        opcoes_menu = ["🏠 Home", "📝 Enviar Limpa Nome", "📋 Minhas Listas", "💲 Financeiro"]
        
        # Se for o Diretor, adiciona o painel secreto
        if is_diretor:
            opcoes_menu.append("⚙️ Painel do Diretor")
            
        menu_selecionado = st.radio("Navegação do Sistema", opcoes_menu)

    # Lógica de Telas
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

    elif menu_selecionado == "📝 Enviar Limpa Nome":
        st.header("Cadastrar Nomes (Ação Limpa Nome)")
        try: st.image("nomelimpo.png", use_container_width=True)
        except: pass
        
        st.write("Preencha os dados abaixo de forma cuidadosa. Após o envio, os dados entrarão em análise.")
        
        # O FORMULÁRIO QUE INJETA DADOS NA TABELA
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
        st.header("Histórico de Listas e Status")
        st.info("Fase 6: Sua tabela de acompanhamento será gerada aqui.")

    elif menu_selecionado == "💲 Financeiro":
        st.header("Painel Financeiro")
        st.info("Fase 6: Links de pagamento e QR Code Pix aparecerão aqui.")

    elif menu_selecionado == "⚙️ Painel do Diretor":
        st.header("👑 Central de Comando (Admin)")
        st.write("Visão global de todos os processos cadastrados pelos clientes.")
        
        try:
            # O Diretor puxa TUDO do banco de dados
            resposta = supabase.table("processos").select("*").execute()
            dados_processos = resposta.data
            
            if dados_processos:
                st.dataframe(dados_processos, use_container_width=True)
            else:
                st.write("Nenhum processo cadastrado no sistema ainda.")
        except Exception as e:
            st.error("Erro ao puxar base de dados.")

# 6. Controlador de Fluxo
if not st.session_state['usuario_autenticado']:
    tela_login()
else:
    tela_principal()
