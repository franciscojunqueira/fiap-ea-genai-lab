# -*- coding: utf-8 -*-
# calendario de dias uteis bancarios
# os feriados moveis vem da planilha anual da Tesouraria. TODO: atualizar todo ano
import datetime

FERIADOS_FIXOS = ["01-01", "04-21", "05-01", "09-07", "10-12", "11-02", "11-15", "12-25"]

# carnaval (seg e ter), sexta-feira santa, corpus christi
FERIADOS_MOVEIS = {
    2019: ["03-04", "03-05", "04-19", "06-20"],
    2020: ["02-24", "02-25", "04-10", "06-11"],
    2021: ["02-15", "02-16", "04-02", "06-03"],
    2022: ["02-28", "03-01", "04-15", "06-16"],
    2023: ["02-20", "02-21", "04-07", "06-08"],
    2024: ["02-12", "02-13", "03-29", "05-30"],
}


def feriados(ano):
    if ano not in FERIADOS_MOVEIS:
        return set()
    datas = set()
    for md in FERIADOS_FIXOS + FERIADOS_MOVEIS[ano]:
        mes, dia = md.split("-")
        datas.add(datetime.date(ano, int(mes), int(dia)))
    return datas


def eh_dia_util(data):
    if data.weekday() >= 5:
        return False
    return data not in feriados(data.year)


def proximo_dia_util(data):
    while not eh_dia_util(data):
        data = data + datetime.timedelta(days=1)
    return data


def dias_corridos(inicio, fim):
    return (fim - inicio).days
