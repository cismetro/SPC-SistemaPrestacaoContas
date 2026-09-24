from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import PERFIL_ADMIN, Entidade, Prestacao
from app.servicos import auditar
from app.utils import cnpj_valido, somente_digitos

bp = Blueprint("entidades", __name__, url_prefix="/entidades")


def _so_admin():
    if not current_user.is_admin:
        abort(403)


def _ler_form():
    return {
        "codigo": (request.form.get("codigo") or "").strip().upper(),
        "nome_exibicao": (request.form.get("nome_exibicao") or "").strip(),
        "razao_social": (request.form.get("razao_social") or "").strip(),
        "cnpj": somente_digitos(request.form.get("cnpj")),
        "endereco": (request.form.get("endereco") or "").strip(),
        "bairro": (request.form.get("bairro") or "").strip(),
        "cidade": (request.form.get("cidade") or "").strip() or "Cosmópolis",
        "uf": (request.form.get("uf") or "SP").strip().upper()[:2],
        "cep": (request.form.get("cep") or "").strip(),
        "telefones": (request.form.get("telefones") or "").strip(),
        "horario": (request.form.get("horario") or "").strip(),
        "email": (request.form.get("email") or "").strip(),
        "email_alternativo": (request.form.get("email_alternativo") or "").strip(),
        "codigo_audesp": request.form.get("codigo_audesp") or None,
        "ativa": "ativa" in request.form,
    }


@bp.route("/")
@login_required
def lista():
    if current_user.perfil != PERFIL_ADMIN and not current_user.is_gestor:
        abort(403)
    entidades = Entidade.query.order_by(Entidade.nome_exibicao).all()
    return render_template("entidades/lista.html", entidades=entidades)


@bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova():
    _so_admin()
    if request.method == "POST":
        dados = _ler_form()
        if not dados["nome_exibicao"] or not dados["codigo"] or not cnpj_valido(dados["cnpj"]):
            flash("Informe código, nome e um CNPJ válido.", "danger")
            return render_template("entidades/form.html", entidade=dados)
        if Entidade.query.filter_by(codigo=dados["codigo"]).first():
            flash("Já existe entidade com esse código.", "danger")
            return render_template("entidades/form.html", entidade=dados)
        entidade = Entidade(**dados)
        if dados["codigo_audesp"]:
            entidade.codigo_audesp = int(dados["codigo_audesp"])
        db.session.add(entidade)
        auditar(current_user, "entidade_criada", entidade.nome_exibicao)
        db.session.commit()
        flash("Entidade cadastrada.", "success")
        return redirect(url_for("entidades.lista"))
    return render_template("entidades/form.html", entidade=None)


@bp.route("/<int:item_id>/editar", methods=["GET", "POST"])
@login_required
def editar(item_id):
    _so_admin()
    entidade = db.session.get(Entidade, item_id) or abort(404)
    if request.method == "POST":
        dados = _ler_form()
        if not dados["nome_exibicao"] or not cnpj_valido(dados["cnpj"]):
            flash("Nome e CNPJ válido são obrigatórios.", "danger")
            return render_template("entidades/form.html", entidade=entidade)
        outra = Entidade.query.filter(Entidade.codigo == dados["codigo"], Entidade.id != entidade.id).first()
        if outra:
            flash("Já existe entidade com esse código.", "danger")
            return render_template("entidades/form.html", entidade=entidade)
        for campo, valor in dados.items():
            if campo == "codigo_audesp":
                entidade.codigo_audesp = int(valor) if valor else None
            else:
                setattr(entidade, campo, valor)
        entidade.atualizado_em = datetime.utcnow()
        auditar(current_user, "entidade_alterada", entidade.nome_exibicao)
        db.session.commit()
        flash("Entidade atualizada.", "success")
        return redirect(url_for("entidades.lista"))
    return render_template("entidades/form.html", entidade=entidade)


@bp.route("/<int:item_id>/excluir", methods=["POST"])
@login_required
def excluir(item_id):
    _so_admin()
    entidade = db.session.get(Entidade, item_id) or abort(404)
    if Prestacao.query.filter_by(entidade_id=entidade.id).count():
        entidade.ativa = False
        auditar(current_user, "entidade_inativada", entidade.nome_exibicao)
        db.session.commit()
        flash("A entidade tem prestação de contas e foi inativada.", "warning")
        return redirect(url_for("entidades.lista"))
    nome = entidade.nome_exibicao
    db.session.delete(entidade)
    auditar(current_user, "entidade_excluida", nome)
    db.session.commit()
    flash("Entidade excluída.", "success")
    return redirect(url_for("entidades.lista"))
