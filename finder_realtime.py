# finder_realtime.py (ver 2.2 - 정교한 속도 제어)

import FinanceDataReader as fdr
import pandas as pd
import json
from datetime import datetime
from get_token import get_token
from fn_ka10083 import fn_ka10083 # 키움 월봉 조회 API 함수
import time

def find_realtime_watchlist_kiwoom_final():
    """
    (ver 2.2)
    - 키움 API의 '초당 5건' 제한을 준수하는 정교한 속도 제어 로직 추가
    """
    print("="*50)
    print("실시간 감시 대상 탐색기 (Finder-Realtime v2.2)를 시작합니다.")

    try:
        # 1. 백테스팅 결과가 담긴 '전체' 관심종목 리스트를 불러온다.
        with open('watchlist_base.json', 'r', encoding='utf-8') as f:
            strategy_fit_stocks = json.load(f)
        print(f" -> 총 {len(strategy_fit_stocks)}개의 전략 적합 종목을 대상으로 분석합니다.")

    except FileNotFoundError:
        print("오류: 'watchlist_base.json' 파일을 찾을 수 없습니다.")
        print("먼저 finder_backtest.py를 실행하여 기본 관심종목 파일을 생성해주세요.")
        return

    today_watchlist = []
    my_token = get_token()
    if not my_token: return

    requests_per_second = 5
    request_count = 0
    last_request_time = time.time()

    for i, stock_info in enumerate(strategy_fit_stocks):
        # 50개 단위 휴식
        if i > 0 and i % 50 == 0:
            print(f"\n--- {i}개 종목 처리 완료. 60초간 휴식합니다... ---\n")
            time.sleep(60)

        # 초당 5회 제한
        current_time = time.time()
        if current_time - last_request_time >= 1.0:
            last_request_time = current_time
            request_count = 0
        if request_count >= requests_per_second:
            time_to_wait = 1.0 - (current_time - last_request_time)
            if time_to_wait > 0:
                time.sleep(time_to_wait)
            last_request_time = time.time()
            request_count = 0

        ticker = stock_info["종목코드"]
        stock_name = stock_info["종목명"]
        ma_period = stock_info["기준_이평선"]

        try:
            request_count += 1
            print(f"[{i+1}/{len(strategy_fit_stocks)}] {stock_name} 조회... (요청 {request_count}/5)")
            params = { 'stk_cd': ticker, 'chart_type_gb': 'M', 'base_dt': datetime.now().strftime('%Y%m%d'), 'upd_stkpc_tp': '1' }
            response = fn_ka10083(token=my_token, data=params)

            # 429 에러 핸들링
            if response.status_code == 429:
                print(f"  -> [API 요청 제한] 60초간 대기 후, 토큰을 갱신하고 재시도합니다.")
                time.sleep(60)
                my_token = get_token()
                response = fn_ka10083(token=my_token, data=params)

            if response.status_code != 200:
                print(f"  -> [API 에러] {stock_name}({ticker}) - 상태 코드: {response.status_code}. 60초간 대기합니다.")
                print(f"     메시지: {response.text}")
                time.sleep(60)
                continue

            response_json = response.json()
            if 'stk_mth_pole_chart_qry' in response_json:
                df_monthly = pd.DataFrame(response_json['stk_mth_pole_chart_qry'])
                df_monthly['Close'] = pd.to_numeric(df_monthly['cur_prc'])
                df_monthly = df_monthly.iloc[::-1].reset_index(drop=True)
                df_monthly['MA'] = df_monthly['Close'].ewm(span=ma_period, adjust=False).mean()
                df_monthly.dropna(inplace=True)
                if df_monthly.empty: continue
                latest_close = df_monthly['Close'].iloc[-1]
                latest_ma = df_monthly['MA'].iloc[-1]
                if latest_close < latest_ma:
                    print(f"  -> [감시 대상 포착!] {stock_name}({ticker}) | 현재가: {latest_close:,.0f} < {ma_period}개월 이평: {latest_ma:,.2f}")
                    today_watchlist.append(stock_info)
        except Exception as e:
            print(f"  -> [에러 발생] {stock_name}({ticker}) 처리 중 오류: {e}")
            continue

    print("\n3. 분석 완료!")
    print("="*50)

    # 5. '오늘의' 최종 감시 목록을 'jtoday.json'으로 저장
    with open('watchlist_today.json', 'w', encoding='utf-8') as f:
        json.dump(today_watchlist, f, ensure_ascii=False, indent=4)
    print(f"\n총 {len(today_watchlist)}개의 금일 감시 대상 종목을 'watchlist_today.json' 파일로 저장했습니다.")
    print("="*50)

if __name__ == "__main__":
    find_realtime_watchlist_kiwoom_final()