FROM python:3.12.5-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y pkg-config \
    python3-dev \ 
    python3-opencv \ 
    libopencv-dev
RUN pip install -r requirements.txt

EXPOSE 80

ENTRYPOINT [ "python", "app.py" ]