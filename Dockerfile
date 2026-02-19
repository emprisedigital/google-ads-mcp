FROM python:3.12-slim

RUN pip install uv
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g supergateway && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN uv sync

EXPOSE 8080

CMD sh -c 'echo "GOOGLE_ADS_DEVELOPER_TOKEN=${GOOGLE_ADS_DEVELOPER_TOKEN}\nGOOGLE_ADS_CLIENT_ID=${GOOGLE_ADS_CLIENT_ID}\nGOOGLE_ADS_CLIENT_SECRET=${GOOGLE_ADS_CLIENT_SECRET}\nGOOGLE_ADS_REFRESH_TOKEN=${GOOGLE_ADS_REFRESH_TOKEN}\nGOOGLE_ADS_LOGIN_CUSTOMER_ID=${GOOGLE_ADS_LOGIN_CUSTOMER_ID}" > .env && supergateway --stdio "uv run main.py --groups all" --port 8080 --host 0.0.0.0'
