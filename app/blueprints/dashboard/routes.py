from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models import ArquivoGerado, Entidade, Pendencia, Prestacao, rotulo_status

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    consulta = Prestacao.query
    if current_user.is_entidade:
        consulta = consulta.filter_by(entidade_id=current_user.entidade_id)
    prestacoes = consulta.order_by(Prestacao.ano.desc(), Prestacao.id.asc()).all()
    pendencias = []
    if current_user.is_gestor or current_user.is_admin:
        pendencias = (
            Pendencia.query.filter_by(status="aberta")
            .order_by(Pendencia.criada_em.desc())
            .limit(8)
            .all()
        )
    arquivos = []
    if current_user.is_gestor or current_user.is_admin:
        arquivos = ArquivoGerado.query.order_by(ArquivoGerado.gerado_em.desc()).limit(6).all()
    em_conferencia = sum(1 for item in prestacoes if item.status in {"enviado_conferencia", "em_conferencia"})
    validadas = sum(
        1
        for item in prestacoes
        if item.status in {"validado", "json_gerado", "json_baixado", "enviado_tce"}
    )
    return render_template(
        "dashboard/index.html",
        prestacoes=prestacoes,
        entidades=Entidade.query.filter_by(ativa=True).order_by(Entidade.nome_exibicao).all(),
        pendencias=pendencias,
        arquivos=arquivos,
        em_conferencia=em_conferencia,
        validadas=validadas,
        rotulo_status=rotulo_status,
    )
