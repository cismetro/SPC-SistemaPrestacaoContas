from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.authz import garantir_prestacao, pode_editar_cabecalho, pode_editar_secao
from app.catalogos import (
    REQ_ART_7,
    REQ_ART_8,
    REQ_DIVULGACAO,
    TIPOS_DECLARACAO,
    TIPOS_DOCUMENTO,
    PERGUNTAS_DECLARACAO,
    secao_aplica,
    secao_por_chave,
    secoes_visiveis,
)
from app.extensions import db
from app.formularios import ler_campos, ler_grade, resumir_item
from app.json_tce import carregar_payload
from app.models import (
    STATUS_CORRIGIDO,
    STATUS_ENVIADO,
    STATUS_PREENCHIDO,
    STATUS_RASCUNHO,
    Entidade,
    Prestacao,
)
from app.servicos import gravar_bloco, historico, obter_bloco

bp = Blueprint("prestacoes", __name__, url_prefix="/prestacoes")


def _padrao(spec):
    if spec["formato"] == "lista":
        return []
    return {}


def _prestacao_ou_404(item_id):
    prestacao = db.session.get(Prestacao, item_id) or abort(404)
    return garantir_prestacao(current_user, prestacao)


def _payload(prestacao, spec):
    bloco = obter_bloco(prestacao, spec["chave"])
    dados = carregar_payload(bloco) if bloco else None
    if dados is None:
        dados = _padrao(spec)
    return bloco, dados


@bp.route("/")
@login_required
def lista():
    consulta = Prestacao.query
    if current_user.is_entidade:
        consulta = consulta.filter_by(entidade_id=current_user.entidade_id)
    prestacoes = consulta.order_by(Prestacao.ano.desc()).all()
    entidades = []
    if current_user.is_admin or current_user.is_gestor:
        entidades = Entidade.query.filter_by(ativa=True).order_by(Entidade.nome_exibicao).all()
    return render_template("prestacoes/lista.html", prestacoes=prestacoes, entidades=entidades)


@bp.route("/nova", methods=["POST"])
@login_required
def nova():
    if not (current_user.is_admin or current_user.is_gestor or current_user.is_entidade):
        abort(403)
    ano = int(request.form.get("ano") or datetime.utcnow().year)
    entidade_id = current_user.entidade_id
    if current_user.is_admin or current_user.is_gestor:
        entidade_id = int(request.form.get("entidade_id") or 0)
    entidade = db.session.get(Entidade, entidade_id) if entidade_id else None
    if not entidade:
        flash("Selecione a entidade da prestação.", "danger")
        return redirect(url_for("prestacoes.lista"))
    if current_user.is_entidade and entidade.id != current_user.entidade_id:
        abort(403)
    existe = Prestacao.query.filter_by(entidade_id=entidade.id, ano=ano).first()
    if existe:
        flash("Essa entidade já tem prestação neste exercício.", "warning")
        return redirect(url_for("prestacoes.detalhe", item_id=existe.id))
    prestacao = Prestacao(entidade_id=entidade.id, ano=ano, mes=12, status=STATUS_RASCUNHO)
    db.session.add(prestacao)
    db.session.flush()
    historico(prestacao, current_user, "abertura", f"Prestação {ano} aberta.")
    db.session.commit()
    flash("Prestação aberta em rascunho.", "success")
    return redirect(url_for("prestacoes.detalhe", item_id=prestacao.id))


@bp.route("/<int:item_id>")
@login_required
def detalhe(item_id):
    prestacao = _prestacao_ou_404(item_id)
    secoes = secoes_visiveis(prestacao.tipo_documento)
    blocos = {bloco.secao: bloco for bloco in prestacao.blocos}
    return render_template(
        "prestacoes/detalhe.html",
        prestacao=prestacao,
        secoes=secoes,
        blocos=blocos,
        tipos=TIPOS_DOCUMENTO,
        pode_cabecalho=pode_editar_cabecalho(current_user, prestacao),
    )


@bp.route("/<int:item_id>/cabecalho", methods=["POST"])
@login_required
def cabecalho(item_id):
    prestacao = _prestacao_ou_404(item_id)
    if not pode_editar_cabecalho(current_user, prestacao):
        abort(403)
    tipo = request.form.get("tipo_documento") or ""
    if tipo and tipo not in dict(TIPOS_DOCUMENTO):
        flash("Tipo de documento inválido.", "danger")
        return redirect(url_for("prestacoes.detalhe", item_id=prestacao.id))
    prestacao.tipo_documento = tipo or None
    prestacao.codigo_ajuste = (request.form.get("codigo_ajuste") or "").strip() or None
    municipio = (request.form.get("municipio_audesp") or "").strip()
    prestacao.municipio_audesp = int(municipio) if municipio.isdigit() else None
    prestacao.mes = 12
    prestacao.retificacao = "retificacao" in request.form
    prestacao.declaracao_negativa = "declaracao_negativa" in request.form
    prestacao.primeira_prestacao = "primeira_prestacao" in request.form
    prestacao.ultimo_periodo_vigencia = "ultimo_periodo_vigencia" in request.form
    if current_user.is_gestor:
        prestacao.conferencia_codigos_audesp = "conferencia_codigos_audesp" in request.form
        prestacao.conferencia_ajuste = "conferencia_ajuste" in request.form
        prestacao.conferencia_certidoes = "conferencia_certidoes" in request.form
    historico(prestacao, current_user, "cabecalho", "Descritor e código do ajuste atualizados.")
    db.session.commit()
    flash("Cabeçalho da prestação atualizado. O mês do descritor permanece 12.", "success")
    return redirect(url_for("prestacoes.detalhe", item_id=prestacao.id))


