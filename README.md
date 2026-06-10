# Global Solution - 1º Semestre
### Colônia Aurora Siger · Global Solution 2026/1 · FIAP

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![FIAP](https://img.shields.io/badge/FIAP-Global%20Solution-red)
![GlobalSolution](https://img.shields.io/badge/Global%20Solution-2026%2F1-orange)

---

## Estrutura do projeto

```
GlobalSolution-S1/
├── src/
│   ├── sistema.py        # sistema principal — menu, análise, previsão
│   └── gerador.py        # gerador de dados simulados e eventos
├── data/
│   ├── dados.csv         # telemetria gerada por turno
│   └── eventos.csv       # log de eventos de pré-missão
├── docs/
│   ├── Relatorio Global Solution.pdf
│   ├── link_video.txt
│   └── uso_ia.md
└── README.md
```

---

## Equipe

| Nome | RM |
|------|----|
| Isabelle Caroline de Camargo Francisco | 572096 |
| Matheus Lyncoln Souza Dias | 570765 |
| Mirela Aparecida Bispo Miguel | 570830 |
| Rodrigo Abrantes Mizerani | 571808 |

---

## Resumo do problema e cenário analisado

A Colônia Aurora Siger é uma base experimental em Marte que opera com recursos energéticos limitados (painéis solares e turbinas eólicas) sob condições climáticas extremas - tempestades de areia frequentes, temperatura externa de −65 °C a −20 °C e radiação solar variável.

O sistema monitora **6 módulos críticos** e **6 turnos de operação**, detectando automaticamente falhas, inconsistências nos dados de telemetria, situações de emergência energética e comunicação comprometida. Com base nos dados históricos, o sistema também prevê o comportamento da próxima janela operacional e emite recomendações priorizadas.

**Inconsistência proposital incluída:** o gerador (`src/gerador.py`) injeta deliberadamente uma contradição nos dados simulados a cada execução - por exemplo, um módulo registrado como FALHA mas com consumo de energia positivo, ou geração solar acima de zero durante uma tempestade de areia. O sistema cruza as variáveis e sinaliza a inconsistência automaticamente na seção "Inconsistências Detectadas" da opção 1.

---

## Estruturas de dados

| Estrutura | Onde é usada | Por quê |
|-----------|-------------|---------|
| **Dicionário** (`MODULOS`) | Acesso a informações dos módulos por ID | Lookup O(1) pelo identificador - ideal para consultas frequentes por chave |
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
- **ALERTA por consumo alto:** consumo acima da geração drena a reserva progressivamente mesmo sem emergência imediata - intervenção antes da crise.
- **ALERTA por comunicação comprometida:** qualidade abaixo de 60 % compromete o envio de telemetria e pedidos de socorro; sinalizar sem desligar a colônia.

---

## Técnica de previsão e resultado

**Método:** Regressão linear por mínimos quadrados, implementada manualmente sem nenhuma biblioteca externa.

**Variáveis previstas para o turno `N+1`:**

1. **Velocidade do vento** - tendência linear dos turnos anteriores.
2. **Geração eólica** - correlação histórica entre vento e potência gerada.
3. **Consumo total** - tendência linear do consumo agregado.
4. **Geração solar** - média histórica como estimativa conservadora.

**Exemplo de resultado (dados padrão - turno 9):**

```
Vento previsto          : 14.3 km/h
Geração eólica prevista : 9.7 kW
Solar (média histórica) : 34.4 kW
Geração total prevista  : 44.1 kW

Consumo previsto        : 105.0 kW

→ ALERTA: consumo previsto (105.0 kW) supera geração prevista (44.1 kW).
  Deficit de 60.9 kW - reserva (18 kWh) se esgotaria em 0.3 hora(s).
  Recomendação: reduzir consumo de módulos não essenciais antes do próximo turno.
```

A previsão influencia diretamente a fila de alertas: se o consumo previsto superar a geração, um alerta de nível ALERTA é enfileirado e exibido ao operador.

---

## Como executar

**Pré-requisito:** Python 3.8 ou superior. Nenhuma biblioteca externa necessária.

```bash
# Clonar o repositório
git clone https://github.com/Aurora-Siger/GlobalSolution-S1
cd GlobalSolution-S1

# Executar o sistema principal
python src/sistema.py

# (Opcional) Regenerar os dados simulados
python src/gerador.py        # gera 6 turnos por padrão
python src/gerador.py 12     # gera 12 turnos
```

---

## Funcionalidades - opções do menu

### Opção 1 - Estado da colônia (turno atual)
Exibe um painel completo do último turno registrado na telemetria:
- Geração total (solar + eólico), consumo total e nível de bateria em %
- Condições ambientais: temperatura externa, tempestade, radiação e qualidade de comunicação
- Status do habitat: oxigênio, temperatura interna e link de comunicação
- **Tabela de módulos** - lista os 6 módulos ordenados por prioridade operacional com status NORMAL/FALHA
- **Diagnóstico automático** - classifica a missão em CRÍTICO, ALERTA ou NORMAL usando as regras booleanas e emite recomendações imediatas
- **Análise de energia** - percentual de cobertura da geração sobre o consumo e autonomia estimada da bateria em horas, com detalhamento por sistema
- **Inconsistências detectadas** - cruza variáveis para identificar contradições nos dados (ex: módulo em FALHA com consumo registrado). Inconsistëncias são geradas de forma proposital pelo *src/gerador.py*
- **Fila de alertas** - exibe os alertas gerados no turno, ordenados por severidade (CRÍTICO primeiro)
- **Pilha de eventos críticos** - mostra os últimos eventos críticos em ordem LIFO (mais recente no topo)

### Opção 2 - Consultar módulo específico
Permite busca por ID de módulo (ex: `MOD-SV-002`):
- Exibe nome, prioridade, criticidade e status atual do módulo
- Mostra o histórico de status (OK / FALHA) turno a turno ao longo de toda a telemetria

### Opção 3 - Previsão por regressão linear
Calcula a previsão para o próximo turno usando mínimos quadrados implementado manualmente (sem bibliotecas):
1. Prevê a **velocidade do vento** pela tendência histórica dos turnos
2. Estima a **geração eólica** com base na correlação vento × potência
3. Usa a **média histórica** de geração solar como estimativa conservadora
4. Prevê o **consumo total** pela tendência dos turnos anteriores
- Se consumo previsto > geração prevista: calcula em quantas horas a bateria se esgota e enfileira um alerta
- Se geração prevista cobre o consumo: informa o excedente estimado

### Opção 4 - Log de eventos
Exibe o registro histórico completo de eventos, ordenado por turno e severidade:
- **Eventos PRE** - eventos de pré-missão lidos de `data/eventos.csv`: reinicialização de sistema, falha de sensor, mudança de prioridade e modo de economia
- **Eventos dinâmicos** - gerados automaticamente a partir dos dados de telemetria: tempestades, falhas de módulo, alertas de bateria, comunicação comprometida e inconsistências detectadas
- Tipos de severidade presentes: CRITICO, ALERTA e NORMAL

### Opção 5 - Matriz de leituras
Exibe uma matriz com as principais variáveis energéticas ao longo de todos os turnos:

| Coluna | Descrição |
|--------|-----------|
| `solar_kw` | Geração solar no turno |
| `eolico_kw` | Geração eólica no turno |
| `bateria_pct` | Nível da bateria em % |
| `consumo_total_kw` | Consumo agregado de todos os sistemas |
| `temperatura` | Temperatura externa em °C |

---

## Geração dos dados simulados

Os dados são gerados por `src/gerador.py` e salvos em dois arquivos na pasta `data/`:

### `data/dados.csv` - telemetria por turno
Cada linha representa um turno de operação. O gerador simula:

- **Tempestade de areia**: probabilidade de 25 % por turno limpo, 60 % de continuação se já ativa. Durante a tempestade: painéis solares desligados ou com geração mínima, radiação alta/muito alta, comunicação comprometida (qualidade 30–55 %), módulos de ciência e mineração em FALHA
- **Geração solar**: proporcional ao número de painéis ativos (0–8) × eficiência aleatória
- **Geração eólica**: proporcional à velocidade do vento × fator de eficiência aleatório
- **Bateria**: atualizada a cada turno com `bateria + (geração − consumo) × 0.4`, limitada entre 5 kWh e 120 kWh
- **Inconsistência proposital**: o gerador sempre injeta uma contradição - geração solar > 0 durante tempestade, ou módulo em FALHA com consumo registrado

### `data/eventos.csv` - log de pré-missão
Gerado junto com `dados.csv`, contém 4 eventos fixos de pré-missão (turno 0) que registram ações realizadas antes do início da monitoração: reinicialização do ECLSS, falha de sensor corrigida, definição de prioridades e modo de economia de calibração.

---

## Exemplo de entrada e saída

> Os dados são simulados aleatoriamente pelo `src/gerador.py` a cada execução. O exemplo abaixo é de uma execução de referência - os valores numéricos variam, mas o formato e o comportamento do sistema são sempre os mesmos.

### Entrada (trecho de `data/dados.csv` - exemplo de turno com tempestade)

| turno | solar_kw | eolico_kw | bateria_atual | bateria_max | tempestade | radiacao | qualidade_com |
|------:|---------:|----------:|-------------:|------------:|-----------:|:---------|-------------:|
|     3 |       12 |        38 |           47 |         120 |          1 | alta     |            41 |

### Saída do sistema (opção 1 - estado da colônia, exemplo com tempestade ativa)

```
--------------------------------------
  [1] ESTADO DA COLONIA - TURNO ATUAL
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
  [CRITICO] Tempestade de areia - paineis solares desligados.
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

## Relatório

[Relatório Global Solution (PDF)](docs/Relatorio%20Global%20Solution.pdf)

---

## Link do vídeo no YouTube

[Assistir ao vídeo de apresentação](https://youtu.be/Hs87NC-OW2g)

> O link também está disponível em [`docs/link_video.txt`](docs/link_video.txt).

---

## Conclusões e aprendizados

O desenvolvimento da primeira fase do Global Solution evidenciou como a escolha de estrutura de dados impacta diretamente a eficiência do sistema: o uso de dicionário para o catálogo de módulos reduziu a complexidade de busca de O(n) para O(1), enquanto a fila e a pilha tornaram o fluxo de alertas determinístico e auditável.

A implementação da regressão linear sem bibliotecas reforçou a compreensão do algoritmo de mínimos quadrados e revelou como dados de vento e geração possuem correlação forte, permitindo previsões úteis mesmo com histórico reduzido (6 turnos).

A inconsistência intencional (solar ativo durante tempestade) demonstrou a importância de validações cruzadas entre variáveis correlacionadas - prática essencial em sistemas críticos onde sensores podem falhar silenciosamente.

Por fim, o projeto aproximou os conceitos das três fases do curso (sistemas numéricos, lógica booleana, estruturas de dados e análise simples) de um cenário realista, tornando tangível como a computação sustenta operações de alto risco.
