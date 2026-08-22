import json
import os
import urllib.request
import urllib.error

from flask import Flask, request, jsonify

app = Flask(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"


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


def handle_recommend():
    try:
        data = request.get_json(force=True, silent=True) or {}
    except Exception:
        return jsonify({"error": "요청 본문을 읽을 수 없어요."}), 400

    interest = (data.get("interest") or "").strip()
    time_budget = (data.get("time") or "").strip()
    level = (data.get("level") or "").strip()

    if not interest or not time_budget:
        return jsonify({"error": "관심사와 가능 시간은 필수입니다."}), 400

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "서버에 API 키가 설정되어 있지 않습니다."}), 500

    prompt = build_prompt(interest, time_budget, level or "초급")

    request_payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    req = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(request_payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (compatible; FitRoutine/1.0)",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            routine_text = result["choices"][0]["message"]["content"].strip()
            return jsonify({"routine": routine_text}), 200

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        return jsonify({"error": f"AI API 오류가 발생했습니다 ({e.code}).", "detail": error_body}), 502
    except urllib.error.URLError:
        return jsonify({"error": "AI 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요."}), 504
    except (KeyError, IndexError, json.JSONDecodeError):
        return jsonify({"error": "AI 응답을 처리하는 중 오류가 발생했습니다."}), 500


@app.route("/", methods=["POST"])
@app.route("/api/recommend", methods=["POST"])
def recommend():
    return handle_recommend()


@app.route("/", methods=["GET"])
@app.route("/api/recommend", methods=["GET"])
def recommend_get():
    return jsonify({"error": "POST 요청만 지원합니다."}), 405
