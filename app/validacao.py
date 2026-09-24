"""Regras locais do Manual TCE-SP v1.19 aplicáveis antes da geração do JSON.

Regras que só o Audesp consegue confirmar (ajuste armazenado, certidão
concluída, classificação econômica do exercício) ficam como conferência
explícita do gestor. O SPC não consulta nem envia nada ao Audesp.
"""

from datetime import date

from app.catalogos import (
    REQ_ART_7,
    REQ_ART_8,
    REQ_DIVULGACAO,
    TIPO_COLAB,
    TIPO_CONVENIO,
    TIPO_FOMENTO,
    TIPO_GESTAO,
    TIPO_PARCERIA,
    TIPOS_DECLARACAO,
    secoes_visiveis,
    secao_por_chave,
)
from app.json_tce import carregar_payload
from app.utils import (
    cnpj_valido,
    cpf_valido,
    crc_valido,
    documento_valido,
    parse_data,
    parse_decimal,
    somente_digitos,
)


class Achado:
    def __init__(self, secao, campo, responsavel, problema, correcao):
        self.secao = secao
        self.campo = campo
        self.responsavel = responsavel
        self.problema = problema
        self.correcao = correcao

    def como_dict(self, entidade_nome):
        spec = secao_por_chave(self.secao)
        titulo = spec["titulo"] if spec else (self.secao or "Prestação")
        quem = {
            "entidade": entidade_nome,
            "gestor": "Gestor da Secretaria",
            "admin": "Administrador",
        }.get(self.responsavel, self.responsavel)
        return {
            "secao": self.secao,
            "titulo": titulo,
            "campo": self.campo,
            "responsavel": self.responsavel,
            "quem": quem,
            "problema": self.problema,
            "correcao": self.correcao,
        }


def _add(achados, secao, campo, responsavel, problema, correcao):
    achados.append(Achado(secao, campo, responsavel, problema, correcao))


def _bloco(mapa, chave):
    bloco = mapa.get(chave)
    if not bloco or bloco.sem_movimento:
        return None
    return carregar_payload(bloco)


def _lista(conteudo, nome=None):
    if conteudo is None:
        return []
    if nome:
        if isinstance(conteudo, dict):
            return list(conteudo.get(nome) or [])
        return []
    if isinstance(conteudo, list):
        return conteudo
    return []


def _no_exercicio(valor, ano):
    data_ref = parse_data(valor)
    return bool(data_ref and data_ref.year == int(ano))


def _credor_ok(achados, secao, credor, rotulo):
    credor = credor or {}
    tipo = credor.get("documento_tipo")
    numero = credor.get("documento_numero")
    if not documento_valido(tipo, numero):
        _add(
            achados, secao, f"{rotulo}.documento_numero", "entidade",
            f"O documento do {rotulo} não é um CPF, CNPJ ou RNE válido.",
            "Informe o tipo 1, 2 ou 3 e um número válido. RNE exige também o nome.",
        )
    if int(tipo or 0) == 3 and not (credor.get("nome") or "").strip():
        _add(
            achados, secao, f"{rotulo}.nome", "entidade",
            f"O nome do {rotulo} é obrigatório para documento RNE.",
            "Preencha o nome ou a razão social do credor estrangeiro.",
        )


