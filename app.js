const form = document.querySelector('#careerForm');
const panels = [...document.querySelectorAll('.form-panel')];
const progressText = document.querySelector('#progressText');
const results = document.querySelector('#results');
const assessment = document.querySelector('#assessment');
const range = document.querySelector('#confidenceRange');
const confidenceNumber = document.querySelector('#confidenceNumber');

function showPanel(number) {
  panels.forEach((panel) => panel.classList.toggle('active-panel', panel.dataset.panel === String(number)));
  progressText.textContent = `Profile · ${number} of 2`;
}

document.querySelector('.next-button').addEventListener('click', () => {
  const stream = form.elements.stream.value;
  const interests = form.querySelectorAll('input[name="interests"]:checked');
  if (!stream) return form.elements.stream.focus();
  if (!interests.length) return document.querySelector('.interest-question').classList.add('shake');
  showPanel(2);
});

document.querySelector('.back-button').addEventListener('click', () => showPanel(1));
range.addEventListener('input', () => { confidenceNumber.textContent = range.value; });

document.querySelectorAll('.interest').forEach((card) => {
  card.addEventListener('animationend', () => card.parentElement?.classList.remove('shake'));
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const submit = form.querySelector('button[type="submit"]');
  submit.disabled = true;
  submit.innerHTML = 'Mapping your paths <span>…</span>';
  const payload = {
    name: form.elements.name.value.trim(),
    stream: form.elements.stream.value,
    confidence: form.elements.confidence.value,
    interests: [...form.querySelectorAll('input[name="interests"]:checked')].map((input) => input.value),
  };
  try {
    const response = await fetch('/api/recommend', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    renderResults(data);
  } catch (error) {
    submit.disabled = false;
    submit.innerHTML = 'Reveal my paths <span>↗</span>';
    alert(error.message || 'Something went wrong. Please try again.');
  }
});

function renderResults(data) {
  document.querySelector('#resultGreeting').innerHTML = data.profile.name ? `${data.profile.name}, your next move starts here.` : 'Possibilities worth exploring.';
  document.querySelector('#recommendationList').innerHTML = data.recommendations.map((career, index) => `
    <article class="recommendation-card ${index === 0 ? 'top-match' : ''}">
      <div class="rank">0${index + 1}</div>
      <div class="career-icon ${career.color}">${career.icon}</div>
      <div class="career-main"><div class="career-meta"><span>${index === 0 ? 'BEST MATCH' : career.category}</span><span>${career.score}% fit</span></div><h3>${career.title}</h3><p>${career.description}</p><div class="skill-row">${career.skills.map((skill) => `<span>${skill}</span>`).join('')}</div></div>
      <div class="career-side"><div><small>STARTING AVG.</small><strong>${career.salary}</strong></div><div><small>DEMAND INDEX</small><strong>${career.demand}<i>/100</i></strong></div></div>
      <details><summary>See your starter roadmap <span>＋</span></summary><div class="roadmap">${career.roadmap.map((step, stepIndex) => `<div><b>0${stepIndex + 1}</b>${step}</div>`).join('')}</div></details>
    </article>`).join('');
  assessment.hidden = true;
  results.hidden = false;
  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

document.querySelector('#resetButton').addEventListener('click', () => {
  form.reset(); range.value = 3; confidenceNumber.textContent = '3';
  panels.forEach((panel) => panel.classList.remove('active-panel'));
  panels[0].classList.add('active-panel');
  progressText.textContent = 'Profile · 1 of 2';
  results.hidden = true; assessment.hidden = false; assessment.scrollIntoView({ behavior: 'smooth' });
  const submit = form.querySelector('button[type="submit"]'); submit.disabled = false; submit.innerHTML = 'Reveal my paths <span>↗</span>';
});
