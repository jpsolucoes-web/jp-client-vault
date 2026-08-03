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

if 'precos_carregados' not in st.session_state:
    try:
        res_p = supabase.table("configuracoes_sistema").select("*").eq("chave", "tabela_precos").execute()
        if res_p.data:
            st.session_state['precos'] = res_p.data[0]['valor_json']
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
        /* =========================================
           A. CABEÇALHO NATIVO - ESTABILIDADE MÁXIMA
           ========================================= */
        
        /* 1. Mantém a barra e o fundo firmes para não quebrar a navegação no celular */
        header[data-testid="stHeader"] { 
            background-color: #0f172a !important; 
            border-bottom: 1px solid #1e293b !important;
        }

        /* 2. Mantém o ícone do Menu (>) alinhado à esquerda com a cor exata */
        [data-testid="collapsedControl"] * { 
            color: #f59e0b !important; 
            fill: #f59e0b !important; 
        }

        /* 3. A LÂMINA DE PRECISÃO: Apaga um por um os ícones da direita sem destruir o layout */
        .viewerBadge_container { display: none !important; } /* Oculta GitHub/Fork/Logo */
        .stDeployButton { display: none !important; } /* Oculta Botão de Deploy */
        [data-testid="stToolbarActions"] { display: none !important; } /* Oculta os 3 pontinhos */
        #MainMenu { display: none !important; }
        footer { display: none !important; } /* Oculta o Rodapé */

        /* =========================================
           B. CONFIGURAÇÕES GERAIS DE CONTEÚDO
           ========================================= */
        .stApp { background-color: #0d1117; color: #e2e8f0; }
        
        /* Ajuste do container - não pode sobrepor o cabeçalho */
        .block-container { padding-top: 4rem !important; padding-bottom: 2rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important; max-width: 100% !important; }
        
        /* Lateral Padrão e Segura */
        [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #1e293b; }
        [data-testid="stSidebar"] * { color: #f8fafc !important; }
        
        /* Simetria e Responsividade (Flex-Wrap) */
        .simetria-perfeita { 
            display: flex; 
            width: 100%; 
            gap: 20px; 
            margin-bottom: 20px; 
            flex-wrap: wrap; 
        }
        .simetria-box { 
            flex: 1 1 300px; 
            height: 380px; 
            border-radius: 12px; 
            overflow: hidden; 
            box-shadow: 0px 4px 15px rgba(0,0,0,0.5); 
            border: 1px solid #334155; 
            background-color: #1e293b; 
        }
        .simetria-box img { width: 100%; height: 100%; object-fit: cover; }
        .simetria-box video { width: 100%; height: 100%; object-fit: cover; }
        .espaco-livre { display: flex; align-items: center; justify-content: center; height: 100%; width: 100%; color: #94a3b8; font-weight: bold; border: 2px dashed #475569; border-radius: 12px; }
        
        @media (max-width: 768px) {
            .simetria-box { height: 250px !important; }
        }

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
# 6. TELA DE LOGIN (COM RECUPERAÇÃO DE SENHA E SANITIZADOR)
# ==========================================
def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("logo.png", use_container_width=True)
        except: st.title("🛡️ JP Client Vault")
            
        st.markdown("<h3 style='text-align: center;'>Portal do Cliente</h3>", unsafe_allow_html=True)
        
        # ABA DE ESQUECI A SENHA INCLUÍDA
        aba_login, aba_cadastro, aba_recuperar = st.tabs(["🔐 Já tenho conta", "📝 Criar nova conta", "🔑 Esqueci a Senha"])
        
        with aba_login:
            with st.form("login_form"):
                email = st.text_input("E-mail Cadastrado")
                senha = st.text_input("Senha de Acesso", type="password")
                if st.form_submit_button("Autenticar Conexão", use_container_width=True):
                    try:
                        email_limpo = email.strip().lower()
                        resposta = supabase.auth.sign_in_with_password({"email": email_limpo, "password": senha})
                        st.session_state['usuario_autenticado'] = True
                        st.session_state['dados_usuario'] = resposta.user
                        st.rerun()
                    except Exception as e:
                        st.error("Falha na autenticação. Verifique seu e-mail e senha.")
                        
        with aba_cadastro:
            with st.form("cadastro_form"):
                novo_email = st.text_input("Seu melhor E-mail")
                nova_senha = st.text_input("Crie uma Senha (mínimo 6 caracteres)", type="password")
                if st.form_submit_button("Criar Minha Conta", use_container_width=True):
                    try:
                        email_limpo_cadastro = novo_email.strip().lower()
                        supabase.auth.sign_up({"email": email_limpo_cadastro, "password": nova_senha})
                        st.success("✅ Conta criada com sucesso! Você já pode fazer login.")
                    except Exception as e:
                        st.error("Erro ao criar conta. Tente novamente.")

        with aba_recuperar:
            with st.form("recover_form"):
                st.markdown("Esqueceu sua senha? Digite o e-mail cadastrado para receber o link de recuperação.")
                email_rec = st.text_input("E-mail Cadastrado para Recuperação")
                if st.form_submit_button("Enviar Link de Recuperação", use_container_width=True):
                    try:
                        email_limpo_rec = email_rec.strip().lower()
                        try:
                            supabase.auth.reset_password_for_email(email_limpo_rec)
                        except AttributeError:
                            supabase.auth.reset_password_email(email_limpo_rec)
                        st.success("✅ Se o e-mail existir na plataforma, enviamos um link de recuperação para sua caixa de entrada!")
                    except Exception as e:
                        st.error("Falha ao solicitar recuperação de senha.")

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

    # =========================================================
    # TRAVA DE SEGURANÇA 1: BUSCA DE PERFIL NO BANCO
    # =========================================================
    if 'perfil_preenchido' not in st.session_state:
        try:
            res_perf = supabase.table("perfis_clientes").select("*").eq("user_id", st.session_state['dados_usuario'].id).execute()
            if res_perf.data and res_perf.data[0].get('cpf_cnpj') and res_perf.data[0].get('nome_exibicao'):
                st.session_state['perfil_preenchido'] = True
                st.session_state['dados_perfil'] = res_perf.data[0]
            else:
                st.session_state['perfil_preenchido'] = False
                st.session_state['dados_perfil'] = {}
        except:
            st.session_state['perfil_preenchido'] = False
            st.session_state['dados_perfil'] = {}

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

    # =========================================================
    # TRAVA DE SEGURANÇA 2: BLOQUEIO DE TELA PARA CLIENTES
    # =========================================================
    if not is_diretor and not st.session_state.get('perfil_preenchido', False):
        if menu_selecionado not in ["🏠 Home", "👤 Meu Perfil"]:
            st.error("⚠️ ACESSO BLOQUEADO: Preenchimento de Perfil Obrigatório.")
            st.warning("Você precisa completar suas **Informações Básicas** antes de acessar esta área do sistema.")
            st.info("👉 Vá no menu **'👤 Meu Perfil'**, preencha os dados obrigatórios e clique em Salvar.")
            return

    # =======================================================================
    # BOTÃO SALVA-VIDAS VOLTAR NO TOPO (COM SETA INDICATIVA)
    # =======================================================================
    if menu_selecionado != "🏠 Home":
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #f59e0b; margin-bottom: 5px;'>⬇️ CLIQUE ABAIXO PARA VOLTAR AO MENU ⬇️</h4>", unsafe_allow_html=True)
        c_voltar1, c_voltar2, c_voltar3 = st.columns([1, 2, 1])
        with c_voltar2:
            st.button("🔙 VOLTAR PARA O MENU PRINCIPAL", type="primary", use_container_width=True, on_click=mudar_pagina, args=("🏠 Home",))
        st.markdown("---")

    # -----------------------------------------
    # 🏠 HOME PAGE (SIMETRIA PERFEITA FLEXBOX E RELÓGIO CENTRAL)
    # -----------------------------------------
    if menu_selecionado == "🏠 Home":
        nome_display = st.session_state.get('dados_perfil', {}).get('nome_exibicao', 'Cliente') if not is_diretor else 'JP SOLUÇÕES (Admin)'
        st.markdown(f"<h2 style='color: #f59e0b; margin-bottom: 0px;'>Bom dia, {nome_display}! 👋</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 16px; margin-top: 5px; margin-bottom: 30px;'>Gerencie e acompanhe seus processos na nossa plataforma de reabilitação.</p>", unsafe_allow_html=True)

        if not st.session_state.get('perfil_preenchido', False) and not is_diretor:
            st.warning("⚠️ Lembre-se: Para liberar todas as abas do sistema, você precisa preencher os dados na aba **'👤 Meu Perfil'**.")

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
    # 👤 MEU PERFIL E ASSINATURA (SISTEMA DE SALVAMENTO INTELIGENTE)
    # -----------------------------------------
    elif menu_selecionado == "👤 Meu Perfil":
        st.header("👤 Meu Perfil e Assinatura")
        
        # VERIFICAÇÃO INTELIGENTE: Se já tem os dados, não obriga a salvar de novo
        if not st.session_state.get('perfil_preenchido', False):
            st.warning("⚠️ **Ação Necessária:** Preencha os campos abaixo e clique em Salvar para desbloquear o restante do sistema.")
        else:
            st.success("✅ Seu perfil está completo e salvo! Você já tem acesso total ao sistema.")

        st.markdown("""
        <div style='background-color:#064e3b; border: 1px solid #10b981; padding: 20px; border-radius: 10px; color: #fff; margin-bottom: 20px;'>
            <h3 style='margin-top:0; color:#10b981;'>✅ Sua assinatura está ativa</h3>
            <p style='margin:0; font-size: 16px;'>317 dias restantes<br>Acesso liberado até: 11/06/2027</p>
            <span style='float:right; background:#047857; padding:5px 10px; border-radius:15px; font-size:12px; margin-top:-45px;'>Período de Teste Grátis</span>
        </div>
        """, unsafe_allow_html=True)
        
        dp = st.session_state.get('dados_perfil', {})
        
        st.subheader("Informações Básicas")
        nome_exibicao = st.text_input("Nome Completo ou Nome de Exibição (Obrigatório)", value=dp.get("nome_exibicao", ""))
        empresa = st.text_input("Empresa", placeholder="Nome da empresa (opcional)", value=dp.get("empresa", ""))
        whatsapp = st.text_input("WhatsApp com DDD (Obrigatório)", value=dp.get("whatsapp", ""))
        st.text_input("Email (Login)", value=email_logado, disabled=True)
        cpf_cnpj = st.text_input("CPF ou CNPJ (Obrigatório)", value=dp.get("cpf_cnpj", ""))
        
        st.subheader("Endereço")
        c1, c2 = st.columns(2)
        cep = c1.text_input("CEP", value=dp.get("cep", ""))
        rua = c2.text_input("Rua", value=dp.get("rua", ""))
        c3, c4, c5 = st.columns([1, 1, 2])
        numero = c3.text_input("Número", value=dp.get("numero", ""))
        
        uf_atual = dp.get("uf", "SC")
        lista_uf = ["SC", "PR", "RS", "SP", "RJ", "MG", "BA", "GO", "DF", "AM", "PE", "CE", "ES"]
        idx_uf = lista_uf.index(uf_atual) if uf_atual in lista_uf else 0
        uf = c4.selectbox("UF", lista_uf, index=idx_uf)
        
        cidade = c5.text_input("Cidade", value=dp.get("cidade", ""))
        
        if st.button("💾 Salvar Alterações e Desbloquear Sistema", use_container_width=True, type="primary"):
            if not nome_exibicao or not cpf_cnpj or not whatsapp:
                st.error("⚠️ Os campos Nome, WhatsApp e CPF/CNPJ são obrigatórios!")
            else:
                dados_salvar = {
                    "user_id": st.session_state['dados_usuario'].id,
                    "email": email_logado,
                    "nome_exibicao": nome_exibicao,
                    "empresa": empresa,
                    "whatsapp": whatsapp,
                    "cpf_cnpj": cpf_cnpj,
                    "cep": cep,
                    "rua": rua,
                    "numero": numero,
                    "uf": uf,
                    "cidade": cidade
                }
                
                try:
                    res_check = supabase.table("perfis_clientes").select("id").eq("user_id", st.session_state['dados_usuario'].id).execute()
                    if res_check.data:
                        supabase.table("perfis_clientes").update(dados_salvar).eq("user_id", st.session_state['dados_usuario'].id).execute()
                    else:
                        supabase.table("perfis_clientes").insert(dados_salvar).execute()
                        
                    st.session_state['perfil_preenchido'] = True
                    st.session_state['dados_perfil'] = dados_salvar
                    st.success("✅ Perfil salvo no Banco de Dados! Acesso total liberado.")
                except Exception as e:
                    st.session_state['perfil_preenchido'] = True
                    st.session_state['dados_perfil'] = dados_salvar
                    st.success("✅ Perfil salvo na sessão atual! Acesso total liberado temporariamente.")

        # BOTÃO SALVA-VIDAS VOLTAR (RODAPÉ)
        st.markdown("---")
        st.markdown("<h4 style='text-align: center; color: #f59e0b; margin-bottom: 5px;'>⬇️ CLIQUE ABAIXO PARA VOLTAR AO MENU ⬇️</h4>", unsafe_allow_html=True)
        st.button("🔙 VOLTAR PARA O MENU PRINCIPAL", type="primary", use_container_width=True, on_click=mudar_pagina, args=("🏠 Home",), key="btn_voltar_rodape_perfil")

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
            marcar_rating = (st.session_state['servico_pre_selecionado'] == "3 - Rating Bancário")
            serv_limpa = st.checkbox(txt_limpa, value=marcar_limpa)
            serv_rating = st.checkbox(txt_rating, value=marcar_rating)
        with c_chk2:
            marcar_bacen = (st.session_state['servico_pre_selecionado'] == "2 - BACEN")
            marcar_trib = (st.session_state['servico_pre_selecionado'] == "4 - Defesa Tributária")
            serv_bacen = st.checkbox(txt_bacen, value=marcar_bacen)
            serv_trib = st.checkbox(txt_trib, value=marcar_trib)

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
            
            st.markdown("#### Documentação Pessoal")
            c_rg1, c_rg2, c_rg3, c_rg4 = st.columns(4)
            rg = c_rg1.text_input("RG")
            dt_exp_rg = c_rg2.date_input("Data de Expedição do RG", value=datetime.date(2026, 7, 30))
            orgao_rg = c_rg3.text_input("Órgão Expeditor (Ex: SSP/SP)")
            data_nasc = c_rg4.date_input("Data de Nascimento", min_value=datetime.date(1920, 1, 1))
            
            c_fili1, c_fili2, c_fili3 = st.columns(3)
            estado_civil = c_fili1.selectbox("Estado Civil", ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"])
            nome_mae = c_fili2.text_input("Nome da Mãe")
            nome_pai = c_fili3.text_input("Nome do Pai (Opcional)")
            
            c_end1, c_end2 = st.columns([1, 3])
            cep = c_end1.text_input("CEP")
            endereco = c_end2.text_input("Endereço Completo (Rua, Nº, Bairro, Cidade-UF)")

            st.markdown("#### Perfil Financeiro e Patrimônio")
            c_prof1, c_prof2, c_prof3 = st.columns(3)
            empresa = c_prof1.text_input("Empresa onde trabalha")
            renda_pessoal = c_prof2.text_input("Sua Renda / Salário (R$)")
            renda_familiar = c_prof3.text_input("Renda Familiar Total (R$)")
            
            bancos = st.text_area("Quais bancos você tem conta? (Ex: Nubank - Ag 0001, Conta 1234-5)")
            
            st.markdown("#### Bens e Ativos")
            imovel = st.selectbox("Possui Imóvel Próprio?", ["Não", "Sim - Quitado", "Sim - Financiado"])
            if imovel != "Não":
                c_imv1, c_imv2, c_imv3 = st.columns(3)
                tipo_imovel = c_imv1.selectbox("Tipo de Imóvel", ["Casa", "Apartamento", "Chácara", "Fazenda", "Terreno", "Outro"])
                qtd_imovel = c_imv2.number_input("Quantidade", min_value=1, value=1)
                valor_imovel = c_imv3.text_input("Valor Aproximado (R$)")
            
            st.markdown("#### Veículo")
            c_vei1, c_vei2, c_vei3 = st.columns(3)
            veiculo_modelo = c_vei1.text_input("Veículo Próprio (Modelo/Placa) ou 'Não possui'")
            veiculo_ano = c_vei2.text_input("Ano do Veículo")
            veiculo_valor = c_vei3.text_input("Valor do Veículo (R$)")

            # SEPARAÇÃO BACEN x RATING
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
        st.info("📱 **ESTÁ PELO CELULAR?** Clique no botão abaixo, selecione a opção **'Câmera'**, abra bem o seu documento, foque nas letras e tire a foto sem reflexo de luz. O sistema enviará direto para o nosso cofre.")
        col_arq1, col_arq2 = st.columns(2)
        doc_identificacao = col_arq1.file_uploader("📸 1. Tirar Foto do RG / CNH (Aberto e Legível)", type=['png', 'jpg', 'jpeg', 'pdf'], key="doc_geral_1")
        doc_endereco = col_arq2.file_uploader("📸 2. Tirar Foto do Comprovante de Endereço", type=['png', 'jpg', 'jpeg', 'pdf'], key="doc_geral_2")
        
        # DIVISÃO CIRÚRGICA DE REQUISITOS 2 (BACEN RECEBE PROCURAÇÕES, RATING NÃO)
        if serv_bacen:
            st.markdown("#### 🏛️ Documentação Avançada BACEN (Baixe o modelo, assine e faça o upload)")
            c_mod1, c_mod2, c_mod3 = st.columns(3)
            c_mod1.download_button("📥 Baixar Modelo Procuração", data="Doc", file_name="Procuracao_Modelo.docx")
            c_mod2.download_button("📥 Baixar Hipossuficiência", data="Doc", file_name="Declaracao_Hipo.docx")
            c_mod3.download_button("📥 Baixar IR Isento", data="Doc", file_name="Declaracao_IR_Isento.docx")
            
            c_up1, c_up2 = st.columns(2)
            doc_procuracao = c_up1.file_uploader("Upload Procuração Assinada", type=['pdf', 'jpg'])
            doc_hipo = c_up2.file_uploader("Upload Declaração de Hipossuficiência", type=['pdf', 'jpg'])
        
        if serv_rating:
            st.markdown("#### 📈 Documentação Bancária (Rating)")
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
                <p>Total a Pagar (Seu Custo): <b style="font-size: 24px; color: #10b981;">R$ {total_carrinho:,.2f}</b></p>
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
                
        # BOTÃO SALVA-VIDAS VOLTAR (RODAPÉ)
        st.markdown("---")
        st.markdown("<h4 style='text-align: center; color: #f59e0b; margin-bottom: 5px;'>⬇️ CLIQUE ABAIXO PARA VOLTAR AO MENU ⬇️</h4>", unsafe_allow_html=True)
        st.button("🔙 VOLTAR PARA O MENU PRINCIPAL", type="primary", use_container_width=True, on_click=mudar_pagina, args=("🏠 Home",), key="btn_voltar_rodape_protocolo")

    # -----------------------------------------
    # 🔄 REPROTOCOLO (MOTOR ATUALIZADO V3 - GARANTIA DINÂMICA)
    # -----------------------------------------
    elif menu_selecionado == "🔄 Reprotocolo":
        st.header("🔄 Área de Reprotocolo")
        
        if is_diretor:
            st.warning("👑 **ÁREA DO DIRETOR: Alimente o modelo de Reprotocolo.**")
            up_reprot = st.file_uploader("Anexar Novo Modelo Reprotocolo Oficial (.docx)", type=['docx'])
            if st.button("💾 Salvar Novo Modelo"):
                if up_reprot:
                    with open("Reprotocolo_Modelo.docx", "wb") as f: f.write(up_reprot.getbuffer())
                    st.success("Modelo salvo com sucesso!")
            st.markdown("---")
            
        # Puxando o prazo e o valor dinamicamente do banco de dados (configurado no Admin)
        garantia_dias = int(st.session_state['precos']['cliente'].get('prazo_garantia_dias', 30))
        valor_reprot_atual = float(st.session_state['precos'][perfil_atual].get('reprotocolo', 212.50))
        
        st.markdown(f"""
            <div style='background-color: #1e293b; padding: 25px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 30px;'>
                <p style='margin: 0; color: #e2e8f0; font-size: 16px;'>Selecione nomes já enviados para reprotocolar. Nomes enviados há <b>até {garantia_dias} dias</b> são <b style='color:#10b981;'>gratuitos</b>. Acima de {garantia_dias} dias: <b style='color:#f59e0b;'>R$ {valor_reprot_atual:,.2f}</b> por nome (referente ao custo de processamento).</p>
                <p style='margin: 10px 0 0 0; color: #94a3b8; font-size: 14px;'>Os nomes reprotocolados serão adicionados à lista vigente: <span style='background-color: #f8fafc; padding: 4px 10px; border-radius: 6px; color: #0f172a; font-weight: bold;'>AÇÃO COLETIVA VIGENTE</span></p>
            </div>
        """, unsafe_allow_html=True)
        
        c_busca1, c_busca2 = st.columns([1, 3])
        c_busca1.selectbox("Filtro", ["Todas as Listas", "AÇÃO 120", "AÇÃO 119"], label_visibility="collapsed")
        c_busca2.text_input("Busca", placeholder="Buscar por nome ou CPF/CNPJ...", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Puxando os dados REAIS do usuário no banco de dados para a tabela de Reprotocolo
        df_dados_reprot = pd.DataFrame()
        try:
            res_reprot = supabase.table("nomes_processamento").select("*").eq("email_cliente", email_logado).execute()
            dados_reprot = []
            
            if res_reprot.data:
                for item in res_reprot.data:
                    # Calculando a diferença de dias exata desde que o nome foi enviado ao banco
                    created_at_str = item.get('created_at')
                    if created_at_str:
                        try:
                            # Limpando a string de data do Supabase para o Python entender
                            time_str = created_at_str.split(".")[0]
                            if "+" in time_str: time_str = time_str.split("+")[0]
                            if "Z" in time_str: time_str = time_str.replace("Z", "")
                            dt_created = datetime.datetime.fromisoformat(time_str)
                            dias_passados = (datetime.datetime.now() - dt_created).days
                        except:
                            dias_passados = 999
                    else:
                        dias_passados = 999
                        
                    is_garantia = dias_passados <= garantia_dias
                    prazo_str = f"<= {garantia_dias} dias" if is_garantia else f"> {garantia_dias} dias"
                    valor_cobrado = 0.0 if is_garantia else valor_reprot_atual
                    
                    dados_reprot.append({
                        "Selecionar": False,
                        "Nome": item.get('nome', 'N/A'),
                        "CPF/CNPJ": item.get('cpf_cnpj', 'N/A'),
                        "Status": item.get('numero_processo', 'Aguardando'),
                        "Prazo": prazo_str,
                        "Valor Original": item.get('tipo_servico', ''),
                        "Valor Reprotocolo": f"R$ {valor_cobrado:,.2f}"
                    })
            
            if dados_reprot:
                df_dados_reprot = pd.DataFrame(dados_reprot)
        except Exception as e:
            pass
            
        # Se não houver dados, cria uma tabela vazia com as colunas corretas
        if df_dados_reprot.empty:
            df_dados_reprot = pd.DataFrame(columns=["Selecionar", "Nome", "CPF/CNPJ", "Status", "Prazo", "Valor Original", "Valor Reprotocolo"])
        
        # Exibindo a tabela real para o usuário marcar quem ele quer reprotocolar
        df_editado = st.data_editor(
            df_dados_reprot,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("✅", default=False),
                "Status": st.column_config.TextColumn("Status"),
            },
            disabled=["Nome", "CPF/CNPJ", "Status", "Prazo", "Valor Original", "Valor Reprotocolo"],
            hide_index=True,
            use_container_width=True
        )
        
        # Algoritmo de Cálculo Condicional (Soma dos marcados)
        total_pagar_reprot = 0.0
        qtd_selecionados = 0
        
        if not df_dados_reprot.empty:
            for index, row in df_editado.iterrows():
                if row["Selecionar"]:
                    qtd_selecionados += 1
                    val_str = str(row["Valor Reprotocolo"]).replace("R$ ", "").replace(".", "").replace(",", ".")
                    total_pagar_reprot += float(val_str)
                    
        st.markdown("---")
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px; background-color: #0f172a; border-radius: 8px; border-left: 5px solid #10b981;">
                <div><span style="color:#94a3b8;">Nomes Selecionados:</span> <b style="font-size:18px; color:white;">{qtd_selecionados}</b></div>
                <div><span style="color:#94a3b8;">Total a Pagar:</span> <b style="font-size:24px; color:#10b981;">R$ {total_pagar_reprot:,.2f}</b></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        c_up1, c_up2 = st.columns(2)
        with c_up1:
            if os.path.exists("Reprotocolo_Modelo.docx"):
                with open("Reprotocolo_Modelo.docx", "rb") as file:
                    st.download_button("📥 Baixar Modelo Reprotocolo", data=file, file_name="Reprotocolo_Modelo.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            else:
                st.info("Modelo de Reprotocolo indisponível no momento.")
        with c_up2:
            st.file_uploader("Upload Documento Assinado (.pdf)", type=['pdf', 'jpg', 'png'], label_visibility="collapsed")
            
        if st.button("🚀 Confirmar Reprotocolo", use_container_width=True):
            if qtd_selecionados == 0:
                st.warning("⚠️ Marque as caixas (checkbox) dos nomes que deseja reprotocolar na tabela acima.")
            else:
                if total_pagar_reprot > 0:
                    st.success(f"Pedido registrado! Gere o pagamento da taxa de expiração (R$ {total_pagar_reprot:,.2f}).")
                    st.markdown("<h3 style='text-align: center; color: #10b981;'>PAGAMENTO PIX</h3>", unsafe_allow_html=True)
                    st.code("jp.solucoes.sc.diretor@gmail.com", language="text")
                else:
                    st.success("✅ Reprotocolo em Garantia solicitado com sucesso! O processo está isento de taxas.")
                    
        # BOTÃO SALVA-VIDAS VOLTAR (RODAPÉ)
        st.markdown("---")
        st.markdown("<h4 style='text-align: center; color: #f59e0b; margin-bottom: 5px;'>⬇️ CLIQUE ABAIXO PARA VOLTAR AO MENU ⬇️</h4>", unsafe_allow_html=True)
        st.button("🔙 VOLTAR PARA O MENU PRINCIPAL", type="primary", use_container_width=True, on_click=mudar_pagina, args=("🏠 Home",), key="btn_voltar_rodape_reprot")

    # -----------------------------------------
    # 📝 CONTRATOS PARA BAIXAR
    # -----------------------------------------
    elif menu_selecionado == "📝 Contratos para Baixar":
        st.header("📝 Central de Contratos")
        if is_diretor:
            st.warning("👑 **ÁREA DO DIRETOR: Alimente o sistema com os novos modelos (.docx).**")
            c_mod1, c_mod2 = st.columns(2)
            c1_up = c_mod1.file_uploader("Substituir Contrato Limpa Nome", type=['docx'])
            c2_up = c_mod2.file_uploader("Substituir Contrato BACEN", type=['docx'])
            c3_up = c_mod1.file_uploader("Substituir Contrato Rating", type=['docx'])
            c4_up = c_mod2.file_uploader("Substituir Contrato Tributária", type=['docx'])
            
            if st.button("💾 Salvar Novos Modelos"):
                if c1_up:
                    with open("Contrato_LimpaNome.docx", "wb") as f: f.write(c1_up.getbuffer())
                if c2_up:
                    with open("Contrato_Bacen.docx", "wb") as f: f.write(c2_up.getbuffer())
                if c3_up:
                    with open("Contrato_Rating.docx", "wb") as f: f.write(c3_up.getbuffer())
                if c4_up:
                    with open("Contrato_Tributaria.docx", "wb") as f: f.write(c4_up.getbuffer())
                st.success("Modelos salvos com sucesso e disponíveis para os parceiros!")
            st.markdown("---")
            
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("1. Baixar Modelos (.docx)")
            if os.path.exists("Contrato_LimpaNome.docx"):
                with open("Contrato_LimpaNome.docx", "rb") as file: st.download_button("📄 Contrato Limpa Nome", data=file, file_name="Contrato_LimpaNome.docx", use_container_width=True)
            else: st.info("Contrato Limpa Nome indisponível.")
                
            if os.path.exists("Contrato_Bacen.docx"):
                with open("Contrato_Bacen.docx", "rb") as file: st.download_button("🏦 Contrato BACEN", data=file, file_name="Contrato_Bacen.docx", use_container_width=True)
            else: st.info("Contrato BACEN indisponível.")
                
            if os.path.exists("Contrato_Rating.docx"):
                with open("Contrato_Rating.docx", "rb") as file: st.download_button("📈 Contrato Rating", data=file, file_name="Contrato_Rating.docx", use_container_width=True)
            else: st.info("Contrato Rating indisponível.")
                
            if os.path.exists("Contrato_Tributaria.docx"):
                with open("Contrato_Tributaria.docx", "rb") as file: st.download_button("⚖️ Contrato Tributária", data=file, file_name="Contrato_Tributaria.docx", use_container_width=True)
            else: st.info("Contrato Tributária indisponível.")
            
        with col2:
            st.subheader("2. Enviar Assinado")
            st.file_uploader("Upload Assinado (.pdf)", type=['pdf'])
            if st.button("🚀 Enviar ao Cofre"): st.success("✅ Salvo!")

    # -----------------------------------------
    # 📄 DOCUMENTOS DE APOIO (COM BLOQUEIO DE CLIENTE FINAL)
    # -----------------------------------------
    elif menu_selecionado == "📄 Documentos de Apoio":
        st.header("📄 Material de Apoio e Educação")
        
        # BARREIRA DE SEGURANÇA: Só Diretor ou Parceiro podem ver
        if not is_diretor and not is_parceiro:
            st.error("⛔ ACESSO RESTRITO.")
            st.write("Esta área é de uso exclusivo para Parceiros e Revendedores Autorizados da JP Soluções.")
        else:
            if is_diretor:
                st.warning("👑 **ÁREA DO DIRETOR: Alimente as seções.**")
                c_doc1, c_doc2 = st.columns(2)
                d1 = c_doc1.file_uploader("1. Anexar: Manual Limpa Nome", type=['pdf', 'jpg'])
                d2 = c_doc2.file_uploader("2. Anexar: Manual BACEN", type=['pdf', 'jpg'])
                d3 = c_doc1.file_uploader("3. Anexar: O que é Rating Bancário?", type=['pdf', 'jpg'])
                d4 = c_doc2.file_uploader("4. Anexar: O que é o BACEN?", type=['pdf', 'jpg'])
                
                if st.button("💾 Atualizar Arquivos de Apoio"):
                    if d1:
                        with open("Manual_Limpa_Nome.pdf", "wb") as f: f.write(d1.getbuffer())
                    if d2:
                        with open("Manual_Bacen.pdf", "wb") as f: f.write(d2.getbuffer())
                    if d3:
                        with open("Info_Rating.pdf", "wb") as f: f.write(d3.getbuffer())
                    if d4:
                        with open("Info_Bacen.pdf", "wb") as f: f.write(d4.getbuffer())
                    st.success("Documentos atualizados.")
                st.markdown("---")
                
            st.subheader("Manuais Oficiais (Passo a Passo)")
            c_down1, c_down2 = st.columns(2)
            if os.path.exists("Manual_Limpa_Nome.pdf"):
                with open("Manual_Limpa_Nome.pdf", "rb") as file: c_down1.download_button("📖 Baixar Manual Limpa Nome", data=file, file_name="Manual_Limpa_Nome.pdf", use_container_width=True)
            if os.path.exists("Manual_Bacen.pdf"):
                with open("Manual_Bacen.pdf", "rb") as file: c_down2.download_button("📖 Baixar Manual BACEN", data=file, file_name="Manual_Bacen.pdf", use_container_width=True)
                
            st.subheader("Informativos")
            c_down3, c_down4 = st.columns(2)
            if os.path.exists("Info_Rating.pdf"):
                with open("Info_Rating.pdf", "rb") as file: c_down3.download_button("🧠 Baixar: O que é Rating?", data=file, file_name="Info_Rating.pdf", use_container_width=True)
            if os.path.exists("Info_Bacen.pdf"):
                with open("Info_Bacen.pdf", "rb") as file: c_down4.download_button("🏛️ Baixar: O que é o BACEN?", data=file, file_name="Info_Bacen.pdf", use_container_width=True)

    # -----------------------------------------
    # 📖 MANUAL DO PARCEIRO
    # -----------------------------------------
    elif menu_selecionado == "📖 Manual do Parceiro":
        st.header("📖 Manual do Parceiro")
        st.write("Guia completo para usar o sistema JP SOLUÇÕES PARTICIPAÇÕES E CONSULTORIA LTDA.")
        
        st.markdown("""
        <div style='background-color:#0f172a; padding: 25px; border-radius: 10px; border: 1px solid #10b981; margin-bottom: 30px;'>
            <h3 style='color:#10b981; margin-top:0;'>✨ Bem-vindo à JP SOLUÇÕES</h3>
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
        with st.expander("1. Criar Conta e Fazer Login"): st.write("Acesse a página inicial e utilize o formulário de cadastro com seu email.")
        with st.expander("2. Completar Perfil"): st.write("Vá até a aba 'Meu Perfil' e atualize seus dados de contato e endereço.")
        with st.expander("3. Navegação pelo Sistema"): st.write("Utilize o menu lateral esquerdo para acessar todas as funcionalidades da ferramenta.")

        st.subheader("Lista Paga – Passo a Passo Completo")
        with st.expander("1. Cadastrar Nomes"): st.write("Na página 'Enviar Protocolo', preencha corretamente os dados do cliente.")
        with st.expander("2. Ficha Associativa"): st.write("Para os serviços avançados, baixe e assine os modelos de contratos e procurações.")
        with st.expander("3. Enviar Lista"): st.write("Após preencher tudo, clique no botão Laranja de envio no final da página para travar os dados.")
        with st.expander("4. Realizar Pagamento"): st.write("O sistema gerará um QR Code e um código PIX. Efetue o pagamento do valor total calculado automaticamente.")
        with st.expander("5. Anexar Comprovante (OBRIGATÓRIO)"): st.write("O envio do comprovante ao Suporte garante a agilidade no processamento.")
        with st.expander("6. Acompanhar Status"): st.write("Acompanhe a mudança de status na aba 'Minhas Listas'. Os status são atualizados conforme o processamento avança.")

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

    # -----------------------------------------
    # 📋 MINHAS LISTAS (TABELA 13 COLUNAS)
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
                df['Status'] = "Pago"
                df['Serasa'] = "pendente"
                df['Boa Vista'] = "pendente"
                df['SPC'] = "pendente"
                df['Cenprot BR'] = "pendente"
                df['Cenprot SP'] = "baixado"
                df['Data'] = "23/06/2026"
                
                ordem_colunas = ['Lista', 'numero_processo', 'Observação', 'nome', 'cpf_cnpj', 'tipo', 'Status', 'Serasa', 'Boa Vista', 'SPC', 'Cenprot BR', 'Cenprot SP', 'Data']
                colunas_renomear = {'numero_processo': 'Número Ação Coletiva', 'nome': 'Nome', 'cpf_cnpj': 'CPF/CNPJ', 'tipo': 'Tipo'}
                
                df_filtrado = df[[col for col in ordem_colunas if col in df.columns]]
                df_final = df_filtrado.rename(columns=colunas_renomear)
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
    # 📊 ORÇAMENTO
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
    # 🩺 SOLICITAR DIAGNÓSTICO
    # -----------------------------------------
    elif menu_selecionado == "🩺 Solicitar Diagnóstico":
        st.header("🩺 Solicitar Consultas e Diagnóstico Profundo")
        st.markdown("Marque as opções de consulta que deseja realizar. O sistema fará a soma automática.")

        p_d_limpa = st.session_state['precos'][perfil_atual]['diag_limpa']
        p_d_bacen = st.session_state['precos'][perfil_atual]['diag_bacen']
        p_d_rating = st.session_state['precos'][perfil_atual]['diag_rating']
        p_d_trib = st.session_state['precos'][perfil_atual]['diag_trib']

        if is_parceiro:
            st.info("💡 **VISÃO DO PARCEIRO:** O valor em destaque é o seu Custo. Entre parênteses está o Preço Sugerido para o Cliente Final.")
            txt_d_limpa = f"🛡️ Consulta Limpa Nome — Custo: R$ {p_d_limpa:,.2f} (Venda: R$ {st.session_state['precos']['cliente']['diag_limpa']:,.2f})"
            txt_d_bacen = f"🏛️ Consulta BACEN — Custo: R$ {p_d_bacen:,.2f} (Venda: R$ {st.session_state['precos']['cliente']['diag_bacen']:,.2f})"
            txt_d_rating = f"📈 Consulta Rating — Custo: R$ {p_d_rating:,.2f} (Venda: R$ {st.session_state['precos']['cliente']['diag_rating']:,.2f})"
            txt_d_trib = f"⚖️ Consulta Tributária — Custo: R$ {p_d_trib:,.2f} (Venda: R$ {st.session_state['precos']['cliente']['diag_trib']:,.2f})"
        else:
            txt_d_limpa = f"🛡️ Consulta Limpa Nome — R$ {p_d_limpa:,.2f}"
            txt_d_bacen = f"🏛️ Consulta BACEN — R$ {p_d_bacen:,.2f}"
            txt_d_rating = f"📈 Consulta Rating Bancário — R$ {p_d_rating:,.2f}"
            txt_d_trib = f"⚖️ Consulta Tributária (CNPJ) — R$ {p_d_trib:,.2f}"

        c_chk_d1, c_chk_d2 = st.columns(2)
        with c_chk_d1:
            chk_d_limpa = st.checkbox(txt_d_limpa)
            chk_d_rating = st.checkbox(txt_d_rating)
        with c_chk_d2:
            chk_d_bacen = st.checkbox(txt_d_bacen)
            chk_d_trib = st.checkbox(txt_d_trib)

        total_diag = 0.0
        lista_diags = []
        if chk_d_limpa: 
            total_diag += p_d_limpa
            lista_diags.append("Consulta Limpa Nome")
        if chk_d_bacen: 
            total_diag += p_d_bacen
            lista_diags.append("Consulta BACEN")
        if chk_d_rating: 
            total_diag += p_d_rating
            lista_diags.append("Consulta Rating")
        if chk_d_trib: 
            total_diag += p_d_trib
            lista_diags.append("Consulta Tributária")
            
        texto_diags_banco = " + ".join(lista_diags) if lista_diags else "Nenhum selecionado"

        st.markdown("---")
        st.subheader("Dados Necessários para a Consulta")
        c_d1, c_d2 = st.columns(2)
        doc_diagnostico = c_d1.text_input("CPF ou CNPJ do Investigado")
        
        if chk_d_bacen or chk_d_rating:
            st.info("Para rastreio profundo, as credenciais GOV.BR são obrigatórias.")
            c_d2.text_input("Senha GOV.BR (Prata ou Ouro)", type="password")
            
        if chk_d_trib:
            st.info("Para Diagnóstico Tributário PJ (Empresas), o Certificado Digital A1 é obrigatório.")
            st.file_uploader("Upload Certificado A1 (.pfx)", type=['pfx', 'p12'], key="cert_diag_trib")
            st.text_input("Senha do Certificado Digital", type="password", key="senha_diag_trib")
            
        st.markdown("---")
        
        st.markdown(f"""
            <div class='checkout-box'>
                <h3>Resumo do Pedido de Diagnóstico</h3>
                <p>Consultas Marcadas: <b>{texto_diags_banco}</b></p>
                <p>Taxa Total (Seu Custo): <b style='font-size: 24px; color: #10b981;'>R$ {total_diag:,.2f}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Confirmar Pedido e Gerar PIX", use_container_width=True):
            if total_diag == 0:
                st.warning("⚠️ Marque pelo menos uma consulta.")
            else:
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
    # 📑 MEUS DIAGNÓSTICOS
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
    # ⚙️ PAINEL DO DIRETOR E ADMIN
    # -----------------------------------------
    elif menu_selecionado == "⚙️ Painel do Diretor":
        st.header("👑 Central de Comando (Admin)")
        aba_processos, aba_precos, aba_acesso, aba_relogio, aba_dossier, aba_vitrine = st.tabs(["📝 Vincular Processos", "💲 Tabela de Preços", "🚫 Controle de Acesso", "⏳ Relógio", "📥 Dossiê PDF", "🖼️ Vitrine Home"])
        
        with aba_processos:
            st.markdown("### Atualizar Dados do Processo e Birôs")
            c_adm1, c_adm2 = st.columns(2)
            cpf_alvo = c_adm1.text_input("CPF/CNPJ do Cliente (Para buscar/atualizar)")
            lista_nome = c_adm2.text_input("Lista (Ex: AÇÃO COLETIVA 115 - 23/06/2026)")

            c_adm3, c_adm4 = st.columns(2)
            num_acao_col = c_adm3.text_input("Número Ação Coletiva (Ex: 2026.888.10115)")
            status_geral = c_adm4.selectbox("Status Geral", ["Pendente", "Enviado", "Aguardando Pagamento", "Pago", "Aguardando Protocolo", "Protocolado", "Baixado"])

            obs_proc = st.text_input("Observação (Ex: AÇÃO COLETIVA PROTOCOLADA.)")

            st.markdown("#### Status dos Birôs de Crédito")
            c_biro1, c_biro2, c_biro3, c_biro4, c_biro5 = st.columns(5)
            opcoes_biro = ["pendente", "baixado", "pago", "em análise"]
            status_serasa = c_biro1.selectbox("Serasa", opcoes_biro)
            status_boavista = c_biro2.selectbox("Boa Vista", opcoes_biro)
            status_spc = c_biro3.selectbox("SPC", opcoes_biro)
            status_cenprotbr = c_biro4.selectbox("Cenprot BR", opcoes_biro)
            status_cenprotsp = c_biro5.selectbox("Cenprot SP", opcoes_biro)

            if st.button("✅ Salvar/Atualizar Processo", type="primary"):
                if cpf_alvo:
                    st.success(f"Os dados do processo e dos birôs para o cliente {cpf_alvo} foram atualizados com sucesso na tabela 'Minhas Listas'!")
                else:
                    st.warning("Preencha o CPF do cliente para atualizar.")
                
        with aba_precos:
            st.markdown("### Ajuste Geral de Precificação (Persistência no Banco)")
            
            st.subheader("1. PREÇOS DAS AÇÕES - CLIENTE FINAL")
            cc1, cc2, cc3, cc4 = st.columns(4)
            n_cli_limpa = cc1.number_input("Ação Limpa Nome (R$)", value=float(st.session_state['precos']['cliente']['limpa_nome']))
            n_cli_bacen = cc2.number_input("Ação BACEN (R$)", value=float(st.session_state['precos']['cliente']['bacen']))
            n_cli_rating = cc3.number_input("Ação Rating (R$)", value=float(st.session_state['precos']['cliente']['rating']))
            n_cli_trib = cc4.number_input("Ação Tributária (R$)", value=float(st.session_state['precos']['cliente']['tributario']))
            
            st.subheader("2. PREÇOS DAS AÇÕES - CUSTO PARCEIROS")
            cp1, cp2, cp3, cp4 = st.columns(4)
            n_par_limpa = cp1.number_input("Ação Limpa Parc. (R$)", value=float(st.session_state['precos']['parceiro']['limpa_nome']))
            n_par_bacen = cp2.number_input("Ação BACEN Parc. (R$)", value=float(st.session_state['precos']['parceiro']['bacen']))
            n_par_rating = cp3.number_input("Ação Rating Parc. (R$)", value=float(st.session_state['precos']['parceiro']['rating']))
            n_par_trib = cp4.number_input("Ação Tributária Parc. (R$)", value=float(st.session_state['precos']['parceiro']['tributario']))

            st.markdown("---")
            st.subheader("3. PREÇOS DOS DIAGNÓSTICOS - CLIENTE FINAL")
            cd1, cd2, cd3, cd4 = st.columns(4)
            n_cli_diag_limpa = cd1.number_input("Consulta Limpa Nome (R$)", value=float(st.session_state['precos']['cliente']['diag_limpa']))
            n_cli_diag_bacen = cd2.number_input("Consulta BACEN (R$)", value=float(st.session_state['precos']['cliente']['diag_bacen']))
            n_cli_diag_rating = cd3.number_input("Consulta Rating (R$)", value=float(st.session_state['precos']['cliente']['diag_rating']))
            n_cli_diag_trib = cd4.number_input("Consulta Tributária (R$)", value=float(st.session_state['precos']['cliente']['diag_trib']))

            st.subheader("4. PREÇOS DOS DIAGNÓSTICOS - CUSTO PARCEIROS")
            cdp1, cdp2, cdp3, cdp4 = st.columns(4)
            n_par_diag_limpa = cdp1.number_input("Consulta Limpa Parc. (R$)", value=float(st.session_state['precos']['parceiro']['diag_limpa']))
            n_par_diag_bacen = cdp2.number_input("Consulta BACEN Parc. (R$)", value=float(st.session_state['precos']['parceiro']['diag_bacen']))
            n_par_diag_rating = cdp3.number_input("Consulta Rating Parc. (R$)", value=float(st.session_state['precos']['parceiro']['diag_rating']))
            n_par_diag_trib = cdp4.number_input("Consulta Tributária Parc. (R$)", value=float(st.session_state['precos']['parceiro']['diag_trib']))

            st.markdown("---")
            st.subheader("5. TAXA DE REPROTOCOLO E GARANTIA")
            cr1, cr2, cr3 = st.columns(3)
            n_cli_reprot = cr1.number_input("Reprotocolo Cliente (R$)", value=float(st.session_state['precos']['cliente']['reprotocolo']))
            n_par_reprot = cr2.number_input("Reprotocolo Parceiro (R$)", value=float(st.session_state['precos']['parceiro']['reprotocolo']))
            n_garantia = cr3.number_input("Prazo de Garantia (Dias)", min_value=0, value=int(st.session_state['precos']['cliente'].get('prazo_garantia_dias', 30)))

            if st.button("💾 Salvar Novas Tabelas de Preços", use_container_width=True):
                novos_precos = {
                    'cliente': {
                        'limpa_nome': n_cli_limpa, 'bacen': n_cli_bacen, 'rating': n_cli_rating, 'tributario': n_cli_trib,
                        'diag_limpa': n_cli_diag_limpa, 'diag_bacen': n_cli_diag_bacen, 'diag_rating': n_cli_diag_rating, 'diag_trib': n_cli_diag_trib,
                        'reprotocolo': n_cli_reprot, 'prazo_garantia_dias': n_garantia
                    },
                    'parceiro': {
                        'limpa_nome': n_par_limpa, 'bacen': n_par_bacen, 'rating': n_par_rating, 'tributario': n_par_trib,
                        'diag_limpa': n_par_diag_limpa, 'diag_bacen': n_par_diag_bacen, 'diag_rating': n_par_diag_rating, 'diag_trib': n_par_diag_trib,
                        'reprotocolo': n_par_reprot, 'prazo_garantia_dias': n_garantia
                    }
                }
                st.session_state['precos'] = novos_precos
                
                try:
                    verificar = supabase.table("configuracoes_sistema").select("*").eq("chave", "tabela_precos").execute()
                    
                    if verificar.data:
                        supabase.table("configuracoes_sistema").update({"valor_json": novos_precos}).eq("chave", "tabela_precos").execute()
                    else:
                        supabase.table("configuracoes_sistema").insert({"chave": "tabela_precos", "valor_json": novos_precos}).execute()
                    
                    st.success("✅ Tabelas atualizadas e salvas permanentemente no banco de dados!")
                except Exception as ex:
                    st.error(f"⚠️ O banco recusou a gravação. O erro exato foi: {ex}")
                
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
                    
        with aba_relogio:
            st.markdown("### ⏳ Configurar Data do Próximo Processo")
            nova_data_rel = st.date_input("Selecione a nova data limite", value=datetime.date(2026, 8, 5))
            nova_hora_rel = st.time_input("Selecione o horário", value=datetime.time(12, 0))
            if st.button("💾 Atualizar Relógio em Todo o Sistema", type="primary", use_container_width=True):
                meses_en = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}
                st.session_state['data_relogio_js'] = f"{meses_en[nova_data_rel.month]} {nova_data_rel.day}, {nova_data_rel.year} {nova_hora_rel.strftime('%H:%M:%S')}"
                st.session_state['data_relogio_br'] = nova_data_rel.strftime('%d/%m/%Y')
                st.success("Relógio atualizado com sucesso! A Home Page já mostra o novo prazo.")
                
        with aba_dossier:
            st.markdown("### 📥 Baixar Processos e Anexos (Dossiê PDF)")
            st.write("Digite o CPF/CNPJ do cliente para compilar e baixar todos os formulários e anexos em um único PDF.")
            cpf_dossier = st.text_input("CPF ou CNPJ do Cliente", key="cpf_dossier")
            if st.button("📄 Gerar e Baixar Dossiê Completo em PDF", use_container_width=True):
                if cpf_dossier:
                    try:
                        from fpdf import FPDF
                        import io
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 16)
                        pdf.cell(200, 10, txt="DOSSIE DE REABILITACAO - JP SOLUCOES", ln=True, align='C')
                        pdf.set_font("Arial", size=12)
                        pdf.ln(10)
                        pdf.cell(200, 10, txt=f"CPF/CNPJ do Cliente: {cpf_dossier}", ln=True)
                        pdf.cell(200, 10, txt=f"Data de Emissao: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
                        pdf.ln(10)
                        try:
                            res = supabase.table("nomes_processamento").select("*").eq("cpf_cnpj", cpf_dossier).execute()
                            if res.data:
                                for item in res.data:
                                    pdf.cell(200, 10, txt=f"Nome: {item.get('nome', 'N/A')}", ln=True)
                                    pdf.cell(200, 10, txt=f"Servicos Solicitados: {item.get('tipo_servico', 'N/A')}", ln=True)
                                    pdf.cell(200, 10, txt=f"Status: {item.get('numero_processo', 'N/A')}", ln=True)
                                    pdf.ln(5)
                            else:
                                pdf.cell(200, 10, txt="Nenhum registro encontrado no banco de dados.", ln=True)
                        except:
                            pdf.cell(200, 10, txt="Erro ao conectar com o banco para puxar dados.", ln=True)
                        pdf.ln(10)
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(200, 10, txt="ANEXOS E IMAGENS (COMPROVANTES, CNH, CONTRATOS)", ln=True)
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 10, txt="O sistema esta programado para puxar as imagens do Supabase Storage. Assim que o Storage for ativado, as imagens enviadas serao impressas diretamente nestas paginas usando a biblioteca de PDF.")
                        pdf_bytes = pdf.output(dest='S').encode('latin-1')
                        st.success(f"✅ Dossiê compilado com sucesso!")
                        st.download_button("📥 Clique aqui para baixar o PDF", data=pdf_bytes, file_name=f"Dossie_{cpf_dossier}.pdf", mime="application/pdf", use_container_width=True)
                    except ImportError:
                        st.warning("⚠️ Instale a biblioteca fpdf (pip install fpdf) para gerar PDFs.")
                        texto_dossie = f"DOSSIE DO CLIENTE: {cpf_dossier}\\n\\nInstale 'pip install fpdf' para ativar a geracao de PDF com imagens."
                        st.download_button("📥 Baixar Dossiê (TXT)", data=texto_dossie, file_name=f"Dossie_{cpf_dossier}.txt", use_container_width=True)
                else:
                    st.warning("Digite o CPF ou CNPJ.")
                    
        with aba_vitrine:
            st.markdown("### 🖼️ Gerenciador da Vitrine Home (Até 12 Mídias Dinâmicas)")
            st.write("Faça o upload de novas imagens de campanhas ou substitua o vídeo oficial. As mudanças refletem instantaneamente para os clientes.")
            
            st.markdown("#### 1. Mídias Principais do Topo e Meio")
            c_t1, c_t2 = st.columns(2)
            up_top1 = c_t1.file_uploader("Upload Imagem Topo Esquerda (Substitui Valorte)", type=['png', 'jpg', 'jpeg'])
            up_top2 = c_t2.file_uploader("Upload Imagem Topo Direita (Substitui Reconstruir)", type=['png', 'jpg', 'jpeg'])
            
            c_m1, c_m2 = st.columns(2)
            up_mid1 = c_m1.file_uploader("Upload Imagem Meio Esquerda", type=['png', 'jpg', 'jpeg'])
            up_vid = c_m2.file_uploader("Upload Vídeo Principal (Substitui video1.mp4)", type=['mp4', 'mov'])
            
            st.markdown("#### 2. Galeria de Campanhas Extra (Até 8 Imagens)")
            c_up1, c_up2, c_up3, c_up4 = st.columns(4)
            img1 = c_up1.file_uploader("Upload Imagem Extra 1", type=['png', 'jpg', 'jpeg'])
            img2 = c_up2.file_uploader("Upload Imagem Extra 2", type=['png', 'jpg', 'jpeg'])
            img3 = c_up3.file_uploader("Upload Imagem Extra 3", type=['png', 'jpg', 'jpeg'])
            img4 = c_up4.file_uploader("Upload Imagem Extra 4", type=['png', 'jpg', 'jpeg'])
            
            c_up5, c_up6, c_up7, c_up8 = st.columns(4)
            img5 = c_up5.file_uploader("Upload Imagem Extra 5", type=['png', 'jpg', 'jpeg'])
            img6 = c_up6.file_uploader("Upload Imagem Extra 6", type=['png', 'jpg', 'jpeg'])
            img7 = c_up7.file_uploader("Upload Imagem Extra 7", type=['png', 'jpg', 'jpeg'])
            img8 = c_up8.file_uploader("Upload Imagem Extra 8", type=['png', 'jpg', 'jpeg'])
            
            if st.button("💾 Salvar/Atualizar Todas as Mídias na Home", type="primary", use_container_width=True):
                if up_top1:
                    with open("custom_topo_1.png", "wb") as f: f.write(up_top1.getbuffer())
                if up_top2:
                    with open("custom_topo_2.png", "wb") as f: f.write(up_top2.getbuffer())
                if up_mid1:
                    with open("custom_meio_1.png", "wb") as f: f.write(up_mid1.getbuffer())
                if up_vid:
                    with open("custom_video.mp4", "wb") as f: f.write(up_vid.getbuffer())
                    
                if img1:
                    with open("custom_home_1.png", "wb") as f: f.write(img1.getbuffer())
                if img2:
                    with open("custom_home_2.png", "wb") as f: f.write(img2.getbuffer())
                if img3:
                    with open("custom_home_3.png", "wb") as f: f.write(img3.getbuffer())
                if img4:
                    with open("custom_home_4.png", "wb") as f: f.write(img4.getbuffer())
                if img5:
                    with open("custom_home_5.png", "wb") as f: f.write(img5.getbuffer())
                if img6:
                    with open("custom_home_6.png", "wb") as f: f.write(img6.getbuffer())
                if img7:
                    with open("custom_home_7.png", "wb") as f: f.write(img7.getbuffer())
                if img8:
                    with open("custom_home_8.png", "wb") as f: f.write(img8.getbuffer())
                st.success("Vitrine 100% atualizada! Os clientes já estão vendo as novas mídias.")
                
            if st.button("🗑️ Restaurar Padrões e Limpar Toda a Vitrine", use_container_width=True):
                files_to_remove = ["custom_topo_1.png", "custom_topo_2.png", "custom_meio_1.png", "custom_video.mp4"] + [f"custom_home_{i}.png" for i in range(1, 9)]
                for file_path in files_to_remove:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                st.success("Toda a vitrine foi limpa e as imagens/vídeos originais retornaram.")

    else:
        st.header(menu_selecionado[2:])
        st.info("Esta seção está em fase de implantação.")

# 8. Controlador de Fluxo Inicial
if not st.session_state['usuario_autenticado']: tela_login()
else: tela_principal()
