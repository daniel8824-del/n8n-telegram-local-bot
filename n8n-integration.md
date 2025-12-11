# n8n 연동 가이드

## 🎯 목적
20MB 이상의 텔레그램 파일을 다운로드하기 위한 Local Bot API Server 연동

## 📋 n8n 워크플로우 설정

### 1. 파일 크기 확인 및 분기 처리

#### Switch 노드 설정
```javascript
// 파일 크기 확인
const fileSize = $('Telegram Trigger').item.json.message.video?.file_size 
  || $('Telegram Trigger').item.json.message.document?.file_size
  || $('Telegram Trigger').item.json.message.photo?.[0]?.file_size
  || 0;

// 분기 처리
if (fileSize <= 20971520) {  // 20MB
  return [0];  // Standard Bot API 사용
} else if (fileSize <= 2147483648) {  // 2GB
  return [1];  // Local Bot API (Railway) 사용
} else {
  return [2];  // file_id만 저장
}
```

### 2. Local Bot API로 파일 다운로드

#### HTTP Request 노드 설정 (20MB 초과 파일용)

**Method**: POST  
**URL**: `https://your-railway-app.railway.app/api/getFile`  
**Body (JSON)**:
```json
{
  "file_id": "={{ $('Telegram Trigger').item.json.message.video.file_id }}"
}
```

**Response Format**: File

### 3. 파일 정보만 조회 (다운로드 없이)

#### HTTP Request 노드 설정

**Method**: POST  
**URL**: `https://your-railway-app.railway.app/api/getFileInfo`  
**Body (JSON)**:
```json
{
  "file_id": "={{ $('Telegram Trigger').item.json.message.video.file_id }}"
}
```

**Response**:
```json
{
  "ok": true,
  "result": {
    "file_id": "...",
    "file_unique_id": "...",
    "file_size": 38651904,
    "file_size_mb": 36.78,
    "file_path": "videos/file_123.mp4",
    "recommended_api": "local"
  }
}
```

### 4. 완전한 워크플로우 예시

```
Telegram Trigger
  ↓
Switch (파일 크기 분기)
  ├─ [0] ≤20MB → Standard Bot API → Supabase 업로드
  ├─ [1] >20MB → Local Bot API → Supabase 업로드
  └─ [2] >2GB → file_id만 Airtable 저장
```

### 5. 코드 예시 (Function 노드)

#### 파일 크기별 처리
```javascript
const fileSize = $input.item.json.message.video?.file_size || 0;
const fileId = $input.item.json.message.video?.file_id;

if (fileSize > 2147483648) {  // 2GB 초과
  // file_id만 저장
  return {
    json: {
      action: 'save_file_id',
      file_id: fileId,
      file_size: fileSize,
      file_size_mb: (fileSize / 1024 / 1024).toFixed(2),
      status: 'file_id_only'
    }
  };
} else if (fileSize > 20971520) {  // 20MB 초과
  // Local Bot API 사용
  return {
    json: {
      action: 'download_via_local_api',
      file_id: fileId,
      api_url: 'https://your-railway-app.railway.app/api/getFile',
      file_size: fileSize
    }
  };
} else {
  // Standard Bot API 사용
  return {
    json: {
      action: 'download_via_standard_api',
      file_id: fileId,
      file_size: fileSize
    }
  };
}
```

## 🔧 환경 변수 설정

Railway 대시보드에서 다음 환경 변수를 설정:

- `TELEGRAM_BOT_TOKEN`: 봇 토큰
- `TELEGRAM_API_ID`: API ID (Local Bot API Server용)
- `TELEGRAM_API_HASH`: API Hash (Local Bot API Server용)
- `LOCAL_API_URL`: Local Bot API Server URL (기본값: http://localhost:8081)

## 📝 API 엔드포인트

### GET `/health`
서버 상태 확인

### POST `/api/getFile`
파일 다운로드 (자동으로 Local/Standard API 선택)

### POST `/api/getFileInfo`
파일 정보 조회 (다운로드 없이)

### POST `/api/proxy/<method>`
모든 Telegram Bot API 메서드 프록시

## ⚠️ 주의사항

1. **비용**: Railway 유료 플랜 필요할 수 있음 ($5/월)
2. **대역폭**: 대용량 파일 다운로드 시 대역폭 사용량 증가
3. **저장공간**: 다운로드한 파일을 임시 저장할 공간 필요
4. **타임아웃**: 큰 파일은 다운로드 시간이 오래 걸릴 수 있음

## 🚀 테스트

### cURL로 테스트
```bash
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

