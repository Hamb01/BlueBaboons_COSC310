const $ = selector => document.querySelector(selector);
const filters = $('#filters');
const restaurantList = $('#restaurants');
const details = $('#details');
const notice = $('#notice');
const editor = $('#editor');
const restaurantForm = $('#restaurant-form');
const loginDialog = $('#login-dialog');
const loginForm = $('#login-form');
const cartDialog = $('#cart-dialog');
const ordersDialog = $('#orders-dialog');
const restaurantsById = new Map();
let editingId = null;
let listRequest = 0;
let detailRequest = 0;
let noticeTimer = null;

// Use textContent for API data so names are always displayed as text.
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function icon(name) {
  const node = element('i', undefined, `ph ph-${name}`);
  node.setAttribute('aria-hidden', 'true');
  return node;
}

function button(label, className, iconName) {
  const node = element('button', undefined, className);
  node.type = 'button';
  if (iconName) node.append(icon(iconName));
  if (label) node.append(document.createTextNode(label));
  return node;
}

const money = value => `$${Number(value).toFixed(2)}`;

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
        message = error.message;
        if (typeof error.details === 'string' && error.details) message += ` ${error.details}`;
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
  return response.status === 204 ? null : response.json();
}

function showMessage(text, isError = false) {
  clearTimeout(noticeTimer);
  notice.textContent = text;
  notice.className = `show${isError ? ' error' : ''}`;
  noticeTimer = setTimeout(() => { notice.className = isError ? 'error' : ''; }, isError ? 6000 : 3200);
}

// ---------------------------------------------------------------- session
// The token is kept in localStorage so a refresh keeps you signed in.
function getToken() {
  try { return localStorage.getItem('bb_token'); } catch { return null; }
}

function setToken(token) {
  try {
    if (token) localStorage.setItem('bb_token', token);
    else localStorage.removeItem('bb_token');
  } catch { /* Private browsing: stay signed in until the page closes. */ }
}

// Read the user id from the token to decide which controls to show.
// The server still checks every request; this only hides buttons that would be refused.
function session() {
  const token = getToken();
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    if (payload.exp && payload.exp * 1000 < Date.now()) return null;
    const roles = {c: 'customer', o: 'owner', a: 'admin', d: 'developer', s: 'support'};
    return {id: payload.id, role: roles[String(payload.id)[0]] || 'customer'};
  } catch {
    return null;
  }
}

const isCustomer = () => session()?.role === 'customer';
const isStaff = () => ['owner', 'admin', 'developer'].includes(session()?.role);

