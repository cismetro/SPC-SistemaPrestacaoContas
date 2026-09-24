import hashlib
from datetime import datetime
from pathlib import Path

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from app.authz import garantir_prestacao, pode_gerar_json
from app.catalogos import ROTAS_AUDESP
from app.extensions import db
from app.json_tce import documento_texto, montar_documento
from app.models import (
    STATUS_BAIXADO,
    STATUS_CONFERENCIA,
    STATUS_DEVOLVIDO,
    STATUS_ENVIADO,
    STATUS_ENVIADO_TCE,
    STATUS_JSON,
    STATUS_VALIDADO,
    ArquivoGerado,
    Pendencia,
    Prestacao,
)
from app.servicos import historico
from app.validacao import validar_prestacao

bp = Blueprint("conferencia", __name__, url_prefix="/conferencia")


def _gestor():
    if not (current_user.is_gestor or current_user.is_admin):
        abort(403)


def _prestacao(item_id):
    _gestor()
    return garantir_prestacao(current_user, db.session.get(Prestacao, item_id) or abort(404))


def _substituir_pendencias(prestacao, achados):
    Pendencia.query.filter_by(prestacao_id=prestacao.id, origem="sistema", status="aberta").delete()
    for achado in achados:
        db.session.add(
            Pendencia(
                prestacao_id=prestacao.id,
                origem="sistema",
                secao=achado["secao"],
                campo=achado["campo"],
                responsavel=achado["responsavel"],
                problema=achado["problema"],
                correcao=achado["correcao"],
                status="aberta",
                criada_por_id=current_user.id,
            )
        )


@bp.route("/<int:item_id>/iniciar", methods=["POST"])
@login_required
def iniciar(item_id):
    prestacao = _prestacao(item_id)
    if not current_user.is_gestor:
        abort(403)
    if prestacao.status == STATUS_ENVIADO:
        prestacao.status = STATUS_CONFERENCIA
        historico(prestacao, current_user, "conferencia", "Gestor iniciou a conferência.")
        db.session.commit()
    return redirect(url_for("prestacoes.detalhe", item_id=prestacao.id))


@bp.route("/<int:item_id>/validar", methods=["POST"])
@login_required
def validar(item_id):
    prestacao = _prestacao(item_id)
    if not current_user.is_gestor:
        abort(403)
    if prestacao.status == STATUS_ENVIADO:
        prestacao.status = STATUS_CONFERENCIA
    achados = validar_prestacao(prestacao)
    _substituir_pendencias(prestacao, achados)
    if achados:
        prestacao.validado_em = None
        if prestacao.status == STATUS_VALIDADO:
            prestacao.status = STATUS_CONFERENCIA
        historico(
            prestacao,
            current_user,
            "validacao_recusada",
            f"{len(achados)} pendência(s) impedem a geração do JSON.",
        )
        db.session.commit()
        flash("A geração do JSON permanece bloqueada. As pendências indicam o campo, a entidade e a correção.", "danger")
        return redirect(url_for("conferencia.pendencias", item_id=prestacao.id))
    prestacao.status = STATUS_VALIDADO
    prestacao.validado_em = datetime.utcnow()
    historico(prestacao, current_user, "validado", "Gestor validou a prestação conforme o Manual do TCE.")
    db.session.commit()
    flash("Prestação validada. O JSON pode ser gerado. O envio ao TCE continua no AUDESP Fase V.", "success")
    return redirect(url_for("conferencia.arquivos", item_id=prestacao.id))


@bp.route("/<int:item_id>/pendencias", methods=["GET", "POST"])
@login_required
def pendencias(item_id):
    prestacao = _prestacao(item_id)
    if request.method == "POST" and current_user.is_gestor:
        problema = (request.form.get("problema") or "").strip()
        correcao = (request.form.get("correcao") or "").strip()
        if not problema or not correcao:
            flash("Descreva o problema e o que precisa ser corrigido.", "danger")
        else:
            db.session.add(
                Pendencia(
                    prestacao_id=prestacao.id,
                    origem="gestor",
                    secao=request.form.get("secao") or "",
                    campo=request.form.get("campo") or "",
                    responsavel=request.form.get("responsavel") or "entidade",
                    problema=problema,
                    correcao=correcao,
                    criada_por_id=current_user.id,
                )
            )
            historico(prestacao, current_user, "pendencia", problema)
            db.session.commit()
            flash("Pendência registrada.", "success")
        return redirect(url_for("conferencia.pendencias", item_id=prestacao.id))
    abertas = [p for p in prestacao.pendencias if p.status == "aberta"]
    return render_template("conferencia/pendencias.html", prestacao=prestacao, pendencias=abertas)


