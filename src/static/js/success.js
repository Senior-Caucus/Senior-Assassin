(function() {
    const countdownEl = document.getElementById('countdown');
    function update() {
      // May 20, 2025 00:00 EST (UTC-4)
      const target = new Date('2025-05-20T00:00:00-04:00');
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
    }
    update();
    setInterval(update, 1000);
  })();