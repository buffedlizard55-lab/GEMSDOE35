(() => {
  const button = document.getElementById('copy-note');
  const note = document.getElementById('submission-note');
  const status = document.getElementById('copy-status');
  if (!button || !note || !status) return;

  button.addEventListener('click', async () => {
    const text = note.textContent.trim();
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const field = document.createElement('textarea');
        field.value = text;
        field.setAttribute('readonly', '');
        field.style.position = 'fixed';
        field.style.opacity = '0';
        document.body.appendChild(field);
        field.select();
        const copied = document.execCommand('copy');
        field.remove();
        if (!copied) throw new Error('copy command was not available');
      }
      status.textContent = 'Submission note copied.';
    } catch (_) {
      status.textContent = 'Copy unavailable — select and copy the note above.';
    }
  });
})();
