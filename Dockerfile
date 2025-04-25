FROM python:3.13-slim

RUN apt-get update && \
    python -m ensurepip && \
    pip install --no-cache-dir --upgrade pip

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --root-user-action=ignore

COPY app/ .

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD ["python", "main.py"]
