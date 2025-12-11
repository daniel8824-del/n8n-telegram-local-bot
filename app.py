import os
import requests
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
import io

load_dotenv()

app = Flask(__name__)

# 환경 변수에서 포트 가져오기 (Railway가 자동으로 설정)
PORT = int(os.environ.get('PORT', 8000))

# Telegram Bot API 설정
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
# Local Bot API Server URL 
# 같은 컨테이너에서 실행 시: http://localhost:8081 (Dockerfile.complete 사용 시)
# Railway에서 별도 서비스로 배포한 경우: https://your-local-api-service.railway.app
# docker-compose 사용 시: http://telegram-bot-api:8081
LOCAL_API_URL = os.environ.get('LOCAL_API_URL', 'http://localhost:8081')
# 표준 Bot API (fallback)
STANDARD_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}' if BOT_TOKEN else ''

# 파일 크기 제한 (바이트)
MAX_STANDARD_SIZE = 20 * 1024 * 1024  # 20MB
MAX_LOCAL_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Telegram Local Bot API Proxy is running',
        'max_file_size': '2GB',
        'standard_api_limit': '20MB'
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check for Railway"""
    return jsonify({
        'status': 'healthy',
        'service': 'telegram-local-api-proxy'
    }), 200

@app.route('/api/getFile', methods=['POST', 'GET'])
def get_file():
    """
    Telegram getFile API 프록시
    파일 크기에 따라 자동으로 Local API 또는 Standard API 사용
    """
    try:
        # 요청 데이터 가져오기
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
        
        file_id = data.get('file_id')
        if not file_id:
            return jsonify({'error': 'file_id is required'}), 400
        
        # 먼저 파일 정보 조회 (표준 API 사용)
        file_info_url = f'{STANDARD_API_URL}/getFile'
        file_info_response = requests.post(file_info_url, json={'file_id': file_id})
        
        if file_info_response.status_code != 200:
            return jsonify({
                'error': 'Failed to get file info',
                'details': file_info_response.json()
            }), file_info_response.status_code
        
        file_info = file_info_response.json()
        if not file_info.get('ok'):
            return jsonify(file_info), 400
        
        file_path = file_info['result'].get('file_path')
        file_size = file_info['result'].get('file_size', 0)
        
        # 파일 크기에 따라 분기 처리
        if file_size > MAX_STANDARD_SIZE:
            # 20MB 초과: Local Bot API 사용
            if file_size > MAX_LOCAL_SIZE:
                return jsonify({
                    'ok': False,
                    'error': 'File too large',
                    'file_size': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'max_size': MAX_LOCAL_SIZE,
                    'max_size_mb': round(MAX_LOCAL_SIZE / (1024 * 1024), 2),
                    'message': 'Files larger than 2GB are not supported. Please save file_id only.'
                }), 413
            
            # Local Bot API로 getFile 호출해서 로컬 파일 경로 얻기
            try:
                local_getfile_url = f'{LOCAL_API_URL}/bot{BOT_TOKEN}/getFile'
                local_response = requests.post(local_getfile_url, json={'file_id': file_id}, timeout=60)
                
                if local_response.status_code != 200:
                    return jsonify({
                        'ok': False,
                        'error': 'Failed to get file from Local API',
                        'status_code': local_response.status_code,
                        'message': 'Local Bot API Server may not be running.',
                        'file_size_mb': round(file_size / (1024 * 1024), 2)
                    }), local_response.status_code
                
                local_file_info = local_response.json()
                if not local_file_info.get('ok'):
                    return jsonify(local_file_info), 400
                
                local_file_path = local_file_info['result'].get('file_path', '')
                
                # 로컬 파일 시스템에서 직접 읽기
                # file_path가 절대 경로일 수 있음 (--local 모드)
                if local_file_path.startswith('/'):
                    actual_path = local_file_path
                else:
                    actual_path = f'/var/lib/telegram-bot-api/{local_file_path}'
                
                if os.path.exists(actual_path):
                    return send_file(
                        actual_path,
                        mimetype='application/octet-stream',
                        as_attachment=True,
                        download_name=local_file_path.split('/')[-1] if '/' in local_file_path else 'file'
                    )
                else:
                    return jsonify({
                        'ok': False,
                        'error': 'File not found on local filesystem',
                        'file_path': local_file_path,
                        'actual_path': actual_path,
                        'file_size_mb': round(file_size / (1024 * 1024), 2)
                    }), 404
                    
            except requests.exceptions.RequestException as e:
                return jsonify({
                    'ok': False,
                    'error': 'Local API connection failed',
                    'message': str(e),
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'recommendation': 'Check if Local Bot API Server is running at ' + LOCAL_API_URL
                }), 503
        else:
            # 20MB 이하: 표준 Bot API 사용
            try:
                standard_file_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}'
                file_response = requests.get(standard_file_url, stream=True, timeout=60)
                
                if file_response.status_code != 200:
                    return jsonify({
                        'ok': False,
                        'error': 'Failed to download file from Standard API',
                        'status_code': file_response.status_code,
                        'details': file_response.text
                    }), file_response.status_code
                
                return send_file(
                    io.BytesIO(file_response.content),
                    mimetype='application/octet-stream',
                    as_attachment=True,
                    download_name=file_path.split('/')[-1] if '/' in file_path else 'file'
                )
            except requests.exceptions.RequestException as e:
                return jsonify({
                    'ok': False,
                    'error': 'Standard API connection failed',
                    'message': str(e)
                }), 503
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500

@app.route('/api/getFileInfo', methods=['POST', 'GET'])
def get_file_info():
    """
    파일 정보만 조회 (다운로드 없이)
    n8n에서 파일 크기 확인용
    """
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
        
        file_id = data.get('file_id')
        if not file_id:
            return jsonify({'error': 'file_id is required'}), 400
        
        file_info_url = f'{STANDARD_API_URL}/getFile'
        response = requests.post(file_info_url, json={'file_id': file_id})
        
        if response.status_code != 200:
            return jsonify(response.json()), response.status_code
        
        file_info = response.json()
        if file_info.get('ok'):
            file_size = file_info['result'].get('file_size', 0)
            file_info['result']['recommended_api'] = 'local' if file_size > MAX_STANDARD_SIZE else 'standard'
            file_info['result']['file_size_mb'] = round(file_size / (1024 * 1024), 2)
        
        return jsonify(file_info), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for Telegram updates"""
    try:
        data = request.get_json()
        # 여기에 텔레그램 웹훅 처리 로직 추가
        return jsonify({'status': 'received'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proxy/<path:method>', methods=['POST', 'GET'])
def proxy_api(method):
    """
    Telegram Bot API 프록시
    모든 Bot API 메서드를 프록시하여 Local API 사용 가능
    """
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
        
        # Local Bot API 사용 (2GB 지원)
        local_api_url = f'{LOCAL_API_URL}/bot{BOT_TOKEN}/{method}'
        response = requests.post(local_api_url, json=data)
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500

if __name__ == '__main__':
    if not BOT_TOKEN:
        print("⚠️  WARNING: TELEGRAM_BOT_TOKEN not set!")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)

