"""Leitura dos formulários no formato exigido pelo JSON do TCE."""

from app.utils import parse_data, parse_decimal, somente_digitos


def _nome(prefixo, campo):
    return f"{prefixo}.{campo}" if prefixo else campo


def _vazio(valor) -> bool:
    return valor is None or valor == "" or valor == []


def ler_campos(form, campos, prefixo=""):
    dados = {}
    for campo in campos:
        nome = campo["nome"]
        chave = _nome(prefixo, nome)
        tipo = campo["tipo"]
        if tipo == "objeto":
            aninhado = ler_campos(form, campo.get("campos") or [], chave)
            if any(not _vazio(v) for v in aninhado.values()):
                dados[nome] = aninhado
            continue
        if tipo == "bool":
            enviados = form.getlist(chave)
            bruto = enviados[-1] if enviados else ""
        else:
            bruto = form.get(chave)
        valor = _converter(tipo, bruto)
        if not _vazio(valor):
            dados[nome] = valor
    return dados


def ler_grade(form, grade):
    linhas = []
    quantidade = 0
    for campo in grade["campos"]:
        quantidade = max(quantidade, len(form.getlist(campo["nome"])))
    for indice in range(quantidade):
        item = {}
        for campo in grade["campos"]:
            lista = form.getlist(campo["nome"])
            bruto = lista[indice] if indice < len(lista) else ""
            valor = _converter(campo["tipo"], bruto)
            if not _vazio(valor):
                item[campo["nome"]] = valor
        if item:
            linhas.append(item)
    return linhas


def _converter(tipo, bruto):
    if tipo == "bool":
        if bruto in (True, False):
            return bool(bruto)
        return str(bruto).lower() in {"1", "true", "on", "sim", "yes"}
    if bruto is None:
        return None
    texto = str(bruto).strip()
    if texto == "":
        return None
    if tipo in {"texto", "escolha"}:
        return texto
    if tipo == "inteiro":
        try:
            return int(texto)
        except ValueError:
            return texto
    if tipo == "inteiros":
        partes = [p.strip() for p in texto.replace(";", ",").split(",") if p.strip()]
        saida = []
        for parte in partes:
            try:
                saida.append(int(parte))
            except ValueError:
                saida.append(parte)
        return saida
    if tipo == "decimal":
        numero = parse_decimal(texto)
        if numero is None:
            return texto
        return float(numero)
    if tipo == "data":
        data_ref = parse_data(texto)
        return data_ref.isoformat() if data_ref else texto
    if tipo == "cpf":
        return somente_digitos(texto)
    if tipo == "cnpj":
        return somente_digitos(texto)
    if tipo == "cpfs":
        brutos = texto.replace(";", ",").replace("\n", ",").split(",")
        return [somente_digitos(item) for item in brutos if somente_digitos(item)]
    return texto


def resumir_item(item) -> str:
    if not isinstance(item, dict):
        return str(item)
    for chave in (
        "nome_programa",
        "numero",
        "cpf",
        "descricao",
        "numero_patrimonio",
        "codigo_meta",
        "tipo_parecer_ata",
    ):
        if item.get(chave):
            return str(item.get(chave))
    credor = item.get("credor") or {}
    if isinstance(credor, dict) and credor.get("documento_numero"):
        return str(credor.get("documento_numero"))
    return "Registro"
