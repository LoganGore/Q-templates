FROM python:3

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

EXPOSE 8050

CMD ["python3.7", "server.py"]
