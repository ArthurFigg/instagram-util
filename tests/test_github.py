from datetime import UTC, datetime, timedelta

import pytest

from github import (
    FichaProjeto,
    buscar_ficha,
    extrair_dono_nome,
    extrair_usuario,
    formatar_ficha,
    montar_ficha,
)
from reels import ProjetoCitado


def _dados_repo(**mudancas) -> dict:
    agora = datetime.now(UTC)
    dados = {
        "owner": {"login": "dono"},
        "name": "projeto",
        "html_url": "https://github.com/dono/projeto",
        "description": "uma ferramenta",
        "stargazers_count": 10,
        "forks_count": 2,
        "created_at": (agora - timedelta(days=30)).isoformat(),
        "pushed_at": (agora - timedelta(days=3)).isoformat(),
        "license": {"spdx_id": "MIT"},
        "archived": False,
    }
    return {**dados, **mudancas}


class _GithubFalso:
    def __init__(self, por_endereco=None, por_busca=None, por_busca_com_dono=None):
        self.por_endereco = por_endereco
        self.por_busca = por_busca
        self.por_busca_com_dono = por_busca_com_dono
        self.buscas: list[str | None] = []

    def obter_repositorio(self, dono, nome):
        return self.por_endereco

    def buscar_repositorio(self, nome, dono=None):
        self.buscas.append(dono)
        if dono:
            return self.por_busca_com_dono
        return self.por_busca

    def contar_commits_recentes(self, dono, nome, dias):
        return 7

    def contar_contribuidores(self, dono, nome):
        return 3


@pytest.mark.parametrize(
    ("endereco", "esperado"),
    [
        ("github.com/public-apis/public-apis", ("public-apis", "public-apis")),
        ("https://github.com/dono/repo.git", ("dono", "repo")),
        ("apilayer.com", None),
        ("", None),
    ],
)
def test_extrair_dono_nome_le_so_enderecos_do_github(endereco, esperado):
    assert extrair_dono_nome(endereco) == esperado


def test_ficha_sem_licenca_diz_sem_licenca():
    ficha = montar_ficha(_dados_repo(license=None), 0, 0, True)
    assert ficha.licenca == "sem licença"


def test_endereco_que_existe_gera_ficha_confirmada():
    github = _GithubFalso(por_endereco=_dados_repo())
    projeto = ProjetoCitado("projeto", "github.com/dono/projeto", "tela")
    ficha = buscar_ficha(github, projeto)  # pyright: ignore[reportArgumentType]
    assert ficha is not None and ficha.confirmado


def test_sem_endereco_usa_busca_e_marca_como_nao_confirmada():
    github = _GithubFalso(por_busca=_dados_repo())
    projeto = ProjetoCitado("projeto", "", "fala")
    ficha = buscar_ficha(github, projeto)  # pyright: ignore[reportArgumentType]
    assert ficha is not None and not ficha.confirmado


def test_nome_e_criador_achados_geram_ficha_confirmada():
    github = _GithubFalso(por_busca_com_dono=_dados_repo())
    projeto = ProjetoCitado("projeto", "", "tela", criador="@dono")
    ficha = buscar_ficha(github, projeto)  # pyright: ignore[reportArgumentType]
    assert ficha is not None and ficha.confirmado


def test_busca_com_criador_usa_o_usuario_sem_arroba():
    github = _GithubFalso(por_busca_com_dono=_dados_repo())
    projeto = ProjetoCitado("projeto", "", "tela", criador="@dono")
    buscar_ficha(github, projeto)  # pyright: ignore[reportArgumentType]
    assert github.buscas == ["dono"]


def test_criador_sem_resultado_cai_na_busca_so_pelo_nome_nao_confirmada():
    github = _GithubFalso(por_busca=_dados_repo())
    projeto = ProjetoCitado("projeto", "", "tela", criador="dono")
    ficha = buscar_ficha(github, projeto)  # pyright: ignore[reportArgumentType]
    assert ficha is not None and not ficha.confirmado


@pytest.mark.parametrize(
    ("criador", "esperado"),
    [
        ("@pablostanley", "pablostanley"),
        ("pablostanley", "pablostanley"),
        ("Pablo Stanley", None),
        ("", None),
        ("@", None),
    ],
)
def test_extrair_usuario_aceita_so_usuario_valido_do_github(criador, esperado):
    assert extrair_usuario(criador) == esperado


def test_nada_no_endereco_nem_na_busca_devolve_none():
    projeto = ProjetoCitado("fantasma", "github.com/x/y", "tela")
    assert buscar_ficha(_GithubFalso(), projeto) is None  # pyright: ignore[reportArgumentType]


def _ficha(**mudancas) -> FichaProjeto:
    return montar_ficha(_dados_repo(**mudancas), 7, 3, True)


def test_ficha_mostra_url_completa_para_ser_clicavel():
    assert "https://github.com/dono/projeto" in formatar_ficha(_ficha())


def test_ficha_nao_confirmada_traz_aviso_de_clone():
    ficha = montar_ficha(_dados_repo(), 7, 3, False)
    assert "achei só pelo nome" in formatar_ficha(ficha)


def test_ficha_arquivada_avisa_que_nao_e_mantido():
    assert "ARQUIVADO" in formatar_ficha(_ficha(archived=True))


def test_contagem_no_teto_da_api_aparece_com_mais():
    ficha = montar_ficha(_dados_repo(), 100, 100, True)
    assert "Contribuidores: 100+" in formatar_ficha(ficha)
