from datetime import UTC, date, datetime, timedelta

from documentos import OpcoesNota, gerar_pacote_ia, gravar_nota
from github import montar_ficha
from reels import ProjetoCitado

_HOJE = date(2026, 10, 14)
_LINK_REEL = "https://www.instagram.com/reel/ABC/"
_PROJETO = ProjetoCitado("projeto", "github.com/dono/projeto", "tela")
_COM_INDICE = OpcoesNota(arquivo_indice="Índice.md")


def _ficha(confirmado: bool = True, topicos: list[str] | None = None):
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
        "topics": topicos or [],
    }
    return montar_ficha(dados, 7, 3, confirmado)


def test_pacote_traz_o_link_do_reel_de_origem():
    pacote = gerar_pacote_ia(_ficha(), _PROJETO, "# Leia-me", _LINK_REEL, _HOJE)
    assert _LINK_REEL in pacote


def test_pacote_traz_o_readme_do_repositorio():
    pacote = gerar_pacote_ia(_ficha(), _PROJETO, "# Leia-me", _LINK_REEL, _HOJE)
    assert "# Leia-me" in pacote


def test_pacote_corta_readme_gigante():
    readme = "x" * 20000
    pacote = gerar_pacote_ia(_ficha(), _PROJETO, readme, _LINK_REEL, _HOJE)
    assert "README cortado" in pacote


def test_pacote_sem_readme_avisa_que_nao_existe():
    pacote = gerar_pacote_ia(_ficha(), _PROJETO, None, _LINK_REEL, _HOJE)
    assert "não tem README" in pacote


def test_pacote_de_ficha_nao_confirmada_traz_aviso_de_clone():
    pacote = gerar_pacote_ia(_ficha(False), _PROJETO, "x", _LINK_REEL, _HOJE)
    assert "achei só pelo nome" in pacote


def test_nota_nova_e_criada_com_a_tag_repositorio(tmp_path):
    caminho = gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE)
    assert caminho is not None and "  - repositorio" in caminho.read_text("utf-8")


def test_nota_usa_topicos_do_github_como_tags(tmp_path):
    caminho = gravar_nota(tmp_path, _ficha(topicos=["ia", "cli"]), _LINK_REEL, _HOJE)
    assert caminho is not None and "  - cli" in caminho.read_text("utf-8")


def test_nota_traz_a_data_e_o_link_do_reel(tmp_path):
    caminho = gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE)
    assert caminho is not None
    assert f"Visto no reel de 14/10/2026: {_LINK_REEL}" in caminho.read_text("utf-8")


def test_nota_existente_nao_e_sobrescrita(tmp_path):
    (tmp_path / "projeto.md").write_text("minha nota", encoding="utf-8")
    gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE)
    assert (tmp_path / "projeto.md").read_text("utf-8") == "minha nota"


def test_nota_existente_devolve_none(tmp_path):
    (tmp_path / "projeto.md").write_text("minha nota", encoding="utf-8")
    assert gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE) is None


def test_nota_nova_entra_no_indice(tmp_path):
    (tmp_path / "Índice.md").write_text("- [[Outra]]\n", encoding="utf-8")
    gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE, _COM_INDICE)
    assert "- [[projeto]]" in (tmp_path / "Índice.md").read_text("utf-8")


def test_indice_sem_quebra_final_nao_cola_a_linha_nova(tmp_path):
    (tmp_path / "Índice.md").write_text("- [[Outra]]", encoding="utf-8")
    gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE, _COM_INDICE)
    texto = (tmp_path / "Índice.md").read_text("utf-8")
    assert texto == "- [[Outra]]\n- [[projeto]]\n"


def test_indice_configurado_mas_inexistente_nao_impede_a_nota(tmp_path):
    caminho = gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE, _COM_INDICE)
    assert caminho is not None


def test_sem_indice_configurado_o_indice_existente_nao_e_tocado(tmp_path):
    (tmp_path / "Índice.md").write_text("- [[Outra]]\n", encoding="utf-8")
    gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE)
    assert (tmp_path / "Índice.md").read_text("utf-8") == "- [[Outra]]\n"


def test_nota_sem_links_de_rodape_nao_tem_ver_tambem(tmp_path):
    caminho = gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE)
    assert caminho is not None and "Ver também" not in caminho.read_text("utf-8")


def test_nota_com_status_inicial_grava_o_status_no_cabecalho(tmp_path):
    opcoes = OpcoesNota(status_inicial="novo")
    caminho = gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE, opcoes)
    assert caminho is not None
    assert "\nstatus: novo\n---\n" in caminho.read_text("utf-8")


def test_nota_sem_status_inicial_nao_tem_status(tmp_path):
    caminho = gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE)
    assert caminho is not None and "status:" not in caminho.read_text("utf-8")


def test_nota_com_links_de_rodape_lista_todos(tmp_path):
    opcoes = OpcoesNota(links_rodape=("Índice", "Repositórios"))
    caminho = gravar_nota(tmp_path, _ficha(), _LINK_REEL, _HOJE, opcoes)
    assert caminho is not None
    assert "[[Índice]] · [[Repositórios]]" in caminho.read_text("utf-8")
