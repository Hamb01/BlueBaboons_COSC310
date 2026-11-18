const filters = document.querySelector('#filters');
const restaurantList = document.querySelector('#restaurants');
const details = document.querySelector('#details');
const notice = document.querySelector('#notice');
const editor = document.querySelector('#editor');
const restaurantForm = document.querySelector('#restaurant-form');
let editingId = null;
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
      if (typeof error.message === 'string') {
        const statusCode = Number.isInteger(error.status_code) ? error.status_code : response.status;
        message = `${error.message} (HTTP ${statusCode})`;
        if (error.details !== undefined && error.details !== null && error.details !== '') {
          const errorDetails = typeof error.details === 'string' ? error.details : JSON.stringify(error.details);
          message += `: ${errorDetails}`;
        }
      } else if (typeof error.detail === 'string') {
        message = error.detail;
      } else if (Array.isArray(error.detail)) {
        message = error.detail.map(item => `${item.loc.slice(1).join('.')}: ${item.msg}`).join('; ');
      }
    } catch { /* Keep the default message for a non-JSON response. */ }
    const failure = new Error(message);
    failure.status = response.status;
    throw failure;
  }
  return response.json();
}

// Sign in and cart. The token is kept in localStorage so a refresh keeps you signed in.
const loginDialog = document.querySelector('#login-dialog');
const loginForm = document.querySelector('#login-form');
const cartDialog = document.querySelector('#cart-dialog');

function getToken() {
  try { return localStorage.getItem('bb_token'); } catch { return null; }
}

function setToken(token) {
  try {
    if (token) localStorage.setItem('bb_token', token);
    else localStorage.removeItem('bb_token');
  } catch { /* Private browsing: stay signed in until the page closes. */ }
}

function authRequest(path, options = {}) {
  const headers = {...(options.headers || {}), Authorization: `Bearer ${getToken()}`};
  return request(path, {...options, headers}).catch(error => {
    if (error.status === 401) {
      setToken(null);
      showSignedOut();
    }
    throw error;
  });
}

function showSignedOut() {
  document.querySelector('#account').textContent = '';
  document.querySelector('#sign-in').hidden = false;
  document.querySelector('#sign-out').hidden = true;
  document.querySelector('#open-cart').textContent = 'Cart (0)';
}

async function refreshAccount() {
  if (!getToken()) return showSignedOut();
  try {
    const me = await authRequest('/customers/me');
    document.querySelector('#account').textContent = `Hi, ${me.name}`;
    document.querySelector('#sign-in').hidden = true;
    document.querySelector('#sign-out').hidden = false;
    await refreshCart();
  } catch (error) {
    if (error.status !== 401) showMessage(error.message, true);
  }
}

function showMessage(text, isError = false) {
  notice.className = isError ? 'error' : '';
  notice.textContent = text;
}

function renderCart(cart) {
  const count = cart.items.reduce((total, line) => total + line.quantity, 0);
  document.querySelector('#open-cart').textContent = `Cart (${count})`;
  const list = document.querySelector('#cart-items');
  list.replaceChildren();
  if (cart.items.length === 0) list.append(element('p', 'Your cart is empty.', 'empty'));
  for (const line of cart.items) {
    const row = element('div', undefined, 'cart-line');
    const name = element('div');
    name.append(element('strong', `${line.name} × ${line.quantity}`),
      element('small', line.available ? `$${line.unit_price.toFixed(2)} each` : 'No longer available'));
    row.append(name, element('span', `$${line.line_total.toFixed(2)}`));
    list.append(row);
  }
  document.querySelector('#cart-total').textContent = `Total: $${cart.total.toFixed(2)}`;
}

async function refreshCart() {
  if (!getToken()) return;
  renderCart(await authRequest('/cart'));
}

async function addToCart(restaurantId, item) {
  if (!getToken()) {
    showMessage('Sign in to add items to your cart.');
    loginDialog.showModal();
    return;
  }
  try {
    const cart = await authRequest('/cart/items', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({restaurant_id: restaurantId, menu_item_id: item.id, quantity: 1}),
    });
    renderCart(cart);
    showMessage(`Added ${item.name} to your cart.`);
  } catch (error) {
    showMessage(error.message, true);
  }
}

loginForm.addEventListener('submit', async event => {
  event.preventDefault();
  const submit = document.querySelector('#submit-login');
  submit.disabled = true;
  document.querySelector('#login-error').textContent = '';
  try {
    const token = await request('/auth/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username: loginForm.elements.username.value.trim(),
        password: loginForm.elements.password.value}),
    });
    setToken(token);
    loginDialog.close();
    loginForm.reset();
    await refreshAccount();
    showMessage('Signed in.');
  } catch (error) {
    document.querySelector('#login-error').textContent = error.message;
  } finally {
    submit.disabled = false;
  }
});

document.querySelector('#sign-in').addEventListener('click', () => loginDialog.showModal());
document.querySelector('#close-login').addEventListener('click', () => loginDialog.close());
document.querySelector('#sign-out').addEventListener('click', () => {
  setToken(null);
  showSignedOut();
  showMessage('Signed out.');
});
document.querySelector('#open-cart').addEventListener('click', async () => {
  if (!getToken()) {
    showMessage('Sign in to see your cart.');
    loginDialog.showModal();
    return;
  }
  try {
    await refreshCart();
    cartDialog.showModal();
  } catch (error) {
    showMessage(error.message, true);
  }
});
document.querySelector('#close-cart').addEventListener('click', () => cartDialog.close());

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
    for (const [label, value] of [['Cuisine', restaurant.cuisine], ['Location', restaurant.location], ['Address', restaurant.address], ['Postal code', restaurant.postal_code], ['Opening hours', restaurant.opening_hours]]) {
      const fact = element('div');
      fact.append(element('dt', label), element('dd', value));
      facts.append(fact);
    }
    const menu = element('div');
    menu.append(element('p', 'Loading menu…'));
    details.replaceChildren(heading, statusBadge(restaurant.isOpen), facts, element('h3', 'Menu'), menu);
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
        row.append(element('br'), button);
        if (item.availability) {
          const add = element('button', 'Add to cart');
          add.type = 'button';
          add.addEventListener('click', () => addToCart(restaurant.id, item));
          row.append(add);
        }
        row.append(itemDetails);
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
    for (const name of ['name', 'cuisine', 'location', 'address', 'postal_code', 'opening_hours']) {
      restaurantForm.elements[name].value = restaurant[name];
    }
    restaurantForm.elements.isOpen.checked = restaurant.isOpen;
  }
  editor.showModal();
}

restaurantForm.addEventListener('submit', async event => {
  event.preventDefault();
  const payload = {};
  for (const name of ['name', 'cuisine', 'location', 'address', 'postal_code', 'opening_hours']) {
    payload[name] = restaurantForm.elements[name].value.trim();
    if (!payload[name]) {
      document.querySelector('#form-error').textContent = 'Please fill in every text field.';
      return;
    }
  }
      payload.postal_code = payload.postal_code?.toUpperCase();
    if (!(/^[A-Z]\d[A-Z] \d[A-Z]\d$/.test(payload.postal_code))) {
      document.querySelector('#form-error').textContent = 'Postal code must use the format A1A 1A1.';
      return;
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
editor.addEventListener('cancel', event => {
  if (document.querySelector('#save-restaurant').disabled) event.preventDefault();
});
loadRestaurants();
refreshAccount();
