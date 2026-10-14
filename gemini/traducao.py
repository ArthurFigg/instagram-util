import tempfile
from pathlib import Path

from gemini.agy import ErroGemini, executar_agy

_LIMITE_SEGUNDOS = 120
# Tradução muito maior que o original indica que o modelo começou a explicar.
_FATOR_MAXIMO = 4

_PEDIDO = (
    "Traduza para o português do Brasil o texto entre as marcas <<< e >>>. "
    "Se já estiver em português, repita igual. Não abra arquivos, não rode "
    "comandos e não explore pastas. Responda SOMENTE com a tradução, sem aspas "
    "e sem explicação.\n<<<{texto}>>>"
)


def traduzir_para_portugues(texto: str) -> str:
    """Traduz um texto curto pelo Gemini; levanta ErroGemini se a resposta falhar."""
    # Pasta vazia: o agy explora a pasta onde roda.
    with tempfile.TemporaryDirectory() as pasta:
        resposta = executar_agy(
            _PEDIDO.format(texto=texto), Path(pasta), _LIMITE_SEGUNDOS
        ).strip()
    if not resposta or len(resposta) > len(texto) * _FATOR_MAXIMO:
        raise ErroGemini("A tradução veio vazia ou fora do tamanho esperado.")
    return resposta
