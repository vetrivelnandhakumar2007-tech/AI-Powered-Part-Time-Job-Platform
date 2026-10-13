/* JobLink AI — shared front-end interactivity */
document.addEventListener('DOMContentLoaded', function () {

  /* ---------- Navbar: elevate on scroll ---------- */
  var nav = document.querySelector('.navbar-jla');
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Auto-dismiss alerts ---------- */
  document.querySelectorAll('.alert').forEach(function (alertEl) {
    setTimeout(function () {
      alertEl.classList.remove('show');
      alertEl.classList.add('fade-out-alert');
      setTimeout(function () { alertEl.remove(); }, 400);
    }, 4500);
  });

  /* ---------- Fade-in-on-scroll ---------- */
  var revealables = document.querySelectorAll('.fade-in-up');
  if ('IntersectionObserver' in window && revealables.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealables.forEach(function (el, i) {
      el.style.transitionDelay = Math.min(i * 60, 300) + 'ms';
      io.observe(el);
    });
  } else {
    revealables.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Animated stat counters ---------- */
  document.querySelectorAll('.stat-num[data-count]').forEach(function (el) {
    var target = parseInt(el.getAttribute('data-count'), 10) || 0;
    var duration = 800;
    var start = null;
    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      el.textContent = Math.floor(progress * target);
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target;
    }
    requestAnimationFrame(step);
  });

  /* ---------- Live client-side job filter (progressive enhancement) ---------- */
  var liveFilter = document.getElementById('live-filter');
  var jobGrid = document.getElementById('job-grid');
  if (liveFilter && jobGrid) {
    var cards = Array.prototype.slice.call(jobGrid.querySelectorAll('.job-grid-item'));
    liveFilter.addEventListener('input', function () {
      var q = liveFilter.value.trim().toLowerCase();
      var visible = 0;
      cards.forEach(function (card) {
        var hay = card.getAttribute('data-search') || '';
        var match = hay.indexOf(q) !== -1;
        card.style.display = match ? '' : 'none';
        if (match) visible++;
      });
      var empty = document.getElementById('live-filter-empty');
      if (empty) empty.style.display = visible === 0 ? '' : 'none';
    });
  }

  /* ---------- Interactive star rating ---------- */
  document.querySelectorAll('.star-rating').forEach(function (widget) {
    var select = widget.querySelector('select');
    if (!select) return;
    select.style.display = 'none';
    var stars = [];
    var starWrap = document.createElement('div');
    starWrap.className = 'star-rating-stars';
    for (var i = 1; i <= 5; i++) {
      var s = document.createElement('span');
      s.textContent = '★';
      s.dataset.value = i;
      s.className = 'star';
      starWrap.appendChild(s);
      stars.push(s);
    }
    widget.appendChild(starWrap);

    function paint(value) {
      stars.forEach(function (s) {
        s.classList.toggle('is-filled', parseInt(s.dataset.value, 10) <= value);
      });
    }
    var current = parseInt(select.value, 10) || 0;
    paint(current);

    stars.forEach(function (s) {
      s.addEventListener('mouseenter', function () { paint(parseInt(s.dataset.value, 10)); });
      s.addEventListener('click', function () {
        current = parseInt(s.dataset.value, 10);
        select.value = current;
        paint(current);
      });
    });
    starWrap.addEventListener('mouseleave', function () { paint(current); });
  });

  /* ---------- Character counters for AI textareas ---------- */
  document.querySelectorAll('[data-counter]').forEach(function (ta) {
    var max = parseInt(ta.getAttribute('data-counter'), 10);
    var counter = document.createElement('div');
    counter.className = 'char-counter';
    ta.insertAdjacentElement('afterend', counter);
    function update() {
      counter.textContent = ta.value.length + (max ? ' / ' + max : '') + ' characters';
    }
    ta.addEventListener('input', update);
    update();
  });

  /* ---------- Password visibility toggle ---------- */
  document.querySelectorAll('.toggle-password').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var input = document.getElementById(btn.getAttribute('data-target'));
      if (!input) return;
      var isHidden = input.type === 'password';
      input.type = isHidden ? 'text' : 'password';
      btn.textContent = isHidden ? 'Hide' : 'Show';
    });
  });

  /* ---------- Auth panel rotating highlights ---------- */
  var authRotator = document.getElementById('auth-rotator');
  if (authRotator) {
    var items = authRotator.querySelectorAll('.auth-highlight');
    var idx = 0;
    setInterval(function () {
      items[idx].classList.remove('is-active');
      idx = (idx + 1) % items.length;
      items[idx].classList.add('is-active');
    }, 3200);
  }

  /* ---------- AI Help Chatbot ---------- */
  (function () {
    var widget = document.getElementById('chatbot-widget');
    if (!widget) return;

    var toggleBtn = document.getElementById('chatbot-toggle');
    var closeBtn = document.getElementById('chatbot-close');
    var form = document.getElementById('chatbot-form');
    var input = document.getElementById('chatbot-input');
    var sendBtn = document.getElementById('chatbot-send');
    var messagesEl = document.getElementById('chatbot-messages');
    var quickReplies = document.getElementById('chatbot-quick-replies');
    var csrfToken = document.querySelector('#chatbot-csrf-form [name=csrfmiddlewaretoken]');

    var history = [];

    function scrollToBottom() {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function addMessage(text, role) {
      var div = document.createElement('div');
      div.className = 'chatbot-msg ' + (role === 'user' ? 'chatbot-msg-user' : 'chatbot-msg-bot');
      div.textContent = text;
      messagesEl.appendChild(div);
      scrollToBottom();
    }

    function showTyping() {
      var div = document.createElement('div');
      div.className = 'chatbot-msg-typing';
      div.id = 'chatbot-typing';
      div.innerHTML = '<span></span><span></span><span></span>';
      messagesEl.appendChild(div);
      scrollToBottom();
    }

    function hideTyping() {
      var el = document.getElementById('chatbot-typing');
      if (el) el.remove();
    }

    function sendMessage(text) {
      text = text.trim();
      if (!text) return;
      addMessage(text, 'user');
      input.value = '';
      sendBtn.disabled = true;
      showTyping();

      fetch('/ai/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken ? csrfToken.value : ''
        },
        body: JSON.stringify({ message: text, history: history })
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          hideTyping();
          var reply = data.reply || "Sorry, I couldn't get a response just now — please try again.";
          addMessage(reply, 'bot');
          history.push({ role: 'user', content: text });
          history.push({ role: 'assistant', content: reply });
        })
        .catch(function () {
          hideTyping();
          addMessage("I'm having trouble connecting right now — please try again in a moment.", 'bot');
        })
        .finally(function () {
          sendBtn.disabled = false;
        });
    }

    toggleBtn.addEventListener('click', function () {
      widget.classList.add('is-open');
      input.focus();
    });
    closeBtn.addEventListener('click', function () {
      widget.classList.remove('is-open');
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      sendMessage(input.value);
    });
    quickReplies.querySelectorAll('.chatbot-chip').forEach(function (chip) {
      chip.addEventListener('click', function () {
        quickReplies.style.display = 'none';
        sendMessage(chip.textContent);
      });
    });
  })();
});