function canManage(restaurant) {
  const user = session();
  if (!user) return false;
  if (user.role === 'admin' || user.role === 'developer') return true;
  return user.role === 'owner' && restaurant.owner_id === user.id;
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

const jsonBody = (method, body) => ({method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});

function setAccountLabel(name, role) {
  const chip = $('#account');
  chip.replaceChildren(document.createTextNode('Hi, '), element('strong', name));
  if (role !== 'customer') chip.append(document.createTextNode(` (${role})`));
  chip.hidden = false;
}

function showSignedOut() {
  $('#account').hidden = true;
  $('#sign-in').hidden = false;
  $('#sign-out').hidden = true;
  $('#open-orders').hidden = true;
  $('#open-cart').hidden = false;
  $('#create-restaurant').hidden = true;
  setCartCount(0);
}

async function refreshAccount() {
  const user = session();
  if (!user) {
    setToken(null);
    return showSignedOut();
  }
  $('#sign-in').hidden = true;
  $('#sign-out').hidden = false;
  if (user.role === 'customer') {
    $('#open-orders').hidden = false;
    $('#open-cart').hidden = false;
    $('#create-restaurant').hidden = true;
    try {
      const me = await authRequest('/customers/me');
      setAccountLabel(me.name.split(' ')[0], 'customer');
      await refreshCart();
    } catch (error) {
      if (error.status !== 401) showMessage(error.message, true);
    }
  } else {
    setAccountLabel(user.id, user.role);
    $('#open-orders').hidden = true;
    $('#open-cart').hidden = true;
    $('#create-restaurant').hidden = !isStaff();
  }
}

loginForm.addEventListener('submit', async event => {
  event.preventDefault();
  const submit = $('#submit-login');
  submit.disabled = true;
  $('#login-error').textContent = '';
  try {
    const token = await request('/auth/login', jsonBody('POST', {
      username: loginForm.elements.username.value.trim(),
      password: loginForm.elements.password.value,
    }));
    setToken(token);
    loginDialog.close();
    loginForm.reset();
    await refreshAccount();
    showMessage('Signed in.');
    const selected = restaurantList.querySelector('[aria-pressed="true"]');
    if (selected) showRestaurant(selected.dataset.id);
  } catch (error) {
    $('#login-error').textContent = error.message;
  } finally {
    submit.disabled = false;
  }
});

for (const chip of document.querySelectorAll('.demo-accounts .chip')) {
  chip.addEventListener('click', () => {
    loginForm.elements.username.value = chip.dataset.username;
    loginForm.elements.password.value = chip.dataset.password;
    $('#submit-login').focus();
  });
}

$('#sign-in').addEventListener('click', () => loginDialog.showModal());
$('#close-login').addEventListener('click', () => loginDialog.close());
$('#sign-out').addEventListener('click', () => {
  setToken(null);
  showSignedOut();
  showMessage('Signed out.');
  const selected = restaurantList.querySelector('[aria-pressed="true"]');
  if (selected) showRestaurant(selected.dataset.id);
});

function askToSignIn(message) {
  showMessage(message);
  loginDialog.showModal();
}

// ---------------------------------------------------------------- cart
function setCartCount(count) {
  const pill = $('#cart-count');
  if (pill.textContent !== String(count)) {
    pill.classList.remove('bump');
    void pill.offsetWidth;
    pill.classList.add('bump');
  }
  pill.textContent = String(count);
  $('#open-cart').setAttribute('aria-label', `Cart, ${count} ${count === 1 ? 'item' : 'items'}`);
}

async function cartAction(path, options, doneMessage) {
  $('#cart-error').textContent = '';
  try {
    const cart = await authRequest(path, options);
    renderCart(cart);
    if (doneMessage) showMessage(doneMessage);
  } catch (error) {
    $('#cart-error').textContent = error.message;
  }
}

function renderCart(cart) {
  const count = cart.items.reduce((total, line) => total + line.quantity, 0);
  setCartCount(count);
  const list = $('#cart-items');
  list.replaceChildren();
  const restaurant = restaurantsById.get(cart.restaurant_id);
  $('#cart-restaurant').textContent = restaurant ? `From ${restaurant.name}` : '';
  if (cart.items.length === 0) {
    const empty = element('div', undefined, 'empty-state');
    const art = element('img');
    art.src = '/ui/baboon.svg';
    art.alt = '';
    art.width = 64;
    art.height = 63;
    empty.append(art, element('p', 'Your cart is empty. Add something from a menu.'));
    list.append(empty);
  }
  for (const line of cart.items) {
    const row = element('div', undefined, 'cart-line');
    const name = element('div');
    name.append(element('strong', line.name),
      element('small', line.available ? `${money(line.unit_price)} each` : 'Sold out or no longer on the menu'));
    const controls = element('div', undefined, 'line-controls');
    const stepper = element('div', undefined, 'stepper');
    const minus = button('', '', 'minus');
    minus.setAttribute('aria-label', `One less ${line.name}`);
    const plus = button('', '', 'plus');
    plus.setAttribute('aria-label', `One more ${line.name}`);
    const quantity = element('output', String(line.quantity));
    quantity.setAttribute('aria-label', 'Quantity');
    const itemPath = `/cart/items/${encodeURIComponent(line.menu_item_id)}`;
    minus.addEventListener('click', () => (line.quantity > 1
      ? cartAction(itemPath, jsonBody('PATCH', {quantity: line.quantity - 1}))
      : cartAction(itemPath, {method: 'DELETE'}, `Removed ${line.name}.`)));
    plus.addEventListener('click', () => cartAction(itemPath, jsonBody('PATCH', {quantity: line.quantity + 1})));
    stepper.append(minus, quantity, plus);
    const remove = button('', 'icon-button remove-line', 'trash');
    remove.setAttribute('aria-label', `Remove ${line.name}`);
    remove.addEventListener('click', () => cartAction(itemPath, {method: 'DELETE'}, `Removed ${line.name}.`));
    controls.append(stepper, remove);
    row.append(name, element('span', money(line.line_total), 'line-total'), controls);
    list.append(row);
  }
  const total = $('#cart-total');
  total.replaceChildren(element('span', 'Total'), element('span', money(cart.total)));
  $('#checkout').disabled = cart.items.length === 0;
  $('#clear-cart').disabled = cart.items.length === 0;
  $('.drawer-foot').hidden = false;
}

async function refreshCart() {
  if (!isCustomer()) return;
  renderCart(await authRequest('/cart'));
}

async function addToCart(restaurantId, item, trigger) {
  if (!getToken()) return askToSignIn('Sign in to add items to your cart.');
  trigger.disabled = true;
  try {
    const cart = await authRequest('/cart/items', jsonBody('POST', {restaurant_id: restaurantId, menu_item_id: item.id, quantity: 1}));
    renderCart(cart);
    showMessage(`Added ${item.name} to your cart.`);
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    trigger.disabled = false;
  }
}

$('#open-cart').addEventListener('click', async () => {
  if (!getToken()) return askToSignIn('Sign in to see your cart.');
  $('#cart-error').textContent = '';
  try {
    await refreshCart();
    cartDialog.showModal();
  } catch (error) {
    showMessage(error.message, true);
  }
});
$('#close-cart').addEventListener('click', () => cartDialog.close());
$('#clear-cart').addEventListener('click', () => cartAction('/cart', {method: 'DELETE'}, 'Cart cleared.'));

$('#checkout').addEventListener('click', async () => {
  const checkout = $('#checkout');
  checkout.disabled = true;
  $('#cart-error').textContent = '';
  try {
    const order = await authRequest('/checkout', {method: 'POST'});
    const done = element('div', undefined, 'success');
    const view = button('View my orders', 'primary', 'receipt');
    view.addEventListener('click', () => { cartDialog.close(); openOrders(); });
    const check = icon('check-circle');
    check.className = 'ph-fill ph-check-circle';
    done.append(check, element('h3', 'Order placed'),
      element('p', `Order ${order.id}, ${money(order.total)}. It will go to ${order.delivery_address}.`), view);
    $('#cart-items').replaceChildren(done);
    $('#cart-restaurant').textContent = '';
    $('.drawer-foot').hidden = true;
    setCartCount(0);
    showMessage('Order placed.');
  } catch (error) {
    $('#cart-error').textContent = error.message;
    checkout.disabled = false;
  }
});

// ---------------------------------------------------------------- orders
async function openOrders() {
  const list = $('#orders-list');
  list.replaceChildren(element('div', undefined, 'skeleton'), element('div', undefined, 'skeleton'));
  ordersDialog.showModal();
  try {
    const orders = await authRequest('/customers/me/orders');
    list.replaceChildren();
    if (orders.length === 0) list.append(element('p', 'No orders yet. Your first one will show up here.', 'empty-state'));
    orders.sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
    for (const order of orders) {
      const card = element('article', undefined, 'order-card');
      const head = element('header');
      head.append(element('span', restaurantsById.get(order.restaurant_id)?.name || order.restaurant_id), element('span', money(order.total)));
      const items = element('ul');
      for (const item of order.items) items.append(element('li', `${item.quantity} x ${item.name} at ${money(item.unit_price)}`));
      const placed = new Date(order.created_at);
      const when = Number.isNaN(placed.getTime()) ? '' : placed.toLocaleString([], {dateStyle: 'medium', timeStyle: 'short'});
      card.append(head, items, element('span', `Order ${order.id}${when ? `, ${when}` : ''}`, 'order-meta'));
      list.append(card);
    }
  } catch (error) {
    list.replaceChildren(element('p', error.message, 'error'));
  }
}

$('#open-orders').addEventListener('click', openOrders);
$('#close-orders').addEventListener('click', () => ordersDialog.close());

// Close drawers and modals when the backdrop is clicked.
for (const dialog of [cartDialog, ordersDialog, loginDialog, editor]) {
  dialog.addEventListener('click', event => {
    if (event.target === dialog && !(dialog === editor && $('#save-restaurant').disabled)) dialog.close();
  });
}

// ---------------------------------------------------------------- restaurants
const CUISINE_ICONS = [
  [/mex|taco/i, 'pepper'], [/japan|sushi|seafood|fish/i, 'fish'], [/ital|pizza/i, 'pizza'],
  [/burger|american|grill/i, 'hamburger'], [/cafe|coffee|bakery/i, 'coffee'],
  [/chin|thai|viet|korea|asian|ramen|noodle/i, 'bowl-food'], [/indian|curry/i, 'cooking-pot'],
  [/dessert|ice cream|sweet/i, 'ice-cream'],
];

function cuisineIcon(cuisine) {
  const match = CUISINE_ICONS.find(([pattern]) => pattern.test(cuisine || ''));
  return match ? match[1] : 'fork-knife';
}

function statusBadge(isOpen) {
  return element('span', isOpen ? 'Open' : 'Closed', isOpen ? 'badge' : 'badge closed');
}

function emptyDetails() {
  const empty = element('div', undefined, 'empty-state');
  const art = element('img');
  art.src = '/ui/baboon.svg';
  art.alt = '';
  art.width = 72;
  art.height = 71;
  empty.append(art, element('p', 'Pick a restaurant to see its menu.'));
  details.replaceChildren(empty);
}

async function loadRestaurants() {
  const currentRequest = ++listRequest;
  ++detailRequest;
  emptyDetails();
  restaurantList.replaceChildren(...Array.from({length: 4}, () => element('div', undefined, 'skeleton')));
  restaurantList.setAttribute('aria-busy', 'true');
  $('#count').textContent = '';
  const params = new URLSearchParams();
  for (const [name, value] of new FormData(filters)) {
    if (value.trim() !== '') params.set(name, value.trim());
  }
  try {
    const restaurants = await request(`/restaurants?${params}`);
    if (currentRequest !== listRequest) return;
    restaurantList.replaceChildren();
    $('#count').textContent = `${restaurants.length} found`;
    if (restaurants.length === 0) {
      restaurantList.append(element('p', 'No restaurants match. Try clearing your filters.', 'empty-state'));
    }
    restaurants.forEach((restaurant, index) => {
      restaurantsById.set(restaurant.id, restaurant);
      const card = element('button', undefined, 'restaurant-card');
      card.type = 'button';
      card.dataset.id = restaurant.id;
      card.style.setProperty('--i', index);
      card.setAttribute('aria-pressed', 'false');
      const tile = element('span', undefined, 'cuisine-tile');
      tile.append(icon(cuisineIcon(restaurant.cuisine)));
      const text = element('span');
      text.append(element('strong', restaurant.name), element('small', `${restaurant.cuisine}, ${restaurant.location}`));
      card.append(tile, text, statusBadge(restaurant.isOpen));
      card.addEventListener('click', () => showRestaurant(restaurant.id));
      restaurantList.append(card);
    });
  } catch (error) {
    if (currentRequest !== listRequest) return;
    restaurantList.replaceChildren(element('p', error.message, 'error'));
  } finally {
    if (currentRequest === listRequest) restaurantList.removeAttribute('aria-busy');
  }
}

function menuItemCard(restaurant, item, index, path) {
  const card = element('article', undefined, item.availability ? 'menu-item' : 'menu-item unavailable');
  card.style.setProperty('--i', index);
  const top = element('div', undefined, 'menu-item-top');
  top.append(element('strong', item.name), element('span', money(item.price), 'item-price'));
  const actions = element('div', undefined, 'menu-item-actions');
  if (!item.availability) actions.append(element('span', 'Sold out', 'badge sold-out'));
  if (item.availability && !isStaff()) {
    const add = button('Add', 'primary', 'plus');
    add.setAttribute('aria-label', `Add ${item.name} to cart`);
    add.addEventListener('click', () => addToCart(restaurant.id, item, add));
    actions.append(add);
  }
  const itemDetails = element('p', undefined, 'item-details');
  itemDetails.hidden = true;
  const more = button('Details', 'ghost', 'info');
  more.addEventListener('click', async () => {
    more.disabled = true;
    itemDetails.hidden = false;
    itemDetails.textContent = 'Loading item...';
    try {
      const fullItem = await request(`${path}/menu/${encodeURIComponent(item.id)}`);
      itemDetails.textContent = `${fullItem.name}, ${money(fullItem.price)}. ${fullItem.availability ? 'Available to order.' : 'Sold out right now.'}`;
    } catch (error) {
      itemDetails.textContent = error.message;
    } finally {
      more.disabled = false;
    }
  });
  actions.append(more);
  if (canManage(restaurant)) {
    const toggle = button(item.availability ? 'Mark sold out' : 'Mark available', 'ghost', item.availability ? 'prohibit' : 'check');
    toggle.addEventListener('click', async () => {
      toggle.disabled = true;
      try {
        await authRequest(`${path}/menu/${encodeURIComponent(item.id)}`, jsonBody('PATCH', {availability: !item.availability}));
        showMessage(`${item.name} is now ${item.availability ? 'sold out' : 'available'}.`);
        showRestaurant(restaurant.id);
      } catch (error) {
        showMessage(error.message, true);
        toggle.disabled = false;
      }
    });
    actions.append(toggle);
  }
  card.append(top, element('p', item.description), actions, itemDetails);
  return card;
}

async function showRestaurant(id) {
  const currentRequest = ++detailRequest;
  details.replaceChildren(element('div', undefined, 'skeleton'));
  for (const card of restaurantList.querySelectorAll('.restaurant-card')) {
    card.setAttribute('aria-pressed', String(card.dataset.id === id));
  }
  const path = `/restaurants/${encodeURIComponent(id)}`;
  try {
    const restaurant = await request(path);
    if (currentRequest !== detailRequest) return;
    restaurantsById.set(restaurant.id, restaurant);
    const head = element('div', undefined, 'detail-head');
    const title = element('div');
    const heading = element('h2', restaurant.name);
    heading.tabIndex = -1;
    title.append(heading);
    head.append(title);
    if (canManage(restaurant)) {
      const edit = button('Edit', 'ghost small', 'pencil-simple');
      edit.addEventListener('click', () => openEditor(restaurant));
      head.append(edit);
    }
    const meta = element('div', undefined, 'detail-meta');
    for (const [iconName, text] of [[cuisineIcon(restaurant.cuisine), restaurant.cuisine],
      ['map-pin', `${restaurant.address}, ${restaurant.postal_code}`], ['clock', restaurant.opening_hours]]) {
      const part = element('span');
      part.append(icon(iconName), document.createTextNode(text));
      meta.append(part);
    }
    meta.prepend(statusBadge(restaurant.isOpen));
    const menu = element('div', undefined, 'menu-grid');
    menu.append(element('div', undefined, 'skeleton'), element('div', undefined, 'skeleton'));
    const menuHead = element('div', undefined, 'menu-head');
    menuHead.append(element('h3', 'Menu'));
    if (canManage(restaurant)) {
      const addItem = button('Add item', 'ghost small', 'plus');
      addItem.addEventListener('click', () => openItemDialog(restaurant));
      menuHead.append(addItem);
    }
    details.replaceChildren(head, meta, menuHead, menu);
    if (window.matchMedia('(max-width: 820px)').matches) details.scrollIntoView({block: 'start'});
    try {
      const items = await request(`${path}/menu`);
      if (currentRequest !== detailRequest) return;
      menu.replaceChildren();
      if (items.length === 0) menu.append(element('p', 'No menu items yet.', 'empty-state'));
      items.forEach((item, index) => menu.append(menuItemCard(restaurant, item, index, path)));
    } catch (error) {
      if (currentRequest !== detailRequest) return;
      menu.replaceChildren(element('p', error.status === 404 ? 'No menu items yet.' : error.message, error.status === 404 ? 'empty-state' : 'error'));
    }
  } catch (error) {
    if (currentRequest === detailRequest) details.replaceChildren(element('p', error.message, 'error'));
  }
}

// ---------------------------------------------------------------- add menu item (owners and admins)
const itemDialog = $('#item-dialog');
const itemForm = $('#item-form');
let itemRestaurant = null;

function openItemDialog(restaurant) {
  itemRestaurant = restaurant;
  itemForm.reset();
  $('#item-title').textContent = `Add item to ${restaurant.name}`;
  $('#item-error').textContent = '';
  itemDialog.showModal();
  itemForm.elements.name.focus();
}

itemForm.addEventListener('submit', async event => {
  event.preventDefault();
  const name = itemForm.elements.name.value.trim();
  const description = itemForm.elements.description.value.trim();
  const price = Number(itemForm.elements.price.value);
  if (!name || !description) {
    $('#item-error').textContent = 'Please fill in the name and description.';
    return;
  }
  if (!Number.isFinite(price) || price < 0) {
    $('#item-error').textContent = 'Price must be 0 or more.';
    return;
  }
  const save = $('#save-item');
  save.disabled = true;
  $('#item-error').textContent = '';
  try {
    const result = await authRequest(`/restaurants/${encodeURIComponent(itemRestaurant.id)}/menu`,
      jsonBody('POST', {name, description, price, availability: itemForm.elements.availability.checked}));
    itemDialog.close();
    showMessage(`Added ${result.item?.name || name} to the menu.`);
    await showRestaurant(itemRestaurant.id);
  } catch (error) {
    $('#item-error').textContent = error.message;
  } finally {
    save.disabled = false;
  }
});

$('#close-item').addEventListener('click', () => itemDialog.close());
itemDialog.addEventListener('click', event => { if (event.target === itemDialog) itemDialog.close(); });

// ---------------------------------------------------------------- restaurant editor (owners and admins)
function openEditor(restaurant = null) {
  editingId = restaurant ? restaurant.id : null;
  restaurantForm.reset();
  $('#editor-title').textContent = restaurant ? 'Edit restaurant' : 'Add restaurant';
  $('#form-error').textContent = '';
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
      $('#form-error').textContent = 'Please fill in every text field.';
      return;
    }
  }
  payload.postal_code = payload.postal_code.toUpperCase();
  if (!/^[A-Z]\d[A-Z] \d[A-Z]\d$/.test(payload.postal_code)) {
    $('#form-error').textContent = 'Postal code must use the format A1A 1A1.';
    return;
  }
  payload.isOpen = restaurantForm.elements.isOpen.checked;
  const save = $('#save-restaurant');
  const close = $('#close-editor');
  save.disabled = true;
  close.disabled = true;
  $('#form-error').textContent = '';
  try {
    const path = editingId ? `/restaurants/${encodeURIComponent(editingId)}` : '/restaurants';
    const saved = await authRequest(path, jsonBody(editingId ? 'PUT' : 'POST', payload));
    editor.close();
    // Clear filters without triggering the Clear button's reload handler.
    for (const name of ['search', 'cuisine', 'location', 'is_open']) filters.elements[name].value = '';
    await loadRestaurants();
    await showRestaurant(saved.id);
    showMessage('Restaurant saved.');
  } catch (error) {
    $('#form-error').textContent = error.message;
  } finally {
    save.disabled = false;
    close.disabled = false;
  }
});

