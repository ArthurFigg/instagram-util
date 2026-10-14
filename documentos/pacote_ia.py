from datetime import date

from github import (
    AVISO_NAO_CONFIRMADO,
    FichaProjeto,
    fatos_da_ficha,
    linhas_de_descricao,
)
from reels import ProjetoCitado

# Um README enorme estoura o contexto da IA que receber o arquivo.
_LIMITE_README = 8000


def gerar_pacote_ia(
    ficha: FichaProjeto,
    projeto: ProjetoCitado,
    readme: str | None,
    link_reel: str,
    hoje: date,
) -> str:
    """Markdown autocontido para colar em qualquer IA pesquisar o projeto."""
    linhas = [f"# {ficha.dono}/{ficha.nome}", "", ficha.url]
    descricao = linhas_de_descricao(ficha)
    if descricao:
        linhas += ["", *descricao]
    if not ficha.confirmado:
        linhas += ["", AVISO_NAO_CONFIRMADO]
    linhas += [
        "",
        "## De onde veio",
        f"Visto em um reel do Instagram em {hoje:%d/%m/%Y}: {link_reel}",
        f"O vídeo citou como: {projeto.nome} ({projeto.onde_apareceu}).",
        "",
        "## Ficha de fatos (medida no GitHub)",
        *fatos_da_ficha(ficha),
        "",
        "## README",
        _cortar_readme(readme),
    ]
    return "\n".join(linhas) + "\n"


def _cortar_readme(readme: str | None) -> str:
    if not readme:
        return "(o repositório não tem README)"
    if len(readme) <= _LIMITE_README:
        return readme
    return readme[:_LIMITE_README] + "\n\n[... README cortado em 8000 caracteres ...]"
