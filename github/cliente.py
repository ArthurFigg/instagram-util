from datetime import UTC, datetime, timedelta

import requests

from github.excecoes import ErroGithub

_URL_BASE = "https://api.github.com"
_LIMITE_SEGUNDOS = 20
# A API devolve no máximo 100 itens por página; usamos 1 página só.
_POR_PAGINA = 100


class ClienteGithub:
    def __init__(self, token: str | None = None):
        self._cabecalhos = {"Accept": "application/vnd.github+json"}
        if token:
            self._cabecalhos["Authorization"] = f"Bearer {token}"

    def _requisitar(
        self,
        caminho: str,
        parametros: dict | None = None,
        cabecalhos_extras: dict | None = None,
    ) -> requests.Response | None:
        """GET na API; devolve None se o recurso não existe ou está vazio."""
        cabecalhos = {**self._cabecalhos, **(cabecalhos_extras or {})}
        try:
            resposta = requests.get(
                f"{_URL_BASE}{caminho}",
                headers=cabecalhos,
                params=parametros,
                timeout=_LIMITE_SEGUNDOS,
            )
        except requests.RequestException as erro:
            raise ErroGithub(f"Não consegui falar com o GitHub: {erro}") from erro

        if resposta.status_code in (404, 409):
            return None
        if resposta.status_code in (403, 429):
            raise ErroGithub("Limite de uso do GitHub atingido. Tente mais tarde.")
        if not resposta.ok:
            raise ErroGithub(f"O GitHub respondeu {resposta.status_code}.")
        return resposta

    def _pegar(self, caminho: str, parametros: dict | None = None):
        resposta = self._requisitar(caminho, parametros)
        return resposta.json() if resposta else None

    def obter_readme(self, dono: str, nome: str) -> str | None:
        resposta = self._requisitar(
            f"/repos/{dono}/{nome}/readme",
            cabecalhos_extras={"Accept": "application/vnd.github.raw+json"},
        )
        return resposta.text if resposta else None

    def obter_repositorio(self, dono: str, nome: str) -> dict | None:
        return self._pegar(f"/repos/{dono}/{nome}")

    def buscar_repositorio(self, nome: str, dono: str | None = None) -> dict | None:
        """O repositório com mais estrelas cujo nome bate com `nome`.

        Com `dono`, procura só entre os repositórios dessa conta.
        """
        consulta = f"{nome} in:name" + (f" user:{dono}" if dono else "")
        dados = self._pegar(
            "/search/repositories",
            {"q": consulta, "sort": "stars", "per_page": 1},
        )
        itens = dados["items"] if dados else []
        return itens[0] if itens else None

    def contar_commits_recentes(self, dono: str, nome: str, dias: int) -> int:
        desde = datetime.now(UTC) - timedelta(days=dias)
        commits = self._pegar(
            f"/repos/{dono}/{nome}/commits",
            {"since": desde.isoformat(), "per_page": _POR_PAGINA},
        )
        return len(commits) if commits else 0

    def contar_contribuidores(self, dono: str, nome: str) -> int:
        contribuidores = self._pegar(
            f"/repos/{dono}/{nome}/contributors", {"per_page": _POR_PAGINA}
        )
        return len(contribuidores) if contribuidores else 0
