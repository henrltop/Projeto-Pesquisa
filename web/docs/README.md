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
| `gpt-oss:20b` | #8 (em andamento) | ⚠️ **cobertura parcial (~69%)** — re-rodar quando concluir |
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
- **taxa de erro**: proporção de falhas de formato.

## Resultados atuais (binário, vs. validação humana)

| Modelo | Cobertura | Erro fmt | Precisão | Recall | F1 | Acurácia |
|---|---|---|---|---|---|---|
| gpt-oss:20b ⚠️parcial | 69% | 5% | 0,73 | 0,78 | **0,76** | **0,70** |
| qwen3:8b | 93% | 2% | 0,57 | **0,87** | 0,69 | 0,57 |
| qwen2.5:7b | 89% | 5% | 0,66 | 0,62 | 0,64 | 0,60 |
| gemma4:e4b ⛔contaminado | 92% | 0% | 0,70 | 0,31 | 0,43 | 0,53 |

> Os números do gemma e a cobertura do gpt-oss mudam ao re-rodar os jobs
> pendentes. Rode `gerar_metricas.py` de novo depois disso.

## Saídas

`dados/`
- `comparativo_tidy.csv` — uma linha por (documento × modelo); fonte única para
  qualquer outro gráfico.
- `distribuicao_classes.csv` — contagem de rótulos por modelo.
- `metricas_modelos.csv` — precisão/recall/F1/acurácia/cobertura/erro por modelo.
- `matrizes_confusao.json` — matriz binária 2×2 por modelo.
- `resumo.json` — tudo agregado + metadados (consumido pelo `plotar.py`).

`graficos/`
- `01_distribuicao_classes.png` — composição de rótulos por modelo.
- `02_gabarito_humano.png` — composição do gabarito (decisões e binário).
- `03_precisao_recall_f1.png`
- `04_acuracia_cobertura.png`
- `05_taxa_erro.png`
- `06_matrizes_confusao.png`
