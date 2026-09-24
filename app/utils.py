import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def somente_digitos(valor) -> str:
    return "".join(ch for ch in str(valor or "") if ch.isdigit())


def cpf_valido(valor) -> bool:
    cpf = somente_digitos(valor)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * ((tamanho + 1) - i) for i in range(tamanho))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[tamanho]):
            return False
    return True


def cnpj_valido(valor) -> bool:
    cnpj = somente_digitos(valor)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    pesos_1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    pesos_2 = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    soma = sum(int(cnpj[i]) * pesos_1[i] for i in range(12))
    digito = 11 - (soma % 11)
    if digito >= 10:
        digito = 0
    if digito != int(cnpj[12]):
        return False
    soma = sum(int(cnpj[i]) * pesos_2[i] for i in range(13))
    digito = 11 - (soma % 11)
    if digito >= 10:
        digito = 0
    return digito == int(cnpj[13])


def documento_valido(tipo, numero) -> bool:
    tipo = int(tipo or 0)
    if tipo == 1:
        return cpf_valido(numero)
    if tipo == 2:
        return cnpj_valido(numero)
    if tipo == 3:
        return bool(str(numero or "").strip())
    return False


def parse_data(valor):
    if not valor:
        return None
    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor
    texto = str(valor).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    return None


def parse_decimal(valor):
    if valor is None or valor == "":
        return None
    if isinstance(valor, (int, float, Decimal)):
        return Decimal(str(valor))
    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return Decimal(texto)
    except InvalidOperation:
        return None


def dentro_do_exercicio(data_ref, ano: int) -> bool:
    if not data_ref or not ano:
        return False
    return data_ref.year == int(ano)


def money(valor) -> str:
    try:
        n = float(valor or 0)
    except (TypeError, ValueError):
        n = 0
    return f"R$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def rotulo_data(valor) -> str:
    data_ref = parse_data(valor) if not isinstance(valor, date) else valor
    if not data_ref:
        return "—"
    return data_ref.strftime("%d/%m/%Y")


def crc_valido(valor) -> bool:
    texto = re.sub(r"\s+", "", str(valor or "")).upper()
    return bool(re.fullmatch(r"[0-9A-Z]{6,20}", texto))
