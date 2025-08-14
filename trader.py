import time
import json
import pandas as pd
from datetime import datetime, time as dt_time

# 우리가 만든 다른 파일에서 필요한 함수들을 가져옵니다.
from get_token import get_token
from fn_ka10083 import fn_ka10083 # 월봉 조회 함수
from kiwoom_order import send_order # 키움 주문 실행 함수

BUY_AMOUNT = 1000000

def is_market_open():
    """현재 시간이 정규 주식 시장 시간(평일 9:00 ~ 15:20)인지 확인합니다."""
    now = datetime.now()
    market_open_time = dt_time(9, 0)
    market_close_time = dt_time(15, 20)
    # 월요일=0, 일요일=6
    return now.weekday() < 5 and market_open_time <= now.time() <= market_close_time

def trader_main_loop():
    # 1. 관심종목 리스트를 불러옵니다.
    try:
        with open('watchlist_today.json', 'r', encoding='utf-8') as f:
            watchlist = json.load(f)
    except FileNotFoundError:
        print("감시할 종목 파일('watchlist_today.json')을 찾을 수 없습니다.")
        return

    # 2. API 토큰을 발급받습니다.
    my_token = get_token()
    if not my_token:
        print("토큰 발급에 실패했습니다. 프로그램을 종료합니다.")
        return

    already_bought = [] # 당일 이미 매수한 종목을 기록하는 리스트

    # 3. 장이 열려있는 동안 계속 실행합니다.
    while is_market_open():
        print(f"\n--- {datetime.now()} 관심종목 실시간 감시 시작 ---")
        for stock_info in watchlist:
            ticker = stock_info['종목코드']
            stock_name = stock_info['종목명']

            if ticker in already_bought:
                continue

            try:
                # 4. 키움 API로 최근 월봉 데이터를 실시간으로 요청합니다.
                params = { 'stk_cd': ticker, 'chart_type_gb': 'M', 'base_dt': datetime.now().strftime('%Y%m%d'), 'upd_stkpc_tp': '1' }
                monthly_data_json = fn_ka10083(token=my_token, data=params)

                # 5. 받아온 JSON 데이터를 DataFrame으로 가공합니다.
                if monthly_data_json and 'stk_mth_pole_chart_qry' in monthly_data_json:
                    df_monthly = pd.DataFrame(monthly_data_json['stk_mth_pole_chart_qry'])
                    
                    df_monthly['Date'] = pd.to_datetime(df_monthly['dt'], format='%Y%m%d')
                    df_monthly.set_index('Date', inplace=True)
                    df_monthly['Close'] = pd.to_numeric(df_monthly['cur_prc'])
                    df_monthly.sort_index(inplace=True)
                    
                    # 6. 5개월, 10개월 이동평균선을 계산합니다.
                    df_monthly['MA5'] = df_monthly['Close'].rolling(window=5).mean()
                    df_monthly['MA10'] = df_monthly['Close'].rolling(window=10).mean()

                    if len(df_monthly) < 10: continue

                     # 7. '월봉 골든크로스' 조건을 판단합니다.
                    last_month = df_monthly.iloc[-2]
                    this_month = df_monthly.iloc[-1]

                    if last_month['Close'] < last_month['MA5'] and this_month['Close'] > this_month['MA5']:
                        print(f"★★★ 최종 매수 신호 발생: {stock_name}({ticker}) ★★★")
                        
                        # --- [여기가 바로 업그레이드 포인트!] ---
                        # 8. 100만원 기준으로 매수 수량 계산
                        
                        # 현재가(이번달 실시간 종가)를 기준으로 계산
                        current_price = this_month['Close']
                        
                        # 0으로 나누는 오류 방지
                        if current_price > 0:
                            # 100만원을 현재가로 나누어 매수 가능한 주식 수를 계산
                            # int()를 사용해 소수점 이하는 버린다 (예: 10.8주 -> 10주)
                            quantity_to_buy = int(BUY_AMOUNT // current_price)
                        else:
                            quantity_to_buy = 0

                        # 계산된 수량이 1주 이상일 경우에만 주문 실행
                        if quantity_to_buy > 0:
                            print(f"  -> 현재가: {int(current_price):,}원, 매수 예정 수량: {quantity_to_buy}주")
                            
                            # 9. 키움증권에 실제 매수 주문을 실행합니다!
                            success, msg = send_order(
                                token=my_token, 
                                ticker=ticker, 
                                price=0,  # 시장가 주문이므로 가격은 0
                                quantity=quantity_to_buy, 
                                order_type="시장가"
                            )
                            
                            if success:
                                print(f"  -> 매수 주문 성공: {msg}")
                                already_bought.append(ticker)
                            else:
                                print(f"  -> 매수 주문 실패: {msg}")
                        else:
                            print(f"  -> 주문 수량 계산 불가 또는 0주. (현재가: {int(current_price):,}원)")
                
            except Exception as e:
                print(f"  -> {stock_name} 처리 중 오류 발생: {e}")

            time.sleep(1)

        print("--- 모든 관심종목 1회 감시 완료. 5분 후 다시 시작합니다. ---")
        time.sleep(300)
    
    print(f"[{datetime.now()}] 장 마감 시간입니다. Trader를 종료합니다.")