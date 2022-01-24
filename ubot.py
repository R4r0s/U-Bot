import asyncio
import random
from asyncio import sleep
from datetime import datetime
from math import sqrt

import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio, utils
from youtube_dl import YoutubeDL

bot = commands.Bot(command_prefix=".", help_command=None)
TOKEN = open("TOKEN.txt").read()

queue = []
banWords = ["gilipollas", "imbecil", "puta", "zorra", "mierda"]
answers = ["Si", "No", "No se", "Ni de broma", "Por supuesto"]


@bot.event
async def on_ready():
    custom = discord.Game("Usa !help para obtener una lista con todos los comandos")
    await bot.change_presence(status=discord.Status.online, activity=custom)


@bot.command(pass_context=True, aliases=['p'])
async def play(ctx, arg):
    try:

        if not queue:
            queue.append(arg)
            await ctx.send("Se ha añadido a la cola")
            channel = ctx.author.voice.channel
            await channel.connect()
        voice = get(bot.voice_clients, guild=ctx.guild)
        ybdl_options = {'format': 'bestaudio', 'noplaylist': 'True'}
        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        if not voice.is_playing():
            while queue:

                with YoutubeDL(ybdl_options) as ydl:
                    info = ydl.extract_info(queue[0], download=False)
                title = info.get("title", None)
                await ctx.send("Playing " + "***" + title + "***")
                url = info['formats'][0]['url']
                voice.play(FFmpegPCMAudio(url, **ffmpeg_options))
                voice.is_playing()

                while voice.is_playing:
                    await sleep(1)
                queue.pop(0)
            await voice.disconnect()

        else:
            queue.append(arg)
            with YoutubeDL(ybdl_options) as ydl:
                info = ydl.extract_info(arg, download=False)
            title = info.get("title", None)
            await ctx.send("***" + title + "***" + " added to the queue")
            return

    except AttributeError:
        await ctx.send("You are not in a voice channel")

    except utils.DownloadError:
        await ctx.send("No video has been found")


