(function(){
  function ready(fn){document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);}
  ready(function(){
    document.body.classList.add('page-loaded');

    document.querySelectorAll('.site-header').forEach(function(header){
      var wrap = header.querySelector('.header-wrap');
      if(!wrap) return;
      var toggle = header.querySelector('.menu-toggle');
      if(!toggle){
        toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'menu-toggle';
        toggle.setAttribute('aria-label','Abrir menu');
        toggle.setAttribute('aria-expanded','false');
        toggle.innerHTML = '<span></span><span></span><span></span>';
        var brand = wrap.querySelector('.brand');
        if(brand && brand.nextSibling){ wrap.insertBefore(toggle, brand.nextSibling); } else { wrap.appendChild(toggle); }
      }
      toggle.addEventListener('click', function(){
        var open = header.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      header.querySelectorAll('a[href^="#"], .main-nav a').forEach(function(link){
        link.addEventListener('click', function(){
          header.classList.remove('is-open');
          toggle.setAttribute('aria-expanded','false');
        });
      });
    });

    var onScroll = function(){
      document.querySelectorAll('.site-header').forEach(function(header){
        header.classList.toggle('is-scrolled', window.scrollY > 8);
      });
    };
    onScroll();
    window.addEventListener('scroll', onScroll, {passive:true});

    var revealTargets = document.querySelectorAll('.info-card,.access-card,.soft-card,.highlight-panel,.course-box,.login-container,.auth-aside,.stat-card,.admin-card,.vacancy-card,.table-wrap,.form-section');
    revealTargets.forEach(function(el){ el.setAttribute('data-reveal',''); });
    if('IntersectionObserver' in window){
      var observer = new IntersectionObserver(function(entries){
        entries.forEach(function(entry){
          if(entry.isIntersecting){
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },{threshold:.12,rootMargin:'0px 0px -40px 0px'});
      revealTargets.forEach(function(el){ observer.observe(el); });
    } else {
      revealTargets.forEach(function(el){ el.classList.add('is-visible'); });
    }
  });
})();

(function(){
  function ready(fn){document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);}
  ready(function(){
    var key = 'vigivagas_cookie_preference_v2';
    if(localStorage.getItem(key)) return;

    var overlay = document.createElement('div');
    overlay.className = 'cookie-consent-overlay';
    overlay.setAttribute('role','dialog');
    overlay.setAttribute('aria-modal','true');
    overlay.setAttribute('aria-labelledby','cookie-consent-title');
    overlay.innerHTML = ''+
      '<div class="cookie-consent-card">'+
        '<div class="cookie-consent-icon" aria-hidden="true">✓</div>'+
        '<div class="cookie-consent-content">'+
          '<span class="section-kicker">Privacidade e cookies</span>'+
          '<h2 id="cookie-consent-title">Controle de cookies do VigiVagas</h2>'+
          '<p>Usamos cookies necessários para login, segurança e funcionamento da plataforma. Cookies opcionais podem ajudar a melhorar a experiência e entender o uso do site. Você pode aceitar ou recusar cookies opcionais agora.</p>'+
          '<div class="cookie-consent-list">'+
            '<span>Essenciais: sempre ativos</span>'+
            '<span>Experiência e métricas: opcionais</span>'+
          '</div>'+
        '</div>'+
        '<div class="cookie-consent-actions">'+
          '<button type="button" class="btn btn-primary" data-cookie-choice="accepted">Aceitar cookies</button>'+
          '<button type="button" class="btn btn-secondary" data-cookie-choice="rejected">Recusar opcionais</button>'+
        '</div>'+
        '<p class="cookie-consent-links"><a href="/privacidade">Política de Privacidade</a> · <a href="/termos">Termos de Uso</a></p>'+
      '</div>';

    document.body.appendChild(overlay);
    document.body.classList.add('cookie-modal-open');

    overlay.querySelectorAll('[data-cookie-choice]').forEach(function(btn){
      btn.addEventListener('click', function(){
        localStorage.setItem(key, JSON.stringify({choice: btn.getAttribute('data-cookie-choice'), at: new Date().toISOString()}));
        overlay.classList.add('is-leaving');
        document.body.classList.remove('cookie-modal-open');
        setTimeout(function(){ overlay.remove(); }, 180);
      });
    });
  });
})();
