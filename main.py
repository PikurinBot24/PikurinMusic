runproject = 1
if runproject == 0:
    exit()

from keep_alive import keep_alive
import discord
from discord.opus import Encoder as OpusEncoder
import shlex
import subprocess
import logging
import asyncio
from googleapiclient.discovery import build
from pytube import YouTube
from pytube import Search

#24時間音楽を流すときの音楽
musicdefaulturl = 'https://youtube.com/watch?v=SHpQ77wDfYg'
#DiscordBotのトークン
TOKEN = 'MTEzMzU5NDMxNTgxMDE0NDMwNg.GpDXeN.YQSvyDFU7I4wwXCXRdbwtLJp80N_nDXNXlxOZ8'
#チャンネルID
channel_id = 1133599794250657872



intents=discord.Intents.all()
intents.typing = False
client = discord.Client(intents=intents)
youtubedataapi = build('youtube', 'v3', developerKey='AIzaSyCIiSbM5QWgxJC4KqKCcR3_jPc0ISIObng')
log = logging.getLogger(__name__)

ffmpeg_options = {
    'before_options':
    '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 600'
}




class OriginalFFmpegPCMAudio(discord.FFmpegPCMAudio):
    def __init__(self,
                 source,
                 *,
                 executable='ffmpeg',
                 pipe=False,
                 stderr=None,
                 before_options=None,
                 options=None):
        self.total_milliseconds = 0
        self.source = source

        super().__init__(source,
                         executable=executable,
                         pipe=pipe,
                         stderr=stderr,
                         before_options=before_options,
                         options=options)

    def wait_buffer(self):
        self._stdout.peek(OpusEncoder.FRAME_SIZE)

    def read(self):
        ret = super().read()

        if ret:
            self.total_milliseconds += 20
        return ret

    def get_tootal_millisecond(self, seek_time):
        if seek_time:
            list = reversed([int(x) for x in seek_time.split(":")])
            total = 0
            for i, x in enumerate(list):
                total += x * 3600 if i == 2 else x * 60 if i == 1 else x
            return max(1000 * total, 0)
        else:
            raise Exception()

    def rewind(self,
               rewind_time,
               *,
               executable='ffmpeg',
               pipe=False,
               stderr=None,
               before_options=None,
               options=None):
        seek_time = str(
            int((self.total_milliseconds -
                 self.get_tootal_millisecond(rewind_time)) / 1000))

        self.seek(seek_time=seek_time,
                  executable=executable,
                  pipe=pipe,
                  stderr=stderr,
                  before_options=before_options,
                  options=options)

    def seek(self,
             seek_time,
             *,
             executable='ffmpeg',
             pipe=False,
             stderr=None,
             before_options=None,
             options=None):
        self.total_milliseconds = self.get_tootal_millisecond(seek_time)
        proc = self._process
        before_options = f"-ss {seek_time} " + before_options
        args = []
        subprocess_kwargs = {
            'stdin': self.source if pipe else subprocess.DEVNULL,
            'stderr': stderr
        }

        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))

        args.append('-i')
        args.append('-' if pipe else self.source)
        args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel',
                     'warning'))

        if isinstance(options, str):
            args.extend(shlex.split(options))

        args.append('pipe:1')

        args = [executable, *args]
        kwargs = {'stdout': subprocess.PIPE}
        kwargs.update(subprocess_kwargs)

        self._process = self._spawn_process(args, **kwargs)
        self._stdout = self._process.stdout
        self.kill(proc)

    def kill(self, proc):
        if proc is None:
            return

        log.info('Preparing to terminate ffmpeg process %s.', proc.pid)

        try:
            proc.kill()
        except Exception:
            log.exception(
                "Ignoring error attempting to kill ffmpeg process %s",
                proc.pid)

        if proc.poll() is None:
            log.info(
                'ffmpeg process %s has not terminated. Waiting to terminate...',
                proc.pid)
            proc.communicate()
            log.info(
                'ffmpeg process %s should have terminated with a return code of %s.',
                proc.pid, proc.returncode)
        else:
            log.info(
                'ffmpeg process %s successfully terminated with return code of %s.',
                proc.pid, proc.returncode)




@client.event
async def on_ready():
    print('ログインしました')
    await client.change_presence(activity=discord.Game(name='Pikurinサーバー専用BOT'))
    logch = client.get_channel(1133638395030163486)
    botlog = await logch.send('ボットが起動しました。')

    channel = client.get_channel(channel_id)
    guild = channel.guild

    if guild.voice_client:
        await guild.voice_client.disconnect()
        await asyncio.sleep(2)
    await channel.connect()
    await asyncio.sleep(2)
    await play_music_in_voice_channels(channel, guild, botlog)



async def play_music(channel, guild, botlog):
    if guild.voice_client:
        await guild.voice_client.disconnect()
        await asyncio.sleep(2)
    await channel.connect()
    await guild.change_voice_state(channel=guild.voice_client.channel, self_deaf=True)

    try:
        yt = YouTube(musicdefaulturl)
        seconds=yt.length
        audio_url = yt.streams.filter(only_audio=True).first().url
        guild.voice_client.play(OriginalFFmpegPCMAudio(audio_url, **ffmpeg_options))
    except Exception as e:
        print(e)
        try:
            await botlog.edit(content=f'おっと！何かエラーが発生したようです。\n```\n{e}\n```')
        except:
            await botlog.edit(content=f'おっと！何かエラーが発生したようです。\nエラーログは長すぎて送信できません。')
        return
    

    await asyncio.sleep(seconds)
    while True:
        if guild.voice_client:
            while guild.voice_client.is_playing():
                await asyncio.sleep(3)
            try:
                yt = YouTube(musicdefaulturl)
                audio_url = yt.streams.filter(only_audio=True).first().url
                guild.voice_client.play(OriginalFFmpegPCMAudio(audio_url, **ffmpeg_options))
            except Exception as e:
                print(e)
                try:
                    await botlog.edit(content=f'おっと！何かエラーが発生したようです。\n```\n{e}\n```')
                except:
                    await botlog.edit(content=f'おっと！何かエラーが発生したようです。\nエラーログは長すぎて送信できません。')
            await asyncio.sleep(seconds)







async def play_music_in_voice_channels(channel, guild, botlog):
    client.loop.create_task(play_music(channel, guild, botlog))









keep_alive()
client.run(TOKEN)
