from keep_alive import keep_alive
import discord
import asyncio
import logging
import os

# GitHub Releases の音源（指定どおり）
audio_url = "https://github.com/PikurinBot24/PikurinMusic/releases/download/v1/audio.mp3"

TOKEN = os.environ["DISCORD_TOKEN"]
channel_id = 1133599794250657872

intents = discord.Intents.all()
intents.typing = False
client = discord.Client(intents=intents)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def ensure_voice(channel: discord.VoiceChannel):
    vc = channel.guild.voice_client

    # まだ接続していない場合
    if vc is None:
        return await channel.connect(self_deaf=True)

    # 何らかの理由で切断されている場合
    if not vc.is_connected():
        try:
            await vc.disconnect(force=True)
        except Exception:
            pass
        return await channel.connect(self_deaf=True)

    return vc


async def play_loop(channel: discord.VoiceChannel):
    await client.wait_until_ready()

    while not client.is_closed():
        try:
            vc = await ensure_voice(channel)

            if vc is None:
                await asyncio.sleep(3)
                continue

            # 再生中なら待機
            if vc.is_playing() or vc.is_paused():
                await asyncio.sleep(5)
                continue

            source = discord.FFmpegPCMAudio(
                audio_url,
                before_options=(
                    "-reconnect 1 "
                    "-reconnect_streamed 1 "
                    "-reconnect_delay_max 5"
                ),
                options="-vn"
            )

            vc.play(source)
            log.info("音声再生開始")

            # 再生が終わるまで待つ
            while vc.is_playing():
                await asyncio.sleep(1)

            # 少し間を置いてから次ループ（安定用）
            await asyncio.sleep(1)

        except Exception:
            log.exception("play_loop error")
            await asyncio.sleep(5)


@client.event
async def on_ready():
    print("ログインしました")
    await client.change_presence(
        activity=discord.Game(name="Pikurinサーバー専用BOT")
    )

    channel = client.get_channel(channel_id)
    if channel is None:
        log.error("指定されたVCが見つかりません")
        return

    client.loop.create_task(play_loop(channel))


keep_alive()
client.run(TOKEN)
