# -*- coding: utf-8 -*-
# SGC - Sistema de Gestao de Cobranca
# Configuracoes gerais. Valores podem ser sobrescritos por variaveis de ambiente (ver ops/rodar_lote.sh)
# 2011-03 versao inicial (JRS)
# 2016-08 inclusao do relatorio de risco (MCP/Risco)
# 2019-11 migracao python 2.7 -> 3 (terceirizada)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# banco do SGC
DB_PATH = os.environ.get("SGC_DB", os.path.join(BASE_DIR, "dados", "sgc.db"))

# diretorios de troca de arquivos com o core (o transporte e feito pelo job de transferencia, fora do SGC)
DIR_ENTRADA = os.environ.get("SGC_DIR_ENTRADA", os.path.join(BASE_DIR, "dados", "entrada"))
DIR_REMESSA = os.environ.get("SGC_DIR_REMESSA", os.path.join(BASE_DIR, "dados", "remessa"))
DIR_RETORNO = os.environ.get("SGC_DIR_RETORNO", os.path.join(BASE_DIR, "dados", "retorno"))
DIR_PROCESSADOS = os.path.join(DIR_RETORNO, "processados")

# relatorio da area de Risco - em producao aponta para o compartilhamento de rede da Risco
DIR_RISCO = os.environ.get("SGC_DIR_RISCO", "/mnt/risco/sgc")
DIR_RISCO_LOCAL = os.path.join(BASE_DIR, "saida", "risco")

# integracao com o ERP do Gestao PJ (le direto do banco do ERP)
ERP_DB = os.environ.get("SGC_ERP_DB", os.path.join(BASE_DIR, "..", "..", "mini-erp", "data", "mini_erp.db"))

# mainframe de cobranca
MAINFRAME_HOST = "mf-cobranca.techcorp.local"
MAINFRAME_PORTA = 3270

# dados do cedente (TechCorp) na remessa
CEDENTE_AGENCIA = "0001"
CEDENTE_CONTA = "0045871"
CEDENTE_CARTEIRA = "17"
CEDENTE_NOME = "TECHCORP BANCO MULTIPLO SA"

# regras de prazo
PRAZO_PADRAO_DIAS = 30
PRAZO_PRIME_DIAS = 45  # segmento PRIME negociado pela area comercial em 2017

# valor minimo do boleto (custo de registro no core). abaixo disso acumula
VALOR_MINIMO_BOLETO = 10.00

# horario de corte da remessa. depois disso a remessa vai com data do proximo dia util
HORA_CORTE = 20

# notificacao por SMS (desligado desde 2021, ver chamado)
NOTIFICA = os.environ.get("SGC_NOTIFICA", "0") == "1"
SMS_URL = "http://sms-gw.techcorp.local:8080/enviar"

LOG_NIVEL = os.environ.get("SGC_LOG", "INFO")