def validar_prestacao(prestacao):
    achados = []
    entidade = prestacao.entidade
    ano = prestacao.ano or 0
    tipo = prestacao.tipo_documento
    mapa = {bloco.secao: bloco for bloco in prestacao.blocos}
    hoje = date.today()

    if not tipo:
        _add(achados, "descritor", "tipo_documento", "gestor",
             "O tipo da prestação não foi informado.",
             "Selecione o tipo do ajuste: convênio, contrato de gestão, colaboração, fomento ou parceria.")
    if not prestacao.municipio_audesp:
        _add(achados, "descritor", "municipio", "gestor",
             "Falta o código do município no Audesp.",
             "Informe o código da planilha de municípios e entidades do coletor Audesp. Não use o código IBGE no lugar desse campo.")
    if not entidade or not entidade.codigo_audesp:
        _add(achados, "descritor", "entidade", "admin",
             f"A entidade {entidade.nome_exibicao if entidade else ''} não tem código Audesp.",
             "Cadastre o código da entidade na manutenção cadastral, conforme a planilha do coletor Audesp.")
    if ano < 2025 or ano > hoje.year:
        _add(achados, "descritor", "ano", "gestor",
             "O exercício está fora da regra do manual.",
             "O ano deve ser igual ou maior que 2025 e não pode ser futuro. No piloto do TCE o início é 2024; este sistema segue a regra de produção do manual v1.19.")
    if int(prestacao.mes or 0) != 12:
        _add(achados, "descritor", "mes", "gestor",
             "O mês do descritor precisa ser 12.",
             "A prestação é anual. O manual determina o valor 12 nesse campo.")
    codigo = somente_digitos(prestacao.codigo_ajuste)
    if len(codigo) != 16:
        _add(achados, "codigo_ajuste", "codigo_ajuste", "gestor",
             "O código do ajuste não tem 16 dígitos.",
             "Informe o código do ajuste já armazenado no módulo de Ajustes do Audesp, com 16 dígitos.")
    if not prestacao.conferencia_codigos_audesp or not prestacao.conferencia_ajuste:
        _add(achados, "descritor", "conferencia", "gestor",
             "A conferência do código do município, da entidade e do ajuste ainda não foi registrada.",
             "Confira os códigos na planilha do Audesp e no módulo de Ajustes, e marque a conferência no cabeçalho da prestação.")

    if prestacao.declaracao_negativa:
        return [item.como_dict(entidade.nome_exibicao) for item in achados]

    obrigatorias = [
        "prestacao_contas_entidade_beneficiaria",
        "demonstracoes_contabeis",
        "parecer_conclusivo",
        "transparencia",
        "dados_gerais_entidade_beneficiaria",
        "responsaveis_membros_orgao_concessor",
        "declaracoes",
        "disponibilidades",
        "receitas",
    ]
    for chave in obrigatorias:
        spec = secao_por_chave(chave)
        if spec and not _secao_conhecida(mapa, chave):
            _add(
                achados, chave, chave, spec["responsavel"],
                f"A seção {spec['numero']} — {spec['titulo']} não foi preenchida nem confirmada sem movimento.",
                "Abra a seção, grave os dados ou confirme expressamente que não há movimento, quando o manual permitir omissão.",
            )

    _validar_empregados(achados, _bloco(mapa, "relacao_empregados"), ano, prestacao.primeira_prestacao)
    _validar_contratos(achados, _bloco(mapa, "contratos"), tipo)
    documentos = _lista(_bloco(mapa, "documentos_fiscais"))
    _validar_documentos(achados, documentos, ano, prestacao.primeira_prestacao)
    _validar_pagamentos(achados, _lista(_bloco(mapa, "pagamentos")), documentos, ano)
    _validar_glosas(achados, _lista(_bloco(mapa, "glosas")), documentos)
    _validar_empenhos(achados, _lista(_bloco(mapa, "empenhos")), ano, prestacao.primeira_prestacao)
    _validar_repasses(achados, _lista(_bloco(mapa, "repasses")), _lista(_bloco(mapa, "empenhos")), ano, prestacao.ultimo_periodo_vigencia)
    _validar_receitas(achados, _bloco(mapa, "receitas"), ano)
    _validar_disponibilidades(achados, _bloco(mapa, "disponibilidades"))
    _validar_prestacao_entidade(achados, _bloco(mapa, "prestacao_contas_entidade_beneficiaria"), ano, hoje)
    _validar_parecer(achados, _bloco(mapa, "parecer_conclusivo"))
    _validar_transparencia(achados, _bloco(mapa, "transparencia"))
    _validar_demonstracoes(achados, _bloco(mapa, "demonstracoes_contabeis"), hoje)
    _validar_declaracoes(achados, _bloco(mapa, "declaracoes"), tipo)
    _validar_relatorios_gestor(achados, mapa, tipo)
    _validar_certidoes(achados, mapa, tipo, prestacao.conferencia_certidoes)
    _validar_atas(achados, _lista(_bloco(mapa, "publicacoes_parecer_ata")), tipo)
    _validar_atividades(achados, _bloco(mapa, "relatorio_atividades"))
    _validar_descontos_devolucoes(achados, mapa, ano)
    _validar_bens(achados, _bloco(mapa, "relacao_bens"), ano, prestacao.primeira_prestacao)

    for secao in secoes_visiveis(tipo):
        if secao["formato"] == "especial" or secao["chave"] == "retificacao":
            continue
        if secao["chave"] in obrigatorias:
            continue
        if secao["chave"] not in mapa:
            responsavel = secao["responsavel"]
            _add(
                achados, secao["chave"], secao["chave"], responsavel,
                f"A seção {secao['numero']} — {secao['titulo']} ainda não foi revisada.",
                "Preencha os registros ou confirme que a seção não tem movimento neste exercício.",
            )

    return [item.como_dict(entidade.nome_exibicao) for item in achados]


def _secao_conhecida(mapa, chave):
    bloco = mapa.get(chave)
    return bool(bloco)


def _validar_empregados(achados, conteudo, ano, primeira):
    vistos = set()
    for item in _lista(conteudo):
        cpf = item.get("cpf")
        admissao = item.get("data_admissao")
        chave = (cpf, admissao)
        if chave in vistos:
            _add(achados, "relacao_empregados", "cpf", "entidade",
                 f"O CPF {cpf} foi informado mais de uma vez com a mesma admissão.",
                 "Deixe um único registro por CPF e data de admissão.")
        vistos.add(chave)
        if not cpf_valido(cpf):
            _add(achados, "relacao_empregados", "cpf", "entidade",
                 "Há empregado com CPF inválido.",
                 "Corrija o CPF para os 11 dígitos válidos, sem pontuação no arquivo.")
        if not (item.get("cbo") or "").isdigit() or len(str(item.get("cbo"))) != 6:
            _add(achados, "relacao_empregados", "cbo", "entidade",
                 "O CBO precisa ter 6 dígitos.",
                 "Informe o código brasileiro de ocupação com seis números.")
        if str(item.get("cbo") or "").startswith("225") and len(somente_digitos(item.get("cns"))) != 15:
            _add(achados, "relacao_empregados", "cns", "entidade",
                 "Médico sem CNS de 15 dígitos.",
                 "Para CBO do subgrupo 225, informe o Cartão Nacional de Saúde.")
        demissao = parse_data(item.get("data_demissao"))
        data_adm = parse_data(admissao)
        if demissao and data_adm and demissao < data_adm:
            _add(achados, "relacao_empregados", "data_demissao", "entidade",
                 "A demissão é anterior à admissão.",
                 "Ajuste as datas. A demissão também precisa cair dentro do exercício.")
        if demissao and not _no_exercicio(demissao, ano):
            _add(achados, "relacao_empregados", "data_demissao", "entidade",
                 "A data de demissão está fora do exercício.",
                 "Informe uma demissão dentro do ano da prestação.")
        if not item.get("periodos_remuneracao"):
            _add(achados, "relacao_empregados", "periodos_remuneracao", "entidade",
                 "Empregado sem períodos de remuneração.",
                 "Informe mês, carga horária e remuneração bruta de cada mês trabalhado no exercício.")


