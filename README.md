# SGCE — Sistema de Gerenciamento e Controle Espacial
### Colônia Aurora Siger · Global Solution 2026 · FIAP

---

## Equipe

| Nome | RM |
|------|----|
| Isabelle Caroline de Camargo Francisco | 572096 |
| Matheus Lyncoln Souza Dias | 570765 |
| Mirela Aparecida Bispo Miguel | 70830 |
| Rodrigo Abrantes Mizerani | 571808 |

---

## Resumo do problema e cenário analisado

A Colônia Aurora Siger é uma base experimental em Marte que opera com recursos energéticos limitados (painéis solares e turbinas eólicas) sob condições climáticas extremas — tempestades de areia frequentes, temperatura externa de −65 °C a −20 °C e radiação solar variável.

O sistema monitora **6 módulos críticos** e **8 turnos de operação**, detectando automaticamente falhas, inconsistências nos dados de telemetria, situações de emergência energética e comunicação comprometida. Com base nos dados históricos, o sistema também prevê o comportamento da próxima janela operacional e emite recomendações priorizadas.

**Inconsistência proposital incluída:** o turno 3 registra geração solar residual (12 kW) com tempestade ativa e apenas 2 painéis funcionando — os painéis deveriam estar desligados. O sistema detecta e sinaliza essa contradição automaticamente.

---

## Estruturas de dados

| Estrutura | Onde é usada | Por quê |
|-----------|-------------|---------|
| **Dicionário** (`MODULOS`) | Acesso a informações dos módulos por ID | Lookup O(1) pelo identificador — ideal para consultas frequentes por chave |
| **Lista** (`historico`) | Séries temporais de telemetria por turno | Preserva a ordem cronológica e permite iterar sobre todos os registros |
| **Fila** (`fila_alertas`) | Alertas pendentes gerados durante a análise | Garante processamento FIFO por ordem de chegada; reordenada por severidade antes da exibição |
| **Pilha** (`pilha_criticos`) | Últimos eventos críticos analisados | Acesso LIFO permite revisar a sequência mais recente de falhas sem percorrer toda a lista |
| **Matriz** (`montar_matriz`) | Leituras de energia e temperatura por turno × variável | Representação tabular facilita visualização e comparação de múltiplas variáveis ao longo do tempo |
| **Hierarquia** (dicionário aninhado) | `energia → solar/eólico/bateria` e `habitat → oxigênio/temperatura/comunicação` | Reflete a estrutura real da colônia e facilita navegação semântica nos dados |

---

## Regras lógicas principais do diagnóstico

### Expressão booleana principal

```
EMERGENCIA = (reserva_bateria < 20% AND consumo > geracao) OR tempestade_ativa OR modulo_critico_falhou
NORMAL     = NOT(EMERGENCIA) AND NOT(consumo > geracao) AND NOT(qualidade_com < 60%)
```

### Portas lógicas implementadas

```python
def porta_and(a, b):  return a and b        # emergencia maxima: reserva critica E consumo alto
def porta_or(a, b):   return a or b         # alerta se energia baixa OU comunicacao falha
def porta_not(a):     return not a          # sem_alerta = NOT(ha_alerta)
```

### Regras de classificação

| Condição | Classificação | Ação gerada |
|----------|--------------|-------------|
| `(reserva < 20% AND consumo > geracao) OR tempestade OR modulo_critico_falhou` | **CRÍTICO** | Desligar mineração e ciência; manter suporte à vida |
| `consumo > geracao OR qualidade_com < 60%` | **ALERTA** | Reduzir sistemas não essenciais; checar enlace |
| `geracao > consumo × 1.2 AND NOT(ha_alerta)` | **NORMAL** | Armazenar excedente na bateria |
| Demais casos | **NORMAL** | Operação dentro dos parâmetros esperados |

### Por que cada regra gera sua ação

- **CRÍTICO por emergência energética:** reserva abaixo de 20 % com consumo superior à geração indica que a bateria se esgotará em poucas horas; desligar sistemas não vitais é a única forma de prolongar a autonomia.
- **CRÍTICO por tempestade:** com painéis desligados a única fonte de energia é a bateria; toda carga não essencial deve ser suspensa imediatamente.
- **ALERTA por consumo alto:** consumo acima da geração drena a reserva progressivamente mesmo sem emergência imediata — intervenção antes da crise.
- **ALERTA por comunicação comprometida:** qualidade abaixo de 60 % compromete o envio de telemetria e pedidos de socorro; sinalizar sem desligar a colônia.

---

## Técnica de previsão e resultado

**Método:** Regressão linear por mínimos quadrados, implementada manualmente sem nenhuma biblioteca externa.

**Variáveis previstas para o turno `N+1`:**

1. **Velocidade do vento** — tendência linear dos turnos anteriores.
2. **Geração eólica** — correlação histórica entre vento e potência gerada.
3. **Consumo total** — tendência linear do consumo agregado.
4. **Geração solar** — média histórica como estimativa conservadora.

**Exemplo de resultado (dados padrão — turno 9):**

