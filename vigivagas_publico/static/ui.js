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
    var key = 'vigivagas_cookie_preference_v3';
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



// Cadastro vigilante: exibe campos de formação/reciclagem sem script inline (CSP segura).
(function () {
    const possuiCfv = document.getElementById('possui_cfv');
    if (!possuiCfv) return;
    const instituicaoWrapper = document.getElementById('instituicao-wrapper');
    const instituicaoInput = document.getElementById('instituicao_formacao');
    const reciclagemDataWrapper = document.getElementById('reciclagem-data-wrapper');
    const reciclagemCursoWrapper = document.getElementById('reciclagem-curso-wrapper');
    const reciclagemDataInput = document.getElementById('data_ultima_reciclagem');
    const reciclagemCursoInput = document.getElementById('curso_ultima_reciclagem');

    function toggleInstituicao() {
        const show = possuiCfv.value === 'SIM';
        if (instituicaoWrapper) instituicaoWrapper.style.display = show ? 'block' : 'none';
        if (instituicaoInput) { instituicaoInput.required = show; if (!show) instituicaoInput.value = ''; }
        if (reciclagemDataWrapper) reciclagemDataWrapper.style.display = show ? 'block' : 'none';
        if (reciclagemCursoWrapper) reciclagemCursoWrapper.style.display = show ? 'block' : 'none';
        if (reciclagemDataInput) { reciclagemDataInput.required = show; if (!show) reciclagemDataInput.value = ''; }
        if (reciclagemCursoInput) { reciclagemCursoInput.required = show; if (!show) reciclagemCursoInput.value = ''; }
    }

    possuiCfv.addEventListener('change', toggleInstituicao);
    toggleInstituicao();
})();

// Confirmações sem atributo onsubmit inline.
document.querySelectorAll('[data-confirm-message]').forEach((form) => {
    form.addEventListener('submit', (event) => {
        const message = form.getAttribute('data-confirm-message');
        if (message && !window.confirm(message)) event.preventDefault();
    });
});

