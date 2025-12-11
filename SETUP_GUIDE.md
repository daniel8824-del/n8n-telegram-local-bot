# 🎯 20MB 초과 파일 다운로드 설정 가이드

## 목표
**20MB를 초과하는 파일을 다운로드할 수 있도록 설정**

## ✅ 완전한 솔루션 (권장)

### 하나의 서비스로 모든 기능 제공

`Dockerfile.complete`를 사용하면 Local Bot API Server와 프록시 서버가 함께 실행되어 **2GB까지 파일 다운로드가 가능**합니다.

### 배포 단계

#### 1. Railway 설정 파일 수정

`railway.json` 파일을 다음과 같이 수정:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.complete"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

또는 Railway 대시보드에서:
- Settings > Build > Dockerfile Path를 `Dockerfile.complete`로 변경

#### 2. GitHub에 코드 푸시

```bash
git add .
git commit -m "Add complete solution with Local Bot API Server"
git push
```

#### 3. Railway에서 프로젝트 생성

1. [Railway Dashboard](https://railway.app/dashboard) 접속
2. "New Project" 클릭
3. "Deploy from GitHub repo" 선택
4. 저장소 선택
5. "Deploy Now" 클릭

#### 4. 환경 변수 설정

Railway 대시보드 > 프로젝트 > Variables 탭에서 설정:

**필수:**
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

**선택사항 (Local Bot API Server 최적화용):**
```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```

**자동 설정됨:**
```
LOCAL_API_URL=http://localhost:8081
PORT=8000
```

#### 5. 배포 확인

배포가 완료되면:
1. Railway 대시보드에서 URL 확인 (예: `https://your-app.railway.app`)
2. Health check 테스트:
   ```bash
   curl https://your-app.railway.app/health
   ```

#### 6. 테스트

**20MB 이하 파일:**
```bash
curl -X POST https://your-app.railway.app/api/getFileInfo \
  -H "Content-Type: application/json" \
  -d '{"file_id": "YOUR_SMALL_FILE_ID"}'
```

**20MB 초과 파일 (36MB 비디오 등):**
```bash
curl -X POST https://your-app.railway.app/api/getFile \
  -H "Content-Type: application/json" \
  -d '{"file_id": "YOUR_LARGE_FILE_ID"}' \
  --output downloaded_video.mp4
```

## 🔧 n8n 연동

### 워크플로우 설정

1. **Telegram Trigger** 노드
   - 봇으로 전송된 메시지 수신

2. **Function** 노드 (파일 크기 확인)
   ```javascript
   const fileSize = $input.item.json.message.video?.file_size 
     || $input.item.json.message.document?.file_size
     || 0;
   
   return {
     json: {
       file_id: $input.item.json.message.video?.file_id 
         || $input.item.json.message.document?.file_id,
       file_size: fileSize,
       file_size_mb: (fileSize / 1024 / 1024).toFixed(2),
       use_local_api: fileSize > 20971520 // 20MB 초과
     }
   };
   ```

3. **HTTP Request** 노드 (파일 다운로드)
   - **Method**: POST
   - **URL**: `https://your-app.railway.app/api/getFile`
   - **Body (JSON)**:
     ```json
     {
       "file_id": "={{ $json.file_id }}"
     }
     ```
   - **Response Format**: File

4. **Supabase** 노드 (파일 업로드)
   - 다운로드한 파일을 Supabase에 저장

5. **Airtable** 노드 (메타데이터 저장)
   - 파일 정보를 Airtable에 저장

## 📊 작동 방식

### 파일 크기별 처리

| 파일 크기 | 처리 방법 | API 사용 |
|---------|---------|---------|
| ≤20MB | 즉시 다운로드 | Standard Bot API |
| 20MB ~ 2GB | 다운로드 가능 | Local Bot API Server |
| >2GB | file_id만 저장 | - |

### 내부 구조

```
Railway Container
├── Telegram Bot API Server (포트 8081)
│   └── 2GB까지 파일 다운로드 지원
└── Python 프록시 서버 (포트 8000)
    └── n8n 연동 및 파일 크기별 분기 처리
```

## ⚠️ 주의사항

1. **비용**: Railway Hobby Plan ($5/월) 권장
2. **대역폭**: 대용량 파일 다운로드 시 대역폭 사용량 증가
3. **타임아웃**: 큰 파일은 다운로드 시간이 오래 걸릴 수 있음 (최대 5분)
4. **메모리**: 파일은 메모리에 임시 저장되므로 큰 파일 처리 시 메모리 사용량 증가

## 🐛 문제 해결

### Local Bot API Server가 시작되지 않음
- Railway 로그 확인: Deployments > Logs
- `TELEGRAM_API_ID`와 `TELEGRAM_API_HASH`가 설정되었는지 확인 (선택사항이지만 권장)

### 파일 다운로드 실패
- Bot Token이 올바른지 확인
- 파일 크기가 2GB를 초과하지 않는지 확인
- Railway 로그에서 에러 메시지 확인

### 타임아웃 발생
- 큰 파일의 경우 타임아웃 시간을 늘려야 할 수 있음
- n8n의 HTTP Request 노드에서 타임아웃 설정 확인

## 📚 추가 리소스

- [Railway 문서](https://docs.railway.app/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Local Bot API Server](https://github.com/tdlib/telegram-bot-api)
- [n8n 연동 가이드](./n8n-integration.md)

