# instagram-util

![Python](https://img.shields.io/badge/python-3.13-blue)
![Plataforma](https://img.shields.io/badge/plataforma-Windows-informational)

Você compartilha um reel do Instagram com o seu bot do Telegram. O bot acha o repositório do GitHub citado no vídeo e devolve uma ficha de fatos, um arquivo `.md` para colar em qualquer IA e, se você quiser, uma nota pronta no Obsidian.

Reels quase nunca escrevem o nome do repositório, e saber se ele é bom dá trabalho manual. O bot faz esse levantamento no seu computador, com as suas chaves.

## Funcionalidades

- Recebe o link de um reel pelo Telegram e baixa o vídeo sem precisar de login no Instagram.
- O Gemini assiste ao vídeo (fala e texto na tela) e lista os projetos de código citados.
- Confere cada projeto no GitHub, em ordem: pelo endereço mostrado no vídeo, por nome + criador, e só por último pelo nome. Quando achou só pelo nome, avisa que pode ser outro projeto ou um clone.
- Manda uma **ficha de fatos** por projeto: idade, estrelas, forks, último push, commits dos últimos 90 dias, contribuidores, licença e se o repositório está arquivado.
- Traduz a descrição do repositório para português e mantém o original ao lado, para você conferir.
- Manda um arquivo `<projeto>.md` no chat, com a ficha, o link do reel e o README (cortado em 8.000 caracteres), pronto para entregar a qualquer IA.
- Cria uma nota por projeto numa pasta do Obsidian, com tags tiradas dos tópicos do GitHub. Se a nota já existe, não sobrescreve.
- Atende só o seu usuário do Telegram; mensagens de outras pessoas são ignoradas.

## Pré-requisitos

- Windows (o script de inicialização automática é do Windows; o resto não foi testado em outros sistemas).
- [`uv`](https://docs.astral.sh/uv/), que instala o Python 3.13 e as dependências.
- `agy`, a CLI do Gemini (Antigravity), instalada e com a sua conta logada. É ela que assiste ao vídeo, e o uso conta na sua cota do Gemini.
- Uma conta no Telegram.

## Instalação

1. Baixe o projeto e entre na pasta dele:

```bash
git clone https://github.com/ArthurFigg/instagram-util.git
cd instagram-util
```

2. Instale as dependências:

```bash
uv sync
```

3. Crie o bot no Telegram: abra o contato `@BotFather`, mande `/newbot`, escolha um nome e guarde o token que ele devolve.
4. Copie `.env.example` para `.env` e cole o token em `TELEGRAM_TOKEN`.

## Uso

```bash
uv run main.py
```

Na primeira execução o bot confere o ambiente e avisa o que faltar (`agy` instalado e logado, token do Telegram válido, pasta do Obsidian existente). Se algo grave faltar, ele não liga e diz o motivo.

Depois:

1. Mande qualquer mensagem para o seu bot. Como `TELEGRAM_ID_AUTORIZADO` está vazio, ele responde com o seu id.
2. Pare o bot (Ctrl+C), coloque esse número em `TELEGRAM_ID_AUTORIZADO` no `.env` e rode de novo.
3. Compartilhe um reel do Instagram com o bot, ou cole o link na conversa.

O bot responde "Processando..." e, em cerca de 1 minuto por vídeo, manda a lista de projetos achados. Para cada um (até 5 por reel) chegam a ficha, o arquivo `.md` e, se configurado, o aviso "Nota criada no Obsidian".

### Ligar sozinho com o Windows

Para o bot não depender de você lembrar de abri-lo, crie uma tarefa que o liga quando você entra no Windows, sem janela de terminal. Na pasta do projeto:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\instalar_inicio_windows.ps1
```

| Ação | Comando |
|---|---|
| Ligar agora | `Start-ScheduledTask -TaskName InstagramUtilBot` |
| Parar | `Stop-ScheduledTask -TaskName InstagramUtilBot` |
| Remover | `Unregister-ScheduledTask -TaskName InstagramUtilBot -Confirm:$false` |

Se o bot cair, o Windows o religa até 3 vezes. Depois de mudar o código ou o `.env`, pare e ligue a tarefa de novo. O que o bot faz fica registrado em `bot.log`, na pasta do projeto.

Com o PC desligado o bot não responde. O Telegram guarda as mensagens por cerca de 24 horas, então um reel enviado nesse período é processado quando o PC ligar.

## Configuração

As variáveis ficam no arquivo `.env` (modelo em `.env.example`). Campo vazio vale como "não definido".

| Variável | Obrigatória | Descrição |
|---|---|---|
| `TELEGRAM_TOKEN` | Sim | Token do bot, criado com o `@BotFather`. |
| `TELEGRAM_ID_AUTORIZADO` | Não* | Seu id no Telegram. *Vazio, o bot só responde com o seu id. |
| `GITHUB_TOKEN` | Não | Sem ele o GitHub limita a 60 consultas por hora; cada projeto achado gasta de 4 a 6. Crie um token sem nenhuma permissão marcada. |
| `OBSIDIAN_PASTA_REPOSITORIOS` | Não | Pasta onde criar uma nota por repositório. Vazio = não grava nota. |
| `OBSIDIAN_ARQUIVO_INDICE` | Não | Nota-índice (ex.: `Índice.md`, na mesma pasta) que ganha uma linha `- [[nota]]` por nota nova. |
| `OBSIDIAN_LINKS_RODAPE` | Não | Notas linkadas no rodapé "Ver também", em JSON. Ex.: `["Índice","Repositórios"]`. |

## Estrutura do projeto

```
main.py             # liga o bot e fica buscando mensagens do Telegram
fluxo.py            # o caminho de um reel: baixar, analisar, conferir, responder
ambiente.py         # confere agy, token e pastas ao ligar
config.py           # lê o .env
processos.py        # roda programas externos sem abrir janela
canal_telegram/     # fala com o Telegram e acha o link do reel na mensagem
reels/              # baixa o vídeo (yt-dlp) e pede ao Gemini a lista de projetos
gemini/             # chamada ao agy e tradução da descrição
github/             # busca o repositório e monta a ficha de fatos
documentos/         # gera o .md para IA e a nota do Obsidian
scripts/            # instalação da tarefa de inicialização do Windows
tests/
```

## Limites que valem saber

- O Gemini pode errar o que leu no vídeo; a conferência no GitHub reduz o erro, mas não elimina. Projeto achado só pelo nome sai com aviso.
- Commits e contribuidores aparecem como `100+` quando passam de 100, porque a API do GitHub devolve no máximo 100 por consulta.
- O download sem login funciona com reels públicos, mas o Instagram pode bloquear ou mudar a qualquer momento, e os termos do Instagram restringem coleta automática. Use por sua conta e risco.
- O README dentro do `.md` vai no idioma original do repositório; só a descrição é traduzida.

## Testes

```bash
uv run pytest -v
```

## Dependências

| Pacote | Uso |
|---|---|
| `requests` | Conversa com as APIs do Telegram e do GitHub. |
| `pydantic-settings` | Lê e valida as variáveis do `.env`. |
| `yt-dlp` | Baixa o reel do Instagram. |

## Licença

MIT. Veja o arquivo [LICENSE](LICENSE).
