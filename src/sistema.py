import csv
import os


DADOS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dados.csv")


# -----------------------------------------------------------
# 1. MODULOS DA COLONIA 
#    Dicionario indexado por ID para acesso rapido O(1)
# ----------------------------------------------------------- 

MODULOS = {
    "MOD-EN-001": {"nome": "Geradores + Paineis Solares",          "prioridade": 1, "criticidade": "Alta"},
    "MOD-SV-002": {"nome": "Sistemas de Suporte a Vida (ECLSS)",   "prioridade": 2, "criticidade": "Alta"},
    "MOD-HB-003": {"nome": "Modulos Inflaveis BEAM (Habitat)",     "prioridade": 3, "criticidade": "Alta"},
    "MOD-LG-006": {"nome": "Logistica e Suprimentos",              "prioridade": 4, "criticidade": "Baixa"},
    "MOD-SC-004": {"nome": "Sensores Cientificos",                 "prioridade": 5, "criticidade": "Media"},
    "MOD-MN-005": {"nome": "Mineracao e Producao ISRU",            "prioridade": 6, "criticidade": "Media"},
}


# -----------------------------------------------------------
# 2. LOG DE EVENTOS  (NOVO — 10 registros pre-carregados)
#    Representa o historico operacional da colonia.
#    Turno 4 contem a inconsistencia proposital detectada.
# -----------------------------------------------------------

LOG_EVENTOS = [
    {"turno": 1, "tipo": "ALERTA",        "severidade": "CRITICO", "descricao": "Tempestade de areia detectada — paineis solares desligados"},
    {"turno": 1, "tipo": "MODO",          "severidade": "CRITICO", "descricao": "Modo EMERGENCIA ativado — colonia operando 100% em bateria"},
    {"turno": 1, "tipo": "ALERTA",        "severidade": "CRITICO", "descricao": "Qualidade de comunicacao: 45% — enlace com Terra comprometido"},
    {"turno": 2, "tipo": "NORMAL",        "severidade": "NORMAL",  "descricao": "Tempestade encerrada — paineis solares religados"},
    {"turno": 3, "tipo": "ALERTA",        "severidade": "ALERTA",  "descricao": "Bateria em 29% — abaixo do limite de seguranca (30%)"},
    {"turno": 3, "tipo": "MODO",          "severidade": "ALERTA",  "descricao": "Modo ECONOMIA ativado — mineracao suspensa temporariamente"},
    {"turno": 4, "tipo": "INCONSISTENCIA","severidade": "CRITICO", "descricao": "ANOMALIA: consumo suporte_vida = 0 kW — leitura de sensor invalida"},
    {"turno": 4, "tipo": "ALERTA",        "severidade": "ALERTA",  "descricao": "Nova tempestade — qualidade de comunicacao: 52%"},
    {"turno": 5, "tipo": "ALERTA",        "severidade": "ALERTA",  "descricao": "Bateria em 20% — proximo ao limite critico de operacao"},
    {"turno": 6, "tipo": "NORMAL",        "severidade": "NORMAL",  "descricao": "Colonia estabilizada — todos os sistemas dentro do esperado"},
]


# -------------------------------------------------------
# 3. FILA DE ALERTAS  (NOVO)
#    Alertas sao enfileirados por ordem de chegada e
#    processados do mais critico para o menos critico
#    via ordenacao por severidade antes de exibir.
# -------------------------------------------------------

fila_alertas = []

ORDEM_SEVERIDADE = {"CRITICO": 0, "ALERTA": 1, "NORMAL": 2}

def enfileirar_alerta(severidade, descricao):
    fila_alertas.append({"severidade": severidade, "descricao": descricao})

def processar_fila_alertas():
    if not fila_alertas:
        print("  Nenhum alerta pendente na fila.")
        return
    ordenados = sorted(fila_alertas, key=lambda a: ORDEM_SEVERIDADE[a["severidade"]])
    print(f"\n  {'SEVERIDADE':<10}  DESCRICAO")
    print("  " + "-" * 70)
    for alerta in ordenados:
        print(f"  {alerta['severidade']:<10}  {alerta['descricao']}")
    fila_alertas.clear()