// Prioridade 3 — UX: máscaras, validação em tempo real, resumo de erros e preservação de rascunho.
(function(){
  function ready(fn){document.readyState !== 'loading' ? fn() : document.addEventListener('DOMContentLoaded', fn);}
  function onlyDigits(v){ return (v || '').replace(/\D/g, ''); }
  function maskCpf(v){ v=onlyDigits(v).slice(0,11); return v.replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d{1,2})$/,'$1-$2'); }
  function maskCnpj(v){ v=onlyDigits(v).slice(0,14); return v.replace(/(\d{2})(\d)/,'$1.$2').replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d)/,'$1/$2').replace(/(\d{4})(\d{1,2})$/,'$1-$2'); }
  function maskCep(v){ v=onlyDigits(v).slice(0,8); return v.replace(/(\d{5})(\d{1,3})$/,'$1-$2'); }
  function maskPhone(v){
    v=onlyDigits(v).slice(0,11);
    if(v.length <= 10) return v.replace(/(\d{2})(\d)/,'($1) $2').replace(/(\d{4})(\d{1,4})$/,'$1-$2');
    return v.replace(/(\d{2})(\d)/,'($1) $2').replace(/(\d{5})(\d{1,4})$/,'$1-$2');
  }
  function isValidCpf(cpf){
    cpf=onlyDigits(cpf); if(cpf.length!==11 || /^(\d)\1+$/.test(cpf)) return false;
    var sum=0, rest; for(var i=1;i<=9;i++) sum += parseInt(cpf.substring(i-1,i),10)*(11-i);
    rest=(sum*10)%11; if(rest===10||rest===11) rest=0; if(rest!==parseInt(cpf.substring(9,10),10)) return false;
    sum=0; for(i=1;i<=10;i++) sum += parseInt(cpf.substring(i-1,i),10)*(12-i);
    rest=(sum*10)%11; if(rest===10||rest===11) rest=0; return rest===parseInt(cpf.substring(10,11),10);
  }
  function isValidCnpj(cnpj){
    cnpj=onlyDigits(cnpj); if(cnpj.length!==14 || /^(\d)\1+$/.test(cnpj)) return false;
    var size=12, nums=cnpj.substring(0,size), digits=cnpj.substring(size), sum=0, pos=size-7;
    for(var i=size;i>=1;i--){ sum += parseInt(nums.charAt(size-i),10)*pos--; if(pos<2) pos=9; }
    var result=sum%11<2?0:11-sum%11; if(result!==parseInt(digits.charAt(0),10)) return false;
    size=13; nums=cnpj.substring(0,size); sum=0; pos=size-7;
    for(i=size;i>=1;i--){ sum += parseInt(nums.charAt(size-i),10)*pos--; if(pos<2) pos=9; }
    result=sum%11<2?0:11-sum%11; return result===parseInt(digits.charAt(1),10);
  }
  function setFieldError(input, message){
    if(!input) return;
    var group=input.closest('.form-group') || input.closest('label') || input.parentElement;
    if(!group) return;
    group.classList.toggle('field-invalid', !!message);
    group.classList.toggle('field-valid', !message && input.value.trim().length>0 && input.checkValidity());
    var id=input.id || input.name;
    var err=group.querySelector('.field-error[data-for="'+id+'"]');
    if(message && !err){ err=document.createElement('small'); err.className='field-error'; err.dataset.for=id; group.appendChild(err); }
    if(err){ err.textContent=message || ''; err.style.display=message?'block':'none'; }
    if(message){ input.setAttribute('aria-invalid','true'); } else { input.removeAttribute('aria-invalid'); }
  }
  function validationMessage(input){
    var name=input.name;
    if(input.required && !String(input.value || '').trim()) return 'Campo obrigatório.';
    if(name==='email' && input.value && !input.checkValidity()) return 'Informe um e-mail válido.';
    if(name==='cpf' && input.value && !isValidCpf(input.value)) return 'CPF inválido.';
    if(name==='cnpj' && input.value && !isValidCnpj(input.value)) return 'CNPJ inválido.';
    if(name==='telefone' && input.value && onlyDigits(input.value).length < 10) return 'Telefone inválido. Informe DDD e número.';
    if(name==='cep' && input.value && onlyDigits(input.value).length !== 8) return 'CEP inválido. Use 8 dígitos.';
    if(name==='estado' && input.value && !/^[A-Za-z]{2}$/.test(input.value.trim())) return 'UF deve ter 2 letras.';
    if(name==='confirm_password'){
      var pw=input.form && input.form.querySelector('[name="password"]');
      if(pw && input.value && pw.value !== input.value) return 'As senhas não conferem.';
    }
    if(name==='password' && input.value && input.value.length < 10) return 'Senha deve ter pelo menos 10 caracteres.';
    return '';
  }
  ready(function(){
    document.querySelectorAll('form[data-vv-validate]').forEach(function(form){
      var draftKey=form.getAttribute('data-draft-key');
      if(draftKey){
        try{
          var saved=JSON.parse(sessionStorage.getItem(draftKey) || '{}');
          Object.keys(saved).forEach(function(name){
            var el=form.elements[name];
            if(el && !el.value && el.type !== 'password' && el.type !== 'hidden') el.value=saved[name];
          });
        }catch(e){}
        form.addEventListener('input', function(){
          var data={};
          Array.prototype.forEach.call(form.elements, function(el){
            if(!el.name || el.type==='password' || el.type==='hidden') return;
            if(el.type==='checkbox') data[el.name]=el.checked ? el.value : '';
            else data[el.name]=el.value;
          });
          try{ sessionStorage.setItem(draftKey, JSON.stringify(data)); }catch(e){}
        });
      }
      form.querySelectorAll('[data-mask]').forEach(function(input){
        input.addEventListener('input', function(){
          var m=input.dataset.mask;
          if(m==='cpf') input.value=maskCpf(input.value);
          if(m==='cnpj') input.value=maskCnpj(input.value);
          if(m==='cep') input.value=maskCep(input.value);
          if(m==='telefone') input.value=maskPhone(input.value);
        });
        input.dispatchEvent(new Event('input'));
      });
      var fields=form.querySelectorAll('input, select, textarea');
      fields.forEach(function(input){
        if(input.type==='hidden') return;
        ['blur','change','input'].forEach(function(ev){ input.addEventListener(ev, function(){ setFieldError(input, validationMessage(input)); }); });
      });
      form.addEventListener('submit', function(event){
        var errors=[];
        fields.forEach(function(input){
          if(input.type==='hidden') return;
          var msg=validationMessage(input);
          setFieldError(input,msg);
          if(msg) errors.push({input:input,msg:msg});
        });
        var summary=form.querySelector('[data-client-error-summary]');
        if(!summary){ summary=document.createElement('div'); summary.className='form-error-summary'; summary.setAttribute('role','alert'); summary.setAttribute('tabindex','-1'); summary.dataset.clientErrorSummary='1'; form.insertBefore(summary, form.firstElementChild.nextElementSibling); }
        if(errors.length){
          event.preventDefault();
          summary.innerHTML='<strong>Corrija os campos abaixo antes de enviar.</strong><ul>'+errors.slice(0,6).map(function(e){return '<li>'+e.msg+'</li>';}).join('')+'</ul>';
          errors[0].input.focus({preventScroll:true});
          errors[0].input.scrollIntoView({behavior:'smooth', block:'center'});
          summary.focus({preventScroll:true});
        } else {
          summary.innerHTML='';
          if(draftKey) { try{ sessionStorage.removeItem(draftKey); }catch(e){} }
        }
      });
      var first=form.querySelector('[data-first-error-field]');
      if(first && first.value){
        var target=form.querySelector('[name="'+first.value+'"]');
        if(target){ setTimeout(function(){ target.focus(); target.scrollIntoView({behavior:'smooth', block:'center'}); }, 120); }
      }
      var summary=form.querySelector('[data-error-summary]');
      if(summary){ setTimeout(function(){ summary.focus(); }, 80); }
    });
  });
})();
