import requests
import json
from get_token import get_token

# 주식월봉차트조회요청
def fn_ka10083(token, data, cont_yn='N', next_key=''):
	# 1. 요청할 API URL
	host = 'https://mockapi.kiwoom.com' # 모의투자
	#host = 'https://api.kiwoom.com' # 실전투자
	endpoint = '/api/dostk/chart'
	url =  host + endpoint

	# 2. header 데이터
	headers = {
		'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
		'authorization': f'Bearer {token}', # 접근토큰
		'cont-yn': cont_yn, # 연속조회여부
		'next-key': next_key, # 연속조회키
		'api-id': 'ka10083', # TR명
	}

	# 3. http POST 요청
	response = requests.post(url, headers=headers, json=data)
	return response

# 실행 구간
if __name__ == '__main__':
	# 1. 토큰 설정
	MY_ACCESS_TOKEN = get_token # 접근토큰

	# 2. 요청 데이터
	params = {
		'stk_cd': '005930', # 종목코드 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL)
		'base_dt': '20241108', # 기준일자 YYYYMMDD
		'upd_stkpc_tp': '1', # 수정주가구분 0 or 1
	}

	# 3. API 실행
	fn_ka10083(token=MY_ACCESS_TOKEN, data=params)

	# next-key, cont-yn 값이 있을 경우
	# fn_ka10083(token=MY_ACCESS_TOKEN, data=params, cont_yn='Y', next_key='nextkey..')