# 🔌 Railway 포트 설정 가이드

## 포트 설정 방법

### Railway Public Networking 설정

1. **Railway 대시보드** > 프로젝트 > **Settings** > **Networking**
2. **Public Networking** 섹션에서:
   - **Generate Service Domain** 클릭
   - **Target port**: `8080` 입력 (또는 Railway가 자동으로 설정한 PORT 값)
   - **Save** 클릭

### 포트 설명

- **8080**: Railway가 기본적으로 사용하는 포트 (프록시 서버)
- **8081**: Local Bot API Server 내부 포트 (외부 노출 불필요)

## 자동 포트 설정

Railway는 자동으로 `PORT` 환경 변수를 설정합니다:
- 기본값: `8080`
- `app.py`가 이 환경 변수를 자동으로 읽어서 사용합니다

## 확인 방법

### 1. Railway 대시보드에서
- **Settings** > **Variables**에서 `PORT` 환경 변수 확인
- 보통 `8080`으로 자동 설정됨

### 2. 배포 후 테스트
```powershell
# Railway가 제공한 도메인으로 접속
Invoke-RestMethod -Uri "https://your-app.railway.app/health"
```

## 중요 사항

✅ **Target port를 `8080`으로 설정하세요**
- Railway가 자동으로 설정하는 PORT 환경 변수와 일치해야 합니다
- `app.py`가 이 값을 자동으로 읽어서 사용합니다

❌ **8000을 사용하지 마세요**
- Railway는 기본적으로 8080을 사용합니다
- 8000을 사용하면 연결이 안 될 수 있습니다

## 문제 해결

### 포트가 맞지 않으면
1. Railway 대시보드 > **Settings** > **Variables** 확인
2. `PORT` 환경 변수가 설정되어 있는지 확인
3. Public Networking의 Target port가 `PORT` 환경 변수와 일치하는지 확인

### 연결이 안 되면
1. Railway 로그 확인
2. `Running on http://0.0.0.0:XXXX` 메시지에서 실제 포트 확인
3. Public Networking의 Target port를 실제 포트와 일치시키기