@bot.command(pass_context=True, aliases=['st'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    await voice.disconnect()
    queue.clear()


@bot.command(pass_context=True, aliases=['s'])
async def skip(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not queue:
        await ctx.send("Nothing to skip")

    else:
        await ctx.send("Skipping song")
        ybdl_options = {'format': 'bestaudio', 'noplaylist': 'True'}
        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        voice.stop()
        with YoutubeDL(ybdl_options) as ydl:
            info = ydl.extract_info(queue[1], download=False)
        title = info.get("title", None)
        await ctx.send("Playing " + "***" + title + "***")
        url = info['formats'][0]['url']
        voice.play(FFmpegPCMAudio(url, **ffmpeg_options))
        queue.pop(1)
        queue.pop(0)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    author = message.author
    mess = str(message.content)
    for word in banWords:
        if word in str.lower(mess):
            await message.delete()
            await author.send("Tu mensaje a sido eliminado por contener una palabra no permitida: ***" + word + "***")


@bot.command(pass_context=True, aliases=["aw"])
async def addword(ctx, arg):
    banWords.append(str(arg))
    print(banWords)


@bot.command(pass_context=True, )
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)


@bot.command(pass_context=True, )
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return


@bot.command(pass_context=True, aliases=["c"])
async def calc(ctx, arg, arg1, arg2):
    if arg1 != "/" or arg2 != "0":
        result = 0
        if arg1 == "+":
            result = int(arg) + int(arg2)
        if arg1 == "-":
            result = int(arg) - int(arg2)
        if arg1 == "*":
            result = int(arg) * int(arg2)
        if arg1 == "/":
            result = int(arg) / int(arg2)
        await ctx.send("El resultado de " + str(arg) + str(arg1) + str(arg2) + " es: ***" + str(result) + "***")
    else:
        await ctx.send("No se puede dividir entre 0")


@bot.command(pass_context=True, aliases=["equa"])
async def ecuacion(ctx, arg, arg1, arg2):
    if ((int(arg1) ** 2) - 4 * int(arg) * int(arg2)) < 0:
        await ctx.send("La solución de la ecuación es con numeros complejos")
    else:
        x1 = (-int(arg1) + sqrt(int(arg1) ** 2 - (4 * int(arg) * int(arg2)))) / (2 * int(arg))
        x2 = (-int(arg1) - sqrt(int(arg1) ** 2 - (4 * int(arg) * int(arg2)))) / (2 * int(arg))
        await ctx.send("Las soluciones de la ecuación son: ***" + str(x1) + " " + str(x2) + "***")


@bot.command(pass_context=True)
async def ball(ctx, *, quest):
    print(quest)
    try:
        if str.__contains__(quest, '?'):
            await ctx.send(random.choice(answers))
        else:
            await ctx.send("¿Eso es una pregunta?")
    except IndexError:
        await ctx.channel.send('Preguntame algo...')


@bot.command(case_insensitive=True, aliases=["rm"])
async def reminder(ctx, time, *, reminder):
    print(time)
    print(reminder)
    embed = discord.Embed(color=0x55a7f7, timestamp=datetime.utcnow())
    seconds = 0
    if reminder is None:
        embed.add_field(name='Cuidado', value='Por favor especifica el recordatorio.')
    if time.lower().endswith("d"):
        seconds += int(time[:-1]) * 60 * 60 * 24
        counter = f"{seconds // 60 // 60 // 24} dias"
    if time.lower().endswith("h"):
        seconds += int(time[:-1]) * 60 * 60
        counter = f"{seconds // 60 // 60} horas"
    elif time.lower().endswith("m"):
        seconds += int(time[:-1]) * 60
        counter = f"{seconds // 60} minutos"
    elif time.lower().endswith("s"):
        seconds += int(time[:-1])
        counter = f"{seconds} segundos"
    if seconds == 0:
        embed.add_field(name='Cuidado',
                        value='La duración no es correcta.')
    elif seconds < 300:
        embed.add_field(name='Cuidado',
                        value='La duración es demasiado corta!\nEl minimo son 5 minutos.')
    elif seconds > 7776000:
        embed.add_field(name='Cuidado', value='La duración es demasiado larga!\nEl maximo son 90 días.')
    else:
        await ctx.send(f"El recordatorio {reminder} saltara en {counter}.")
        await asyncio.sleep(seconds)
        await ctx.send(f"{reminder}")
        return
    await ctx.send(embed=embed)


@bot.command(pass_context=True, aliases=['h'])
async def help(ctx):
    author = ctx.message.author
    embed = discord.Embed(
        colour=discord.Colour.purple()
    )
    embed.set_author(name="U-bot's Help")
    embed.add_field(name="!help, !h", value="Muestra esta lista.", inline=False)
    embed.add_field(name="!play, !p",
                    value="Reproduce audio desde una URL, si ya se esta reproduciendo algo lo añade a la lista.",
                    inline=False)
    embed.add_field(name="!stop, !st", value="Desconecta el bot del canal de audio, borra la lista y para el audio.",
                    inline=False)
    embed.add_field(name="!skip, !s", value="Se salta el audio actual.", inline=False)
    embed.add_field(name="!ball", value="Bola 8.", inline=False)
    embed.add_field(name="!ban", value="Comando solo para moderadores, expulsa al usuario del servidor.", inline=False)
    embed.add_field(name="!saddword, !ad", value="Comando solo para moderadores, añade palabras prohibidas a la lista.",
                    inline=False)
    embed.add_field(name="!calc, !c", value="Realiza calculos basicos (Formato: num1 operador num2).", inline=False)
    embed.add_field(name="!ecuacion, !equa", value="resuelve ecuaciones de segundo grado (Formato: a b c).",
                    inline=False)
    embed.add_field(name="!reminder, !rm", value="Comando solo para moderadores. Crea recordatorios (Formato: "
                                                   "tiempo (1s/5m/2h/1d), recordatorio).", inline=False)
    await author.send(embed=embed)


bot.run(TOKEN)
