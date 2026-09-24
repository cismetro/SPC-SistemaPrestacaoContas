from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import PERFIS, Auditoria, Entidade, Historico, Usuario
from app.servicos import auditar

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _so_admin():
    if not current_user.is_admin:
        abort(403)


@bp.route("/usuarios", methods=["GET", "POST"])
@login_required
def usuarios():
    _so_admin()
    if request.method == "POST":
        username = (request.form.get("username") or "").strip().lower()
        nome = (request.form.get("nome") or "").strip()
        senha = request.form.get("password") or ""
        perfil = request.form.get("perfil") or "entidade"
        if perfil not in dict(PERFIS):
            flash("Perfil inválido.", "danger")
            return redirect(url_for("admin.usuarios"))
        if not username or not nome or len(senha) < 6:
            flash("Informe usuário, nome e senha com ao menos 6 caracteres.", "danger")
            return redirect(url_for("admin.usuarios"))
        if Usuario.query.filter_by(username=username).first():
            flash("Esse login já existe.", "danger")
            return redirect(url_for("admin.usuarios"))
        entidade_id = request.form.get("entidade_id") or None
        if perfil == "entidade" and not entidade_id:
            flash("O perfil de entidade precisa estar ligado a uma entidade.", "danger")
            return redirect(url_for("admin.usuarios"))
        if perfil != "entidade":
            entidade_id = None
        usuario = Usuario(
            username=username,
            nome=nome,
            email=(request.form.get("email") or "").strip(),
            perfil=perfil,
            ativo=True,
            pode_gerar_json=perfil == "gestor" or "pode_gerar_json" in request.form,
            entidade_id=int(entidade_id) if entidade_id else None,
        )
        usuario.set_senha(senha)
        db.session.add(usuario)
        auditar(current_user, "usuario_criado", username)
        db.session.commit()
        flash("Usuário criado.", "success")
        return redirect(url_for("admin.usuarios"))
    return render_template(
        "admin/usuarios.html",
        usuarios=Usuario.query.order_by(Usuario.nome).all(),
        entidades=Entidade.query.filter_by(ativa=True).order_by(Entidade.nome_exibicao).all(),
        perfis=PERFIS,
        historico=Historico.query.order_by(Historico.criado_em.desc()).limit(30).all(),
        auditoria=Auditoria.query.order_by(Auditoria.criado_em.desc()).limit(20).all(),
    )


@bp.route("/usuarios/<int:user_id>/alternar", methods=["POST"])
@login_required
def alternar(user_id):
    _so_admin()
    usuario = db.session.get(Usuario, user_id) or abort(404)
    if usuario.username == "admin":
        flash("O administrador principal permanece ativo.", "warning")
        return redirect(url_for("admin.usuarios"))
    usuario.ativo = not usuario.ativo
    auditar(current_user, "usuario_status", f"{usuario.username} ativo={usuario.ativo}")
    db.session.commit()
    flash("Situação do usuário atualizada.", "success")
    return redirect(url_for("admin.usuarios"))
