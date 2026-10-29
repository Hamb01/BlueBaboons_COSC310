const filters = document.querySelector('#filters');
const restaurantList = document.querySelector('#restaurants');
const details = document.querySelector('#details');
const notice = document.querySelector('#notice');
const editor = document.querySelector('#editor');
const restaurantForm = document.querySelector('#restaurant-form');
const menuEditor = document.querySelector('#menu-editor');
const menuItemForm = document.querySelector('#menu-item-form');
let editingId = null;
let menuRestaurantId = null;
let listRequest = 0;
let detailRequest = 0;

// Use textContent for API data so restaurant names are always displayed as text.
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new Error('Cannot reach the server. Check your connection and try again.');
  }
  if (!response.ok) {
    let message = `Request failed (${response.status}). Please try again.`;
    try {
      const error = await response.json();
      if (typeof error.detail === 'string') message = error.detail;
      if (Array.isArray(error.detail)) {
        message = error.detail.map(item => `${item.loc.slice(1).join('.')}: ${item.msg}`).join('; ');
      }
    } catch { /* Keep the default message for a non-JSON response. */ }
    throw new Error(message);
  }
  return response.json();
}

function statusBadge(isOpen) {
  return element('span', isOpen ? 'Open' : 'Closed', isOpen ? 'badge' : 'badge closed');
}

async function loadRestaurants() {
  const currentRequest = ++listRequest;
  ++detailRequest;
  details.replaceChildren(element('p', 'Select a restaurant to explore its details and menu.', 'empty'));
  restaurantList.replaceChildren();
  document.querySelector('#count').textContent = '';
  notice.className = '';
  notice.textContent = 'Loading restaurants…';
  const params = new URLSearchParams();
  for (const [name, value] of new FormData(filters)) {
    if (value.trim() !== '') params.set(name, value.trim());
  }
  try {
    const restaurants = await request(`/restaurants?${params}`);
    if (currentRequest !== listRequest) return;
    notice.textContent = '';
    document.querySelector('#count').textContent = `${restaurants.length} found`;
    if (restaurants.length === 0) {
      restaurantList.append(element('p', 'No restaurants match. Try clearing your filters.', 'empty'));
    }
    for (const restaurant of restaurants) {
      const card = element('button', undefined, 'restaurant-card');
      card.type = 'button';
      card.dataset.id = restaurant.id;
      card.setAttribute('aria-pressed', 'false');
      card.append(element('strong', restaurant.name),
        element('small', `${restaurant.cuisine} · ${restaurant.location}`), statusBadge(restaurant.isOpen));
      card.addEventListener('click', () => showRestaurant(restaurant.id));
      restaurantList.append(card);
    }
  } catch (error) {
    if (currentRequest !== listRequest) return;
    notice.className = 'error';
    notice.textContent = error.message;
  }
}

async function showRestaurant(id) {
  const currentRequest = ++detailRequest;
  details.replaceChildren(element('p', 'Loading restaurant…'));
  for (const card of restaurantList.querySelectorAll('button')) {
    card.setAttribute('aria-pressed', String(card.dataset.id === id));
  }
  const path = `/restaurants/${encodeURIComponent(id)}`;
  try {
    const restaurant = await request(path);
    if (currentRequest !== detailRequest) return;
    const heading = element('div', undefined, 'section-heading');
    const edit = element('button', 'Edit restaurant', 'secondary');
    edit.type = 'button';
    edit.addEventListener('click', () => openEditor(restaurant));
    heading.append(element('h2', restaurant.name), edit);
    const facts = element('dl', undefined, 'facts');
    for (const [label, value] of [['Cuisine', restaurant.cuisine], ['Location', restaurant.location], ['Opening hours', restaurant.opening_hours]]) {
      const fact = element('div');
      fact.append(element('dt', label), element('dd', value));
      facts.append(fact);
    }
    const menu = element('div');
    menu.append(element('p', 'Loading menu…'));
    const menuHeading = element('div', undefined, 'section-heading menu-heading');
    const addItem = element('button', '+ Add item', 'secondary');
    addItem.type = 'button';
    addItem.addEventListener('click', () => openMenuEditor(restaurant));
    menuHeading.append(element('h3', 'Menu'), addItem);
    details.replaceChildren(heading, statusBadge(restaurant.isOpen), facts, menuHeading, menu);
    try {
      const items = await request(`${path}/menu`);
      if (currentRequest !== detailRequest) return;
      menu.replaceChildren();
      if (items.length === 0) menu.append(element('p', 'No menu items yet.'));
      for (const item of items) {
        const row = element('article', undefined, 'menu-item');
        row.append(element('span', `$${Number(item.price).toFixed(2)}`, 'item-price'),
          element('strong', item.name), element('p', item.description),
          element('span', item.availability ? 'Available' : 'Unavailable', item.availability ? 'badge' : 'badge closed'));
        const button = element('button', 'View item', 'secondary');
        button.type = 'button';
        const itemDetails = element('p');
        itemDetails.hidden = true;
        button.addEventListener('click', async () => {
          button.disabled = true;
          itemDetails.hidden = false;
          itemDetails.textContent = 'Loading item…';
          try {
            const fullItem = await request(`${path}/menu/${encodeURIComponent(item.id)}`);
            itemDetails.textContent = `${fullItem.name}: ${fullItem.description} — $${Number(fullItem.price).toFixed(2)}. ${fullItem.availability ? 'Available' : 'Unavailable'}.`;
          } catch (error) {
            itemDetails.textContent = error.message;
          } finally {
            button.disabled = false;
          }
        });
        row.append(element('br'), button, itemDetails);
        menu.append(row);
      }
    } catch (error) {
      if (currentRequest === detailRequest) menu.replaceChildren(element('p', error.message, 'error'));
    }
  } catch (error) {
    if (currentRequest === detailRequest) details.replaceChildren(element('p', error.message, 'error'));
  }
}

