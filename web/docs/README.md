# Avaliação dos modelos locais de classificação

Pacote reprodutível que compara os **modelos LLM locais** de classificação
contra o **gabarito humano**, sobre o mesmo corpus (termo *"Formação
profissional"*, 1961–2008, 203 documentos do IOMAT).

## O que tem aqui

| Arquivo | Papel |
|---|---|
| `gerar_metricas.py` | Lê o banco (somente leitura), monta a comparação e calcula as métricas. Escreve em `dados/`. |
| `plotar.py` | Lê `dados/resumo.json` e gera os gráficos em `graficos/`. Não acessa o banco. |
| `dados/` | Saídas tabulares (CSV) e agregadas (JSON). |
| `graficos/` | Figuras PNG. |

## Como rodar

A partir da pasta `web/`, com o virtualenv ativo:

```bash
python docs/gerar_metricas.py            # gabarito = humano (padrão)
python docs/plotar.py                    # gera as figuras
python docs/gerar_metricas.py --gabarito=modelo   # (opcional) referência = modelo-assistente
```

`gerar_metricas.py` é **idempotente e somente leitura**. Ele auto-seleciona o
job mais recente de cada modelo; quando uma busca em andamento terminar, basta
rodar de novo para atualizar números e figuras.

## O gabarito = validação humana

A referência é a **decisão do revisor humano** registrada na tabela `Review`
(202 documentos). O critério é o do pesquisador: **concordar com a sugestão da
IA é uma validação; discordar e justificar também é uma validação**. Portanto a
verdade é sempre a decisão humana — não a resposta crua do modelo-assistente.

Mapeamento para binário (classe positiva = relevante):

| Decisão humana | Binário |
|---|---|
| super_relevante, aprovado, ressalva | relevante |
| rejeitado | não-relevante |

Gabarito atual: **113 relevantes / 89 não-relevantes**.

> **Referência auxiliar.** O modelo-assistente que produziu as sugestões iniciais
> concorda com o humano em **~75%** dos casos (reportado em `referencia_auxiliar`
> no `resumo.json`). Isso justamente mostra *por que* não se usa a resposta crua
> dele como gabarito: em ~1 a cada 4 documentos o humano decidiu diferente.

## Modelos avaliados (seleção automática de job)

| Modelo | Job | Observação sobre o dado |
|---|---|---|
| `qwen3:8b` | #6 (concluído) | ✅ limpo (pós-correção de erro de formato) |
| `qwen2.5:7b` | #7 (concluído) | ✅ limpo |
| `gpt-oss:20b` | #8 (concluído) | ✅ concluído; cobertura 83% (os 17% restantes são falhas de formato + não processados) |
| `gemma4:e4b` | #3 (concluído) | ⛔ **contaminado**: os 100 "duvidosos" são **100% falhas de formato** (pré-correção), não decisões. Recall artificialmente baixo. **Re-rodar.** |

### Sobre a contaminação do gemma (e o que mudou no código)

Antes da correção `8adfb3f` (16/06 11:23), o parser do classificador tinha um
*fallback* silencioso: qualquer resposta sem o campo `classificacao` válido era
**forçada para "duvidoso"**:

```python
if classe not in {"super_relevante","relevante","duvidoso","irrelevante"}:
    classe = "duvidoso"          # <- forçava, sem retry e sem registrar erro
```

O `gemma4:e4b` (#3, rodado às 08:24, ~3 h antes do fix) frequentemente devolvia
JSON fora da tarefa (`{"resumo": ...}`, `{"result": {...}}` etc.), então **todos
os 100 "duvidosos" dele são esse fallback** — verificado documento a documento.
Após a correção, essas respostas passam por *retry* com reforço e, se
persistirem, viram a classe `erro` (com a resposta crua salva), ficando **fora**
do cálculo de métricas em vez de poluir como "duvidoso".

## Métricas calculadas

Binário, classe positiva = **relevante**. A classe `erro` (falha de formato) é
**excluída** do cálculo e reportada à parte como `taxa_erro`.

- precisão, recall, F1, acurácia, matriz de confusão 2×2 (vs. humano);
- **cobertura**: documentos do gabarito efetivamente classificados pelo modelo;
- **taxa de erro**: proporção de falhas de formato;
- **tempo por documento**: mediana do intervalo entre classificações consecutivas
  (robusta a pausas). É tempo **fim-a-fim** — inclui o delimitador e os downloads
  do IOMAT —, **não** a inferência pura do classificador.

## Resultados atuais (binário, vs. validação humana)

| Modelo | Cobertura | Erro fmt | Precisão | Recall | F1 | Acurácia | Tempo/doc |
|---|---|---|---|---|---|---|---|
| gpt-oss:20b | 83% | 6% | 0,71 | 0,76 | **0,73** | **0,68** | 41 s |
| qwen3:8b | 93% | 2% | 0,57 | **0,87** | 0,69 | 0,57 | 59 s |
| qwen2.5:7b | 89% | 5% | 0,66 | 0,62 | 0,64 | 0,60 | 29 s |
| gemma4:e4b ⛔contaminado | 92% | 0% | 0,70 | 0,31 | 0,43 | 0,53 | 29 s |

> O gemma segue contaminado (os 100 "duvidosos" pré-correção derrubam o recall);
> os números dele só melhoram ao re-rodar o job com o código atual. Rode
> `gerar_metricas.py` de novo depois disso.

## Saídas

`dados/`
- `comparativo_tidy.csv` — uma linha por (documento × modelo); fonte única para
  qualquer outro gráfico.
- `distribuicao_classes.csv` — contagem de rótulos por modelo.
- `metricas_modelos.csv` — precisão/recall/F1/acurácia/cobertura/erro/tempo por modelo.
- `matrizes_confusao.json` — matriz binária 2×2 por modelo.
- `resumo.json` — tudo agregado + metadados (consumido pelo `plotar.py`).

`graficos/` (cada uma descrita na seção abaixo)
- `01_comparativo_humano_modelos.png`
- `02_gabarito_humano.png`
- `03_precisao_recall_f1.png`
- `04_completude.png`
- `05_tempo_por_modelo.png`
- `06_matrizes_confusao.png`

## Descrição das figuras (para legendas do artigo)

Texto pronto para adaptar como legenda. Em todas, **o gabarito é a validação
humana** e a **classe positiva é "relevante"**.

### 01 — Relevância: humano vs. modelos
**Mostra:** quantos dos documentos cada um considerou relevante (verde) ou
não-relevante (cinza); em vermelho, as falhas de formato dos modelos. A barra do
humano, com contorno, é a referência (113 relevantes / 89 não).
**Como ler:** compare a altura do bloco verde de cada modelo com a do humano.
Acima de 113 → o modelo **super-sinaliza** relevância; abaixo → **subnotifica**.
**Conclusão:** gpt-oss (103) é o mais próximo do humano; qwen3 infla muito (158);
gemma subnotifica (47).

### 02 — O gabarito humano
**Mostra:** a distribuição das decisões manuais nos quatro níveis (super
relevante, aprovado, ressalva, rejeitado).
**Como ler / uso:** figura de **caracterização do conjunto de referência** (para
a seção de metodologia). No binário: super + aprovado + ressalva = relevante;
rejeitado = não-relevante.

### 03 — Precisão, Recall e F1
**Mostra:** as três métricas por modelo, contra o gabarito humano.
**Como ler:** *Precisão* = dos que o modelo chamou de relevante, quantos o humano
confirmou. *Recall* = dos relevantes do humano, quantos o modelo encontrou. *F1*
= equilíbrio entre as duas (média harmônica).
**Conclusão:** gpt-oss tem o melhor F1 (0,73); qwen3 tem recall altíssimo (0,87)
mas precisão baixa (0,57) — encontra quase todos os relevantes, ao custo de
muitos falsos positivos.

### 04 — Completude
**Mostra:** dos documentos do corpus, quantos cada modelo classificou com
sucesso (teal), quantos falharam no formato (vermelho) e quantos não chegaram a
ser processados (cinza claro).
**Como ler:** é **robustez de execução — quanto** do corpus o modelo entregou —,
**não qualidade**. A qualidade (acurácia, F1) está na tabela e nas figuras 03 e
06. Aqui só importa o tamanho do bloco teal.
**Conclusão:** qwen3 e gemma cobriram quase tudo; gpt-oss foi o que mais deixou
de fora (entre falhas de formato e documentos não processados).

### 05 — Tempo por documento
**Mostra:** a mediana de segundos por documento, do mais rápido (verde) ao mais
lento (vermelho).
**Como ler:** é tempo **fim-a-fim** do pipeline (delimitador local + download +
classificação), **não** a inferência pura do classificador. Serve para comparar o
custo de processamento **relativo** entre os modelos.
**Conclusão:** qwen2.5 e gemma (~29 s) são os mais rápidos; gpt-oss 41 s; qwen3
59 s.

### 06 — Matrizes de confusão
**Mostra:** para cada modelo, a matriz 2×2 contra o humano. Linhas = decisão
humana; colunas = predição do modelo. A diagonal são os acertos; cada célula traz
a contagem e o percentual por linha.
**Como ler:** célula inferior-direita = verdadeiros relevantes; superior-direita
= falsos positivos; inferior-esquerda = falsos negativos.
**Conclusão:** qwen3 quase não tem falsos negativos (13) mas muitos falsos
positivos (67); gemma é o oposto (73 falsos negativos); gpt-oss é o mais
equilibrado.

> **Acurácia** não tem figura própria (era a fonte de confusão do gráfico
> anterior): ela é redundante com o F1 + a matriz de confusão, então fica apenas
> na tabela de resultados acima.
