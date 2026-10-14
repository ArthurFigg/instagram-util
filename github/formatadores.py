from datetime import UTC, datetime

from github.modelos import FichaProjeto
from reels import ProjetoCitado

_TETO_DA_API = 100

AVISO_NAO_CONFIRMADO = (
    "ATENÇÃO: achei só pelo nome, sem endereço nem criador do vídeo. "
    "Pode ser outro projeto ou um clone; confira."
)


def _contagem(valor: int) -> str:
    # A API corta em 100 por página; acima disso o número real é maior.
    return f"{valor}+" if valor >= _TETO_DA_API else str(valor)


def _dias_desde(momento: datetime) -> int:
    return (datetime.now(UTC) - momento).days


def fatos_da_ficha(ficha: FichaProjeto) -> list[str]:
    """Linhas de fatos medidos, reaproveitadas no chat, no .md e na nota."""
    linhas = [
        f"• Idade: {_dias_desde(ficha.criado_em)} dias",
        f"• Estrelas: {ficha.estrelas} · forks: {ficha.forks}",
        f"• Último push: há {_dias_desde(ficha.ultimo_push)} dias",
        f"• Commits nos últimos 90 dias: {_contagem(ficha.commits_90_dias)}",
        f"• Contribuidores: {_contagem(ficha.contribuidores)}",
        f"• Licença: {ficha.licenca}",
    ]
    if ficha.arquivado:
        linhas.append("• ARQUIVADO: o dono não mantém mais")
    return linhas


def linhas_de_descricao(ficha: FichaProjeto) -> list[str]:
    """Descrição em português; o original em inglês vai junto para conferência."""
    if not ficha.descricao:
        return []
    if not ficha.descricao_pt or ficha.descricao_pt == ficha.descricao:
        return [ficha.descricao]
    return [ficha.descricao_pt, f"(original: {ficha.descricao})"]


def formatar_ficha(ficha: FichaProjeto) -> str:
    linhas = [f"{ficha.dono}/{ficha.nome}", ficha.url]
    if not ficha.confirmado:
        linhas.append(AVISO_NAO_CONFIRMADO)
    linhas += linhas_de_descricao(ficha)
    linhas += ["", "FICHA DE FATOS", *fatos_da_ficha(ficha)]
    return "\n".join(linhas)


def formatar_nao_encontrado(projeto: ProjetoCitado) -> str:
    return f"{projeto.nome}: não achei no GitHub."