@bp.route("/<int:item_id>/enviar", methods=["POST"])
@login_required
def enviar(item_id):
    prestacao = _prestacao_ou_404(item_id)
    if not current_user.is_entidade or current_user.entidade_id != prestacao.entidade_id:
        abort(403)
    if prestacao.status not in {STATUS_RASCUNHO, STATUS_PREENCHIDO, STATUS_CORRIGIDO, "devolvido"}:
        flash("Esta prestação não está em fase de envio pela entidade.", "warning")
        return redirect(url_for("prestacoes.detalhe", item_id=prestacao.id))
    prestacao.status = STATUS_ENVIADO
    prestacao.enviado_em = datetime.utcnow()
    historico(prestacao, current_user, "envio_conferencia", "Entidade enviou os dados para conferência do gestor.")
    db.session.commit()
    flash("Dados enviados para conferência. A geração do JSON continua exclusiva do gestor.", "success")
    return redirect(url_for("prestacoes.detalhe", item_id=prestacao.id))


@bp.route("/<int:item_id>/preenchido", methods=["POST"])
@login_required
def preenchido(item_id):
    prestacao = _prestacao_ou_404(item_id)
    if not current_user.is_entidade or not prestacao.editavel_entidade:
        abort(403)
    if prestacao.status == STATUS_RASCUNHO:
        prestacao.status = STATUS_PREENCHIDO
        historico(prestacao, current_user, "preenchido", "Entidade marcou a prestação como preenchida.")
        db.session.commit()
    return redirect(url_for("prestacoes.detalhe", item_id=prestacao.id))


@bp.route("/<int:item_id>/secoes/<secao>", methods=["GET", "POST"])
@login_required
def secao(item_id, secao):
    prestacao = _prestacao_ou_404(item_id)
    spec = secao_por_chave(secao)
    if not spec or not secao_aplica(spec, prestacao.tipo_documento):
        abort(404)
    if spec["formato"] == "especial":
        destino = "prestacoes.parecer" if secao == "parecer_conclusivo" else "prestacoes.transparencia"
        return redirect(url_for(destino, item_id=prestacao.id))
    bloco, payload = _payload(prestacao, spec)
    editavel = pode_editar_secao(current_user, prestacao, spec)
    if request.method == "POST":
        if not editavel:
            abort(403)
        acao = request.form.get("acao") or ""
        if acao == "sem_movimento" and secao in {
            "demonstracoes_contabeis",
            "parecer_conclusivo",
            "prestacao_contas_entidade_beneficiaria",
            "dados_gerais_entidade_beneficiaria",
            "responsaveis_membros_orgao_concessor",
            "transparencia",
            "declaracoes",
            "disponibilidades",
            "receitas",
        }:
            flash("Esta seção é obrigatória e não pode ser confirmada sem movimento.", "danger")
            return redirect(url_for("prestacoes.secao", item_id=prestacao.id, secao=secao))
        if acao == "sem_movimento":
            gravar_bloco(prestacao, secao, _padrao(spec), current_user, sem_movimento=True)
        elif acao == "com_movimento":
            gravar_bloco(prestacao, secao, payload if payload is not None else _padrao(spec), current_user, False)
        elif spec["formato"] in {"objeto", "flag"} and acao == "salvar":
            dados = ler_campos(request.form, spec.get("campos") or [])
            if isinstance(payload, dict):
                for lista in spec.get("listas") or []:
                    dados[lista["nome"]] = payload.get(lista["nome"]) or []
            gravar_bloco(prestacao, secao, dados, current_user, False)
        elif spec["formato"] == "lista" and acao == "adicionar":
            item = ler_campos(request.form, spec.get("campos") or [])
            for grade in spec.get("grades") or []:
                linhas = ler_grade(request.form, grade)
                if linhas:
                    item[grade["nome"]] = linhas
            if not isinstance(payload, list):
                payload = []
            payload.append(item)
            gravar_bloco(prestacao, secao, payload, current_user, False)
        elif spec["formato"] == "lista" and acao == "excluir":
            indice = int(request.form.get("indice") or -1)
            if isinstance(payload, list) and 0 <= indice < len(payload):
                payload.pop(indice)
            gravar_bloco(prestacao, secao, payload, current_user, False)
        elif acao == "adicionar_sub":
            nome_lista = request.form.get("lista") or ""
            definicao = next((lista for lista in spec.get("listas") or [] if lista["nome"] == nome_lista), None)
            if not definicao or not isinstance(payload, dict):
                abort(400)
            payload.setdefault(nome_lista, [])
            payload[nome_lista].append(ler_campos(request.form, definicao["campos"]))
            gravar_bloco(prestacao, secao, payload, current_user, False)
        elif acao == "excluir_sub":
            nome_lista = request.form.get("lista") or ""
            indice = int(request.form.get("indice") or -1)
            if isinstance(payload, dict) and 0 <= indice < len(payload.get(nome_lista) or []):
                payload[nome_lista].pop(indice)
            gravar_bloco(prestacao, secao, payload, current_user, False)
        else:
            flash("Ação não reconhecida.", "warning")
            return redirect(url_for("prestacoes.secao", item_id=prestacao.id, secao=secao))
        db.session.commit()
        flash("Seção gravada.", "success")
        return redirect(url_for("prestacoes.secao", item_id=prestacao.id, secao=secao))
    return render_template(
        "prestacoes/secao.html",
        prestacao=prestacao,
        spec=spec,
        bloco=bloco,
        payload=payload,
        editavel=editavel,
        resumir_item=resumir_item,
    )


