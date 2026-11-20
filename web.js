const ALLOWED = new Set(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Enter','Shift','Tab','Escape']);
const stack = ['case'];            // case > book > entry > glyph
let lastEsc = 0, inspect = false;

function back() { if (stack.length > 1) stack.pop(); render(); }
function exitApp() { window.close(); location.replace('about:blank'); }  // a browser tab can't always close itself

addEventListener('keydown', e => {
  if (e.ctrlKey || e.metaKey || e.altKey) return;      // leave F5, Ctrl+W etc. alone
  e.preventDefault();                                   // all other keys do nothing
  if (!ALLOWED.has(e.key)) return;
  if (e.repeat && !e.key.startsWith('Arrow')) return;
  switch (e.key) {
    case 'ArrowUp':    move(0, -1); break;
    case 'ArrowDown':  move(0,  1); break;
    case 'ArrowLeft':  move(-1, 0); break;
    case 'ArrowRight': move( 1, 0); break;
    case 'Enter':      enter(); break;
    case 'Shift':      back(); break;
    case 'Tab':        inspect = !inspect; render(); break;
    case 'Escape': {
      const now = performance.now();
      if (now - lastEsc < 600) return exitApp();
      lastEsc = now; back(); break;
    }
  }
});