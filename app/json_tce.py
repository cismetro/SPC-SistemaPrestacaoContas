"""Montagem do documento JSON no layout do Manual TCE-SP v1.19."""

import json
from collections import OrderedDict

from app.catalogos import SECOES, secao_aplica


def carregar_payload(bloco):
    if not bloco or not bloco.payload:
        return None
    try:
        return json.loads(bloco.payload)
    except json.JSONDecodeError:
        return None


def limpar(valor):
    if isinstance(valor, dict):
        saida = {}
        for chave, item in valor.items():
            limpo = limpar(item)
            if limpo is None or limpo == "" or limpo == {} or limpo == []:
                continue
            saida[chave] = limpo
        return saida
    if isinstance(valor, list):
        saida = []
        for item in valor:
            limpo = limpar(item)
            if limpo is None or limpo == "" or limpo == {} or limpo == []:
                continue
            saida.append(limpo)
        return saida
    return valor


def _agrupar_atividades(conteudo):
    linhas = (conteudo or {}).get("programas") or []
    programas = OrderedDict()
    for linha in linhas:
        nome = (linha.get("nome_programa") or "").strip()
        codigo = str(linha.get("codigo_meta") or "").strip()
        if not nome or not codigo:
            continue
        programa = programas.setdefault(nome, OrderedDict())
        meta = programa.setdefault(
            codigo,
            {
                "codigo_meta": codigo,
                "periodicidades": [],
                "meta_atendida": bool(linha.get("meta_atendida")),
                "justificativa": linha.get("justificativa") or "",
            },
        )
        if linha.get("justificativa"):
            meta["justificativa"] = linha.get("justificativa")
        meta["meta_atendida"] = bool(linha.get("meta_atendida"))
        periodo = {"periodo": linha.get("periodo")}
        if linha.get("quantidade_realizada") not in (None, ""):
            periodo["quantidade_realizada"] = linha.get("quantidade_realizada")
        if linha.get("resultado_meta") not in (None, ""):
            periodo["resultado_meta"] = int(linha.get("resultado_meta"))
        if linha.get("justificativa_periodo"):
            periodo["justificativa"] = linha.get("justificativa_periodo")
        meta["periodicidades"].append(periodo)
    return {
        "programas": [
            {
                "nome_programa": nome,
                "metas": list(metas.values()),
            }
            for nome, metas in programas.items()
        ]
    }


def _ajustar_regras_de_omissao(chave, conteudo):
    if chave == "glosas" and isinstance(conteudo, list):
        for item in conteudo:
            resultado = int(item.get("resultado_analise") or 0)
            if resultado in (1, 3):
                item.pop("valor_glosa", None)
            if not item.get("pagamento_data"):
                item.pop("pagamento_data", None)
    if chave == "documentos_fiscais" and isinstance(conteudo, list):
        for item in conteudo:
            if int(item.get("rateio_proveniente_tipo") or 0) != 1:
                item.pop("rateio_percentual", None)
            contrato = item.get("identificacao_contrato") or {}
            if not contrato.get("numero"):
                item.pop("identificacao_contrato", None)
    if chave == "contratos" and isinstance(conteudo, list):
        for item in conteudo:
            naturezas = item.get("natureza_contratacao") or []
            if 23 not in naturezas:
                item.pop("natureza_contratacao_outro", None)
            if int(item.get("criterio_selecao") or 0) != 4:
                item.pop("criterio_selecao_outro", None)
            if int(item.get("vigencia_tipo") or 0) != 1 and not item.get("vigencia_data_final"):
                item.pop("vigencia_data_final", None)
    if chave == "pagamentos" and isinstance(conteudo, list):
        for item in conteudo:
            if int(item.get("meio_pagamento_tipo") or 0) != 1:
                for campo in ("banco", "agencia", "conta_corrente", "numero_transacao"):
                    item.pop(campo, None)
    if chave == "repasses" and isinstance(conteudo, list):
        for item in conteudo:
            if item.get("valor_previsto") == item.get("valor_repasse"):
                item.pop("justificativa_diferenca_valor", None)
            if int(item.get("tipo_documento_bancario") or 0) != 2:
                item.pop("descricao_outros", None)
    if chave == "relatorio_atividades":
        for programa in conteudo.get("programas") or []:
            for meta in programa.get("metas") or []:
                if meta.get("meta_atendida"):
                    meta.pop("justificativa", None)
                for periodo in meta.get("periodicidades") or []:
                    if not periodo.get("justificativa"):
                        periodo.pop("justificativa", None)
    return conteudo


def montar_documento(prestacao) -> dict:
    entidade = prestacao.entidade
    documento = {
        "descritor": {
            "tipo_documento": prestacao.tipo_documento,
            "municipio": prestacao.municipio_audesp,
            "entidade": entidade.codigo_audesp if entidade else None,
            "ano": prestacao.ano,
            "mes": 12,
        },
        "codigo_ajuste": prestacao.codigo_ajuste,
    }
    if prestacao.declaracao_negativa:
        return limpar(documento)

    blocos = {bloco.secao: bloco for bloco in prestacao.blocos}
    for secao in SECOES:
        if not secao_aplica(secao, prestacao.tipo_documento):
            continue
        if secao["chave"] == "retificacao":
            continue
        bloco = blocos.get(secao["chave"])
        if not bloco or bloco.sem_movimento:
            continue
        conteudo = carregar_payload(bloco)
        if conteudo is None:
            continue
        if secao["chave"] == "relatorio_atividades":
            conteudo = _agrupar_atividades(conteudo)
        if secao["formato"] == "flag":
            if secao["chave"] == "termo_cessao_permissao_bens":
                documento["termo_cessao_permissao_bens"] = bool(
                    (conteudo or {}).get("termo_cessao_permissao_bens")
                )
            continue
        conteudo = _ajustar_regras_de_omissao(secao["chave"], conteudo)
        limpo = limpar(conteudo)
        if limpo in (None, {}, []):
            continue
        documento[secao["json_chave"]] = limpo

    if prestacao.retificacao:
        documento["retificacao"] = True
    return limpar(documento)


def documento_texto(prestacao) -> str:
    return json.dumps(montar_documento(prestacao), ensure_ascii=False, indent=2)
