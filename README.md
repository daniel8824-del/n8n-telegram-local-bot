# Telegram Local Bot API Server - Railway 배포

**20MB 이상의 텔레그램 파일을 다운로드하기 위한 Local Bot API Server**

## 🎯 목적

- ✅ **20MB 초과 파일 다운로드** (최대 2GB까지 지원)
- ✅ **Bot Token 그대로 사용** (Premium 불필요)
- ✅ **n8n과 쉽게 연동**
- ✅ **파일 크기별 자동 분기 처리**

## 📊 파일 크기별 처리

| 파일 크기 | 사용 API | 제한 |
|---------|---------|------|
| ≤20MB | Standard Bot API | ✅ 즉시 처리 |
| 20MB ~ 2GB | Local Bot API (Railway) | ✅ 이 프로젝트 |
| >2GB | file_id만 저장 | ⚠️ 재전송 필요 |

## ⚠️ 중요: 배포 전 확인

현재 구조는 **프록시 서버**입니다. 완전한 기능을 위해서는 **Local Bot API Server**가 필요합니다.

**빠른 시작:** [`QUICK_START.md`](./QUICK_START.md) 참고

## 🚀 Railway 배포 방법

### 1. Railway 계정 생성 및 프로젝트 생성

1. [Railway](https://railway.app/)에 접속하여 계정을 생성합니다.
2. "New Project"를 클릭합니다.
3. "Deploy from GitHub repo"를 선택하거나 "Empty Project"를 선택합니다.

### 2. GitHub 저장소 연결

GitHub 저장소를 사용하는 경우:
1. 이 프로젝트를 GitHub에 푸시
2. Railway 대시보드에서 "New Project" > "Deploy from GitHub repo" 선택
3. 저장소를 선택하고 연결
4. 자동으로 배포가 시작됩니다

### 3. 환경 변수 설정

Railway 대시보드의 "Variables" 탭에서 다음 환경 변수를 설정합니다:

**필수:**
- `TELEGRAM_BOT_TOKEN`: 텔레그램 봇 토큰 (BotFather에서 발급)

**선택사항:**
- `TELEGRAM_API_ID`: 텔레그램 API ID (Local Bot API Server용, 공식 API에서 발급)
- `TELEGRAM_API_HASH`: 텔레그램 API Hash (Local Bot API Server용)
- `LOCAL_API_URL`: Local Bot API Server URL (기본값: http://localhost:8081)
- `PORT`: 포트 번호 (Railway가 자동으로 설정)

### 4. 배포

Railway는 자동으로 다음을 수행합니다:
- Dockerfile을 사용하여 이미지 빌드
- Python 의존성 설치
- 애플리케이션 실행

### 5. 도메인 확인

배포가 완료되면 Railway가 제공하는 도메인을 확인할 수 있습니다.
예: `https://your-app-name.up.railway.app`

## 🔧 API 엔드포인트

### `GET /` 또는 `GET /health`
서버 상태 확인

**Response:**
```json
{
  "status": "ok",
  "message": "Telegram Local Bot API Proxy is running",
  "max_file_size": "2GB",
  "standard_api_limit": "20MB"
}
```

### `POST /api/getFile`
파일 다운로드 (자동으로 Local/Standard API 선택)

**Request:**
```json
{
  "file_id": "BAACAgIAAxkBAAIB..."
}
```

**Response:** 파일 다운로드 (binary)

### `POST /api/getFileInfo`
파일 정보 조회 (다운로드 없이)

**Request:**
```json
{
  "file_id": "BAACAgIAAxkBAAIB..."
}
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "file_id": "BAACAgIAAxkBAAIB...",
    "file_unique_id": "AgAD...",
    "file_size": 38651904,
    "file_size_mb": 36.78,
    "file_path": "videos/file_123.mp4",
    "recommended_api": "local"
  }
}
```

### `POST /api/proxy/<method>`
모든 Telegram Bot API 메서드 프록시

예: `/api/proxy/sendMessage`, `/api/proxy/getUpdates` 등

## 🔗 n8n 연동

자세한 n8n 연동 가이드는 [`n8n-integration.md`](./n8n-integration.md)를 참고하세요.

### 빠른 시작

1. **파일 크기 확인**
```javascript
const fileSize = $input.item.json.message.video?.file_size || 0;
return fileSize > 20971520; // 20MB 초과 여부
```

2. **Local API로 파일 다운로드**
- HTTP Request 노드
- URL: `https://your-railway-app.railway.app/api/getFile`
- Method: POST
- Body: `{"file_id": "{{ $json.message.video.file_id }}"}`

## 📝 로컬 개발

### 필수 요구사항

- Python 3.11 이상
- pip
- Docker (선택사항, Local Bot API Server 테스트용)

### 설치 및 실행

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
# .env 파일 생성 후 다음 내용 추가:
# TELEGRAM_BOT_TOKEN=your_bot_token_here
# LOCAL_API_URL=http://localhost:8081

# 애플리케이션 실행
python app.py
```

### Docker Compose로 전체 스택 실행

```bash
docker-compose up -d
```

이렇게 하면:
- Telegram Bot API Server (포트 8081)
- Python 프록시 서버 (포트 8000)

모두 실행됩니다.

## ⚠️ 주의사항

1. **비용**: Railway 무료 플랜은 제한이 있을 수 있습니다. 대용량 파일 처리를 위해서는 유료 플랜($5/월) 권장
2. **대역폭**: 대용량 파일 다운로드 시 대역폭 사용량이 증가합니다
3. **저장공간**: 다운로드한 파일을 임시 저장할 공간이 필요합니다
4. **타임아웃**: 큰 파일은 다운로드 시간이 오래 걸릴 수 있으므로 타임아웃 설정을 확인하세요

## 🧪 테스트

### cURL로 테스트

```bash
# Health check
curl https://your-railway-app.railway.app/health

# 파일 정보 조회
curl -X POST https://your-railway-app.railway.app/api/getFileInfo \
  -H "Content-Type: application/json" \
  -d '{"file_id": "YOUR_FILE_ID"}'

# 파일 다운로드
curl -X POST https://your-railway-app.railway.app/api/getFile \
  -H "Content-Type: application/json" \
  -d '{"file_id": "YOUR_FILE_ID"}' \
  --output downloaded_file.mp4
```

## 📚 참고 자료

- [Railway 문서](https://docs.railway.app/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Local Bot API Server](https://github.com/tdlib/telegram-bot-api)
- [Flask 문서](https://flask.palletsprojects.com/)
- [n8n 연동 가이드](./n8n-integration.md)

## 🆘 문제 해결

### 파일 다운로드 실패
- `TELEGRAM_BOT_TOKEN`이 올바르게 설정되었는지 확인
- 파일 크기가 2GB를 초과하지 않는지 확인
- Railway 로그 확인: Railway 대시보드 > Deployments > Logs

### Local API 연결 실패
- `LOCAL_API_URL` 환경 변수 확인
- Local Bot API Server가 실행 중인지 확인 (docker-compose 사용 시)

## 📄 라이선스

MIT License

