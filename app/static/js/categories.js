const $ = selector => document.querySelector(selector);
const categoryDialog = $('#category-dialog');
const categoryForm = $('#category-form');
const editDialog = $('#edit-category-dialog');
const editForm = $('#edit-category-form');
const subcategoryDialog = $('#subcategory-dialog');
const subcategoryForm = $('#subcategory-form');
let categories = [];
let editingCategoryId = null;
let selectedCategoryId = null;

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem('appdespesas-theme', theme);
}
$('#theme-toggle').addEventListener('click', () => setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'));
setTheme(localStorage.getItem('appdespesas-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));

async function request(url, options = {}) {
  const response = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) {
    let message = 'Não foi possível concluir a operação.';
    try { message = (await response.json()).detail || message; } catch (_) {}
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}
function showError(selector, message) {
  const element = $(selector);
  element.textContent = message;
  element.hidden = false;
}
function hideError(selector) { $(selector).hidden = true; }

function renderCategories() {
  const container = $('#categories-list');
  if (!categories.length) {
    container.innerHTML = '<div class="empty-state"><span class="empty-icon">▦</span><strong>Nenhuma categoria cadastrada</strong><span>Crie sua primeira categoria para começar a organizar os gastos.</span></div>';
    return;
  }
  container.replaceChildren(...categories.map(category => {
    const card = document.createElement('article');
    card.className = 'category-card';
    const header = document.createElement('div');
    header.className = 'category-card-header';
    const identity = document.createElement('div');
    identity.className = 'category-identity';
    const swatch = document.createElement('span');
    swatch.className = 'category-swatch';
    swatch.style.backgroundColor = category.color;
    const title = document.createElement('div');
    title.className = 'category-title';
    const name = document.createElement('h3');
    name.textContent = category.name;
    const count = document.createElement('span');
    count.className = 'muted';
    count.textContent = `${category.subcategories.length} ${category.subcategories.length === 1 ? 'subcategoria' : 'subcategorias'}`;
    title.append(name, count);
    identity.append(swatch, title);
    const actions = document.createElement('div');
    actions.className = 'category-actions';
    const edit = document.createElement('button');
    edit.className = 'secondary-button compact-button';
    edit.type = 'button';
    edit.textContent = 'Editar';
    edit.addEventListener('click', () => openEditCategory(category));
    const add = document.createElement('button');
    add.className = 'secondary-button compact-button';
    add.type = 'button';
    add.textContent = '+ Subcategoria';
    add.addEventListener('click', () => openSubcategory(category));
    actions.append(edit, add);
    header.append(identity, actions);
    const list = document.createElement('div');
    list.className = 'subcategory-list';
    category.subcategories.forEach(subcategory => {
      const row = document.createElement('div');
      row.className = 'subcategory-row';
      const label = document.createElement('span');
      label.textContent = subcategory.name;
      const inherited = document.createElement('span');
      inherited.className = 'subcategory-color';
      inherited.style.backgroundColor = category.color;
      inherited.title = `Cor herdada: ${category.color}`;
      const remove = document.createElement('button');
      remove.className = 'text-button danger-button';
      remove.type = 'button';
      remove.textContent = 'Remover';
      remove.addEventListener('click', () => removeSubcategory(category, subcategory));
      row.append(label, inherited, remove);
      list.append(row);
    });
    card.append(header, list);
    return card;
  }));
}
async function loadCategories() {
  categories = await request('/api/categories');
  renderCategories();
}
function openEditCategory(category) {
  editingCategoryId = category.id;
  editForm.elements.name.value = category.name;
  editForm.elements.color.value = category.color;
  hideError('#edit-category-error');
  editDialog.showModal();
}
function openSubcategory(category) {
  selectedCategoryId = category.id;
  subcategoryForm.reset();
  $('#subcategory-parent').textContent = `Categoria: ${category.name}`;
  hideError('#subcategory-error');
  subcategoryDialog.showModal();
}
async function removeSubcategory(category, subcategory) {
  if (!confirm(`Remover a subcategoria "${subcategory.name}"?`)) return;
  try {
    await request(`/api/categories/subcategories/${subcategory.id}`, { method: 'DELETE' });
    await loadCategories();
  } catch (error) {
    showError('#page-error', error.message);
  }
}
$('#open-category-form').addEventListener('click', () => {
  categoryForm.reset();
  $('#category-color').value = '#64748B';
  hideError('#category-form-error');
  categoryDialog.showModal();
});
$('#close-category-form').addEventListener('click', () => categoryDialog.close());
$('#cancel-category-form').addEventListener('click', () => categoryDialog.close());
$('#close-edit-category').addEventListener('click', () => editDialog.close());
$('#cancel-edit-category').addEventListener('click', () => editDialog.close());
$('#close-subcategory').addEventListener('click', () => subcategoryDialog.close());
$('#cancel-subcategory').addEventListener('click', () => subcategoryDialog.close());

categoryForm.addEventListener('submit', async event => {
  event.preventDefault();
  const button = $('#save-category');
  button.disabled = true;
  hideError('#category-form-error');
  try {
    const data = new FormData(categoryForm);
    await request('/api/categories', { method: 'POST', body: JSON.stringify({
      name: data.get('name').trim(), color: data.get('color'),
      initial_subcategory: data.get('initial_subcategory').trim()
    })});
    categoryDialog.close();
    await loadCategories();
  } catch (error) {
    showError('#category-form-error', error.message);
  } finally {
    button.disabled = false;
  }
});
editForm.addEventListener('submit', async event => {
  event.preventDefault();
  hideError('#edit-category-error');
  try {
    const data = new FormData(editForm);
    await request(`/api/categories/${editingCategoryId}`, { method: 'PATCH', body: JSON.stringify({
      name: data.get('name').trim(), color: data.get('color')
    })});
    editDialog.close();
    await loadCategories();
  } catch (error) {
    showError('#edit-category-error', error.message);
  }
});
subcategoryForm.addEventListener('submit', async event => {
  event.preventDefault();
  hideError('#subcategory-error');
  try {
    const data = new FormData(subcategoryForm);
    await request(`/api/categories/${selectedCategoryId}/subcategories`, {
      method: 'POST', body: JSON.stringify({ name: data.get('name').trim() })
    });
    subcategoryDialog.close();
    await loadCategories();
  } catch (error) {
    showError('#subcategory-error', error.message);
  }
});
loadCategories().catch(error => showError('#page-error', `${error.message} Verifique a conexão com o banco.`));
