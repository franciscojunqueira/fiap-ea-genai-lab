# Comandos dos labs. `make` sem alvo lista os comandos.
.DEFAULT_GOAL := help
.PHONY: help check test erp mcp skill-check \
        lab1 lab2 lab3 lab4 lab5 lab6 \
        lab1-check lab2-check lab3-check lab4-check lab5-check lab6-check \
        legado er-check checkpoint-check pacote-check

RUN := uv run --quiet
SKILLS := $(wildcard .agents/skills/*)

help: ## Lista os comandos
	@grep -E '^[a-z0-9 -]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-12s %s\n", $$1, $$2}'

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

lab1: ## Lab 1 (Aula 1)
	@echo "lab1: em construção, disponível antes da Aula 1."
lab2 lab3: ## Labs 2 e 3 (Aula 2)
	@echo "$@: em construção, disponível antes da Aula 2."
lab4 lab5: ## Labs 4 e 5 (Aula 3)
	@echo "$@: em construção, disponível antes da Aula 3."
lab6: ## Lab 6 (Aula 4)
	@echo "lab6: em construção, disponível antes da Aula 4."

# Um check que ainda não existe não pode dar PASS: imprime e sai com erro.
lab1-check lab2-check lab3-check lab4-check lab5-check lab6-check: ## PASS/FAIL de cada lab
	@$(MAKE) --no-print-directory $(subst -check,,$@) && exit 1

legado: ## Roda um ciclo do SGC, o legado do projeto integrador (não usa modelo)
	@$(RUN) python integrador/scripts/demo_legado.py

er-check: ## Confere a engenharia reversa (Atividade 1 do integrador)
	@$(RUN) python integrador/scripts/checar_entrega.py er

checkpoint-check: ## Confere o checkpoint (Atividade 2 do integrador)
	@$(RUN) python integrador/scripts/checar_entrega.py checkpoint

pacote-check: ## Confere o pacote final (Atividade 3 do integrador)
	@$(RUN) python integrador/scripts/checar_entrega.py final
