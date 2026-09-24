from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


PERFIL_ADMIN = "admin"
PERFIL_GESTOR = "gestor"
PERFIL_ENTIDADE = "entidade"

PERFIS = (
    (PERFIL_ADMIN, "Administrador"),
    (PERFIL_GESTOR, "Gestor"),
    (PERFIL_ENTIDADE, "Entidade"),
)

STATUS_RASCUNHO = "rascunho"
STATUS_PREENCHIDO = "preenchido"
STATUS_ENVIADO = "enviado_conferencia"
STATUS_CONFERENCIA = "em_conferencia"
STATUS_DEVOLVIDO = "devolvido"
STATUS_CORRIGIDO = "corrigido"
STATUS_VALIDADO = "validado"
STATUS_JSON = "json_gerado"
STATUS_BAIXADO = "json_baixado"
STATUS_ENVIADO_TCE = "enviado_tce"

STATUS_PRESTACAO = (
    (STATUS_RASCUNHO, "Rascunho"),
    (STATUS_PREENCHIDO, "Preenchido"),
    (STATUS_ENVIADO, "Enviado para conferência"),
    (STATUS_CONFERENCIA, "Em conferência pelo Gestor"),
    (STATUS_DEVOLVIDO, "Devolvido para correção"),
    (STATUS_CORRIGIDO, "Corrigido pela entidade"),
    (STATUS_VALIDADO, "Validado"),
    (STATUS_JSON, "JSON gerado"),
    (STATUS_BAIXADO, "JSON baixado"),
    (STATUS_ENVIADO_TCE, "Enviado ao TCE"),
)

STATUS_EDITAVEIS_ENTIDADE = {
    STATUS_RASCUNHO,
    STATUS_PREENCHIDO,
    STATUS_DEVOLVIDO,
    STATUS_CORRIGIDO,
}
STATUS_EDITAVEIS_GESTOR = {
    STATUS_ENVIADO,
    STATUS_CONFERENCIA,
    STATUS_CORRIGIDO,
    STATUS_VALIDADO,
    STATUS_JSON,
    STATUS_BAIXADO,
}


def rotulo_status(codigo: str) -> str:
    return dict(STATUS_PRESTACAO).get(codigo, codigo or "—")


def rotulo_perfil(codigo: str) -> str:
    return dict(PERFIS).get(codigo, codigo or "—")


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(160))
    senha_hash = db.Column(db.String(256), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default=PERFIL_ENTIDADE)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    pode_gerar_json = db.Column(db.Boolean, default=False, nullable=False)
    entidade_id = db.Column(db.Integer, db.ForeignKey("entidades.id"))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)

    entidade = db.relationship("Entidade", backref="usuarios")

    def set_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_admin(self) -> bool:
        return self.perfil == PERFIL_ADMIN

    @property
    def is_gestor(self) -> bool:
        return self.perfil == PERFIL_GESTOR

    @property
    def is_entidade(self) -> bool:
        return self.perfil == PERFIL_ENTIDADE

    @property
    def is_active(self) -> bool:
        return bool(self.ativo)

    @property
    def perfil_rotulo(self) -> str:
        return rotulo_perfil(self.perfil)


class Entidade(db.Model):
    __tablename__ = "entidades"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(40), unique=True, nullable=False)
    nome_exibicao = db.Column(db.String(200), nullable=False)
    razao_social = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(18), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(120))
    cidade = db.Column(db.String(120), default="Cosmópolis")
    uf = db.Column(db.String(2), default="SP")
    cep = db.Column(db.String(12))
    telefones = db.Column(db.String(120))
    horario = db.Column(db.String(80))
    email = db.Column(db.String(160))
    email_alternativo = db.Column(db.String(160))
    codigo_audesp = db.Column(db.Integer)
    ativa = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prestacoes = db.relationship("Prestacao", backref="entidade", lazy="dynamic")

    @property
    def cnpj_formatado(self) -> str:
        digitos = "".join(ch for ch in (self.cnpj or "") if ch.isdigit())
        if len(digitos) != 14:
            return self.cnpj or ""
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"


