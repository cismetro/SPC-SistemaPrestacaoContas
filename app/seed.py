from datetime import datetime

from app.extensions import db
from app.models import PERFIL_ADMIN, PERFIL_ENTIDADE, PERFIL_GESTOR, Entidade, Prestacao, Usuario


ENTIDADES = [
    {
        "codigo": "APAE",
        "nome_exibicao": "APAE - Cosmópolis",
        "razao_social": "APAE - Cosmópolis",
        "cnpj": "54127931000184",
        "endereco": "R. Antônio de Souza Peres, 1175",
        "bairro": "Jardim Planalto",
        "cidade": "Cosmópolis",
        "uf": "SP",
        "cep": "13152-112",
        "telefones": "(19) 3872-6597",
        "horario": "Aberto até as 16h",
        "email": "administrativo@apaecosmopolis.org.br",
        "email_alternativo": "apaecosmopolis@hotmail.com.br",
    },
    {
        "codigo": "HOSPITAL",
        "nome_exibicao": "Hospital Beneficente Santa Gertrudes",
        "razao_social": "Hospital Beneficente Santa Gertrudes",
        "cnpj": "47368675000151",
        "endereco": "Rua Max Hergert, 978",
        "bairro": "Jardim Bela Vista",
        "cidade": "Cosmópolis",
        "uf": "SP",
        "cep": "13150-130",
        "telefones": "(19) 3872-1458 e (19) 3812-8300",
        "horario": "",
        "email": "",
        "email_alternativo": "",
    },
]


def _entidade(dados):
    entidade = Entidade.query.filter_by(codigo=dados["codigo"]).first()
    if not entidade:
        entidade = Entidade(codigo=dados["codigo"])
        db.session.add(entidade)
    for campo, valor in dados.items():
        setattr(entidade, campo, valor)
    entidade.ativa = True
    return entidade


def _usuario(username, nome, perfil, senha, email="", entidade=None, pode_gerar=False):
    usuario = Usuario.query.filter_by(username=username).first()
    if usuario:
        if entidade and not usuario.entidade_id:
            usuario.entidade_id = entidade.id
        return usuario
    usuario = Usuario(
        username=username,
        nome=nome,
        email=email,
        perfil=perfil,
        ativo=True,
        pode_gerar_json=pode_gerar,
        entidade_id=entidade.id if entidade else None,
    )
    usuario.set_senha(senha)
    db.session.add(usuario)
    return usuario


def seed_all() -> None:
    apae = _entidade(ENTIDADES[0])
    hospital = _entidade(ENTIDADES[1])
    db.session.flush()

    _usuario("admin", "Administrador SPC", PERFIL_ADMIN, "admin123", "admin@cosmopolis.sp.gov.br")
    _usuario(
        "gestor",
        "Gestor da Secretaria",
        PERFIL_GESTOR,
        "gestor123",
        "gestor@cosmopolis.sp.gov.br",
        pode_gerar=True,
    )
    _usuario(
        "apae",
        "APAE - Cosmópolis",
        PERFIL_ENTIDADE,
        "apae123",
        "administrativo@apaecosmopolis.org.br",
        apae,
    )
    _usuario(
        "hospital",
        "Hospital Beneficente Santa Gertrudes",
        PERFIL_ENTIDADE,
        "hospital123",
        "",
        hospital,
    )

    ano = datetime.utcnow().year
    for entidade in (apae, hospital):
        existe = Prestacao.query.filter_by(entidade_id=entidade.id, ano=ano).first()
        if not existe:
            db.session.add(
                Prestacao(
                    entidade_id=entidade.id,
                    ano=ano,
                    mes=12,
                    status="rascunho",
                    primeira_prestacao=True,
                )
            )
    db.session.commit()
