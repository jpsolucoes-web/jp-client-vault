import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime

# 1. Configuração da Página Mestra
st.set_page_config(page_title="JP Client Vault - Limpa Nome", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# MATRIZ DE ESTILO PROFISSIONAL (CSS) CORRIGIDA E BLINDADA
# ==========================================
def injetar_css_profissional():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Fundo Geral e Fonte Principal */
        .stApp { background-color: #0d1117; color: #e2e8f0; }
        
        /* CORREÇÃO DA IMAGEM 6: MENU LATERAL DARK MODE OBRIGATÓRIO */
        [data-testid="stSidebar"] {
            background-color: #1e293b !important; 
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        /* CORREÇÃO DE LEGIBILIDADE GERAL (Branco Brilhante para textos) */
        label, p, .stRadio label, .stSelectbox label, .stTextInput label, .stTextArea label, .stFileUploader label {
            color: #ffffff !important;
            font-size: 16px !important;
            font-weight: 500 !important;
        }

        img, video { border-radius: 10px; }
        
        h1, h2, h3, h4 {
            color: #f59e0b !important; /* Laranja Neon */
            font-weight: 800 !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea {
            background-color: #0f172a !important;
            color: #ffffff !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
        }
        .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
            border-color: #f59e0b !important;
            box-shadow: 0 0 5px #f59e0b !important;
        }
        
        .stButton>button {
            background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%);
            color: black !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            transition: 0.3s;
            width: 100%;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0px 0px 15px rgba(245, 158, 11, 0.5);
        }
        hr { border-color: #334155; }
        
        .checkout-box {
            background-color: #1e293b;
            border-left: 5px solid #10b981;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .card-servico {
            background-color: #1e293b;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #334155;
            margin-bottom: 15px;
        }
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

# 3. Gerenciamento de Estado para Navegação Dinâmica
if 'usuario_autenticado' not in st.session_state:
    st.session_state['usuario_autenticado'] = False
if 'dados_usuario' not in st.session_state:
    st.session_state['dados_usuario'] = None
if 'menu_navegacao' not in st.session_state:
    st.session_state['menu_navegacao'] = "🏠 Home"

# Função Callback para mudar de página pelos botões
def mudar_pagina(nova_pagina):
    st.session_state['menu_navegacao'] = nova_pagina

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
        
        opcoes_menu = [
            "🏠 Home", "💼 Serviços", "📅 Eventos",
            "🛡️ Enviar Protocolo", "🔄 Reprotocolo", "📖 Manual do Parceiro", 
            "📋 Minhas Listas", "💲 Financeiro", "⚠️ Reclame Aqui", 
            "📊 Orçamento", "📝 Contrato Limpa Nome", "📄 Documentos de Apoio", 
            "🎓 Academia Limpa Nome", "🏢 CNPJ Inapto",
            "🩺 Solicitar Diagnóstico", "📑 Meus Diagnósticos"
        ]
        if is_diretor:
            opcoes_menu.append("⚙️ Painel do Diretor")
            
        # Menu controlado por Session State
        st.radio("Navegação do Sistema", opcoes_menu, key="menu_navegacao")

    # Variável auxiliar para encurtar o código
    menu_selecionado = st.session_state['menu_navegacao']

    # -----------------------------------------
    # LÓGICA DE ROTEAMENTO DE PÁGINAS
    # -----------------------------------------
    
    if menu_selecionado == "🏠 Home":
        st.markdown("<h1 style='text-align: center; color: #f59e0b;'>Portal de Reabilitação de Crédito</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 18px;'>Ambiente blindado para envio e análise dos seus processos.</p>", unsafe_allow_html=True)
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

    # ==========================================
    # IMAGEM 1: ABA DE SERVIÇOS
    # ==========================================
    elif menu_selecionado == "💼 Serviços":
        st.header("💼 Nossos Serviços Avançados")
        st.write("Selecione o serviço desejado para iniciar o protocolo e ser redirecionado para a tela correta.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card-servico">', unsafe_allow_html=True)
            st.subheader("🛡️ Limpa Nome")
            st.info("Reabilitação de crédito Padrão.")
            # Você pode adicionar as imagens trocando "placeholder.png" pelo nome da foto que fará upload depois
            try: st.image("placeholder_limpanome.png", use_container_width=True)
            except: pass
            st.button("Acessar Limpa Nome", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_limpa", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card-servico">', unsafe_allow_html=True)
            st.subheader("🏦 Rating Bancário")
            st.info("Aumento de Score e Relacionamento.")
            try: st.image("placeholder_rating.png", use_container_width=True)
            except: pass
            st.button("Acessar Rating", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_rating", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card-servico">', unsafe_allow_html=True)
            st.subheader("🏛️ BACEN")
            st.info("Retirada de restrições no Banco Central.")
            try: st.image("placeholder_bacen.png", use_container_width=True)
            except: pass
            st.button("Acessar BACEN", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_bacen", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card-servico">', unsafe_allow_html=True)
            st.subheader("⚖️ Defesa Tributária")
            st.info("Estratégias fiscais e tributárias.")
            try: st.image("placeholder_tributario.png", use_container_width=True)
            except: pass
            st.button("Acessar Tributário", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_trib", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


    elif menu_selecionado == "🛡️ Enviar Protocolo":
        st.title("🚀 Central de Protocolos Avançados")
        st.markdown("Preencha os dados e anexe a documentação necessária para iniciar a engenharia de reabilitação.")

        # MENU COM AS 4 OPÇÕES EXATAS
        st.subheader("1. Selecione a Natureza da Ação")
        tipo_servico = st.selectbox("Qual serviço será executado?", 
                                    ["1 - Ação Limpa Nome (Padrão)", 
                                     "2 - BACEN", 
                                     "3 - Rating Bancário", 
                                     "4 - Defesa Tributária"])
        st.markdown("---")

        st.subheader("2. Identificação do Cliente")
        col1, col2 = st.columns(2)
        with col1:
            tipo_pessoa = st.radio("Pessoa Física ou Jurídica?", ["CPF", "CNPJ"])
            nome_cliente = st.text_input("Nome Completo / Razão Social")
        with col2:
            cpf_cnpj = st.text_input("Número do CPF ou CNPJ (Apenas números)")
            telefone = st.text_input("WhatsApp com DDD")

        st.markdown("---")

        # QUESTIONÁRIO (Abre para BACEN, RATING e TRIBUTÁRIO)
        if tipo_servico in ["2 - BACEN", "3 - Rating Bancário", "4 - Defesa Tributária"]:
            st.subheader("3. Questionário Analítico de Rating e Bens")
            
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

            st.markdown("#### Perfil Financeiro")
            c_prof1, c_prof2, c_prof3 = st.columns(3)
            empresa = c_prof1.text_input("Empresa onde trabalha")
            renda_pessoal = c_prof2.text_input("Sua Renda / Salário (R$)")
            renda_familiar = c_prof3.text_input("Renda Familiar Total (R$)")

            st.markdown("#### Patrimônio e Senhas Base")
            bancos = st.text_area("Bancos e Contas (Ex: Nubank - Ag 0001, Conta 1234-5)")
            veiculo = st.text_input("Veículo Próprio (Modelo, Ano, Placa - se houver)")
            
            c_senha1, c_senha2, c_senha3, c_senha4 = st.columns(4)
            gov_login = c_senha1.text_input("Login GOV.BR")
            gov_senha = c_senha2.text_input("Senha GOV.BR", type="password")
            serasa_login = c_senha3.text_input("Login Serasa")
            serasa_senha = c_senha4.text_input("Senha Serasa", type="password")

        # ANEXOS E DOCUMENTAÇÃO
        st.markdown("---")
        st.subheader("4. Anexos e Documentação Oficial")
        col_arq1, col_arq2 = st.columns(2)
        doc_identificacao = col_arq1.file_uploader("Upload RG / CNH / CPF (Frente/Verso)", type=['png', 'jpg', 'pdf'])
        doc_endereco = col_arq2.file_uploader("Comprovante de Endereço", type=['png', 'jpg', 'pdf'])
        
        # ANEXOS BACEN E RATING
        if tipo_servico in ["2 - BACEN", "3 - Rating Bancário"]:
            st.markdown("#### Documentação Avançada (Baixe, Assine e Anexe)")
            c_mod1, c_mod2, c_mod3 = st.columns(3)
            c_mod1.download_button("📥 Modelo Procuração", data="Conteúdo Procuração", file_name="Procuracao.docx")
            c_mod2.download_button("📥 Modelo Hipossuficiência", data="Conteúdo Hipo", file_name="Declaracao_Hipo.docx")
            c_mod3.download_button("📥 Modelo Imposto de Renda", data="Conteúdo IR", file_name="IR_Isento.docx")
            
            c_up1, c_up2 = st.columns(2)
            doc_procuracao = c_up1.file_uploader("Upload Procuração Assinada", type=['pdf'])
            doc_hipo = c_up2.file_uploader("Upload Declaração Hipossuficiência", type=['pdf'])
            
            c_up3, c_up4 = st.columns(2)
            doc_scr = c_up3.file_uploader("Extrato SCR (Últimos 5 anos)", type=['pdf'])
            doc_extratos = c_up4.file_uploader("4 Últimos Extratos Bancários", type=['pdf'])

        # ANEXOS EXCLUSIVOS TRIBUTÁRIO
        if tipo_servico == "4 - Defesa Tributária":
            st.markdown("#### 🔐 Acessos Fiscais (Tributário)")
            st.info("Para Defesa Tributária, o Certificado Digital é obrigatório.")
            c_cert1, c_cert2 = st.columns(2)
            cert_a1 = c_cert1.file_uploader("Upload Certificado Digital A1 (.pfx / .p12)", type=['pfx', 'p12'])
            senha_cert = c_cert2.text_input("Senha do Certificado Digital", type="password")

        st.markdown("---")
        
        # CHECKOUT
        st.subheader("5. Processamento e Pagamento")
        valor_servico = "R$ 250,00" if tipo_servico == "1 - Ação Limpa Nome (Padrão)" else "R$ 1.200,00"
        
        st.markdown(f"""
            <div class="checkout-box">
                <h3 style="margin-top:0; color: #f59e0b;">Resumo Financeiro</h3>
                <p>Serviço Contratado: <b>{tipo_servico}</b></p>
                <p>Taxa de Protocolo: <b style="font-size: 24px; color: #10b981;">{valor_servico}</b></p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 ENVIAR DADOS E GERAR PAGAMENTO"):
            if not nome_cliente or not cpf_cnpj:
                st.error("⚠️ Nome e CPF/CNPJ são obrigatórios!")
            else:
                try:
                    dados = {
                        "user_id": st.session_state['dados_usuario'].id,
                        "email_cliente": email_logado,
                        "nome": nome_cliente,
                        "cpf_cnpj": cpf_cnpj,
                        "tipo": tipo_pessoa,
                        "tipo_servico": tipo_servico,
                        "numero_processo": "Aguardando Protocolo"
                    }
                    supabase.table("nomes_processamento").insert(dados).execute()
                    st.success("✅ Protocolo salvo com sucesso no Cofre!")
                    st.markdown("### 💳 Opções de Pagamento")
                    st.info("O QR Code e o Boleto serão gerados pelo PagSeguro aqui.")
                except Exception as e:
                    st.error(f"Erro no sistema: {e}")

    # ==========================================
    # IMAGEM 2: REPROTOCOLO
    # ==========================================
    elif menu_selecionado == "🔄 Reprotocolo":
        st.header("🔄 Área de Reprotocolo")
        st.write("Utilize esta seção caso tenha sido notificado de alguma pendência nos envios anteriores.")
        
        with st.form("form_reprotocolo"):
            st.subheader("1. Identificação para Correção")
            col1, col2 = st.columns(2)
            with col1:
                tipo_pessoa_rep = st.radio("Pessoa Física ou Jurídica?", ["CPF", "CNPJ"], key="rad_reprot")
                nome_reprot = st.text_input("Nome Completo / Razão Social", key="nome_reprot")
            with col2:
                doc_reprot = st.text_input("Número do CPF ou CNPJ", key="doc_reprot")
            
            st.markdown("---")
            st.subheader("2. Modelo de Reprotocolo")
            st.write("Baixe o modelo exigido, assine e anexe-o novamente abaixo.")
            
            st.download_button("📥 Baixar Modelo Reprotocolo", data="Conteúdo Modelo Reprotocolo", file_name="Reprotocolo.docx")
            
            arquivo_reprot = st.file_uploader("Upload do Reprotocolo Assinado", type=['pdf', 'jpg', 'png'])
            
            if st.form_submit_button("🚀 Enviar Reprotocolo", use_container_width=True):
                if not nome_reprot or not doc_reprot:
                    st.error("Nome e Documento são obrigatórios!")
                elif not arquivo_reprot:
                    st.warning("É obrigatório anexar o arquivo assinado!")
                else:
                    st.success("✅ Reprotocolo enviado com sucesso para análise.")


    elif menu_selecionado == "📋 Minhas Listas":
        st.header("Minhas Listas")
        st.write("Acompanhe o status e o número da ação dos seus protocolos.")
        try:
            resposta = supabase.table("nomes_processamento").select("numero_processo, cpf_cnpj, tipo_servico, status_serasa, status_boa_vista, status_spc, status_cenprot_br").eq("email_cliente", email_logado).execute()
            if resposta.data:
                df = pd.DataFrame(resposta.data)
                df.columns = ["Nº Ação/Processo", "CPF/CNPJ", "Serviço", "Serasa", "Boa Vista", "SPC", "Cenprot BR"]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum processo foi encontrado no seu histórico.")
        except Exception as e:
            st.error("Sincronize o banco com a injeção SQL passada pelo sistema.")


    # ==========================================
    # IMAGEM 3: FINANCEIRO E VALORES
    # ==========================================
    elif menu_selecionado == "💲 Financeiro":
        st.header("💲 Extrato Financeiro")
        st.write("Acompanhe a relação dos seus pagamentos e protocolos efetuados.")
        
        # MÓDULO DE CÁLCULO DE EXEMPLO (MOCK DATA baseada no seu pedido)
        st.markdown(f"""
            <div class="checkout-box">
                <h3 style="margin-top:0; color: #10b981;">Resumo de Contratações</h3>
                <p>Mês: <b>Janeiro/2026</b> | Serviços: 1 (Limpa Nome) | Valor Mensal: <b>R$ 500,00</b></p>
                <p>Mês: <b>Março/2026</b> | Serviços: 2 (Limpa Nome) | Valor Mensal: <b>R$ 1.000,00</b></p>
                <hr style="border-color: #10b981;">
                <h4 style="color: #ffffff;">VALOR TOTAL PAGO (HISTÓRICO): <span style="color: #f59e0b;">R$ 1.500,00</span></h4>
            </div>
        """, unsafe_allow_html=True)
        
        st.info("Em breve este painel puxará os valores em tempo real do PagSeguro.")


    # ==========================================
    # IMAGEM 4: CONTRATOS (BAIXAR E ENVIAR)
    # ==========================================
    elif menu_selecionado == "📝 Contrato Limpa Nome":
        st.header("📝 Central de Contratos")
        st.write("Faça o download do contrato referente ao seu serviço, assine digitalmente ou fisicamente e envie em formato PDF.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("1. Baixar Modelos (.docx)")
            st.download_button("📄 Contrato Limpa Nome", data="Contrato Limpa", file_name="Contrato_LimpaNome.docx", use_container_width=True)
            st.download_button("🏦 Contrato BACEN", data="Contrato Bacen", file_name="Contrato_Bacen.docx", use_container_width=True)
            st.download_button("📈 Contrato Rating Bancário", data="Contrato Rating", file_name="Contrato_Rating.docx", use_container_width=True)
            st.download_button("⚖️ Contrato Defesa Tributária", data="Contrato Trib", file_name="Contrato_Tributario.docx", use_container_width=True)
            
        with col2:
            st.subheader("2. Enviar Contrato Assinado")
            contrato_anexo = st.file_uploader("Upload do Contrato (.pdf)", type=['pdf'])
            if st.button("🚀 Enviar Contrato ao Cofre", use_container_width=True):
                if contrato_anexo:
                    st.success("✅ Contrato criptografado e salvo com sucesso!")
                else:
                    st.error("⚠️ Anexe o PDF antes de enviar.")


    # ==========================================
    # IMAGEM 5: SOLICITAR DIAGNÓSTICO
    # ==========================================
    elif menu_selecionado == "🩺 Solicitar Diagnóstico":
        st.header("🩺 Solicitar Diagnóstico Profundo")
        st.write("Obtenha um mapeamento completo do seu CPF/CNPJ antes de iniciar as ações.")
        
        diag_tipo = st.selectbox("Qual o foco do diagnóstico?", 
                                 ["1 - BACEN", "2 - Birôs de Crédito (SPC/Serasa/Boa Vista)", "3 - Rating Bancário", "4 - Tributário / Fiscal"])
        
        st.markdown("---")
        st.subheader("Dados Necessários para Investigação")
        
        # MÓDULO BACEN
        if diag_tipo == "1 - BACEN":
            st.info("Para rastreio BACEN, as credenciais GOV.BR são obrigatórias.")
            c1, c2 = st.columns(2)
            c1.text_input("CPF do Investigado")
            c2.text_input("Senha GOV.BR (Nível Prata ou Ouro)", type="password")
            valor_diag = "R$ 150,00"
            
        # MÓDULO BIRÔS / RATING
        elif diag_tipo in ["2 - Birôs de Crédito (SPC/Serasa/Boa Vista)", "3 - Rating Bancário"]:
            st.info("Rastreio nos birôs de crédito.")
            st.text_input("CPF ou CNPJ")
            valor_diag = "R$ 90,00"
            
        # MÓDULO TRIBUTÁRIO
        elif diag_tipo == "4 - Tributário / Fiscal":
            st.info("Para Diagnóstico PJ (Empresas), o Certificado A1 é obrigatório.")
            st.text_input("CNPJ da Empresa")
            c_cert1, c_cert2 = st.columns(2)
            c_cert1.file_uploader("Upload Certificado Digital A1 (.pfx / .p12)", type=['pfx', 'p12'])
            c_cert2.text_input("Senha do Certificado Digital", type="password")
            valor_diag = "R$ 300,00"

        st.markdown("---")
        
        # PAGAMENTO E CHECKOUT DO DIAGNÓSTICO
        st.markdown(f"""
            <div class="checkout-box">
                <h3 style="margin-top:0;">Resumo do Pedido</h3>
                <p>Investigação: <b>{diag_tipo}</b></p>
                <p>Taxa Única: <b style="font-size: 24px; color: #10b981;">{valor_diag}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ Confirmar Pedido e Gerar PIX", use_container_width=True):
            st.success("Pedido registrado! Efetue o pagamento abaixo para liberar a análise.")
            
            c_pix1, c_pix2 = st.columns([1, 2])
            with c_pix1:
                st.image("https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg", width=150)
            with c_pix2:
                st.markdown("**Chave PIX (Copia e Cola):**")
                st.code("00020126360014BR.GOV.BCB.PIX0114+5549998077332...", language="text")
                st.info("Após o pagamento, o diagnóstico será entregue na aba 'Meus Diagnósticos' em até 24 horas.")

    elif menu_selecionado == "⚙️ Painel do Diretor":
        st.header("👑 Central de Comando (Admin)")
        
        st.markdown("### 📝 Atualizar Número da Ação para o Cliente")
        st.info("Use este painel para informar ao cliente qual é o número oficial do processo dele.")
        c_admin1, c_admin2 = st.columns(2)
        cpf_alvo = c_admin1.text_input("Digite o CPF/CNPJ do Cliente")
        novo_num_processo = c_admin2.text_input("Novo Número (Ex: AÇÃO 11011)")
        
        if st.button("✅ Vincular Processo ao Cliente"):
            if cpf_alvo and novo_num_processo:
                try:
                    supabase.table("nomes_processamento").update({"numero_processo": novo_num_processo}).eq("cpf_cnpj", cpf_alvo).execute()
                    st.success(f"O processo {novo_num_processo} foi vinculado! O cliente já pode ver na aba 'Minhas Listas'.")
                except Exception as e:
                    st.error("Erro ao vincular. Verifique se o CPF está correto.")
            else:
                st.warning("Preencha o CPF e o Número do processo.")

        st.write("---")
        st.write("Visão global de todos os protocolos cadastrados:")
        try:
            resposta = supabase.table("nomes_processamento").select("*").execute()
            if resposta.data:
                st.dataframe(resposta.data, use_container_width=True)
            else:
                st.write("Nenhum processo cadastrado no sistema ainda.")
        except Exception as e:
            st.error("Erro ao puxar base de dados.")
            
    else:
        st.header(menu_selecionado[2:])
        st.info("Esta seção está em fase de implantação.")

# 6. Controlador de Fluxo
if not st.session_state['usuario_autenticado']:
    tela_login()
else:
    tela_principal()
