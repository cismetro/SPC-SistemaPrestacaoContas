from flask import abort
from flask_login import current_user

from app.models import PERFIL_ENTIDADE


def exigir_login_perfil(*perfis):
    if not current_user.is_authenticated:
        abort(401)
    if perfis and current_user.perfil not in perfis:
        abort(403)


def pode_ver_prestacao(usuario, prestacao) -> bool:
    if usuario.is_admin or usuario.is_gestor:
        return True
    return usuario.perfil == PERFIL_ENTIDADE and usuario.entidade_id == prestacao.entidade_id


def pode_editar_secao(usuario, prestacao, secao) -> bool:
    if secao["responsavel"] == "entidade":
        return (
            usuario.is_entidade
            and usuario.entidade_id == prestacao.entidade_id
            and prestacao.editavel_entidade
        )
    if secao["responsavel"] == "gestor":
        return usuario.is_gestor and prestacao.editavel_gestor
    return False


def pode_editar_cabecalho(usuario, prestacao) -> bool:
    if usuario.is_admin:
        return True
    return usuario.is_gestor and prestacao.editavel_gestor


def pode_gerar_json(usuario) -> bool:
    if usuario.is_entidade:
        return False
    if usuario.is_gestor:
        return True
    return bool(usuario.is_admin and usuario.pode_gerar_json)


def garantir_prestacao(usuario, prestacao):
    if not pode_ver_prestacao(usuario, prestacao):
        abort(403)
    return prestacao