def _validar_contratos(achados, conteudo, tipo):
    vistos = set()
    for item in _lista(conteudo):
        credor = item.get("credor") or {}
        chave = (item.get("numero"), item.get("data_assinatura"), credor.get("documento_tipo"), credor.get("documento_numero"))
        if chave in vistos:
            _add(achados, "contratos", "numero", "entidade",
                 "Contrato repetido para o mesmo credor e a mesma data.",
                 "Unifique os contratos com o mesmo número, data e documento do credor.")
        vistos.add(chave)
        _credor_ok(achados, "contratos", credor, "credor")
        naturezas = item.get("natureza_contratacao") or []
        if 23 in naturezas and not (item.get("natureza_contratacao_outro") or "").strip():
            _add(achados, "contratos", "natureza_contratacao_outro", "entidade",
                 "A natureza 23 exige a descrição dos outros serviços.",
                 "Descreva os serviços ou retire o código 23.")
        if int(item.get("criterio_selecao") or 0) == 4 and not (item.get("criterio_selecao_outro") or "").strip():
            _add(achados, "contratos", "criterio_selecao_outro", "entidade",
                 "O critério 4 exige a descrição dos outros critérios.",
                 "Descreva o critério ou escolha outro código.")
        if int(item.get("vigencia_tipo") or 0) == 1 and not item.get("vigencia_data_final"):
            _add(achados, "contratos", "vigencia_data_final", "entidade",
                 "Vigência pré-estabelecida sem data final.",
                 "Informe a data final, que deve ser igual ou posterior ao início e não pode passar de 10 anos.")
        if tipo in (TIPO_GESTAO, TIPO_PARCERIA) and not (item.get("artigo_regulamento_compras") or "").strip():
            _add(achados, "contratos", "artigo_regulamento_compras", "entidade",
                 "Falta o artigo do regulamento de compras.",
                 "Esse campo é obrigatório em Contrato de Gestão e Termo de Parceria.")


def _validar_documentos(achados, documentos, ano, primeira):
    vistos = set()
    for item in documentos:
        credor = item.get("credor") or {}
        chave = (item.get("numero"), credor.get("documento_tipo"), credor.get("documento_numero"))
        if chave in vistos:
            _add(achados, "documentos_fiscais", "numero", "entidade",
                 "Documento fiscal repetido para o mesmo credor.",
                 "Não repita número, tipo e número do documento do credor.")
        vistos.add(chave)
        _credor_ok(achados, "documentos_fiscais", credor, "credor")
        if not primeira and item.get("data_emissao") and not _no_exercicio(item.get("data_emissao"), ano):
            _add(achados, "documentos_fiscais", "data_emissao", "entidade",
                 "A emissão do documento fiscal está fora do exercício.",
                 "Na prestação que não é a primeira do ajuste, a data de emissão precisa cair no ano informado no descritor.")
        bruto = parse_decimal(item.get("valor_bruto"))
        encargos = parse_decimal(item.get("valor_encargos"))
        if encargos is None or bruto is None or encargos < 0 or encargos >= bruto:
            _add(achados, "documentos_fiscais", "valor_encargos", "entidade",
                 "Os encargos retidos estão inconsistentes.",
                 "Informe zero quando não houver retenção. O valor precisa ser maior ou igual a zero e menor que o valor bruto.")
        if int(item.get("categoria_despesas_tipo") or 0) == 75:
            _add(achados, "documentos_fiscais", "categoria_despesas_tipo", "entidade",
                 "A categoria 75 não é aceita.",
                 "O schema 1.9 excluiu a categoria 75 — utilidades públicas, gás. Escolha a categoria de maior valor do documento.")
        if int(item.get("rateio_proveniente_tipo") or 0) == 1 and item.get("rateio_percentual") in (None, ""):
            _add(achados, "documentos_fiscais", "rateio_percentual", "entidade",
                 "Rateio marcado como sim sem percentual.",
                 "Informe o percentual ou marque que o documento não provém de rateio.")


