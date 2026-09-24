"""Catálogo dos blocos do Manual TCE-SP v1.19 (JSON schema 1.14).

Os nomes de campo reproduzem o documento JSON do manual. Códigos numéricos
só entram quando o próprio manual os nomeia.
"""

TIPO_GESTAO = "Prestação de Contas de Contrato de Gestão"
TIPO_CONVENIO = "Prestação de Contas de Convênio"
TIPO_COLAB = "Prestação de Contas de Termo de Colaboração"
TIPO_FOMENTO = "Prestação de Contas de Termo de Fomento"
TIPO_PARCERIA = "Prestação de Contas de Termo de Parceria"

TIPOS_DOCUMENTO = (
    (TIPO_GESTAO, TIPO_GESTAO),
    (TIPO_CONVENIO, TIPO_CONVENIO),
    (TIPO_COLAB, TIPO_COLAB),
    (TIPO_FOMENTO, TIPO_FOMENTO),
    (TIPO_PARCERIA, TIPO_PARCERIA),
)

ROTAS_AUDESP = {
    TIPO_GESTAO: "/f5/enviar-prestacao-contas-contrato-gestao",
    TIPO_CONVENIO: "/f5/enviar-prestacao-contas-convenio",
    TIPO_COLAB: "/f5/enviar-prestacao-contas-termo-colaboracao",
    TIPO_FOMENTO: "/f5/enviar-prestacao-contas-termo-fomento",
    TIPO_PARCERIA: "/f5/enviar-prestacao-contas-termo-parceria",
}

DOC_TIPO = ((1, "1 — CPF"), (2, "2 — CNPJ"), (3, "3 — RNE"))
MEIO_PAGAMENTO = ((1, "1 — Banco"), (2, "2 — Fundo fixo"))
VIGENCIA = ((1, "1 — Pré-estabelecida"),)
VEICULOS = (
    (1, "1 — Diário Oficial do Município"),
    (2, "2 — Diário Oficial do Estado"),
    (3, "3 — Diário Oficial da União"),
    (4, "4 — Diário da Justiça Eletrônico"),
    (5, "5 — Portal Nacional de Compras Públicas"),
    (6, "6 — Jornal de grande circulação nacional"),
    (7, "7 — Jornal de grande circulação regional/municipal"),
    (8, "8 — Quadro ou mural de acesso público"),
    (9, "9 — Site da administração direta na Internet"),
    (10, "10 — Outros"),
)
CONCLUSAO_3 = (
    (1, "1 — Favorável sem ressalvas"),
    (2, "2 — Favorável com ressalvas"),
    (3, "3 — Desfavorável"),
)
CONCLUSAO_PARECER = (
    (1, "1 — Favorável"),
    (2, "2 — Favorável com ressalvas"),
    (3, "3 — Desfavorável"),
)
CONCLUSAO_ATA = CONCLUSAO_3 + (
    (4, "4 — Adverso"),
    (5, "5 — Com abstenção de opinião"),
)
RESULTADO_META = (
    (1, "1 — Cumprida"),
    (2, "2 — Não cumprida"),
    (3, "3 — Cumprida parcialmente"),
)
RESULTADO_GLOSA = (
    (1, "1 — Aprovado"),
    (2, "2 — Aprovado parcialmente"),
    (3, "3 — Reprovado"),
)
TIPO_DOC_BANCARIO = ((1, "1 — Documento bancário"), (2, "2 — Outros"))
POSICIONAMENTO = ((1, "1 — Sim"), (2, "2 — Não"), (3, "3 — Prejudicado"))
TIPO_PARECER_ATA = (
    (1, "1 — Parecer ou Ata do Conselho Fiscal"),
    (2, "2 — Parecer ou Ata do Conselho de Administração"),
    (3, "3 — Parecer da Auditoria Independente"),
    (4, "4 — Parecer do Conselho de Políticas Públicas"),
)
ESTADOS = (
    (12, "AC"), (27, "AL"), (16, "AP"), (13, "AM"), (29, "BA"), (23, "CE"),
    (53, "DF"), (32, "ES"), (52, "GO"), (21, "MA"), (51, "MT"), (50, "MS"),
    (31, "MG"), (15, "PA"), (25, "PB"), (41, "PR"), (26, "PE"), (22, "PI"),
    (33, "RJ"), (24, "RN"), (43, "RS"), (11, "RO"), (14, "RR"), (42, "SC"),
    (35, "SP"), (28, "SE"), (17, "TO"),
)
TIPOS_DECLARACAO = (
    (1, "Cumprimento das cláusulas"),
    (2, "Regularidade dos gastos"),
    (3, "Identificação nos comprovantes"),
    (4, "Regularidade dos recolhimentos dos encargos trabalhistas"),
    (5, "Atendimento aos princípios"),
    (6, "Realização de visita"),
    (7, "Aplicação de sanções"),
)
PERGUNTAS_DECLARACAO = {
    1: "Houve o cumprimento das cláusulas pactuadas em conformidade com a regulamentação que rege a matéria?",
    2: "Houve regularidade dos gastos efetuados e sua perfeita contabilização, atestadas pelo órgão/entidade concessor?",
    3: "Os originais dos comprovantes de gastos contêm a identificação da entidade beneficiária, do tipo de repasse e do número do ajuste, bem como do órgão/entidade repassador(a) a que se referem?",
    4: "Houve regularidade dos recolhimentos de encargos trabalhistas, quando a aplicação dos recursos envolver gastos com pessoal?",
    5: "Houve atendimento aos princípios da legalidade, impessoalidade, moralidade, publicidade, eficiência, motivação e interesse público?",
    6: "Houve realização de visita in loco pelo órgão ou entidade concessor(a)?",
    7: "Houve aplicação de sanções por eventuais ausências de comprovação ou desvio de finalidade?",
}
REQ_ART_7 = (
    (1, "Competência e estrutura organizacional"),
    (2, "Endereço, e-mail, telefones e horários de atendimento"),
    (3, "Registro de quaisquer repasses ou transferências de recursos financeiros"),
    (4, "Registros de despesas realizadas com recursos públicos"),
    (5, "Informações referentes às contratações de bens e serviços"),
    (6, "Informações para subsidiar acompanhamento e resultados de programas"),
    (7, "Respostas a perguntas mais frequentes da sociedade"),
    (8, "Resultado de inspeções, auditorias, prestações e tomadas de contas"),
)
REQ_ART_8 = (
    (1, "Ferramenta de pesquisa de conteúdo"),
    (2, "Geração de relatórios em diversos formatos eletrônicos abertos"),
    (3, "Possibilitar acesso automatizado por sistemas externos em formatos abertos"),
    (4, "Divulga em detalhes os formatos utilizados na estruturação da informação"),
    (5, "Garante a autenticidade e integridade das informações divulgadas"),
    (6, "Atualização periódica"),
)
REQ_DIVULGACAO = (
    (1, "Estatuto social atualizado"),
    (2, "Ajustes (termo de parceria, convênio etc.)"),
    (3, "Plano de trabalho"),
    (4, "Relação nominal dos dirigentes"),
    (5, "Lista de prestadores de serviços e valores pagos"),
    (6, "Remuneração individualizada dos dirigentes e empregados"),
    (7, "Balanços e demonstrações contábeis"),
    (8, "Regulamento de compras"),
    (9, "Regulamento de contratação de pessoal"),
    (10, "Relatório estatístico de atendimento realizado pelo SIC"),
)


