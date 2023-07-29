from flask import Flask
from threading import Thread
import datetime

app = Flask('')

@app.route('/')
def home():
  timenow = datetime.datetime.now() + datetime.timedelta(hours=9)
  return f'<font color="blue", size="7">【{timenow}】PikurinServer用BOT<p>サーバー状況:<p>サーバーは正常です<p><p>もしPikurinBotがオフラインである場合は、サーバーのプログラムでエラーが発生し停止してしまった可能性があります。再起動をお待ちください。'

def run():
  app.run(host='0.0.0.0', port=1235)

def keep_alive():
  t = Thread(target=run)
  t.start()
