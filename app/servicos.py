import json
from datetime import datetime

from app.extensions import db
from app.models import (
    STATUS_CONFERENCIA,
    STATUS_CORRIGIDO,
    STATUS_DEVOLVIDO,
    STATUS_JSON,
    STATUS_VALIDADO,
    Auditoria,
    Bloco,
    Historico,
)


def auditar(usuario, acao, detalhe=""):
    db.session.add(
        Auditoria(
            usuario_id=usuario.id if usuario else None,
            acao=acao,
            detalhe=detalhe,
        )
    )


def historico(prestacao, usuario, acao, detalhe=""):
    db.session.add(
        Historico(
            prestacao_id=prestacao.id if prestacao else None,
            usuario_id=usuario.id if usuario else None,
            entidade_id=prestacao.entidade_id if prestacao else None,
            acao=acao,
            detalhe=detalhe,
        )
    )


def obter_bloco(prestacao, secao):
    return Bloco.query.filter_by(prestacao_id=prestacao.id, secao=secao).first()


def gravar_bloco(prestacao, secao, payload, usuario, sem_movimento=False):
    bloco = obter_bloco(prestacao, secao)
    if not bloco:
        bloco = Bloco(prestacao_id=prestacao.id, secao=secao)
        db.session.add(bloco)
    bloco.payload = json.dumps(payload, ensure_ascii=False)
    bloco.sem_movimento = bool(sem_movimento)
    bloco.atualizado_por_id = usuario.id if usuario else None
    bloco.atualizado_em = datetime.utcnow()
    if prestacao.status == STATUS_DEVOLVIDO and usuario and usuario.is_entidade:
        prestacao.status = STATUS_CORRIGIDO
    if prestacao.status in {STATUS_VALIDADO, STATUS_JSON}:
        prestacao.status = STATUS_CONFERENCIA
        prestacao.validado_em = None
        for arquivo in prestacao.arquivos:
            arquivo.vigente = False
    prestacao.atualizado_em = datetime.utcnow()
    historico(prestacao, usuario, "alteracao", f"Seção {secao} atualizada.")
    return bloco
