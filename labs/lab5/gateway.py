#!/usr/bin/env python3
"""Gateway simulado do Bússola (Aula 3, Demonstração 4). Executar: make lab5-gateway SIMULACAO=<nome>.

O Bússola não chama o modelo direto: chama o gateway. O gateway lê labs/lab5/rotas.toml, aplica as
regras na ordem abaixo, chama o modelo (pelo RAG do Lab 2) e grava o registro. Cada decisão sai numa
linha, para a turma ver o caminho do pedido.

  1. identificação  departamento, sensibilidade e dado pessoal (CPF ou CNPJ na pergunta)
  2. cota           tokens usados no mês pelo departamento (RC-08)       APIM: llm-token-limit
  3. residência     dado pessoal ou departamento Regulado → Brasil (RC-03) APIM: set-backend-service
  4. complexidade   pergunta de análise → modelo grande                   Foundry: model router
  5. apelido        o nome que a aplicação usa → a versão do modelo       APIM: unified model API
  6. cache          pergunta parecida já respondida → resposta guardada   APIM: llm-semantic-cache-lookup
  7. modelo         a chamada; se o principal recusar, o reserva           APIM: backend pool + circuit breaker
  8. registro       uma linha por chamada (RC-05)                         APIM: ApiManagementGatewayLlmLog

Simulações: residencia, complexidade, cota, cache, reserva, apelido, registro (ou todas).
Simplificações declaradas: a rota "Brasil" é simulada (nenhum Claude roda no Brasil em 16/11/2026);
a complexidade é uma lista de palavras; o cache compara palavras, e não embeddings.
"""
import argparse
import json
import re
import sys
import time
import tomllib
import unicodedata
import uuid
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
sys.path.insert(0, str(RAIZ / "labs" / "lab2"))
sys.path.insert(0, str(RAIZ / "scripts"))
import cli_modelo  # noqa: E402
import corpus  # noqa: E402
import rodar  # noqa: E402

ESTADO = LAB / "estado"
DADO_PESSOAL = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b|\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
# Palavras que não ajudam a comparar perguntas (artigos, preposições, interrogativos).
VAZIAS = set("a o as os um uma e é de do da dos das em no na nos nas que qual quais quanto quando onde como "
             "para por com se ao à me diga sobre".split())
# Estimativa de tokens de um pedido, para a cota decidir antes de chamar: o RAG do Lab 2 gastou cerca
# de 1,8 mil tokens por pergunta (replay/lab2, 14/10/2026). O APIM estima pelo prompt da mesma forma.
ESTIMATIVA_TOKENS = 2000


def ler_rotas(caminho):
    return tomllib.loads(Path(caminho).read_text(encoding="utf-8"))


def mil(n):
    return f"{n:,}".replace(",", ".")


def palavras(texto):
    sem_acento = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return {p for p in re.findall(r"[a-z0-9-]+", sem_acento) if p not in VAZIAS and len(p) > 1}


def semelhanca(a, b):
    pa, pb = palavras(a), palavras(b)
    return len(pa & pb) / len(pa | pb) if pa | pb else 0.0


def ler_estado(nome, padrao):
    caminho = ESTADO / nome
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else padrao


def gravar_estado(nome, dados):
    ESTADO.mkdir(exist_ok=True)
    (ESTADO / nome).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def chamar_modelo(departamento, pergunta, modelo):
    """O Bússola de verdade atrás do gateway: o RAG do Lab 2, com o filtro de permissão."""
    p = {"departamento": departamento, "texto": pergunta}
    r, leu = rodar.perguntar(p, "rag", dict(rodar.PADRAO), corpus.carregar(), modelo, "claude")
    texto = r.estruturado.get("resposta", "") if isinstance(r.estruturado, dict) else r.texto
    return r, texto, leu.get("arquivos", [])


