# Comandos dos labs. `make` sem alvo lista os comandos.
.DEFAULT_GOAL := help
.PHONY: help check test erp mcp skill-check \
        lab1 lab1-referencia lab1-extra lab2 lab2-rodar lab2-replay lab3 lab3-comparar lab3-replay lab4 lab5 lab6 atualizar \
        lab4-orquestrar lab4-orquestrar-replay lab4-skill lab4-skill-replay lab4-eval lab4-juiz lab4-replay lab5-gateway lab5-gateway-replay lab5-tco \
        lab1-check lab2-check lab3-check lab4-check lab5-check lab6-check \
        legado er-check checkpoint-check pacote-check atividade2 atividade2-entregar atividade3 atividade3-entregar

RUN := uv run --quiet
SKILLS := $(wildcard .agents/skills/*)

help: ## Lista os comandos
	@grep -E '^[a-z0-9 -]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-16s %s\n", $$1, $$2}'

check: ## Verifica o ambiente (Python, ERP, MCP, acesso a modelo)
	@$(RUN) python scripts/check.py

test: ## Testes de fumaça do ERP e do MCP server
	@$(RUN) pytest -q

erp: ## Sobe o Mini-ERP em http://localhost:8000 (Ctrl+C para parar)
	@$(RUN) uvicorn app.main:app --app-dir mini-erp --host 0.0.0.0 --port 8000 --reload

comma := ,
# No Codespace, o navegador acessa o Inspector pela URL encaminhada; o Inspector v2 só aceita origens listadas.
INSPECTOR_ORIGENS := http://127.0.0.1:6274,http://localhost:6274$(if $(CODESPACE_NAME),$(comma)https://$(CODESPACE_NAME)-6274.$(GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN))
mcp: ## Abre o MCP Inspector no MCP server do Mini-ERP (precisa do `make erp` em outro terminal)
	@ALLOWED_ORIGINS="$(INSPECTOR_ORIGENS)" npx -y @modelcontextprotocol/inspector .venv/bin/python mcp-server/server.py

skill-check: ## Valida as skills do repositório (boas práticas de skills da Anthropic)
	@python3 scripts/validar_skill.py $(SKILLS)

lab1: ## Lab 1 (Aula 1): prepara a spec, os sensores e o rascunho do colega
	@$(RUN) python labs/lab1/preparar.py
lab1-check: ## Lab 1: PASS/FAIL dos 7 itens
	@$(RUN) python labs/lab1/checar.py
lab1-referencia: ## Lab 1, plano B: aplica o código de referência (cota esgotada)
	@$(RUN) python labs/lab1/referencia/aplicar.py
lab1-extra: ## Lab 1, desafio extra: skill escrevendo-adrs sem × com, no Haiku
	@$(RUN) python labs/lab1/extra.py $(ARGS)
lab2: ## Lab 2 (Aula 2): prepara o config e confere o login do operador
	@$(RUN) python labs/lab2/preparar.py
lab2-rodar: ## Lab 2: roda as 10 perguntas (PIPELINE=rag | agentica | contexto; CLI=codex opcional)
	@$(RUN) python labs/lab2/rodar.py $(PIPELINE) $(if $(CLI),--cli $(CLI))
lab2-check: ## Lab 2: não tem check (as respostas vão no chat; os números, na Atividade 2)
	@echo "O Lab 2 não tem check: respondam às 3 perguntas do labs/lab2/README.md. Os números vão para a Atividade 2 (make checkpoint-check)."
lab2-replay: ## Lab 2, plano B: copia as execuções gravadas (cota esgotada)
	@$(RUN) python labs/lab2/usar_replay.py
lab3: ## Lab 3 (Aula 2): prepara o contrato e a descrição do grupo
	@$(RUN) python labs/lab3/preparar.py
lab3-comparar: ## Lab 3: 3 cenários com o contrato VERSAO=ruim | boa | grupo (CLI=codex opcional)
	@$(RUN) python labs/lab3/comparar.py $(VERSAO) $(if $(MODELO),--modelo $(MODELO)) $(if $(CLI),--cli $(CLI))
lab3-check: ## Lab 3: PASS/FAIL dos 5 itens
	@$(RUN) python labs/lab3/checar.py
lab3-replay: ## Lab 3, plano B: copia as comparações gravadas (cota esgotada)
	@$(RUN) python labs/lab3/usar_replay.py
lab4 lab5: ## Aula 3: demonstrações do professor (veja labs/lab4/README.md e labs/lab5/README.md)
	@echo "$@: na Aula 3, os Labs 4 e 5 são demonstrações do professor. Comandos em labs/$@/README.md (make help)."
lab4-orquestrar: ## Aula 3, demonstração 1: um agente × subagentes (MODO=unico | subagentes | ambos)
	@$(RUN) python labs/lab4/orquestrar.py $(or $(MODO),ambos)
lab4-orquestrar-replay: ## Aula 3, demonstração 1: as duas execuções gravadas pelo professor
	@$(RUN) python labs/lab4/orquestrar.py replay
lab4-skill: ## Aula 3, demonstração 2: como a skill escrevendo-adrs é carregada, passo a passo
	@$(RUN) python labs/lab4/skill_carregada.py
lab4-skill-replay: ## Aula 3, demonstração 2: a sessão gravada e o skill-creator (replay/lab4/skill_creator/)
	@$(RUN) python labs/lab4/skill_carregada.py --replay && cat replay/lab4/skill_creator/resultado.md
lab4-eval: ## Aula 3, demonstração 3: a eval do Bússola (K=3; CASO=<id> roda só um caso)
	@$(RUN) python labs/lab4/eval.py --k $(or $(K),3) $(if $(CASO),--caso $(CASO))
lab4-juiz: ## Aula 3, demonstração 3: o juiz confere uma pergunta do Lab 2 (PERGUNTA=P03)
	@$(RUN) python labs/lab4/juiz.py $(or $(PERGUNTA),P03)
lab4-replay: ## Aula 3, demonstração 3: a eval gravada pelo professor
	@cat replay/lab4/eval/eval_k3.txt
lab5-gateway: ## Aula 3, demonstração 4: o gateway simulado (SIMULACAO=residencia | complexidade | cota | cache | reserva | apelido | registro | todas)
	@$(RUN) python labs/lab5/gateway.py $(or $(SIMULACAO),todas)
lab5-gateway-replay: ## Aula 3, demonstração 4: as simulações gravadas pelo professor (SIMULACAO=<nome> mostra uma só)
	@$(RUN) python labs/lab5/gateway.py --replay $(or $(SIMULACAO),todas)
lab5-tco: ## Aula 3, demonstração 5: o custo por rota (DIVISAO=roteado | tudo-haiku-rag | tudo-sonnet-agentica | multiagente)
	@$(RUN) python labs/lab5/tco.py --divisao $(or $(DIVISAO),roteado)
lab6: ## Lab 6 (Aula 4)
	@echo "lab6: em construção, disponível antes da Aula 4."

# Um check que ainda não existe não pode dar PASS: imprime e sai com erro.
lab4-check lab5-check lab6-check: ## PASS/FAIL de cada lab
	@$(MAKE) --no-print-directory $(subst -check,,$@) && exit 1

atualizar: ## Traz do repositório-template os labs novos e as correções, sem tocar nos arquivos do grupo
	@python3 scripts/atualizar_do_template.py

legado: ## Roda um ciclo do SGC, o legado do projeto integrador (não usa modelo)
	@$(RUN) python integrador/scripts/demo_legado.py

er-check: ## Confere a engenharia reversa (Atividade 1 do integrador)
	@$(RUN) python integrador/scripts/checar_entrega.py er

checkpoint-check: ## Confere o checkpoint (Atividade 2 do integrador)
	@$(RUN) python integrador/scripts/checar_entrega.py checkpoint

atividade2: ## Atividade 2: prepara o 01-design.md para preencher e mostra os números do Lab 2
	@$(RUN) python integrador/scripts/atividade2.py preparar

atividade2-entregar: ## Atividade 2: confere, faz commit e push e mostra o link e o SHA para o Portal
	@$(RUN) python integrador/scripts/atividade2.py entregar
atividade3: ## Trabalho final: preenche os resultados da Aula 3 em 02-qualidade.md e 03-economia.md
	@$(RUN) python integrador/scripts/atividade3.py preparar

atividade3-entregar: ## Trabalho final: confere, faz commit e push e mostra o link e o SHA para o Portal
	@$(RUN) python integrador/scripts/atividade3.py entregar

pacote-check: ## Confere o pacote final (Atividade 3 do integrador)
	@$(RUN) python integrador/scripts/checar_entrega.py final
