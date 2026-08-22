document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('routineForm');
  const submitBtn = document.getElementById('submitBtn');
  const formMsg = document.getElementById('formMsg');
  const resultArea = document.getElementById('resultArea');
  const resultBody = document.getElementById('resultBody');
  const resultLevel = document.getElementById('resultLevel');
  const resultTime = document.getElementById('resultTime');
  const resultNo = document.getElementById('resultNo');

  const REQUEST_TIMEOUT_MS = 15000;

  function setMsg(text, type) {
    formMsg.textContent = text;
    formMsg.className = 'form-msg' + (type ? ' ' + type : '');
  }

  function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    submitBtn.textContent = isLoading ? '루틴 만드는 중…' : '루틴 만들기 →';
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const interest = document.getElementById('interest').value.trim();
    const time = document.getElementById('time').value;
    const level = form.querySelector('input[name="level"]:checked').value;

    // 1) 빈 입력(필수값 누락) 처리
    if (!interest || !time) {
      setMsg('관심사와 가능 시간을 모두 입력해주세요.', 'error');
      return;
    }

    setMsg('', '');
    setLoading(true);
    resultArea.hidden = true;
    setMsg('AI가 루틴을 만들고 있어요…', 'loading');

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interest, time, level }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // 2) API 오류(4xx/5xx) 처리
      if (!res.ok) {
        setMsg('요청이 실패했어요 (오류 코드 ' + res.status + '). 잠시 후 다시 시도해주세요.', 'error');
        setLoading(false);
        return;
      }

      const data = await res.json();

      if (!data.routine) {
        setMsg('결과를 받지 못했어요. 잠시 후 다시 시도해주세요.', 'error');
        setLoading(false);
        return;
      }

      // 결과 렌더링
      resultBody.textContent = data.routine;
      resultLevel.textContent = 'LEVEL · ' + level;
      resultTime.textContent = 'TIME · ' + time;
      resultNo.textContent = 'NO. ' + String(Math.floor(Math.random() * 90) + 10);
      resultArea.hidden = false;
      setMsg('', '');
      resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (err) {
      clearTimeout(timeoutId);
      // 3) 지연/타임아웃 처리
      if (err.name === 'AbortError') {
        setMsg('응답이 너무 지연되고 있어요. 잠시 후 다시 시도해주세요.', 'error');
      } else {
        setMsg('네트워크 오류가 발생했어요. 인터넷 연결을 확인해주세요.', 'error');
      }
    } finally {
      setLoading(false);
    }
  });
});