filters.addEventListener('submit', event => { event.preventDefault(); loadRestaurants(); });
filters.addEventListener('reset', () => { setTimeout(loadRestaurants, 0); });
$('#create-restaurant').addEventListener('click', () => openEditor());
$('#close-editor').addEventListener('click', () => editor.close());
editor.addEventListener('cancel', event => {
  if ($('#save-restaurant').disabled) event.preventDefault();
});

// ---------------------------------------------------------------- hero baboon looks at the cursor
// Sets --look-x / --look-y (-1..1) once per frame; CSS turns them into a head tilt and pupil shift.
// Skipped for reduced motion and touch-only devices.
(() => {
  const baboon = $('#hero-baboon');
  const stillPlease = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    || !window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (!baboon || stillPlease) return;
  let pointer = null;
  let frame = 0;
  const clamp = value => Math.max(-1, Math.min(1, value));
  const update = () => {
    frame = 0;
    if (!pointer) {
      baboon.style.setProperty('--look-x', 0);
      baboon.style.setProperty('--look-y', 0);
      return;
    }
    const box = baboon.getBoundingClientRect();
    const reach = Math.max(window.innerWidth, window.innerHeight) / 2;
    baboon.style.setProperty('--look-x', clamp((pointer.x - (box.left + box.width / 2)) / reach).toFixed(3));
    baboon.style.setProperty('--look-y', clamp((pointer.y - (box.top + box.height * 0.42)) / reach).toFixed(3));
  };
  const schedule = () => { if (!frame) frame = requestAnimationFrame(update); };
  window.addEventListener('pointermove', event => { pointer = {x: event.clientX, y: event.clientY}; schedule(); }, {passive: true});
  document.documentElement.addEventListener('pointerleave', () => { pointer = null; schedule(); });
})();

loadRestaurants();
refreshAccount();
