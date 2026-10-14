from dataclasses import dataclass
from datetime import date
from pathlib import Path

from github import (
    AVISO_NAO_CONFIRMADO,
    FichaProjeto,
    fatos_da_ficha,
    linhas_de_descricao,
)

_MAXIMO_TAGS = 5


@dataclass(frozen=True)
class OpcoesNota:
    """Convenções do vault de cada pessoa; o padrão não assume nenhuma."""

    # Nota-índice (ex.: "Índice.md") que ganha uma linha por nota nova.
    arquivo_indice: str | None = None
    # Notas linkadas no rodapé "Ver também" (ex.: ("Índice", "Repositórios")).
    links_rodape: tuple[str, ...] = ()


def _montar_nota(
    ficha: FichaProjeto, link_reel: str, hoje: date, opcoes: OpcoesNota
) -> str:
    tags = ["repositorio", *ficha.topicos[:_MAXIMO_TAGS]]
    linhas = ["---", "tags:", *[f"  - {tag}" for tag in tags], "---", ""]
    descricao = linhas_de_descricao(ficha)
    if descricao:
        linhas += [*descricao, ""]
    if not ficha.confirmado:
        linhas += [AVISO_NAO_CONFIRMADO, ""]
    linhas += [
        *fatos_da_ficha(ficha),
        "",
        f"Visto no reel de {hoje:%d/%m/%Y}: {link_reel}",
        "",
        ficha.url,
        "",
    ]
    if opcoes.links_rodape:
        links = " · ".join(f"[[{nome}]]" for nome in opcoes.links_rodape)
        linhas += ["## Ver também", links, ""]
    return "\n".join(linhas)


def _acrescentar_ao_indice(pasta: Path, arquivo_indice: str, nome_da_nota: str) -> None:
    indice = pasta / arquivo_indice
    if not indice.exists():
        return
    texto = indice.read_text(encoding="utf-8")
    link = f"[[{nome_da_nota}]]"
    if link in texto:
        return
    separador = "" if texto.endswith("\n") else "\n"
    indice.write_text(f"{texto}{separador}- {link}\n", encoding="utf-8")


def gravar_nota(
    pasta: Path,
    ficha: FichaProjeto,
    link_reel: str,
    hoje: date,
    opcoes: OpcoesNota | None = None,
) -> Path | None:
    """Cria a nota do repositório; devolve None se ela já existia (não sobrescreve)."""
    opcoes = opcoes or OpcoesNota()
    caminho = pasta / f"{ficha.nome}.md"
    if caminho.exists():
        return None
    caminho.write_text(_montar_nota(ficha, link_reel, hoje, opcoes), encoding="utf-8")
    if opcoes.arquivo_indice:
        _acrescentar_ao_indice(pasta, opcoes.arquivo_indice, ficha.nome)
    return caminho
