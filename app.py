import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime
import streamlit.components.v1 as components

# 1. Configuração da Página Mestra
st.set_page_config(page_title="JP Client Vault", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# INICIALIZAÇÃO DE PREÇOS (SESSÃO)
# ==========================================
if 'precos' not in st.session_state:
    st.session_state['precos'] = {
        'cliente': {'limpa_nome': 250.00, 'bacen': 1200.00, 'rating': 500.00, 'tributario': 2000.00, 'diag': 150.00},
        'parceiro': {'limpa_nome': 150.00, 'bacen': 600.00, 'rating': 250.00, 'tributario': 1000.00, 'diag': 50.00}
    }

is_parceiro = st.query_params.get("tipo") == "parceiro"
perfil_atual = 'parceiro' if is_parceiro else 'cliente'

# ==========================================
# MATRIZ DE ESTILO PROFISSIONAL (CSS)
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
        .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus { border-color: #f59e0b !important; box-shadow: 0 0 5px #f59e0b !important; }
        .stButton>button { background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%); color: black !important; font-weight: bold !important; border: none !important; border-radius: 8px !important; padding: 10px 20px !important; transition: 0.3s; width: 100%; }
        .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 0px 15px rgba(245, 158, 11, 0.5); }
        hr { border-color: #334155; }
        .checkout-box { background-color: #1e293b; border-left: 5px solid #10b981; padding: 20px; border-radius: 8px; margin-top: 20px; }
        .card-servico { background-color: #1e293b; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #334155; margin-bottom: 15px; }
        .metric-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: left; }
        .metric-title { color: #94a3b8; font-size: 14px; margin-bottom: 5px; font-weight: 600; }
        .metric-value { color: #10b981; font-size: 28px; font-weight: bold; margin: 0; }
        </style>
    """, unsafe_allow_html=True)

injetar_css_profissional()

# 2. Inicialização do Banco de Dados
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase: Client = init_connection()

# 3. Gerenciamento de Estado
if 'usuario_autenticado' not in st.session_state: st.session_state['usuario_autenticado'] = False
if 'dados_usuario' not in st.session_state: st.session_state['dados_usuario'] = None
if 'menu_navegacao' not in st.session_state: st.session_state['menu_navegacao'] = "🏠 Home"

def mudar_pagina(nova_pagina): st.session_state['menu_navegacao'] = nova_pagina

# 4. Login
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
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Autenticar Conexão", use_container_width=True):
                    try:
                        resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                        st.session_state['usuario_autenticado'] = True
                        st.session_state['dados_usuario'] = resposta.user
                        st.rerun()
                    except: st.error("Falha na autenticação.")
        with aba_cadastro:
            with st.form("cadastro_form"):
                novo_email = st.text_input("E-mail")
                nova_senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Criar Conta", use_container_width=True):
                    try:
                        supabase.auth.sign_up({"email": novo_email, "password": nova_senha})
                        st.success("Conta criada! Faça login.")
                    except Exception as e: st.error(f"Erro: {e}")

# 5. Interface Interna Principal
def tela_principal():
    email_logado = st.session_state['dados_usuario'].email
    is_diretor = (email_logado == "jp.solucoes.sc.diretor@gmail.com")

    with st.sidebar:
        try: st.image("logo.png", use_container_width=True)
        except: st.title("🛡️ JP Client Vault")
        if is_diretor: st.error("👑 MODO DIRETOR")
        else: st.success(f"👤 Cliente: {email_logado}")
        if is_parceiro: st.warning("🤝 MODO PARCEIRO (Valores Custo)")
        if st.button("Desconectar (Sair)", use_container_width=True):
            st.session_state['usuario_autenticado'] = False
            st.rerun()
        st.write("---")
        opcoes_menu = [
            "🏠 Home", "💼 Serviços", "📅 Eventos", "🛡️ Enviar Protocolo", "🔄 Reprotocolo", 
            "📖 Manual do Parceiro", "📋 Minhas Listas", "💲 Financeiro", "⚠️ Reclame Aqui", 
            "📊 Orçamento", "📝 Modelos de Contratos para Baixar", "📄 Documentos de Apoio", 
            "🎓 Academia Limpa Nome", "🏢 CNPJ Inapto", "🩺 Solicitar Diagnóstico", "📑 Meus Diagnósticos"
        ]
        if is_diretor: opcoes_menu.append("⚙️ Painel do Diretor")
        st.radio("Navegação", opcoes_menu, key="menu_navegacao", label_visibility="collapsed")

    menu = st.session_state['menu_navegacao']

    # -----------------------------------------
    # 🏠 HOME E RELÓGIO (COMPONENTS I-FRAME)
    # -----------------------------------------
    if menu == "🏠 Home":
        st.markdown("<h1 style='text-align: center; color: #f59e0b;'>Portal de Reabilitação de Crédito</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8;'>Ambiente blindado para envio e análise dos processos.</p>", unsafe_allow_html=True)
        
        # O Relógio Digital Oficial que funciona!
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
                
                // Formatação para ter sempre 2 dígitos
                hours = hours < 10 ? "0" + hours : hours;
                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;
                
                document.getElementById("clock_div").innerHTML = days + " Dias : " + hours + "h : " + minutes + "m : " + seconds + "s";
            }, 1000);
        </script>
        """
        components.html(clock_html, height=150)
        
        # Calibragem das imagens e vídeos (Lado a lado, tamanhos iguais)
        col_img, col_vid = st.columns(2)
        with col_img:
            try: st.image("valortecpflimpo.png", use_container_width=True)
            except: pass
        with col_vid:
            try: st.video("video1.mp4")
            except: st.info("O vídeo 'video1.mp4' não foi encontrado.")

    # -----------------------------------------
    # 💼 SERVIÇOS
    # -----------------------------------------
    elif menu == "💼 Serviços":
        st.header("💼 Nossos Serviços Avançados")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="card-servico"><h3>🛡️ Limpa Nome</h3><p>Reabilitação de crédito Padrão.</p></div>', unsafe_allow_html=True)
            st.button("Acessar Limpa Nome", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_limpa")
            st.markdown('<div class="card-servico"><h3>🏦 Rating Bancário</h3><p>Aumento de Score e Relacionamento.</p></div>', unsafe_allow_html=True)
            st.button("Acessar Rating", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_rat")
        with c2:
            st.markdown('<div class="card-servico"><h3>🏛️ BACEN</h3><p>Retirada de restrições no Banco Central.</p></div>', unsafe_allow_html=True)
            st.button("Acessar BACEN", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_bac")
            st.markdown('<div class="card-servico"><h3>⚖️ Defesa Tributária</h3><p>Estratégias fiscais e tributárias.</p></div>', unsafe_allow_html=True)
            st.button("Acessar Tributário", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",), key="btn_trib")

    # -----------------------------------------
    # 🛡️ ENVIAR PROTOCOLO
    # -----------------------------------------
    elif menu == "🛡️ Enviar Protocolo":
        st.title("🚀 Central de Protocolos")
        tipo_servico = st.selectbox("1. Natureza da Ação", ["1 - Ação Limpa Nome (Padrão)", "2 - BACEN", "3 - Rating Bancário", "4 - Defesa Tributária"])
        
        c1, c2 = st.columns(2)
        tipo_pessoa = c1.radio("Pessoa?", ["CPF", "CNPJ"])
        nome_cliente = c1.text_input("Nome / Razão Social")
        cpf_cnpj = c2.text_input("CPF ou CNPJ")
        
        if tipo_servico in ["2 - BACEN", "3 - Rating Bancário", "4 - Defesa Tributária"]:
            st.subheader("Questionário Analítico e Acessos")
            cs1, cs2 = st.columns(2)
            gov_login = cs1.text_input("Login GOV.BR")
            gov_senha = cs2.text_input("Senha GOV.BR", type="password")
            
        st.subheader("Anexos Oficiais")
        ca1, ca2 = st.columns(2)
        ca1.file_uploader("Upload RG/CNH/CPF", type=['png', 'jpg', 'pdf'])
        ca2.file_uploader("Comprovante de Endereço", type=['png', 'jpg', 'pdf'])
        
        if tipo_servico == "4 - Defesa Tributária":
            st.file_uploader("Certificado A1 (.pfx / .p12)", type=['pfx', 'p12'])
            st.text_input("Senha Certificado", type="password")

        # Checkout PIX
        if tipo_servico.startswith("1"): preco = st.session_state['precos'][perfil_atual]['limpa_nome']
        elif tipo_servico.startswith("2"): preco = st.session_state['precos'][perfil_atual]['bacen']
        elif tipo_servico.startswith("3"): preco = st.session_state['precos'][perfil_atual]['rating']
        else: preco = st.session_state['precos'][perfil_atual]['tributario']
        
        st.markdown(f"<div class='checkout-box'><h3>Taxa: R$ {preco:,.2f}</h3></div>", unsafe_allow_html=True)
        
        if st.button("🚀 ENVIAR DADOS E PAGAR VIA PIX"):
            if not nome_cliente or not cpf_cnpj: st.error("⚠️ Preencha Nome e CPF/CNPJ!")
            else:
                try:
                    supabase.table("nomes_processamento").insert({
                        "user_id": st.session_state['dados_usuario'].id, "email_cliente": email_logado,
                        "nome": nome_cliente, "cpf_cnpj": cpf_cnpj, "tipo_servico": tipo_servico, "numero_processo": "Aguardando"
                    }).execute()
                    st.success("✅ Salvo! Efetue o pagamento abaixo.")
                    
                    st.markdown("---")
                    st.markdown("<h2 style='text-align: center; color: #10b981;'>PAGAMENTO PIX OFICIAL</h2>", unsafe_allow_html=True)
                    cp1, cp2 = st.columns([1, 2])
                    with cp1:
                        try: st.image("qr_pix.png", width=250)
                        except: pass
                    with cp2:
                        st.markdown("**Chave PIX (E-mail):**")
                        st.code("jp.solucoes.sc.diretor@gmail.com", language="text")
                        st.markdown("**Código Copia e Cola:**")
                        st.code("00020126540014br.gov.bcb.pix0132jp.solucoes.sc.diretor@gmail.com5204000053039865802BR5925JP SOLUCOES PARTICIPACOES6007CHAPECO62250521bBOkVhq3TKa8lHpaMavJi63044A0E", language="text")
                except: st.error("Erro banco.")

    # -----------------------------------------
    # 🔄 REPROTOCOLO (COM ÁREA DO DIRETOR)
    # -----------------------------------------
    elif menu == "🔄 Reprotocolo":
        st.header("🔄 Área de Reprotocolo")
        
        if is_diretor:
            st.warning("👑 ÁREA DO DIRETOR: Alimente o modelo de Reprotocolo")
            st.file_uploader("Anexar Novo Modelo Reprotocolo", type=['docx', 'pdf'])
            st.button("Salvar Modelo")
            st.markdown("---")
            
        c1, c2 = st.columns(2)
        c1.radio("Pessoa?", ["CPF", "CNPJ"])
        nome = c1.text_input("Nome Completo")
        doc = c2.text_input("CPF ou CNPJ")
        st.download_button("📥 Baixar Modelo Oficial", data="Doc", file_name="Reprotocolo.docx")
        arq = st.file_uploader("Anexar Reprotocolo Assinado e Preenchido", type=['pdf', 'jpg'])
        if st.button("🚀 Enviar", use_container_width=True):
            if not nome or not doc or not arq: st.warning("Preencha e anexe o arquivo!")
            else: st.success("Enviado para análise!")

    # -----------------------------------------
    # 📋 MINHAS LISTAS (BANCO DE DADOS INTELIGENTE)
    # -----------------------------------------
    elif menu == "📋 Minhas Listas":
        st.header("Minhas Listas e Status")
        try:
            # Puxa tudo para não dar erro se faltar coluna
            res = supabase.table("nomes_processamento").select("*").eq("email_cliente", email_logado).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                
                # Cria colunas amigáveis apenas se elas existirem no banco
                colunas_display = {}
                if 'numero_processo' in df.columns: colunas_display['numero_processo'] = "Nº Ação/Processo"
                if 'cpf_cnpj' in df.columns: colunas_display['cpf_cnpj'] = "CPF/CNPJ"
                if 'tipo_servico' in df.columns: colunas_display['tipo_servico'] = "Serviço"
                
                # Injeta um Status Geral Visual
                df['Status Geral'] = "Em procedimento" 
                colunas_display['Status Geral'] = "Status"
                
                df_final = df[list(colunas_display.keys())].rename(columns=colunas_display)
                st.dataframe(df_final, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum processo foi finalizado ou enviado ainda.")
        except Exception as e:
            st.error("Falha ao sincronizar com o banco de dados. Contate o suporte.")

    # -----------------------------------------
    # 💲 FINANCEIRO (ZERADO E PREPARADO)
    # -----------------------------------------
    elif menu == "💲 Financeiro":
        st.header("Financeiro")
        st.markdown("<p style='color: #94a3b8;'>Minhas listas enviadas e valores (Aguardando processamento de pagamentos)</p>", unsafe_allow_html=True)
        
        # Variáveis começando zeradas conforme solicitado
        total_enviado = "0,00"
        aprovados = "0,00"
        pendentes = "0,00"
        processados = "0"
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='metric-card'><div class='metric-title'>Total Enviado 💲</div><div class='metric-value'>R$ {total_enviado}</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><div class='metric-title'>Aprovados ✅</div><div class='metric-value'>R$ {aprovados}</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><div class='metric-title'>Pendentes ⏳</div><div class='metric-value' style='color:#f59e0b;'>R$ {pendentes}</div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-card'><div class='metric-title'>Nomes Processados 📈</div><div class='metric-value' style='color:#ffffff;'>{processados}</div></div>", unsafe_allow_html=True)

    # -----------------------------------------
    # ⚠️ RECLAME AQUI
    # -----------------------------------------
    elif menu == "⚠️ Reclame Aqui":
        st.header("⚠️ Reclame Aqui JP Soluções")
        st.write("Canal de atendimento prioritário para correção de baixas não refletidas (Após 72h da conclusão).")
        
        with st.form("form_reclame"):
            st.selectbox("Motivo da Solicitação", ["Lista concluiu e o nome não baixou", "Ação não aparece em Minhas Listas", "Dúvida sobre andamento", "Outro (Descreva)"])
            st.selectbox("Selecione a Lista (Nº Processo)", ["Selecione...", "AÇÃO 11011", "AÇÃO 11012"])
            st.text_area("Observação (opcional)", placeholder="Descreva os detalhes do problema...")
            if st.form_submit_button("🚀 Enviar Solicitação"): st.success("Recebido pela equipe JP Soluções!")

    # -----------------------------------------
    # 📄 DOCUMENTOS DE APOIO (SEPARADOS)
    # -----------------------------------------
    elif menu == "📄 Documentos de Apoio":
        st.header("📄 Material de Apoio e Educação")
        
        # ÁREA DIRETOR: UPLOADS ESPECÍFICOS
        if is_diretor:
            st.warning("👑 **ÁREA DO DIRETOR: Alimente as 4 seções com arquivos JPG/PDF.**")
            cd1, cd2 = st.columns(2)
            cd1.file_uploader("1. Anexar: Manual Limpa Nome", type=['pdf', 'jpg', 'png'])
            cd2.file_uploader("2. Anexar: Manual BACEN", type=['pdf', 'jpg', 'png'])
            cd1.file_uploader("3. Anexar: O que é Rating Bancário?", type=['pdf', 'jpg', 'png'])
            cd2.file_uploader("4. Anexar: O que é BACEN?", type=['pdf', 'jpg', 'png'])
            st.button("💾 Atualizar Arquivos no Sistema")
            st.markdown("---")
            
        st.write("Baixe nossos manuais e imagens informativas para entender nossos serviços.")
        st.subheader("Manuais Oficiais")
        st.download_button("📖 Baixar Manual Limpa Nome", data="Doc", file_name="Manual_Limpa_Nome.pdf")
        st.download_button("📖 Baixar Manual BACEN", data="Doc", file_name="Manual_Bacen.pdf")
        
        st.subheader("Informativos")
        st.download_button("🧠 Baixar: O que é Rating Bancário?", data="Doc", file_name="O_que_e_Rating.pdf")
        st.download_button("🏛️ Baixar: O que é o BACEN?", data="Doc", file_name="O_que_e_Bacen.pdf")

    # -----------------------------------------
    # RESTANTE PADRÃO (Contratos, Diagnóstico, Painel Diretor)
    # -----------------------------------------
    elif menu == "📝 Modelos de Contratos para Baixar":
        st.header("Central de Contratos")
        if is_diretor:
            st.warning("👑 MODO DIRETOR: Suba novos contratos")
            c1, c2 = st.columns(2)
            c1.file_uploader("Substituir Contrato Limpa Nome", type=['docx', 'pdf'])
            c2.file_uploader("Substituir Contrato BACEN", type=['docx', 'pdf'])
            st.button("Salvar")
            st.markdown("---")
        st.download_button("📄 Contrato Limpa Nome", data="Doc", file_name="LimpaNome.docx")
        st.download_button("🏦 Contrato BACEN", data="Doc", file_name="Bacen.docx")
        st.file_uploader("Enviar Contrato Assinado", type=['pdf'])
        if st.button("Enviar"): st.success("Salvo!")

    elif menu == "🩺 Solicitar Diagnóstico":
        st.header("🩺 Diagnóstico Profundo")
        st.selectbox("Foco?", ["1 - BACEN", "2 - Birôs", "3 - Rating", "4 - Tributário"])
        val_d = st.session_state['precos'][perfil_atual]['diag']
        st.markdown(f"<div class='checkout-box'><h3>Taxa: R$ {val_d:,.2f}</h3></div>", unsafe_allow_html=True)
        if st.button("Gerar PIX"): st.success("Vá para pagamento!")

    elif menu == "⚙️ Painel do Diretor":
        st.header("👑 Central de Comando")
        aba1, aba2 = st.tabs(["📝 Vincular Processos", "💲 Preços do Sistema"])
        with aba1:
            cpf_alvo = st.text_input("CPF do Cliente")
            num_acao = st.text_input("Nº Ação")
            if st.button("Vincular Processo"): 
                supabase.table("nomes_processamento").update({"numero_processo": num_acao}).eq("cpf_cnpj", cpf_alvo).execute()
                st.success("Vinculado com sucesso!")
        with aba2:
            st.write("Altere os valores cobrados no Checkout.")
            st.subheader("1. CLIENTE FINAL")
            cc1, cc2 = st.columns(2)
            n_cli_limpa = cc1.number_input("Limpa Nome (R$)", value=float(st.session_state['precos']['cliente']['limpa_nome']))
            n_cli_bacen = cc2.number_input("BACEN (R$)", value=float(st.session_state['precos']['cliente']['bacen']))
            st.subheader("2. PARCEIROS")
            cp1, cp2 = st.columns(2)
            n_par_limpa = cp1.number_input("Limpa Parc. (R$)", value=float(st.session_state['precos']['parceiro']['limpa_nome']))
            n_par_bacen = cp2.number_input("BACEN Parc. (R$)", value=float(st.session_state['precos']['parceiro']['bacen']))
            if st.button("Salvar Preços"):
                st.session_state['precos']['cliente']['limpa_nome'] = n_cli_limpa
                st.session_state['precos']['cliente']['bacen'] = n_cli_bacen
                st.session_state['precos']['parceiro']['limpa_nome'] = n_par_limpa
                st.session_state['precos']['parceiro']['bacen'] = n_par_bacen
                st.success("Preços atualizados!")
    else:
        st.header(menu)
        st.info("Em implantação.")

if not st.session_state['usuario_autenticado']: tela_login()
else: tela_principal()
