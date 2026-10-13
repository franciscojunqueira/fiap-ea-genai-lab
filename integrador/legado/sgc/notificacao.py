# -*- coding: utf-8 -*-
# aviso de atraso por SMS ao sacado
# desligado por padrao (SGC_NOTIFICA=0) desde a troca do fornecedor de SMS em 2021
import urllib.parse
import urllib.request

from sgc import config, util

DIAS_AVISO = 5


def avisar_atrasados(con, data_ref):
    if not config.NOTIFICA:
        return 0
    atrasadas = con.execute(
        "SELECT c.nosso_numero, c.valor, c.vencimento, s.documento, s.telefone FROM cobranca c "
        "JOIN sacado s ON s.id = c.sacado_id WHERE c.status = 'REGISTRADA'"
    ).fetchall()
    enviados = 0
    for cob in atrasadas:
        if (data_ref - util.para_data(cob["vencimento"])).days != DIAS_AVISO:
            continue
        params = urllib.parse.urlencode({
            "fone": cob["telefone"],
            "doc": cob["documento"],
            "msg": "TECHCORP: boleto %s de R$ %.2f vencido. Regularize." % (cob["nosso_numero"], cob["valor"]),
        })
        url = config.SMS_URL + "?" + params
        util.log().info("SMS: %s", url)
        try:
            urllib.request.urlopen(url, timeout=5)
            enviados += 1
        except Exception as e:
            util.log().error("falha no SMS: %s", e)
    return enviados
