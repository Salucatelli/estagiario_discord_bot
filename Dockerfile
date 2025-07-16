FROM python:3.11

WORKDIR /usr/src/app

# Instala ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

COPY ./bot ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]