```
Vento previsto          : 14.3 km/h
Geração eólica prevista : 9.7 kW
Solar (média histórica) : 34.4 kW
Geração total prevista  : 44.1 kW

Consumo previsto        : 105.0 kW

→ ALERTA: consumo previsto (105.0 kW) supera geração prevista (44.1 kW).
  Deficit de 60.9 kW — reserva (18 kWh) se esgotaria em 0.3 hora(s).
  Recomendação: reduzir consumo de módulos não essenciais antes do próximo turno.
```

A previsão influencia diretamente a fila de alertas: se o consumo previsto superar a geração, um alerta de nível ALERTA é enfileirado e exibido ao operador.

---

## Como executar

**Pré-requisito:** Python 3.8 ou superior. Nenhuma biblioteca externa necessária.

```bash
# Clonar o repositório
git clone <URL_DO_REPOSITORIO>
cd sgce

# Executar o sistema principal
python src/sistema.py

# (Opcional) Regenerar os dados simulados
python src/gerador.py        # gera 8 turnos por padrão
python src/gerador.py 12     # gera 12 turnos
```

---

## Exemplo de entrada e saída

### Entrada (trecho de `data/dados.csv` — turno 3)

```
turno, solar_kw, eolico_kw, bateria_atual, bateria_max, tempestade, radiacao,  qualidade_com
    3,       12,        38,            47,         120,          1,     alta,             41
```

### Saída do sistema (opção 1 — estado da colônia, turno 3)

```
--------------------------------------
  [1] ESTADO DA COLONIA — TURNO ATUAL
----------------------------------------

  Turno atual        : 3
  Geracao total      : 50 kW  (solar: 12 + eolico: 38)
  Consumo total      : 39 kW
  Bateria            : 39%  (47/120 kWh)
  Temperatura ext.   : -52 C
  Tempestade areia   : SIM

  Habitat:
    Oxigenio         : 20.8%
    Temp. interna    : 21.5 C
    Comunicacao      : INATIVA
  Radiacao           : alta
  Comunicacao        : 41%

--- STATUS DOS MODULOS ---

  ID            NOME                                        PRIO    STATUS    CRITICIDADE
  ---------------------------------------------------------------------------------
  MOD-EN-001    Geradores + Paineis Solares                    1    NORMAL    Alta
  MOD-SV-002    Sistemas de Suporte a Vida (ECLSS)             2    NORMAL    Alta
  MOD-HB-003    Modulos Inflaveis BEAM (Habitat)               3    NORMAL    Alta
  MOD-LG-006    Logistica e Suprimentos                        4    NORMAL    Baixa
  MOD-SC-004    Sensores Cientificos                           5    FALHA     Media
  MOD-MN-005    Mineracao e Producao ISRU                      6    FALHA     Media

--- DIAGNOSTICO AUTOMATICO ---
  [CRITICO] Tempestade de areia — paineis solares desligados.
            Sistema operando em reserva de bateria.
            Suporte a vida mantido (prioridade maxima).

--- INCONSISTENCIAS DETECTADAS ---
  !! Turno 3: tempestade ativa mas solar = 12 kW (paineis deveriam estar desligados)
```

---

## Recomendações geradas pelo sistema

O sistema emite recomendações automáticas priorizadas de acordo com o nível de severidade:

| Severidade | Situação | Recomendação |
|-----------|----------|-------------|
| CRÍTICO | Tempestade de areia ativa | Desligar painéis; operar em bateria; suspender mineração e ciência |
| CRÍTICO | Reserva < 20 % e consumo > geração | Desligar mineração e ciência imediatamente; manter suporte à vida |
| ALERTA | Consumo maior que geração | Reduzir sistemas não essenciais; verificar eficiência dos geradores |
| ALERTA | Qualidade de comunicação < 60 % | Verificar antenas; acionar protocolo de comunicação de emergência |
| ALERTA | Previsão: consumo futuro > geração futura | Iniciar corte preventivo de carga antes do próximo turno |
| NORMAL | Geração excede consumo em 20 %+ | Armazenar excedente na bateria para garantir autonomia |

---

## Link do vídeo no YouTube

<!-- [Assistir ao vídeo de apresentação](https://youtu.be/LINK_DO_VIDEO) -->

> Link será adicionado após publicação no YouTube.

---

## Conclusões e aprendizados

O desenvolvimento do SGCE evidenciou como a escolha de estrutura de dados impacta diretamente a eficiência do sistema: o uso de dicionário para o catálogo de módulos reduziu a complexidade de busca de O(n) para O(1), enquanto a fila e a pilha tornaram o fluxo de alertas determinístico e auditável.

A implementação da regressão linear sem bibliotecas reforçou a compreensão do algoritmo de mínimos quadrados e revelou como dados de vento e geração possuem correlação forte, permitindo previsões úteis mesmo com histórico reduzido (8 turnos).

A inconsistência intencional (solar ativo durante tempestade) demonstrou a importância de validações cruzadas entre variáveis correlacionadas — prática essencial em sistemas críticos onde sensores podem falhar silenciosamente.

Por fim, o projeto aproximou os conceitos das três fases do curso (sistemas numéricos, lógica booleana, estruturas de dados e análise simples) de um cenário realista, tornando tangível como a computação sustenta operações de alto risco.
