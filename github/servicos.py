import re
from datetime import datetime

from github.cliente import ClienteGithub
from github.modelos import FichaProjeto
from reels import ProjetoCitado

_PADRAO_ENDERECO = re.compile(r"github\.com/([\w.-]+)/([\w.-]+)", re.IGNORECASE)
_PADRAO_USUARIO = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?")
_DIAS_DE_ATIVIDADE = 90


def extrair_dono_nome(endereco: str) -> tuple[str, str] | None:
    """Lê 'github.com/dono/nome' de um endereço; None se não for do GitHub."""
    achado = _PADRAO_ENDERECO.search(endereco)
    if achado is None:
        return None
    return achado.group(1), achado.group(2).removesuffix(".git")


def montar_ficha(
    dados: dict, commits_90_dias: int, contribuidores: int, confirmado: bool
) -> FichaProjeto:
    licenca = (dados.get("license") or {}).get("spdx_id") or "sem licença"
    return FichaProjeto(
        dono=dados["owner"]["login"],
        nome=dados["name"],
        url=dados["html_url"],
        descricao=dados.get("description") or "",
        estrelas=dados["stargazers_count"],
        forks=dados["forks_count"],
        criado_em=datetime.fromisoformat(dados["created_at"]),
        ultimo_push=datetime.fromisoformat(dados["pushed_at"]),
        commits_90_dias=commits_90_dias,
        contribuidores=contribuidores,
        licenca=licenca,
        arquivado=dados["archived"],
        topicos=tuple(dados.get("topics", [])),
        confirmado=confirmado,
    )


def extrair_usuario(criador: str) -> str | None:
    """Usuário do GitHub a partir de '@fulano' ou 'fulano'; None se não servir.

    Nome de exibição com espaço ("Pablo Stanley") não é usuário do GitHub.
    """
    candidato = criador.strip().removeprefix("@")
    return candidato if _PADRAO_USUARIO.fullmatch(candidato) else None


def _achar_repositorio(
    cliente: ClienteGithub, projeto: ProjetoCitado
) -> tuple[dict, bool] | None:
    """Tenta, em ordem: endereço do vídeo, nome + criador, só o nome.

    Só os dois primeiros contam como confirmados; só o nome é palpite.
    """
    dono_nome = extrair_dono_nome(projeto.endereco)
    if dono_nome:
        dados = cliente.obter_repositorio(*dono_nome)
        if dados:
            return dados, True

    usuario = extrair_usuario(projeto.criador)
    if usuario:
        dados = cliente.buscar_repositorio(projeto.nome, usuario)
        if dados:
            return dados, True

    dados = cliente.buscar_repositorio(projeto.nome)
    return (dados, False) if dados else None


def buscar_ficha(cliente: ClienteGithub, projeto: ProjetoCitado) -> FichaProjeto | None:
    achado = _achar_repositorio(cliente, projeto)
    if achado is None:
        return None
    dados, confirmado = achado
    dono, nome = dados["owner"]["login"], dados["name"]
    return montar_ficha(
        dados,
        cliente.contar_commits_recentes(dono, nome, _DIAS_DE_ATIVIDADE),
        cliente.contar_contribuidores(dono, nome),
        confirmado,
    )
