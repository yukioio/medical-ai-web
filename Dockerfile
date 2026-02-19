# 3.9 から 3.12 へ変更
FROM python:3.12-slim

WORKDIR /app

# ビルド時の余計なキャッシュを生成しない設定
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

# pip 自体も最新にしてからインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

# 修正版 CMD
CMD ["streamlit", "run", "app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
