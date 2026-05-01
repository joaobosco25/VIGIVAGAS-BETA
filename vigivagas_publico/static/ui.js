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