class Prestacao(db.Model):
    __tablename__ = "prestacoes"

    id = db.Column(db.Integer, primary_key=True)
    entidade_id = db.Column(db.Integer, db.ForeignKey("entidades.id"), nullable=False, index=True)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False, default=12)
    tipo_documento = db.Column(db.String(80))
    codigo_ajuste = db.Column(db.String(24))
    municipio_audesp = db.Column(db.Integer)
    status = db.Column(db.String(40), nullable=False, default=STATUS_RASCUNHO, index=True)
    retificacao = db.Column(db.Boolean, default=False, nullable=False)
    declaracao_negativa = db.Column(db.Boolean, default=False, nullable=False)
    primeira_prestacao = db.Column(db.Boolean, default=True, nullable=False)
    ultimo_periodo_vigencia = db.Column(db.Boolean, default=False, nullable=False)
    conferencia_codigos_audesp = db.Column(db.Boolean, default=False, nullable=False)
    conferencia_ajuste = db.Column(db.Boolean, default=False, nullable=False)
    conferencia_certidoes = db.Column(db.Boolean, default=False, nullable=False)
    protocolo_audesp = db.Column(db.String(80))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    enviado_em = db.Column(db.DateTime)
    validado_em = db.Column(db.DateTime)
    json_gerado_em = db.Column(db.DateTime)

    blocos = db.relationship("Bloco", backref="prestacao", cascade="all, delete-orphan")
    pendencias = db.relationship("Pendencia", backref="prestacao", cascade="all, delete-orphan")
    eventos = db.relationship(
        "Historico",
        backref="prestacao",
        cascade="all, delete-orphan",
        order_by="Historico.criado_em.desc()",
    )
    arquivos = db.relationship(
        "ArquivoGerado",
        backref="prestacao",
        cascade="all, delete-orphan",
        order_by="ArquivoGerado.gerado_em.desc()",
    )

    __table_args__ = (db.UniqueConstraint("entidade_id", "ano", name="uq_prestacao_entidade_ano"),)

    @property
    def status_rotulo(self) -> str:
        return rotulo_status(self.status)

    @property
    def editavel_entidade(self) -> bool:
        return self.status in STATUS_EDITAVEIS_ENTIDADE

    @property
    def editavel_gestor(self) -> bool:
        return self.status in STATUS_EDITAVEIS_GESTOR


class Bloco(db.Model):
    __tablename__ = "blocos"

    id = db.Column(db.Integer, primary_key=True)
    prestacao_id = db.Column(db.Integer, db.ForeignKey("prestacoes.id"), nullable=False, index=True)
    secao = db.Column(db.String(80), nullable=False)
    payload = db.Column(db.Text, nullable=False, default="{}")
    sem_movimento = db.Column(db.Boolean, default=False, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    atualizado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

    __table_args__ = (db.UniqueConstraint("prestacao_id", "secao", name="uq_bloco_secao"),)


class Pendencia(db.Model):
    __tablename__ = "pendencias"

    id = db.Column(db.Integer, primary_key=True)
    prestacao_id = db.Column(db.Integer, db.ForeignKey("prestacoes.id"), nullable=False, index=True)
    origem = db.Column(db.String(20), nullable=False, default="sistema")
    secao = db.Column(db.String(80))
    campo = db.Column(db.String(120))
    responsavel = db.Column(db.String(40), nullable=False, default="entidade")
    problema = db.Column(db.Text, nullable=False)
    correcao = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="aberta")
    criada_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)
    resolvida_em = db.Column(db.DateTime)

    autor = db.relationship("Usuario", foreign_keys=[criada_por_id])


class Historico(db.Model):
    __tablename__ = "historicos"

    id = db.Column(db.Integer, primary_key=True)
    prestacao_id = db.Column(db.Integer, db.ForeignKey("prestacoes.id"), index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    entidade_id = db.Column(db.Integer, db.ForeignKey("entidades.id"))
    acao = db.Column(db.String(80), nullable=False)
    detalhe = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    usuario = db.relationship("Usuario")
    entidade = db.relationship("Entidade")


class ArquivoGerado(db.Model):
    __tablename__ = "arquivos_gerados"

    id = db.Column(db.Integer, primary_key=True)
    prestacao_id = db.Column(db.Integer, db.ForeignKey("prestacoes.id"), nullable=False, index=True)
    nome = db.Column(db.String(255), nullable=False)
    caminho = db.Column(db.String(500), nullable=False)
    sha256 = db.Column(db.String(64), nullable=False)
    gerado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    gerado_em = db.Column(db.DateTime, default=datetime.utcnow)
    baixado_em = db.Column(db.DateTime)
    baixado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    vigente = db.Column(db.Boolean, default=True, nullable=False)

    gerado_por = db.relationship("Usuario", foreign_keys=[gerado_por_id])
    baixado_por = db.relationship("Usuario", foreign_keys=[baixado_por_id])


class Auditoria(db.Model):
    __tablename__ = "auditoria"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    acao = db.Column(db.String(80), nullable=False)
    detalhe = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    usuario = db.relationship("Usuario")
