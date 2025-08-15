# main.py (ver 2.0 - 생존 신호 기능 추가)

import time
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# --- 우리가 만든 프로그램들 ---
from finder_realtime import find_realtime_watchlist_kiwoom_final as run_finder # 이름 변경
from trader import trader_main_loop as run_trader # 이름 변경

def heart_beat():
    """스케줄러가 살아있는지 확인시켜주는 생존 신호 함수"""
    print(f"[{datetime.now()}] 스케줄러 정상 작동 중... 다음 작업을 대기합니다.")

if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='Asia/Seoul')

    # --- 스케줄 등록 ---
    # 1. 'finder_realtime.py'는 매일 오후 4시에 실행
    scheduler.add_job(run_finder, 'cron', hour=16, minute=5, day_of_week='mon-fri')

    # 2. 'trader.py'는 매일 오전 8시 58분에 실행
    scheduler.add_job(run_trader, 'cron', hour=8, minute=58, day_of_week='mon-fri')
    
    # --- [핵심 추가 기능!] 생존 신호 스케줄 ---
    # 3. 'heart_beat' 함수를 매 1시간마다 실행 (interval 방식)
    scheduler.add_job(heart_beat, 'interval', hours=1)

    print("="*50)
    print("전체 자동매매 시스템 스케줄러가 시작되었습니다.")
    print(f" -> 현재 시간: {datetime.now()}")
    print("Ctrl+C를 눌러 종료할 수 있습니다.")
    print("="*50)
    
    # 프로그램 시작 시 첫 생존 신호 보내기
    heart_beat()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("스케줄러가 종료되었습니다.")