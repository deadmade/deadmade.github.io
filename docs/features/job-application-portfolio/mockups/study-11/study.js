// THROWAWAY study chrome: palette toggle (P), remembered across the study's pages.
(function () {
  var root = document.documentElement;
  function get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function put(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  root.dataset.palette = get('s5-palette') || 'a';

  var chip = document.createElement('button');
  chip.type = 'button';
  chip.className = 'chip';
  function label() { chip.textContent = 'study 11 · P palette ' + root.dataset.palette.toUpperCase(); }
  function togglePalette() { root.dataset.palette = root.dataset.palette === 'a' ? 'b' : 'a'; put('s5-palette', root.dataset.palette); label(); }
  chip.addEventListener('click', togglePalette);
  addEventListener('keydown', function (e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.key === 'p' || e.key === 'P') togglePalette();
  });
  label();
  document.body.appendChild(chip);
})();
