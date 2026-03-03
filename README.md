# 🤖 Pipeline de Mineração IOMAT + IA

> **Vínculo Institucional:** Este projeto foi desenvolvido para atender às demandas do edital referente ao projeto **"Mapeamento da legislação do ensino superior tecnológico (1961-2008)"**.

Este projeto é uma ferramenta de automação voltada para a extração, análise e classificação de Diários Oficiais do Estado de Mato Grosso (IOMAT). A aplicação é construída em **Python/Streamlit** e integra inteligência artificial usando a API da **OpenAI** para separar regulamentações, atos legais relevantes, de menções casuais, realizando o download dos cadernos (PDFs) no final.

## 🚀 Funcionalidades

1. **Busca Exata e Flexível**: Permite buscar frases específicas na API pública de Transparência do IOMAT (por ex.: currículos e portarias oficiais).
2. **Estimativa de Custo Inteligente**: Integração com a biblioteca `tiktoken` paralelizada, estimando precisamente o custo em tokens antes de chamar a inteligência artificial.
3. **Classificação via IA (OpenAI)**: Envia excertos do diário para um assistente de pesquisa configurado, que avalia a relevância de acordo com escopo parametrizado (ex: ensino superior tecnológico, legislação do MEC/MT).
4. **Armazenamento Seguro (SQLite)**: Consolida tudo o que foi capturado, salvo ou descartado num banco de dados relacional interno (`documentos_relevantes.db`).
5. **Automação de Downloads**: PDFs originais são baixados e apresentados para o usuário.

## 📦 Dependências e Instalação

Certifique-se de que tenha o [Python 3.8+](https://www.python.org/downloads/) instalado.

```bash
# 1. Clone ou baixe as pastas do projeto
# 2. Crie e ative um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instale os pacotes requeridos
pip install -r requirements.txt
```

Dependências principais (já inclusas no `requirements.txt`):
* `streamlit` – Interface gráfica interativa web.
* `requests` – Conexão e consumo da arquitetura da API do IOMAT.
* `pandas` – Organização visual dos resultados descartados e relevantes.
* `openai` – Comunicação e inferência (LLM).
* `tiktoken` – Encoding e calculadora exata de tokens da OpenAI.

## ⚙️ Como usar

Inicie o servidor local do Streamlit:

```bash
streamlit run app_iomat.py
```

O navegador abrirá automaticamente em `http://localhost:8501`. Na barra lateral, você deve:
1. Inserir a sua **Chave da OpenAI** (`sk-...`).
2. Digitar o **termo/palavra-chave** desejada.
3. Definir o range de anos e clicar em "Iniciar Pipeline".

## 📁 Estrutura de Arquivos

* `app_iomat.py`: Código-fonte central da aplicação.
* `documentos_relevantes.db`: Banco de dados gerado automaticamente.
* `/pdfs_relevantes`: Pasta criada para armazenar os diários capturados.
* `.streamlit/config.toml`: Configurações visuais globais (tema e visualização).

## 💡 Customizando a IA

Se desejar alterar a pesquisa, basta editar a variável `prompt_sistema` dentro do arquivo `app_iomat.py` e modificar as suas `REGRAS DE CLASSIFICAÇÃO`.

## 👩‍💻 Autores e Desenvolvedores

Código escrito e idealizado por:
* [Beatriz Schuindt](https://github.com/BeatrizSchuindt)
* [Henrique](https://github.com/henrltop)

