import subprocess
import sys
from pathlib import Path

from processos import rodar_sem_janela
from reels.excecoes import ErroDownload

_LIMITE_SEGUNDOS = 120


def baixar_reel(link: str, pasta: Path) -> Path:
    """Baixa o reel (sem login) para `pasta` e devolve o caminho do arquivo."""
    # Chama o yt-dlp como módulo para usar o mesmo ambiente do projeto.
    comando = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--quiet",
        "--no-warnings",
        "-o",
        str(pasta / "video.%(ext)s"),
        link,
    ]
    try:
        resultado = rodar_sem_janela(comando, timeout=_LIMITE_SEGUNDOS)
    except subprocess.TimeoutExpired as erro:
        raise ErroDownload("O download passou do tempo limite.") from erro

    if resultado.returncode != 0:
        raise ErroDownload(f"O yt-dlp falhou: {resultado.stderr.strip()[-300:]}")

    arquivos = list(pasta.glob("video.*"))
    if not arquivos:
        raise ErroDownload("O yt-dlp terminou sem gerar arquivo de vídeo.")
    return arquivos[0]
