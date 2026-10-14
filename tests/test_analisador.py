import shutil
import subprocess

import pytest

from reels import (
    ErroAnalise,
    ProjetoCitado,
    analisar_video,
    formatar_projetos,
    interpretar_resposta,
)

_JSON_UM_PROJETO = (
    '{"projetos":[{"nome":"laya","dono_ou_endereco":"x/laya","onde_apareceu":"tela"}]}'
)


def test_json_puro_vira_lista_de_projetos():
    esperado = [ProjetoCitado("laya", "x/laya", "tela")]
    assert interpretar_resposta(_JSON_UM_PROJETO) == esperado


def test_json_dentro_de_cerca_de_codigo_e_lido():
    texto = f"```json\n{_JSON_UM_PROJETO}\n```"
    assert interpretar_resposta(texto)[0].nome == "laya"


def test_criador_do_json_chega_ao_projeto():
    texto = '{"projetos":[{"nome":"a","criador":"@fulano"}]}'
    assert interpretar_resposta(texto)[0].criador == "@fulano"


def test_criador_ausente_ou_nulo_vira_texto_vazio():
    texto = '{"projetos":[{"nome":"a","criador":null}]}'
    assert interpretar_resposta(texto)[0].criador == ""


def test_lista_vazia_devolve_lista_vazia():
    assert interpretar_resposta('{"projetos":[]}') == []


def test_resposta_sem_json_levanta_erro_de_analise():
    with pytest.raises(ErroAnalise):
        interpretar_resposta("não achei nada")


def test_json_sem_chave_projetos_levanta_erro_de_analise():
    with pytest.raises(ErroAnalise):
        interpretar_resposta('{"outra":1}')


def test_formatar_lista_vazia_avisa_que_nada_foi_achado():
    assert "Não achei" in formatar_projetos([])


def test_formatar_projeto_mostra_nome_e_endereco():
    texto = formatar_projetos([ProjetoCitado("laya", "x/laya", "tela")])
    assert "laya (x/laya) [tela]" in texto


def test_agy_roda_na_pasta_do_video_e_nao_na_do_projeto(tmp_path, monkeypatch):
    chamadas = []

    def falso_agy(*args, **kwargs):
        chamadas.append(kwargs)
        return subprocess.CompletedProcess([], 0, stdout='{"projetos":[]}', stderr="")

    monkeypatch.setattr(subprocess, "run", falso_agy)
    monkeypatch.setattr(shutil, "which", lambda nome: "agy")
    analisar_video(tmp_path / "video.mp4")
    assert chamadas[0]["cwd"] == tmp_path
