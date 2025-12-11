# 🚀 빠른 시작 가이드

## ✅ 완전한 솔루션 (20MB 초과 파일 다운로드 가능)

**이제 하나의 Dockerfile로 모든 것이 작동합니다!**

`Dockerfile.complete`를 사용하면 Local Bot API Server와 프록시 서버가 함께 실행되어 **2GB까지 파일 다운로드가 가능**합니다.

## ⚠️ 중요: 현재 상태

기본 `Dockerfile`은 **프록시 서버만** 포함되어 있습니다. 

### ✅ 지금 바로 작동하는 것:
- **20MB 이하 파일**: Standard Bot API로 다운로드 가능 ✅
- **Health check**: 서버 상태 확인 가능 ✅
- **파일 정보 조회**: 파일 크기 확인 가능 ✅

### ❌ 지금 작동하지 않는 것:
- **20MB 초과 파일**: Local Bot API Server가 없어서 다운로드 불가 ❌

## 🎯 배포 방법 선택

### ⭐ 방법 1: 완전한 솔루션 배포 (권장 - 2GB까지 지원)

**`Dockerfile.complete` 사용 - Local Bot API Server + 프록시 서버 함께 실행**

**장점:**
- ✅ **2GB까지 파일 다운로드 가능**
- ✅ 하나의 서비스로 모든 기능 제공
- ✅ 설정이 간단함

**배포 단계:**
1. `railway.json` 파일 수정:
   ```json
   {
     "build": {
       "dockerfilePath": "Dockerfile.complete"
     }
   }
   ```
   또는 Railway 대시보드에서 Dockerfile 경로를 `Dockerfile.complete`로 설정

2. GitHub에 코드 푸시
3. Railway에서 저장소 연결
4. 환경 변수 설정:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_API_ID=your_api_id (선택사항, Local API Server용)
   TELEGRAM_API_HASH=your_api_hash (선택사항, Local API Server용)
   LOCAL_API_URL=http://localhost:8081 (자동 설정됨)
   ```
5. 배포 완료!

**결과:**
- ✅ 20MB 이하 파일: Standard API로 다운로드
- ✅ 20MB 초과 파일: Local API로 다운로드 (2GB까지)

### 방법 2: 프록시 서버만 배포 (20MB 이하만)

**장점:**
- ✅ 빠르게 배포 가능 (5분)
- ✅ 무료로 시작 가능
- ✅ 20MB 이하 파일은 즉시 작동

**단점:**
- ❌ 20MB 초과 파일은 file_id만 저장해야 함

**배포 단계:**
1. GitHub에 코드 푸시
2. Railway에서 저장소 연결
3. `TELEGRAM_BOT_TOKEN` 환경 변수 설정
4. 배포 완료!

**n8n에서 사용:**
```javascript
// 파일 크기 확인
const fileSize = $input.item.json.message.video?.file_size || 0;

if (fileSize <= 20971520) {  // 20MB
  // Standard API 사용
  return { json: { use_local_api: false } };
} else {
  // file_id만 저장
  return { json: { use_local_api: false, save_file_id_only: true } };
}
```

### 방법 2: Local Bot API Server 추가 배포 (완전한 솔루션, 2GB까지)

**장점:**
- ✅ 2GB까지 파일 다운로드 가능
- ✅ 완전한 솔루션

**단점:**
- ⚠️ 두 개의 Railway 서비스 필요
- ⚠️ 비용 증가 ($10/월 정도)

**배포 단계:**

#### 2-1. Local Bot API Server 배포

1. Railway에서 새 서비스 생성
2. `Dockerfile.local-api` 사용
3. 환경 변수 설정:
   ```
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   ```
4. 서비스 URL 확인 (예: `https://telegram-api-server.railway.app`)

#### 2-2. 프록시 서버 배포

1. Railway에서 새 서비스 생성 (또는 기존 프로젝트에 추가)
2. 현재 `Dockerfile` 사용
3. 환경 변수 설정:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   LOCAL_API_URL=https://telegram-api-server.railway.app
   ```
4. 배포 완료!

**n8n에서 사용:**
```javascript
// 파일 크기 확인
const fileSize = $input.item.json.message.video?.file_size || 0;

if (fileSize <= 20971520) {  // 20MB
  return [0]; // Standard API
} else if (fileSize <= 2147483648) {  // 2GB
  return [1]; // Local API
} else {
  return [2]; // file_id만 저장
}
```

## 📋 체크리스트

### 방법 1 선택 시:
- [ ] GitHub에 코드 푸시
- [ ] Railway 계정 생성
- [ ] Railway에서 저장소 연결
- [ ] `TELEGRAM_BOT_TOKEN` 환경 변수 설정
- [ ] 배포 확인
- [ ] `/health` 엔드포인트 테스트

### 방법 2 선택 시:
- [ ] Telegram API Credentials 발급 (my.telegram.org)
- [ ] Local Bot API Server Railway 서비스 생성
- [ ] `Dockerfile.local-api` 사용하여 배포
- [ ] 프록시 서버 Railway 서비스 생성
- [ ] `LOCAL_API_URL` 환경 변수 설정
- [ ] 두 서비스 모두 배포 확인
- [ ] 테스트 파일로 다운로드 확인

## 🧪 배포 후 테스트

### 1. Health Check
```bash
curl https://your-proxy-app.railway.app/health
```

### 2. 파일 정보 조회 (20MB 이하)
```bash
curl -X POST https://your-proxy-app.railway.app/api/getFileInfo \
  -H "Content-Type: application/json" \
  -d '{"file_id": "YOUR_SMALL_FILE_ID"}'
```

### 3. 파일 다운로드 (20MB 이하)
```bash
curl -X POST https://your-proxy-app.railway.app/api/getFile \
  -H "Content-Type: application/json" \
  -d '{"file_id": "YOUR_SMALL_FILE_ID"}' \
  --output test_file.mp4
```

### 4. 파일 다운로드 (20MB 초과) - 방법 2만 가능
```bash
curl -X POST https://your-proxy-app.railway.app/api/getFile \
  -H "Content-Type: application/json" \
  -d '{"file_id": "YOUR_LARGE_FILE_ID"}' \
  --output large_file.mp4
```

## 💡 추천

**지금 당장 시작하려면:** 방법 1 (프록시 서버만)
- 빠르게 배포 가능
- 20MB 이하 파일은 즉시 작동
- 나중에 Local Bot API Server 추가 가능

**완전한 솔루션이 필요하면:** 방법 2 (Local Bot API Server 포함)
- 2GB까지 파일 다운로드 가능
- 완전한 기능 제공

## ❓ 질문

**Q: 방법 1로 시작하고 나중에 방법 2로 업그레이드할 수 있나요?**
A: 네! 프록시 서버는 그대로 두고, Local Bot API Server만 추가하면 됩니다.

**Q: 비용이 얼마나 드나요?**
A: 
- 방법 1: $5/월 (Railway Hobby Plan)
- 방법 2: $10/월 (두 서비스)

**Q: 36MB 비디오를 다운로드하려면?**
A: 방법 2가 필요합니다. 방법 1로는 file_id만 저장할 수 있습니다.

