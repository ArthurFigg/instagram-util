from reels.analisador import ProjetoCitado


def formatar_projetos(projetos: list[ProjetoCitado]) -> str:
    if not projetos:
        return "Não achei nenhum projeto de código citado nesse vídeo."
    linhas = [f"Achei {len(projetos)} projeto(s):"]
    for projeto in projetos:
        endereco = f" ({projeto.endereco})" if projeto.endereco else ""
        linhas.append(f"- {projeto.nome}{endereco} [{projeto.onde_apareceu}]")
    return "\n".join(linhas)
