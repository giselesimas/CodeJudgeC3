import streamlit as st
import streamlit.components.v1 as components
from code_editor import code_editor
import json
import base64
import tempfile
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from juiz_core import corrigir_codigo
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import sys
import io
import traceback
import random
import zipfile

SALT = b"CodeJudgeC3_FURG_C3_2026"

VERSAO = Path("VERSION").read_text(encoding="utf-8").strip()

# Arquivo .enc informado na execução:
# sh rodar.sh testes_parte3.enc
if len(sys.argv) < 2:
    st.error(
        "❌ Informe o arquivo de testes.\n\n"
        "Exemplo (Linux): `sh scripts/rodar.sh testes_parte3.enc`\n\n"
        "Exemplo (Windows): `scripts\\rodar.bat testes_parte3.enc`"
    )
    st.stop()

ARQUIVO_TESTES = Path(sys.argv[1])

PASTA_SOLUCOES = Path("solucoes")

# Cria um backup diferente para cada arquivo de testes
ARQUIVO_BACKUP = (
    PASTA_SOLUCOES / f"backup_{ARQUIVO_TESTES.stem}.json"
)

# ==========================================
# Funções de Backup e Segurança
# ==========================================
def salvar_backup_local(historico):
    try:
        with open(ARQUIVO_BACKUP, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Erro ao salvar backup: {e}")

def carregar_backup_local():
    if ARQUIVO_BACKUP.exists():
        try:
            with open(ARQUIVO_BACKUP, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def gerar_chave(senha: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=SALT, iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(senha.encode("utf-8")))

def carregar_testes_criptografados(senha: str):
    caminho = ARQUIVO_TESTES

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo de testes não encontrado: {caminho}"
        )

    if caminho.suffix.lower() != ".enc":
        raise ValueError(
            "O arquivo de testes deve possuir extensão .enc"
        )

    conteudo_criptografado = caminho.read_bytes()
    fernet = Fernet(gerar_chave(senha))
    dados = fernet.decrypt(conteudo_criptografado)
    return json.loads(dados.decode("utf-8"))

def obter_dados_questao(dados):
    if isinstance(dados, dict):
        peso = float(dados.get("peso", 1.0))
        casos = dados.get("casos", [])
        funcao_alvo = dados.get("funcao_alvo", "")
        template = dados.get("template", "")
    else:
        peso = 1.0
        casos = dados
        funcao_alvo = ""
        template = ""
    return peso, casos, funcao_alvo, template

# ==========================================
# Função de Geração de PDF 
# ==========================================
def gerar_pdf_relatorio(historico, testes, nota_pratica, total_pratica, nota_teorica, nome, matricula, questoes_teoricas, respostas_teoricas):
    pdf = FPDF()
    pdf.add_page()
    
    def limpar_texto(texto):
        return str(texto).encode('latin-1', 'replace').decode('latin-1')
    
    nota_final_total = nota_pratica + nota_teorica
    total_prova_geral = 5.0 + total_pratica # 5 de teórica + soma dos pesos práticos
    
    # CABEÇALHO
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, text=limpar_texto("CodeJudgeC3 - Relatório de Prova"), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(5)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, text=limpar_texto(f"Aluno(a): {nome if nome else 'Não Identificado'}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, text=limpar_texto(f"Matrícula: {matricula if matricula else 'Não Informada'}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, text=limpar_texto(f"Nota Prática (Preliminar): {nota_pratica:.2f} / {total_pratica:.1f} pts"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    
    pdf.set_font("Helvetica", 'I', 9)
    pdf.cell(0, 5, text=limpar_texto("* Observação: Esta é uma nota preliminar automática. A prática será revisada."), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    

    # ------------------------------------------
    # DETALHAMENTO DA PROVA PRÁTICA
    # ------------------------------------------
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, text=limpar_texto("Detalhamento - Prova Prática"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    
    for questao, dados in testes.items():
        peso, casos, funcao_alvo, template = obter_dados_questao(dados)
        tentativas = historico.get(questao, [])
        melhor_acerto = max([t['acertos'] / max(t['total'], 1) for t in tentativas], default=0) if tentativas else 0.0
        nota_questao = melhor_acerto * peso
        
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 10, text=limpar_texto(f"{questao} | Nota: {nota_questao:.1f} / {peso:.1f} pts"), new_x=XPos.LMARGIN, new_y=YPos.NEXT,)
        
        if not tentativas:
            pdf.set_font("Helvetica", 'I', 11)
            pdf.cell(0, 8, text=limpar_texto("Nenhuma submissão enviada."), new_x=XPos.LMARGIN, new_y=YPos.NEXT,)
            pdf.ln(5)
            continue
            
        for i, t in enumerate(tentativas, start=1):
            total_testes = max(t['total'], 1)
            porcentagem = (t['acertos'] / total_testes) * 100
            
            pdf.set_font("Helvetica", 'B', 11)
            pdf.cell(0, 8, text=limpar_texto(f"Tentativa {i} | Acertos: {t['acertos']}/{t['total']} ({porcentagem:.0f}%)"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.set_font("Courier", '', 9)
            codigo_linhas = t['codigo'].split('\n')
            for linha in codigo_linhas:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 5, text=limpar_texto(linha))
            pdf.ln(5)
            
        pdf.ln(5)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        caminho_pdf = Path(tmp.name)

    try:
        pdf.output(str(caminho_pdf))
        return caminho_pdf.read_bytes()
    finally:
        caminho_pdf.unlink(missing_ok=True)

# ==========================================
# Configuração e Estado
# ==========================================
st.set_page_config(page_title="CodeJudgeC3 - Prova", layout="wide")
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 150px !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ATENÇÃO: Mude para False no dia de aplicar a prova!
MODO_DEV = True

if "historico" not in st.session_state:
    st.session_state.historico = carregar_backup_local()
if "sistema_liberado" not in st.session_state:
    st.session_state.sistema_liberado = False
if "nome_permanente" not in st.session_state:
    st.session_state.nome_permanente = ""
if "mat_permanente" not in st.session_state:
    st.session_state.mat_permanente = ""

# --- MODIFICADO: Verifica o backup para saber se a teórica já foi concluída ---
if "etapa_atual" not in st.session_state:
    if st.session_state.historico.get("teorica_concluida", False):
        st.session_state.etapa_atual = "pratica"
    else:
        st.session_state.etapa_atual = "pratica" if MODO_DEV else "teorica"

if "respostas_teoricas" not in st.session_state:
    st.session_state.respostas_teoricas = st.session_state.historico.get("respostas_teoricas", {})
if "questao_teorica_atual" not in st.session_state:
    st.session_state.questao_teorica_atual = 0

# --- MODIFICADO: Carrega a nota teórica salva no backup, se existir ---
if "nota_teorica" not in st.session_state:
    st.session_state.nota_teorica = st.session_state.historico.get("nota_teorica", 0.0)

if "modal_finalizar" not in st.session_state:
    st.session_state.modal_finalizar = False

def salvar_dados():
    st.session_state.nome_permanente = st.session_state.nome_input
    st.session_state.mat_permanente = st.session_state.mat_input

# ==========================================
# Interface de Login
# ==========================================
if not st.session_state.sistema_liberado:
    st.title("🔐 CodeJudgeC3")
    senha = st.text_input("Senha do(a) Professor(a):", type="password")
    
    if st.button("Liberar Sistema", type="primary"):
        try:
            dados_brutos = carregar_testes_criptografados(senha)
            
            # --- LÓGICA DE EMBARALHAMENTO (SHUFFLE) ---
            if "teoricas" in dados_brutos:
                # 1. Embaralha a ordem das questões
                random.shuffle(dados_brutos["teoricas"])
                
                # 2. Embaralha as opções dentro de cada questão
                for q in dados_brutos["teoricas"]:
                    if "opcoes" in q:
                        random.shuffle(q["opcoes"])
                        
            st.session_state.testes = dados_brutos
            st.session_state.sistema_liberado = True
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao liberar o sistema: {e}")
    st.stop()


try:
    # Desempacota o dicionário completo do arquivo .enc
    dados_completos = st.session_state.testes
    
    # Retrocompatibilidade: Se for uma prova antiga (só práticas), trata adequadamente
    if "praticas" in dados_completos or "teoricas" in dados_completos:
        QUESTOES_TEORICAS = dados_completos.get("teoricas", [])
        testes_atuais = dados_completos.get("praticas", {})
    else:
        QUESTOES_TEORICAS = []
        testes_atuais = dados_completos

    # ======================================================
    # ETAPA 1: PROVA TEÓRICA (Múltipla Escolha - Tipo Moodle)
    # ======================================================
    if st.session_state.etapa_atual == "teorica":
        st.title("📝 Parte 1: Teórica (Peso 5.0)")
        
        # Caso o professor não tenha adicionado questões teóricas
        if not QUESTOES_TEORICAS:
            st.info("Nenhuma questão teórica cadastrada nesta prova.")
            if st.button("Ir direto para a Prova Prática 🚀", type="primary"):
                st.session_state.nota_teorica = 0.0
                st.session_state.etapa_atual = "pratica"
                
                # --- MODIFICADO: Registra no backup que pulou/concluiu a etapa ---
                st.session_state.historico["teorica_concluida"] = True
                st.session_state.historico["nota_teorica"] = 0.0
                salvar_backup_local(st.session_state.historico)
                
                st.rerun()
        else:
            # BARRA LATERAL (Navegação Moodle)
            st.sidebar.subheader("Navegação do Questionário")
            st.sidebar.write("🟢 Respondida | ⚪ Pendente")
            
            cols = st.sidebar.columns(4)
            for idx in range(len(QUESTOES_TEORICAS)):
                enunciado_atual = QUESTOES_TEORICAS[idx]["enunciado"]
                foi_respondida = enunciado_atual in st.session_state.respostas_teoricas
                icone = "🟢" if foi_respondida else "⚪"
                
                tipo_botao = "primary" if st.session_state.questao_teorica_atual == idx else "secondary"
                
                if cols[idx % 4].button(f"{icone} {idx+1}", key=f"nav_{idx}", type=tipo_botao):
                    st.session_state.questao_teorica_atual = idx
                    st.rerun()
                    
            st.sidebar.divider()
            todas_respondidas = len(st.session_state.respostas_teoricas) == len(QUESTOES_TEORICAS)
            
            # LÓGICA DE CONFIRMAÇÃO
            if not st.session_state.modal_finalizar:
                # Mostra o botão normal
                if st.sidebar.button("Terminar Prova Teórica", type="primary", disabled=not todas_respondidas):
                    st.session_state.modal_finalizar = True
                    st.rerun()
            else:
                # Mostra o aviso e os botões de Sim/Não
                st.sidebar.warning("⚠️ **Tem certeza?**\n\nSua prova teórica será corrigida agora e você **não poderá alterar suas respostas** após avançar para a prática.")
                col_sim, col_nao = st.sidebar.columns(2)
                
                if col_sim.button("✔️ Confirmar", type="primary"):
                    acertos = sum(1 for q in QUESTOES_TEORICAS if st.session_state.respostas_teoricas.get(q["enunciado"]) == q["correta"])
                    st.session_state.nota_teorica = (acertos / len(QUESTOES_TEORICAS)) * 5.0
                    st.session_state.modal_finalizar = False # Reseta a variável
                    st.session_state.etapa_atual = "pratica"
                    
                    # --- MODIFICADO: Salva a conclusão e a nota no backup ---
                    st.session_state.historico["teorica_concluida"] = True
                    st.session_state.historico["nota_teorica"] = st.session_state.nota_teorica
                    salvar_backup_local(st.session_state.historico)
                    
                    st.rerun()
                    
                if col_nao.button("❌ Voltar"):
                    st.session_state.modal_finalizar = False
                    st.rerun()
                
            if not todas_respondidas:
                st.sidebar.caption("Responda todas as questões para liberar a entrega da teórica.")

            # ÁREA DA QUESTÃO PRINCIPAL
            q_idx = st.session_state.questao_teorica_atual
            questao = QUESTOES_TEORICAS[q_idx]
            
            # Variável para forçar a recriação do radio button ao limpar
            reset_key = f"reset_q_{q_idx}"
            if reset_key not in st.session_state:
                st.session_state[reset_key] = 0
                
            with st.container(border=True):
                st.subheader(f"Questão {q_idx + 1} de {len(QUESTOES_TEORICAS)}")
                st.markdown(questao["enunciado"])
                
                resposta_salva = st.session_state.respostas_teoricas.get(questao["enunciado"], None)
                indice_selecionado = questao["opcoes"].index(resposta_salva) if resposta_salva in questao["opcoes"] else None
                
                # Chave dinâmica
                chave_radio = f"radio_q_{q_idx}_{st.session_state[reset_key]}"
                
                def registrar_resposta():
                    st.session_state.respostas_teoricas[questao["enunciado"]] = st.session_state[chave_radio]
                    # ---> SALVA NO BACKUP
                    st.session_state.historico["respostas_teoricas"] = st.session_state.respostas_teoricas
                    salvar_backup_local(st.session_state.historico)
                
                # Cria um dicionário vinculando a opção ao formato "a) Opção"
                opcoes_com_letras = {opcao: f"{chr(97+i)}) {opcao}" for i, opcao in enumerate(questao["opcoes"])}
                
                st.radio(
                    label="Alternativas",
                    label_visibility="collapsed",
                    options=questao["opcoes"],
                    format_func=lambda x: opcoes_com_letras[x],
                    index=indice_selecionado,
                    key=chave_radio,
                    on_change=registrar_resposta
                )
                
                def limpar_resposta(enunciado_limpar, idx):
                    if enunciado_limpar in st.session_state.respostas_teoricas:
                        del st.session_state.respostas_teoricas[enunciado_limpar]
                    st.session_state[f"reset_q_{idx}"] += 1
                    # ---> SALVA NO BACKUP APÓS LIMPAR
                    st.session_state.historico["respostas_teoricas"] = st.session_state.respostas_teoricas
                    salvar_backup_local(st.session_state.historico)

                if resposta_salva is not None:
                    st.write("") 
                    st.button("🧹 Limpar Escolha", on_click=limpar_resposta, args=(questao["enunciado"], q_idx))
                
            # Botões de Voltar / Avançar
            col_voltar, col_vazio, col_avancar = st.columns([1, 2, 1])
            if q_idx > 0:
                if col_voltar.button("⬅️ Anterior", use_container_width=True):
                    st.session_state.questao_teorica_atual -= 1
                    st.rerun()
            if q_idx < len(QUESTOES_TEORICAS) - 1:
                if col_avancar.button("Próxima ➡️", use_container_width=True):
                    st.session_state.questao_teorica_atual += 1
                    st.rerun()
    
    # ======================================================
    # ETAPA 2: PROVA PRÁTICA (LeetCode / Beecrowd / Juiz Core)
    # ======================================================
    elif st.session_state.etapa_atual == "pratica":
        
        st.title("💻 Exercícios Práticos")

        aba_prova, aba_relatorio = st.tabs([
            "💻 Área de Prova",        
            "📄 Relatório e Entrega",         
        ])

        with aba_prova:
            col1, col2 = st.columns(2)

            with col1:
                questao_sel = st.selectbox("Selecione a Questão:", list(testes_atuais.keys()))
                
                if questao_sel:
                    dados_q = testes_atuais[questao_sel]
                    peso_q, casos_q, funcao_alvo, template_q = obter_dados_questao(dados_q)
                    
                    tentativas_questao = st.session_state.historico.get(questao_sel, [])
                    
                    # Se houver histórico, carrega o código anterior. Caso contrário, carrega o template (estilo LeetCode)
                    if tentativas_questao:
                        codigo_inicial = tentativas_questao[-1]["codigo"]
                    else:
                        codigo_inicial = template_q if template_q else ""

                    codigo_submeter = ""
                    acionou_correcao = False
                    
                    st.markdown("**Escreva seu código aqui:**")
                    botoes_editor = [{
                        "name": "Corrigir Código",
                        "feather": "Play",
                        "primary": True,
                        "hasText": True,
                        "showWithIcon": True,
                        "commands": ["submit"],
                        "style": {"bottom": "0.5rem", "right": "0.5rem"}
                    }]

                    with st.container(border=True):
                        chave_editor = f"editor_codigo_{questao_sel}"
                        
                        resultado_editor = code_editor(
                            codigo_inicial, 
                            lang="python",
                            theme="textmate", 
                            shortcuts="vscode", 
                            buttons=botoes_editor,
                            key=chave_editor, 
                            options={
                                "minLines": 10, 
                                "maxLines": 50, 
                                "showLineNumbers": True, 
                                "showPrintMargin": False,
                                "tabSize": 4,
                                "enableBasicAutocompletion": False,
                                "enableLiveAutocompletion": False,
                                "enableSnippets": False
                            }
                        )
                    
                    if resultado_editor and 'text' in resultado_editor and len(resultado_editor['text']) > 0:
                        codigo_submeter = resultado_editor['text']
                    else:
                        codigo_submeter = codigo_inicial
                        
                    acionou_correcao = (resultado_editor.get('type') == "submit")

                    if acionou_correcao:
                        if not codigo_submeter or not codigo_submeter.strip():
                            st.warning("⚠️ Digite um código antes de corrigir.")
                        else:
                            with st.spinner("Compilando e executando testes..."):
                                res = corrigir_codigo(codigo_submeter, casos_q, funcao_alvo)
                                if questao_sel not in st.session_state.historico:
                                    st.session_state.historico[questao_sel] = []
                                
                                st.session_state.historico[questao_sel].append({
                                    "codigo": codigo_submeter,
                                    "acertos": res["acertos"],
                                    "total": res["total"],
                                    "resultados": res["resultados"]
                                })
                                salvar_backup_local(st.session_state.historico)
                                
                                if res["acertos"] == res["total"] and res["total"] > 0:
                                    st.balloons()

            with col2:
                st.subheader("📜 Histórico de Submissões")
                if questao_sel:
                    tentativas = st.session_state.historico.get(questao_sel, [])
                    if not tentativas: 
                        st.write("Nenhuma tentativa enviada ainda.")
                    else:
                        for i, t in enumerate(reversed(tentativas)):
                            label = f"Tentativa {len(tentativas)-i} - Acertos: {t['acertos']}/{t['total']}"
                            with st.expander(label, expanded=(i==0)):
                                if t['acertos'] == t['total'] and t['total'] > 0:
                                    st.success("⭐ 100% de Acerto!")                                
                                st.code(t['codigo'], language="python")
                                st.divider()
                                
                                for r in t['resultados']:
                                    status = r.get('status', 'Erro')
                                    if status == "Accepted":
                                        st.success(f"✅ Teste {r['teste']}: Accepted")
                                    elif status == "Runtime Error":
                                        st.error(f"💥 Teste {r['teste']}: Runtime Error")
                                        st.code(r.get('erro', ''), language="python")
                                    elif status == "Time Limit Exceeded":
                                        st.warning(f"⏳ Teste {r['teste']}: Time Limit Exceeded")
                                    elif status == "Compilation Error":
                                        st.error(f"🛑 Teste {r['teste']}: Compilation Error")
                                        st.code(r.get('erro', ''), language="python")
                                    else:
                                        st.error(f"❌ Teste {r['teste']}: Wrong Answer")
                                        c_obt, c_esp = st.columns(2)
                                        c_obt.write("**Sua Saída:**")
                                        c_obt.code(r.get('saida_obtida', ''))
                                        c_esp.write("**Saída Esperada:**")
                                        c_esp.code(r.get('saida_esperada', ''))

        # ==========================================
        # CÁLCULO DAS NOTAS
        # ==========================================
        nota_pratica_calculada = 0.0
        total_prova_pratica = 0.0
        
        for q, dados in testes_atuais.items():
            peso, casos, funcao_alvo, template = obter_dados_questao(dados)
            total_prova_pratica += peso
            tentativas = st.session_state.historico.get(q, [])
            melhor_acerto = max([t['acertos']/max(t['total'], 1) for t in tentativas], default=0)
            nota_pratica_calculada += (melhor_acerto * peso)

        # ==========================================
        # Relatório e Entrega
        # ==========================================
        with aba_relatorio:
            st.subheader("👤 Identificação do Aluno")
            col_nome, col_mat = st.columns(2)
            with col_nome:
                st.text_input("Nome Completo:", key="nome_input", value=st.session_state.nome_permanente, on_change=salvar_dados)
            with col_mat:
                st.text_input("Matrícula:", key="mat_input", value=st.session_state.mat_permanente, on_change=salvar_dados)
                
            st.divider()
            
            nome = st.session_state.nome_permanente
            matricula = st.session_state.mat_permanente
            faltam_dados = not nome.strip() or not matricula.strip()
            
            if not faltam_dados:
                nome_formatado = '_'.join(nome.lower().split())
                
                # ---> NOVIDADE: Cria uma cópia do JSON com o nome do aluno
                try:
                    with open(PASTA_SOLUCOES / f"{nome_formatado}.json", "w", encoding="utf-8") as f:
                        json.dump(st.session_state.historico, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    st.error(f"Erro ao criar cópia do JSON do aluno: {e}")

                # ---> Geração do PDF
                pdf_bytes = gerar_pdf_relatorio(
                    st.session_state.historico, 
                    testes_atuais, 
                    nota_pratica_calculada, 
                    total_prova_pratica,
                    st.session_state.nota_teorica,
                    nome,
                    matricula,
                    QUESTOES_TEORICAS,
                    st.session_state.respostas_teoricas
                )

                # Nome da prova, por exemplo: testes_parte3
                nome_prova = ARQUIVO_TESTES.stem

                # JSON consolidado
                json_bytes = json.dumps(
                    st.session_state.historico,
                    ensure_ascii=False,
                    indent=4
                ).encode("utf-8")

                # Cria ZIP em memória
                zip_buffer = io.BytesIO()

                with zipfile.ZipFile(
                    zip_buffer,
                    "w",
                    zipfile.ZIP_DEFLATED
                ) as zip_file:

                    zip_file.writestr(
                        f"solucoes_{nome_prova}_{nome_formatado}_{matricula}.json",
                        json_bytes
                    )

                    zip_file.writestr(
                        f"comprovante_{nome_prova}_{nome_formatado}_{matricula}.pdf",
                        pdf_bytes
                    )

                zip_buffer.seek(0)

                st.download_button(
                    label="📦 Baixar Entrega",
                    data=zip_buffer.getvalue(),
                    file_name=f"entrega_{nome_prova}_{nome_formatado}_{matricula}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
            else:
                st.warning("⚠️ Preencha nome e matrícula para gerar o relatório e salvar os dados.")

        # ==========================================
        # BARRA LATERAL (Sidebar - Fase Prática)
        # ==========================================
        with st.sidebar:
            # Substitui st.subheader por HTML
            st.markdown('<h4 style="font-size: 14px; margin-bottom: 0px;">Progresso Prático</h4>', unsafe_allow_html=True)
            
            for q, dados in testes_atuais.items():
                peso, casos, funcao_alvo, template = obter_dados_questao(dados)
                tentativas = st.session_state.historico.get(q, [])
                melhor_acerto = max([t['acertos']/max(t['total'], 1) for t in tentativas], default=0)
                
                status = "✅" if melhor_acerto == 1 else "⏳"
                
                # Substitui st.write por HTML para controlar a fonte (ex: 13px)
                st.markdown(f"<p style='font-size: 13px; margin-bottom: 5px;'>{status} <b>{q}</b> ({peso} pts)</p>", unsafe_allow_html=True)
                st.progress(melhor_acerto)
            
            st.divider()
            #nota_total = st.session_state.nota_teorica + nota_pratica_calculada
            nota_total = st.session_state.nota_teorica + nota_pratica_calculada
            total_geral = total_prova_pratica
            
            st.metric("Nota Final Total Estimada", f"{nota_total:.1f} / {total_geral:.1f}")
            
            # st.info já tem um tamanho fixo, mas podemos customizar usando markdown num bloco div parecido
            st.markdown(
                """
                <div style="background-color: #e8f4f8; padding: 10px; border-radius: 5px; font-size: 13px;">
                    💡 <b>Aviso:</b> Esta nota é preliminar. Todos os códigos serão revisados manualmente pelo(a) professor(a).
                </div>
                """, 
                unsafe_allow_html=True
            )            

            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 40px;">
                    <p style="color: #808495; font-size: 12px;">
                        Desenvolvido por <br><b>Profª. Gisele Simas - C3, FURG</b><br>
                        CodeJudgeC3 v{VERSAO}
                    </p>
                </div>
                """, 
                unsafe_allow_html=True
            )

except Exception as erro_critico:
    st.error("🚨 Ocorreu um erro crítico!")
    st.exception(erro_critico)
