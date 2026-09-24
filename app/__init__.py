import hashlib
from pathlib import Path

from flask import Flask, redirect, render_template, send_from_directory, url_for

from app.config import Config
from app.extensions import db, login_manager


def resolve_favicon_file(app: Flask) -> Path:
    static = Path(app.static_folder)
    configured = static / app.config.get("FAVICON_IMAGE", "img/Favicon.ico")
    if configured.exists():
        return configured
    for name in ("Favicon.ico", "Favicon.png", "favicon.ico"):
        fallback = static / "img" / name
        if fallback.exists():
            return fallback
    return configured


def create_app(config_class=Config) -> Flask:
    root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(root / "templates"),
        static_folder=str(root / "static"),
        instance_path=str(root / "instance"),
        instance_relative_config=False,
    )
    app.config.from_object(config_class)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["JSON_DIR"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    from app.blueprints.admin.routes import bp as admin_bp
    from app.blueprints.auth.routes import bp as auth_bp
    from app.blueprints.conferencia.routes import bp as conferencia_bp
    from app.blueprints.dashboard.routes import bp as dashboard_bp
    from app.blueprints.entidades.routes import bp as entidades_bp
    from app.blueprints.prestacoes.routes import bp as prestacoes_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(entidades_bp)
    app.register_blueprint(prestacoes_bp)
    app.register_blueprint(conferencia_bp)
    app.register_blueprint(admin_bp)

    @app.route("/login")
    def login_alias():
        return redirect(url_for("auth.login"))

    @app.route("/favicon.ico")
    def favicon():
        icon = resolve_favicon_file(app)
        return send_from_directory(icon.parent, icon.name, mimetype="image/x-icon")

    @app.template_filter("brl")
    def brl(value):
        from app.utils import money

        return money(value)

    @app.template_filter("dmy")
    def dmy(value):
        from app.utils import rotulo_data

        return rotulo_data(value)

    @app.template_filter("resumo")
    def resumo(valor):
        if isinstance(valor, dict):
            partes = [f"{chave}: {resumo(item)}" for chave, item in valor.items()]
            return "; ".join(partes)
        if isinstance(valor, list):
            return f"{len(valor)} item(ns)"
        if isinstance(valor, bool):
            return "Sim" if valor else "Não"
        if valor in (None, ""):
            return "—"
        return valor

    @app.context_processor
    def inject_globals():
        from datetime import datetime

        from app.models import rotulo_perfil, rotulo_status

        favicon_file = resolve_favicon_file(app)
        if favicon_file.exists():
            favicon_rel = favicon_file.relative_to(Path(app.static_folder)).as_posix()
            favicon_v = hashlib.sha256(favicon_file.read_bytes()).hexdigest()[:12]
            favicon_url = url_for("static", filename=favicon_rel, v=favicon_v)
        else:
            favicon_url = url_for("favicon")

        def badge_status(codigo):
            return {
                "rascunho": "badge-neutral",
                "preenchido": "badge-info",
                "enviado_conferencia": "badge-warning",
                "em_conferencia": "badge-warning",
                "devolvido": "badge-danger",
                "corrigido": "badge-info",
                "validado": "badge-success",
                "json_gerado": "badge-success",
                "json_baixado": "badge-purple",
                "enviado_tce": "badge-success",
            }.get(codigo, "badge-neutral")

        return {
            "app_name": app.config["NOME_SISTEMA"],
            "prefeitura": app.config["PREFEITURA"],
            "orgao": app.config["ORGAO"],
            "versao": app.config["VERSAO"],
            "manual": app.config["MANUAL"],
            "favicon_url": favicon_url,
            "login_hero_image": app.config["LOGIN_HERO_IMAGE"],
            "now": datetime.utcnow(),
            "rotulo_status": rotulo_status,
            "rotulo_perfil": rotulo_perfil,
            "badge_status": badge_status,
        }

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def missing(_e):
        return render_template("errors/403.html", mensagem="O recurso solicitado não foi encontrado."), 404

    with app.app_context():
        db.create_all()
        from app.seed import seed_all

        seed_all()

    return app
