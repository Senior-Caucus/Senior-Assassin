(function() {
  const countdownEl = document.getElementById('countdown');
  function update() {
    // May 20, 2025 00:00 EST (UTC-4)
    const target = new Date('2025-05-26T00:00:00-04:00');
    const now = new Date();
    let diff = target - now;
    if (diff <= 0) {
      countdownEl.textContent = 'Signup period has ended.';
      // hide login_with_google id button
      const loginButton = document.getElementById('login');
      if (loginButton) {
        loginButton.style.display = 'none';
      }
      // May 20, 2025 00:00 EST (UTC-4)
      const target = new Date('2025-05-28T06:00:00-04:00');
      const now = new Date();
      let diff = target - now;
      if (diff <= 0) {
        countdownEl.textContent = 'The game has started.';
        return;
      }
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      diff %= 1000 * 60 * 60 * 24;
      const hours = Math.floor(diff / (1000 * 60 * 60));
      diff %= 1000 * 60 * 60;
      const minutes = Math.floor(diff / (1000 * 60));
      diff %= 1000 * 60;
      const seconds = Math.floor(diff / 1000);
      countdownEl.textContent = `The game starts in ${days}d ${hours}h ${minutes}m ${seconds}s`;
      return;
    }
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    diff %= 1000 * 60 * 60 * 24;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    diff %= 1000 * 60 * 60;
    const minutes = Math.floor(diff / (1000 * 60));
    diff %= 1000 * 60;
    const seconds = Math.floor(diff / 1000);
    countdownEl.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s left to sign up`;
  }
  update();
  setInterval(update, 1000);
})();