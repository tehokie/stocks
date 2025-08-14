import requests
import json


def get_token(mode='mock'):
    """
    설정 파일(config.json)을 읽어와 키움 API 접근 토큰을 발급받는 함수
    :param mode: 'real' 또는 'mock'을 입력. 기본값은 'mock'(모의투자)
    :return: 발급받은 접근 토큰 문자열, 실패 시 None
    """
    # 1. 설정 파일(config.json) 읽기
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("오류: config.json 파일을 찾을 수 없습니다. 파일을 생성해주세요.")
        return None

    # 2. 거래 모드(실전/모의)에 따른 설정 선택
    if mode not in config:
        print(f"오류: config.json 파일에 '{mode}' 설정이 없습니다. 'real' 또는 'mock'을 확인해주세요.")
        return None
        
    settings = config[mode]
    url = f"{settings['host']}/oauth2/token"

    # 3. 요청 데이터 준비
    params = {
        "grant_type": "client_credentials",
        "appkey": settings['app_key'],
        "secretkey": settings['app_secret']
    }

    # 4. API 요청 보내기
    headers = {"content-type": "application/json"}
    try:
        res = requests.post(url, headers=headers, data=json.dumps(params))
        # 성공적으로 응답을 받았는지 확인 (상태 코드가 200이 아니면 오류)
        res.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")
        # 응답 내용이 있다면 출력
        if e.response is not None:
            print(f"응답 내용: {e.response.text}")
        return None

    # 5. 결과 처리 및 토큰 반환
    token_data = res.json()
    access_token = token_data.get('token')

    if access_token:
        print(f"[{mode.upper()}] 모드 토큰 발급 성공!")
        return access_token
    else:
        print(f"[{mode.upper()}] 모드 토큰 발급 실패. 응답: {token_data}")
        return None


# --- 이 파일을 직접 실행했을 때만 아래 코드가 동작 ---
if __name__ == '__main__':
    # 모의투자 토큰 발급 테스트
    mock_token = get_token(mode='mock')
    if mock_token:
        print(f"모의투자 토큰: {mock_token[:15]}...") # 토큰이 너무 길어서 일부만 출력
        # 이 토큰을 다른 API 요청에 사용하면 됩니다.
        # 예: fn_ka10001(token=mock_token, data=...)

    print("-" * 30)

    # # 실전투자 토큰 발급 테스트 (필요시 주석 해제)
    # real_token = get_token(mode='real')
    # if real_token:
    #     print(f"실전투자 토큰: {real_token[:15]}...")