# ---------------------------------------------------------
# 4. PILHA DE EVENTOS CRITICOS
#    Registra LIFO os ultimos eventos criticos analisados.
#    Permite revisar a sequencia mais recente de falhas.
# ---------------------------------------------------------

pilha_criticos = []

def empilhar_critico(descricao):
    pilha_criticos.append(descricao)

def exibir_pilha_criticos():
    if not pilha_criticos:
        print("  Nenhum evento critico registrado.")
        return
    print(f"\n  Ultimos {len(pilha_criticos)} evento(s) critico(s) — ordem LIFO (mais recente primeiro):")
    for evento in reversed(pilha_criticos):
        print(f"    >> {evento}")


# -------------------------------
# 5. CARREGAMENTO DE DADOS
# -------------------------------

def carregar_dados():
    if not os.path.exists(DADOS_PATH):
        raise FileNotFoundError(f"Arquivo nao encontrado: {DADOS_PATH}")
    historico = []
    with open(DADOS_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            historico.append({
                "turno": int(row["turno"]),
                "dados": {
                    "energia": {
                        "solar":   {"geracao_kw": float(row["solar_kw"]),  "paineis_ativos": int(row["paineis_ativos"])},
                        "eolico":  {"geracao_kw": float(row["eolico_kw"]), "velocidade_vento": float(row["velocidade_vento"])},
                        "bateria": {"carga_atual": float(row["bateria_atual"]), "capacidade_max": float(row["bateria_max"])},
                    },
                    "consumo": {
                        "suporte_vida": float(row["consumo_sv"]),
                        "habitacao":    float(row["consumo_hab"]),
                        "logistica":    float(row["consumo_log"]),
                        "ciencia":      float(row["consumo_cien"]),
                        "mineracao":    float(row["consumo_min"]),
                    },
                    "clima": {
                        "temperatura":           float(row["temperatura"]),
                        "vento_kmh":             float(row["vento_kmh"]),
                        "tempestade_areia":      row["tempestade"] == "1",
                        "radiacao":              row["radiacao"],
                        "qualidade_comunicacao": float(row["qualidade_com"]),
                    },
                    "habitat": {
                        "oxigenio_pct":       float(row["oxigenio_pct"]),
                        "temperatura_interna": float(row["temp_interna"]),
                        "comunicacao_ativa":  int(row["com_ativa"]),
                    },
                    "modulos": {
                        "MOD-EN-001": int(row["mod_en001"]),
                        "MOD-SV-002": int(row["mod_sv002"]),
                        "MOD-HB-003": int(row["mod_hb003"]),
                        "MOD-LG-006": int(row["mod_lg006"]),
                        "MOD-SC-004": int(row["mod_sc004"]),
                        "MOD-MN-005": int(row["mod_mn005"]),
                    },
                },
            })
    return historico


# -----------------------------------------------------------
# 6. DETECCAO DE INCONSISTENCIAS
#    Regra: suporte_vida nunca pode ser 0 — e um sistema
#    critico com prioridade maxima e consumo constante.
#    Turno 4 contem esta inconsistencia propositalmente.
# -----------------------------------------------------------

def detectar_inconsistencias(historico):
    inconsistencias = []
    for registro in historico:
        turno = registro["turno"]
        sv = registro["dados"]["consumo"]["suporte_vida"]
        if sv == 0:
            inconsistencias.append(
                f"Turno {turno}: suporte_vida = 0 kW — impossivel, sistema critico sempre ativo"
            )
        geracao = (registro["dados"]["energia"]["solar"]["geracao_kw"] +
                   registro["dados"]["energia"]["eolico"]["geracao_kw"])
        if geracao > 130:
            inconsistencias.append(
                f"Turno {turno}: geracao total = {geracao} kW — acima da capacidade instalada"
            )
    return inconsistencias


# -----------------------------------------------------------
# 7. MATRIZ DE LEITURAS
#    Lista de listas: matriz[turno][variavel]
#    Linhas = turnos (1-6), Colunas = variaveis de energia
# -----------------------------------------------------------

COLUNAS_MATRIZ = ["solar_kw", "eolico_kw", "bateria_pct", "consumo_total_kw", "temperatura"]

def montar_matriz(historico):
    matriz = []
    for registro in historico:
        d = registro["dados"]
        linha = [
            d["energia"]["solar"]["geracao_kw"],
            d["energia"]["eolico"]["geracao_kw"],
            round((d["energia"]["bateria"]["carga_atual"] / d["energia"]["bateria"]["capacidade_max"]) * 100, 1),
            sum(d["consumo"].values()),
            d["clima"]["temperatura"],
        ]
        matriz.append(linha)
    return matriz

def exibir_matriz(matriz):
    cabecalho = f"  {'TURNO':>6}  " + "  ".join(f"{c:>16}" for c in COLUNAS_MATRIZ)
    print(cabecalho)
    print("  " + "-" * len(cabecalho))
    for i, linha in enumerate(matriz):
        valores = "  ".join(f"{v:>16}" for v in linha)
        print(f"  {i+1:>6}  {valores}")


# -----------------------------------------------------------
# 8. PORTAS LOGICAS
#    AND: condicao OK somente se TODOS os parametros OK
#    OR:  alerta ativo se QUALQUER parametro critico
#    NOT: inverte o resultado da porta OR
# -----------------------------------------------------------

def porta_and(bateria_ok, comunicacao_ok, modulos_criticos_ok):
    return bateria_ok and comunicacao_ok and modulos_criticos_ok

def porta_or(energia_baixa, comunicacao_falha):
    return energia_baixa or comunicacao_falha

def porta_not(resultado_or):
    return not resultado_or


# -----------------------------------------------------
# 9. TABELA DE STATUS DOS MODULOS
#    Exibe o status binario (0/1) de cada modulo como
#    NORMAL / FALHA com prioridade operacional.
# -----------------------------------------------------

def exibir_tabela_modulos(colonia):
    status_bin = colonia["modulos"]
    print(f"\n  {'ID':<12}  {'NOME':<42}  {'PRIO':>4}  {'STATUS':<8}  {'CRITICIDADE'}")
    print("  " + "-" * 85)

    modulos_ordenados = sorted(MODULOS.items(), key=lambda x: x[1]["prioridade"])
    for mod_id, info in modulos_ordenados:
        bin_val = status_bin.get(mod_id, 0)
        status_str = "NORMAL" if bin_val == 1 else "FALHA"
        print(f"  {mod_id:<12}  {info['nome']:<42}  {info['prioridade']:>4}  {status_str:<8}  {info['criticidade']}")


# -------------------------------------------------------------------
# 10. REGRAS LOGICAS + CLASSIFICACAO
#
#     Expressao booleana principal do diagnostico:
#     EMERGENCIA = (reserva < 20 AND consumo > geracao) OR tempestade
#     NORMAL     = NOT(EMERGENCIA) AND NOT(consumo > geracao)
# -------------------------------------------------------------------

def decisao_automatica(geracao, consumo, reserva_pct, tempestade, qualidade_com):
    reserva_critica   = reserva_pct < 20
    consumo_alto      = consumo > geracao
    com_comprometida  = qualidade_com < 60

    # Porta AND: emergencia maxima requer reserva critica E consumo alto
    emergencia_energia = porta_and(reserva_critica, consumo_alto, True)

    # Porta OR: alerta se energia baixa OU comunicacao falha
    ha_alerta = porta_or(consumo_alto, com_comprometida)

    # Porta NOT: sem_alerta so se nao ha nenhuma condicao de alerta
    sem_alerta = porta_not(ha_alerta)

    if emergencia_energia or tempestade:
        nivel = "CRITICO"
        if tempestade:
            print("  [CRITICO] Tempestade de areia — paineis solares desligados.")
            print("            Sistema operando em reserva de bateria.")
        if emergencia_energia:
            print("  [CRITICO] Reserva critica e consumo acima da geracao.")
            print("            Mineracao: DESLIGADA. Ciencia: DESLIGADA.")
        print("            Suporte a vida mantido (prioridade maxima).")
        enfileirar_alerta("CRITICO", "Emergencia energetica ou tempestade detectada")
        empilhar_critico(f"Emergencia: reserva={reserva_pct:.0f}% | consumo={consumo}kW | geracao={geracao}kW | tempestade={tempestade}")

    elif ha_alerta:
        nivel = "ALERTA"
        if consumo_alto:
            print("  [ALERTA]  Consumo maior que geracao.")
            print("            Reduzir sistemas nao essenciais.")
            enfileirar_alerta("ALERTA", f"Consumo ({consumo} kW) acima da geracao ({geracao} kW)")
            empilhar_critico(f"Alerta energia: consumo={consumo}kW > geracao={geracao}kW")
        if com_comprometida:
            print(f"  [ALERTA]  Qualidade de comunicacao: {qualidade_com}% — abaixo de 60%.")
            enfileirar_alerta("ALERTA", f"Comunicacao comprometida: {qualidade_com}%")

    elif geracao > consumo * 1.2 and sem_alerta:
        nivel = "NORMAL"
        print("  [NORMAL]  Geracao excede consumo em 20%+.")
        print("            Armazenar excedente na bateria.")

    else:
        nivel = "NORMAL"
        print("  [NORMAL]  Operacao dentro dos parametros esperados.")

    return nivel


# -----------------------
# 11. ANALISE DE ENERGIA
# -----------------------

def analisar_energia(geracao, consumo, reserva_kwh, consumo_por_sistema):
    cobertura = (geracao / consumo * 100) if consumo > 0 else 0
    autonomia = (reserva_kwh / consumo) if consumo > 0 else 0
    print(f"  Geracao cobre {cobertura:.1f}% do consumo.")
    print(f"  Reserva sustenta a colonia por {autonomia:.1f} hora(s).")
    print("\n  Consumo por sistema:")
    for sistema, valor in consumo_por_sistema.items():
        pct = (valor / consumo * 100) if consumo > 0 else 0
        print(f"    {sistema:<15}: {valor:>3} kW  ({pct:.1f}%)")


# ---------------------
# 12. REGRESSAO LINEAR
# ---------------------

def regressao_linear(x_lista, y_lista, x_novo):
    n   = len(x_lista)
    sx  = sum(x_lista)
    sy  = sum(y_lista)
    sxy = sum(x_lista[i] * y_lista[i] for i in range(n))
    sx2 = sum(x_lista[i] ** 2         for i in range(n))
    denom = (n * sx2 - sx ** 2)
    if denom == 0:
        return round(sy / n, 1)
    a = (n * sxy - sx * sy) / denom
    b = (sy - a * sx) / n
    return round(a * x_novo + b, 1)

def prever_vento_turno(historico, turno_novo):
    x = [r["turno"]                                              for r in historico]
    y = [r["dados"]["energia"]["eolico"]["velocidade_vento"]     for r in historico]
    return regressao_linear(x, y, turno_novo)

def prever_geracao_eolica(historico, vento_novo):
    x = [r["dados"]["energia"]["eolico"]["velocidade_vento"] for r in historico]
    y = [r["dados"]["energia"]["eolico"]["geracao_kw"]        for r in historico]
    return regressao_linear(x, y, vento_novo)

def prever_consumo_turno(historico, turno_novo):
    x = [r["turno"]                          for r in historico]
    y = [sum(r["dados"]["consumo"].values()) for r in historico]
    return regressao_linear(x, y, turno_novo)


# --------------------
# 13. OPCOES DO MENU
# --------------------

def opcao_visualizar_colonia(historico):
    print("\n--------------------------------------")
    print("  [1] ESTADO DA COLONIA — TURNO ATUAL")
    print("----------------------------------------")

    registro = historico[-1]
    turno    = registro["turno"]
    d        = registro["dados"]

    geracao  = d["energia"]["solar"]["geracao_kw"] + d["energia"]["eolico"]["geracao_kw"]
    consumo  = sum(d["consumo"].values())
    bateria  = d["energia"]["bateria"]["carga_atual"]
    cap_max  = d["energia"]["bateria"]["capacidade_max"]
    reserva  = (bateria / cap_max) * 100
    temp     = d["clima"]["tempestade_areia"]
    qual_com = d["clima"]["qualidade_comunicacao"]

    print(f"\n  Turno atual        : {turno}")
    print(f"  Geracao total      : {geracao} kW  (solar: {d['energia']['solar']['geracao_kw']} + eolico: {d['energia']['eolico']['geracao_kw']})")
    print(f"  Consumo total      : {consumo} kW")
    print(f"  Bateria            : {reserva:.0f}%  ({bateria}/{cap_max} kWh)")
    print(f"  Temperatura ext.   : {d['clima']['temperatura']} C")
    print(f"  Tempestade areia   : {'SIM' if temp else 'NAO'}")
    print(f"\n  Habitat:")
    print(f"    Oxigenio         : {d['habitat']['oxigenio_pct']}%")
    print(f"    Temp. interna    : {d['habitat']['temperatura_interna']} C")
    print(f"    Comunicacao      : {'ATIVA' if d['habitat']['comunicacao_ativa'] else 'INATIVA'}")
    print(f"  Radiacao           : {d['clima']['radiacao']}")
    print(f"  Comunicacao        : {qual_com}%")

    print("\n--- STATUS DOS MODULOS ---")
    exibir_tabela_modulos(d)

    print("\n--- DIAGNOSTICO AUTOMATICO ---")
    decisao_automatica(geracao, consumo, reserva, temp, qual_com)

    print("\n--- ANALISE DE ENERGIA ---")
    analisar_energia(geracao, consumo, bateria, d["consumo"])

    print("\n--- INCONSISTENCIAS DETECTADAS ---")
    incons = detectar_inconsistencias(historico)
    if incons:
        for i in incons:
            print(f"  !! {i}")
    else:
        print("  Nenhuma inconsistencia detectada.")

    print("\n--- ALERTAS PENDENTES ---")
    processar_fila_alertas()

    print("\n--- EVENTOS CRITICOS (PILHA LIFO) ---")
    exibir_pilha_criticos()

    print("\n-----------------------------------------------------------")


def opcao_consultar_modulo(historico):
    print("\n-----------------------")
    print("  [2] CONSULTAR MODULO")
    print("-------------------------")
    colonia = historico[-1]["dados"]
    exibir_tabela_modulos(colonia)
    print()
    mod_id = input("  Digite o ID do modulo (ex: MOD-EN-001): ").strip().upper()
    if mod_id not in MODULOS:
        print("  ID nao encontrado.")
        return
    info   = MODULOS[mod_id]
    status = colonia["modulos"].get(mod_id, 0)
    print(f"\n  ID           : {mod_id}")
    print(f"  Nome         : {info['nome']}")
    print(f"  Prioridade   : {info['prioridade']}")
    print(f"  Criticidade  : {info['criticidade']}")
    print(f"  Status atual : {'NORMAL (1)' if status == 1 else 'FALHA (0)'}")

    historico_modulo = [
        (r["turno"], r["dados"]["modulos"].get(mod_id, 0))
        for r in historico
    ]
    print(f"\n  Historico de status por turno:")
    for turno, s in historico_modulo:
        marcador = "OK " if s == 1 else "FALHA"
        print(f"    Turno {turno}: {marcador}")
    print("-----------------------------------------------------------")


def opcao_executar_previsao(historico):
    print("\n-----------------------------------------------------------")
    print("  [3] PREVISAO POR REGRESSAO LINEAR")
    print("      (Minimos quadrados — sem bibliotecas externas)")
    print("-----------------------------------------------------------")

    turno_proximo = historico[-1]["turno"] + 1

    print(f"\n  Previsao automatica para o turno {turno_proximo}:")
    print(f"  Dados historicos utilizados: turnos 1 a {historico[-1]['turno']}\n")

    # 1. Prever vento do proximo turno pela tendencia historica
    vento_previsto = prever_vento_turno(historico, turno_proximo)
    vento_previsto = max(0, vento_previsto)

    # 2. Usar vento previsto para estimar geracao eolica
    gen_eolica_prevista = prever_geracao_eolica(historico, vento_previsto)
    gen_eolica_prevista = max(0, gen_eolica_prevista)

    # 3. Prever consumo total do proximo turno
    cons_previsto = prever_consumo_turno(historico, turno_proximo)
    cons_previsto = max(0, cons_previsto)

    # Solar: mantém média histórica como estimativa conservadora
    solar_medio = sum(r["dados"]["energia"]["solar"]["geracao_kw"] for r in historico) / len(historico)
    geracao_total_prevista = solar_medio + gen_eolica_prevista

    print(f"  -- Vento --")
    print(f"  Tendencia historica → vento previsto : {vento_previsto:.1f} km/h")
    print(f"\n  -- Geracao eolica --")
    print(f"  Vento previsto ({vento_previsto:.1f} km/h) → geracao eolica : {gen_eolica_prevista:.1f} kW")
    print(f"  Solar (media historica)              : {solar_medio:.1f} kW")
    print(f"  Geracao total prevista               : {geracao_total_prevista:.1f} kW")
    print(f"\n  -- Consumo --")
    print(f"  Tendencia historica → consumo previsto: {cons_previsto:.1f} kW")

    print(f"\n  -- Impacto na decisao --")
    bateria = historico[-1]["dados"]["energia"]["bateria"]["carga_atual"]

    if cons_previsto > geracao_total_prevista:
        delta = cons_previsto - geracao_total_prevista
        horas = bateria / delta if delta > 0 else float("inf")
        print(f"  ALERTA: consumo previsto ({cons_previsto:.1f} kW) supera geracao prevista ({geracao_total_prevista:.1f} kW).")
        print(f"  Deficit de {delta:.1f} kW — reserva ({bateria:.0f} kWh) se esgotaria em {horas:.1f} hora(s).")
        print("  Recomendacao: reduzir consumo de mineracao e ciencia antes do proximo turno.")
        enfileirar_alerta("ALERTA", f"Previsao T{turno_proximo}: consumo {cons_previsto:.1f} kW > geracao {geracao_total_prevista:.1f} kW")
    else:
        excedente = geracao_total_prevista - cons_previsto
        print(f"  OK: geracao prevista ({geracao_total_prevista:.1f} kW) cobre consumo previsto ({cons_previsto:.1f} kW).")
        print(f"  Excedente estimado de {excedente:.1f} kW — armazenar na bateria.")
    print("-----------------------------------------------------------")


def opcao_simular_cenario(historico):
    print("\n---------------------------------------")
    print("  [4] SIMULACAO DE CENARIO OPERACIONAL")
    print("-----------------------------------------")
    print("\n  Cenarios disponiveis:")
    print("    [A] Tempestade de areia severa")
    print("    [B] Falha no modulo de energia (MOD-EN-001)")
    print("    [C] Bateria critica (reserva < 15%)")

    opcao = input("\n  Escolha o cenario (A/B/C): ").strip().upper()

    if opcao == "A":
        print("\n  SIMULANDO: Tempestade de areia severa")
        print("  Geracao solar: 0 kW (paineis desligados)")
        geracao_sim = historico[-1]["dados"]["energia"]["eolico"]["geracao_kw"]
        consumo_sim = sum(historico[-1]["dados"]["consumo"].values())
        reserva_sim = (historico[-1]["dados"]["energia"]["bateria"]["carga_atual"] /
                       historico[-1]["dados"]["energia"]["bateria"]["capacidade_max"]) * 100
        print(f"  Geracao disponivel (so eolico): {geracao_sim} kW")
        print(f"  Consumo atual: {consumo_sim} kW")
        print("\n  Diagnostico:")
        decisao_automatica(geracao_sim, consumo_sim, reserva_sim, True, 40)

    elif opcao == "B":
        print("\n  SIMULANDO: Falha em MOD-EN-001 (Geradores + Paineis Solares)")
        print("  Geracao solar e eolica zerada — modulo de energia inativo.")
        geracao_sim = 0
        consumo_sim = sum(historico[-1]["dados"]["consumo"].values())
        reserva_sim = (historico[-1]["dados"]["energia"]["bateria"]["carga_atual"] /
                       historico[-1]["dados"]["energia"]["bateria"]["capacidade_max"]) * 100
        bateria_kwh = historico[-1]["dados"]["energia"]["bateria"]["carga_atual"]
        autonomia   = bateria_kwh / consumo_sim if consumo_sim > 0 else 0
        print(f"  Reserva de bateria: {reserva_sim:.0f}% ({bateria_kwh} kWh)")
        print(f"  Autonomia estimada: {autonomia:.1f} hora(s)")
        print("\n  Diagnostico:")
        decisao_automatica(geracao_sim, consumo_sim, reserva_sim, False, 80)
        enfileirar_alerta("CRITICO", "Simulacao: MOD-EN-001 em falha — autonomia limitada")
        empilhar_critico("SIMULACAO: Falha MOD-EN-001 — geracao zerada")

    elif opcao == "C":
        print("\n  SIMULANDO: Bateria critica (reserva = 12%)")
        geracao_sim = (historico[-1]["dados"]["energia"]["solar"]["geracao_kw"] +
                       historico[-1]["dados"]["energia"]["eolico"]["geracao_kw"])
        consumo_sim = sum(historico[-1]["dados"]["consumo"].values())
        reserva_sim = 12.0
        print(f"  Geracao: {geracao_sim} kW | Consumo: {consumo_sim} kW | Bateria: 12%")
        print("\n  Diagnostico:")
        decisao_automatica(geracao_sim, consumo_sim, reserva_sim, False, 80)

    else:
        print("  Opcao invalida.")
        return

    print("\n--- ALERTAS GERADOS ---")
    processar_fila_alertas()
    print("\n--- EVENTOS CRITICOS ---")
    exibir_pilha_criticos()
    print("-----------------------------------------------------------")


def opcao_historico_eventos():
    print("\n----------------------------")
    print("  LOG DE EVENTOS DA COLONIA")
    print("------------------------------")
    print(f"\n  {'TURNO':>6}  {'TIPO':<15}  {'SEVERIDADE':<10}  DESCRICAO")
    print("  " + "-" * 80)
    for ev in LOG_EVENTOS:
        print(f"  {ev['turno']:>6}  {ev['tipo']:<15}  {ev['severidade']:<10}  {ev['descricao']}")
    print("-----------------------------------------------------------")


def opcao_matriz_leituras(historico):
    print("\n------------------------------------------")
    print("  MATRIZ DE LEITURAS (turnos x variaveis)")
    print("--------------------------------------------\n")
    matriz = montar_matriz(historico)
    exibir_matriz(matriz)
    print("-----------------------------------------------------------")


# -----------------------------------------------------------
# 14. MENU PRINCIPAL
# -----------------------------------------------------------

def menu_principal(historico):
    while True:
        print("\n-------------------------------------")
        print("  SGCE — SISTEMA DE MONITORAMENTO")
        print("       COLONIA AURORA SIGER")
        print("-------------------------------------")
        print("  [1] Visualizar estado da colonia")
        print("  [2] Consultar modulo especifico")
        print("  [3] Executar previsao (regressao linear)")
        print("  [4] Simular cenario operacional")
        print("  [5] Exibir log de eventos")
        print("  [6] Exibir matriz de leituras")
        print("  [0] Sair")
        print("-------------------------------------")
        opcao = input("  Escolha uma opcao: ").strip()

        if opcao == "1":
            opcao_visualizar_colonia(historico)
        elif opcao == "2":
            opcao_consultar_modulo(historico)
        elif opcao == "3":
            opcao_executar_previsao(historico)
        elif opcao == "4":
            opcao_simular_cenario(historico)
        elif opcao == "5":
            opcao_historico_eventos()
        elif opcao == "6":
            opcao_matriz_leituras(historico)
        elif opcao == "0":
            print("\n  Sistema encerrado.\n")
            break
        else:
            print("  Opcao invalida. Tente novamente.")


# -----------------------------------------------------------
# 15. ENTRADA PRINCIPAL
# -----------------------------------------------------------

if __name__ == "__main__":
    historico = carregar_dados()
    menu_principal(historico)
