import csv
import os
import random

DADOS_PATH   = os.path.join(os.path.dirname(__file__), "..", "data", "dados.csv")
EVENTOS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "eventos.csv")

NOMES_MODULOS = {
    19: "MOD-EN-001", 20: "MOD-SV-002", 21: "MOD-HB-003",
    22: "MOD-LG-006", 23: "MOD-SC-004", 24: "MOD-MN-005",
}
SENSORES = ["pressao", "temperatura", "radiacao", "oxigenio", "velocidade do vento"]


def gerar_eventos(turnos):
    eventos = []

    # Eventos fixos de pre-missao (turno 0)
    eventos.append({"turno": 0, "tipo": "REINICIALIZACAO", "severidade": "NORMAL",
                    "descricao": "Sistema ECLSS reinicializado apos atualizacao de firmware - modulo operacional"})
    eventos.append({"turno": 0, "tipo": "MUDANCA_PRIORIDADE", "severidade": "ALERTA",
                    "descricao": "Prioridade operacional definida: energia (P1), suporte a vida (P2) e habitat (P3) em nivel maximo"})

    modulos_anterior = None
    for linha in turnos:
        turno      = linha[0]
        tempestade = linha[13]
        geracao    = linha[1] + linha[3]
        consumo    = sum(linha[7:12])
        bat_pct    = round(linha[5] / linha[6] * 100, 1)
        modulos    = linha[19:25]

        # Tempestade: falha de sensor aleatoria (60% de chance)
        if tempestade and random.random() < 0.6:
            sensor = random.choice(SENSORES)
            eventos.append({"turno": turno, "tipo": "FALHA_SENSOR", "severidade": "ALERTA",
                            "descricao": f"Falha de sensor de {sensor} durante tempestade de areia - leitura suspensa"})

        # Consumo supera geracao: modo de economia ativado
        if consumo > geracao:
            eventos.append({"turno": turno, "tipo": "MODO_ECONOMIA", "severidade": "ALERTA",
                            "descricao": f"Modo de economia ativado - consumo ({consumo} kW) supera geracao ({geracao:.0f} kW)"})

        # Bateria critica: alerta de modo de emergencia
        if bat_pct < 20:
            eventos.append({"turno": turno, "tipo": "MODO_ECONOMIA", "severidade": "CRITICO",
                            "descricao": f"Modo de emergencia ativado - bateria em {bat_pct:.0f}%, desligando sistemas nao essenciais"})

        # Modulo se recuperou em relacao ao turno anterior: reinicializacao
        if modulos_anterior:
            for idx, (ant, cur) in enumerate(zip(modulos_anterior, modulos)):
                if ant == 0 and cur == 1:
                    mod_id = list(NOMES_MODULOS.values())[idx]
                    eventos.append({"turno": turno, "tipo": "REINICIALIZACAO", "severidade": "NORMAL",
                                    "descricao": f"Modulo {mod_id} reinicializado com sucesso apos falha no turno anterior"})

        modulos_anterior = modulos

    return sorted(eventos, key=lambda e: e["turno"])

CABECALHO = [
    "turno", "solar_kw", "paineis_ativos", "eolico_kw", "velocidade_vento",
    "bateria_atual", "bateria_max", "consumo_sv", "consumo_hab", "consumo_log",
    "consumo_cien", "consumo_min", "temperatura", "tempestade",
    "radiacao", "qualidade_com", "oxigenio_pct", "temp_interna", "com_ativa",
    "mod_en001", "mod_sv002", "mod_hb003", "mod_lg006", "mod_sc004", "mod_mn005",
]

CAPACIDADE_BATERIA = 120
SOLAR_MAX_KW       = 80
SOLAR_POR_PAINEL   = 10


def gerar_turno(turno, bateria, tempestade_anterior):
    # Tempestade: maior chance de continuar se ja estava ativa
    prob_tempestade = 0.6 if tempestade_anterior else 0.25
    tempestade = 1 if random.random() < prob_tempestade else 0

    if tempestade:
        paineis    = random.randint(0, 1)
        solar_kw   = round(paineis * SOLAR_POR_PAINEL * random.uniform(0.0, 0.3), 1)
        radiacao   = random.choice(["alta", "muito_alta"])
        qual_com   = random.randint(30, 55)
        com_ativa  = 0
    else:
        paineis    = random.randint(4, 8)
        solar_kw   = round(paineis * SOLAR_POR_PAINEL * random.uniform(0.7, 1.0), 1)
        radiacao   = "normal"
        qual_com   = random.randint(72, 95)
        com_ativa  = 1

    vento_kmh  = round(random.uniform(10, 60), 1)
    eolico_kw  = round(vento_kmh * random.uniform(0.4, 0.8), 1)

    consumo_sv  = 23
    consumo_hab = random.randint(13, 20)
    consumo_log = random.randint(5, 12)
    consumo_cien = 0 if tempestade else random.randint(10, 30)
    consumo_min  = 0 if tempestade else random.randint(15, 35)

    geracao = solar_kw + eolico_kw
    consumo = consumo_sv + consumo_hab + consumo_log + consumo_cien + consumo_min
    nova_bateria = round(min(CAPACIDADE_BATERIA, max(5.0, bateria + (geracao - consumo) * 0.4)), 1)

    temperatura   = round(random.uniform(-65, -20), 1)
    oxigenio_pct  = round(random.uniform(20.3, 21.0), 1)
    temp_interna  = round(random.uniform(20.5, 22.5), 1)

    mod_sc004 = 0 if tempestade and random.random() < 0.5 else 1
    mod_mn005 = 0 if tempestade else 1

    return nova_bateria, [
        turno, solar_kw, paineis, eolico_kw, vento_kmh,
        nova_bateria, CAPACIDADE_BATERIA,
        consumo_sv, consumo_hab, consumo_log, consumo_cien, consumo_min,
        temperatura, tempestade, radiacao, qual_com,
        oxigenio_pct, temp_interna, com_ativa,
        1, 1, 1, 1, mod_sc004, mod_mn005,
    ]


def injetar_inconsistencia(turnos):

    for linha in turnos:
        if linha[13] == 1 and linha[1] == 0:   # tempestade=1 e solar_kw=0
            linha[1] = round(random.uniform(5, 15), 1)  # solar residual "impossivel"
            return

    for linha in turnos:
        if linha[23] == 0 and linha[10] == 0:   # mod_sc004=0 e consumo_cien=0
            linha[10] = random.randint(15, 28)
            return


def gerar_csv(n_turnos=6, seed=None):
    if seed is not None:
        random.seed(seed)

    bateria    = round(random.uniform(70, 95), 1)
    tempestade = 0
    turnos     = []

    for t in range(1, n_turnos + 1):
        bateria, linha = gerar_turno(t, bateria, tempestade)
        tempestade = linha[13]
        turnos.append(linha)

    injetar_inconsistencia(turnos)

    with open(DADOS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CABECALHO)
        writer.writerows(turnos)

    with open(EVENTOS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["turno", "tipo", "severidade", "descricao"])
        writer.writeheader()
        writer.writerows(gerar_eventos(turnos))

    print(f"CSV gerado com {n_turnos} turnos em: {DADOS_PATH}")
    for linha in turnos:
        print(f"  Turno {linha[0]:>2} | solar={linha[1]:>5} kW | eolico={linha[3]:>5} kW | "
              f"bateria={linha[5]:>5} kWh | tempestade={linha[13]}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    gerar_csv(n_turnos=n)
