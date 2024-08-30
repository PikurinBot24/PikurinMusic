from flask import Flask
from threading import Thread
import datetime


app = Flask('')


@app.route('/')
def home():
    timenow = datetime.datetime.now() + datetime.timedelta(hours=9)
    return f'''
    <html>
    <head>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f9;
                color: #333;
                text-align: center;
                padding: 50px;
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                padding: 30px;
                max-width: 600px;
                margin: auto;
            }}
            h1 {{
                color: #007bff;
                font-size: 24px;
            }}
            p {{
                font-size: 18px;
                margin: 10px 0;
            }}
            .timestamp {{
                font-size: 20px;
                font-weight: bold;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PikurinBot サーバー状況</h1>
            <p class="timestamp">【{timenow}】</p>
            <p>サーバーは正常です。</p>
            <p>もしPikurinBotがオフラインである場合は、サーバーのプログラムでエラーが発生し停止してしまった可能性があります。</p>
            <p>再起動をお待ちください。</p>
        </div>
    </body>
    </html>
    '''


def run():
  app.run(host='0.0.0.0', port=1236)


def keep_alive():
  t = Thread(target=run)
  t.start()
