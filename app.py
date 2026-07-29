import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime

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

# Verifica se é link de parceiro pela URL (?tipo=parceiro)
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
        
        /* Estilo dos Cards Financeiros */
        .metric-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: left; }
        .metric-title { color: #94a3b8; font-size: 14px; margin-bottom: 5px; font-weight: 600; }
        .metric-value { color: #10b981; font-size: 28px; font-weight: bold; margin: 0; }
        
        /* Relógio Digital Neon */
        .relogio-box { background-color: #0f172a; border: 2px solid #f59e0b; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 0 15px rgba(245, 158, 11, 0.2); }
        .clock-text { color: #10b981; font-size: 45px; font-weight: 900; font-family: 'Courier New', Courier, monospace; letter-spacing: 2px; }
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
                        st.success("✅ Conta criada com sucesso! Faça login ao lado.")
                    except Exception as e:
                        st.error(f"Erro ao criar conta: {e}")

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
            "🏠 Home", "💼 Serviços", "📅 Eventos",
            "🛡️ Enviar Protocolo", "🔄 Reprotocolo", "📖 Manual do Parceiro", 
            "📋 Minhas Listas", "💲 Financeiro", "⚠️ Reclame Aqui", 
            "📊 Orçamento", "📝 Modelos de Contratos para Baixar", "📄 Documentos de Apoio", 
            "🎓 Academia Limpa Nome", "🏢 CNPJ Inapto",
            "🩺 Solicitar Diagnóstico", "📑 Meus Diagnósticos"
        ]
        if is_diretor: opcoes_menu.append("⚙️ Painel do Diretor")
        
        st.radio("Navegação", opcoes_menu, key="menu_navegacao", label_visibility="collapsed")

    menu_selecionado = st.session_state['menu_navegacao']

    # -----------------------------------------
    # 🏠 HOME E RELÓGIO DIGITAL AO VIVO (JS)
    # -----------------------------------------
    if menu_selecionado == "🏠 Home":
        st.markdown("<h1 style='text-align: center;'>Portal de Reabilitação de Crédito</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8;'>Ambiente blindado para envio e análise dos processos.</p>", unsafe_allow_html=True)
        st.write("---")
        
        # INJEÇÃO JAVASCRIPT: Relógio Processando ao Vivo
        st.markdown("""
            <div class="relogio-box">
                <h3 style="margin: 0; color: #f59e0b;">⏳ TEMPO PARA A PRÓXIMA AÇÃO OFICIAL (05/08/2026)</h3>
                <div id="clock_div" class="clock-text">Processando tempo...</div>
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
                document.getElementById("clock_div").innerHTML = days + " Dias, " + hours + "h " + minutes + "m " + seconds + "s";
            }, 1000);
            </script>
            <br>
        """, unsafe_allow_html=True)
        
        col_img, col_vid = st.columns([1, 1])
        with col_img:
            try: st.image("valortecpflimpo.png", use_container_width=True)
            except: pass
        with col_vid:
            try: st.video("video1.mp4")
            except: st.info("O vídeo 'video1.mp4' não foi encontrado ou formato incompatível.")

    # -----------------------------------------
    # 💼 SERVIÇOS
    # -----------------------------------------
    elif menu_selecionado == "💼 Serviços":
        st.header("💼 Nossos Serviços Avançados")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card-servico"><h3>🛡️ Limpa Nome</h3><p>Reabilitação de crédito Padrão.</p>', unsafe_allow_html=True)
            if st.button("Acessar Limpa Nome", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",)): pass
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card-servico"><h3>🏦 Rating Bancário</h3><p>Aumento de Score e Relacionamento.</p>', unsafe_allow_html=True)
            if st.button("Acessar Rating", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",)): pass
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="card-servico"><h3>🏛️ BACEN</h3><p>Retirada de restrições no Banco Central.</p>', unsafe_allow_html=True)
            if st.button("Acessar BACEN", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",)): pass
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card-servico"><h3>⚖️ Defesa Tributária</h3><p>Estratégias fiscais e tributárias.</p>', unsafe_allow_html=True)
            if st.button("Acessar Tributário", on_click=mudar_pagina, args=("🛡️ Enviar Protocolo",)): pass
            st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------
    # 🛡️ ENVIAR PROTOCOLO & PIX OFICIAL
    # -----------------------------------------
    elif menu_selecionado == "🛡️ Enviar Protocolo":
        st.title("🚀 Central de Protocolos")
        
        tipo_servico = st.selectbox("1. Selecione a Natureza da Ação", ["1 - Ação Limpa Nome (Padrão)", "2 - BACEN", "3 - Rating Bancário", "4 - Defesa Tributária"])
        
        st.subheader("2. Identificação do Cliente")
        c1, c2 = st.columns(2)
        tipo_pessoa = c1.radio("Pessoa?", ["CPF", "CNPJ"])
        nome_cliente = c1.text_input("Nome / Razão Social")
        cpf_cnpj = c2.text_input("CPF ou CNPJ")
        telefone = c2.text_input("WhatsApp com DDD")

        # QUESTIONÁRIO
        if tipo_servico in ["2 - BACEN", "3 - Rating Bancário", "4 - Defesa Tributária"]:
            st.subheader("3. Questionário Analítico de Rating")
            cp1, cp2, cp3 = st.columns(3)
            rg = cp1.text_input("RG")
            from datetime import date
            data_nasc = cp2.date_input("Data Nascimento", min_value=date(1920, 1, 1))
            estado_civil = cp3.selectbox("Estado Civil", ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"])
            bancos = st.text_area("Bancos e Contas")
            
            cs1, cs2, cs3, cs4 = st.columns(4)
            gov_login = cs1.text_input("Login GOV.BR")
            gov_senha = cs2.text_input("Senha GOV.BR", type="password")
            serasa_login = cs3.text_input("Login Serasa")
            serasa_senha = cs4.text_input("Senha Serasa", type="password")

        # ANEXOS
        st.subheader("4. Anexos Oficiais")
        ca1, ca2 = st.columns(2)
        ca1.file_uploader("Upload RG/CNH/CPF", type=['png', 'jpg', 'pdf'])
        ca2.file_uploader("Comprovante de Endereço", type=['png', 'jpg', 'pdf'])
        
        if tipo_servico in ["2 - BACEN", "3 - Rating Bancário"]:
            cu1, cu2 = st.columns(2)
            cu1.file_uploader("Procuração Assinada (.pdf)", type=['pdf'])
            cu1.file_uploader("Declaração Hipo (.pdf)", type=['pdf'])
            cu2.file_uploader("Extrato SCR (.pdf)", type=['pdf'])
            cu2.file_uploader("Extratos Bancários (.pdf)", type=['pdf'])

        if tipo_servico == "4 - Defesa Tributária":
            ct1, ct2 = st.columns(2)
            ct1.file_uploader("Certificado A1 (.pfx / .p12)", type=['pfx', 'p12'])
            ct2.text_input("Senha Certificado", type="password")

        # CHECKOUT E PIX
        st.subheader("5. Processamento e Pagamento")
        
        # Puxa o preço dinâmico do Banco/Sessão
        if tipo_servico.startswith("1"): preco_num = st.session_state['precos'][perfil_atual]['limpa_nome']
        elif tipo_servico.startswith("2"): preco_num = st.session_state['precos'][perfil_atual]['bacen']
        elif tipo_servico.startswith("3"): preco_num = st.session_state['precos'][perfil_atual]['rating']
        else: preco_num = st.session_state['precos'][perfil_atual]['tributario']
        
        valor_formatado = f"R$ {preco_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        st.markdown(f"""
            <div class="checkout-box">
                <h3 style="margin-top:0;">Resumo Financeiro</h3>
                <p>Serviço: <b>{tipo_servico}</b></p>
                <p>Taxa de Protocolo: <b style="font-size: 24px; color: #10b981;">{valor_formatado}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 ENVIAR DADOS E PAGAR VIA PIX"):
            if not nome_cliente or not cpf_cnpj: st.error("⚠️ Nome e CPF/CNPJ são obrigatórios!")
            else:
                try:
                    supabase.table("nomes_processamento").insert({
                        "user_id": st.session_state['dados_usuario'].id, "email_cliente": email_logado,
                        "nome": nome_cliente, "cpf_cnpj": cpf_cnpj, "tipo_servico": tipo_servico, "numero_processo": "Aguardando"
                    }).execute()
                    st.success("✅ Protocolo salvo! Efetue o pagamento abaixo.")
                    
                    st.markdown("---")
                    st.markdown("<h2 style='text-align: center; color: #10b981;'>PAGAMENTO PIX OFICIAL</h2>", unsafe_allow_html=True)
                    
                    c_pix1, c_pix2 = st.columns([1, 2])
                    with c_pix1:
                        try: st.image("qr_pix.png", width=250)
                        except: st.info("Salve o seu QR code no Github com o nome qr_pix.png")
                    with c_pix2:
                        st.markdown("<p style='font-size: 18px;'><b>Chave PIX (E-mail):</b></p>", unsafe_allow_html=True)
                        st.code("jp.solucoes.sc.diretor@gmail.com", language="text")
                        
                        st.markdown("<p style='font-size: 18px; margin-top: 15px;'><b>Código Copia e Cola:</b></p>", unsafe_allow_html=True)
                        st.code("00020126540014br.gov.bcb.pix0132jp.solucoes.sc.diretor@gmail.com5204000053039865802BR5925JP SOLUCOES PARTICIPACOES6007CHAPECO62250521bBOkVhq3TKa8lHpaMavJi63044A0E", language="text")
                        
                        st.info("O protocolo só avança após a confirmação do pagamento.")
                except Exception as e:
                    st.error("Falha ao salvar no banco.")

    # -----------------------------------------
    # 🔄 REPROTOCOLO
    # -----------------------------------------
    elif menu_selecionado == "🔄 Reprotocolo":
        st.header("🔄 Área de Reprotocolo")
        c1, c2 = st.columns(2)
        c1.radio("Pessoa?", ["CPF", "CNPJ"])
        c1.text_input("Nome Completo")
        c2.text_input("CPF ou CNPJ")
        st.download_button("📥 Baixar Modelo", data="Doc", file_name="Reprotocolo.docx")
        st.file_uploader("Anexar Assinado", type=['pdf'])
        if st.button("🚀 Enviar"): st.success("Enviado!")

    # -----------------------------------------
    # 📋 MINHAS LISTAS
    # -----------------------------------------
    elif menu_selecionado == "📋 Minhas Listas":
        st.header("Minhas Listas")
        try:
            res = supabase.table("nomes_processamento").select("numero_processo, cpf_cnpj, tipo_servico, status_serasa, status_boa_vista").eq("email_cliente", email_logado).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df.columns = ["Nº Ação/Processo", "CPF/CNPJ", "Serviço", "Serasa", "Boa Vista"]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else: st.info("Nenhum processo.")
        except: st.error("Erro banco.")

    # -----------------------------------------
    # 💲 FINANCEIRO (CARDS ESTILIZADOS)
    # -----------------------------------------
    elif menu_selecionado == "💲 Financeiro":
        st.header("Financeiro")
        st.markdown("<p style='color: #94a3b8;'>Minhas listas enviadas e valores</p>", unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown("<div class='metric-card'><div class='metric-title'>Total Enviado 💲</div><div class='metric-value'>R$ 2.250,00</div></div>", unsafe_allow_html=True)
        c2.markdown("<div class='metric-card'><div class='metric-title'>Aprovados ✅</div><div class='metric-value'>R$ 2.250,00</div></div>", unsafe_allow_html=True)
        c3.markdown("<div class='metric-card'><div class='metric-title'>Pendentes ⏳</div><div class='metric-value' style='color:#f59e0b;'>R$ 0,00</div></div>", unsafe_allow_html=True)
        c4.markdown("<div class='metric-card'><div class='metric-title'>Nomes Processados 📈</div><div class='metric-value' style='color:#ffffff;'>0</div></div>", unsafe_allow_html=True)

    # -----------------------------------------
    # ⚠️ RECLAME AQUI JP SOLUÇÕES
    # -----------------------------------------
    elif menu_selecionado == "⚠️ Reclame Aqui":
        st.header("⚠️ Reclame Aqui")
        st.markdown("""
            **Ainda existe alguma restrição após a conclusão da sua ação?**
            O Reclame Aqui JP Soluções é um canal de atendimento prioritário para solicitar a correção de baixas que não tenham sido refletidas corretamente.
            *Importante: utilize este canal 72h após a ação constar como Concluída.*
        """)
        
        with st.form("form_reclame"):
            st.text_input("Motivo", value="Lista concluiu e o nome não baixou", disabled=True)
            st.selectbox("Selecione a Lista (Nº Processo)", ["Selecione...", "AÇÃO 11011", "AÇÃO 11012"])
            st.text_area("Observação (opcional)", placeholder="Descreva detalhes...")
            if st.form_submit_button("🚀 Enviar Solicitação"): st.success("Recebido pela equipe JP Soluções!")

    # -----------------------------------------
    # 📝 MODELOS DE CONTRATOS (COM UPLOADS DO DIRETOR)
    # -----------------------------------------
    elif menu_selecionado == "📝 Modelos de Contratos para Baixar":
        st.header("Central de Contratos")
        
        if is_diretor:
            st.warning("👑 **ÁREA DO DIRETOR: Alimente o sistema com os novos modelos.**")
            cd1, cd2 = st.columns(2)
            cd1.file_uploader("Substituir Contrato Limpa Nome", type=['docx', 'pdf'])
            cd2.file_uploader("Substituir Contrato BACEN", type=['docx', 'pdf'])
            cd1.file_uploader("Substituir Contrato Rating Bancário", type=['docx', 'pdf'])
            cd2.file_uploader("Substituir Contrato Defesa Tributária", type=['docx', 'pdf'])
            st.button("💾 Salvar Novos Modelos")
            st.markdown("---")
            
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📄 Contrato Limpa Nome", data="Doc", file_name="LimpaNome.docx")
            st.download_button("🏦 Contrato BACEN", data="Doc", file_name="Bacen.docx")
            st.download_button("📈 Contrato Rating", data="Doc", file_name="Rating.docx")
            st.download_button("⚖️ Contrato Tributário", data="Doc", file_name="Tributario.docx")
        with c2:
            st.file_uploader("Enviar Contrato Assinado", type=['pdf'])
            if st.button("Enviar ao Cofre"): st.success("Salvo!")

    # -----------------------------------------
    # 🩺 DIAGNÓSTICO
    # -----------------------------------------
    elif menu_selecionado == "🩺 Solicitar Diagnóstico":
        st.header("🩺 Diagnóstico Profundo")
        tipo_diag = st.selectbox("Foco?", ["1 - BACEN", "2 - Birôs", "3 - Rating", "4 - Tributário"])
        
        if tipo_diag.startswith("1"): val_d = st.session_state['precos'][perfil_atual]['diag']
        else: val_d = st.session_state['precos'][perfil_atual]['diag']
        
        st.markdown(f"<div class='checkout-box'><h3>Taxa: R$ {val_d:,.2f}</h3></div>", unsafe_allow_html=True)
        if st.button("Confirmar Pedido"): st.success("Ir para pagamento!")

    # -----------------------------------------
    # ⚙️ PAINEL DO DIRETOR (ADMIN GERAL E PREÇOS)
    # -----------------------------------------
    elif menu_selecionado == "⚙️ Painel do Diretor":
        st.header("👑 Central de Comando")
        
        aba_processos, aba_precos = st.tabs(["📝 Vincular Processos", "💲 Tabela de Preços do Sistema"])
        
        with aba_processos:
            st.info("Atualizar Número da Ação para o Cliente ver.")
            c1, c2 = st.columns(2)
            cpf_alvo = c1.text_input("CPF do Cliente")
            num_acao = c2.text_input("Nº Ação (Ex: AÇÃO 11011)")
            if st.button("Vincular Processo"): 
                supabase.table("nomes_processamento").update({"numero_processo": num_acao}).eq("cpf_cnpj", cpf_alvo).execute()
                st.success("Vinculado com sucesso!")
                
            try:
                res = supabase.table("nomes_processamento").select("*").execute()
                st.dataframe(res.data, use_container_width=True)
            except: pass
            
        with aba_precos:
            st.markdown("### Ajuste Geral de Precificação")
            st.write("Altere os valores cobrados no Checkout. As alterações são aplicadas instantaneamente.")
            
            st.subheader("1. Preços para CLIENTE FINAL")
            cc1, cc2, cc3, cc4 = st.columns(4)
            n_cli_limpa = cc1.number_input("Limpa Nome (R$)", value=float(st.session_state['precos']['cliente']['limpa_nome']))
            n_cli_bacen = cc2.number_input("BACEN (R$)", value=float(st.session_state['precos']['cliente']['bacen']))
            n_cli_rating = cc3.number_input("Rating (R$)", value=float(st.session_state['precos']['cliente']['rating']))
            n_cli_trib = cc4.number_input("Tributário (R$)", value=float(st.session_state['precos']['cliente']['tributario']))
            
            st.subheader("2. Preços de Custo para PARCEIROS")
            cp1, cp2, cp3, cp4 = st.columns(4)
            n_par_limpa = cp1.number_input("Limpa Nome Parc. (R$)", value=float(st.session_state['precos']['parceiro']['limpa_nome']))
            n_par_bacen = cp2.number_input("BACEN Parc. (R$)", value=float(st.session_state['precos']['parceiro']['bacen']))
            n_par_rating = cp3.number_input("Rating Parc. (R$)", value=float(st.session_state['precos']['parceiro']['rating']))
            n_par_trib = cp4.number_input("Tributário Parc. (R$)", value=float(st.session_state['precos']['parceiro']['tributario']))
            
            if st.button("💾 Salvar Novas Tabelas de Preços", use_container_width=True):
                st.session_state['precos']['cliente'] = {'limpa_nome': n_cli_limpa, 'bacen': n_cli_bacen, 'rating': n_cli_rating, 'tributario': n_cli_trib, 'diag': 150.0}
                st.session_state['precos']['parceiro'] = {'limpa_nome': n_par_limpa, 'bacen': n_par_bacen, 'rating': n_par_rating, 'tributario': n_par_trib, 'diag': 50.0}
                st.success("Tabelas atualizadas! O Checkout já está cobrando os novos valores.")

    else:
        st.header(menu_selecionado[2:])
        st.info("Esta seção está em fase de implantação.")

if not st.session_state['usuario_autenticado']: tela_login()
else: tela_principal()
