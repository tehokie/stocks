# main.py (24시간 지휘자, 스케줄러)

import subprocess
import time

from schedulers.blocking import BlockingScheduler
from datetime import datetime

# --- 우리가 만든 프로그램들 ---
from finder_realtime import find_realtime_watchlist_fast
from trader import trader_main_loop

def run_finder():
    """장 마감 후 관심종목 탐색기 실행"""
    print(f"[{datetime.now()}] 스케줄러: 장 마감, 'Finder'를 실행합니다.")
    try:
        find_realtime_watchlist_fast()
    except Exception as e:
        print(f"'Finder' 실행 중 오류 발생: {e}")

def run_trader():
    """장 시작 시 거래 실행기 실행"""
    print(f"[{datetime.now()}] 스케줄러: 장 시작, 'Trader'를 실행합니다.")
    try:
        trader_main_loop()
    except Exception as e:
        print(f"'Trader' 실행 중 오류 발생: {e}")

if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='Asia/Seoul')

    # --- 스케줄 등록 ---
    # 1. 'finder_realtime.py'는 매일 오후 4시에 실행
    # (월~금만 실행하고 싶으면 day_of_week='mon-fri' 추가)
    scheduler.add_job(run_finder, 'cron', hour=16, minute=0)

    # 2. 'trader.py'는 매일 오전 8시 58분에 실행 (장 시작 2분 전)
    scheduler.add_job(run_trader, 'cron', hour=8, minute=58)

    print("="*50)
    print("전체 자동매매 시스템 스케줄러가 시작되었습니다.")
    print("Ctrl+C를 눌러 종료할 수 있습니다.")
    print("="*50)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("스케줄러가 종료되었습니다.")