class Gateway:
    def __init__(self, rotas, falhar=(), chamar=chamar_modelo):
        self.rotas = rotas
        self.falhar = set(falhar)
        self.chamar = chamar

    def linha(self, regra, texto):
        print(f"  {regra:<13} {texto}", flush=True)

    def atender(self, departamento, pergunta, apelido="bussola-padrao", usuario="(não informado)"):
        """Atende um pedido do Bússola. Devolve (resposta, registro do gateway)."""
        r = self.rotas
        corr = uuid.uuid4().hex[:8]
        print(f'\nPedido {corr} · {departamento} · "{pergunta}"', flush=True)
        reg = {"correlacao": corr, "data": time.strftime("%Y-%m-%d %H:%M:%S"), "departamento_da_rota": departamento,
               "apelido": apelido, "modelo": "", "regiao": "global", "tokens_entrada": 0, "tokens_saida": 0,
               "custo_usd": 0.0, "cache": "não", "decisao": "", "pergunta_como_veio": pergunta}

        # 1. identificação
        sens = r["sensibilidade"].get(departamento, "Interno")
        pessoal = DADO_PESSOAL.search(pergunta)
        self.linha("identificação", f"departamento {departamento}, sensibilidade {sens}; dado pessoal: "
                   + (f"sim ({pessoal.group(0)})" if pessoal else "não"))

        # 2. cota
        cotas = ler_estado("cota.json", {})
        usado, limite = cotas.get(departamento, 0), r["cota"]["tokens"].get(departamento, 0)
        if usado + ESTIMATIVA_TOKENS > limite:
            self.linha("cota", f"{departamento} já usou {mil(usado)} de {mil(limite)} tokens no {r['cota']['periodo']}. "
                       f"Pedido RECUSADO (429): \"cota mensal esgotada; fale com o dono do orçamento\" (RC-08)")
            reg["decisao"] = "recusado pela cota (429)"
            return self.registrar(reg, "")
        self.linha("cota", f"{departamento}: {mil(usado)} de {mil(limite)} tokens usados no {r['cota']['periodo']}; segue")

        # 3. residência
        if pessoal or departamento in r["residencia"]["departamentos"]:
            motivo = "dado pessoal na pergunta" if pessoal else f"departamento {sens}"
            self.linha("residência", f"{motivo} → região obrigatória: {r['residencia']['regiao_obrigatoria']} (RC-03) "
                       f"→ {r['residencia']['modelo_brasil']}")
            reg.update(modelo=r["residencia"]["modelo_brasil"], regiao=r["residencia"]["regiao_obrigatoria"],
                       decisao="rota no Brasil (simulada: nenhum Claude roda no Brasil)")
            return self.registrar(reg, "[simulado] Esta rota levaria o pedido a um modelo hospedado no Brasil.")
        self.linha("residência", "sem dado pessoal e departamento não Regulado → região global permitida")

        # 4. complexidade
        comp = r["complexidade"]
        achou = [p for p in comp["palavras_de_analise"] if p in pergunta.lower()]
        if apelido == comp["apelido_simples"] and achou:
            apelido = comp["apelido_analise"]
            self.linha("complexidade", f'pergunta de análise ("{achou[0]}") → {apelido}')
        else:
            self.linha("complexidade", f"pergunta simples → {apelido}")
        reg["apelido"] = apelido

        # 5. apelido
        modelo = r["apelidos"][apelido]
        self.linha("apelido", f"{apelido} → {modelo}")

        # 6. cache (só entre perguntas do mesmo departamento: o APIM separa por vary-by)
        guardadas = [c for c in ler_estado("cache.json", []) if c["departamento"] == departamento]
        melhor = max(guardadas, key=lambda c: semelhanca(c["pergunta"], pergunta), default=None)
        nota = semelhanca(melhor["pergunta"], pergunta) if melhor else 0.0
        if melhor and nota >= r["cache"]["limiar"]:
            self.linha("cache", f'parecida com "{melhor["pergunta"]}" (semelhança {rodar.virgula(nota, 2)}, limiar '
                       f'{rodar.virgula(r["cache"]["limiar"], 2)}) → resposta do cache, sem chamar o modelo, custo zero')
            reg.update(modelo=melhor["modelo"], cache="sim", decisao="respondido pelo cache")
            return self.registrar(reg, melhor["resposta"])
        self.linha("cache", "nenhuma pergunta parecida guardada" if not melhor
                   else f"a mais parecida tem semelhança {rodar.virgula(nota, 2)}, abaixo do limiar {rodar.virgula(r['cache']['limiar'], 2)}")

        # 7. modelo, com reserva
        if modelo in self.falhar:
            reserva = r["apelidos"][r["reserva"]["apelido"]]
            self.linha("modelo", f"{modelo} recusou (429, excesso de uso) → circuit breaker aberto para ele")
            self.linha("reserva", f"{r['reserva']['apelido']} → {reserva}")
            modelo = reserva
        resp, texto, fontes = self.chamar(departamento, pergunta, modelo)
        if resp.erro:
            self.linha("modelo", f"ERRO: {resp.erro}")
            reg.update(modelo=modelo, decisao="erro do modelo")
            return self.registrar(reg, "")
        custo = cli_modelo.custo_api(resp.uso_por_modelo, rodar.PRECOS) or 0.0
        total = resp.tokens_entrada + resp.tokens_saida
        self.linha("modelo", f"{modelo} respondeu em {rodar.virgula(resp.duracao_s)} s; {mil(total)} tokens; "
                   f"US$ {rodar.virgula(custo, 5)}")
        cotas[departamento] = usado + total
        gravar_estado("cota.json", cotas)
        gravar_estado("cache.json", ler_estado("cache.json", []) + [
            {"departamento": departamento, "pergunta": pergunta, "resposta": texto, "modelo": modelo}])
        reg.update(modelo=modelo, tokens_entrada=resp.tokens_entrada, tokens_saida=resp.tokens_saida,
                   custo_usd=round(custo, 6), decisao="respondido pelo modelo")
        self.ultima_app = {"correlacao": corr, "usuario": usuario, "fontes": fontes, "ferramentas": []}
        return self.registrar(reg, texto)

    def registrar(self, reg, resposta):
        reg["resposta_como_saiu"] = resposta[:200]
        ESTADO.mkdir(exist_ok=True)
        with (ESTADO / "registro.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")
        self.linha("registro", f"gravado em labs/lab5/estado/registro.jsonl (correlação {reg['correlacao']})")
        if resposta:
            print(f"  {'resposta':<13} {resposta[:160]}{'…' if len(resposta) > 160 else ''}", flush=True)
        return resposta, reg


