import json
from dataclasses import dataclass
from pathlib import Path

from gemini import ErroGemini, executar_agy
from reels.excecoes import ErroAnalise

_LIMITE_SEGUNDOS = 300

_PEDIDO = (
    "Assista ao arquivo {arquivo} desta pasta. Liste os projetos de código "
    "(repositórios, bibliotecas, apps de código aberto) que são o assunto do "
    "vídeo ou que o autor recomenda, falados ou escritos na tela. Não liste "
    "empresas, sites nem cada item de uma lista rolando na tela: só o projeto "
    "que contém essa lista. Não abra nenhum outro arquivo, não rode comandos "
    "e não explore outras pastas: use só o vídeo. Em dono_ou_endereco ponha o "
    "endereço completo do repositório se aparecer; em criador ponha o nome ou "
    "@ de quem criou o projeto se o vídeo mostrar ou falar, senão deixe vazio. "
    "Responda SOMENTE com JSON: "
    '{{"projetos":[{{"nome":"","dono_ou_endereco":"","criador":"",'
    '"onde_apareceu":"fala|tela"}}]}}. '
    'Se não houver nenhum, {{"projetos":[]}}.'
)


@dataclass(frozen=True)
class ProjetoCitado:
    nome: str
    endereco: str
    onde_apareceu: str
    criador: str = ""


def interpretar_resposta(texto: str) -> list[ProjetoCitado]:
    """Lê o JSON da resposta do Gemini, tolerando texto ou cercas ``` em volta."""
    inicio, fim = texto.find("{"), texto.rfind("}")
    if inicio == -1 or fim == -1:
        raise ErroAnalise("A resposta do Gemini não trouxe JSON.")
    try:
        dados = json.loads(texto[inicio : fim + 1])
        return [
            ProjetoCitado(
                nome=item["nome"],
                endereco=item.get("dono_ou_endereco", ""),
                onde_apareceu=item.get("onde_apareceu", ""),
                criador=item.get("criador") or "",
            )
            for item in dados["projetos"]
        ]
    except (json.JSONDecodeError, KeyError, TypeError) as erro:
        raise ErroAnalise("O JSON do Gemini veio fora do formato.") from erro


def analisar_video(video: Path) -> list[ProjetoCitado]:
    """Pede ao Gemini (via agy) para assistir ao vídeo e listar os projetos."""
    pedido = _PEDIDO.format(arquivo=video.name)
    try:
        resposta = executar_agy(pedido, video.parent, _LIMITE_SEGUNDOS)
    except ErroGemini as erro:
        raise ErroAnalise(str(erro)) from erro
    return interpretar_resposta(resposta)
