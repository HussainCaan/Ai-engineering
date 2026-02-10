document.addEventListener('DOMContentLoaded', () => {
  const resumeInput = document.getElementById('resume');
  const jdInput = document.getElementById('job-desc');
  const analyzeBtn = document.querySelector('[data-action="analyze"]');
  const resumeStatus = document.querySelector('[data-slot="resume-status"]');
  const sendBtn = document.querySelector('[data-action="send"]');
  const chatInput = document.querySelector('.chat-input input');
  const chatWindow = document.querySelector('[data-slot="chat-window"]');
  const scoreHeading = document.getElementById('Score');


  document.addEventListener('submit', (e) => {
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    return false;
  });

  const apiBase = 'http://127.0.0.1:8000';

  const setStatus = (text, color = '') => {
    resumeStatus.textContent = text;
    resumeStatus.style.color = color;
  };

  const setScore = (text) => {
    if (!scoreHeading) return;
    scoreHeading.textContent = text;
  };

  const recordBotQuestion = () => {
    if (interviewDone) return;
    questionCount += 1;
    if (questionCount >= targetCount) {
      interviewDone = true;
      setStatus('Interview complete. Score coming soon.', '#f59e0b');
      sendBtn.disabled = true;
      chatInput.disabled = true;
    }
  };

  let chatReady = false;
  let questionCount = 0;
  const targetCount = 4; 
  let interviewDone = false;

  const appendMessage = (role, text) => {
    const div = document.createElement('div');
    div.className = role === 'user' ? 'msg user' : 'msg bot';
    div.textContent = text;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  };

  if (!analyzeBtn || !sendBtn || !chatInput || !chatWindow) {
    console.error('Required UI elements not found');
    return;
  }

  analyzeBtn.addEventListener('click', async (event) => {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    const file = resumeInput.files?.[0];
    const jd = jdInput.value.trim();

    console.log('Analyze clicked, file:', file, 'JD length:', jd.length);

    if (!file) {
      setStatus('Please upload a CV (PDF/DOCX).', 'red');
      return;
    }
    if (!jd) {
      setStatus('Please paste the job description.', 'red');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setStatus('File too large (max 10MB).', 'red');
      return;
    }

    setStatus(`Uploading ${file.name}…`);
    setScore('Score:'); 

    const form = new FormData();
    form.append('resume', file);
    form.append('job_description', jd);

    try {
      console.log('Sending request to backend...');

      await fetchReset();
      console.log('Session reset');

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 180000);

      const resp = await fetch(`${apiBase}/analyze`, {
        method: 'POST',
        body: form,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      console.log('Response received:', resp.status);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      setStatus('Uploaded. Initializing chat…', '#10b981');

  
      chatReady = true;
      await bootstrapChat();

      console.log('Analysis result:', data);
    } catch (err) {
      console.error('Full error:', err);
      console.error('Error name:', err.name);
      console.error('Error stack:', err.stack);

      let errorMsg = err.message;
      if (err.name === 'AbortError') {
        errorMsg = 'Request timed out (3 min). Backend may be slow or stuck.';
      } else if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
        errorMsg = 'Backend not reachable. Check if server is running on port 8000.';
        console.error('CORS or network issue - backend not reachable at http://127.0.0.1:8000');
      }

      setStatus('Error: ' + errorMsg, 'red');
      chatReady = false;
    }

    return false; 
  });

  const fetchChatNext = async (userText) => {
    const resp = await fetch(`${apiBase}/chat/next`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_answer: userText }),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  };

  const fetchScore = async () => {
    const resp = await fetch(`${apiBase}/chat/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  };

  const fetchReset = async () => {
    const resp = await fetch(`${apiBase}/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  };

  const bootstrapChat = async () => {
    chatWindow.innerHTML = '';
    appendMessage('bot', 'Analyzing your profile…');
    questionCount = 0;
    interviewDone = false;
    chatInput.disabled = false;
    sendBtn.disabled = false;
    setScore('Score:');  // Reset score for new interview
    try {
      const data = await fetchChatNext('');
      appendMessage('bot', data.question || 'Let us start the mock interview.');
      recordBotQuestion();
      setStatus('Chat ready. Ask or respond to proceed.', '#10b981');
    } catch (err) {
      console.error('Bootstrap chat error:', err);
      setStatus('Chat init error: ' + err.message, 'red');
      chatReady = false;
    }
  };

  const sendMessage = async () => {
    if (!chatReady) {
      setStatus('Upload CV + JD first.', 'red');
      return;
    }

    const userText = chatInput.value.trim();
    if (!userText) return;

    appendMessage('user', userText);
    chatInput.value = '';
    sendBtn.disabled = true;

    try {
      const data = await fetchChatNext(userText);
      appendMessage('bot', data.question || '');
      recordBotQuestion();
      if (interviewDone) {
        setScore('Score: calculating...');
        try {
          const scoreData = await fetchScore();
          setScore(`Score: ${scoreData.score}/10`);
          appendMessage('bot', `Interview complete! Your score: ${scoreData.score}/10\n\nFeedback: ${scoreData.feedback}`);
          setStatus('Interview finished. See your score above.', '#10b981');
        } catch (scoreErr) {
          console.error('Score error:', scoreErr);
          setScore('Score: error');
          setStatus('Could not fetch score: ' + scoreErr.message, 'red');
        }
      }
    } catch (err) {
      console.error('Chat error:', err);
      setStatus('Chat error: ' + err.message, 'red');
    } finally {
      sendBtn.disabled = false;
    }
  };

  sendBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    sendMessage();
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });
});