function openEditor(restaurant = null) {
  editingId = restaurant ? restaurant.id : null;
  restaurantForm.reset();
  document.querySelector('#editor-title').textContent = restaurant ? 'Edit restaurant' : 'Add restaurant';
  document.querySelector('#form-error').textContent = '';
  if (restaurant) {
    for (const name of ['name', 'cuisine', 'location', 'opening_hours']) {
      restaurantForm.elements[name].value = restaurant[name];
    }
    restaurantForm.elements.isOpen.checked = restaurant.isOpen;
  }
  editor.showModal();
}

restaurantForm.addEventListener('submit', async event => {
  event.preventDefault();
  const payload = {};
  for (const name of ['name', 'cuisine', 'location', 'opening_hours']) {
    payload[name] = restaurantForm.elements[name].value.trim();
    if (!payload[name]) {
      document.querySelector('#form-error').textContent = 'Please fill in every text field.';
      return;
    }
  }
  payload.isOpen = restaurantForm.elements.isOpen.checked;
  const save = document.querySelector('#save-restaurant');
  const close = document.querySelector('#close-editor');
  save.disabled = true;
  close.disabled = true;
  document.querySelector('#form-error').textContent = '';
  try {
    const path = editingId ? `/restaurants/${encodeURIComponent(editingId)}` : '/restaurants';
    const saved = await request(path, {
      method: editingId ? 'PUT' : 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    editor.close();
    // Clear filters without triggering the Clear button's reload handler.
    for (const name of ['search', 'cuisine', 'location', 'is_open']) {
      filters.elements[name].value = '';
    }
    await loadRestaurants();
    await showRestaurant(saved.id);
    notice.className = '';
    notice.textContent = 'Restaurant saved.';
  } catch (error) {
    document.querySelector('#form-error').textContent = error.message;
  } finally {
    save.disabled = false;
    close.disabled = false;
  }
});

filters.addEventListener('submit', event => { event.preventDefault(); loadRestaurants(); });
filters.addEventListener('reset', () => { setTimeout(loadRestaurants, 0); });
document.querySelector('#create-restaurant').addEventListener('click', () => openEditor());
document.querySelector('#close-editor').addEventListener('click', () => editor.close());
function openMenuEditor(restaurant) {
  menuRestaurantId = restaurant.id;
  menuItemForm.reset();
  document.querySelector('#menu-editor-title').textContent = `Add item to ${restaurant.name}`;
  document.querySelector('#menu-form-error').textContent = '';
  menuEditor.showModal();
}

menuItemForm.addEventListener('submit', async event => {
  event.preventDefault();
  const formError = document.querySelector('#menu-form-error');
  const name = menuItemForm.elements.name.value.trim();
  const description = menuItemForm.elements.description.value.trim();
  const price = Number(menuItemForm.elements.price.value);
  if (!name || !description) {
    formError.textContent = 'Please fill in the name and description.';
    return;
  }
  if (menuItemForm.elements.price.value === '' || !Number.isFinite(price) || price < 0) {
    formError.textContent = 'Price must be a number of 0 or more.';
    return;
  }
  const save = document.querySelector('#save-menu-item');
  const close = document.querySelector('#close-menu-editor');
  save.disabled = true;
  close.disabled = true;
  formError.textContent = '';
  try {
    // restaurant_id in the body is still a required int on the API (issue #60); the backend
    // ignores it and uses the restaurant in the URL, so 0 is only a placeholder.
    await request(`/restaurant/${encodeURIComponent(menuRestaurantId)}/menu`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        restaurant_id: 0, name, description, price,
        availability: menuItemForm.elements.availability.checked,
      }),
    });
    menuEditor.close();
    await showRestaurant(menuRestaurantId);
    notice.className = '';
    notice.textContent = `Added "${name}" to the menu.`;
  } catch (error) {
    formError.textContent = error.message;
  } finally {
    save.disabled = false;
    close.disabled = false;
  }
});

document.querySelector('#close-menu-editor').addEventListener('click', () => menuEditor.close());
menuEditor.addEventListener('cancel', event => {
  if (document.querySelector('#save-menu-item').disabled) event.preventDefault();
});
editor.addEventListener('cancel', event => {
  if (document.querySelector('#save-restaurant').disabled) event.preventDefault();
});
loadRestaurants();