def _c(nome, rotulo, tipo="texto", obrigatorio=False, opcoes=None, ajuda="", max_len=None):
    return {
        "nome": nome,
        "rotulo": rotulo,
        "tipo": tipo,
        "obrigatorio": obrigatorio,
        "opcoes": list(opcoes or []),
        "ajuda": ajuda,
        "max_len": max_len,
    }


CREDOR = _c(
    "credor",
    "Credor",
    "objeto",
    True,
    ajuda="documento_tipo 1 = CPF, 2 = CNPJ, 3 = RNE.",
)
CREDOR = {
    **_c("credor", "Credor", "objeto", True),
    "campos": [
        _c("documento_tipo", "Tipo do documento", "escolha", True, DOC_TIPO),
        _c("documento_numero", "Número do documento", "texto", True, ajuda="Somente números para CPF e CNPJ."),
        _c("nome", "Nome ou razão social", "texto", ajuda="Obrigatório quando o documento for RNE."),
    ],
}
IDENT_CREDOR = {
    **_c("identificacao_credor", "Identificação do credor", "objeto", True),
    "campos": [
        _c("documento_tipo", "Tipo do documento", "escolha", True, DOC_TIPO),
        _c("documento_numero", "Número do documento", "texto", True),
    ],
}
PUBLICACAO = [
    _c("tipo_veiculo_publicacao", "Veículo de publicação", "escolha", True, VEICULOS),
    _c("nome_veiculo", "Nome do veículo", "texto", ajuda="Obrigatório quando o veículo for 10 — Outros."),
    _c("data_publicacao", "Data da publicação", "data", True),
    _c("endereco_internet", "Endereço na internet", "texto"),
]
PERIODO_REMUN = [
    _c("mes", "Mês", "inteiro", True),
    _c("carga_horaria", "Carga horária", "decimal", True),
    _c("remuneracao_bruta", "Remuneração bruta", "decimal", True),
]


