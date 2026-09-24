from datetime import datetime
from urllib.parse import urljoin, urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models import Usuario
from app.servicos import auditar

bp = Blueprint("auth", __name__)


def _url_interna(destino):
    if not destino:
        return None
    destino = destino.strip()
    if destino.startswith("//") or "\\" in destino:
        return None
    referencia = urlparse(request.host_url)
    alvo = urlparse(urljoin(request.host_url, destino))
    if alvo.scheme not in ("http", "https") or alvo.netloc != referencia.netloc:
        return None
    if not alvo.path.startswith("/"):
        return None
    return destino


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    username = ""
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        senha = request.form.get("password") or ""
        if not username or not senha:
            flash("Informe usuário e senha para continuar.", "danger")
            return render_template("auth/login.html", username=username)
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and usuario.ativo and usuario.check_senha(senha):
            login_user(usuario, remember="remember" in request.form)
            usuario.ultimo_acesso = datetime.utcnow()
            auditar(usuario, "login", "Acesso ao sistema")
            db.session.commit()
            destino = _url_interna(request.form.get("next") or request.args.get("next"))
            return redirect(destino or url_for("dashboard.index"))
        flash("Usuário ou senha inválidos, ou conta inativa.", "danger")
        return render_template("auth/login.html", username=username)
    return render_template("auth/login.html", username=username)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("auth.login"))