def _validar_pagamentos(achados, pagamentos, documentos, ano):
    chaves_doc = set()
    for doc in documentos:
        credor = doc.get("credor") or {}
        chaves_doc.add((str(doc.get("numero")), int(credor.get("documento_tipo") or 0), somente_digitos(credor.get("documento_numero"))))
    vistos = set()
    for item in pagamentos:
        ident = item.get("identificacao_documento_fiscal") or {}
        credor = ident.get("identificacao_credor") or {}
        numero = str(ident.get("numero") or "")
        chave_doc = (numero, int(credor.get("documento_tipo") or 0), somente_digitos(credor.get("documento_numero")))
        chave = chave_doc + (item.get("pagamento_data"), item.get("pagamento_valor"), item.get("fonte_recurso_tipo"))
        if chave in vistos:
            _add(achados, "pagamentos", "pagamento_valor", "entidade",
                 "Pagamento duplicado.",
                 "Não repita o mesmo documento, data, valor e fonte de recurso.")
        vistos.add(chave)
        if numero != "9999" and chave_doc not in chaves_doc:
            _add(achados, "pagamentos", "identificacao_documento_fiscal", "entidade",
                 f"O pagamento referencia o documento {numero}, que não está na relação de documentos fiscais.",
                 "Inclua o documento fiscal nesta prestação ou, se for folha ordinária, use o número 9999.")
        if not _no_exercicio(item.get("pagamento_data"), ano):
            _add(achados, "pagamentos", "pagamento_data", "entidade",
                 "A data do pagamento está fora do exercício.",
                 "Informe um pagamento dentro do ano do descritor.")
        if int(item.get("meio_pagamento_tipo") or 0) == 1:
            faltas = [nome for nome in ("banco", "agencia", "conta_corrente", "numero_transacao") if not item.get(nome)]
            if faltas:
                _add(achados, "pagamentos", "banco", "entidade",
                     "Pagamento bancário sem os dados da conta.",
                     "Informe banco, agência, conta corrente e número da transação. Na folha ordinária a transação pode ser 9999.")
        if item.get("numero_transacao") and len(str(item.get("numero_transacao"))) > 40:
            _add(achados, "pagamentos", "numero_transacao", "entidade",
                 "O número da transação passa de 40 caracteres.",
                 "Reduza o identificador para no máximo 40 caracteres, conforme o schema 1.11.")


def _validar_glosas(achados, glosas, documentos):
    analisados = set()
    for item in glosas:
        ident = item.get("identificacao_documento_fiscal") or {}
        credor = ident.get("identificacao_credor") or {}
        chave = (str(ident.get("numero")), int(credor.get("documento_tipo") or 0), somente_digitos(credor.get("documento_numero")))
        if chave in analisados and str(ident.get("numero")) != "9999":
            _add(achados, "glosas", "identificacao_documento_fiscal", "gestor",
                 "O mesmo documento fiscal foi analisado mais de uma vez.",
                 "Deixe uma única análise por documento fiscal.")
        analisados.add(chave)
        resultado = int(item.get("resultado_analise") or 0)
        valor = parse_decimal(item.get("valor_glosa"))
        if resultado == 2 and (valor is None or valor <= 0):
            _add(achados, "glosas", "valor_glosa", "gestor",
                 "Aprovado parcialmente sem valor de glosa.",
                 "Informe um valor de glosa maior que zero e menor que o valor bruto do documento.")
        if resultado in (1, 3) and valor not in (None, 0):
            _add(achados, "glosas", "valor_glosa", "gestor",
                 "Valor de glosa informado para resultado que não é parcial.",
                 "No aprovado o valor não deve ser informado. No reprovado ele também não é informado e será considerado o valor bruto.")
    for doc in documentos:
        credor = doc.get("credor") or {}
        chave = (str(doc.get("numero")), int(credor.get("documento_tipo") or 0), somente_digitos(credor.get("documento_numero")))
        if chave not in analisados:
            _add(achados, "glosas", "identificacao_documento_fiscal", "gestor",
                 f"O documento fiscal {doc.get('numero')} não tem análise de glosa.",
                 "Relacione todos os documentos fiscais na seção de glosas, inclusive os aprovados.")


def _validar_empenhos(achados, empenhos, ano, primeira):
    vistos = set()
    for item in empenhos:
        chave = (item.get("numero"), item.get("data_emissao"))
        if chave in vistos:
            _add(achados, "empenhos", "numero", "gestor",
                 "Empenho repetido.",
                 "Não repita o mesmo número e a mesma data de emissão.")
        vistos.add(chave)
        if not cpf_valido(item.get("cpf_ordenador_despesa")):
            _add(achados, "empenhos", "cpf_ordenador_despesa", "gestor",
                 "CPF do ordenador da despesa inválido.",
                 "Informe um CPF válido do ordenador.")
        classificacao = somente_digitos(item.get("classificacao_economica_tipo"))
        if len(classificacao) != 8:
            _add(achados, "empenhos", "classificacao_economica_tipo", "gestor",
                 "A classificação econômica não tem 8 dígitos.",
                 "Informe o código válido para o exercício e para a esfera municipal.")
        if not primeira and not _no_exercicio(item.get("data_emissao"), ano):
            _add(achados, "empenhos", "data_emissao", "gestor",
                 "A emissão do empenho está fora do exercício.",
                 "Fora da primeira prestação do ajuste, a data precisa estar dentro do ano.")


