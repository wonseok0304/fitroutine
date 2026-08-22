import json
import os
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.error


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"


def build_prompt(interest, time_budget, level):
    return (
        "너는 운동/취미 루틴 코치야. 아래 조건에 맞는 7일(월~일) 주간 루틴을 만들어줘.\n"
        f"- 관심사/종목: {interest}\n"
        f"- 하루 가능 시간: {time_budget}\n"
        f"- 현재 레벨: {level}\n\n"
        "형식 규칙:\n"
        "- 각 줄은 '요일: 활동 내용' 형태로 작성 (예: '월: 가벼운 러닝 20분')\n"
        "- 쉬는 날도 '휴식: 스트레칭 5분' 처럼 최소한의 활동을 포함해줘\n"
        "- 초보자도 이해할 수 있는 쉬운 말로, 과장 없이 현실적으로 작성해줘\n"
        "- 마지막 줄에 '팁:' 으로 시작하는 한 줄 조언을 추가해줘\n"
        "- 불필요한 인사말이나 서론 없이 바로 루틴만 출력해줘"
    )


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            data = json.loads(raw_body or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._send_json(400, {"error": "요청 본문을 읽을 수 없어요."})
            return

        interest = (data.get("interest") or "").strip()
        time_budget = (data.get("time") or "").strip()
        level = (data.get("level") or "").strip()

        # 필수값 검증 (빈 입력 처리)
        if not interest or not time_budget:
            self._send_json(400, {"error": "관심사와 가능 시간은 필수입니다."})
            return

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            self._send_json(500, {"error": "서버에 API 키가 설정되어 있지 않습니다."})
            return

        prompt = build_prompt(interest, time_budget, level or "초급")

        request_payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }

        req = urllib.request.Request(
            GROQ_URL,
            data=json.dumps(request_payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                result = json.loads(response.read().decode("utf-8"))
                routine_text = result["choices"][0]["message"]["content"].strip()
                self._send_json(200, {"routine": routine_text})

        except urllib.error.HTTPError as e:
            # API 오류(4xx/5xx) 처리
            self._send_json(502, {"error": f"AI API 오류가 발생했습니다 ({e.code})."})
        except urllib.error.URLError:
            # 지연/타임아웃 처리
            self._send_json(504, {"error": "AI 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."})
        except (KeyError, IndexError, json.JSONDecodeError):
            self._send_json(500, {"error": "AI 응답을 처리하는 중 오류가 발생했습니다."})

    def do_GET(self):
        self._send_json(405, {"error": "POST 요청만 지원합니다."})
