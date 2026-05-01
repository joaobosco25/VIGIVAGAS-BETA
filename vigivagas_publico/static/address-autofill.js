(function () {
  function digitsOnly(value) {
    return (value || '').replace(/\D/g, '');
  }

  function applyCepMask(input) {
    if (!input) return;
    input.addEventListener('input', function () {
      const raw = digitsOnly(input.value).slice(0, 8);
      input.value = raw.length > 5 ? raw.slice(0, 5) + '-' + raw.slice(5) : raw;
    });
  }

  function setStatus(el, message, tone) {
    if (!el) return;
    el.textContent = message || '';
    el.dataset.tone = tone || 'neutral';
  }

  function setupAddressForm(config) {
    const cep = document.getElementById(config.cepId);
    const endereco = document.getElementById(config.enderecoId);
    const cidade = document.getElementById(config.cidadeId);
    const estado = document.getElementById(config.estadoId);
    const status = document.getElementById(config.statusId);
    if (!cep || !endereco || !cidade || !estado) return;

    applyCepMask(cep);

    async function buscarCep() {
      const raw = digitsOnly(cep.value);
      if (raw.length !== 8) {
        setStatus(status, 'Digite um CEP com 8 dígitos para preencher o endereço automaticamente.', 'neutral');
        return;
      }

      setStatus(status, 'Buscando endereço pelo CEP...', 'info');
      try {
        const response = await fetch('https://viacep.com.br/ws/' + raw + '/json/');
        const data = await response.json();
        if (data.erro) {
          setStatus(status, 'CEP não encontrado. Revise o número ou preencha os campos manualmente.', 'error');
          return;
        }

        const partesEndereco = [data.logradouro, data.bairro].filter(Boolean);
        if (!endereco.value.trim()) endereco.value = partesEndereco.join(', ');
        if (!cidade.value.trim()) cidade.value = data.localidade || '';
        if (!estado.value.trim()) estado.value = data.uf || '';

        setStatus(status, 'Endereço localizado. Confira número e complemento antes de enviar.', 'success');
      } catch (error) {
        setStatus(status, 'Não foi possível consultar o CEP agora. Você pode preencher manualmente.', 'error');
      }
    }

    cep.addEventListener('blur', buscarCep);
    cep.addEventListener('change', buscarCep);
  }

  document.addEventListener('DOMContentLoaded', function () {
    setupAddressForm({
      cepId: 'cep',
      enderecoId: 'endereco',
      cidadeId: 'cidade',
      estadoId: 'estado',
      statusId: 'cep-status'
    });
  });
})();