def _validar_repasses(achados, repasses, empenhos, ano, ultimo):
    empenhos_ok = {(str(item.get("numero")), item.get("data_emissao")) for item in empenhos}
    somas = {}
    valores = {str(item.get("numero")): parse_decimal(item.get("valor")) or 0 for item in empenhos}
    for item in repasses:
        ident = item.get("identificacao_empenho") or {}
        chave = (str(ident.get("numero")), ident.get("data_emissao"))
        if chave not in empenhos_ok:
            _add(achados, "repasses", "identificacao_empenho", "gestor",
                 f"O repasse aponta para o empenho {ident.get('numero')}, que não está nesta prestação.",
                 "Inclua o empenho nesta prestação ou use um empenho já informado.")
        data_repasse = parse_data(item.get("data_repasse"))
        data_empenho = parse_data(ident.get("data_emissao"))
        if data_repasse and data_empenho and data_repasse < data_empenho:
            _add(achados, "repasses", "data_repasse", "gestor",
                 "O repasse é anterior à emissão do empenho.",
                 "A data do repasse precisa ser igual ou posterior à emissão do empenho.")
        if data_repasse and not ultimo and data_repasse.year != int(ano):
            _add(achados, "repasses", "data_repasse", "gestor",
                 "A data do repasse está fora do exercício.",
                 "Somente na prestação do último período da vigência a data pode cair no período seguinte.")
        previsto = parse_decimal(item.get("valor_previsto"))
        repassado = parse_decimal(item.get("valor_repasse"))
        if previsto is not None and valores.get(str(ident.get("numero"))) is not None:
            if previsto > valores.get(str(ident.get("numero"))):
                _add(achados, "repasses", "valor_previsto", "gestor",
                     "O valor previsto do repasse é maior que o empenho.",
                     "Reduza o valor previsto para no máximo o valor do empenho.")
        if previsto is not None and repassado is not None and previsto != repassado and not (item.get("justificativa_diferenca_valor") or "").strip():
            _add(achados, "repasses", "justificativa_diferenca_valor", "gestor",
                 "Há diferença entre o valor previsto e o valor repassado sem justificativa.",
                 "Justifique a diferença ou iguale os valores.")
        if int(item.get("tipo_documento_bancario") or 0) == 2 and not (item.get("descricao_outros") or "").strip():
            _add(achados, "repasses", "descricao_outros", "gestor",
                 "Documento bancário do tipo Outros sem descrição.",
                 "Descreva o documento utilizado.")
        somas[str(ident.get("numero"))] = somas.get(str(ident.get("numero")), 0) + (repassado or 0)
    for numero, total in somas.items():
        teto = valores.get(numero)
        if teto is not None and total > teto:
            _add(achados, "repasses", "valor_repasse", "gestor",
                 f"A soma dos repasses do empenho {numero} ultrapassa o valor empenhado.",
                 "Ajuste os valores para que a soma fique dentro do empenho.")


def _validar_receitas(achados, conteudo, ano):
    if not isinstance(conteudo, dict):
        return
    vistos = set()
    for item in conteudo.get("repasses_recebidos") or []:
        chave = (item.get("data_prevista"), item.get("data_repasse"), item.get("fonte_recurso_tipo"))
        if chave in vistos:
            _add(achados, "receitas", "repasses_recebidos", "entidade",
                 "Repasse recebido duplicado.",
                 "Some os valores e deixe um único registro por data prevista, data do repasse e fonte.")
        vistos.add(chave)
        valor = parse_decimal(item.get("valor"))
        if valor is None or valor < parse_decimal("0.01"):
            _add(achados, "receitas", "valor", "entidade",
                 "Repasse recebido abaixo do mínimo.",
                 "O valor mínimo do repasse recebido é R$ 0,01.")
        if not _no_exercicio(item.get("data_repasse"), ano):
            _add(achados, "receitas", "data_repasse", "entidade",
                 "A data do repasse recebido está fora do exercício.",
                 "Informe a data dentro do ano do descritor.")


def _validar_disponibilidades(achados, conteudo):
    if not isinstance(conteudo, dict):
        return
    vistos = set()
    for item in conteudo.get("saldos") or []:
        chave = (item.get("banco"), item.get("agencia"), item.get("conta"), item.get("conta_tipo"))
        if chave in vistos:
            _add(achados, "disponibilidades", "saldos", "entidade",
                 "Saldo bancário repetido.",
                 "Não repita a mesma combinação de banco, agência, conta e tipo.")
        vistos.add(chave)
    if conteudo.get("saldo_fundo_fixo") in (None, ""):
        _add(achados, "disponibilidades", "saldo_fundo_fixo", "entidade",
             "Falta o saldo do fundo fixo em 31/12.",
             "Informe o saldo, mesmo que seja zero.")


def _validar_prestacao_entidade(achados, conteudo, ano, hoje):
    if not isinstance(conteudo, dict):
        return
    inicio = parse_data(conteudo.get("periodo_referencia_data_inicial"))
    fim = parse_data(conteudo.get("periodo_referencia_data_final"))
    conclusao = parse_data(conteudo.get("data_prestacao"))
    if not inicio or not fim or not conclusao:
        _add(achados, "prestacao_contas_entidade_beneficiaria", "data_prestacao", "entidade",
             "As datas da prestação da entidade estão incompletas.",
             "Informe a data de conclusão e o período de referência.")
        return
    if inicio.year != int(ano) or fim.year != int(ano) or inicio > fim:
        _add(achados, "prestacao_contas_entidade_beneficiaria", "periodo_referencia_data_inicial", "entidade",
             "O período de referência não está dentro do exercício.",
             "As duas datas precisam cair no ano da prestação, e o início não pode ser posterior ao fim.")
    if conclusao > hoje or conclusao <= fim:
        _add(achados, "prestacao_contas_entidade_beneficiaria", "data_prestacao", "entidade",
             "A data de conclusão da entidade é inválida.",
             "Ela precisa ser posterior ao fim do período de referência e não pode ser futura.")


