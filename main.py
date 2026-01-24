from keep_alive import keep_alive
import discord
import asyncio
import logging
import os

# GitHub Releases の音源
AUDIO_URL = "https://github.com/PikurinBot24/PikurinMusic/releases/download/v1/audio.mp3"

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = 1133599794250657872

intents = discord.Intents.all()
intents.typing = False
client = discord.Client(intents=intents)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def connect_voice(channel: discord.VoiceChannel) -> discord.VoiceClient:
    """VC接続を保証する（切断時は再接続）"""
    vc = channel.guild.voice_client

    if vc is None:
        log.info("VCに新規接続します")
        return await channel.connect(self_deaf=True)

    if not vc.is_connected():
        log.warning("VCが切断されていたため再接続します")
        try:
            await vc.disconnect(force=True)
        except Exception:
            pass
        return await channel.connect(self_deaf=True)

    return vc


def create_source():
    """FFmpeg音源を生成"""
    return discord.FFmpegPCMAudio(
        AUDIO_URL,
        before_options=(
            "-reconnect 1 "
            "-reconnect_streamed 1 "
            "-reconnect_delay_max 5"
        ),
        options="-vn"
    )


async def play_loop(channel: discord.VoiceChannel):
    await client.wait_until_ready()

    last_connected = False

    while not client.is_closed():
        try:
            vc = await connect_voice(channel)

            # 接続状態チェック
            if vc is None or not vc.is_connected():
                last_connected = False
                await asyncio.sleep(2)
                continue

            # 🔴 再接続を検知したら必ず再生し直す
            if not last_connected:
                log.info("VC再接続を検知。再生を初期化します")
                if vc.is_playing() or vc.is_paused():
                    vc.stop()

                vc.play(create_source())
                last_connected = True

            # 再生が止まっていたら再開
            if not vc.is_playing():
                log.info("再生が停止していたため再開します")
                vc.play(create_source())

            await asyncio.sleep(1)

        except Exception:
            log.exception("play_loop error")
            last_connected = False
            await asyncio.sleep(5)


@client.event
async def on_ready():
    print("ログインしました")
    await client.change_presence(
        activity=discord.Game(name="Pikurinサーバー専用BOT")
    )

    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        log.error("指定されたVCが見つかりません")
        return

    client.loop.create_task(play_loop(channel))


keep_alive()
client.run(TOKEN)
