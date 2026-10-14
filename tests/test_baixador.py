import subprocess

import pytest

from reels import ErroDownload, baixar_reel


def _resultado(codigo: int, erro: str = ""):
    return subprocess.CompletedProcess([], codigo, stdout="", stderr=erro)


def test_falha_do_yt_dlp_levanta_erro_de_download(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _resultado(1, "bloqueado"))
    with pytest.raises(ErroDownload, match="bloqueado"):
        baixar_reel("https://www.instagram.com/reel/A/", tmp_path)


def test_sucesso_sem_arquivo_levanta_erro_de_download(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _resultado(0))
    with pytest.raises(ErroDownload):
        baixar_reel("https://www.instagram.com/reel/A/", tmp_path)


def test_sucesso_devolve_o_arquivo_baixado(tmp_path, monkeypatch):
    def falso_yt_dlp(*args, **kwargs):
        (tmp_path / "video.mp4").write_bytes(b"x")
        return _resultado(0)

    monkeypatch.setattr(subprocess, "run", falso_yt_dlp)
    caminho = baixar_reel("https://www.instagram.com/reel/A/", tmp_path)
    assert caminho == tmp_path / "video.mp4"


def test_tempo_esgotado_levanta_erro_de_download(tmp_path, monkeypatch):
    def estoura(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="yt-dlp", timeout=1)

    monkeypatch.setattr(subprocess, "run", estoura)
    with pytest.raises(ErroDownload):
        baixar_reel("https://www.instagram.com/reel/A/", tmp_path)
