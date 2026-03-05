from keep_alive import keep_alive
import discord
import asyncio
import logging
import os
import aiohttp

AUDIO_URL = "https://github.com/PikurinBot2473/PikurinBot2473/releases/download/v1/auido.mp3"
AUDIO_FILE = "audio.mp3"

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = 1277188290121961586

intents = discord.Intents.all()
intents.typing = False
client = discord.Client(intents=intents)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# ---------- 音源DL（初回のみ） ----------
async def download_audio():
    if os.path.exists(AUDIO_FILE):
        return

    log.info("音源をダウンロード中...")
    async with aiohttp.ClientSession() as session:
        async with session.get(AUDIO_URL) as resp:
            with open(AUDIO_FILE, "wb") as f:
                f.write(await resp.read())

    log.info("音源ダウンロード完了")


# ---------- VC接続保証（安定版） ----------
async def ensure_voice(channel: discord.VoiceChannel):
    vc = channel.guild.voice_client

    if vc and vc.is_connected():
        return vc

    try:
        if vc:
            await vc.disconnect(force=True)
    except Exception:
        pass

    await asyncio.sleep(2)

    return await channel.connect(self_deaf=True, reconnect=True)


# ---------- 再生 ----------
def start_play(vc: discord.VoiceClient):
    if vc.is_playing():
        return

    source = discord.FFmpegPCMAudio(
        AUDIO_FILE,
        options="-vn"
    )

    def after(err):
        if err:
            log.error(f"再生エラー: {err}")

        if vc.is_connected():
            asyncio.run_coroutine_threadsafe(
                delayed_restart(vc), client.loop
            )

    vc.play(source, after=after)
    log.info("音声再生開始")


async def delayed_restart(vc):
    await asyncio.sleep(2)
    start_play(vc)


# ---------- メインループ ----------
async def play_loop(channel):
    await client.wait_until_ready()

    # Discord起動安定待機
    await asyncio.sleep(5)

    await download_audio()

    while True:
        try:
            vc = await ensure_voice(channel)
            start_play(vc)
            await asyncio.sleep(10)

        except Exception:
            log.exception("メインループエラー")
            await asyncio.sleep(5)


# ---------- 起動 ----------
@client.event
async def on_ready():
    log.info("ログインしました")

    await client.change_presence(
        activity=discord.Game(name="Pikurinサーバー専用BOT")
    )

    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        log.error("VCが見つかりません")
        return

    client.loop.create_task(play_loop(channel))


keep_alive()
client.run(TOKEN)
