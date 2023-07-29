FROM python:3.11
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /bot
CMD python main.py
