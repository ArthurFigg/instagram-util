import logging
import time
from pathlib import Path

import requests
from pydantic import ValidationError

from ambiente import verificar_ambiente
from canal_telegram import ClienteTelegram, extrair_link_instagram
from config import Configuracoes
from fluxo import processar_link
from github import ClienteGithub

# Grava em arquivo também: erro que só aparece no terminal se perde ao fechá-lo.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).with_name("bot.log"), encoding="utf-8"),
    ],
)
registro = logging.getLogger("instagram-util")

_ESPERA_APOS_FALHA = 15


def tratar_mensagem(
    telegram: ClienteTelegram,
    github: ClienteGithub,
    configuracoes: Configuracoes,
    mensagem: dict,
) -> None:
    id_usuario = mensagem["from"]["id"]
    id_conversa = mensagem["chat"]["id"]

    if configuracoes.telegram_id_autorizado is None:
        telegram.enviar_mensagem(
            id_conversa,
            f"Seu id é {id_usuario}. Coloque em TELEGRAM_ID_AUTORIZADO no .env "
            "e reinicie o bot.",
        )
        return

    if id_usuario != configuracoes.telegram_id_autorizado:
        registro.warning("Mensagem ignorada de usuário não autorizado: %s", id_usuario)
        return

    link = extrair_link_instagram(mensagem.get("text", ""))
    if link is None:
        telegram.enviar_mensagem(id_conversa, "Não achei link de reel nessa mensagem.")
        return

    try:
        processar_link(telegram, github, configuracoes, id_conversa, link)
    except Exception as erro:  # noqa: BLE001
        # Um erro inesperado num reel não pode derrubar o bot nem calar a resposta.
        registro.exception("Erro inesperado ao processar %s", link)
        telegram.enviar_mensagem(
            id_conversa, f"Erro inesperado ({type(erro).__name__}). Veja o bot.log."
        )


def carregar_configuracoes() -> Configuracoes:
    try:
        # O pydantic-settings lê o token do .env; o pyright não enxerga isso.
        return Configuracoes()  # pyright: ignore[reportCallIssue]
    except ValidationError as erro:
        campos = ", ".join(str(e["loc"][0]).upper() for e in erro.errors())
        registro.error("Configuração inválida no .env. Confira: %s", campos)
        raise SystemExit(1) from erro


def conferir_ambiente(configuracoes: Configuracoes, telegram: ClienteTelegram) -> None:
    graves = False
    for problema in verificar_ambiente(configuracoes, telegram):
        nivel = logging.ERROR if problema.grave else logging.WARNING
        registro.log(nivel, problema.texto)
        graves = graves or problema.grave
    if graves:
        raise SystemExit(1)


def main() -> None:
    configuracoes = carregar_configuracoes()
    telegram = ClienteTelegram(configuracoes.telegram_token)
    github = ClienteGithub(configuracoes.github_token)
    conferir_ambiente(configuracoes, telegram)
    deslocamento = None
    registro.info("Bot ligado. Mande um link de reel pelo Telegram.")

    while True:
        try:
            atualizacoes = telegram.buscar_mensagens(deslocamento)
        except requests.RequestException as erro:
            # Internet caiu ou o Telegram falhou: espera e tenta de novo.
            registro.warning("Falha ao buscar mensagens: %s", erro)
            time.sleep(_ESPERA_APOS_FALHA)
            continue
        for atualizacao in atualizacoes:
            deslocamento = atualizacao["update_id"] + 1
            if "message" in atualizacao:
                tratar_mensagem(telegram, github, configuracoes, atualizacao["message"])


if __name__ == "__main__":
    main()