def zerar():
    for nome in ("cota.json", "cache.json", "registro.jsonl"):
        (ESTADO / nome).unlink(missing_ok=True)


def titulo(texto):
    print(f"\n=== {texto} ===", flush=True)


def sim_residencia(rotas):
    titulo("Residência (RC-03): o mesmo Bússola, duas rotas")
    gw = Gateway(rotas)
    gw.atender("TI Operacional", "Em que horário roda a janela do lote noturno do SGC?")
    gw.atender("Risco", "Qual é o saldo em atraso do cliente de CPF 123.456.789-09?")


def sim_complexidade(rotas):
    titulo("Roteamento por complexidade: a pergunta decide o modelo")
    gw = Gateway(rotas)
    gw.atender("Arquitetura", "O que o ADR-047 decidiu sobre o cache do saldo?")
    gw.atender("Arquitetura", "Compare o cache local e o Redis do ADR-047 e diga os riscos de cada opção para o saldo.")


def sim_cota(rotas):
    titulo("Cota de tokens por departamento (RC-08)")
    cotas = ler_estado("cota.json", {})
    cotas["Risco"] = 49000   # o Risco já usou quase toda a cota do mês
    gravar_estado("cota.json", cotas)
    Gateway(rotas).atender("Risco", "Qual é o percentual de provisão para a faixa de 90 dias de atraso?")


