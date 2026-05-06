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
    document.querySelectorAll('.soft-card,.admin-card,.stat-card,.metric-card,.quick-card,.table-wrap').forEach(function(card){
      card.classList.add('vv-card-ready');
    });
  });
})();

(function(){
  function ready(fn){document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);}
  ready(function(){
    document.querySelectorAll('.table-wrap').forEach(function(wrap){
      if(wrap.dataset.vvLimited === '1') return;
      var table = wrap.querySelector('table.data-table');
      if(!table || !table.querySelector('thead')) return;
      var tbody = table.querySelector('tbody');
      if(!tbody) return;
      var rows = Array.prototype.slice.call(tbody.querySelectorAll(':scope > tr'));
      if(rows.length <= 5) return;
      wrap.dataset.vvLimited = '1';
      var expanded = false;
      function apply(){
        rows.forEach(function(row, index){
          row.classList.toggle('vv-row-hidden', !expanded && index >= 5);
        });
        button.textContent = expanded ? 'Mostrar menos' : 'Mostrar tudo';
        button.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      }
      var holder = document.createElement('div');
      holder.className = 'vv-table-toggle-row';
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn btn-secondary';
      button.setAttribute('aria-expanded','false');
      button.addEventListener('click', function(){
        expanded = !expanded;
        apply();
        if(!expanded){ wrap.scrollIntoView({behavior:'smooth', block:'nearest'}); }
      });
      holder.appendChild(button);
      wrap.insertAdjacentElement('afterend', holder);
      apply();
    });
  });
})();


(function(){
  function ready(fn){document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);}
  ready(function(){
    var mq = window.matchMedia('(max-width: 760px)');
    document.querySelectorAll('.metric-strip').forEach(function(strip){
      if(strip.dataset.vvMobileMetrics === '1') return;
      var cards = Array.prototype.slice.call(strip.querySelectorAll(':scope > .metric-card'));
      if(cards.length <= 2) return;
      strip.dataset.vvMobileMetrics = '1';
      var expanded = false;
      var holder = document.createElement('div');
      holder.className = 'vv-metric-toggle-row';
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'btn btn-secondary';
      button.setAttribute('aria-expanded','false');
      holder.appendChild(button);
      strip.insertAdjacentElement('afterend', holder);
      function apply(){
        var mobile = mq.matches;
        cards.forEach(function(card, index){
          card.classList.toggle('vv-mobile-metric-hidden', mobile && !expanded && index >= 2);
        });
        holder.style.display = mobile ? 'flex' : 'none';
        button.textContent = expanded ? 'Mostrar menos indicadores' : 'Mostrar mais indicadores';
        button.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      }
      button.addEventListener('click', function(){
        expanded = !expanded;
        apply();
        if(!expanded){ strip.scrollIntoView({behavior:'smooth', block:'start'}); }
      });
      if(mq.addEventListener){ mq.addEventListener('change', apply); }
      else if(mq.addListener){ mq.addListener(apply); }
      apply();
    });
  });
})();


// Mantém a seção do painel após filtros e ações, sem script inline (compatível com CSP).
document.querySelectorAll('.preserve-section-form').forEach((form) => {
    form.addEventListener('submit', () => {
        const sectionId = form.dataset.targetSection;
        if (sectionId) sessionStorage.setItem('mauricio_last_section', sectionId);
    });
});

window.addEventListener('load', () => {
    if (window.location.hash) return;
    const sectionId = sessionStorage.getItem('mauricio_last_section');
    if (!sectionId) return;
    const target = document.getElementById(sectionId);
    if (target) setTimeout(() => target.scrollIntoView({ behavior: 'smooth', block: 'start' }), 40);
    sessionStorage.removeItem('mauricio_last_section');
});

// Prioridade 3 — preservar posição/filtros no painel e destacar aviso de exportação limitada.
(function(){
  function ready(fn){document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);}
  ready(function(){
    var key='vigivagas:mauricio:scroll';
    document.querySelectorAll('form').forEach(function(form){
      form.addEventListener('submit', function(){ try{ sessionStorage.setItem(key, String(window.scrollY)); }catch(e){} });
    });
    document.querySelectorAll('a[href*="/exportar/"]').forEach(function(a){
      a.addEventListener('click', function(){ try{ sessionStorage.setItem(key, String(window.scrollY)); }catch(e){} });
      if(!a.dataset.limitedHint){ a.dataset.limitedHint='1'; a.title='A exportação respeita os filtros e o limite atualmente carregado na tela.'; }
    });
    if(location.hash){
      setTimeout(function(){ var el=document.querySelector(location.hash); if(el) el.scrollIntoView({behavior:'smooth', block:'start'}); }, 120);
    } else {
      try{ var y=parseInt(sessionStorage.getItem(key)||'',10); if(!isNaN(y) && y>0) setTimeout(function(){ window.scrollTo({top:y, behavior:'smooth'}); sessionStorage.removeItem(key); }, 120); }catch(e){}
    }
  });
})();
