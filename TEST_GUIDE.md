# 🧪 배포 확인 및 테스트 가이드

## 1. Railway 대시보드에서 확인

### 배포 상태 확인
1. [Railway Dashboard](https://railway.app/dashboard) 접속
2. 프로젝트 클릭
3. **Deployments** 탭 확인:
   - ✅ **Active** 상태면 배포 완료
   - ⏳ **Building** 또는 **Deploying**이면 대기
   - ❌ **Failed**면 로그 확인 필요

### 로그 확인
1. 프로젝트 > **Deployments** > 최신 배포 클릭
2. **Logs** 탭에서 확인:
   - `telegram-bot-api` 서비스가 시작되었는지 확인
   - `api-proxy` 서비스가 시작되었는지 확인
   - 에러 메시지가 있는지 확인

### 서비스 URL 확인
1. 프로젝트 > **Settings** > **Domains**
2. 또는 **Deployments** > 최신 배포에서 URL 확인
   - 예: `https://your-app-name.up.railway.app`

## 2. Health Check 테스트

### 브라우저에서 확인
```
https://your-app.railway.app/health
```

**예상 응답:**
```json
{
  "status": "healthy",
  "service": "telegram-local-api-proxy"
}
```

### 터미널/CMD에서 확인 (Windows)
```powershell
# Health check
curl https://your-app.railway.app/health

# 또는 PowerShell
Invoke-WebRequest -Uri https://your-app.railway.app/health
```

### 메인 엔드포인트 확인
```
https://your-app.railway.app/
```

**예상 응답:**
```json
{
  "status": "ok",
  "message": "Telegram Local Bot API Proxy is running",
  "max_file_size": "2GB",
  "standard_api_limit": "20MB"
}
```

## 3. 파일 정보 조회 테스트

### 작은 파일 테스트 (20MB 이하)
```powershell
# PowerShell
$body = @{
    file_id = "YOUR_FILE_ID"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://your-app.railway.app/api/getFileInfo" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**예상 응답:**
```json
{
  "ok": true,
  "result": {
    "file_id": "...",
    "file_size": 1048576,
    "file_size_mb": 1.0,
    "file_path": "photos/file_123.jpg",
    "recommended_api": "standard"
  }
}
```

### 큰 파일 테스트 (20MB 초과)
```powershell
# 36MB 비디오 같은 경우
$body = @{
    file_id = "YOUR_LARGE_FILE_ID"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://your-app.railway.app/api/getFileInfo" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**예상 응답:**
```json
{
  "ok": true,
  "result": {
    "file_id": "...",
    "file_size": 38651904,
    "file_size_mb": 36.78,
    "file_path": "videos/file_123.mp4",
    "recommended_api": "local"
  }
}
```

## 4. 실제 파일 다운로드 테스트

### 작은 파일 다운로드 (20MB 이하)
```powershell
$body = @{
    file_id = "YOUR_SMALL_FILE_ID"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://your-app.railway.app/api/getFile" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body `
    -OutFile "downloaded_file.jpg"
```

### 큰 파일 다운로드 (20MB 초과) - 36MB 비디오
```powershell
$body = @{
    file_id = "YOUR_LARGE_FILE_ID"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://your-app.railway.app/api/getFile" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body `
    -OutFile "downloaded_video.mp4"
```

**주의:** 큰 파일은 다운로드 시간이 오래 걸릴 수 있습니다 (최대 5분).

## 5. n8n에서 테스트

### 워크플로우 설정

1. **HTTP Request 노드** 추가
2. 설정:
   - **Method**: POST
   - **URL**: `https://your-app.railway.app/api/getFileInfo`
   - **Body (JSON)**:
     ```json
     {
       "file_id": "={{ $json.message.video.file_id }}"
     }
     ```
3. 실행하여 파일 정보 확인

### 파일 다운로드 테스트

1. **HTTP Request 노드** 추가
2. 설정:
   - **Method**: POST
   - **URL**: `https://your-app.railway.app/api/getFile`
   - **Body (JSON)**:
     ```json
     {
       "file_id": "={{ $json.message.video.file_id }}"
     }
     ```
   - **Response Format**: File
3. 실행하여 파일 다운로드 확인

## 6. 문제 해결

### Health check 실패
- Railway 로그 확인
- 환경 변수 `TELEGRAM_BOT_TOKEN`이 설정되었는지 확인
- 포트가 올바르게 노출되었는지 확인

### 파일 다운로드 실패 (20MB 초과)
- Railway 로그에서 `telegram-bot-api` 서비스 확인
- `LOCAL_API_URL` 환경 변수 확인 (자동 설정됨)
- 로그에서 에러 메시지 확인:
  ```
  ERROR: Failed to download file from Local API
  ```

### 타임아웃 발생
- 큰 파일은 다운로드 시간이 오래 걸릴 수 있음
- Railway 타임아웃 설정 확인
- n8n HTTP Request 노드의 타임아웃 설정 확인

## 7. 성공 확인 체크리스트

- [ ] Health check 엔드포인트 응답 확인
- [ ] 메인 엔드포인트 응답 확인
- [ ] 파일 정보 조회 테스트 성공
- [ ] 작은 파일 (20MB 이하) 다운로드 성공
- [ ] 큰 파일 (20MB 초과) 다운로드 성공
- [ ] n8n 워크플로우에서 연동 테스트 성공

## 8. 로그 확인 명령어

### Railway 대시보드에서
1. 프로젝트 > **Deployments** > 최신 배포
2. **Logs** 탭에서 실시간 로그 확인

### 확인할 로그 메시지
- ✅ `telegram-bot-api` 서비스 시작 메시지
- ✅ `api-proxy` 서비스 시작 메시지
- ✅ `Running on http://0.0.0.0:8000` (프록시 서버)
- ✅ `Listening on port 8081` (Local Bot API Server)

## 9. 빠른 테스트 스크립트

### PowerShell 스크립트 (`test.ps1`)
```powershell
$BASE_URL = "https://your-app.railway.app"

Write-Host "1. Health Check..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/health"
    Write-Host "✅ Health Check: OK" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ Health Check Failed: $_" -ForegroundColor Red
}

Write-Host "`n2. Main Endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/"
    Write-Host "✅ Main Endpoint: OK" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ Main Endpoint Failed: $_" -ForegroundColor Red
}

Write-Host "`n3. File Info Test (작은 파일)..." -ForegroundColor Cyan
$body = @{
    file_id = "YOUR_FILE_ID"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/getFileInfo" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    Write-Host "✅ File Info: OK" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ File Info Failed: $_" -ForegroundColor Red
}
```

사용 방법:
```powershell
# 파일 ID를 실제 값으로 변경 후 실행
.\test.ps1
```