@bp.route("/<int:item_id>/parecer", methods=["GET", "POST"])
@login_required
def parecer(item_id):
    prestacao = _prestacao_ou_404(item_id)
    spec = secao_por_chave("parecer_conclusivo")
    bloco, payload = _payload(prestacao, spec)
    if not isinstance(payload, dict):
        payload = {}
    editavel = pode_editar_secao(current_user, prestacao, spec)
    if request.method == "POST":
        if not editavel:
            abort(403)
        declaracoes = []
        for codigo, _titulo in TIPOS_DECLARACAO:
            declaracoes.append(
                {
                    "tipo_declaracao": codigo,
                    "declaracao": int(request.form.get(f"declaracao_{codigo}") or 0) or None,
                    "justificativa": (request.form.get(f"justificativa_{codigo}") or "").strip(),
                }
            )
        dados = {
            "identificacao_parecer": (request.form.get("identificacao_parecer") or "").strip(),
            "conclusao_parecer": int(request.form.get("conclusao_parecer") or 0) or None,
            "consideracoes_parecer": (request.form.get("consideracoes_parecer") or "").strip(),
            "declaracoes": declaracoes,
        }
        gravar_bloco(prestacao, "parecer_conclusivo", dados, current_user, False)
        db.session.commit()
        flash("Parecer conclusivo gravado.", "success")
        return redirect(url_for("prestacoes.parecer", item_id=prestacao.id))
    atuais = {int(item.get("tipo_declaracao") or 0): item for item in payload.get("declaracoes") or []}
    return render_template(
        "prestacoes/parecer.html",
        prestacao=prestacao,
        spec=spec,
        payload=payload,
        editavel=editavel,
        tipos=TIPOS_DECLARACAO,
        perguntas=PERGUNTAS_DECLARACAO,
        atuais=atuais,
    )


@bp.route("/<int:item_id>/transparencia", methods=["GET", "POST"])
@login_required
def transparencia(item_id):
    prestacao = _prestacao_ou_404(item_id)
    spec = secao_por_chave("transparencia")
    bloco, payload = _payload(prestacao, spec)
    if not isinstance(payload, dict):
        payload = {}
    editavel = pode_editar_secao(current_user, prestacao, spec)
    grupos = (
        ("requisitos_artigos_7o_8o_paragrafo_1o", "Arts. 7º e 8º, § 1º", REQ_ART_7),
        ("requisitos_sitio_artigo_8o_paragrafo_3o", "Art. 8º, § 3º", REQ_ART_8),
        ("requisitos_divulgacao_informacoes", "Divulgação das informações", REQ_DIVULGACAO),
    )
    if request.method == "POST":
        if not editavel:
            abort(403)
        sitios = [linha.strip() for linha in (request.form.get("sitios_internet") or "").splitlines() if linha.strip()]
        dados = {
            "entidade_beneficiaria_mantem_sitio_internet": "mantem" in request.form,
            "sitios_internet": sitios,
        }
        for campo, _titulo, tabela in grupos:
            dados[campo] = [
                {"requisito": codigo, "atende": f"{campo}_{codigo}" in request.form}
                for codigo, _rotulo in tabela
            ]
        gravar_bloco(prestacao, "transparencia", dados, current_user, False)
        db.session.commit()
        flash("Transparência gravada.", "success")
        return redirect(url_for("prestacoes.transparencia", item_id=prestacao.id))
    marcados = {}
    for campo, _titulo, _tabela in grupos:
        marcados[campo] = {
            int(item.get("requisito") or 0)
            for item in (payload.get(campo) or [])
            if item.get("atende")
        }
    return render_template(
        "prestacoes/transparencia.html",
        prestacao=prestacao,
        spec=spec,
        payload=payload,
        editavel=editavel,
        grupos=grupos,
        marcados=marcados,
        sitios="\n".join(payload.get("sitios_internet") or []),
    )


@bp.route("/<int:item_id>/historico")
@login_required
def trilha(item_id):
    prestacao = _prestacao_ou_404(item_id)
    return render_template("prestacoes/historico.html", prestacao=prestacao)
