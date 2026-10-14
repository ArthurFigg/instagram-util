from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
    # env_ignore_empty: "VARIAVEL=" vazia no .env conta como não definida.
    # Caminho fixo ao lado do código: a tarefa do Windows não garante a pasta atual.
    model_config = SettingsConfigDict(
        env_file=Path(__file__).with_name(".env"), env_ignore_empty=True
    )

    telegram_token: str
    # Só esse usuário é atendido; vazio = o bot só diz qual é o seu id.
    telegram_id_autorizado: int | None = None
    # Opcional: sem ele o GitHub limita a 60 consultas por hora.
    github_token: str | None = None
    # Pasta das notas de repositórios no Obsidian; vazio = não grava nota.
    obsidian_pasta_repositorios: Path | None = None
    # Opcional: nota-índice que ganha uma linha por nota nova (ex.: "Índice.md").
    obsidian_arquivo_indice: str | None = None
    # Opcional: notas linkadas no rodapé, em JSON (ex.: ["Índice","Repositórios"]).
    obsidian_links_rodape: list[str] = []
