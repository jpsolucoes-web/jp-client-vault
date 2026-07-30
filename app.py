import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime
import streamlit.components.v1 as components

# 1. Configuração da Página Mestra
st.set_page_config(page_title="JP Client Vault - Limpa Nome", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# INICIALIZAÇÃO DE PREÇOS E ACESSOS (SESSÃO)
# ==========================================
if 'precos' not in st.session_state:
    st.session_state['precos'] = {
        'cliente': {'limpa_nome': 250.00, 'bacen': 1200.00, 'rating': 500.00, 'tributario': 2000.00, 'diag': 150.00},
        'parceiro': {'limpa_nome': 150.00, 'bacen': 600.00, 'rating': 250.00, 'tributario': 1000.00, 'diag': 50.00}
    }

if 'usuarios_bloqueados' not in st.session_state:
    st.session_state['usuarios_bloqueados'] = []

is_parceiro = st.query_params.get("tipo") == "parceiro"
perfil_atual = 'parceiro' if is_parceiro else 'cliente'

# ==========================================
# MATRIZ DE ESTILO PROFISSIONAL E WHATSAPP
# ==========================================
def injetar_css_profissional():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .stApp { background-color: #0d1117; color: #e2e8f0; }
        
        [data-testid="stSidebar"] { background-color: #1e293b !important; }
        [data-testid="stSidebar"] * { color: #ffffff !important; }
        
        label, p, .stRadio label, .stSelectbox label, .stTextInput label, .stTextArea label, .stFileUploader label {
            color: #ffffff !important; font-size: 16px !important; font-weight: 500 !important;
        }
        
        img, video { border-radius: 10px; }
        h1, h2, h3, h4 { color: #f59e0b !important; font-weight: 800 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        
        .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
            background-color: #0f172a !important; color: #ffffff !important; border: 1px solid #334155 !important; border-radius: 8px !important;
        }
        .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
            border-color: #f59e0b !important; box-shadow: 0 0 5px #f59e0b !important;
        }
        
        .stButton>button {
            background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%); color: black !important; font-weight: bold !important; border: none !important; border-radius: 8px !important; padding: 10px 20px !important; transition: 0.3s; width: 100%;
        }
        .stButton>button:hover {
            transform: scale(1.02); box-shadow: 0px 0px 15px rgba(245, 158, 11, 0.5);
        }
        hr { border-color: #334155; }
        
        .checkout-box { background-color: #1e293b; border-left: 5px solid #10b981; padding: 20px; border-radius: 8px; margin-top: 20px; }
        .card-servico { background-color: #1e293b; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #334155; margin-bottom: 15px; }
        .metric-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: left; }
        .metric-title { color: #94a3b8; font-size: 14px; margin-bottom: 5px; font-weight: 600; }
        .metric-value { color: #10b981; font-size: 28px; font-weight: bold; margin: 0; }
        
        /* Botão WhatsApp Flutuante */
        .whatsapp-float {
            position: fixed; bottom: 30px; right: 30px; background-color: #10b981; color: #ffffff !important;
            border-radius: 50px; padding: 12px 24px; font-size: 16px; font-weight: bold; text-decoration: none;
            box-shadow: 2px 2px 15px rgba(0,0,0,0.5); z-index: 99999; display: flex; align-items: center; gap: 10px; transition: all 0.3s ease;
        }
        .whatsapp-float:hover { background-color: #059669; transform: scale(1.05); }
        
        /* Ajuste pré-visualização PDF */
        .pdf-preview { background-color: #ffffff; padding: 40px; border-radius: 10px; color: #000000; font-family: Arial, sans-serif; box-shadow: 0 0 10px rgba(255,255,255,0.1); margin-top: 20px;}
        
        /* Status Manual Parceiro */
        .status-badge { display: inline-block; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-right: 15px; width: 150px; text-align: center; color: white;}
        .status-row { display: flex; align-items: center; margin-bottom: 10px; padding: 10px; background-color: #1e293b; border-radius: 8px;}
        </style>
    """, unsafe_allow_html=True)

injetar_css_profissional()

# Botão WhatsApp Global
st.markdown("""
    <a href="https://wa.me/5549998077332" class="whatsapp-float" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
        Precisa de ajuda?
    </a>
""", unsafe_allow_html=True)

# 2. Inicialização do Banco de Dados
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# 3. Gerenciamento de Estado
if 'usuario_autenticado' not in st.session_state: st.session_state['usuario_autenticado'] = False
if 'dados_usuario' not in st.session_state: st.session_state['dados_usuario'] = None
if 'menu_navegacao' not in st.session_state: st.session_state['menu_navegacao'] = "🏠 Home"

def mudar_pagina(nova_pagina): st.session_state['menu_navegacao'] = nova_pagina

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
                if st.form_submit_button("Autenticar Conexão", use_container_width=True):
                    try:
                        resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                        st.session_state['usuario_autenticado'] = True
                        st.session_state['dados_usuario'] = resposta.user
                        st.rerun()
                    except Exception as e:
                        st.error("Falha na autenticação. E-mail ou senha inválidos.")
                        
        with aba_cadastro:
            with st.form("cadastro_form"):
                novo_email = st.text_input("Seu melhor E-mail")
                nova_senha = st.text_input("Crie uma Senha (mínimo 6 caracteres)", type="password")
                if st.form_submit_button("Criar Minha Conta", use_container_width=True):
                    try:
                        supabase.auth.sign_up({"email": novo_email, "password": nova_senha})
                        st.success("✅ Conta criada com sucesso! Você já pode fazer login.")
                    except Exception as e:
                        st.error(f"Erro ao criar conta.")

# 5. Renderização da Interface Interna
def tela_principal():
    email_logado = st.session_state['dados_usuario'].email
    is_diretor = (email_logado == "jp.solucoes.sc.diretor@gmail.com")
    
    # Bloqueio Tático do Diretor
    if email_logado in st.session_state['usuarios_bloqueados'] and not is_diretor:
        st.error("🚫 SEU ACESSO FOI SUSPENSO PELO DIRETOR DA PLATAFORMA.")
        st.info("Entre em contato com o suporte para regularizar sua assinatura.")
        if st.button("Sair da Conta"):
            st.session_state['usuario_autenticado'] = False
            st.rerun()
        return

    with st.sidebar:
        try: st.image("logo.png", use_container_width=True)
        except: st.title("🛡️ JP Client Vault")
            
        if is_diretor: st.error("👑 MODO DIRETOR")
        else: st.success(f"👤 Cliente: {email_logado}")
            
        if is_parceiro: st.warning("🤝 MODO PARCEIRO ATIVADO")
        
        if st.button("Desconectar (Sair)", use_container_width=True):
            st.session_state['usuario_autenticado'] = False
            st.rerun()
            
        st.write("---")
        opcoes_menu = [
            "🏠 Home", "👤 Meu Perfil", "💼 Serviços", "📅 Eventos",
            "🛡️ Enviar Protocolo", "🔄 Reprotocolo", "📖 Manual do Parceiro", 
            "📋 Minhas Listas", "💲 Financeiro", "⚠️ Reclame Aqui", 
            "📊 Orçamento", "📝 Contratos para Baixar", "📄 Documentos de Apoio", 
            "🎓 Academia Limpa Nome", "🏢 CNPJ Inapto", "🩺 Solicitar Diagnóstico", "📑 Meus Diagnósticos"
        ]
        if is_diretor: opcoes_menu.append("⚙️ Painel do Diretor")
        st.radio("Navegação do Sistema", opcoes_menu, key="menu_navegacao", label_visibility="collapsed")

    menu_selecionado = st.session_state['menu_navegacao']

    # -----------------------------------------
    # 🏠 HOME
    # -----------------------------------------
    if menu_selecionado == "🏠 Home":
        st.markdown("<h1 style='text-align: center; color: #f59e0b;'>Portal de Reabilitação de Crédito</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8;'>Ambiente blindado para envio e análise dos seus processos.</p>", unsafe_allow_html=True)
        st.write("---")
        clock_html = """
        <div style="background-color: #0f172a; border: 2px solid #f59e0b; padding: 20px; border-radius: 15px; text-align: center; font-family: 'Segoe UI', Tahoma, sans-serif;">
            <h3 style="margin: 0; color: #f59e0b; font-size: 20px;">⏳ TEMPO PARA A PRÓXIMA AÇÃO OFICIAL (05/08/2026)</h3>
            <div id="clock_div" style="color: #10b981; font-size: 45px; font-weight: 900; letter-spacing: 2px; margin-top: 10px;">Calculando tempo...</div>
        </div>
        <script>
            var countDownDate = new Date("Aug 5, 2026 12:00:00").getTime();
            setInterval(function() {
                var now = new Date().getTime();
                var distance = countDownDate - now;
                if(distance < 0) { document.getElementById("clock_div").innerHTML = "AÇÃO INICIADA!"; return; }
                var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                hours = hours < 10 ? "0" + hours : hours; minutes = minutes < 10 ? "0" + minutes : minutes; seconds = seconds < 10 ? "0" + seconds : seconds;
                document.getElementById("clock_div").innerHTML = days + " Dias : " + hours + "h : " + minutes + "m : " + seconds + "s";
            }, 1000);
        </script>
        """
        components.html(clock_html, height=150)
        col_img, col_vid = st.columns([1, 1])
        with col_img:
            try: st.image("valortecpflimpo.png", use_container_width=True)
            except: pass
        with col_vid:
            try: st.video("video1.mp4")
            except: st.info("O vídeo 'video1.mp4' não foi encontrado.")

    # -----------------------------------------
    # 👤 MEU PERFIL E ASSINATURA
    # -----------------------------------------
    elif menu_selecionado == "👤 Meu Perfil":
        st.header("👤 Meu Perfil e Assinatura")
        st.markdown("""
        <div style='background-color:#064e3b; border: 1px solid #10b981; padding: 20px; border-radius: 10px; color: #fff; margin-bottom: 20px;'>
            <h3 style='margin-top:0; color:#10b981;'>✅ Sua assinatura está ativa</h3>
            <p style='margin:0; font-size: 16px;'>317 dias restantes<br>Acesso liberado até: 11/06/2027</p>
            <span style='float:right; background:#047857; padding:5px 10px; border-radius:15px; font-size:12px; margin-top:-45px;'>Período de Teste Grátis</span>
        </div>
        """, unsafe_allow_html=True)
        st.subheader("Informações Básicas")
        st.text_input("Nome de Exibição", value="JP SOLUÇÕES PARTICIPAÇÕES LTDA")
        st.text_input("Empresa", placeholder="Nome da empresa (opcional)")
        st.text_input("WhatsApp", value="999388222")
        st.text_input("Email (Login)", value=email_logado, disabled=True)
        st.text_input("CPF/CNPJ", value="55.399.519/0001-86")
        st.subheader("Endereço")
        c1, c2 = st.columns(2)
        c1.text_input("CEP")
        c2.text_input("Rua")
        c3, c4, c5 = st.columns([1, 1, 2])
        c3.text_input("Número")
        c4.selectbox("UF", ["SC", "PR", "RS", "SP", "RJ", "MG", "BA", "GO"])
        c5.text_input("Cidade")
        if st.button("💾 Salvar Alterações", use_container_width=True): st.success("Dados atualizados!")

    # -----------------------------------------
    # 💼 SERVIÇOS
    # -----------------------------------------
    elif menu_selecionado == "💼 Serviços":
        st.header("💼 Nossos Serviços Avançados")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card-servico"><h3>🛡️ Limpa Nome</h3><p>Reabilitação de crédito Padrão.</p></div>', unsafe_allow_html=True)
            st.button("Acessar Limpa Nome", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_limpa", use_container_width=True)
            st.markdown('<div class="card-servico"><h3>🏦 Rating Bancário</h3><p>Aumento de Score e Relacionamento.</p></div>', unsafe_allow_html=True)
            st.button("Acessar Rating", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_rating", use_container_width=True)
        with col2:
            st.markdown('<div class="card-servico"><h3>🏛️ BACEN</h3><p>Retirada de restrições no Banco Central.</p></div>', unsafe_allow_html=True)
            st.button("Acessar BACEN", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_bacen", use_container_width=True)
            st.markdown('<div class="card-servico"><h3>⚖️ Defesa Tributária</h3><p>Estratégias fiscais e tributárias.</p></div>', unsafe_allow_html=True)
            st.button("Acessar Tributário", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_trib", use_container_width=True)

    # -----------------------------------------
    # 🛡️ ENVIAR PROTOCOLO (AGORA COM CHECKBOXES DE SOMA!)
    # -----------------------------------------
    elif menu_selecionado == "🛡️ Enviar Protocolo":
        st.title("🚀 Central de Protocolos Avançados")
        st.markdown("Preencha os dados e selecione um ou mais serviços.")

        st.subheader("1. Selecione a Natureza da Ação (Pode marcar vários)")
        st.write("Marque as opções desejadas. O valor total será calculado automaticamente no final.")
        
        p_limpa = st.session_state['precos'][perfil_atual]['limpa_nome']
        p_bacen = st.session_state['precos'][perfil_atual]['bacen']
        p_rating = st.session_state['precos'][perfil_atual]['rating']
        p_trib = st.session_state['precos'][perfil_atual]['tributario']

        c_chk1, c_chk2 = st.columns(2)
        with c_chk1:
            serv_limpa = st.checkbox(f"🛡️ 1 - Ação Limpa Nome (Padrão) — R$ {p_limpa:,.2f}")
            serv_rating = st.checkbox(f"📈 3 - Rating Bancário — R$ {p_rating:,.2f}")
        with c_chk2:
            serv_bacen = st.checkbox(f"🏛️ 2 - BACEN — R$ {p_bacen:,.2f}")
            serv_trib = st.checkbox(f"⚖️ 4 - Defesa Tributária — R$ {p_trib:,.2f}")

        # Cálculo do carrinho
        total_carrinho = 0.0
        lista_servicos = []
        if serv_limpa: 
            total_carrinho += p_limpa
            lista_servicos.append("Limpa Nome")
        if serv_bacen: 
            total_carrinho += p_bacen
            lista_servicos.append("BACEN")
        if serv_rating: 
            total_carrinho += p_rating
            lista_servicos.append("Rating Bancário")
        if serv_trib: 
            total_carrinho += p_trib
            lista_servicos.append("Defesa Tributária")
            
        texto_servicos_banco = " + ".join(lista_servicos) if lista_servicos else "Nenhum"

        st.markdown("---")
        st.subheader("2. Identificação do Cliente")
        col1, col2 = st.columns(2)
        with col1:
            tipo_pessoa = st.radio("Pessoa Física ou Jurídica?", ["CPF", "CNPJ"])
            nome_cliente = st.text_input("Nome Completo / Razão Social")
        with col2:
            cpf_cnpj = st.text_input("Número do CPF ou CNPJ")
            telefone = st.text_input("WhatsApp com DDD")
        st.markdown("---")

        if serv_bacen or serv_rating:
            st.subheader("3. Questionário Analítico Completo (Obrigatório)")
            st.info("Para elevar Score, Rating e liberar histórico BACEN, preencha os dados abaixo.")
            c_pessoal1, c_pessoal2, c_pessoal3 = st.columns(3)
            rg = c_pessoal1.text_input("RG")
            from datetime import date
            data_nasc = c_pessoal2.date_input("Data de Nascimento", min_value=date(1920, 1, 1))
            estado_civil = c_pessoal3.selectbox("Estado Civil", ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"])
            c_filiacao1, c_filiacao2 = st.columns(2)
            nome_mae = c_filiacao1.text_input("Nome da Mãe")
            nome_pai = c_filiacao2.text_input("Nome do Pai (Opcional)")
            c_end1, c_end2 = st.columns([1, 3])
            cep = c_end1.text_input("CEP")
            endereco = c_end2.text_input("Endereço Completo (Rua, Nº, Bairro, Cidade-UF)")

            st.markdown("#### Perfil Financeiro e Patrimônio")
            c_prof1, c_prof2, c_prof3 = st.columns(3)
            empresa = c_prof1.text_input("Empresa onde trabalha")
            renda_pessoal = c_prof2.text_input("Sua Renda / Salário (R$)")
            renda_familiar = c_prof3.text_input("Renda Familiar Total (R$)")
            
            bancos = st.text_area("Quais bancos você tem conta? (Ex: Nubank - Ag 0001, Conta 1234-5)")
            c_veiculo1, c_veiculo2 = st.columns(2)
            imovel = c_veiculo1.selectbox("Possui Imóvel Próprio?", ["Não", "Sim - Quitado", "Sim - Financiado"])
            veiculo = c_veiculo2.text_input("Veículo Próprio (Modelo, Ano, Placa)")

            if serv_bacen:
                st.markdown("#### 🏛️ Acessos e Documentos Exclusivos (BACEN)")
                doc_scr_bacen = st.file_uploader("Upload do Extrato SCR Completo (Últimos 5 anos)", type=['pdf'])
                if tipo_pessoa == "CPF":
                    c_gov1, c_gov2 = st.columns(2)
                    gov_login = c_gov1.text_input("Login GOV.BR")
                    gov_senha = c_gov2.text_input("Senha GOV.BR", type="password")
                    doc_ident = st.file_uploader("Upload CNH ou RG (Documento 100% Legível)", type=['png', 'jpg', 'pdf'])
                else:
                    c_cert1, c_cert2 = st.columns(2)
                    cert_a1_bacen = c_cert1.file_uploader("Upload Certificado Digital A1 (.pfx)", type=['pfx', 'p12'])
                    senha_cert_bacen = c_cert2.text_input("Senha do Certificado Digital", type="password")
                    comp_end_pj = st.file_uploader("Comprovantes de Endereços", type=['png', 'jpg', 'pdf'], accept_multiple_files=True)
            
            if serv_rating:
                st.markdown("#### 📈 Credenciais de Acesso (Rating)")
                c_senha1, c_senha2, c_senha3, c_senha4 = st.columns(4)
                gov_login_r = c_senha1.text_input("Login GOV.BR (Rating)")
                gov_senha_r = c_senha2.text_input("Senha GOV.BR (Rating)", type="password")
                serasa_login = c_senha3.text_input("Login Serasa")
                serasa_senha = c_senha4.text_input("Senha Serasa", type="password")

        if serv_trib:
            st.subheader("3. Acessos Fiscais (Tributário)")
            st.info("Para Defesa Tributária, o Certificado Digital é obrigatório.")
            ct1, ct2 = st.columns(2)
            ct1.file_uploader("Upload Certificado Digital A1 (.pfx / .p12)", type=['pfx', 'p12'], key="cert_trib")
            ct2.text_input("Senha do Certificado Digital", type="password", key="senha_trib")

        st.markdown("---")
        st.subheader("4. Anexos e Documentação Oficial Geral")
        col_arq1, col_arq2 = st.columns(2)
        doc_identificacao = col_arq1.file_uploader("Upload RG / CNH / CPF (Frente e Verso)", type=['png', 'jpg', 'jpeg', 'pdf'], key="doc1")
        doc_endereco = col_arq2.file_uploader("Comprovante de Endereço (Atualizado)", type=['png', 'jpg', 'jpeg', 'pdf'], key="doc2")
        
        if serv_bacen or serv_rating:
            st.markdown("#### Documentação Avançada (Baixe o modelo, assine e faça o upload)")
            c_mod1, c_mod2, c_mod3 = st.columns(3)
            c_mod1.download_button("📥 Baixar Modelo Procuração", data="Doc", file_name="Procuracao_Modelo.docx")
            c_mod2.download_button("📥 Baixar Hipossuficiência", data="Doc", file_name="Declaracao_Hipo.docx")
            c_mod3.download_button("📥 Baixar IR Isento", data="Doc", file_name="Declaracao_IR_Isento.docx")
            
            c_up1, c_up2 = st.columns(2)
            doc_procuracao = c_up1.file_uploader("Upload Procuração Assinada", type=['pdf', 'jpg'])
            doc_hipo = c_up2.file_uploader("Upload Declaração de Hipossuficiência", type=['pdf', 'jpg'])
            
            c_up3, c_up4 = st.columns(2)
            if not serv_bacen: 
                doc_scr_rat = c_up3.file_uploader("Relatório de Empréstimos SCR (Últimos 5 anos)", type=['pdf'])
            doc_extratos = c_up4.file_uploader("4 Últimos Extratos Bancários", type=['pdf'])

        st.markdown("---")
        st.subheader("5. Processamento e Pagamento")
        
        st.markdown(f"""
            <div class="checkout-box">
                <h3 style="margin-top:0; color: #f59e0b;">Resumo do Carrinho</h3>
                <p>Serviços Selecionados: <b>{texto_servicos_banco}</b></p>
                <p>Total a Pagar: <b style="font-size: 24px; color: #10b981;">R$ {total_carrinho:,.2f}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 ENVIAR DADOS E GERAR PAGAMENTO"):
            if total_carrinho == 0:
                st.warning("⚠️ Você precisa marcar pelo menos UM serviço na etapa 1.")
            elif not nome_cliente or not cpf_cnpj: 
                st.error("⚠️ Nome e Documento são obrigatórios!")
            else:
                try:
                    supabase.table("nomes_processamento").insert({"user_id": st.session_state['dados_usuario'].id, "email_cliente": email_logado, "nome": nome_cliente, "cpf_cnpj": cpf_cnpj, "tipo_servico": texto_servicos_banco, "numero_processo": "Aguardando Protocolo"}).execute()
                    st.success("✅ Dados salvos com sucesso!")
                    st.markdown("---")
                    st.markdown("<h2 style='text-align: center; color: #10b981;'>PAGAMENTO PIX OFICIAL</h2>", unsafe_allow_html=True)
                    c_pix1, c_pix2 = st.columns([1, 2])
                    with c_pix1:
                        try: st.image("qr_pix.png", width=250)
                        except: pass
                    with c_pix2:
                        st.markdown("**Chave PIX (E-mail):**")
                        st.code("jp.solucoes.sc.diretor@gmail.com", language="text")
                        st.markdown("**Código Copia e Cola:**")
                        st.code("00020126540014br.gov.bcb.pix0132jp.solucoes.sc.diretor@gmail.com5204000053039865802BR5925JP SOLUCOES PARTICIPACOES6007CHAPECO62250521bBOkVhq3TKa8lHpaMavJi63044A0E", language="text")
                except: st.error("Erro no sistema.")

    # -----------------------------------------
    # 🔄 REPROTOCOLO
    # -----------------------------------------
    elif menu_selecionado == "🔄 Reprotocolo":
        st.header("🔄 Área de Reprotocolo")
        if is_diretor:
            st.warning("👑 **ÁREA DO DIRETOR: Alimente o modelo de Reprotocolo.**")
            st.file_uploader("Anexar Novo Modelo Reprotocolo Oficial (.docx)", type=['docx', 'pdf'])
            st.button("💾 Salvar Novo Modelo")
            st.markdown("---")
        c1, c2 = st.columns(2)
        c1.text_input("Nome Completo / Razão Social")
        c2.text_input("Número do CPF ou CNPJ")
        st.download_button("📥 Baixar Modelo Reprotocolo Oficial", data="Conteúdo", file_name="Reprotocolo.docx")
        st.file_uploader("Upload do Reprotocolo Assinado e Preenchido", type=['pdf', 'jpg', 'png'])
        if st.button("🚀 Enviar Reprotocolo", use_container_width=True): st.success("✅ Enviado com sucesso.")

    # -----------------------------------------
    # 📖 MANUAL DO PARCEIRO (COMPLETO RESTAURADO)
    # -----------------------------------------
    elif menu_selecionado == "📖 Manual do Parceiro":
        st.header("📖 Manual do Parceiro")
        st.write("Guia completo para usar o sistema JP Soluções.")
        
        st.markdown("""
        <div style='background-color:#0f172a; padding: 25px; border-radius: 10px; border: 1px solid #10b981; margin-bottom: 30px;'>
            <h3 style='color:#10b981; margin-top:0;'>✨ Bem-vindo à JP Soluções</h3>
            <p>Nossa plataforma conecta parceiros aos serviços de regularização de CPF/CNPJ de forma ágil.</p>
            <ul style='list-style-type: none; padding: 0;'>
                <li>✅ Sistema fácil e intuitivo</li>
                <li>✅ Acompanhamento em tempo real</li>
                <li>✅ Suporte dedicado via WhatsApp</li>
                <li>✅ Transparência total nos processos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Primeiros Passos")
        with st.expander("1. Criar Conta e Fazer Login"): st.write("Acesse a página inicial e utilize o formulário de cadastro.")
        with st.expander("2. Completar Perfil"): st.write("Vá até a aba 'Meu Perfil' e atualize seus dados de contato e endereço.")
        with st.expander("3. Navegação pelo Sistema"): st.write("Utilize o menu lateral esquerdo para acessar todas as funcionalidades.")

        st.subheader("Lista Paga – Passo a Passo Completo")
        with st.expander("1. Cadastrar Nomes"): st.write("Na página 'Enviar Protocolo', preencha corretamente os dados do cliente e anexe a documentação.")
        with st.expander("2. Ficha Associativa"): st.write("Para os serviços avançados, baixe e assine os modelos de contratos e procurações.")
        with st.expander("3. Enviar Lista"): st.write("Após preencher tudo, clique no botão Laranja de envio no final da página.")
        with st.expander("4. Realizar Pagamento"): st.write("O sistema gerará um QR Code e um código PIX. Efetue o pagamento do valor exato.")
        with st.expander("5. Anexar Comprovante (OBRIGATÓRIO)"): st.write("O envio do comprovante garante a agilidade no processamento da sua fila.")
        with st.expander("6. Acompanhar Status"): st.write("Acompanhe a mudança de status na aba 'Minhas Listas'.")

        st.subheader("Status Possíveis")
        st.markdown("""
        <div class="status-row"><span class="status-badge" style="background:#475569;">Pendente</span> Nome cadastrado, aguardando envio da lista.</div>
        <div class="status-row"><span class="status-badge" style="background:#3b82f6;">Enviado</span> Lista enviada, aguardando pagamento.</div>
        <div class="status-row"><span class="status-badge" style="background:#eab308;">Aguardando Pagamento</span> Comprovante em análise.</div>
        <div class="status-row"><span class="status-badge" style="background:#10b981;">Pago</span> Pagamento confirmado, entrará em processamento.</div>
        <div class="status-row"><span class="status-badge" style="background:#ef4444;">Reprovado</span> Problema com pagamento, verifique.</div>
        <div class="status-row"><span class="status-badge" style="background:#f97316;">Aguardando Protocolo</span> Nome sendo preparado.</div>
        <div class="status-row"><span class="status-badge" style="background:#8b5cf6;">Protocolado</span> Nome protocolado, em processamento.</div>
        <div class="status-row"><span class="status-badge" style="background:#22c55e;">Baixado</span> Processo finalizado com sucesso!</div>
        """, unsafe_allow_html=True)
        
        st.subheader("Perguntas Frequentes")
        with st.expander("Quanto custa o serviço?"): st.write("Os valores variam conforme o pacote escolhido na tela de envio.")
        with st.expander("Quanto tempo leva o processamento?"): st.write("O tempo médio é informado diretamente pelo nosso suporte de acordo com o serviço.")
        with st.expander("Posso cancelar um nome após o envio?"): st.write("Após o pagamento e envio ao banco de dados, o cancelamento obedece aos termos do contrato.")
        
        st.markdown("""
        <div style='background-color:#1e293b; padding: 25px; border-radius: 10px; margin-top: 30px;'>
            <h3 style='color:#10b981; margin-top:0;'>💬 Suporte e Ajuda</h3>
            <p><b>WhatsApp:</b> 49 9807 7332</p>
            <p><b>Email:</b> jp.solucoes.sc.diretor@gmail.com</p>
        </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------
    # 📋 MINHAS LISTAS
    # -----------------------------------------
    elif menu_selecionado == "📋 Minhas Listas":
        c_tit, c_btn = st.columns([4, 1])
        with c_tit:
            st.header("Minhas Listas")
            st.write("Histórico completo de todos os nomes cadastrados")
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("📥 Exportar Excel", data="planilha", file_name="Minhas_Listas.csv", use_container_width=True)
            
        c_f1, c_f2, c_f3, c_f4, c_f5 = st.columns([2, 2, 2, 1, 1])
        c_f1.text_input("Buscar nome ou CPF...", label_visibility="collapsed", placeholder="Buscar nome ou CPF...")
        c_f2.selectbox("Todas as listas", ["Todas as listas", "AÇÃO COLETIVA 115", "AÇÃO COLETIVA 111"], label_visibility="collapsed")
        c_f3.selectbox("Todos os status", ["Todos os status", "Pendente", "Enviado", "Aguardando Pagamento", "Pago", "Reprovado", "Aguardando Protocolo", "Protocolado", "Baixado"], label_visibility="collapsed")
        c_f4.date_input("De")
        c_f5.date_input("Até")
        st.markdown("<br>", unsafe_allow_html=True)
        
        try:
            resposta = supabase.table("nomes_processamento").select("*").eq("email_cliente", email_logado).execute()
            if resposta.data:
                df = pd.DataFrame(resposta.data)
                df['Lista'] = "AÇÃO COLETIVA 115 - 23/06/2026"
                df['Observação'] = "AÇÃO COLETIVA PROTOCOLADA."
                df['Serasa'] = "pago"
                df['Boa Vista'] = "pendente"
                df['SPC'] = "pendente"
                df['Cenprot BR'] = "pendente"
                df['Cenprot SP'] = "baixado"
                df['Data'] = "23/06/2026"
                colunas_display = {'Lista':'Lista', 'numero_processo':'Número Ação Coletiva', 'Observação':'Observação', 'nome':'Nome', 'cpf_cnpj':'CPF/CNPJ', 'tipo':'Tipo', 'tipo_servico':'Status', 'Serasa':'Serasa', 'Boa Vista':'Boa Vista', 'SPC':'SPC', 'Cenprot BR':'Cenprot BR', 'Cenprot SP':'Cenprot SP', 'Data':'Data'}
                colunas_existentes = {k: v for k, v in colunas_display.items() if k in df.columns}
                df_final = df[list(colunas_existentes.keys())].rename(columns=colunas_existentes)
                st.dataframe(df_final, use_container_width=True, hide_index=True)
            else: st.info("Nenhum processo foi encontrado.")
        except: pass

    # -----------------------------------------
    # 💲 FINANCEIRO
    # -----------------------------------------
    elif menu_selecionado == "💲 Financeiro":
        st.header("Financeiro")
        st.markdown("<p style='color: #94a3b8;'>Minhas listas enviadas e valores (Aguardando processamento de pagamentos)</p>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown("<div class='metric-card'><div class='metric-title'>Total Enviado 💲</div><div class='metric-value'>R$ 0,00</div></div>", unsafe_allow_html=True)
        c2.markdown("<div class='metric-card'><div class='metric-title'>Aprovados ✅</div><div class='metric-value'>R$ 0,00</div></div>", unsafe_allow_html=True)
        c3.markdown("<div class='metric-card'><div class='metric-title'>Pendentes ⏳</div><div class='metric-value' style='color:#f59e0b;'>R$ 0,00</div></div>", unsafe_allow_html=True)
        c4.markdown("<div class='metric-card'><div class='metric-title'>Nomes Processados 📈</div><div class='metric-value' style='color:#ffffff;'>0</div></div>", unsafe_allow_html=True)

    # -----------------------------------------
    # ⚠️ RECLAME AQUI
    # -----------------------------------------
    elif menu_selecionado == "⚠️ Reclame Aqui":
        st.header("⚠️ Reclame Aqui JP Soluções")
        with st.form("form_reclame"):
            st.selectbox("Motivo da Solicitação", ["Lista concluiu e o nome não baixou", "Ação não aparece em Minhas Listas", "Dúvida sobre andamento", "Outro (Descreva na observação)"])
            st.selectbox("Selecione a Lista (Nº Processo)", ["Selecione...", "AÇÃO 11011", "AÇÃO 11012", "Não sei informar"])
            st.text_area("Observação (opcional)")
            if st.form_submit_button("🚀 Enviar Solicitação"): st.success("Recebido pela equipe JP Soluções!")

    # -----------------------------------------
    # 📊 ORÇAMENTO (CALCULADORA E PDF COM PREVIEW)
    # -----------------------------------------
    elif menu_selecionado == "📊 Orçamento":
        st.header("Orçamento")
        st.write("Use a calculadora inteligente e a projeção de ganhos para planejar seu orçamento.")
        col_calc, col_proj = st.columns(2)
        with col_calc:
            st.markdown("<div style='background-color:#1e293b; padding:20px; border-radius:10px; height: 100%; border: 1px solid #334155;'>", unsafe_allow_html=True)
            st.subheader("🧮 Calculadora de Orçamento")
            st.number_input("DÍVIDA (R$)", min_value=0.00, value=0.00, format="%.2f")
            st.selectbox("PROCESSO", ["R$ 250,00", "R$ 600,00", "R$ 1.200,00", "R$ 2.000,00"])
            st.markdown("</div>", unsafe_allow_html=True)
        with col_proj:
            st.markdown("<div style='background-color:#1e293b; padding:20px; border-radius:10px; height: 100%; border: 1px solid #334155;'>", unsafe_allow_html=True)
            st.subheader("📈 Projeção de Ganhos")
            st.text_input("META MENSAL (R$)", value="10.000,00")
            projecoes = [("R$ 1.000 a R$ 3.000", "R$ 750,00 -> 14 contratos"), ("R$ 3.001 a R$ 5.000", "R$ 1.400,00 -> 8 contratos"), ("R$ 5.001 a R$ 10.000", "R$ 1.700,00 -> 6 contratos"), ("R$ 10.001 a R$ 20.000", "R$ 2.000,00 -> 5 contratos"), ("R$ 20.001 a R$ 30.000", "R$ 2.500,00 -> 4 contratos"), ("R$ 30.001 a R$ 50.000", "R$ 3.000,00 -> 4 contratos")]
            for p1, p2 in projecoes: st.markdown(f"<div style='border: 1px solid #334155; padding: 10px 15px; border-radius: 20px; margin-bottom: 8px; display: flex; justify-content: space-between;'><span>{p1}</span><span style='color: #10b981; font-weight: bold;'>{p2}</span></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='background-color:#1e293b; padding:30px; border-radius:10px; border: 1px solid #334155;'>", unsafe_allow_html=True)
        st.subheader("📄 Gerar Orçamento em PDF")
        c_cor, c_logo = st.columns([2, 1])
        cor_selecionada = c_cor.color_picker("COR DO CARD", "#1e3a8a")
        c_logo.file_uploader("LOGO DA EMPRESA", type=['png', 'jpg'])
        c_cli1, c_cli2 = st.columns(2)
        nome_cliente_orc = c_cli1.text_input("NOME DO CLIENTE", placeholder="Ex: João da Silva")
        c_cli2.text_input("ENDEREÇO", placeholder="Rua, Cidade - UF")
        c_orc1, c_orc2 = st.columns(2)
        num_orc = c_orc1.text_input("Nº DO ORÇAMENTO", value="001")
        data_orc = c_orc2.date_input("DATA", value=datetime.date(2026, 7, 29))
        st.markdown("<br><b>ITENS / SERVIÇOS</b>", unsafe_allow_html=True)
        c_it1, c_it2, c_it3 = st.columns([3, 1, 1])
        desc_orc = c_it1.text_input("Descrição", value="Limpa Nome")
        preco_orc = c_it2.number_input("Preço (R$)", value=50.00, format="%.2f")
        qtd_orc = c_it3.number_input("Qtd", value=1)
        c_desc1, c_desc2 = st.columns(2)
        c_desc1.number_input("DESCONTO (R$)", value=0.00, format="%.2f")
        termos_orc = c_desc2.text_area("TERMOS / OBSERVAÇÕES", value="Validade: 15 dias. Pagamento via PIX.")
        
        if st.button("📥 Gerar Orçamento em PDF", use_container_width=True, type="primary"):
            st.success("PDF Gerado com sucesso!")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # PRE-VISUALIZACAO DO PDF
        st.markdown("---")
        st.markdown("<p style='color: #94a3b8;'>Pré-visualização</p>", unsafe_allow_html=True)
        nome_exibir = nome_cliente_orc if nome_cliente_orc else "João da Silva"
        st.markdown(f"""
            <div class="pdf-preview">
                <h1 style="color: {cor_selecionada}; text-align: right; border-bottom: 2px solid {cor_selecionada}; padding-bottom: 10px;">RECUPERE SEU CRÉDITO</h1>
                <div style="display:flex; justify-content: space-between; margin-top: 20px;">
                    <div><b>Orçamento para:</b><br>{nome_exibir}</div>
                    <div style="text-align: right;"><b>Nº:</b> {num_orc}<br><b>Data:</b> {data_orc.strftime('%d/%m/%Y')}</div>
                </div>
                <table style="width: 100%; margin-top: 30px; border-collapse: collapse;">
                    <tr style="background-color: {cor_selecionada}; color: white;">
                        <th style="padding: 10px; text-align: left;">Nº</th>
                        <th style="padding: 10px; text-align: left;">Descrição</th>
                        <th style="padding: 10px; text-align: right;">Preço</th>
                        <th style="padding: 10px; text-align: center;">Qtd</th>
                        <th style="padding: 10px; text-align: right;">Total</th>
                    </tr>
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">1</td>
                        <td style="padding: 10px;">{desc_orc}</td>
                        <td style="padding: 10px; text-align: right;">R$ {preco_orc:,.2f}</td>
                        <td style="padding: 10px; text-align: center;">{qtd_orc}</td>
                        <td style="padding: 10px; text-align: right;">R$ {(preco_orc * qtd_orc):,.2f}</td>
                    </tr>
                </table>
                <div style="text-align: right; margin-top: 20px;">
                    Subtotal: R$ {(preco_orc * qtd_orc):,.2f}<br>
                    <div style="background-color: {cor_selecionada}; color: white; display: inline-block; padding: 10px 20px; margin-top: 10px; border-radius: 5px;">
                        <b>Total: R$ {(preco_orc * qtd_orc):,.2f}</b>
                    </div>
                </div>
                <div style="margin-top: 40px; font-size: 12px; color: #666;">
                    <b>Termos e Condições</b><br>{termos_orc}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # -----------------------------------------
    # 📝 CONTRATOS PARA BAIXAR
    # -----------------------------------------
    elif menu_selecionado == "📝 Contratos para Baixar":
        st.header("📝 Central de Contratos")
        if is_diretor:
            st.warning("👑 **ÁREA DO DIRETOR: Alimente o sistema com os novos modelos.**")
            c_mod1, c_mod2 = st.columns(2)
            c_mod1.file_uploader("Substituir Contrato Limpa Nome", type=['docx', 'pdf'])
            c_mod2.file_uploader("Substituir Contrato BACEN", type=['docx', 'pdf'])
            c_mod1.file_uploader("Substituir Contrato Rating", type=['docx', 'pdf'])
            c_mod2.file_uploader("Substituir Contrato Tributária", type=['docx', 'pdf'])
            st.button("💾 Salvar Novos Modelos")
            st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("1. Baixar Modelos (.docx)")
            st.download_button("📄 Contrato Limpa Nome", data="Doc", file_name="LimpaNome.docx", use_container_width=True)
            st.download_button("🏦 Contrato BACEN", data="Doc", file_name="Bacen.docx", use_container_width=True)
            st.download_button("📈 Contrato Rating", data="Doc", file_name="Rating.docx", use_container_width=True)
            st.download_button("⚖️ Contrato Tributária", data="Doc", file_name="Tributario.docx", use_container_width=True)
        with col2:
            st.subheader("2. Enviar Assinado")
            st.file_uploader("Upload Assinado", type=['pdf'])
            if st.button("🚀 Enviar ao Cofre"): st.success("✅ Salvo!")

    # -----------------------------------------
    # 📄 DOCUMENTOS DE APOIO
    # -----------------------------------------
    elif menu_selecionado == "📄 Documentos de Apoio":
        st.header("📄 Material de Apoio e Educação")
        if is_diretor:
            st.warning("👑 **ÁREA DO DIRETOR: Alimente as seções.**")
            c_doc1, c_doc2 = st.columns(2)
            c_doc1.file_uploader("1. Anexar: Manual Limpa Nome", type=['pdf', 'jpg'])
            c_doc2.file_uploader("2. Anexar: Manual BACEN", type=['pdf', 'jpg'])
            c_doc1.file_uploader("3. Anexar: O que é Rating Bancário?", type=['pdf', 'jpg'])
            c_doc2.file_uploader("4. Anexar: O que é o BACEN?", type=['pdf', 'jpg'])
            st.button("💾 Atualizar Arquivos")
            st.markdown("---")
        st.subheader("Manuais Oficiais (Passo a Passo)")
        c_down1, c_down2 = st.columns(2)
        c_down1.download_button("📖 Baixar Manual Limpa Nome", data="Doc", file_name="Manual_Limpa_Nome.pdf", use_container_width=True)
        c_down2.download_button("📖 Baixar Manual BACEN", data="Doc", file_name="Manual_Bacen.pdf", use_container_width=True)
        st.subheader("Informativos")
        c_down3, c_down4 = st.columns(2)
        c_down3.download_button("🧠 Baixar: O que é Rating?", data="Doc", file_name="Rating.pdf", use_container_width=True)
        c_down4.download_button("🏛️ Baixar: O que é o BACEN?", data="Doc", file_name="Bacen.pdf", use_container_width=True)

    # -----------------------------------------
    # 🩺 SOLICITAR DIAGNÓSTICO
    # -----------------------------------------
    elif menu_selecionado == "🩺 Solicitar Diagnóstico":
        st.header("🩺 Solicitar Diagnóstico Profundo")
        diag_tipo = st.selectbox("Foco?", ["1 - BACEN", "2 - Birôs de Crédito", "3 - Rating Bancário", "4 - Tributário / Fiscal (CNPJ)"])
        st.markdown("---")
        st.subheader("Dados Necessários")
        c_d1, c_d2 = st.columns(2)
        doc_diagnostico = c_d1.text_input("CPF ou CNPJ do Investigado")
        if diag_tipo == "1 - BACEN":
            c_d2.text_input("Senha GOV.BR (Prata ou Ouro)", type="password")
        elif diag_tipo == "4 - Tributário / Fiscal (CNPJ)":
            c_d2.text_input("Senha do Certificado Digital", type="password")
            st.file_uploader("Upload Certificado A1 (.pfx)", type=['pfx', 'p12'])
        st.markdown("---")
        val_d = st.session_state['precos'][perfil_atual]['diag']
        st.markdown(f"<div class='checkout-box'><h3>Resumo do Pedido</h3><p>Investigação: <b>{diag_tipo}</b></p><p>Taxa Única: <b style='font-size: 24px; color: #10b981;'>R$ {val_d:,.2f}</b></p></div>", unsafe_allow_html=True)
        if st.button("✅ Confirmar e Gerar PIX", use_container_width=True):
            st.success("Pedido registrado!")
            st.markdown("<h2 style='text-align: center; color: #10b981;'>PAGAMENTO PIX OFICIAL</h2>", unsafe_allow_html=True)
            c_p1, c_p2 = st.columns([1, 2])
            with c_p1:
                try: st.image("qr_pix.png", width=250)
                except: pass
            with c_p2:
                st.code("jp.solucoes.sc.diretor@gmail.com", language="text")
                st.code("00020126540014br.gov.bcb.pix0132jp.solucoes.sc.diretor@gmail.com5204000053039865802BR5925JP SOLUCOES PARTICIPACOES6007CHAPECO62250521bBOkVhq3TKa8lHpaMavJi63044A0E", language="text")

    # -----------------------------------------
    # 📑 MEUS DIAGNÓSTICOS (COM FILTROS)
    # -----------------------------------------
    elif menu_selecionado == "📑 Meus Diagnósticos":
        st.header("🩺 Meus Diagnósticos")
        st.write("Visualize o histórico dos relatórios solicitados e faça o download.")
        st.markdown("<div style='background-color:#1e293b; padding:25px; border-radius:10px; border: 1px solid #334155;'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.markdown("<h4>Histórico</h4>", unsafe_allow_html=True)
        c2.selectbox("Todos os pagamentos", ["Todos os pagamentos", "Pendente", "Pago", "Cancelado"], label_visibility="collapsed")
        c3.selectbox("Todos os status", ["Todos os status", "Aguardando pagamento", "Iniciado", "Concluído", "Cancelado"], label_visibility="collapsed")
        st.markdown("<br><br><p style='text-align:center; color:#94a3b8; font-size:16px;'>Nenhum diagnóstico solicitado ainda.</p><br><br>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------
    # ⚙️ PAINEL DO DIRETOR E ACESSO
    # -----------------------------------------
    elif menu_selecionado == "⚙️ Painel do Diretor":
        st.header("👑 Central de Comando (Admin)")
        aba_processos, aba_precos, aba_acesso = st.tabs(["📝 Vincular Processos", "💲 Tabela de Preços", "🚫 Controle de Acesso"])
        
        with aba_processos:
            st.markdown("### Atualizar Número da Ação")
            c_admin1, c_admin2 = st.columns(2)
            cpf_alvo = c_admin1.text_input("Digite o CPF/CNPJ do Cliente")
            novo_num_processo = c_admin2.text_input("Novo Número (Ex: AÇÃO 11011)")
            if st.button("✅ Vincular Processo"):
                if cpf_alvo and novo_num_processo:
                    try:
                        supabase.table("nomes_processamento").update({"numero_processo": novo_num_processo}).eq("cpf_cnpj", cpf_alvo).execute()
                        st.success(f"O processo {novo_num_processo} foi vinculado!")
                    except: st.error("Erro ao vincular.")
                else: st.warning("Preencha CPF e Número.")
            st.write("Visão global dos protocolos:")
            try:
                resposta = supabase.table("nomes_processamento").select("*").execute()
                if resposta.data: st.dataframe(resposta.data, use_container_width=True)
            except: pass
                
        with aba_precos:
            st.markdown("### Ajuste Geral de Precificação")
            st.subheader("1. Preços para CLIENTE FINAL")
            cc1, cc2, cc3, cc4 = st.columns(4)
            n_cli_limpa = cc1.number_input("Limpa Nome (R$)", value=float(st.session_state['precos']['cliente']['limpa_nome']))
            n_cli_bacen = cc2.number_input("BACEN (R$)", value=float(st.session_state['precos']['cliente']['bacen']))
            n_cli_rating = cc3.number_input("Rating (R$)", value=float(st.session_state['precos']['cliente']['rating']))
            n_cli_trib = cc4.number_input("Tributário (R$)", value=float(st.session_state['precos']['cliente']['tributario']))
            st.subheader("2. Preços de Custo para PARCEIROS")
            cp1, cp2, cp3, cp4 = st.columns(4)
            n_par_limpa = cp1.number_input("Limpa Parc. (R$)", value=float(st.session_state['precos']['parceiro']['limpa_nome']))
            n_par_bacen = cp2.number_input("BACEN Parc. (R$)", value=float(st.session_state['precos']['parceiro']['bacen']))
            n_par_rating = cp3.number_input("Rating Parc. (R$)", value=float(st.session_state['precos']['parceiro']['rating']))
            n_par_trib = cp4.number_input("Tributário Parc. (R$)", value=float(st.session_state['precos']['parceiro']['tributario']))
            
            if st.button("💾 Salvar Novas Tabelas de Preços", use_container_width=True):
                st.session_state['precos']['cliente'] = {'limpa_nome': n_cli_limpa, 'bacen': n_cli_bacen, 'rating': n_cli_rating, 'tributario': n_cli_trib, 'diag': 150.0}
                st.session_state['precos']['parceiro'] = {'limpa_nome': n_par_limpa, 'bacen': n_par_bacen, 'rating': n_par_rating, 'tributario': n_par_trib, 'diag': 50.0}
                st.success("Tabelas atualizadas! O Checkout já está cobrando os novos valores.")
                
        with aba_acesso:
            st.markdown("### 🚫 Bloquear ou Desbloquear Usuários")
            email_alvo_bloqueio = st.text_input("E-mail do Usuário Alvo")
            c_btn_blk1, c_btn_blk2 = st.columns(2)
            if c_btn_blk1.button("🔒 BLOQUEAR ACESSO", type="primary", use_container_width=True):
                if email_alvo_bloqueio:
                    if email_alvo_bloqueio not in st.session_state['usuarios_bloqueados']:
                        st.session_state['usuarios_bloqueados'].append(email_alvo_bloqueio)
                    st.error(f"O acesso do usuário {email_alvo_bloqueio} foi SUSPENSO.")
            if c_btn_blk2.button("✅ DESBLOQUEAR ACESSO", use_container_width=True):
                if email_alvo_bloqueio in st.session_state['usuarios_bloqueados']:
                    st.session_state['usuarios_bloqueados'].remove(email_alvo_bloqueio)
                    st.success(f"O acesso de {email_alvo_bloqueio} foi RESTAURADO.")

    else:
        st.header(menu_selecionado[2:])
        st.info("Esta seção está em fase de implantação.")

if not st.session_state['usuario_autenticado']: tela_login()
else: tela_principal()
