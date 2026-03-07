from keep_alive import keep_alive
import discord
import asyncio
import logging
import os
import aiohttp

TOKEN = os.environ["DISCORD_TOKEN"]

CHANNEL_ID = 1277188290121961586

AUDIO_URL = "https://github.com/PikurinBot24/PikurinMusic/releases/download/v2/audio.opus"
AUDIO_FILE = "audio.opus"


intents = discord.Intents.default()
intents.voice_states = True

client = discord.Client(intents=intents)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# ----------------------------
# 音源ダウンロード
# ----------------------------

async def download_audio():

    if os.path.exists(AUDIO_FILE):
        return

    log.info("音源ダウンロード開始")

    async with aiohttp.ClientSession() as session:
        async with session.get(AUDIO_URL) as resp:

            if resp.status != 200:
                log.error("音源ダウンロード失敗")
                return

            with open(AUDIO_FILE, "wb") as f:
                f.write(await resp.read())

    log.info("音源ダウンロード完了")


# ----------------------------
# 再生
# ----------------------------

def start_play(vc: discord.VoiceClient):

    if vc.is_playing():
        return

    source = discord.FFmpegOpusAudio(
        AUDIO_FILE,
        before_options="-stream_loop -1",
        options="-loglevel quiet"
    )

    vc.play(source)

    log.info("音声再生開始")


# ----------------------------
# VC接続保証
# ----------------------------

async def ensure_voice(channel):

    vc = channel.guild.voice_client

    if vc and vc.is_connected():

        if not vc.is_playing():
            log.info("再生停止検知 → 再開")
            start_play(vc)

        return vc

    try:
        if vc:
            await vc.disconnect(force=True)
    except:
        pass

    await asyncio.sleep(2)

    log.info("VC接続")

    vc = await channel.connect(self_deaf=True)

    start_play(vc)

    return vc


# ----------------------------
# 再接続検知
# ----------------------------

@client.event
async def on_voice_state_update(member, before, after):

    if member.id != client.user.id:
        return

    vc = member.guild.voice_client

    if vc and not vc.is_playing():
        log.info("VC状態変化 → 再生再開")
        start_play(vc)


# ----------------------------
# メイン監視ループ
# ----------------------------

async def play_loop(channel):

    await client.wait_until_ready()

    await asyncio.sleep(5)

    await download_audio()

    while True:

        try:

            vc = await ensure_voice(channel)

            if not vc.is_playing():
                start_play(vc)

            if not vc.is_connected():
                log.warning("VC切断検知 → 再接続")
                vc = await ensure_voice(channel)

            await asyncio.sleep(30)

        except Exception:

            log.exception("メインループエラー")

            await asyncio.sleep(10)


# ----------------------------
# 起動
# ----------------------------

@client.event
async def on_ready():

    log.info("ログイン成功")

    await client.change_presence(
        activity=discord.Game(name="Pikurinサーバー専用BOT")
    )

    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        log.error("VCが見つかりません")
        return

    client.loop.create_task(play_loop(channel))


keep_alive()

client.run(TOKEN)
