import shutil
import subprocess
from dataclasses import dataclass

import requests

from canal_telegram import ClienteTelegram
from config import Configuracoes
from processos import rodar_sem_janela

_LIMITE_AGY_SEGUNDOS = 60


@dataclass(frozen=True)
class Problema:
    grave: bool
    texto: str


def _checar_agy() -> Problema | None:
    if shutil.which("agy") is None:
        return Problema(True, "O agy (Gemini) não está instalado ou não está no PATH.")
    try:
        # Lista os modelos: só responde com o agy instalado, logado e com rede.
        resultado = rodar_sem_janela(["agy", "models"], timeout=_LIMITE_AGY_SEGUNDOS)
    except subprocess.TimeoutExpired:
        return Problema(True, "O agy não respondeu a tempo. Confira login e internet.")
    if resultado.returncode != 0 or "gemini" not in resultado.stdout.lower():
        return Problema(True, "O agy não está logado. Rode `agy` no terminal e entre.")
    return None


def _checar_telegram(telegram: ClienteTelegram) -> Problema | None:
    try:
        telegram.identificar_bot()
    except requests.RequestException:
        return Problema(True, "O TELEGRAM_TOKEN foi recusado ou o Telegram está fora.")
    return None


def _checar_configuracao(configuracoes: Configuracoes) -> list[Problema]:
    problemas = []
    if configuracoes.telegram_id_autorizado is None:
        problemas.append(
            Problema(False, "TELEGRAM_ID_AUTORIZADO vazio: o bot só vai dizer seu id.")
        )
    pasta = configuracoes.obsidian_pasta_repositorios
    if pasta is not None and not pasta.is_dir():
        problemas.append(
            Problema(False, f"A pasta do Obsidian não existe: {pasta}. Sem notas.")
        )
    if not configuracoes.github_token:
        problemas.append(
            Problema(
                False, "Sem GITHUB_TOKEN: o GitHub limita a 60 consultas por hora."
            )
        )
    return problemas


def verificar_ambiente(
    configuracoes: Configuracoes, telegram: ClienteTelegram
) -> list[Problema]:
    """Confere o que o bot precisa para funcionar; graves impedem de ligar."""
    problemas = [_checar_agy(), _checar_telegram(telegram)]
    return [p for p in problemas if p] + _checar_configuracao(configuracoes)
