const api = window.location.origin;

const elements = {
  totalSensores: document.querySelector('#totalSensores'),
  sensoresAtivos: document.querySelector('#sensoresAtivos'),
  totalLeituras: document.querySelector('#totalLeituras'),
  totalAlertas: document.querySelector('#totalAlertas'),
  listaSensores: document.querySelector('#listaSensores'),
  tabelaLeituras: document.querySelector('#tabelaLeituras'),
  leituraSensor: document.querySelector('#leituraSensor'),
  mensagem: document.querySelector('#mensagem'),
  apenasAlertas: document.querySelector('#apenasAlertas'),
  btnAtualizar: document.querySelector('#btnAtualizar'),
  formSensor: document.querySelector('#formSensor'),
  formLeitura: document.querySelector('#formLeitura'),
};

function mostrarMensagem(texto, erro = false) {
  elements.mensagem.textContent = texto;
  elements.mensagem.style.color = erro ? '#fb7185' : '#38bdf8';
  clearTimeout(window.__msgTimer);
  window.__msgTimer = setTimeout(() => {
    elements.mensagem.textContent = '';
  }, 3500);
}

async function request(path, options = {}) {
  const response = await fetch(`${api}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    let detail = 'Erro ao comunicar com a API.';
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }

  return response.json();
}

function formatarData(valor) {
  return new Date(valor).toLocaleString('pt-BR');
}

function statusClass(status) {
  return status === 'NORMAL' ? 'normal' : 'alerta';
}

async function carregarResumo() {
  const resumo = await request('/dashboard/resumo');
  elements.totalSensores.textContent = resumo.total_sensores;
  elements.sensoresAtivos.textContent = resumo.sensores_ativos;
  elements.totalLeituras.textContent = resumo.total_leituras;
  elements.totalAlertas.textContent = resumo.total_alertas;
}

async function carregarSensores() {
  const sensores = await request('/sensores');

  elements.leituraSensor.innerHTML = sensores
    .filter((sensor) => sensor.ativo)
    .map((sensor) => `<option value="${sensor.id}">${sensor.id} - ${sensor.nome}</option>`)
    .join('');

  if (!sensores.length) {
    elements.listaSensores.innerHTML = '<p class="empty">Nenhum sensor cadastrado.</p>';
    return;
  }

  elements.listaSensores.innerHTML = sensores.map((sensor) => `
    <div class="sensor-item">
      <strong>${sensor.nome}</strong>
      <span>ID: ${sensor.id}</span><br />
      <span>Local: ${sensor.localizacao}</span><br />
      <span class="status ${sensor.ativo ? 'normal' : 'alerta'}">${sensor.ativo ? 'ATIVO' : 'INATIVO'}</span>
    </div>
  `).join('');
}

async function carregarLeituras() {
  const path = elements.apenasAlertas.checked
    ? '/leituras/alertas?limit=50'
    : '/leituras?limit=50';

  const leituras = await request(path);

  if (!leituras.length) {
    elements.tabelaLeituras.innerHTML = '<tr><td colspan="6" class="empty">Nenhuma leitura encontrada.</td></tr>';
    return;
  }

  elements.tabelaLeituras.innerHTML = leituras.map((leitura) => `
    <tr>
      <td>${leitura.id}</td>
      <td>${leitura.sensor_id}</td>
      <td>${leitura.temperatura.toFixed(2)} °C</td>
      <td>${leitura.umidade.toFixed(2)} %</td>
      <td><span class="status ${statusClass(leitura.status)}">${leitura.status}</span></td>
      <td>${formatarData(leitura.criado_em)}</td>
    </tr>
  `).join('');
}

async function carregarTudo() {
  try {
    elements.btnAtualizar.disabled = true;
    await Promise.all([carregarResumo(), carregarSensores(), carregarLeituras()]);
  } catch (error) {
    mostrarMensagem(error.message, true);
  } finally {
    elements.btnAtualizar.disabled = false;
  }
}

elements.formSensor.addEventListener('submit', async (event) => {
  event.preventDefault();

  const payload = {
    nome: document.querySelector('#sensorNome').value,
    localizacao: document.querySelector('#sensorLocalizacao').value,
    descricao: document.querySelector('#sensorDescricao').value || null,
  };

  try {
    await request('/sensores', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    elements.formSensor.reset();
    mostrarMensagem('Sensor cadastrado com sucesso.');
    await carregarTudo();
  } catch (error) {
    mostrarMensagem(error.message, true);
  }
});

elements.formLeitura.addEventListener('submit', async (event) => {
  event.preventDefault();

  const payload = {
    sensor_id: Number(elements.leituraSensor.value),
    temperatura: Number(document.querySelector('#temperatura').value),
    umidade: Number(document.querySelector('#umidade').value),
  };

  try {
    await request('/leituras', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    elements.formLeitura.reset();
    mostrarMensagem('Leitura registrada com sucesso.');
    await carregarTudo();
  } catch (error) {
    mostrarMensagem(error.message, true);
  }
});

elements.btnAtualizar.addEventListener('click', carregarTudo);
elements.apenasAlertas.addEventListener('change', carregarLeituras);

carregarTudo();
setInterval(carregarTudo, 10000);
