import requests

_URL_BASE = "https://api.telegram.org/bot{token}/{metodo}"
# O Telegram segura a conexão até chegar mensagem; o timeout do requests
# precisa ser maior que a espera, senão cai antes da resposta.
_ESPERA_SEGUNDOS = 30


class ClienteTelegram:
    def __init__(self, token: str):
        self._token = token

    def _chamar(self, metodo: str, **parametros) -> dict:
        url = _URL_BASE.format(token=self._token, metodo=metodo)
        resposta = requests.post(url, json=parametros, timeout=_ESPERA_SEGUNDOS + 10)
        resposta.raise_for_status()
        return resposta.json()

    def identificar_bot(self) -> str:
        """Usuário do bot; falha (HTTPError) se o token for inválido."""
        return self._chamar("getMe")["result"]["username"]

    def buscar_mensagens(self, deslocamento: int | None) -> list[dict]:
        """Mensagens novas desde o `deslocamento` (id da última lida + 1)."""
        dados = self._chamar(
            "getUpdates",
            offset=deslocamento,
            timeout=_ESPERA_SEGUNDOS,
            allowed_updates=["message"],
        )
        return dados["result"]

    def enviar_mensagem(self, id_conversa: int, texto: str) -> None:
        self._chamar("sendMessage", chat_id=id_conversa, text=texto)

    def enviar_arquivo(self, id_conversa: int, nome: str, conteudo: str) -> None:
        url = _URL_BASE.format(token=self._token, metodo="sendDocument")
        resposta = requests.post(
            url,
            data={"chat_id": id_conversa},
            files={"document": (nome, conteudo.encode("utf-8"))},
            timeout=_ESPERA_SEGUNDOS + 10,
        )
        resposta.raise_for_status()
