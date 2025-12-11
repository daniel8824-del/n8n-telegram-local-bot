# Railway 배포 상세 가이드

## 🎯 목표
20MB 이상의 텔레그램 파일을 다운로드하기 위한 Local Bot API Server를 Railway에 배포

## 📋 사전 준비

### 1. Telegram API Credentials 발급

1. [my.telegram.org](https://my.telegram.org/)에 접속
2. 로그인 후 "API development tools" 클릭
3. 애플리케이션 생성
4. 다음 정보를 받습니다:
   - `api_id`: 숫자
   - `api_hash`: 문자열

### 2. Telegram Bot Token 발급

1. [@BotFather](https://t.me/botfather)와 대화
2. `/newbot` 명령어 실행
3. 봇 이름과 username 설정
4. 받은 토큰을 저장합니다 (예: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## 🚀 Railway 배포 단계

### 방법 1: GitHub를 통한 배포 (권장)

#### 1단계: GitHub 저장소 생성

```bash
# 현재 디렉토리에서
git init
git add .
git commit -m "Initial commit: Telegram Local Bot API Server"
git branch -M main
git remote add origin https://github.com/your-username/telegram-local-api.git
git push -u origin main
```

#### 2단계: Railway에 프로젝트 연결

1. [Railway Dashboard](https://railway.app/dashboard) 접속
2. "New Project" 클릭
3. "Deploy from GitHub repo" 선택
4. GitHub 저장소 선택
5. "Deploy Now" 클릭

#### 3단계: 환경 변수 설정

Railway 대시보드에서 프로젝트 선택 > "Variables" 탭:

**필수 변수:**
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

**선택 변수 (Local Bot API Server 사용 시):**
```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
LOCAL_API_URL=http://localhost:8081
```

#### 4단계: 도메인 확인

배포 완료 후:
1. "Settings" > "Domains"에서 URL 확인
2. 예: `https://telegram-api-production.up.railway.app`

### 방법 2: Railway CLI를 통한 배포

```bash
# Railway CLI 설치
npm i -g @railway/cli

# 로그인
railway login

# 프로젝트 초기화
railway init

# 환경 변수 설정
railway variables set TELEGRAM_BOT_TOKEN=your_token_here
railway variables set TELEGRAM_API_ID=your_api_id
railway variables set TELEGRAM_API_HASH=your_api_hash

# 배포
railway up
```

## 🔧 Local Bot API Server 설정 (선택사항)

현재 구현은 프록시 서버입니다. 실제 2GB 파일 다운로드를 위해서는 공식 Local Bot API Server가 필요합니다.

### 옵션 1: 별도 Railway 서비스로 실행

`docker-compose.yml`의 `telegram-bot-api` 서비스를 별도 Railway 서비스로 배포:

1. 새 Railway 서비스 생성
2. Docker 이미지 사용: `aiogram/telegram-bot-api:latest`
3. 환경 변수 설정:
   - `TELEGRAM_API_ID`
   - `TELEGRAM_API_HASH`
4. 내부 네트워크 URL을 `LOCAL_API_URL`로 설정

### 옵션 2: 현재 프록시 서버만 사용

현재 프록시 서버는:
- ✅ 20MB 이하 파일: Standard Bot API 사용
- ⚠️ 20MB 초과 파일: Local Bot API Server 필요 (에러 반환)

**임시 해결책:**
- 20MB 초과 파일은 `file_id`만 저장
- 나중에 사용자가 요청 시 `sendDocument`로 재전송

## 🧪 배포 후 테스트

### 1. Health Check

```bash
curl https://your-app.railway.app/health
```

예상 응답:
```json
{
  "status": "healthy",
  "service": "telegram-local-api-proxy"
}
```

### 2. 파일 정보 조회 테스트

```bash
curl -X POST https://your-app.railway.app/api/getFileInfo \
  -H "Content-Type: application/json" \
  -d '{"file_id": "YOUR_FILE_ID"}'
```

### 3. 파일 다운로드 테스트

```bash
curl -X POST https://your-app.railway.app/api/getFile \
  -H "Content-Type: application/json" \
  -d '{"file_id": "YOUR_FILE_ID"}' \
  --output test_file.mp4
```

## 🔗 n8n 연동

배포된 API URL을 n8n 워크플로우에 추가:

1. HTTP Request 노드 추가
2. URL: `https://your-app.railway.app/api/getFile`
3. Method: POST
4. Body: `{"file_id": "{{ $json.message.video.file_id }}"}`

자세한 내용은 [`n8n-integration.md`](./n8n-integration.md) 참고

## 💰 비용 예상

### Railway 요금제

- **Hobby Plan**: $5/월
  - $5 크레딧 포함
  - 추가 사용량: $0.000463/GB-hour
  - 대용량 파일 처리에 충분

- **Pro Plan**: $20/월
  - 더 많은 리소스
  - 더 높은 대역폭

### 예상 비용 (36MB 비디오 처리 기준)

- 월 1000개 파일 처리 시: 약 $5-10
- 월 10000개 파일 처리 시: 약 $20-30

## ⚠️ 주의사항

1. **대역폭 제한**: Railway는 대역폭 제한이 있을 수 있습니다
2. **타임아웃**: 큰 파일은 다운로드 시간이 오래 걸릴 수 있습니다 (최대 5분)
3. **저장공간**: 다운로드한 파일은 메모리에 임시 저장됩니다
4. **보안**: Bot Token을 안전하게 관리하세요

## 🐛 문제 해결

### 배포 실패
- Railway 로그 확인: Deployments > Logs
- 환경 변수가 올바르게 설정되었는지 확인
- `requirements.txt`의 패키지 버전 확인

### API 호출 실패
- Bot Token이 올바른지 확인
- Railway URL이 올바른지 확인
- CORS 문제가 있는지 확인 (필요 시 CORS 설정 추가)

### 파일 다운로드 실패
- 파일 크기가 2GB를 초과하지 않는지 확인
- Local Bot API Server가 실행 중인지 확인 (20MB 초과 파일의 경우)
- Railway 로그에서 에러 메시지 확인

## 📚 추가 리소스

- [Railway 문서](https://docs.railway.app/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Local Bot API Server](https://github.com/tdlib/telegram-bot-api)

