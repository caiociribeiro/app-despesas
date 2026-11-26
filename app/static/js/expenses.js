const $ = selector => document.querySelector(selector);
const money = cents => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100);
const state = { offset: 0, limit: 200, rows: [], hasMore: false, categories: [] };

async function request(url, options = {}) {
  const response = await fetch(url, { headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
  if (!response.ok) {
    let message = 'Não foi possível concluir a operação.';
    try { message = (await response.json()).detail || message; } catch (_) {}
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}
function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem('appdespesas-theme', theme);
}
function selectedValues(select) {
  return [...select.selectedOptions].map(option => option.value).filter(Boolean);
}
function addOptions(select, rows, label = 'name') {
  select.replaceChildren(...rows.map(row => new Option(row[label], row.id)));
}
function dateToInput(date) {
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
}
function buildQuery() {
  const form = new FormData($('#filters-form'));
  const params = new URLSearchParams();
  for (const key of ['search','start_date','end_date']) {
    const value = String(form.get(key) || '').trim();
    if (value) params.set(key, value);
  }
  const multiFilters = [
    ['#filter-category', 'category_id'],
    ['#filter-subcategory', 'subcategory_id'],
    ['#filter-tag', 'tag_id'],
    ['#filter-establishment', 'establishment_id'],
    ['#filter-payment', 'payment_method_id'],
  ];
  for (const [selector, param] of multiFilters) {
    selectedValues($(selector)).forEach(value => params.append(param, value));
  }
  for (const [field, param] of [['min_amount','min_cents'],['max_amount','max_cents']]) {
    const value = form.get(field);
    if (value !== '') {
      const cents = Math.round(Number(value) * 100);
      if (!Number.isSafeInteger(cents) || cents < 0) throw new Error('Informe uma faixa de valores válida.');
      params.set(param, String(cents));
    }
  }
  params.set('limit', String(state.limit));
  params.set('offset', String(state.offset));
  return params;
}
function createExpenseRow(item) {
  const row = document.createElement('article');
  row.className = 'expense-row history-expense-row';
  const marker = document.createElement('span');
  marker.className = 'category-marker';
  marker.style.backgroundColor = item.category_color;
  const details = document.createElement('div');
  details.className = 'expense-details';
  const title = document.createElement('strong');
  title.textContent = item.description;
  const subtitle = document.createElement('span');
  subtitle.textContent = `${item.category} / ${item.subcategory} · ${item.establishment} · ${item.payment_method} · ${new Date(`${item.expense_date}T12:00:00`).toLocaleDateString('pt-BR')}`;
  details.append(title, subtitle);
  if (item.tags.length) {
    const tags = document.createElement('span');
    tags.className = 'expense-tags';
    tags.textContent = item.tags.map(tag => `#${tag.name}`).join('  ');
    details.append(tags);
  }
  if (item.notes) {
    const notes = document.createElement('span');
    notes.className = 'expense-notes';
    notes.textContent = item.notes;
    details.append(notes);
  }
  const amount = document.createElement('strong');
  amount.className = 'expense-amount';
  amount.textContent = money(item.amount_cents);
  const actions = document.createElement('div');
  actions.className = 'expense-actions';
  const remove = document.createElement('button');
  remove.type = 'button';
  remove.className = 'text-button danger-button';
  remove.textContent = 'Excluir';
  remove.addEventListener('click', async () => {
    if (!confirm(`Excluir a despesa "${item.description}"? Esta ação não pode ser desfeita.`)) return;
    remove.disabled = true;
    try {
      await request(`/api/expenses/${item.id}`, { method: 'DELETE' });
      await loadExpenses(true);
    } catch (error) {
      alert(error.message);
      remove.disabled = false;
    }
  });
  actions.append(remove);
  row.append(marker, details, amount, actions);
  return row;
}
function renderRows(append = false) {
  const container = $('#expenses-list');
  if (!append) container.replaceChildren();
  if (!state.rows.length && !append) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.innerHTML = '<strong>Nenhuma despesa encontrada</strong><span>Tente alterar os filtros ou registre uma nova despesa.</span>';
    container.append(empty);
  } else {
    state.rows.forEach(item => container.append(createExpenseRow(item)));
  }
  $('#results-total').textContent = money(state.rows.reduce((sum, item) => sum + item.amount_cents, 0));
  $('#results-count').textContent = state.rows.length.toLocaleString('pt-BR');
  $('#results-caption').textContent = state.hasMore ? `Exibindo ${state.rows.length} despesas. Existem mais resultados.` : `${state.rows.length} despesa(s) encontrada(s).`;
  $('#load-more').hidden = !state.hasMore;
}
async function loadExpenses(reset = false) {
  const error = $('#page-error');
  error.hidden = true;
  if (reset) { state.offset = 0; state.rows = []; }
  const params = buildQuery();
  try {
    const data = await request(`/api/expenses?${params}`);
    state.hasMore = data.length === state.limit;
    state.rows = reset ? data : [...state.rows, ...data];
    state.offset = state.rows.length;
    renderRows(reset ? false : true);
  } catch (exception) {
    error.textContent = exception.message;
    error.hidden = false;
  }
}
async function initializeFilters() {
  const [categories, tags, establishments, methods] = await Promise.all([
    request('/api/categories'), request('/api/tags'), request('/api/establishments'), request('/api/payment-methods')
  ]);
  state.categories = categories;
  addOptions($('#filter-category'), categories);
  addOptions($('#filter-tag'), tags);
  addOptions($('#filter-establishment'), establishments);
  addOptions($('#filter-payment'), methods.filter(item => item.is_active));
  refreshSubcategories();
}
function refreshSubcategories() {
  const chosen = selectedValues($('#filter-category'));
  const subs = state.categories.flatMap(category => category.subcategories
    .filter(sub => !chosen.length || chosen.includes(category.id))
    .map(sub => ({ id: sub.id, name: `${category.name} — ${sub.name}` })));
  const select = $('#filter-subcategory');
  const previous = new Set(selectedValues(select));
  addOptions(select, subs);
  [...select.options].forEach(option => { option.selected = previous.has(option.value); });
}
$('#theme-toggle').addEventListener('click', () => setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'));
$('#filter-category').addEventListener('change', refreshSubcategories);
$('#filters-form').addEventListener('submit', event => { event.preventDefault(); loadExpenses(true); });
$('#clear-filters').addEventListener('click', () => {
  $('#filters-form').reset();
  refreshSubcategories();
  loadExpenses(true);
});
$('#load-more').addEventListener('click', () => loadExpenses(false));
(async function init() {
  const saved = localStorage.getItem('appdespesas-theme');
  setTheme(saved || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
  const now = new Date();
  $('#filters-form').elements.start_date.value = dateToInput(new Date(now.getFullYear(), now.getMonth(), 1));
  $('#filters-form').elements.end_date.value = dateToInput(new Date(now.getFullYear(), now.getMonth()+1, 0));
  try {
    await initializeFilters();
    await loadExpenses(true);
  } catch (error) {
    $('#page-error').textContent = error.message;
    $('#page-error').hidden = false;
  }
})();
