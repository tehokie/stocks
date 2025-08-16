# finder_backtest.py (ver 2.0)

import FinanceDataReader as fdr
import pandas as pd
import numpy as np
from pykrx import stock
import time
import json
from datetime import datetime

def get_validated_stocks(min_win_rate=85.0, max_drawdown=-10.0):
    """
    (ver 2.0)
    - 관리종목 필터링 강화
    - 분석 대상 이평선을 48, 60, 72개월로 확대
    """
    print("="*50)
    print("관심종목 탐색기 (Finder v2.0)를 시작합니다.")
    
    # --- [개선점 1] 관리종목 필터링 강화 ---
    print("1. KRX 전체 종목 코드 및 관리종목 정보를 가져오는 중입니다...")
    try:
        # 코스피, 코스닥 종목 정보를 각각 가져온다.
        kospi_tickers = stock.get_market_ticker_list(market="KOSPI")
        kosdaq_tickers = stock.get_market_ticker_list(market="KOSDAQ")
        all_tickers = kospi_tickers + kosdaq_tickers
        
        # 각 시장의 관리종목/거래정지 목록을 가져온다.
        admin_tickers = set()
        for ticker in all_tickers:
            try:
                stock_name = stock.get_market_ticker_name(ticker)
                # 종목코드와 종목명을 함께 출력
                print(f"{ticker}: {stock_name}")
                # '관리종목' 또는 '거래정지'가 종목명에 포함되어 있으면 필터링
                if '관리종목' in stock_name or '거래정지' in stock_name:
                    admin_tickers.add(ticker)
            except:
                continue

        tickers = [ticker for ticker in all_tickers if ticker not in admin_tickers and ticker[-1] == '0']
        print(f" -> 관리/우선주 등 제외 후 {len(tickers)}개 종목 대상")
    except Exception as e:
        print(f" -> 종목 필터링 중 오류 발생: {e}. 기본 로직으로 실행합니다.")
        tickers = [t for t in stock.get_market_ticker_list(market="ALL") if t[-1] == '0']

    final_watchlist = []
    start_time = time.time()

    print("\n2. 각 종목별 승률 및 안전성 분석을 시작합니다...")
    
    for i, ticker in enumerate(tickers):
        if (i + 1) % 50 == 0:
            print(f" -> 진행률: [{i+1}/{len(tickers)}]")
            
        try:
            df = fdr.DataReader(ticker, '2002-01-01')
            if df.empty or len(df) < 72 * 20:
                continue
            
            df_monthly = df.resample('ME').agg({'Close': 'last'}).ffill()
            
            # --- [개선점 2] 분석 대상 이평선 확대 ---
            best_result_for_stock = None
            ma_periods_to_test = [48, 60, 72] # 테스트할 이평선 리스트

            for period in ma_periods_to_test:
                if len(df_monthly) < period: continue

                # --- 1차 필터링: 승률 분석 ---
                df_monthly[f'MA{period}'] = df_monthly['Close'].rolling(window=period).mean()
                test_df_winrate = df_monthly.dropna().copy()
                
                close_prices_wr = test_df_winrate['Close'].to_numpy()
                ma_prices_wr = test_df_winrate[f'MA{period}'].to_numpy()
                
                signals_wr = 0
                wins_wr = 0
                k = 0
                while k < len(close_prices_wr):
                    if close_prices_wr[k] < ma_prices_wr[k]:
                        signals_wr += 1
                        if k + 12 < len(close_prices_wr):
                            if close_prices_wr[k + 12] > close_prices_wr[k]:
                                wins_wr += 1
                        k += 12
                    else:
                        k += 1

                if signals_wr < 3:
                    continue
                
                win_rate = (wins_wr / signals_wr) * 100
                if win_rate < min_win_rate:
                    continue

                # --- 2차 필터링: 안전성 분석 (평균 추가 하락률) ---
                drawdowns = []
                for j in range(1, len(close_prices_wr)):
                    if close_prices_wr[j-1] >= ma_prices_wr[j-1] and close_prices_wr[j] < ma_prices_wr[j]:
                        signal_price = close_prices_wr[j]
                        lowest_price = signal_price
                        for l in range(j, len(close_prices_wr)):
                            if close_prices_wr[l] < lowest_price:
                                lowest_price = close_prices_wr[l]
                            if close_prices_wr[l] > ma_prices_wr[l]:
                                break
                        drawdown = ((lowest_price - signal_price) / signal_price) * 100
                        drawdowns.append(drawdown)

                if not drawdowns:
                    continue

                avg_drawdown = np.mean(drawdowns)
                if avg_drawdown < max_drawdown:
                    continue

                # --- 모든 필터를 통과했다면, 결과 정리 ---
                current_result = {
                    "종목코드": ticker, "기준_이평선": period,
                    "승률(%)": round(win_rate, 2), "평균추가하락률(%)": round(avg_drawdown, 2)
                }

                # 이 종목의 '최고의 결과'를 저장하는 로직
                if best_result_for_stock is None or \
                   current_result["승률(%)"] > best_result_for_stock["승률(%)"] or \
                   (current_result["승률(%)"] == best_result_for_stock["승률(%)"] and 
                    current_result["평균추가하락률(%)"] > best_result_for_stock["평균추가하락률(%)"]):
                    best_result_for_stock = current_result

            # 한 종목에 대한 모든 이평선 테스트가 끝난 후, 최고의 결과가 있다면 관심종목에 추가
            if best_result_for_stock:
                stock_name = stock.get_market_ticker_name(ticker)
                best_result_for_stock["종목명"] = stock_name # 종목명 추가
                final_watchlist.append(best_result_for_stock)
                print(f"  -> [관심종목 발견!] {stock_name}({ticker}) @{best_result_for_stock['기준_이평선']}개월 | 승률: {best_result_for_stock['승률(%)']:.2f}%, 안전성: {best_result_for_stock['평균추가하락률(%)']:.2f}%")

        except Exception:
            continue
            
    # ... (이하 파일 저장 및 종료 부분은 동일) ...
    end_time = time.time()
    print(f"\n3. 분석 완료! (총 소요 시간: {int(end_time - start_time)}초)")

    # --- 4. watchlist.json 파일로 저장 ---
    if final_watchlist:
        try:
            with open('watchlist_base.json', 'w', encoding='utf-8') as f:
                json.dump(final_watchlist, f, ensure_ascii=False, indent=4)
            print(f"\n총 {len(final_watchlist)}개의 관심종목을 'watchlist_base.json' 파일로 저장했습니다.")
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {e}")
    else:
        print("\n조건을 만족하는 관심종목을 찾지 못했습니다.")
    print("="*50)
if __name__ == "__main__":
    get_validated_stocks(min_win_rate=75.0, max_drawdown=-10.0)