from sgc import nosso_numero


def test_dv_modulo11():
    assert nosso_numero.dv_modulo11("17000000001") == "6"
    assert nosso_numero.dv_modulo11("17000000002") == "4"


def test_dv_zero_quando_resto_0_ou_1():
    assert nosso_numero.dv_modulo11("17000000010") == "5"
    assert nosso_numero.dv_modulo11("17000000019") == "9"
