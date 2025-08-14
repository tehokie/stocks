파이썬 기반 주식 자동매매 시스템 (Python-based Stock Trading Bot)
📖 프로젝트 개요 (Project Overview)
이 프로젝트는 **"데이터에 기반한 잃지 않는 투자"**를 목표로 개발된 개인용 주식 자동매매 시스템입니다. 월봉 차트의 장기 이동평균선을 기준으로 통계적으로 검증된 '저평가' 구간을 포착하고, 5개월 이동평균선 골든크로스를 통해 추세 전환의 초입을 감지하여 매수/매도 주문을 자동으로 실행합니다.
본 시스템은 키움증권 REST API를 활용하며, 모든 투자 판단은 과거 데이터에 대한 백테스팅 결과를 기반으로 이루어집니다.
🌟 핵심 전략 (Core Strategy)
본 시스템은 크게 2단계의 필터링을 통해 매수 대상을 선정합니다.
관심종목 선정 (What): 과거 20년간의 데이터를 분석하여, 특정 장기 이동평균선(48, 60, 72개월) 아래로 하락했을 때 **높은 '회복 확률(승률)'**과 **낮은 '평균 추가 하락률(안전성)'**을 보인 우량주만을 '관심종목 유니버스'로 구성합니다.
매수 시점 포착 (When): 선정된 관심종목이 장기 이평선 아래에 머물러 있다가, 월봉 차트에서 5개월 이동평균선이 골든크로스하는 추세 전환의 순간을 실시간으로 포착하여 매수 주문을 실행합니다.
🚀 시스템 아키텍처 (System Architecture)
본 시스템은 각기 다른 역할을 수행하는 여러 개의 파이썬 모듈이 유기적으로 협력하여 작동하도록 설계되었습니다.
code
Code
.
├── 📂 stocks/
│   ├── 📜 main.py                  # (지휘자) 전체 시스템을 스케줄링하고 실행
│   ├── 📜 finder_realtime.py       # (눈) 매일 장 마감 후 '오늘의 감시 대상' 선정
│   ├── 📜 trader.py                 # (심장) 장중에 실시간으로 종목을 감시하고 거래 실행
│   ├── 📜 kiwoom_order.py          # (손과 발) 키움증권 API에 실제 주문 전송
│   ├── 📜 get_token.py               # (출입증) 키움증권 API 접속 토큰 발급
│   ├── 📜 fn_ka10083.py            # (데이터 수집기) 키움증권 API로 월봉 데이터 조회
│   └── 🔑 config.json.example      # (설정값 예시) API 키 등 개인 정보를 입력하는 파일
└── 📄 README.md                    # (사용 설명서) 현재 이 파일
⚙️ 파일별 상세 설명 (File Descriptions)
main.py (지휘자):
APScheduler를 이용해 전체 시스템을 24시간 관리합니다. 매일 정해진 시간에 finder_realtime.py과 trader.py를 자동으로 실행하고 종료시키는 총사령관 역할을 합니다.
finder_realtime.py (눈):
매일 장 마감 후 실행됩니다. 사전에 finder_backtest.py(미포함)를 통해 검증된 '전략 적합 종목' 리스트(watchlist_base.json) 중에서, '현재' 장기 이평선 아래에 위치한 종목만을 골라내어 그날의 최종 감시 목록인 watchlist_today.json을 생성합니다.
trader.py (심장):
매일 장중에 실행됩니다. watchlist_today.json에 있는 종목들의 월봉 데이터를 실시간으로 조회하여 '5개월 이평선 골든크로스' 신호를 감시하고, 조건이 충족되면 kiwoom_order.py를 통해 자동으로 매수 주문을 실행합니다.
kiwoom_order.py (손과 발):
키움증권 API에 실제 매수/매도 주문을 전송하는 함수가 정의되어 있습니다.
get_token.py & fn_ka10083.py (지원팀):
API 접속을 위한 토큰 발급과 월봉 데이터 조회를 담당하는 유틸리티 모듈입니다.
config.json (개인 정보):
⚠️ 중요: 이 파일은 민감한 개인 API 키 정보를 담고 있으므로, git 관리 대상에서 반드시 제외해야 합니다 (.gitignore에 추가). 다른 사용자를 위해 config.json.example 파일에 어떤 내용을 채워야 하는지 예시를 제공합니다.
code
JSON
{
  "mock": {
    "host": "https://mockapi.kiwoom.com",
    "app_key": "YOUR_MOCK_APP_KEY",
    "app_secret": "YOUR_MOCK_APP_SECRET"
  },
  "real": {
    "host": "https://api.kiwoom.com",
    "app_key": "YOUR_REAL_APP_KEY",
    "app_secret": "YOUR_REAL_APP_SECRET"
  }
}
🛠️ 실행 방법 (How to Run)
Git Clone: git clone https://github.com/tehokie/stocks.git
라이브러리 설치: pip install -r requirements.txt (필요한 라이브러리 목록 파일 생성 권장)
config.json 생성: config.json.example 파일을 복사하여 config.json을 만들고, 자신의 키움증권 API 키를 입력합니다.
시스템 실행: python main.py
📜 면책 조항 (Disclaimer)
본 프로젝트는 투자의 참고 자료로만 활용될 수 있으며, 실제 투자에 대한 책임은 전적으로 투자자 본인에게 있습니다. 모든 투자는 모의투자를 통해 충분히 검증한 후, 신중하게 결정하시기 바랍니다.

💡 Special Thanks To
Special thanks to my partner, Gemini, an AI assistant from Google, who helped conceptualize the ideas, validate numerous backtesting codes, and collaboratively solve complex problems throughout this project.