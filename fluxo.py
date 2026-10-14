import logging
import tempfile
from dataclasses import replace
from datetime import date
from pathlib import Path

from canal_telegram import ClienteTelegram
from config import Configuracoes
from documentos import OpcoesNota, gerar_pacote_ia, gravar_nota
from gemini import ErroGemini, traduzir_para_portugues
from github import (
    ClienteGithub,
    ErroGithub,
    FichaProjeto,
    buscar_ficha,
    formatar_ficha,
    formatar_nao_encontrado,
)
from reels import (
    ErroReel,
    ProjetoCitado,
    analisar_video,
    baixar_reel,
    formatar_projetos,
)

registro = logging.getLogger("instagram-util")

# Teto por reel: cada projeto gasta consultas do limite do GitHub.
_MAXIMO_PROJETOS = 5


def traduzir_descricao(ficha: FichaProjeto) -> FichaProjeto:
    """Traduz a descrição; se o Gemini falhar, segue com o original em inglês."""
    if not ficha.descricao:
        return ficha
    try:
        return replace(ficha, descricao_pt=traduzir_para_portugues(ficha.descricao))
    except ErroGemini as erro:
        registro.warning("Tradução falhou para %s: %s", ficha.nome, erro)
        return ficha


def processar_projeto(
    telegram: ClienteTelegram,
    github: ClienteGithub,
    configuracoes: Configuracoes,
    id_conversa: int,
    projeto: ProjetoCitado,
    link_reel: str,
) -> None:
    ficha = buscar_ficha(github, projeto)
    if ficha is None:
        telegram.enviar_mensagem(id_conversa, formatar_nao_encontrado(projeto))
        return
    ficha = traduzir_descricao(ficha)

    telegram.enviar_mensagem(id_conversa, formatar_ficha(ficha))
    hoje = date.today()
    readme = github.obter_readme(ficha.dono, ficha.nome)
    pacote = gerar_pacote_ia(ficha, projeto, readme, link_reel, hoje)
    telegram.enviar_arquivo(id_conversa, f"{ficha.nome}.md", pacote)

    pasta = configuracoes.obsidian_pasta_repositorios
    if pasta is None:
        return
    opcoes = OpcoesNota(
        arquivo_indice=configuracoes.obsidian_arquivo_indice,
        links_rodape=tuple(configuracoes.obsidian_links_rodape),
    )
    nota = gravar_nota(pasta, ficha, link_reel, hoje, opcoes)
    aviso = "Nota criada" if nota else "Já existia nota"
    telegram.enviar_mensagem(id_conversa, f"{aviso} no Obsidian: {ficha.nome}")


def processar_link(
    telegram: ClienteTelegram,
    github: ClienteGithub,
    configuracoes: Configuracoes,
    id_conversa: int,
    link: str,
) -> None:
    telegram.enviar_mensagem(id_conversa, "Processando, leva cerca de 1 minuto...")
    try:
        with tempfile.TemporaryDirectory() as pasta:
            video = baixar_reel(link, Path(pasta))
            projetos = analisar_video(video)
        telegram.enviar_mensagem(id_conversa, formatar_projetos(projetos))
        for projeto in projetos[:_MAXIMO_PROJETOS]:
            processar_projeto(
                telegram, github, configuracoes, id_conversa, projeto, link
            )
        if len(projetos) > _MAXIMO_PROJETOS:
            telegram.enviar_mensagem(
                id_conversa, f"Mostrei só os {_MAXIMO_PROJETOS} primeiros projetos."
            )
    except (ErroReel, ErroGithub, OSError) as erro:
        registro.warning("Falha ao processar %s: %s", link, erro)
        telegram.enviar_mensagem(id_conversa, f"Não consegui: {erro}")
