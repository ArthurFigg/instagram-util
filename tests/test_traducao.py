from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import fluxo
from gemini import ErroGemini, traduzir_para_portugues
from gemini import traducao as modulo_traducao
from github import linhas_de_descricao, montar_ficha


def _ficha(descricao_pt: str = ""):
    agora = datetime.now(UTC)
    dados = {
        "owner": {"login": "dono"},
        "name": "projeto",
        "html_url": "https://github.com/dono/projeto",
        "description": "A tool for videos",
        "stargazers_count": 1,
        "forks_count": 1,
        "created_at": (agora - timedelta(days=1)).isoformat(),
        "pushed_at": agora.isoformat(),
        "license": None,
        "archived": False,
    }
    ficha = montar_ficha(dados, 0, 0, True)
    return (
        ficha if not descricao_pt else fluxo.replace(ficha, descricao_pt=descricao_pt)
    )


def _agy_responde(monkeypatch, texto: str):
    def falso(pedido: str, pasta: Path, limite: int) -> str:
        return texto

    monkeypatch.setattr(modulo_traducao, "executar_agy", falso)


def test_traducao_devolve_a_resposta_do_gemini_sem_espacos_nas_pontas(monkeypatch):
    _agy_responde(monkeypatch, "  Uma ferramenta para vídeos \n")
    assert traduzir_para_portugues("A tool for videos") == "Uma ferramenta para vídeos"


def test_traducao_vazia_levanta_erro(monkeypatch):
    _agy_responde(monkeypatch, "  ")
    with pytest.raises(ErroGemini):
        traduzir_para_portugues("A tool for videos")


def test_traducao_enorme_levanta_erro_pois_o_modelo_explicou_em_vez_de_traduzir(
    monkeypatch,
):
    _agy_responde(monkeypatch, "x" * 500)
    with pytest.raises(ErroGemini):
        traduzir_para_portugues("A tool")


def test_descricao_traduzida_mostra_a_traducao_e_o_original():
    linhas = linhas_de_descricao(_ficha("Uma ferramenta para vídeos"))
    assert linhas == ["Uma ferramenta para vídeos", "(original: A tool for videos)"]


def test_descricao_sem_traducao_mostra_so_o_original():
    assert linhas_de_descricao(_ficha()) == ["A tool for videos"]


def test_falha_na_traducao_mantem_a_ficha_com_o_original(monkeypatch):
    def quebra(texto: str) -> str:
        raise ErroGemini("travou")

    monkeypatch.setattr(fluxo, "traduzir_para_portugues", quebra)
    assert fluxo.traduzir_descricao(_ficha()).descricao_pt == ""


def test_traducao_com_sucesso_preenche_a_descricao_em_portugues(monkeypatch):
    monkeypatch.setattr(
        fluxo, "traduzir_para_portugues", lambda texto: "Uma ferramenta"
    )
    assert fluxo.traduzir_descricao(_ficha()).descricao_pt == "Uma ferramenta"
