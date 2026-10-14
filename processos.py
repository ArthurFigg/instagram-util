import subprocess

# Sem isso, o bot rodando sem terminal abre uma janela preta a cada subprocesso.
_SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def rodar_sem_janela(
    comando: list[str], **argumentos
) -> subprocess.CompletedProcess[str]:
    """subprocess.run que captura a saída em texto UTF-8 e não abre janela."""
    return subprocess.run(
        comando,
        # Sem terminal não há stdin herdado; o Windows falha com "handle inválido".
        stdin=subprocess.DEVNULL,
        creationflags=_SEM_JANELA,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        **argumentos,
    )
