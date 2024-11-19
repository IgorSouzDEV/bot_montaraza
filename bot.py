import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Crie uma instância do bot
intents = discord.Intents.default()
intents.messages = True  # Habilita a leitura de mensagens
intents.message_content = True  # Habilita a leitura do conteúdo das mensagens
bot = commands.Bot(command_prefix='/', intents=intents)

# Dicionário para armazenar produtos por canal
produtos_por_canal = {}


def carregar_produtos():
    """Carrega produtos de um arquivo JSON."""
    if os.path.exists('produtos.json'):
        with open('produtos.json', 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Erro ao decodificar o arquivo JSON. O arquivo pode estar vazio ou malformado.")
                return {}
    return {}


def salvar_produtos():
    """Salva os produtos armazenados em um arquivo JSON."""
    try:
        with open('produtos.json', 'w') as f:
            json.dump(produtos_por_canal, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar produtos: {e}")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    global produtos_por_canal
    produtos_por_canal = carregar_produtos()  # Carrega produtos ao iniciar


@bot.command()
async def adicionar(ctx, codigo: int, *, produto: str):
    """Adiciona um produto ao canal atual."""
    canal_id = str(ctx.channel.id)
    if canal_id not in produtos_por_canal:
        produtos_por_canal[canal_id] = {}

    # Verifica se o código já existe
    if codigo in produtos_por_canal[canal_id]:
        await ctx.reply(f"Produto com código {codigo} já existe. Use um código diferente.")
        return

    produtos_por_canal[canal_id][codigo] = produto
    salvar_produtos()  # Salva os produtos após adicionar
    await ctx.reply(f"Produto adicionado: {produto} com código {codigo}.")
    print(f"Produto adicionado no canal {ctx.channel.name}: {produto} (Código: {codigo})")  # Log no console


@bot.command()
@commands.has_role('Moderador')  # Ou use @commands.has_permissions(manage_messages=True)
async def remover(ctx, codigo: int):
    """Remove um produto do canal atual, apenas para moderadores."""
    canal_id = str(ctx.channel.id)
    if canal_id in produtos_por_canal and codigo in produtos_por_canal[canal_id]:
        del produtos_por_canal[canal_id][codigo]
        salvar_produtos()  # Salva os produtos após remover
        await ctx.reply(f"Produto com código {codigo} removido.")
    else:
        await ctx.reply(f"Produto com código {codigo} não encontrado.")


@remover.error
async def remover_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.reply("Você não tem permissão para usar este comando.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("Você precisa da permissão 'Gerenciar Mensagens' para usar este comando.")


@bot.command()
async def listar(ctx):
    """Lista todos os produtos do canal atual."""
    canal_id = str(ctx.channel.id)
    if canal_id in produtos_por_canal and produtos_por_canal[canal_id]:
        produtos = "\n".join([f"Código: {codigo}, Produto: {produto}" for codigo, produto in produtos_por_canal[canal_id].items()])
        await ctx.reply(f"Produtos no canal:\n{produtos}")
    else:
        await ctx.reply("Nenhum produto encontrado neste canal.")


@bot.command()
async def ajuda(ctx):
    """Mostra a lista de comandos disponíveis."""
    ajuda_msg = (
        "Aqui estão os comandos disponíveis:\n"
        "`/adicionar <código> <nome do produto>` - Adiciona um produto ao canal.\n"
        "`/remover <código>` - Remove um produto do canal.\n"
        "`/listar` - Lista todos os produtos do canal.\n"
        "`/ajuda` - Mostra esta mensagem de ajuda.\n"
        "`/saudacao` - Envia uma saudação."
    )
    await ctx.reply(ajuda_msg)


@bot.command()
async def saudacao(ctx):
    """Envia uma saudação ao usuário."""
    await ctx.reply(f"Olá, {ctx.author.mention}! Como posso ajudar você hoje?")


def verificar_permissoes(arquivo):
    """Verifica se o arquivo pode ser lido e escrito."""
    pode_ler = os.access(arquivo, os.R_OK)
    pode_escrever = os.access(arquivo, os.W_OK)

    if pode_ler and pode_escrever:
        print(f"O arquivo '{arquivo}' pode ser lido e escrito.")
    elif pode_ler:
        print(f"O arquivo '{arquivo}' pode ser lido, mas não pode ser escrito.")
    elif pode_escrever:
        print(f"O arquivo '{arquivo}' pode ser escrito, mas não pode ser lido.")
    else:
        print(f"O arquivo '{arquivo}' não pode ser lido nem escrito.")


# Exemplo de uso
verificar_permissoes('produtos.json')


async def main():
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')  # Obtém o token do bot do arquivo .env
    try:
        await bot.start(DISCORD_TOKEN)  # Usa o token carregado
    except Exception as e:
        print(f'Ocorreu um erro ao iniciar o bot: {e}')

# Executa a função main
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
