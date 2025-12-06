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
import datetime
import os
import sys

audio_url = "https://www.dropbox.com/scl/fi/djpoftpqp3a61mxbxf09g/nature_sound_ambient.mp3?rlkey=7med7l9l0p1uy57p05vdpr2mb&st=d4c6qkyg&dl=1"

#DiscordBotのトークン
TOKEN = 'MTEzMzU5NDMxNTgxMDE0NDMwNg.GgZ2Jw.0_WSBPGvof3s5uH4g_fD3bYDrZaqHuZsOKAOTc'
#チャンネルID
channel_id = 1133599794250657872



intents=discord.Intents.all()
intents.typing = False
client = discord.Client(intents=intents)
log = logging.getLogger(__name__)


@client.event
async def on_ready():
    print('ログインしました')
    await client.change_presence(activity=discord.Game(name='Pikurinサーバー専用BOT'))
    logch = client.get_channel(1133638395030163486)
    botlog = await logch.send('ボットが起動しました。')

    channel = client.get_channel(channel_id)
    guild = channel.guild


    await asyncio.sleep(2)
    await play_music_in_voice_channels(channel, guild, botlog)



async def play_music(channel, guild, botlog):
    try:
        if guild.voice_client:
            await guild.voice_client.disconnect()
            await asyncio.sleep(2)
        await channel.connect()
        await guild.change_voice_state(channel=guild.voice_client.channel, self_deaf=True)
        print('VCに参加成功')
        guild.voice_client.play(discord.FFmpegPCMAudio(audio_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))
        print('play!')
    except Exception as e:
        print(e)
        try:
            await botlog.edit(content=f'おっと！何かエラーが発生したようです。\nエラーのタイミング：ボイスチャンネルに接続して音楽を再生するとき\n```\n{e}\n```\n')
        except:
            await botlog.edit(content=f'おっと！何かエラーが発生したようです。\nエラーのタイミング：ボイスチャンネルに接続して音楽を再生するとき\nエラーログは長すぎて送信できません。')
    
    while True:
        if guild.voice_client:
            while guild.voice_client.is_playing():
                await asyncio.sleep(5)
            try:
                guild.voice_client.play(discord.FFmpegPCMAudio(audio_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))
            except Exception as e:
                print(e)
                try:
                    await botlog.edit(content=f'おっと！何かエラーが発生したようです。\nエラーのタイミング：2回目以降で音楽を再生するとき\n```\n{e}\n```')
                except:
                    await botlog.edit(content=f'おっと！何かエラーが発生したようです。\nエラーのタイミング：2回目以降で音楽を再生するとき\nエラーログは長すぎて送信できません。')







async def play_music_in_voice_channels(channel, guild, botlog):
    client.loop.create_task(play_music(channel, guild, botlog))









keep_alive()
client.run(TOKEN)