@bp.route("/<int:item_id>/devolver", methods=["POST"])
@login_required
def devolver(item_id):
    prestacao = _prestacao(item_id)
    if not current_user.is_gestor:
        abort(403)
    abertas = [p for p in prestacao.pendencias if p.status == "aberta" and p.responsavel == "entidade"]
    if not abertas:
        flash("Registre ao menos uma pendência da entidade antes de devolver.", "warning")
        return redirect(url_for("conferencia.pendencias", item_id=prestacao.id))
    prestacao.status = STATUS_DEVOLVIDO
    prestacao.validado_em = None
    historico(prestacao, current_user, "devolucao", f"{len(abertas)} pendência(s) devolvidas à entidade.")
    db.session.commit()
    flash("Prestação devolvida para correção da entidade.", "success")
    return redirect(url_for("prestacoes.detalhe", item_id=prestacao.id))


@bp.route("/<int:item_id>/arquivos")
@login_required
def arquivos(item_id):
    prestacao = _prestacao(item_id)
    achados = validar_prestacao(prestacao) if current_user.is_gestor else []
    return render_template(
        "conferencia/arquivos.html",
        prestacao=prestacao,
        achados=achados,
        pode_gerar=pode_gerar_json(current_user),
        rota_audesp=ROTAS_AUDESP.get(prestacao.tipo_documento, ""),
        previa=montar_documento(prestacao) if prestacao.status in {STATUS_VALIDADO, STATUS_JSON, STATUS_BAIXADO, STATUS_ENVIADO_TCE} else None,
    )


@bp.route("/<int:item_id>/gerar", methods=["POST"])
@login_required
def gerar(item_id):
    prestacao = _prestacao(item_id)
    if not pode_gerar_json(current_user):
        abort(403)
    achados = validar_prestacao(prestacao)
    if achados or prestacao.status not in {STATUS_VALIDADO, STATUS_JSON, STATUS_BAIXADO}:
        _substituir_pendencias(prestacao, achados)
        db.session.commit()
        flash("O JSON não foi gerado. Corrija as pendências e valide novamente.", "danger")
        return redirect(url_for("conferencia.pendencias", item_id=prestacao.id))
    texto = documento_texto(prestacao)
    digest = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    pasta = Path(current_app.config["JSON_DIR"])
    pasta.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    nome = f"PC_{prestacao.entidade.codigo}_{prestacao.ano}_{carimbo}.json"
    caminho = pasta / nome
    caminho.write_text(texto, encoding="utf-8")
    for arquivo in prestacao.arquivos:
        arquivo.vigente = False
    gerado = ArquivoGerado(
        prestacao_id=prestacao.id,
        nome=nome,
        caminho=str(caminho),
        sha256=digest,
        gerado_por_id=current_user.id,
        vigente=True,
    )
    db.session.add(gerado)
    prestacao.status = STATUS_JSON
    prestacao.json_gerado_em = datetime.utcnow()
    historico(prestacao, current_user, "json_gerado", f"{nome} · SHA-256 {digest}")
    db.session.commit()
    flash("JSON gerado. Baixe o arquivo e transmita-o você mesmo no AUDESP Fase V. Este sistema não envia ao TCE.", "success")
    return redirect(url_for("conferencia.arquivos", item_id=prestacao.id))


@bp.route("/arquivos/<int:arquivo_id>/baixar")
@login_required
def baixar(arquivo_id):
    _gestor()
    arquivo = db.session.get(ArquivoGerado, arquivo_id) or abort(404)
    prestacao = garantir_prestacao(current_user, arquivo.prestacao)
    if not pode_gerar_json(current_user) and not current_user.is_admin:
        abort(403)
    caminho = Path(arquivo.caminho)
    if not caminho.exists():
        abort(404)
    arquivo.baixado_em = datetime.utcnow()
    arquivo.baixado_por_id = current_user.id
    if prestacao.status == STATUS_JSON:
        prestacao.status = STATUS_BAIXADO
    historico(prestacao, current_user, "json_baixado", arquivo.nome)
    db.session.commit()
    return send_file(caminho, as_attachment=True, download_name=arquivo.nome, mimetype="application/json")


@bp.route("/<int:item_id>/protocolo", methods=["POST"])
@login_required
def protocolo(item_id):
    prestacao = _prestacao(item_id)
    if not current_user.is_gestor:
        abort(403)
    if prestacao.status not in {STATUS_JSON, STATUS_BAIXADO, STATUS_ENVIADO_TCE}:
        flash("Gere e baixe o JSON antes de registrar o envio feito no AUDESP.", "warning")
        return redirect(url_for("conferencia.arquivos", item_id=prestacao.id))
    protocolo_num = (request.form.get("protocolo_audesp") or "").strip()
    if not protocolo_num:
        flash("Informe o protocolo recebido no AUDESP Fase V.", "danger")
        return redirect(url_for("conferencia.arquivos", item_id=prestacao.id))
    prestacao.protocolo_audesp = protocolo_num
    prestacao.status = STATUS_ENVIADO_TCE
    historico(
        prestacao,
        current_user,
        "envio_registrado",
        f"Gestor registrou o protocolo {protocolo_num}. O SPC não transmitiu o arquivo.",
    )
    db.session.commit()
    flash("Protocolo registrado. A transmissão foi feita por você no AUDESP Fase V.", "success")
    return redirect(url_for("conferencia.arquivos", item_id=prestacao.id))