def _validar_parecer(achados, conteudo):
    if not isinstance(conteudo, dict):
        return
    conclusao = int(conteudo.get("conclusao_parecer") or 0)
    if conclusao not in (1, 2, 3):
        _add(achados, "parecer_conclusivo", "conclusao_parecer", "gestor",
             "A conclusão do parecer não foi informada.",
             "Use 1 para favorável, 2 para favorável com ressalvas ou 3 para desfavorável.")
    if conclusao == 3 and not (conteudo.get("consideracoes_parecer") or "").strip():
        _add(achados, "parecer_conclusivo", "consideracoes_parecer", "gestor",
             "Parecer desfavorável sem considerações.",
             "Descreva as considerações do parecer conclusivo.")
    declaracoes = {int(item.get("tipo_declaracao") or 0): item for item in conteudo.get("declaracoes") or []}
    for codigo, _titulo in TIPOS_DECLARACAO:
        item = declaracoes.get(codigo)
        if not item:
            _add(achados, "parecer_conclusivo", f"tipo_declaracao_{codigo}", "gestor",
                 f"Falta a declaração {codigo} do parecer conclusivo.",
                 "Informe as sete declarações do artigo 203 da IN 01/2024.")
            continue
        posicao = int(item.get("declaracao") or 0)
        if codigo == 4 and posicao not in (1, 2, 3):
            _add(achados, "parecer_conclusivo", "declaracao", "gestor",
                 "A declaração de encargos trabalhistas está sem posicionamento.",
                 "Responda Sim, Não ou Prejudicado.")
        if codigo != 4 and posicao not in (1, 2):
            _add(achados, "parecer_conclusivo", "declaracao", "gestor",
                 "Há declaração do parecer fora de Sim ou Não.",
                 "Somente a declaração de encargos trabalhistas aceita Prejudicado.")
        precisa = (codigo == 7 and posicao == 1) or (posicao in (2, 3))
        if precisa and not (item.get("justificativa") or "").strip():
            _add(achados, "parecer_conclusivo", "justificativa", "gestor",
                 "Declaração do parecer sem a justificativa exigida.",
                 "Justifique quando a resposta for Não ou Prejudicado. Na aplicação de sanções, justifique também quando a resposta for Sim.")


def _validar_transparencia(achados, conteudo):
    if not isinstance(conteudo, dict):
        return
    mantem = bool(conteudo.get("entidade_beneficiaria_mantem_sitio_internet"))
    sitios = [s for s in (conteudo.get("sitios_internet") or []) if str(s).strip()]
    if mantem and not sitios:
        _add(achados, "transparencia", "sitios_internet", "entidade",
             "A entidade declara que mantém sítio, mas nenhum endereço foi informado.",
             "Inclua ao menos um sítio de internet.")
    if not mantem:
        return
    esperados = (
        ("requisitos_artigos_7o_8o_paragrafo_1o", REQ_ART_7),
        ("requisitos_sitio_artigo_8o_paragrafo_3o", REQ_ART_8),
        ("requisitos_divulgacao_informacoes", REQ_DIVULGACAO),
    )
    for campo, tabela in esperados:
        informados = {int(item.get("requisito") or 0) for item in conteudo.get(campo) or []}
        faltantes = [codigo for codigo, _rotulo in tabela if codigo not in informados]
        if faltantes:
            _add(achados, "transparencia", campo, "entidade",
                 f"Faltam requisitos de transparência: {', '.join(str(n) for n in faltantes)}.",
                 "Responda sim ou não para todos os requisitos do manual quando a entidade mantém sítio.")


def _validar_demonstracoes(achados, conteudo, hoje):
    if not isinstance(conteudo, dict):
        return
    if not conteudo.get("publicacoes"):
        _add(achados, "demonstracoes_contabeis", "publicacoes", "entidade",
             "Não há publicação das demonstrações contábeis.",
             "Informe ao menos um veículo de publicação.")
    responsavel = conteudo.get("responsavel") or {}
    if not crc_valido(responsavel.get("numero_crc")):
        _add(achados, "demonstracoes_contabeis", "numero_crc", "entidade",
             "O CRC do responsável pelas demonstrações é inválido.",
             "Informe o número do CRC, como no exemplo 1SP000001.")
    if not cpf_valido(responsavel.get("cpf")):
        _add(achados, "demonstracoes_contabeis", "cpf", "entidade",
             "O CPF de quem assinou as demonstrações é inválido.",
             "Corrija o CPF do responsável contábil.")
    for pub in conteudo.get("publicacoes") or []:
        if int(pub.get("tipo_veiculo_publicacao") or 0) == 10 and not (pub.get("nome_veiculo") or "").strip():
            _add(achados, "demonstracoes_contabeis", "nome_veiculo", "entidade",
                 "Publicação em veículo Outros sem nome.",
                 "Informe o nome do veículo quando o tipo for 10.")
        data_pub = parse_data(pub.get("data_publicacao"))
        if data_pub and data_pub > hoje:
            _add(achados, "demonstracoes_contabeis", "data_publicacao", "entidade",
                 "Há publicação com data futura.",
                 "A data da publicação não pode ser posterior a hoje.")


