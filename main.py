import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []

def yt_dl_source(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "default_search": "auto",
        "noplaylist": True,
    }
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        title = info.get('title', url)
        webpage_url = info.get('webpage_url', url)
        thumbnail = info.get('thumbnail', None)
        return audio_url, title, webpage_url, thumbnail

async def play_next(ctx):
    if queue:
        url = queue.pop(0)
        audio_url, title, webpage_url, thumbnail = yt_dl_source(url)
        source = await discord.FFmpegOpusAudio.from_probe(audio_url)
        ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

        # Embedでタイトル＋サムネイルを送信
        embed = discord.Embed(title=f"Now Playing: {title}", url=webpage_url, description=f"リクエスト: {ctx.author.display_name}")
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        await ctx.send(embed=embed)
    else:
        await ctx.send("再生する曲はありません。")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("ボイスチャンネルに入りました。")
    else:
        await ctx.send("先にボイスチャンネルに入ってください。")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("退出しました。")

@bot.command()
async def play(ctx, *, url):
    if not ctx.voice_client:
        await ctx.invoke(bot.get_command("join"))
    queue.append(url)
    if not ctx.voice_client.is_playing():
        await play_next(ctx)
    else:
        await ctx.send("キューに追加しました。")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("次の曲にスキップしました。")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        queue.clear()
        ctx.voice_client.stop()
        await ctx.send("再生を停止し、キューを空にしました。")

@bot.command()
async def queue_list(ctx):
    if queue:
        msg = "キュー:\n" + "\n".join(f"{i+1}. {url}" for i, url in enumerate(queue))
        await ctx.send(msg)
    else:
        await ctx.send("キューは空です。")

bot.run("YOUR_DISCORD_BOT_TOKEN")
