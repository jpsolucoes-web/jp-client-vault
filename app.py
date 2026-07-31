import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime
import os
import base64
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA MESTRA (Sempre a primeira linha)
# ==========================================
st.set_page_config(page_title="JP Client Vault - Reabilitação", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 2. CONEXÃO SUPABASE
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# ==========================================
# 3. LEITURA BLINDADA DE PARÂMETROS E INICIALIZAÇÃO
# ==========================================
# Proteção Anti-Queda: Evita erro se a URL carregar antes do servidor acordar
try:
    tipo_acesso = st.query_params.get("tipo")
    is_parceiro = (tipo_acesso == "parceiro")
except Exception:
    is_parceiro = False

perfil_atual = 'parceiro' if is_parceiro else 'cliente'

if 'precos' not in st.session_state:
    st.session_state['precos'] = {
        'cliente': {
            'limpa_nome': 250.00, 'bacen': 1200.00, 'rating': 500.00, 'tributario': 2000.00,
            'diag_limpa': 150.00, 'diag_bacen': 150.00, 'diag_rating': 150.00, 'diag_trib': 150.00,
            'reprotocolo': 212.50, 'prazo_garantia_dias': 30
        },
        'parceiro': {
            'limpa_nome': 150.00, 'bacen': 600.00, 'rating': 250.00, 'tributario': 1000.00,
            'diag_limpa': 50.00, 'diag_bacen': 50.00, 'diag_rating': 50.00, 'diag_trib': 50.00,
            'reprotocolo': 127.50, 'prazo_garantia_dias': 30
        }
    }

# Carregar preços salvos no banco de dados (Persistência)
if 'precos_carregados' not in st.session_state:
    try:
        res_p = supabase.table("configuracoes_sistema").select("*").eq("chave", "tabela_precos").execute()
        if res_p.data:
            st.session_state['precos'] = res_p.data[0]['valor_json']
            
            # Injeção retroativa de segurança para as novas variáveis
            if 'reprotocolo' not in st.session_state['precos']['cliente']:
                st.session_state['precos']['cliente']['reprotocolo'] = 212.50
                st.session_state['precos']['parceiro']['reprotocolo'] = 127.50
            if 'prazo_garantia_dias' not in st.session_state['precos']['cliente']:
                st.session_state['precos']['cliente']['prazo_garantia_dias'] = 30
                st.session_state['precos']['parceiro']['prazo_garantia_dias'] = 30
    except:
        pass
    st.session_state['precos_carregados'] = True

if 'usuarios_bloqueados' not in st.session_state:
    st.session_state['usuarios_bloqueados'] = []

if 'servico_pre_selecionado' not in st.session_state:
    st.session_state['servico_pre_selecionado'] = "1 - Ação Limpa Nome (Padrão)"

if 'data_relogio_js' not in st.session_state:
    st.session_state['data_relogio_js'] = "Aug 5, 2026 12:00:00"
    st.session_state['data_relogio_br'] = "05/08/2026"

# ==========================================
# 4. MATRIZ DE ESTILO PROFISSIONAL E WHATSAPP
# ==========================================
def injetar_css_profissional():
    st.markdown("""
        <style>
        /* Ajuste do Cabeçalho: Esconde o GitHub/Streamlit, mas MANTÉM o botão de menu visível no celular */
        #MainMenu {visibility: hidden;} 
        footer {visibility: hidden;} 
        header [data-testid="stToolbar"] {visibility: hidden; display: none;}
        
        .stApp { background-color: #0d1117; color: #e2e8f0; }
        
        /* Expandindo o container para matar o vácuo nas bordas globais */
        .block-container { padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; }
        
        /* Lateral Padrão e Segura */
        [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #1e293b; }
        [data-testid="stSidebar"] * { color: #f8fafc !important; }
        
        /* O GRANDE SEGREDO: Flexbox CSS para Forçar Simetria e Eliminar Vácuos */
        .simetria-perfeita { display: flex; width: 100%; gap: 20px; margin-bottom: 20px; }
        .simetria-box { flex: 1; height: 380px; border-radius: 12px; overflow: hidden; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); border: 1px solid #334155; background-color: #1e293b; }
        .simetria-box img { width: 100%; height: 100%; object-fit: cover; }
        .simetria-box video { width: 100%; height: 100%; object-fit: cover; }
        .espaco-livre { display: flex; align-items: center; justify-content: center; height: 100%; width: 100%; color: #94a3b8; font-weight: bold; border: 2px dashed #475569; border-radius: 12px; }
        
        /* Ajuste Galeria de Campanhas */
        [data-testid="stImage"] img { border-radius: 12px; }
        
        /* Textos e Caixas de Entrada */
        label, p, .stRadio label, .stSelectbox label, .stTextInput label, .stTextArea label, .stFileUploader label { color: #e2e8f0 !important; font-size: 15px !important; font-weight: 500 !important; }
        h1, h2, h3, h4 { color: #f59e0b !important; font-weight: 800 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        
        .stTextInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea, .stDateInput>div>div>input { background-color: #1e293b !important; color: #ffffff !important; border: 1px solid #475569 !important; border-radius: 8px !important; }
        .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus, .stDateInput>div>div>input:focus { border-color: #10b981 !important; box-shadow: 0 0 5px #10b981 !important; }
        ::placeholder { color: #94a3b8 !important; opacity: 1 !important; }
        
        /* Botões */
        .stButton>button { background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%); color: black !important; font-weight: bold !important; border: none !important; border-radius: 8px !important; padding: 10px 20px !important; transition: 0.3s; width: 100%; }
        .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 0px 15px rgba(245, 158, 11, 0.5); }
        hr { border-color: #334155; }
        
        /* Cards */
        .dashboard-card { background-color: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.2); height: 100%; }
        .checkout-box { background-color: #1e293b; border-left: 5px solid #10b981; padding: 20px; border-radius: 8px; margin-top: 20px; }
        .card-servico { background-color: #1e293b; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #334155; margin-bottom: 15px; }
        .metric-card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: left; }
        .metric-title { color: #94a3b8; font-size: 14px; margin-bottom: 5px; font-weight: 600; }
        .metric-value { color: #10b981; font-size: 28px; font-weight: bold; margin: 0; }
        
        /* Botão WhatsApp Flutuante Minimalista */
        .whatsapp-float { position: fixed; bottom: 30px; right: 30px; background-color: #25D366; color: #ffffff !important; border-radius: 50%; width: 65px; height: 65px; display: flex; align-items: center; justify-content: center; box-shadow: 2px 4px 15px rgba(0,0,0,0.5); z-index: 99999; transition: all 0.3s ease; }
        .whatsapp-float svg { width: 35px; height: 35px; }
        .whatsapp-float:hover { background-color: #128C7E; transform: scale(1.1); }
        
        /* Tabela e Badges */
        .pdf-preview { background-color: #ffffff; padding: 40px; border-radius: 10px; color: #000000; font-family: Arial, sans-serif; box-shadow: 0 0 10px rgba(255,255,255,0.1); margin-top: 20px;}
        .status-badge { display: inline-block; padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-right: 15px; width: 150px; text-align: center; color: white;}
        .status-row { display: flex; align-items: center; margin-bottom: 10px; padding: 10px; background-color: #1e293b; border-radius: 8px;}
        </style>
    """, unsafe_allow_html=True)

injetar_css_profissional()

# Ícone WhatsApp Flutuante Oficial
st.markdown("""
    <a href="https://wa.me/5549998077332" class="whatsapp-float" target="_blank" title="Suporte (49) 99807-7332">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
    </a>
""", unsafe_allow_html=True)

# ==========================================
# 5. CONTROLE DE SESSÃO E NAVEGAÇÃO
# ==========================================
if 'usuario_autenticado' not in st.session_state: st.session_state['usuario_autenticado'] = False
if 'dados_usuario' not in st.session_state: st.session_state['dados_usuario'] = None
if 'menu_navegacao' not in st.session_state: st.session_state['menu_navegacao'] = "🏠 Home"

def mudar_pagina(nova_pagina): 
    st.session_state['menu_navegacao'] = nova_pagina

def ir_para_protocolo_especifico(servico):
    st.session_state['servico_pre_selecionado'] = servico
    st.session_state['menu_navegacao'] = "🛡️ Enviar Protocolo"

# ==========================================
# 6. TELA DE LOGIN
# ==========================================
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
                        st.error("Erro ao criar conta.")

# ==========================================
# 7. TELA PRINCIPAL (O MOTOR DO SISTEMA)
# ==========================================
def tela_principal():
    email_logado = st.session_state['dados_usuario'].email
    is_diretor = (email_logado == "jp.solucoes.sc.diretor@gmail.com")
    
    if email_logado in st.session_state['usuarios_bloqueados'] and not is_diretor:
        st.error("🚫 SEU ACESSO FOI SUSPENSO PELO DIRETOR DA PLATAFORMA.")
        st.info("Entre em contato com o suporte via WhatsApp para regularizar.")
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
            st.session_state['dados_usuario'] = None
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
    # 🏠 HOME PAGE (SIMETRIA PERFEITA FLEXBOX E RELÓGIO CENTRAL)
    # -----------------------------------------
    if menu_selecionado == "🏠 Home":
        st.markdown("<h2 style='color: #f59e0b; margin-bottom: 0px;'>Bom dia, JP SOLUÇÕES PARTICIPAÇÕES LTDA! 👋</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 16px; margin-top: 5px; margin-bottom: 30px;'>Gerencie e acompanhe seus processos na nossa plataforma de reabilitação.</p>", unsafe_allow_html=True)

        def img_to_base64(filepath):
            if os.path.exists(filepath):
                with open(filepath, "rb") as f: return base64.b64encode(f.read()).decode()
            return ""

        # =========================================================================
        # LINHA 1: Imagens do Topo (Simetria Absoluta 50/50 sem vácuo)
        # =========================================================================
        img_t1 = img_to_base64("custom_topo_1.png") or img_to_base64("valortecpflimpo.png")
        img_t2 = img_to_base64("custom_topo_2.png") or img_to_base64("RECONSTRUIR.png")
        
        html_linha1 = f"""
        <div class="simetria-perfeita">
            <div class="simetria-box">
                {f'<img src="data:image/png;base64,{img_t1}">' if img_t1 else '<div class="espaco-livre">Topo Esquerda (Upload no Admin)</div>'}
            </div>
            <div class="simetria-box">
                {f'<img src="data:image/png;base64,{img_t2}">' if img_t2 else '<div class="espaco-livre">Topo Direita (Upload no Admin)</div>'}
            </div>
        </div>
        """
        st.markdown(html_linha1, unsafe_allow_html=True)

        # =========================================================================
        # LINHA 2: Imagem do Meio e Vídeo (Simetria Absoluta 50/50 sem vácuo)
        # =========================================================================
        st.markdown("""<style>
            div[data-testid="column"] > div { height: 100%; }
            div[data-testid="column"] img, div[data-testid="column"] video { width: 100% !important; height: 380px !important; object-fit: cover !important; border-radius: 12px !important; border: 1px solid #334155; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
        </style>""", unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if os.path.exists("custom_meio_1.png"): st.image("custom_meio_1.png", use_container_width=True)
            elif is_diretor: st.markdown("<div class='espaco-livre' style='height:380px;'>Vitrine Meio Esquerda (Upload no Admin)</div>", unsafe_allow_html=True)
            else: st.markdown("<div style='height:380px;'></div>", unsafe_allow_html=True)
            
        with col_m2:
            vid_path = "custom_video.mp4" if os.path.exists("custom_video.mp4") else "video1.mp4"
            if os.path.exists(vid_path): st.video(vid_path)
            elif is_diretor: st.markdown("<div class='espaco-livre' style='height:380px;'>Vídeo Meio Direita (Upload no Admin)</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================================================================
        # LINHA 3: O RELÓGIO CENTRAL (Banner Full Width)
        # =========================================================================
        d_js = st.session_state['data_relogio_js']
        d_br = st.session_state['data_relogio_br']
        
        clock_html = f"""
        <div style="background-color: #0f172a; border: 2px solid #f59e0b; border-radius: 12px; padding: 25px; text-align: center; font-family: 'Segoe UI', Tahoma, sans-serif; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.4); margin-bottom: 30px;">
            <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
                <div>
                    <h3 style="margin: 0; color: #f59e0b; font-size: clamp(18px, 2vw, 24px);">⏳ PRAZO OFICIAL</h3>
                    <p style="color: #94a3b8; font-size: 16px; margin: 5px 0 0 0;">Data Limite de Envio: {d_br}</p>
                </div>
                <div id="clock_div" style="color: #10b981; font-size: clamp(30px, 4vw, 55px); font-weight: 900; letter-spacing: 2px;">Calculando...</div>
            </div>
        </div>
        <script>
            var countDownDate = new Date("{d_js}").getTime();
            setInterval(function() {{
                var now = new Date().getTime();
                var distance = countDownDate - now;
                if(distance < 0) {{ document.getElementById("clock_div").innerHTML = "AÇÃO INICIADA!"; return; }}
                var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                hours = hours < 10 ? "0" + hours : hours; minutes = minutes < 10 ? "0" + minutes : minutes; seconds = seconds < 10 ? "0" + seconds : seconds;
                document.getElementById("clock_div").innerHTML = days + " D : " + hours + " h : " + minutes + " m : " + seconds + " s";
            }}, 1000);
        </script>
        """
        components.html(clock_html, height=150)

        # =========================================================================
        # LINHA 4: A GALERIA DE CAMPANHAS (Até 8 Imagens via Admin)
        # =========================================================================
        st.markdown("""<style>div[data-testid="column"] img { height: auto !important; max-height: 250px !important; }</style>""", unsafe_allow_html=True)
        
        imagens_ativas = [i for i in range(1, 9) if os.path.exists(f"custom_home_{i}.png")]
        
        if is_diretor or imagens_ativas:
            st.markdown("<h4 style='color:#f8fafc; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-top:20px;'>🌟 Campanhas e Informativos</h4>", unsafe_allow_html=True)
            
            if is_diretor:
                c1, c2, c3, c4 = st.columns(4, gap="small")
                cols1 = [c1, c2, c3, c4]
                for i in range(1, 5):
                    with cols1[i-1]:
                        if i in imagens_ativas: st.image(f"custom_home_{i}.png", use_container_width=True)
                        else: st.markdown(f"<div class='espaco-livre' style='height: 200px;'>Espaço {i} Livre</div>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                c5, c6, c7, c8 = st.columns(4, gap="small")
                cols2 = [c5, c6, c7, c8]
                for i in range(5, 9):
                    with cols2[i-5]:
                        if i in imagens_ativas: st.image(f"custom_home_{i}.png", use_container_width=True)
                        else: st.markdown(f"<div class='espaco-livre' style='height: 200px;'>Espaço {i} Livre</div>", unsafe_allow_html=True)
            else:
                for row_start in range(0, len(imagens_ativas), 4):
                    cols = st.columns(4, gap="small")
                    for col_offset in range(4):
                        if row_start + col_offset < len(imagens_ativas):
                            with cols[col_offset]:
                                st.image(f"custom_home_{imagens_ativas[row_start + col_offset]}.png", use_container_width=True)
        # =========================================================================

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Ações Rápidas (Acesso Fácil no Rodapé da Home)
        st.markdown("<h4 style='color:#f8fafc; margin-bottom:15px;'>⚡ Ações Rápidas</h4>", unsafe_allow_html=True)
        c_act1, c_act2, c_act3 = st.columns(3)
        with c_act1: st.button("📋 Gerenciar Minhas Listas", use_container_width=True, on_click=mudar_pagina, args=("📋 Minhas Listas",))
        with c_act2: st.button("💲 Painel Financeiro", use_container_width=True, on_click=mudar_pagina, args=("💲 Financeiro",))
        with c_act3: st.button("💬 Suporte Rápido", use_container_width=True)

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
        c4.selectbox("UF", ["SC", "PR", "RS", "SP", "RJ", "MG", "BA", "GO", "DF", "AM", "PE", "CE", "ES"])
        c5.text_input("Cidade")
        if st.button("💾 Salvar Alterações", use_container_width=True): st.success("Dados atualizados com sucesso!")

    # -----------------------------------------
    # 💼 SERVIÇOS AVANÇADOS
    # -----------------------------------------
    elif menu_selecionado == "💼 Serviços":
        st.header("💼 Nossos Serviços Avançados")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card-servico"><h3>🛡️ Limpa Nome</h3><p>Reabilitação de crédito Padrão.</p></div>', unsafe_allow_html=True)
            st.button("Acessar Limpa Nome", on_click=ir_para_protocolo_especifico, args=("1 - Ação Limpa Nome (Padrão)",), key="btn_limpa", use_container_width=True)
            st.markdown('<div class="card-servico"><h3>🏦 Rating Bancário</h3><p>Aumento de Score e Relacionamento.</p></div>', unsafe_allow_html=True)
            st.button("Acessar Rating", on_click=ir_para_protocolo_especifico, args=("3 - Rating Bancário",), key="btn_rating", use_container_width=True)
        with col2:
            st.markdown('<div class="card-servico"><h3>🏛️ BACEN</h3><p>Retirada de restrições no Banco Central.</p></div>', unsafe_allow_html=True)
            st.button("Acessar BACEN", on_click=ir_para_protocolo_especifico, args=("2 - BACEN",), key="btn_bacen", use_container_width=True)
            st.markdown('<div class="card-servico"><h3>⚖️ Defesa Tributária</h3><p>Estratégias fiscais e tributárias.</p></div>', unsafe_allow_html=True)
            st.button("Acessar Tributário", on_click=ir_para_protocolo_especifico, args=("4 - Defesa Tributária",), key="btn_trib", use_container_width=True)

    # -----------------------------------------
    # 🛡️ ENVIAR PROTOCOLO
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

        if is_parceiro:
            st.info("💡 **VISÃO DO PARCEIRO:** O valor principal exibido é o seu Custo. Entre parênteses está o Preço Sugerido para você cobrar do seu Cliente Final.")
            txt_limpa = f"🛡️ 1 - Ação Limpa Nome — Custo: R$ {p_limpa:,.2f} (Venda Sugerida: R$ {st.session_state['precos']['cliente']['limpa_nome']:,.2f})"
            txt_bacen = f"🏛️ 2 - BACEN — Custo: R$ {p_bacen:,.2f} (Venda Sugerida: R$ {st.session_state['precos']['cliente']['bacen']:,.2f})"
            txt_rating = f"📈 3 - Rating Bancário — Custo: R$ {p_rating:,.2f} (Venda Sugerida: R$ {st.session_state['precos']['cliente']['rating']:,.2f})"
            txt_trib = f"⚖️ 4 - Defesa Tributária — Custo: R$ {p_trib:,.2f} (Venda Sugerida: R$ {st.session_state['precos']['cliente']['tributario']:,.2f})"
        else:
            txt_limpa = f"🛡️ 1 - Ação Limpa Nome (Padrão) — R$ {p_limpa:,.2f}"
            txt_bacen = f"🏛️ 2 - BACEN — R$ {p_bacen:,.2f}"
            txt_rating = f"📈 3 - Rating Bancário — R$ {p_rating:,.2f}"
            txt_trib = f"⚖️ 4 - Defesa Tributária — R$ {p_trib:,.2f}"

        c_chk1, c_chk2 = st.columns(2)
        with c_chk1:
            marcar_limpa = (st.session_state['servico_pre_selecionado'] == "1 - Ação Limpa Nome (Padrão)")
            marcar_rating = (st.session_state['servico_pre_selecionado']
