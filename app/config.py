from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = "spc-cosmopolis-prestacao-contas-2026"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'spc.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_DIR = BASE_DIR / "data" / "json"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    NOME_SISTEMA = "SPC - Sistema de Prestação de Contas"
    PREFEITURA = "Prefeitura Municipal de Cosmópolis - SP"
    ORGAO = "Prestação de contas dos repasses ao terceiro setor"
    VERSAO = "1.0.0"
    LOGIN_HERO_IMAGE = "img/login-hero.png"
    FAVICON_IMAGE = "img/Favicon.ico"
    PORTA = 5735
    MANUAL = "Manual da Prestação de Contas dos Repasses ao Terceiro Setor — v1.19"
    SCHEMA_JSON = "1.14"
