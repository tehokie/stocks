
import requests
import json

# 키움증권 실전투자 주문 API 엔드포인트 (가상)
# 실제 엔드포인트는 키움증권 API 문서를 참조해야 합니다.
KIWOOM_API_URL = "https://api.kiwoom.com/v1/order"

def send_order(token, ticker, price, quantity, order_type):
    """
    키움증권 API를 통해 매수/매도 주문을 전송합니다.

    Args:
        token (str): 인증을 위한 API 토큰
        ticker (str): 주문할 종목의 종목코드 (예: "005930")
        price (int): 주문 가격 (시장가 주문 시 0)
        quantity (int): 주문 수량
        order_type (str): 주문 유형 ("시장가", "지정가" 등)

    Returns:
        tuple: (성공여부(bool), 메시지(str))
    """
    try:
        # 1. 주문 유형을 API가 이해하는 코드로 변환
        # (실제 코드는 API 문서에 따라 다를 수 있습니다)
        if order_type == "시장가":
            order_code = "01"
        elif order_type == "지정가":
            order_code = "00"
        else:
            return False, f"지원하지 않는 주문 유형입니다: {order_type}"

        # 2. API 서버로 보낼 요청 헤더와 데이터를 구성
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payload = {
            "stk_cd": ticker,
            "ord_qty": quantity,
            "ord_prc": price,
            "ord_dv_cd": order_code, # 주문 구분 코드
            "buy_sell_gb": "B" # 매수(B) / 매도(S) 구분 (여기서는 매수만 가정)
        }

        # 3. API에 POST 요청을 보냄
        response = requests.post(KIWOOM_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # HTTP 오류 발생 시 예외 발생

        # 4. API 응답 결과를 파싱
        result = response.json()

        # 5. 주문 성공 여부에 따라 결과 반환
        # (실제 응답 형식은 API 문서 확인 필요)
        if result.get("success"):
            order_number = result.get("order_no", "N/A")
            return True, f"주문 성공 (주문번호: {order_number})"
        else:
            error_msg = result.get("msg", "알 수 없는 오류")
            return False, f"주문 실패: {error_msg}"

    except requests.exceptions.RequestException as e:
        return False, f"API 요청 실패: {e}"
    except Exception as e:
        return False, f"주문 처리 중 예외 발생: {e}"

# 이 파일이 직접 실행될 때를 위한 테스트 코드
if __name__ == '__main__':
    # 모의 테스트
    print("--- kiwoom_order.py 모의 테스트 ---")
    # 실제 토큰과 주문 정보가 필요합니다.
    # my_test_token = "실제_발급받은_토큰"
    # success, message = send_order(my_test_token, "005930", 0, 10, "시장가")
    # print(f"테스트 결과: {success}, 메시지: {message}")
    print("실제 주문을 위해서는 토큰과 주문 정보가 필요합니다.")
