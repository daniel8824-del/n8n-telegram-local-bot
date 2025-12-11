FROM aiogram/telegram-bot-api:latest

# 작업 디렉토리 설정
WORKDIR /app

# Railway 포트 환경 변수 사용
ENV PORT=8080

# Telegram API 환경 변수는 Railway에서 주입됨
# TELEGRAM_API_ID와 TELEGRAM_API_HASH

# 포트 노출
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

# 실행 명령어 (환경 변수 직접 참조)
CMD telegram-bot-api \
    --local \
    --api-id=$TELEGRAM_API_ID \
    --api-hash=$TELEGRAM_API_HASH \
    --http-port=8080 \
    --log=/tmp/telegram-bot-api.log \
    --verbosity=2