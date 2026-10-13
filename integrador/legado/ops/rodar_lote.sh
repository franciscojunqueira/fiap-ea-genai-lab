#!/bin/bash
# lote noturno do SGC - chamado pelo cron (ver crontab.txt)
# servidor: sgc-batch01
export SGC_DB=/dados/sgc/sgc.db
export SGC_DIR_ENTRADA=/troca/entrada
export SGC_DIR_REMESSA=/troca/remessa
export SGC_DIR_RETORNO=/troca/retorno
export SGC_DIR_RISCO=/mnt/risco/sgc
export SGC_ERP_DB=/dados/gestaopj/mini_erp.db

cd /opt/sgc

# o retorno da manha precisa entrar antes do relatorio de risco
python3 -m sgc retorno || exit 1
python3 -m sgc importar --origem erp
python3 -m sgc importar --origem csv
python3 -m sgc remessa
/opt/cd/bin/cdtransfer -p SGC_REMESSA -f "/troca/remessa/REM_*.txt"
python3 -m sgc risco