def _validar_declaracoes(achados, conteudo, tipo):
    if not isinstance(conteudo, dict):
        return
    if conteudo.get("houve_contratacao_empresas_pertencentes") and not conteudo.get("empresas_pertencentes"):
        _add(achados, "declaracoes", "empresas_pertencentes", "entidade",
             "Foi declarada contratação de empresa pertencente sem identificar a empresa.",
             "Informe CNPJ e CPF do dirigente, ambos válidos.")
    for empresa in conteudo.get("empresas_pertencentes") or []:
        if not cnpj_valido(empresa.get("cnpj")) or not cpf_valido(empresa.get("cpf")):
            _add(achados, "declaracoes", "cnpj", "entidade",
                 "Empresa pertencente com CNPJ ou CPF inválido.",
                 "Corrija os dois documentos.")
    if conteudo.get("houve_participacao_quadro_diretivo_administrativo") and not conteudo.get("participacoes_quadro_diretivo_administrativo"):
        _add(achados, "declaracoes", "participacoes_quadro_diretivo_administrativo", "entidade",
             "Foi declarada participação no quadro diretivo sem a relação de CPFs.",
             "Informe o CPF do dirigente e os CPFs dos contratados.")
    if tipo in (TIPO_GESTAO, TIPO_PARCERIA) and conteudo.get("compras_contratacoes_adequados_regulamento_proprio") is None:
        _add(achados, "declaracoes", "compras_contratacoes_adequados_regulamento_proprio", "entidade",
             "Falta a declaração sobre adequação das compras ao regulamento.",
             "Essa declaração é exigida em Contrato de Gestão e Termo de Parceria.")


def _validar_relatorios_gestor(achados, mapa, tipo):
    mapa_tipo = {
        TIPO_GESTAO: "relatorio_comissao_avaliacao",
        TIPO_CONVENIO: "relatorio_governamental_analise_execucao",
    }
    if tipo in (TIPO_COLAB, TIPO_FOMENTO):
        chave = "relatorio_monitoramento_avaliacao"
    else:
        chave = mapa_tipo.get(tipo)
    if not chave:
        return
    conteudo = _bloco(mapa, chave)
    if not isinstance(conteudo, dict):
        return
    if conteudo.get("houve_emissao_relatorio_final") and int(conteudo.get("conclusao_relatorio") or 0) not in (1, 2, 3):
        _add(achados, chave, "conclusao_relatorio", "gestor",
             "Houve emissão do relatório final sem a conclusão.",
             "Informe favorável sem ressalvas, com ressalvas ou desfavorável.")
    if int(conteudo.get("conclusao_relatorio") or 0) == 3 and not (conteudo.get("justificativa") or "").strip():
        _add(achados, chave, "justificativa", "gestor",
             "Conclusão desfavorável sem justificativa.",
             "Registre a justificativa da conclusão desfavorável.")


def _validar_certidoes(achados, mapa, tipo, conferidas):
    dados = _bloco(mapa, "dados_gerais_entidade_beneficiaria") or {}
    if isinstance(dados, dict):
        for campo in (
            "identificacao_certidao_dados_gerais",
            "identificacao_certidao_corpo_diretivo",
            "identificacao_certidao_membros_conselho",
        ):
            if not str(dados.get(campo) or "").strip():
                _add(achados, "dados_gerais_entidade_beneficiaria", campo, "entidade",
                     "Falta a identificação de uma certidão da entidade.",
                     "Informe o número da certidão concluída no Audesp Fase V.")
        if tipo == TIPO_GESTAO and not str(dados.get("identificacao_certidao_responsaveis") or "").strip():
            _add(achados, "dados_gerais_entidade_beneficiaria", "identificacao_certidao_responsaveis", "entidade",
                 "Contrato de gestão sem a certidão dos responsáveis da entidade gerenciada.",
                 "Informe a certidão exigida somente para contrato de gestão.")
    orgao = _bloco(mapa, "responsaveis_membros_orgao_concessor") or {}
    if isinstance(orgao, dict):
        for campo in (
            "identificacao_certidao_responsaveis",
            "identificacao_certidao_membros_comissao_avaliacao",
            "identificacao_certidao_membros_controle_interno",
        ):
            if not str(orgao.get(campo) or "").strip():
                _add(achados, "responsaveis_membros_orgao_concessor", campo, "gestor",
                     "Falta uma certidão do órgão concessor.",
                     "Informe a identificação da certidão cuja vigência cubra o exercício.")
        if tipo in (TIPO_CONVENIO, TIPO_COLAB, TIPO_FOMENTO) and not str(orgao.get("identificacao_certidao_responsaveis_fiscalizacao_execucao") or "").strip():
            _add(achados, "responsaveis_membros_orgao_concessor", "identificacao_certidao_responsaveis_fiscalizacao_execucao", "gestor",
                 "Falta a certidão da fiscalização da execução.",
                 "Ela é exigida em convênio, termo de colaboração e termo de fomento.")
    if not conferidas:
        _add(achados, "dados_gerais_entidade_beneficiaria", "conferencia_certidoes", "gestor",
             "O gestor ainda não registrou a conferência das certidões no Audesp.",
             "Confirme no Audesp Fase V que as certidões existem, estão concluídas e cobrem o exercício. O SPC não consulta o Audesp.")


