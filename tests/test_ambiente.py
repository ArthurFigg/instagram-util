import shutil
import subprocess
from pathlib import Path

import requests

import ambiente
from ambiente import verificar_ambiente
from config import Configuracoes


class _TelegramFalso:
    def __init__(self, falha: bool = False):
        self.falha = falha

    def identificar_bot(self) -> str:
        if self.falha:
            raise requests.HTTPError("401")
        return "meu_bot"


def _configuracoes(**mudancas) -> Configuracoes:
    base = {
        "telegram_token": "x",
        "telegram_id_autorizado": 1,
        "github_token": "y",
    }
    return Configuracoes(_env_file=None, **{**base, **mudancas})  # pyright: ignore


def _agy_ok(monkeypatch, saida: str = "gemini-3.8-flash-medium", codigo: int = 0):
    monkeypatch.setattr(shutil, "which", lambda nome: "agy")
    resposta = subprocess.CompletedProcess([], codigo, stdout=saida, stderr="")
    monkeypatch.setattr(ambiente, "rodar_sem_janela", lambda *a, **k: resposta)


def _verificar(telegram=None, **config):
    return verificar_ambiente(_configuracoes(**config), telegram or _TelegramFalso())  # pyright: ignore


def test_ambiente_completo_nao_tem_problemas(monkeypatch):
    _agy_ok(monkeypatch)
    assert _verificar() == []


def test_agy_ausente_e_problema_grave(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda nome: None)
    problemas = _verificar()
    assert problemas[0].grave and "não está instalado" in problemas[0].texto


def test_agy_que_falha_ao_listar_modelos_e_problema_grave_de_login(monkeypatch):
    _agy_ok(monkeypatch, saida="", codigo=1)
    problemas = _verificar()
    assert problemas[0].grave and "não está logado" in problemas[0].texto


def test_agy_que_estoura_o_tempo_e_problema_grave(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda nome: "agy")

    def estoura(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="agy", timeout=1)

    monkeypatch.setattr(ambiente, "rodar_sem_janela", estoura)
    assert _verificar()[0].grave


def test_token_do_telegram_recusado_e_problema_grave(monkeypatch):
    _agy_ok(monkeypatch)
    problemas = _verificar(telegram=_TelegramFalso(falha=True))
    assert problemas[0].grave and "TELEGRAM_TOKEN" in problemas[0].texto


def test_id_autorizado_vazio_e_so_aviso(monkeypatch):
    _agy_ok(monkeypatch)
    problemas = _verificar(telegram_id_autorizado=None)
    assert [p.grave for p in problemas] == [False]


def test_pasta_do_obsidian_inexistente_e_so_aviso(monkeypatch, tmp_path):
    _agy_ok(monkeypatch)
    problemas = _verificar(obsidian_pasta_repositorios=Path(tmp_path / "nao-existe"))
    assert [p.grave for p in problemas] == [False]


def test_sem_token_do_github_e_so_aviso(monkeypatch):
    _agy_ok(monkeypatch)
    problemas = _verificar(github_token=None)
    assert [p.grave for p in problemas] == [False]