SECOES = [
    {
        "chave": "relacao_empregados",
        "numero": "5",
        "titulo": "Relação de empregados",
        "responsavel": "entidade",
        "formato": "lista",
        "aplica": "todos",
        "json_chave": "relacao_empregados",
        "ajuda": "Empregado único por CPF e data de admissão. CNS é exigido para CBO do subgrupo 225 (médicos).",
        "campos": [
            _c("cpf", "CPF", "cpf", True),
            _c("data_admissao", "Data de admissão", "data", True),
            _c("data_demissao", "Data de demissão", "data"),
            _c("cbo", "CBO", "texto", True, max_len=6, ajuda="Seis dígitos. Estagiário usa o CBO da função exercida."),
            _c("cns", "CNS", "texto", max_len=15, ajuda="Obrigatório para médicos (CBO 225)."),
            _c("salario_contratual", "Salário contratual", "decimal", True, ajuda="Situação do início do exercício."),
        ],
        "grades": [{"nome": "periodos_remuneracao", "rotulo": "Períodos de remuneração", "campos": PERIODO_REMUN}],
    },
    {
        "chave": "relacao_bens",
        "numero": "6",
        "titulo": "Relação de bens",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": "todos",
        "json_chave": "relacao_bens",
        "listas": [
            {
                "nome": "relacao_bens_moveis_adquiridos",
                "rotulo": "Bens móveis adquiridos",
                "campos": [
                    _c("numero_patrimonio", "Número do patrimônio", "texto", True),
                    _c("descricao", "Descrição", "texto", True),
                    _c("data_aquisicao", "Data de aquisição", "data", True),
                    _c("valor_aquisicao", "Valor de aquisição", "decimal", True),
                ],
            },
            {
                "nome": "relacao_bens_moveis_cedidos",
                "rotulo": "Bens móveis cedidos",
                "campos": [
                    _c("numero_patrimonio", "Número do patrimônio", "texto", True),
                    _c("descricao", "Descrição", "texto", True),
                    _c("data_cessao", "Data da cessão", "data", True),
                    _c("valor_cessao", "Valor da cessão", "decimal", True),
                ],
            },
            {
                "nome": "relacao_bens_moveis_baixados_devolvidos",
                "rotulo": "Bens móveis baixados ou devolvidos",
                "campos": [
                    _c("numero_patrimonio", "Número do patrimônio", "texto", True),
                    _c("data_baixa_devolucao", "Data da baixa ou devolução", "data", True),
                ],
            },
            {
                "nome": "relacao_bens_imoveis_adquiridos",
                "rotulo": "Bens imóveis adquiridos",
                "campos": [
                    _c("descricao", "Descrição", "texto", True),
                    _c("data_aquisicao", "Data de aquisição", "data", True),
                ],
            },
            {
                "nome": "relacao_bens_imoveis_cedidos",
                "rotulo": "Bens imóveis cedidos",
                "campos": [
                    _c("descricao", "Descrição", "texto", True),
                    _c("data_cessao", "Data da cessão", "data", True),
                ],
            },
            {
                "nome": "relacao_bens_imoveis_baixados_devolvidos",
                "rotulo": "Bens imóveis baixados ou devolvidos",
                "campos": [
                    _c("descricao", "Descrição", "texto", True),
                    _c("data_baixa_devolucao", "Data da baixa ou devolução", "data", True),
                ],
            },
        ],
    },
    {
        "chave": "contratos",
        "numero": "7",
        "titulo": "Contratos",
        "responsavel": "entidade",
        "formato": "lista",
        "aplica": "todos",
        "json_chave": "contratos",
        "ajuda": "Informe todos os contratos vigentes no exercício. artigo_regulamento_compras é obrigatório em Contrato de Gestão e Termo de Parceria.",
        "campos": [
            _c("numero", "Número", "texto", True),
            CREDOR,
            _c("data_assinatura", "Data de assinatura", "data", True),
            _c("vigencia_tipo", "Tipo de vigência", "escolha", True, VIGENCIA),
            _c("vigencia_data_inicial", "Início da vigência", "data", True),
            _c("vigencia_data_final", "Fim da vigência", "data", ajuda="Obrigatório quando a vigência for pré-estabelecida."),
            _c("objeto", "Objeto", "texto", True),
            _c("natureza_contratacao", "Natureza da contratação", "inteiros", True, ajuda="Códigos separados por vírgula. 23 = Outros serviços."),
            _c("natureza_contratacao_outro", "Outros serviços", "texto"),
            _c("criterio_selecao", "Critério de seleção", "inteiro", True, ajuda="4 = Outros."),
            _c("criterio_selecao_outro", "Outros critérios", "texto"),
            _c("artigo_regulamento_compras", "Artigo do regulamento de compras", "texto"),
            _c("valor_montante", "Valor", "decimal", True),
            _c("valor_tipo", "Tipo de valor", "inteiro", True),
        ],
    },
    {
        "chave": "documentos_fiscais",
        "numero": "8",
        "titulo": "Documentos fiscais",
        "responsavel": "entidade",
        "formato": "lista",
        "aplica": "todos",
        "json_chave": "documentos_fiscais",
        "ajuda": "Inclui nota, fatura, recibo e guia. Folha ordinária não entra aqui: o pagamento usa o número 9999.",
        "campos": [
            _c("numero", "Número", "texto", True),
            CREDOR,
            {
                **_c("identificacao_contrato", "Contrato vinculado", "objeto"),
                "campos": [
                    _c("numero", "Número do contrato", "texto"),
                    _c("data_assinatura", "Data de assinatura", "data"),
                    IDENT_CREDOR,
                ],
            },
            _c("descricao", "Descrição", "texto", True),
            _c("data_emissao", "Data de emissão", "data", True),
            _c("estado_emissor", "Estado emissor", "escolha", True, ESTADOS),
            _c("valor_bruto", "Valor bruto", "decimal", True),
            _c("valor_encargos", "Encargos retidos", "decimal", True, ajuda="Zero quando não houver retenção. Deve ser menor que o valor bruto."),
            _c("categoria_despesas_tipo", "Categoria de despesa", "inteiro", True, ajuda="Se houver mais de uma, informe a de maior valor. A categoria 75 não é aceita."),
            _c("rateio_proveniente_tipo", "Proveniente de rateio", "escolha", True, ((1, "1 — Sim"), (2, "2 — Não"))),
            _c("rateio_percentual", "Percentual de rateio", "decimal"),
        ],
    },
    {
        "chave": "pagamentos",
        "numero": "9",
        "titulo": "Pagamentos",
        "responsavel": "entidade",
        "formato": "lista",
        "aplica": "todos",
        "json_chave": "pagamentos",
        "ajuda": "Folha ordinária: número do documento e número da transação podem ser 9999. Dados bancários são obrigatórios quando o meio for banco.",
        "campos": [
            {
                **_c("identificacao_documento_fiscal", "Documento fiscal", "objeto", True),
                "campos": [
                    _c("numero", "Número", "texto", True),
                    IDENT_CREDOR,
                ],
            },
            _c("pagamento_data", "Data do pagamento", "data", True),
            _c("pagamento_valor", "Valor", "decimal", True),
            _c("fonte_recurso_tipo", "Fonte de recurso", "inteiro", True, ajuda="Código oficial do schema TCE. O manual v1.19 não reproduz a tabela."),
            _c("meio_pagamento_tipo", "Meio de pagamento", "escolha", True, MEIO_PAGAMENTO),
            _c("banco", "Banco", "inteiro"),
            _c("agencia", "Agência", "inteiro"),
            _c("conta_corrente", "Conta corrente", "texto"),
            _c("numero_transacao", "Número da transação", "texto", max_len=40),
        ],
    },
    {
        "chave": "disponibilidades",
        "numero": "10",
        "titulo": "Disponibilidades",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": "todos",
        "json_chave": "disponibilidades",
        "campos": [_c("saldo_fundo_fixo", "Saldo do fundo fixo em 31/12", "decimal", True)],
        "listas": [
            {
                "nome": "saldos",
                "rotulo": "Saldos bancários em 31/12",
                "campos": [
                    _c("banco", "Banco", "inteiro", True),
                    _c("agencia", "Agência", "inteiro", True),
                    _c("conta", "Conta", "texto", True),
                    _c("conta_tipo", "Tipo de conta", "inteiro", True),
                    _c("saldo_bancario", "Saldo bancário", "decimal", True),
                    _c("saldo_contabil", "Saldo contábil", "decimal", True),
                ],
            }
        ],
    },
    {
        "chave": "receitas",
        "numero": "11",
        "titulo": "Receitas",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": "todos",
        "json_chave": "receitas",
        "campos": [
            _c("receitas_aplic_financ_repasses_publicos_municipais", "Aplicações financeiras — repasses municipais", "decimal", True),
            _c("receitas_aplic_financ_repasses_publicos_estaduais", "Aplicações financeiras — repasses estaduais", "decimal", True),
            _c("receitas_aplic_financ_repasses_publicos_federais", "Aplicações financeiras — repasses federais", "decimal", True),
        ],
        "listas": [
            {
                "nome": "repasses_recebidos",
                "rotulo": "Repasses recebidos",
                "campos": [
                    _c("data_prevista", "Data prevista", "data", True),
                    _c("data_repasse", "Data do repasse", "data", True),
                    _c("valor", "Valor", "decimal", True, ajuda="Mínimo de R$ 0,01."),
                    _c("fonte_recurso_tipo", "Fonte de recurso", "inteiro", True),
                ],
            },
            {
                "nome": "outras_receitas",
                "rotulo": "Outras receitas",
                "campos": [
                    _c("descricao", "Descrição", "texto", True),
                    _c("valor", "Valor", "decimal", True),
                ],
            },
            {
                "nome": "recursos_proprios",
                "rotulo": "Recursos próprios",
                "campos": [
                    _c("descricao", "Descrição", "texto", True),
                    _c("valor", "Valor", "decimal", True),
                ],
            },
        ],
    },
    {
        "chave": "ajustes_saldo",
        "numero": "12",
        "titulo": "Ajustes de saldo",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": "todos",
        "json_chave": "ajustes_saldo",
        "ajuda": "Use somente para corrigir ou incluir repasses e pagamentos de exercícios anteriores.",
        "listas": [
            {
                "nome": "retificacao_repasses",
                "rotulo": "Retificação de repasses",
                "campos": [
                    _c("data_prevista", "Data prevista", "data", True),
                    _c("data_repasse", "Data do repasse", "data", True),
                    _c("fonte_recurso_tipo", "Fonte de recurso", "inteiro", True),
                    _c("valor_retificado", "Valor retificado", "decimal", True, ajuda="Zero cancela o repasse."),
                ],
            },
            {
                "nome": "inclusao_repasses",
                "rotulo": "Inclusão de repasses",
                "campos": [
                    _c("data_prevista", "Data prevista", "data", True),
                    _c("data_repasse", "Data do repasse", "data", True),
                    _c("valor", "Valor", "decimal", True),
                    _c("fonte_recurso_tipo", "Fonte de recurso", "inteiro", True),
                ],
            },
            {
                "nome": "retificacao_pagamentos",
                "rotulo": "Retificação de pagamentos",
                "campos": [
                    {
                        **_c("identificacao_documento_fiscal", "Documento fiscal", "objeto", True),
                        "campos": [_c("numero", "Número", "texto", True), IDENT_CREDOR],
                    },
                    _c("pagamento_data", "Data do pagamento", "data", True),
                    _c("pagamento_valor", "Valor original", "decimal", True),
                    _c("fonte_recurso_tipo", "Fonte de recurso", "inteiro", True),
                    _c("valor_retificado", "Valor retificado", "decimal", True, ajuda="Zero cancela o pagamento."),
                ],
            },
            {
                "nome": "inclusao_pagamentos",
                "rotulo": "Inclusão de pagamentos",
                "campos": [
                    {
                        **_c("identificacao_documento_fiscal", "Documento fiscal", "objeto", True),
                        "campos": [_c("numero", "Número", "texto", True), IDENT_CREDOR],
                    },
                    _c("pagamento_data", "Data", "data", True),
                    _c("pagamento_valor", "Valor", "decimal", True),
                    _c("fonte_recurso_tipo", "Fonte de recurso", "inteiro", True),
                    _c("meio_pagamento_tipo", "Meio de pagamento", "escolha", True, MEIO_PAGAMENTO),
                    _c("banco", "Banco", "inteiro"),
                    _c("agencia", "Agência", "inteiro"),
                    _c("conta_corrente", "Conta corrente", "texto"),
                    _c("numero_transacao", "Número da transação", "texto", max_len=40),
                ],
            },
        ],
    },
    {
        "chave": "servidores_cedidos",
        "numero": "13",
        "titulo": "Servidores cedidos",
        "responsavel": "entidade",
        "formato": "lista",
        "aplica": {"exceto": [TIPO_COLAB, TIPO_FOMENTO]},
        "json_chave": "servidores_cedidos",
        "ajuda": "Não se aplica a Termo de Colaboração nem a Termo de Fomento.",
        "campos": [
            _c("cpf", "CPF", "cpf", True),
            _c("data_inicial_cessao", "Início da cessão", "data", True),
            _c("data_final_cessao", "Fim da cessão", "data"),
            _c("cargo_publico_ocupado", "Cargo público de origem", "texto", True),
            _c("funcao_desempenhada_entidade_beneficiaria", "Função na entidade", "texto", True),
            _c("onus_pagamento", "Ônus do pagamento", "inteiro", True),
        ],
        "grades": [{"nome": "periodos_cessao", "rotulo": "Períodos da cessão", "campos": PERIODO_REMUN}],
    },
    {
        "chave": "descontos",
        "numero": "14",
        "titulo": "Descontos",
        "responsavel": "gestor",
        "formato": "lista",
        "aplica": "todos",
        "json_chave": "descontos",
        "ajuda": "Dedução do repasse por descumprimento de meta. Valor maior que zero.",
        "campos": [
            _c("data", "Data", "data", True),
            _c("descricao", "Descrição", "texto", True),
            _c("valor", "Valor", "decimal", True),
        ],
    },
    {
        "chave": "devolucoes",
        "numero": "15",
        "titulo": "Devoluções",
        "responsavel": "gestor",
        "formato": "lista",
        "aplica": "todos",
        "json_chave": "devolucoes",
        "ajuda": "Glosa devolvida à conta do repasse, glosa devolvida ao concedente ou valor não aplicado.",
        "campos": [
            _c("data", "Data", "data", True),
            _c("natureza_devolucao_tipo", "Natureza da devolução", "inteiro", True),
            _c("valor", "Valor", "decimal", True),
        ],
    },
    {
        "chave": "glosas",
        "numero": "16",
        "titulo": "Glosas",
        "responsavel": "gestor",
        "formato": "lista",
        "aplica": "todos",
        "json_chave": "glosas",
        "ajuda": "Todo documento fiscal precisa de análise, mesmo o aprovado. pagamento_data só entra na folha ordinária.",
        "campos": [
            {
                **_c("identificacao_documento_fiscal", "Documento fiscal", "objeto", True),
                "campos": [_c("numero", "Número", "texto", True), IDENT_CREDOR],
            },
            _c("pagamento_data", "Data do pagamento da folha", "data", ajuda="Somente para folha ordinária."),
            _c("resultado_analise", "Resultado da análise", "escolha", True, RESULTADO_GLOSA),
            _c("valor_glosa", "Valor da glosa", "decimal", ajuda="Obrigatório e maior que zero apenas no aprovado parcialmente."),
        ],
    },
    {
        "chave": "empenhos",
        "numero": "17",
        "titulo": "Empenhos",
        "responsavel": "gestor",
        "formato": "lista",
        "aplica": "todos",
        "json_chave": "empenhos",
        "campos": [
            _c("numero", "Número", "texto", True),
            _c("data_emissao", "Data de emissão", "data", True),
            _c("classificacao_economica_tipo", "Classificação econômica", "texto", True, max_len=8),
            _c("fonte_recurso_tipo", "Fonte de recurso", "inteiro", True),
            _c("valor", "Valor", "decimal", True),
            _c("historico", "Histórico", "texto", True),
            _c("cpf_ordenador_despesa", "CPF do ordenador", "cpf", True),
        ],
    },
    {
        "chave": "repasses",
        "numero": "18",
        "titulo": "Repasses",
        "responsavel": "gestor",
        "formato": "lista",
        "aplica": "todos",
        "json_chave": "repasses",
        "campos": [
            {
                **_c("identificacao_empenho", "Empenho", "objeto", True),
                "campos": [
                    _c("numero", "Número", "texto", True),
                    _c("data_emissao", "Data de emissão", "data", True),
                ],
            },
            _c("data_prevista", "Data prevista", "data", True),
            _c("data_repasse", "Data do repasse", "data", True),
            _c("valor_previsto", "Valor previsto", "decimal", True),
            _c("valor_repasse", "Valor repassado", "decimal", True),
            _c("justificativa_diferenca_valor", "Justificativa da diferença", "texto"),
            _c("tipo_documento_bancario", "Documento bancário", "escolha", True, TIPO_DOC_BANCARIO),
            _c("descricao_outros", "Descrição, se outros", "texto"),
            _c("numero_documento", "Número do documento", "texto", True),
            _c("banco", "Banco", "inteiro", True),
            _c("agencia", "Agência", "inteiro", True),
            _c("conta", "Conta", "texto", True),
        ],
    },
    {
        "chave": "relatorio_atividades",
        "numero": "19",
        "titulo": "Relatório de atividades",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": "todos",
        "json_chave": "relatorio_atividades",
        "listas": [
            {
                "nome": "programas",
                "rotulo": "Programas e metas",
                "campos": [
                    _c("nome_programa", "Programa", "texto", True),
                    _c("codigo_meta", "Código da meta", "texto", True),
                    _c("periodo", "Período", "inteiro", True, ajuda="1 a 12 no mensal; 1 no caso de periodicidade única."),
                    _c("quantidade_realizada", "Quantidade realizada", "decimal", ajuda="Meta quantitativa ou qualitativa quantificável."),
                    _c("resultado_meta", "Resultado da meta", "escolha", opcoes=RESULTADO_META, ajuda="Meta qualitativa não quantificável."),
                    _c("justificativa_periodo", "Justificativa do período", "texto"),
                    _c("meta_atendida", "Meta atendida", "bool", True),
                    _c("justificativa", "Justificativa da meta", "texto", ajuda="Obrigatória quando a meta não for atendida."),
                ],
            }
        ],
    },
    {
        "chave": "dados_gerais_entidade_beneficiaria",
        "numero": "20",
        "titulo": "Dados gerais da entidade",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": "todos",
        "json_chave": "dados_gerais_entidade_beneficiaria",
        "campos": [
            _c("identificacao_certidao_dados_gerais", "Certidão de dados gerais", "texto", True),
            _c("identificacao_certidao_corpo_diretivo", "Certidão do corpo diretivo", "texto", True),
            _c("identificacao_certidao_membros_conselho", "Certidão dos membros do conselho", "texto", True),
            _c("identificacao_certidao_responsaveis", "Certidão dos responsáveis da entidade gerenciada", "texto", ajuda="Somente Contrato de Gestão."),
        ],
    },
    {
        "chave": "responsaveis_membros_orgao_concessor",
        "numero": "21",
        "titulo": "Responsáveis do órgão concessor",
        "responsavel": "gestor",
        "formato": "objeto",
        "aplica": "todos",
        "json_chave": "responsaveis_membros_orgao_concessor",
        "campos": [
            _c("identificacao_certidao_responsaveis", "Certidão dos responsáveis", "texto", True),
            _c("identificacao_certidao_membros_comissao_avaliacao", "Certidão da comissão de avaliação", "texto", True),
            _c("identificacao_certidao_membros_controle_interno", "Certidão do controle interno", "texto", True),
            _c("identificacao_certidao_responsaveis_fiscalizacao_execucao", "Certidão da fiscalização da execução", "texto", ajuda="Convênio, colaboração e fomento."),
        ],
    },
    {
        "chave": "publicacao_regulamento_compras",
        "numero": "22",
        "titulo": "Regulamento de compras",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": {"somente": [TIPO_GESTAO]},
        "json_chave": "publicacao_regulamento_compras",
        "campos": [
            _c("houve_publicacao_inicial", "Houve publicação inicial", "bool", True),
            _c("houve_alteracao_do_regulamento", "Houve alteração do regulamento", "bool", True),
            _c("houve_publicacao_regulamento_alterado", "A alteração foi publicada", "bool"),
        ],
        "listas": [
            {"nome": "publicacoes_regulamento_inicial", "rotulo": "Publicações do regulamento inicial", "campos": PUBLICACAO},
            {"nome": "publicacoes_alteracao_regulamento", "rotulo": "Publicações da alteração", "campos": PUBLICACAO},
        ],
    },
    {
        "chave": "publicacao_extrato_execucao_fisica_financeira",
        "numero": "23",
        "titulo": "Extrato de execução física e financeira",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": {"somente": [TIPO_PARCERIA]},
        "json_chave": "publicacao_extrato_execucao_fisica_financeira",
        "campos": [
            _c("ha_extrato_execucao_fisica_financeira", "Há extrato", "bool", True),
            _c("extrato_elaborado_conforme_modelo", "Extrato conforme o modelo", "bool"),
        ],
        "listas": [{"nome": "publicacoes", "rotulo": "Publicações do extrato", "campos": PUBLICACAO}],
    },
    {
        "chave": "declaracoes",
        "numero": "24",
        "titulo": "Declarações",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": "todos",
        "json_chave": "declaracoes",
        "campos": [
            _c("houve_contratacao_empresas_pertencentes", "Houve contratação de empresas pertencentes", "bool", True),
            _c("houve_participacao_quadro_diretivo_administrativo", "Houve participação no quadro diretivo", "bool", True),
            _c("compras_contratacoes_adequados_regulamento_proprio", "Compras adequadas ao regulamento", "bool", ajuda="Contrato de Gestão e Termo de Parceria."),
        ],
        "listas": [
            {
                "nome": "empresas_pertencentes",
                "rotulo": "Empresas pertencentes",
                "campos": [_c("cnpj", "CNPJ", "cnpj", True), _c("cpf", "CPF do dirigente", "cpf", True)],
            },
            {
                "nome": "participacoes_quadro_diretivo_administrativo",
                "rotulo": "Participações no quadro diretivo",
                "campos": [
                    _c("cpf_dirigente", "CPF do dirigente", "cpf", True),
                    _c("cpf_contratados", "CPFs dos contratados", "cpfs", True, ajuda="Separados por vírgula ou linha."),
                ],
            },
        ],
    },
    {
        "chave": "relatorio_comissao_avaliacao",
        "numero": "25",
        "titulo": "Relatório da comissão de avaliação",
        "responsavel": "gestor",
        "formato": "objeto",
        "aplica": {"somente": [TIPO_GESTAO]},
        "json_chave": "relatorio_comissao_avaliacao",
        "campos": [
            _c("houve_emissao_relatorio_final", "Houve relatório final", "bool", True),
            _c("conclusao_relatorio", "Conclusão", "escolha", opcoes=CONCLUSAO_3),
            _c("justificativa", "Justificativa", "texto"),
        ],
    },
    {
        "chave": "relatorio_governamental_analise_execucao",
        "numero": "26",
        "titulo": "Relatório governamental",
        "responsavel": "gestor",
        "formato": "objeto",
        "aplica": {"somente": [TIPO_CONVENIO]},
        "json_chave": "relatorio_governamental_analise_execucao",
        "campos": [
            _c("houve_emissao_relatorio_final", "Houve relatório final", "bool", True),
            _c("conclusao_relatorio", "Conclusão", "escolha", opcoes=CONCLUSAO_3),
            _c("justificativa", "Justificativa", "texto"),
        ],
    },
    {
        "chave": "relatorio_monitoramento_avaliacao",
        "numero": "27",
        "titulo": "Monitoramento e avaliação",
        "responsavel": "gestor",
        "formato": "objeto",
        "aplica": {"somente": [TIPO_COLAB, TIPO_FOMENTO]},
        "json_chave": "relatorio_monitoramento_avaliacao",
        "campos": [
            _c("houve_emissao_relatorio_final", "Houve relatório final", "bool", True),
            _c("conclusao_relatorio", "Conclusão", "escolha", opcoes=CONCLUSAO_3),
            _c("justificativa", "Justificativa", "texto"),
        ],
    },
    {
        "chave": "demonstracoes_contabeis",
        "numero": "28",
        "titulo": "Demonstrações contábeis",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": "todos",
        "json_chave": "demonstracoes_contabeis",
        "campos": [
            {
                **_c("responsavel", "Responsável pelas demonstrações", "objeto", True),
                "campos": [
                    _c("numero_crc", "CRC", "texto", True),
                    _c("cpf", "CPF", "cpf", True),
                    _c("situacao_regular_crc", "Situação regular no CRC", "bool", True),
                ],
            }
        ],
        "listas": [{"nome": "publicacoes", "rotulo": "Publicações", "campos": PUBLICACAO}],
    },
    {
        "chave": "publicacoes_parecer_ata",
        "numero": "29",
        "titulo": "Pareceres e atas",
        "responsavel": "entidade",
        "formato": "lista",
        "aplica": "todos",
        "json_chave": "publicacoes_parecer_ata",
        "campos": [
            _c("tipo_parecer_ata", "Tipo", "escolha", True, TIPO_PARECER_ATA),
            _c("houve_publicacao", "Houve publicação", "bool", True),
            _c("conclusao_parecer", "Conclusão", "escolha", True, CONCLUSAO_ATA),
        ],
        "grades": [{"nome": "publicacoes", "rotulo": "Publicações", "campos": PUBLICACAO}],
    },
    {
        "chave": "publicacao_relatorio_atividades",
        "numero": "30",
        "titulo": "Publicação do relatório de atividades",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": {"somente": [TIPO_GESTAO]},
        "json_chave": "publicacao_relatorio_atividades",
        "campos": [_c("houve_publicacao_exercicio", "Houve publicação no exercício", "bool", True)],
        "listas": [{"nome": "publicacoes", "rotulo": "Publicações", "campos": PUBLICACAO}],
    },
    {
        "chave": "termo_cessao_permissao_bens",
        "numero": "31",
        "titulo": "Termo de bens cedidos",
        "responsavel": "entidade",
        "formato": "flag",
        "aplica": {"somente": [TIPO_GESTAO]},
        "json_chave": "termo_cessao_permissao_bens",
        "campos": [_c("termo_cessao_permissao_bens", "Foi formalizado termo de cessão ou permissão", "bool", True)],
    },
    {
        "chave": "prestacao_contas_entidade_beneficiaria",
        "numero": "32",
        "titulo": "Prestação da entidade beneficiária",
        "responsavel": "entidade",
        "formato": "objeto",
        "aplica": "todos",
        "json_chave": "prestacao_contas_entidade_beneficiaria",
        "campos": [
            _c("data_prestacao", "Data da conclusão pela entidade", "data", True),
            _c("periodo_referencia_data_inicial", "Início do período de referência", "data", True),
            _c("periodo_referencia_data_final", "Fim do período de referência", "data", True),
        ],
    },
    {
        "chave": "parecer_conclusivo",
        "numero": "33",
        "titulo": "Parecer conclusivo",
        "responsavel": "gestor",
        "formato": "especial",
        "aplica": "todos",
        "json_chave": "parecer_conclusivo",
    },
    {
        "chave": "transparencia",
        "numero": "34",
        "titulo": "Transparência",
        "responsavel": "entidade",
        "formato": "especial",
        "aplica": "todos",
        "json_chave": "transparencia",
    },
    {
        "chave": "retificacao",
        "numero": "35",
        "titulo": "Retificação",
        "responsavel": "gestor",
        "formato": "flag",
        "aplica": "todos",
        "json_chave": "retificacao",
        "campos": [_c("retificacao", "Este JSON substitui uma prestação já armazenada", "bool", True)],
    },
]


def secao_por_chave(chave):
    for secao in SECOES:
        if secao["chave"] == chave:
            return secao
    return None


def secao_aplica(secao, tipo_documento) -> bool:
    regra = secao.get("aplica") or "todos"
    if regra == "todos":
        return True
    if isinstance(regra, dict) and "somente" in regra:
        return tipo_documento in regra["somente"]
    if isinstance(regra, dict) and "exceto" in regra:
        return bool(tipo_documento) and tipo_documento not in regra["exceto"]
    return True


def secoes_visiveis(tipo_documento, responsavel=None):
    itens = [s for s in SECOES if secao_aplica(s, tipo_documento)]
    if responsavel:
        itens = [s for s in itens if s["responsavel"] == responsavel]
    return itens
