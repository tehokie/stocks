# 파이썬 기반 주식 자동매매 시스템 (Python-based Stock Trading Bot)

## 📖 프로젝트 개요 (Project Overview)

이 프로젝트는 **"데이터에 기반한 잃지 않는 투자"**를 목표로 개발된 개인용 주식 자동매매 시스템입니다. 키움증권 REST API를 활용하며, 과거 데이터에 대한 통계적 백테스팅을 통해 검증된 투자 전략을 자동으로 실행합니다.

**👉 [프로젝트 상세 설명 위키 페이지 바로가기 (Click here for detailed project Wiki)](https://github.com/tehokie/stocks/wiki)**

---

## 🚀 시스템 아키텍처 (System Architecture)

![System Architecture Diagram](https://example.com/your_diagram_image_url.png) 
*(선택사항: 위 다이어그램 이미지를 만들어 올리면 훨씬 더 전문적으로 보입니다.)*

*   **`main.py` (지휘자):** 전체 시스템을 24시간 스케줄링하고 실행.
*   **`finder_realtime.py` (눈):** 매일 장 마감 후 '오늘의 감시 대상' 선정.
*   **`trader.py` (심장):** 장중에 실시간으로 종목을 감시하고 거래 실행.
*   **`kiwoom_order.py` (손과 발):** 키움증권 API에 실제 주문 전송.
*   **... (기타 지원 모듈)**

---

## 🛠️ 실행 방법 (How to Run)

1.  **Git Clone:** `git clone https://github.com/tehokie/stocks.git`
2.  **라이브러리 설치:** `pip install -r requirements.txt`
3.  **`config.json` 생성:** `config.json.example` 파일을 복사하여 `config.json`을 만들고, 자신의 키움증권 API 키를 입력합니다.
4.  **시스템 실행:** `python main.py`

---

## 📜 면책 조항 (Disclaimer)

본 프로젝트는 투자의 참고 자료로만 활용될 수 있으며, 실제 투자에 대한 책임은 전적으로 투자자 본인에게 있습니다.

---

## 💡 Special Thanks To

Special thanks to my partner, **Gemini, an AI assistant from Google**, who helped conceptualize the ideas and validate numerous backtesting codes.