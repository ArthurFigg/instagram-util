import shutil
import subprocess
from pathlib import Path

from processos import rodar_sem_janela


class ErroGemini(Exception):
    """Falha ao chamar o Gemini pelo agy (não achou, travou ou retornou erro)."""


_MODELO = "gemini-3.8-flash"


def executar_agy(pedido: str, pasta: Path, limite_segundos: int) -> str:
    """Roda um pedido no Gemini via agy, dentro de `pasta`, e devolve o texto."""
    agy = shutil.which("agy")
    if agy is None:
        raise ErroGemini("O agy não foi encontrado no PATH.")

    comando = [
        agy,
        "--add-dir",
        str(pasta),
        "--mode",
        "plan",
        "--model",
        _MODELO,
        "--effort",
        "medium",
        "-p",
        pedido,
    ]
    try:
        resultado = rodar_sem_janela(
            comando,
            # O agy é um agente e explora a pasta onde roda. Na pasta do projeto
            # ele lia o código em vez de fazer o pedido e nunca terminava.
            cwd=pasta,
            timeout=limite_segundos,
        )
    except subprocess.TimeoutExpired as erro:
        raise ErroGemini("O Gemini passou do tempo limite.") from erro

    if resultado.returncode != 0:
        raise ErroGemini(f"O agy falhou: {resultado.stderr.strip()[-300:]}")
    return resultado.stdout
