import re

_PADRAO_LINK = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?:reel|reels|p|tv)/[\w-]+/?[^\s]*"
)


def extrair_link_instagram(texto: str) -> str | None:
    """Devolve o primeiro link de reel/post do Instagram no texto, ou None."""
    achado = _PADRAO_LINK.search(texto)
    return achado.group(0) if achado else None
