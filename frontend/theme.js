(() => {
  let savedTheme = null;
  try {
    savedTheme = window.localStorage.getItem('tenderlens-theme');
  } catch (error) {
    // The page can still use the browser's color preference when storage is disabled.
  }

  const systemPrefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  const theme = savedTheme === 'dark' || savedTheme === 'light'
    ? savedTheme
    : (systemPrefersDark ? 'dark' : 'light');
  document.documentElement.dataset.theme = theme;
})();
