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

## Passo a passo: do zero até funcionar

Os comandos são para o **PowerShell** do Windows (procure "PowerShell" no menu Iniciar). Depois de instalar cada programa, **feche o PowerShell e abra de novo**, para o Windows enxergar o comando novo.

Você vai precisar de: um computador com Windows, uma conta no Telegram e uma conta Google.

### Passo 1: instalar o `uv`

O `uv` instala o Python certo e as peças do projeto.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Confira com `uv --version`. Se aparecer um número de versão, está pronto.

### Passo 2: instalar o `agy` e entrar na sua conta

O `agy` é a CLI do Gemini (Antigravity). É ela que assiste ao vídeo. O uso conta na sua conta do Gemini.

```powershell
irm https://antigravity.google/cli/install.ps1 | iex
```

1. Feche e abra o PowerShell, depois confira com `agy --version`.
2. Rode `agy`. Na primeira vez ele abre o navegador para você entrar com a sua conta Google. Responda às perguntas iniciais (cores, confiar na pasta) e, depois de entrar, pode fechar.
3. Confira o login com `agy models`. Se aparecer uma lista de modelos Gemini, está certo. Se der erro, repita o passo 2.

Detalhes e outras formas de login (chave de API, conta empresarial) estão na [documentação oficial](https://antigravity.google/docs/cli/install).

### Passo 3: baixar o projeto

Com o `git`:

```powershell
git clone https://github.com/ArthurFigg/instagram-util.git
cd instagram-util
```

Sem o `git`: na página do projeto no GitHub, clique em **Code**, depois **Download ZIP**, extraia e abra o PowerShell dentro da pasta extraída.

Depois instale as dependências:

```powershell
uv sync
```

### Passo 4: criar o seu bot no Telegram

1. No Telegram, procure o contato **@BotFather** (o oficial, com o selo azul de verificado).
2. Mande `/newbot`.
3. Escolha um nome de exibição (qualquer um) e depois um nome de usuário, que precisa terminar em `bot` (por exemplo, `meu_reels_bot`).
4. O BotFather responde com o **token**, um texto parecido com `123456789:ABC...`. Guarde: ele é a senha do bot. Não publique nem mande para ninguém.

### Passo 5: preencher o `.env`

```powershell
Copy-Item .env.example .env
notepad .env
```

No Bloco de Notas, cole o token depois de `TELEGRAM_TOKEN=`, sem espaço e sem aspas. **Salve o arquivo (Ctrl+S)** antes de continuar. Deixe os outros campos vazios por enquanto.

### Passo 6: descobrir o seu id e ligar o bot

```powershell
uv run main.py
```

O bot confere o ambiente e mostra o que faltar. Quando aparecer "Bot ligado":

1. No Telegram, abra o seu bot (pelo nome de usuário que você escolheu) e mande qualquer mensagem.
2. O bot responde com o **seu id**, um número.
3. No PowerShell, pare o bot com **Ctrl+C**.
4. No `.env` (`notepad .env`), coloque o número depois de `TELEGRAM_ID_AUTORIZADO=` e **salve**. A partir daí o bot só atende você.
5. Rode `uv run main.py` de novo.

### Passo 7: testar com um reel

No Instagram, abra um reel que fale de algum projeto de código, toque em **Compartilhar**, escolha o **Telegram** e mande para o seu bot. Também funciona copiar o link do reel e colar na conversa.

O bot responde "Processando...". Em cerca de 1 minuto por vídeo chegam a lista de projetos, a ficha de fatos de cada um e o arquivo `.md`. Se chegou, está tudo certo.

### Passo 8 (opcional): token do GitHub

Sem token, o GitHub limita a 60 consultas por hora, e cada projeto achado gasta de 4 a 6. Para tirar o limite: no GitHub, abra **Settings → Developer settings → Personal access tokens**, gere um token **sem marcar nenhuma permissão** e cole em `GITHUB_TOKEN=` no `.env`. Salve e reinicie o bot.

### Passo 9 (opcional): notas no Obsidian

Crie uma pasta dentro do seu vault para os repositórios e coloque o caminho completo em `OBSIDIAN_PASTA_REPOSITORIOS=` no `.env`. Exemplo:

```
OBSIDIAN_PASTA_REPOSITORIOS=C:\Users\voce\Documents\MeuVault\Repositorios
```

Cada projeto achado vira uma nota nessa pasta. As duas opções abaixo são extras, para quem já usa uma nota-índice:

```
OBSIDIAN_ARQUIVO_INDICE=Indice.md
OBSIDIAN_LINKS_RODAPE=["Indice"]
```

O primeiro faz o bot acrescentar `- [[nota]]` ao `Indice.md` (que precisa existir na mesma pasta). O segundo coloca um rodapé "Ver também" com esses links em cada nota.

### Passo 10 (opcional): ligar sozinho com o Windows

Para você não precisar abrir o bot toda vez, crie uma tarefa que o liga quando você entra no Windows, sem janela de terminal. Com o PowerShell na pasta do projeto:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\instalar_inicio_windows.ps1
```

| Ação | Comando |
|---|---|
| Ligar agora | `Start-ScheduledTask -TaskName InstagramUtilBot` |
| Parar | `Stop-ScheduledTask -TaskName InstagramUtilBot` |
| Remover | `Unregister-ScheduledTask -TaskName InstagramUtilBot -Confirm:$false` |

Antes de ligar a tarefa, **feche o bot que estiver aberto no terminal**: duas cópias com o mesmo token brigam entre si no Telegram. Se o bot cair, o Windows o religa até 3 vezes. Depois de mudar o `.env` ou atualizar o código, pare e ligue a tarefa de novo.

Com o PC desligado o bot não responde. O Telegram guarda as mensagens por cerca de 24 horas, então um reel enviado nesse período é processado quando o PC ligar.

## Se algo der errado

O bot grava tudo o que faz em `bot.log`, na pasta do projeto. Abra esse arquivo primeiro.

| O que aparece | Causa provável | O que fazer |
|---|---|---|
| `Configuração inválida no .env. Confira: TELEGRAM_TOKEN` | O `.env` não existe, o token está vazio ou você não salvou o arquivo | Refaça o passo 5 e salve com Ctrl+S |
| `O agy (Gemini) não está instalado ou não está no PATH` | O `agy` não foi instalado, ou o PowerShell foi aberto antes da instalação | Refaça o passo 2 e abra um PowerShell novo |
| `O agy não está logado` | Sem login na conta Google, ou sem internet | Rode `agy` e entre; confira com `agy models` |
| `O TELEGRAM_TOKEN foi recusado ou o Telegram está fora` | Token errado, com espaço ou aspas, ou Telegram fora do ar | Copie o token de novo do BotFather (`/mybots`) |
| O bot liga mas não responde | Duas cópias do bot rodando ao mesmo tempo, ou o `TELEGRAM_ID_AUTORIZADO` não é o seu id | Feche as cópias extras; confira o id com o passo 6 |
| `Limite de uso do GitHub atingido` | Passou de 60 consultas por hora sem token | Faça o passo 8 |
| `Não consegui: O yt-dlp falhou` | Reel privado, apagado ou bloqueado pelo Instagram, ou `yt-dlp` desatualizado | Tente outro reel; atualize com `uv sync --upgrade-package yt-dlp` |
| `O Gemini passou do tempo limite` | Gemini lento ou sem internet | Mande o reel de novo |
| `Já existia nota no Obsidian` | Já há uma nota com o nome desse repositório | Normal: o bot nunca sobrescreve notas |

## Configuração

As variáveis ficam no arquivo `.env` (modelo em `.env.example`). Campo vazio vale como "não definido".

| Variável | Obrigatória | Descrição |
|---|---|---|
| `TELEGRAM_TOKEN` | Sim | Token do bot, criado com o `@BotFather`. |
| `TELEGRAM_ID_AUTORIZADO` | Não* | Seu id no Telegram. *Vazio, o bot só responde com o seu id. |
| `GITHUB_TOKEN` | Não | Sem ele o GitHub limita a 60 consultas por hora; cada projeto achado gasta de 4 a 6. Crie um token sem nenhuma permissão marcada. |
| `OBSIDIAN_PASTA_REPOSITORIOS` | Não | Pasta onde criar uma nota por repositório. Vazio = não grava nota. |
| `OBSIDIAN_ARQUIVO_INDICE` | Não | Nota-índice (ex.: `Indice.md`, na mesma pasta) que ganha uma linha `- [[nota]]` por nota nova. |
| `OBSIDIAN_LINKS_RODAPE` | Não | Notas linkadas no rodapé "Ver também", em JSON. Ex.: `["Indice","Repositorios"]`. |

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
- O bot foi testado só no Windows.

## Testes

```powershell
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
