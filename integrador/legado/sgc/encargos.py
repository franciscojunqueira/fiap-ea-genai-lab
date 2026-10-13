# -*- coding: utf-8 -*-
# multa e juros de mora sobre boleto pago em atraso
from sgc import util

MULTA = 0.02          # 2% sobre o valor
JUROS_DIA = 0.00033   # 1% ao mes
CARENCIA_DIAS = 3     # acordo com a area comercial (2014)


def dias_atraso(vencimento, pagamento):
    return (util.para_data(pagamento) - util.para_data(vencimento)).days


def valor_devido(valor, vencimento, pagamento):
    atraso = dias_atraso(vencimento, pagamento)
    if atraso <= CARENCIA_DIAS:
        return round(valor, 2)
    multa = valor * MULTA
    juros = valor * JUROS_DIA * atraso
    return round(valor + multa + juros, 2)
