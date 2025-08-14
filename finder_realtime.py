import FinanceDataReader as fdr
import pandas as pd
import json
from datetime import datetime
from get_token import get_token
from fn_ka10083 import fn_ka10083 # 키움 월봉 조회 API 함수
import time



def find_realtime_watchlist_kiwoom():

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

    for i, stock_info in enumerate(strategy_fit_stocks):
        if i > 0 and i % 50 == 0:
            print(f"\n--- {i}개 종목 처리 완료. 60초간 휴식합니다... ---\n")
            time.sleep(60)

        ticker = stock_info["종목코드"]
        stock_name = stock_info["종목명"]
        ma_period = stock_info["기준_이평선"]

        try:
            # --- [핵심 수정] 키움 API로 월봉 데이터 직접 요청 ---
            time.sleep(0.5) # 요청 속도 제어
            params = { 'stk_cd': ticker, 'chart_type_gb': 'M', 'base_dt': datetime.now().strftime('%Y%m%d'), 'upd_stkpc_tp': '1' }
            response = fn_ka10083(token=my_token, data=params)

            if response.status_code != 200:
                print(f"  -> [API 에러] {stock_name}({ticker}) - 상태 코드: {response.status_code}. 60초간 대기합니다.")
                print(f"     메시지: {response.text}")
                time.sleep(60)
                continue

            response_json = response.json()
            if 'stk_mth_pole_chart_qry' in response_json:
                df_monthly = pd.DataFrame(response_json['stk_mth_pole_chart_qry'])

                
                
                # --- [핵심 수정] 키움 데이터로 직접 계산 ---
                df_monthly['Close'] = pd.to_numeric(df_monthly['cur_prc'])
                # 키움 API는 최신순으로 데이터를 주므로, 뒤집어서 오래된 순으로 정렬
                df_monthly = df_monthly.iloc[::-1].reset_index(drop=True)
                
                df_monthly['MA'] = df_monthly['Close'].ewm(span=ma_period, adjust=False).mean()
                df_monthly.dropna(inplace=True)
                if df_monthly.empty: continue

                latest_close = df_monthly['Close'].iloc[-1]
                latest_ma = df_monthly['MA'].iloc[-1]

                

                # 4. 조건 확인
                if latest_close < latest_ma:
                    print(f"  -> [감시 대상 포착!] {stock_name}({ticker}) | 현재가: {latest_close:,.0f} < {ma_period}개월 이평: {latest_ma:,.2f}")
                    today_watchlist.append(stock_info)

        except Exception as e:
            print(f"  -> [에러 발생] {stock_name}({ticker}) 처리 중 오류: {e}")
            continue

    # 5. '오늘의' 최종 감시 목록을 'watchlist_today.json'으로 저장
    with open('watchlist_today.json', 'w', encoding='utf-8') as f:
        json.dump(today_watchlist, f, ensure_ascii=False, indent=4)
        
    print(f"\n총 {len(today_watchlist)}개의 금일 감시 대상 종목을 'watchlist_today.json' 파일로 저장했습니다.")
    print("="*50)

if __name__ == "__main__":
    # finder_backtest.py가 만든 파일 이름을 'watchlist_base.json'으로 변경해서 사용
    find_realtime_watchlist_kiwoom()