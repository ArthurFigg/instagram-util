import pytest

from canal_telegram import extrair_link_instagram


def test_link_de_reel_puro_e_devolvido():
    link = "https://www.instagram.com/reel/ABC123xyz/"
    assert extrair_link_instagram(link) == link


def test_link_no_meio_do_texto_e_achado():
    texto = "olha isso https://www.instagram.com/reel/ABC123/ muito bom"
    assert extrair_link_instagram(texto) == "https://www.instagram.com/reel/ABC123/"


def test_link_com_parametros_de_rastreio_e_mantido():
    link = "https://www.instagram.com/reel/ABC123/?igsh=MWx4"
    assert extrair_link_instagram(link) == link


def test_link_de_post_comum_e_aceito():
    link = "https://instagram.com/p/XYZ789/"
    assert extrair_link_instagram(link) == link


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "sem link nenhum",
        "https://www.youtube.com/watch?v=abc",
        "https://www.instagram.com/perfil_qualquer/",
    ],
)
def test_texto_sem_link_de_instagram_devolve_none(texto):
    assert extrair_link_instagram(texto) is None
