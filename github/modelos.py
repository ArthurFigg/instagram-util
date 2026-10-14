from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FichaProjeto:
    dono: str
    nome: str
    url: str
    descricao: str
    estrelas: int
    forks: int
    criado_em: datetime
    ultimo_push: datetime
    commits_90_dias: int
    contribuidores: int
    licenca: str
    arquivado: bool
    topicos: tuple[str, ...]
    # True = bateu pelo endereço do vídeo ou por nome + criador.
    # False = achado só pelo nome, pode ser outro projeto ou um clone.
    confirmado: bool
    # Tradução automática de `descricao`; vazio = não traduzida.
    descricao_pt: str = ""
