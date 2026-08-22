// 문의하기 폼 - Formspree(무료 노코드 자동화 도구)로 전송
// 아래 FORMSPREE_ENDPOINT를 본인의 Formspree 폼 주소로 교체하세요.
// (https://formspree.io 에서 무료 가입 후 발급받은 https://formspree.io/f/xxxxxxx 형태의 주소)
const FORMSPREE_ENDPOINT = 'https://formspree.io/f/xppanyjg';

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('contactForm');
  if (!form) return;

  const submitBtn = document.getElementById('contactSubmitBtn');
  const msg = document.getElementById('contactMsg');

  function setMsg(text, type) {
    msg.textContent = text;
    msg.className = 'form-msg' + (type ? ' ' + type : '');
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('contactName').value.trim();
    const email = document.getElementById('contactEmail').value.trim();
    const message = document.getElementById('contactMessage').value.trim();

    if (!name || !email || !message) {
      setMsg('모든 항목을 입력해주세요.', 'error');
      return;
    }

    if (FORMSPREE_ENDPOINT.includes('YOUR_FORM_ID')) {
      setMsg('문의 폼이 아직 연결되지 않았어요. (관리자: Formspree 연동 필요)', 'error');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = '보내는 중…';
    setMsg('', '');

    try {
      const res = await fetch(FORMSPREE_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ name, email, message }),
      });

      if (res.ok) {
        setMsg('문의가 접수됐어요. 빠르게 답변드릴게요!', 'success');
        form.reset();
      } else {
        setMsg('전송에 실패했어요 (오류 코드 ' + res.status + '). 잠시 후 다시 시도해주세요.', 'error');
      }
    } catch (err) {
      setMsg('네트워크 오류가 발생했어요. 인터넷 연결을 확인해주세요.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = '문의 보내기 →';
    }
  });
});