def _validar_atas(achados, atas, tipo):
    tipos = [int(item.get("tipo_parecer_ata") or 0) for item in atas]
    if len(tipos) != len(set(tipos)):
        _add(achados, "publicacoes_parecer_ata", "tipo_parecer_ata", "entidade",
             "Há mais de uma ata ou parecer do mesmo tipo.",
             "Informe no máximo um registro de cada tipo.")
    if tipo == TIPO_GESTAO and not ({1, 2} & set(tipos) and 3 in tipos):
        _add(achados, "publicacoes_parecer_ata", "tipo_parecer_ata", "entidade",
             "Contrato de gestão sem conselho e sem auditoria independente.",
             "Informe ao menos um parecer de conselho fiscal ou de administração e o parecer da auditoria independente.")
    if tipo in (TIPO_CONVENIO, TIPO_COLAB, TIPO_FOMENTO) and not ({1, 2} & set(tipos)):
        _add(achados, "publicacoes_parecer_ata", "tipo_parecer_ata", "entidade",
             "Falta parecer ou ata de conselho fiscal ou de administração.",
             "Esse documento é obrigatório para convênio, colaboração e fomento.")
    if tipo == TIPO_PARCERIA and not ({1, 2} & set(tipos) and 4 in tipos):
        _add(achados, "publicacoes_parecer_ata", "tipo_parecer_ata", "entidade",
             "Termo de parceria sem conselho ou sem o Conselho de Políticas Públicas.",
             "Informe o conselho fiscal ou de administração e o parecer do Conselho de Políticas Públicas.")


def _validar_atividades(achados, conteudo):
    if not isinstance(conteudo, dict):
        return
    programas = {}
    for linha in conteudo.get("programas") or []:
        nome = (linha.get("nome_programa") or "").strip()
        codigo = str(linha.get("codigo_meta") or "").strip()
        programas.setdefault(nome, set()).add((codigo, linha.get("periodo")))
        if linha.get("quantidade_realizada") in (None, "") and linha.get("resultado_meta") in (None, ""):
            _add(achados, "relatorio_atividades", "quantidade_realizada", "entidade",
                 f"A meta {codigo} não tem quantidade nem resultado.",
                 "Informe a quantidade realizada nas metas quantificáveis ou o resultado nas metas qualitativas não quantificáveis.")
        if linha.get("meta_atendida") is False and not (linha.get("justificativa") or "").strip():
            _add(achados, "relatorio_atividades", "justificativa", "entidade",
                 f"A meta {codigo} não foi atendida e está sem justificativa.",
                 "Registre a justificativa da meta não atendida.")
        resultado = int(linha.get("resultado_meta") or 0)
        if resultado == 2 and not (linha.get("justificativa_periodo") or "").strip():
            _add(achados, "relatorio_atividades", "justificativa_periodo", "entidade",
                 f"A meta {codigo} foi marcada como não cumprida sem justificativa do período.",
                 "Justifique o não cumprimento no período.")


def _validar_descontos_devolucoes(achados, mapa, ano):
    vistos = set()
    for item in _lista(_bloco(mapa, "descontos")):
        chave = (item.get("data"), item.get("descricao"), item.get("valor"))
        if chave in vistos:
            _add(achados, "descontos", "descricao", "gestor",
                 "Desconto duplicado.",
                 "Some os valores iguais de mesma data e descrição.")
        vistos.add(chave)
        valor = parse_decimal(item.get("valor"))
        if valor is None or valor <= 0:
            _add(achados, "descontos", "valor", "gestor",
                 "Desconto com valor inválido.",
                 "O valor precisa ser maior que zero.")
        if not _no_exercicio(item.get("data"), ano):
            _add(achados, "descontos", "data", "gestor",
                 "A data do desconto está fora do exercício.",
                 "Informe uma data dentro do ano da prestação.")
    vistos = set()
    for item in _lista(_bloco(mapa, "devolucoes")):
        chave = (item.get("data"), item.get("natureza_devolucao_tipo"), item.get("valor"))
        if chave in vistos:
            _add(achados, "devolucoes", "valor", "gestor",
                 "Devolução duplicada.",
                 "Some as devoluções de mesma data, natureza e valor.")
        vistos.add(chave)
        valor = parse_decimal(item.get("valor"))
        if valor is None or valor <= 0:
            _add(achados, "devolucoes", "valor", "gestor",
                 "Devolução com valor inválido.",
                 "O valor precisa ser maior que zero.")
        if not _no_exercicio(item.get("data"), ano):
            _add(achados, "devolucoes", "data", "gestor",
                 "A data da devolução está fora do exercício.",
                 "Informe uma data dentro do ano da prestação.")


def _validar_bens(achados, conteudo, ano, primeira):
    if not isinstance(conteudo, dict) or primeira:
        return
    pares = (
        ("relacao_bens_moveis_adquiridos", "data_aquisicao"),
        ("relacao_bens_moveis_cedidos", "data_cessao"),
        ("relacao_bens_moveis_baixados_devolvidos", "data_baixa_devolucao"),
        ("relacao_bens_imoveis_adquiridos", "data_aquisicao"),
        ("relacao_bens_imoveis_cedidos", "data_cessao"),
        ("relacao_bens_imoveis_baixados_devolvidos", "data_baixa_devolucao"),
    )
    for lista, campo in pares:
        for item in conteudo.get(lista) or []:
            if item.get(campo) and not _no_exercicio(item.get(campo), ano):
                _add(achados, "relacao_bens", campo, "entidade",
                     "Há bem com data fora do exercício.",
                     "Fora da primeira prestação, aquisição, cessão e baixa precisam cair no ano. Na primeira, a data pode ser anterior.")
