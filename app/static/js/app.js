const money = cents => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100);
const $ = selector => document.querySelector(selector);
const dialog = $('#expense-dialog');
const form = $('#expense-form');
let categories = [];
let establishments = [];

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem('appdespesas-theme', theme);
}

function showPageError(message) {
  const element = $('#page-error');
  element.textContent = message;
  element.hidden = false;
}

async function request(url, options = {}) {
  const response = await fetch(url, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
  if (!response.ok) {
    let message = 'Não foi possível concluir a operação.';
    try { message = (await response.json()).detail || message; } catch (_) {}
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

function renderExpenses(expenses) {
  const container = $('#recent-expenses');
  if (!expenses.length) {
    container.innerHTML = '<div class="empty-state"><span class="empty-icon">▤</span><strong>Nenhuma despesa neste mês</strong><span>Adicione sua primeira despesa para começar.</span></div>';
    return;
  }
  container.replaceChildren(...expenses.map(item => {
    const row = document.createElement('article');
    row.className = 'expense-row';
    const marker = document.createElement('span');
    marker.className = 'category-marker';
    marker.style.backgroundColor = item.category_color;
    const details = document.createElement('div');
    details.className = 'expense-details';
    const title = document.createElement('strong');
    title.textContent = item.description;
    const subtitle = document.createElement('span');
    subtitle.textContent = `${item.category} / ${item.subcategory} · ${item.establishment} · ${new Date(`${item.expense_date}T12:00:00`).toLocaleDateString('pt-BR')}`;
    details.append(title, subtitle);
    const amount = document.createElement('strong');
    amount.className = 'expense-amount';
    amount.textContent = money(item.amount_cents);
    row.append(marker, details, amount);
    return row;
  }));
}

async function loadDashboard() {
  const summary = await request('/api/dashboard/monthly');
  $('#month-total').textContent = money(summary.total_cents);
  renderExpenses(summary.recent_expenses);
}

async function loadFormOptions() {
  await Promise.all([
    request('/api/categories').then(data => { categories = data; }),
    request('/api/establishments').then(data => { establishments = data; renderEstablishmentOptions(); }),
    request('/api/payment-methods').then(methods => {
      const select = $('#payment-method-select');
      select.replaceChildren(new Option('Selecione uma forma de pagamento', ''));
      methods.forEach(method => select.add(new Option(method.name, method.id)));
    })
  ]);
  const select = $('#category-select');
  select.replaceChildren(new Option('Selecione uma categoria', ''));
  categories.forEach(category => select.add(new Option(category.name, category.id)));
  $('#subcategory-select').replaceChildren(new Option('Selecione uma subcategoria', ''));
  $('#subcategory-select').disabled = true;
}

function renderEstablishmentOptions() {
  const list = $('#establishment-options');
  list.replaceChildren(...establishments.map(item => {
    const option = document.createElement('option');
    option.value = item.name;
    return option;
  }));
}

async function getOrCreateEstablishment(name) {
  const normalized = name.trim().toLocaleLowerCase('pt-BR');
  if (!normalized) throw new Error('Informe o estabelecimento.');
  const existing = establishments.find(item => item.name.trim().toLocaleLowerCase('pt-BR') === normalized);
  if (existing) return existing.id;
  const created = await request('/api/establishments', {
    method: 'POST',
    body: JSON.stringify({ name: name.trim() })
  });
  establishments.push(created);
  renderEstablishmentOptions();
  return created.id;
}

function openDialog() {
  form.reset();
  $('#form-error').hidden = true;
  $('#subcategory-select').replaceChildren(new Option('Selecione uma subcategoria', ''));
  $('#subcategory-select').disabled = true;
  form.elements.expense_date.value = new Date().toISOString().slice(0, 10);
  dialog.showModal();
}

$('#theme-toggle').addEventListener('click', () => {
  setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
});
$('#open-expense-form').addEventListener('click', openDialog);
$('#close-expense-form').addEventListener('click', () => dialog.close());
$('#cancel-expense-form').addEventListener('click', () => dialog.close());
$('#category-select').addEventListener('change', event => {
  const category = categories.find(item => item.id === event.target.value);
  const select = $('#subcategory-select');
  select.replaceChildren(new Option('Selecione uma subcategoria', ''));
  (category?.subcategories || []).forEach(sub => select.add(new Option(sub.name, sub.id)));
  select.disabled = !category?.subcategories.length;
});

form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = $('#save-expense');
  const error = $('#form-error');
  error.hidden = true;
  button.disabled = true;
  try {
    const data = new FormData(form);
    const amount = Math.round(Number(data.get('amount')) * 100);
    if (!Number.isSafeInteger(amount) || amount <= 0) throw new Error('Informe um valor válido.');
    const establishmentId = await getOrCreateEstablishment(data.get('establishment_name'));
    await request('/api/expenses', {
      method: 'POST',
      body: JSON.stringify({
        description: data.get('description').trim(), amount_cents: amount,
        expense_date: data.get('expense_date'), subcategory_id: data.get('subcategory_id'),
        establishment_id: establishmentId,
        payment_method_id: data.get('payment_method_id'), notes: data.get('notes') || null
      })
    });
    dialog.close();
    await loadDashboard();
  } catch (exception) {
    error.textContent = exception.message;
    error.hidden = false;
  } finally {
    button.disabled = false;
  }
});

(async function initialize() {
  const savedTheme = localStorage.getItem('appdespesas-theme');
  setTheme(savedTheme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
  $('#current-month').textContent = new Intl.DateTimeFormat('pt-BR', { month: 'long', year: 'numeric' }).format(new Date());
  try {
    await Promise.all([loadDashboard(), loadFormOptions()]);
  } catch (error) {
    showPageError(`${error.message} Verifique a conexão com o banco e tente novamente.`);
    $('#recent-expenses').innerHTML = '<div class="empty-state">Não foi possível carregar as despesas.</div>';
  }
})();