def sim_cache(rotas):
    titulo("Cache semântico: economia e risco")
    gw = Gateway(rotas)
    gw.atender("TI Operacional", "Em que horário roda a janela do lote noturno do SGC?")
    gw.atender("TI Operacional", "Qual é o horário da janela do lote noturno do SGC?")
    gw.atender("TI Operacional", "Em que horário roda a janela do lote diurno do SGC?")
    print("\n  Atenção: a terceira pergunta é sobre o lote DIURNO, mas recebeu a resposta do NOTURNO.")


def sim_reserva(rotas):
    titulo("Modelo reserva: o principal recusa, o gateway desvia")
    Gateway(rotas, falhar={rotas["apelidos"]["bussola-padrao"]}).atender(
        "TI Operacional", "Quem é o dono do runbook do lote do SGC?")


def sim_apelido(rotas):
    titulo("Apelido de modelo: trocar a versão sem mudar a aplicação (sem chamar o modelo)")
    antes = rotas["apelidos"]["bussola-padrao"]
    print(f'\n  A aplicação sempre pede "bussola-padrao".')
    print(f"  Hoje, em labs/lab5/rotas.toml:      bussola-padrao = \"{antes}\"")
    print("  O fornecedor anuncia a aposentadoria do modelo. A eval roda no modelo novo e passa.")
    print('  O time troca UMA linha no gateway:   bussola-padrao = "claude-sonnet-5-5"')
    print("  Resultado: todas as aplicações que pedem bussola-padrao passam a usar o modelo novo,")
    print("  sem deploy. Sem a eval aprovada, a troca não acontece: a eval é o portão.")


def sim_registro(rotas):
    titulo("Registro para auditoria (RC-05): o que o gateway vê e o que não vê")
    gw = Gateway(rotas)
    gw.atender("TI Operacional", "Em que horário roda a janela do lote noturno do SGC?", usuario="ana.souza (TI Operacional)")
    app = getattr(gw, "ultima_app", None)
    gw.atender("Risco", "Qual é o saldo em atraso do cliente de CPF 123.456.789-09?")
    linhas = (ESTADO / "registro.jsonl").read_text(encoding="utf-8").splitlines()[-2:]
    print("\n  O que o GATEWAY registrou (últimas 2 linhas):")
    for l in linhas:
        d = json.loads(l)
        print("   ", {k: d[k] for k in ("correlacao", "modelo", "regiao", "tokens_entrada", "tokens_saida",
                                         "custo_usd", "decisao", "pergunta_como_veio")})
    print("\n  O que falta no registro do gateway: o USUÁRIO, as FONTES usadas e as FERRAMENTAS chamadas.")
    print("  E o CPF ficou gravado como veio: o gateway não mascara dado pessoal sozinho.")
    if app:
        print("\n  O que a APLICAÇÃO registra, ligado pelo mesmo número de correlação:")
        print("   ", app)


SIMULACOES = {"residencia": sim_residencia, "complexidade": sim_complexidade, "cota": sim_cota,
              "cache": sim_cache, "reserva": sim_reserva, "apelido": sim_apelido, "registro": sim_registro}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("simulacao", choices=[*SIMULACOES, "todas"])
    ap.add_argument("--rotas", default=str(LAB / "rotas.toml"))
    ap.add_argument("--manter-estado", action="store_true", help="não zera cota, cache e registro antes")
    a = ap.parse_args()
    if a.simulacao != "apelido":
        msg = cli_modelo.disponivel("claude") or cli_modelo.logado()
        if msg:
            sys.exit(msg)
    rotas = ler_rotas(a.rotas)
    if not a.manter_estado:
        zerar()
    for nome in (SIMULACOES if a.simulacao == "todas" else [a.simulacao]):
        if a.simulacao == "todas" and nome != "residencia":
            zerar()
        SIMULACOES[nome](rotas)
    print()


if __name__ == "__main__":
    main()
