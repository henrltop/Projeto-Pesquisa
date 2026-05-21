import streamlit as st
import requests
import pandas as pd
import time
import math
import urllib.parse
import sqlite3
import json
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import os
import tiktoken

def contar_tokens(texto, modelo="gpt-4o-mini"):
    try:
        codificador = tiktoken.encoding_for_model(modelo)
        return len(codificador.encode(texto))
    except KeyError:
        codificador = tiktoken.get_encoding("cl100k_base")
        return len(codificador.encode(texto))

st.set_page_config(page_title="Mineração IOMAT + IA", page_icon="🤖", layout="wide")

st.title("🤖 Pipeline de Mineração IOMAT + IA")
st.markdown("Extração Bruta (Com Busca Exata) ➡️ Classificação IA ➡️ Download de PDFs")

# Cria a pasta para salvar os PDFs automaticamente se ela não existir
if not os.path.exists("pdfs_relevantes"):
    os.makedirs("pdfs_relevantes")

# --- BANCO DE DADOS ---
def inicializar_banco():
    conn = sqlite3.connect("documentos_relevantes.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ano INTEGER,
            data_pub TEXT,
            edicao TEXT,
            pagina INTEGER,
            link_oficial TEXT,
            termo_buscado TEXT,
            tipo_ato TEXT,
            justificativa TEXT,
            texto_bruto TEXT,
            caminho_pdf TEXT,
            UNIQUE(edicao, pagina, termo_buscado)
        )
    ''')
    # Migração para bancos criados sem a coluna caminho_pdf
    try:
        cursor.execute("ALTER TABLE documentos ADD COLUMN caminho_pdf TEXT")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
    conn.commit()
    return conn

conn_db = inicializar_banco()

# --- FUNÇÃO DE DOWNLOAD DO PDF ---
def baixar_pdf_pagina(tipo_edicao, edicao_id, numero_pagina, ano):
    url = f"https://api.iomat.mt.gov.br/transparencia/v1/diarios/{tipo_edicao}/edicoes/{edicao_id}/paginas/{numero_pagina}"
    params = {'formato': 'pdf'}
    headers = {
        "accept": "application/pdf", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        res = requests.get(url, params=params, headers=headers, timeout=20)
        if res.status_code == 200 and 'pdf' in res.headers.get('Content-Type', '').lower():
            caminho_arquivo = f"pdfs_relevantes/DOE_MT_{ano}_Edicao_{edicao_id}_Pagina_{numero_pagina}.pdf"
            with open(caminho_arquivo, 'wb') as f:
                f.write(res.content)
            return caminho_arquivo
        else:
            return None
    except Exception as e:
        return None

# --- FUNÇÃO DA IA ---
def analisar_texto_com_ia(texto, palavra_chave, api_key):
    client = OpenAI(api_key=api_key)
    prompt_sistema = """Você é um pesquisador acadêmico rigoroso avaliando o Diário Oficial de Mato Grosso.
Projeto: "Mapeamento da legislação do ensino superior tecnológico (1961-2008)".

REGRAS DE CLASSIFICAÇÃO:
- CLASSIFIQUE COMO RELEVANTE (true): Textos que tratem de criação, autorização, reconhecimento ou regulamentação de Cursos Superiores de Tecnologia, Educação Profissional, Convênios educacionais (MEC/Estado), estruturação do Conselho Estadual de Educação (CEE/MT), Secretaria de Educação (SEC/SEDUC), UNEMAT ou Escola Técnica Federal. Procure por atos normativos explícitos.
- CLASSIFIQUE COMO IRRELEVANTE (false): Pregões, licitações, contratos de compra, nomeação de servidores comuns, avisos de início de aulas sem peso legal, balanços ou menções casuais.

TIPOS DE ATO ESPERADOS (use exatamente um destes quando aplicável):
Constituição, Emenda Constitucional, Lei, Lei Complementar, Lei Ordinária, Lei Delegada, Medida Provisória, Decreto Legislativo, Decreto, Decreto-Lei, Resolução, Portaria, Instrução Normativa, Regimento, Regulamento, Estatuto, Diretrizes Curriculares, Plano.
Se nenhum tipo se aplica (conteúdo irrelevante), use "Outro" seguido de descrição curta (ex: "Outro - Licitação").

Responda EXCLUSIVAMENTE em JSON:
{
  "relevante": true ou false,
  "tipo_ato": "string (<tipo da lista acima>)",
  "justificativa": "string (motivo curto da classificação)"
}"""
    
    # Removido o limite de 5000 caracteres. Enviaremos o texto bruto extraído da página.
    texto_limpo = texto 
    prompt_usuario = f"Palavra-chave: '{palavra_chave}'.\n\nTexto:\n{texto_limpo}"

    for tentativa in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={ "type": "json_object" },
                messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_usuario}],
                temperature=0.0 
            )
            resposta_crua = response.choices[0].message.content
            try:
                parsed = json.loads(resposta_crua)
            except json.JSONDecodeError:
                parsed = {"relevante": False, "tipo_ato": "Erro de Parse", "justificativa": "A IA retornou JSON malformado."}
            return parsed, prompt_usuario, resposta_crua, None
        except Exception as e:
            if "Rate limit" in str(e) or "429" in str(e):
                time.sleep(3)
            else:
                return None, None, None, str(e)
    return None, None, None, "Limite da OpenAI excedido repetidamente."

# --- FUNÇÃO DE REQUISIÇÃO BLINDADA ---
def fazer_requisicao_iomat(url, params):
    headers = {
        "accept": "application/json", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Connection": "keep-alive"
    }
    for tentativa in range(3):
        try:
            res = requests.get(url, params=params, headers=headers, timeout=20)
            res.raise_for_status()
            return res
        except requests.exceptions.ConnectionError:
            if tentativa < 2:
                time.sleep(5) 
            else:
                raise Exception("O firewall do IOMAT bloqueou seu IP.")
        except Exception as e:
            raise e

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configurações")
    chave_openai = st.text_input("🔑 Chave de API da OpenAI (sk-...):", type="password")
    
    st.divider()
    st.header("🔎 Filtros da Busca")
    palavra_chave = st.text_input("Digite a palavra-chave:", value="henrique severino da cunha")
    
    # A NOVA OPÇÃO DE BUSCA EXATA
    busca_exata = st.checkbox("🎯 Busca Exata (Frase completa)", value=True, help="Se marcado, busca exatamente as palavras juntas na mesma ordem.")
    
    ano_inicio, ano_fim = st.slider("Selecione a faixa de anos:", 1967, 2026, (2000, 2026))
    
    modo_raio_x = st.checkbox("🕵️ Ativar Modo Raio-X", value=True)
    
    st.divider()
    btn_iniciar_pipeline = st.button("🚀 Iniciar Pipeline Completo", type="primary", use_container_width=True)

# =====================================================================
# O GRANDE PIPELINE
# =====================================================================
if btn_iniciar_pipeline:
    # --- VALIDAÇÕES ---
    if not chave_openai:
        st.error("⚠️ A Chave da OpenAI é obrigatória para rodar o pipeline completo.")
        st.stop()
    
    if not chave_openai.startswith("sk-"):
        st.error("⚠️ A chave da OpenAI parece inválida. Ela deve começar com `sk-`.")
        st.stop()
    
    if not palavra_chave.strip():
        st.error("⚠️ Digite uma palavra-chave para buscar.")
        st.stop()
        
    dados_brutos = []
    dados_relevantes = []
    dados_descartados = []
    erros_ia = []
    
    url_busca = "https://api.iomat.mt.gov.br/busca/v1/buscas"
    termo_url = urllib.parse.quote(palavra_chave)
    
    # Envelopa em aspas para enviar à API se a Busca Exata estiver ligada
    termo_para_api = f'"{palavra_chave}"' if busca_exata else palavra_chave
    
    anos_lista = list(range(ano_inicio, ano_fim + 1))
    total_anos = len(anos_lista)
    documentos_processados = set()

    # ---------------------------------------------------------
    # FASE 1: EXTRAÇÃO
    # ---------------------------------------------------------
    with st.status("📥 FASE 1: Extração de Dados do Governo", expanded=True) as status_fase1:
        barra_extracao = st.progress(0)
        painel_status_extracao = st.empty()
        
        for idx_ano, ano_alvo in enumerate(anos_lista):
            barra_extracao.progress(idx_ano / total_anos, text=f"🔍 Baixando documentos do ano {ano_alvo}...")
            
            params_iniciais = {'q': termo_para_api, 'y': ano_alvo}
            
            try:
                res_inicial = fazer_requisicao_iomat(url_busca, params_iniciais)
                json_resp = res_inicial.json()
                es_data = json_resp.get('data', [{}])[0] if 'data' in json_resp else json_resp
                
                total_enc = es_data.get('hits', {}).get('total', 0)
                if isinstance(total_enc, dict): total_enc = total_enc.get('value', 0)
                
                if total_enc == 0: continue 
                
                tamanho_pagina = 10 
                total_paginas = math.ceil(total_enc / tamanho_pagina)
                if total_paginas > 200: total_paginas = 200 
                
                repeticoes_consecutivas = 0
                
                for pagina_atual in range(1, total_paginas + 1):
                    params_pagina = {'q': termo_para_api, 'y': ano_alvo, 'page': pagina_atual}
                    
                    res_pag = fazer_requisicao_iomat(url_busca, params_pagina)
                    json_pag = res_pag.json()
                    dados_pag = json_pag.get('data', [{}])[0] if 'data' in json_pag else json_pag
                    
                    lista_docs = dados_pag.get('hits', {}).get('hits', [])
                    if not lista_docs: break 
                    
                    documentos_novos_na_pagina = 0
                    
                    for item in lista_docs:
                        source = item.get('_source', {})
                        edicao_id = source.get('diario_id') 
                        pagina_doc = source.get('pagina')
                        tipo_edicao = source.get('tipo_edicao', 1) 
                        
                        id_unico = f"{edicao_id}_{pagina_doc}"
                        if id_unico in documentos_processados: continue
                            
                        documentos_processados.add(id_unico)
                        documentos_novos_na_pagina += 1
                        
                        ano_doc = int(source.get('year', 0))
                        data_pub = source.get('data', '')
                        url_iomat = f"https://iomat.mt.gov.br/portal/visualizacoes/pdf/{edicao_id}#/p:{pagina_doc}/e:{edicao_id}?find={termo_url}"
                        texto_bruto = source.get('conteudo', '')
                        texto_conteudo = texto_bruto[0] if isinstance(texto_bruto, list) else texto_bruto
                        nome_edicao = item.get('suplemento', f"{edicao_id}")
                        
                        dados_brutos.append({
                            "Ano": ano_doc,
                            "Data": data_pub,
                            "Edição": nome_edicao,
                            "ID_Edicao": edicao_id, 
                            "Tipo_Edicao": tipo_edicao,
                            "Página": pagina_doc,
                            "Link": url_iomat,
                            "Texto Bruto": texto_conteudo
                        })
                    
                    if documentos_novos_na_pagina == 0:
                        repeticoes_consecutivas += 1
                    else:
                        repeticoes_consecutivas = 0
                        
                    if repeticoes_consecutivas >= 3: break 
                    time.sleep(0.5) 
                
            except Exception as e_req:
                painel_status_extracao.warning(f"Erro ao acessar {ano_alvo}: {e_req}")
                continue

        barra_extracao.progress(1.0, text="Extração 100% Concluída!")
        
        if len(dados_brutos) == 0:
            status_fase1.update(label="📥 FASE 1: Nenhum documento encontrado", state="error")
        else:
            status_fase1.update(label=f"📥 FASE 1: {len(dados_brutos)} documentos extraídos ✅", state="complete", expanded=False)
    
    if len(dados_brutos) == 0:
        st.error("A extração finalizou, mas nenhum documento foi encontrado com esse termo.")
        st.stop()
    
    st.toast(f"✅ {len(dados_brutos)} documentos capturados!")

    # ---------------------------------------------------------
    # ESTIMATIVA DE CUSTO
    # ---------------------------------------------------------
    total_docs = len(dados_brutos)
    
    # Processamento paralelo para contar tokens muito mais rápido
    def processar_tokens_doc(doc):
        # Agora estamos enviando o texto completo, então contamos o texto completo
        return contar_tokens(doc['Texto Bruto'])

    with st.spinner("Calculando estimativa de tokens..."):
        # Usa ThreadPoolExecutor para rodar a tokenização em paralelo
        with ThreadPoolExecutor() as executor:
            resultados_tokens = list(executor.map(processar_tokens_doc, dados_brutos))
            
        tokens_totais_textos = sum(resultados_tokens)
        
    # Adicionamos ~350 tokens extras por documento para cobrir o prompt do sistema, 
    # as instruções fixas e o tamanho da resposta em JSON.
    tokens_estimados = tokens_totais_textos + (total_docs * 350)
    
    # Preço do gpt-4o-mini: ~$0.15 por 1 Milhão de tokens de input e $0.60 por 1M de output.
    custo_estimado = (tokens_estimados / 1_000_000) * 0.15
    
    with st.expander(f"💰 Estimativa de custo: ~${custo_estimado:.4f} USD para {total_docs} documentos", expanded=False):
        st.caption(f"Baseado em ~{tokens_estimados} tokens totais (texto real + prompt do sistema) × $0.15/1M tokens (gpt-4o-mini)")

    # ---------------------------------------------------------
    # FASE 2: ANÁLISE IA E DOWNLOADS
    # ---------------------------------------------------------
    with st.status("🧠 FASE 2: Análise Cognitiva & Download de PDFs", expanded=True) as status_fase2:
        barra_ia = st.progress(0)
        log_raio_x = st.empty()
        
        # Contadores em tempo real
        col_counter1, col_counter2, col_counter3 = st.columns(3)
        placeholder_aprovados = col_counter1.empty()
        placeholder_descartados = col_counter2.empty()
        placeholder_erros = col_counter3.empty()
        placeholder_aprovados.metric("✅ Aprovados", 0)
        placeholder_descartados.metric("🗑️ Descartados", 0)
        placeholder_erros.metric("⚠️ Erros", 0)
        
        for idx, doc in enumerate(dados_brutos):
            barra_ia.progress((idx + 1) / total_docs, text=f"Analisando doc {idx + 1} de {total_docs} (Ano: {doc['Ano']})...")
            
            if modo_raio_x:
                with log_raio_x.container():
                    st.info(f"🔄 Enviando Edição {doc['Edição']} (Pág {doc['Página']}) para a IA...")
            
            analise_ia, texto_enviado, texto_recebido, erro_ia = analisar_texto_com_ia(doc['Texto Bruto'], palavra_chave, chave_openai)
            
            # Em vez de parar o pipeline inteiro, pula o documento com erro
            if erro_ia:
                if modo_raio_x:
                    st.warning(f"⚠️ Erro na IA para Edição {doc['Edição']} (Pág {doc['Página']}): {erro_ia}. Pulando...")
                erros_ia.append({"Ano": doc['Ano'], "Edição": doc['Edição'], "Erro": erro_ia})
                dados_descartados.append({
                    "Ano": doc['Ano'],
                    "Edição": doc['Edição'],
                    "Motivo (IA)": f"Erro: {erro_ia}"
                })
                placeholder_erros.metric("⚠️ Erros", len(erros_ia))
                placeholder_descartados.metric("🗑️ Descartados", len(dados_descartados))
                continue
                
            if modo_raio_x:
                with log_raio_x.container():
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander(f"📤 Texto enviado (Edição {doc['Edição']})"):
                            st.text(texto_enviado)
                    with col2:
                        with st.expander(f"📥 Resposta da IA (Edição {doc['Edição']})"):
                            st.json(texto_recebido)
                            
            if analise_ia.get("relevante") == True:
                if modo_raio_x: st.success(f"✅ APROVADO: {analise_ia.get('justificativa')} - Baixando PDF...")
                
                caminho_pdf = baixar_pdf_pagina(doc['Tipo_Edicao'], doc['ID_Edicao'], doc['Página'], doc['Ano'])
                
                try:
                    cursor = conn_db.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO documentos (ano, data_pub, edicao, pagina, link_oficial, termo_buscado, tipo_ato, justificativa, texto_bruto, caminho_pdf)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (doc['Ano'], doc['Data'], doc['Edição'], doc['Página'], doc['Link'], palavra_chave, analise_ia.get("tipo_ato"), analise_ia.get("justificativa"), doc['Texto Bruto'], caminho_pdf))
                    conn_db.commit()
                except sqlite3.Error as e_db:
                    st.warning(f"⚠️ Erro ao salvar no banco: {e_db}")
                
                dados_relevantes.append({
                    "Ano": doc['Ano'],
                    "Tipo de Ato": analise_ia.get("tipo_ato"),
                    "Justificativa": analise_ia.get("justificativa"),
                    "Link": doc['Link'],
                    "Arquivo PDF": caminho_pdf,
                    "Edição": doc['Edição'],
                    "Página": doc['Página']
                })
                placeholder_aprovados.metric("✅ Aprovados", len(dados_relevantes))
            else:
                if modo_raio_x: st.warning(f"🗑️ DESCARTADO: {analise_ia.get('justificativa')}")
                dados_descartados.append({
                    "Ano": doc['Ano'],
                    "Edição": doc['Edição'],
                    "Motivo (IA)": analise_ia.get('justificativa')
                })
                placeholder_descartados.metric("🗑️ Descartados", len(dados_descartados))
            
            time.sleep(0.3)  # Delay reduzido (era 1.5s)
            
        barra_ia.progress(1.0, text="Análise e Downloads 100% Concluídos!")
        log_raio_x.empty()
        status_fase2.update(label=f"🧠 FASE 2: Concluída ({len(dados_relevantes)} aprovados) ✅", state="complete", expanded=False)

    # ---------------------------------------------------------
    # RESULTADOS FINAIS
    # ---------------------------------------------------------
    st.write("---")
    st.markdown("### 🎉 Pipeline Finalizado!")
    st.balloons()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Aprovados (Com PDF)", len(dados_relevantes))
    col2.metric("🗑️ Descartados", len(dados_descartados))
    col3.metric("📄 Total Analisado", total_docs)
    
    if len(dados_relevantes) > 0:
        st.success("Estes documentos passaram pelo crivo rigoroso da IA. O PDF original de cada um deles foi baixado com sucesso.")
        
        # Tabela resumo interativa
        df_relevantes = pd.DataFrame(dados_relevantes)
        with st.expander("📊 Tabela de Resultados Relevantes", expanded=True):
            st.dataframe(
                df_relevantes[["Ano", "Tipo de Ato", "Justificativa", "Edição", "Página"]],
                use_container_width=True,
                hide_index=True
            )
        
        st.markdown("#### 📥 Downloads Individuais")
        for doc in dados_relevantes:
            with st.container():
                col_info, col_pdf, col_link = st.columns([3, 1, 1])
                with col_info:
                    st.markdown(f"**Ano {doc['Ano']} — {doc['Tipo de Ato']}**")
                    st.caption(f"📝 {doc['Justificativa']}")
                with col_pdf:
                    if doc.get('Arquivo PDF') and os.path.exists(doc['Arquivo PDF']):
                        with open(doc['Arquivo PDF'], "rb") as file:
                            st.download_button(
                                label=f"📄 PDF (Pág {doc['Página']})",
                                data=file,
                                file_name=os.path.basename(doc['Arquivo PDF']),
                                mime="application/pdf",
                                key=f"dl_{doc['Edição']}_{doc['Página']}"
                            )
                    else:
                        st.button("❌ Indisponível", disabled=True, key=f"dl_fail_{doc['Edição']}_{doc['Página']}")
                with col_link:
                    st.link_button("🔗 IOMAT", doc['Link'])
                st.divider()

        if os.path.exists("documentos_relevantes.db"):
            with open("documentos_relevantes.db", "rb") as file:
                st.download_button("💾 Baixar Banco de Dados Completo (.db)", data=file, file_name="documentos_relevantes.db", mime="application/octet-stream", type="primary", use_container_width=True)
    else:
        st.warning("Nenhum documento atendeu aos critérios da pesquisa. Todos foram descartados pela Inteligência Artificial.")
        
    if len(dados_descartados) > 0:
        with st.expander("🗑️ Ver lixeira da Inteligência Artificial"):
            st.dataframe(pd.DataFrame(dados_descartados), use_container_width=True, hide_index=True)
    
    if len(erros_ia) > 0:
        with st.expander(f"⚠️ Ver erros da IA ({len(erros_ia)} documentos com falha)"):
            st.dataframe(pd.DataFrame(erros_ia), use_container_width=True, hide_index=True)

    # Fecha a conexão com o banco ao final do pipeline
    conn_db.close()
    st.toast("🏁 Pipeline finalizado com sucesso!")



    #código bolado