/* ============================================================
   КОНФИГУРАЦИЯ И ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
   ============================================================ */
const API = "http://127.0.0.1:8000";
let activeMatchId = null;


/* ============================================================
   ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (утилиты)
   ============================================================ */

// Уведомления
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.classList.add("toast", type);
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// Крестик закрытия окна
function addCloseButton(container, onClose) {
  const closeBtn = document.createElement("button");
  closeBtn.textContent = "✕";
  closeBtn.className = "close-btn";
  closeBtn.onclick = () => {
    container.innerHTML = "";
    if (onClose) onClose();
  };
  container.appendChild(closeBtn);
}

// HTTP запросы
async function request(url, options = {}) {
  try {
    const res = await fetch(url, options);
    let data = null;
    let text = "";
    try {
      text = await res.text();
    } catch {
      text = "";
    }
    if (text && text.trim()) {
      try {
        data = JSON.parse(text);
      } catch {
        data = { _raw: text };
      }
    } else {
      data = {};
    }
    if (!res.ok) {
      const message = data?.detail || `Ошибка ${res.status}`;
      showToast(message, "error");
      throw new Error(message);
    }
    return data;
  } catch (err) {
    if (err.message.includes("fetch")) showToast("Сервер недоступен", "error");
    throw err;
  }
}


/* ============================================================
   ИГРОКИ
   ============================================================ */

// Создать игрока
async function createPlayer() {
  const input = document.getElementById("playerName");
  const name = input.value.trim();
  if (!name) {
    showToast("Введите имя игрока", "error");
    return;
  }
  try {
    await request(`${API}/players/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name })
    });
    showToast("Игрок создан", "success");
    input.value = "";
  } catch (err) {}
}

// Показать всех игроков
async function getPlayers() {
  try {
    const data = await request(`${API}/players/`);
    const container = document.getElementById("players");
    container.innerHTML = "";
    addCloseButton(container, () => container.innerHTML = "");
    data.forEach(p => {
      const card = document.createElement("div");
      card.className = "card";
      card.style.display = "flex";
      card.style.justifyContent = "space-between";
      card.style.alignItems = "center";
      card.style.gap = "10px";
      const left = document.createElement("div");
      left.textContent = `${p.id}. ${p.name}`;
      left.style.fontWeight = "500";
      const right = document.createElement("div");
      right.style.display = "flex";
      right.style.gap = "8px";
      const myMatchesBtn = document.createElement("button");
      myMatchesBtn.textContent = "🔍 Мои матчи";
      myMatchesBtn.style.background = "#00c2ff";
      myMatchesBtn.style.color = "#000";
      myMatchesBtn.onclick = () => showPlayerMatches(p.name);
      const deleteBtn = document.createElement("button");
      deleteBtn.textContent = "🗑 Удалить игрока";
      deleteBtn.style.background = "orange";
      deleteBtn.style.color = "#000";
      deleteBtn.onclick = async () => {
        const success = await deletePlayer(p.id);
        if (success) {
          showToast("Игрок удалён", "success");
          await getPlayers();
        }
      };
      right.appendChild(myMatchesBtn);
      right.appendChild(deleteBtn);
      card.appendChild(left);
      card.appendChild(right);
      container.appendChild(card);
    });
  } catch (err) {}
}

// Удалить игрока
async function deletePlayer(id) {
  try {
    await request(`${API}/players/${id}`, { method: "DELETE" });
    return true;
  } catch (err) {
    return false;
  }
}

// Поиск игрока
async function searchPlayer() {
  const input = document.getElementById("searchName");
  const name = input.value.trim();
  if (!name) {
    showToast("Введите имя игрока", "error");
    return;
  }
  try {
    const data = await request(`${API}/players/`);
    const found = data.find(p => p.name.toLowerCase().trim() === name.toLowerCase());
    const result = document.getElementById("searchResult");
    result.innerHTML = "";
    if (!found) {
      showToast("Игрок не найден", "error");
      input.value = "";
      return;
    }
    const card = document.createElement("div");
    card.className = "card";
    const text = document.createElement("div");
    text.textContent = `ID: ${found.id} | Имя: ${found.name}`;
    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Удалить игрока";
    deleteBtn.style.background = "orange";
    deleteBtn.style.marginTop = "8px";
    deleteBtn.onclick = async () => {
      const success = await deletePlayer(found.id);
      if (success) {
        showToast("Игрок удалён", "success");
        result.innerHTML = "";
        await getPlayers();
      }
    };
    card.appendChild(text);
    card.appendChild(deleteBtn);
    result.appendChild(card);
    showToast("Игрок найден", "success");
    input.value = "";
  } catch (err) {}
}


/* ============================================================
   МАТЧИ
   ============================================================ */

// Создать матч
async function createMatch() {
  const p1Input = document.getElementById("p1");
  const p2Input = document.getElementById("p2");
  const p1 = p1Input.value.trim();
  const p2 = p2Input.value.trim();
  if (!p1 || !p2) {
    showToast("Введите обоих игроков", "error");
    return;
  }
  try {
    await request(`${API}/matches/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_1_name: p1, player_2_name: p2 })
    });
    showToast("Матч создан", "success");
    p1Input.value = "";
    p2Input.value = "";
  } catch (err) {}
}

// Показать все матчи
async function getMatches(showNotification = true) {
  try {
    const data = await request(`${API}/matches/`);
    const container = document.getElementById("matches");
    container.innerHTML = "";
    addCloseButton(container, () => container.innerHTML = "");
    data.forEach(m => {
      const wrapper = document.createElement("div");
      wrapper.appendChild(renderMatch(m, false));
      const delBtn = document.createElement("button");
      delBtn.textContent = "🗑 Удалить матч";
      delBtn.style.background = "orange";
      delBtn.style.color = "#000";
      delBtn.style.marginTop = "8px";
      delBtn.onclick = async () => {
        const success = await deleteMatch(m.match_id);
        if (success) {
          showToast("Матч удалён", "success");
          await getMatches(false);
        }
      };
      wrapper.appendChild(delBtn);
      container.appendChild(wrapper);
    });
    if (showNotification) showToast("Матчи загружены", "success");
  } catch (err) {}
}

// Удалить матч
async function deleteMatch(id) {
  try {
    await request(`${API}/matches/${id}`, { method: "DELETE" });
    return true;
  } catch (err) {
    return false;
  }
}

// Изменить счёт (добавить +1/-1)
async function addGame(matchId, player, delta = 1) {
  try {
    await request(`${API}/matches/${matchId}/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player, count: delta })
    });
    showToast(delta > 0 ? `+1 ${player}` : `-1 ${player}`, delta > 0 ? "success" : "error");

    // Обновляем карточки матчей в блоке "Мои матчи" без перерисовки
    const playerMatchesBlock = document.getElementById("playerMatchesBlock");
    if (playerMatchesBlock && playerMatchesBlock.style.display === "block") {
      // Получаем свежие данные матча
      const updatedMatch = await request(`${API}/matches/${matchId}`);

      // Находим карточку этого матча в блоке и обновляем её
      const wrappers = playerMatchesBlock.querySelectorAll(".match-wrapper");
      for (const wrapper of wrappers) {
        const matchIdAttr = wrapper.getAttribute("data-match-id");
        if (matchIdAttr == matchId) {
          // Обновляем содержимое карточки
          const oldMatchElement = wrapper.querySelector(".match-card");
          if (oldMatchElement) {
            const newMatchElement = renderMatch(updatedMatch, false);
            newMatchElement.className = "match-card";
            oldMatchElement.replaceWith(newMatchElement);
          }
          break;
        }
      }
    }

    if (activeMatchId === matchId) await loadMatch();
  } catch (err) {}
}


/* ============================================================
   ОТОБРАЖЕНИЕ (UI)
   ============================================================ */

// Строка счета
function createScoreRow(name, sets, current) {
  const row = document.createElement("div");
  row.className = "score-row";
  const nameEl = document.createElement("div");
  nameEl.className = "name";
  nameEl.textContent = name;
  row.appendChild(nameEl);
  sets.forEach(v => {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.textContent = v;
    row.appendChild(cell);
  });
  const currentCell = document.createElement("div");
  currentCell.className = "cell";
  currentCell.textContent = current;
  row.appendChild(currentCell);
  return row;
}

// Рендер матча (карточка)
function renderMatch(m, showControls) {
  const p1 = m.players?.[0] || "P1";
  const p2 = m.players?.[1] || "P2";
  const history = m.history_sets || [];
  const current = m.current_set || {};
  const server = m.server;
  const setsCount = m.sets || [0, 0];  // текущий счёт по сетам

  const p1Sets = history.map(s => s[p1] ?? 0);
  const p2Sets = history.map(s => s[p2] ?? 0);

  const card = document.createElement("div");
  card.className = "card";

  const title = document.createElement("div");
  title.className = "title";
  title.textContent = `Матч №${m.match_id}`;
  card.appendChild(title);

  // Строка счёта для игрока 1
  card.appendChild(createScoreRow(
    p1,
    setsCount[0],           // текущий счёт по сетам
    p1Sets,                 // история сетов
    current[p1] ?? 0,       // текущий гейм
    server === p1           // подаёт ли
  ));

  // Строка счёта для игрока 2
  card.appendChild(createScoreRow(
    p2,
    setsCount[1],
    p2Sets,
    current[p2] ?? 0,
    server === p2
  ));

  if (showControls) {
    const controls = document.createElement("div");
    controls.style.display = "flex";
    controls.style.gap = "10px";
    controls.style.flexWrap = "wrap";
    controls.style.marginTop = "10px";

    const p1Group = document.createElement("div");
    p1Group.style.display = "flex";
    p1Group.style.gap = "5px";

    const btn1Plus = document.createElement("button");
    btn1Plus.textContent = `+1 ${p1}`;
    btn1Plus.onclick = () => addGame(m.match_id, p1, 1);
    p1Group.appendChild(btn1Plus);

    const p2Group = document.createElement("div");
    p2Group.style.display = "flex";
    p2Group.style.gap = "5px";

    const btn2Plus = document.createElement("button");
    btn2Plus.textContent = `+1 ${p2}`;
    btn2Plus.onclick = () => addGame(m.match_id, p2, 1);
    p2Group.appendChild(btn2Plus);

    const undoBtn = document.createElement("button");
    undoBtn.textContent = "↩️ Отмена";
    undoBtn.style.background = "orange";
    undoBtn.onclick = async () => {
      await undoMatchAction(m.match_id);
      const updatedMatch = await request(`${API}/matches/${m.match_id}`);
      const newMatchElement = renderMatch(updatedMatch, true);
      const container = document.getElementById("match");
      if (container) {
        container.innerHTML = "";
        addCloseButton(container, () => {
          container.innerHTML = "";
          activeMatchId = null;
        });
        container.appendChild(newMatchElement);
      }
      // Обновляем блок "Мои матчи" если открыт
      const playerMatchesBlock = document.getElementById("playerMatchesBlock");
      if (playerMatchesBlock && playerMatchesBlock.style.display === "block") {
        const title = playerMatchesBlock.querySelector("h3");
        if (title) {
          const playerName = title.textContent.replace("🎾 Мои матчи", "").trim();
          if (playerName) await showPlayerMatches(playerName);
        }
      }
    };

    controls.appendChild(p1Group);
    controls.appendChild(p2Group);
    controls.appendChild(undoBtn);
    card.appendChild(controls);
  }

  return card;
}

function createScoreRow(name, currentSets, setsHistory, currentGame, isServing) {
  const row = document.createElement("div");
  row.className = "score-row";

  // Имя с подачей
  const nameEl = document.createElement("div");
  nameEl.className = "name";
  nameEl.innerHTML = isServing ? name + " 🎾" : name;
  row.appendChild(nameEl);

  // Текущий счёт по сетам
  const currentSetsCell = document.createElement("div");
  currentSetsCell.className = "cell";
  currentSetsCell.textContent = currentSets;
  currentSetsCell.style.fontWeight = "bold";
  currentSetsCell.style.background = "rgba(53, 255, 138, 0.2)";
  row.appendChild(currentSetsCell);

  // История сетов
  setsHistory.forEach(v => {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.textContent = v;
    row.appendChild(cell);
  });

  // Текущий гейм
  const currentGameCell = document.createElement("div");
  currentGameCell.className = "cell";
  currentGameCell.textContent = currentGame;
  row.appendChild(currentGameCell);

  return row;
}


/* ============================================================
   РАБОТА С ОТКРЫТЫМ МАТЧЕМ
   ============================================================ */

// Открыть матч по ID из поля ввода
async function openMatch() {
  const input = document.getElementById("matchId");
  const id = input.value.trim();
  if (!id) {
    showToast("Введите ID матча", "error");
    return;
  }
  activeMatchId = Number(id);
  const success = await loadMatch();
  if (success) input.value = "";
}

// Загрузить и отобразить открытый матч
async function loadMatch() {
  if (!activeMatchId) return false;
  try {
    const data = await request(`${API}/matches/${activeMatchId}`);
    const container = document.getElementById("match");
    container.innerHTML = "";
    addCloseButton(container, () => {
      container.innerHTML = "";
      activeMatchId = null;
    });
    container.appendChild(renderMatch(data, true));
    return true;
  } catch (err) {
    return false;
  }
}

// Открыть матч по ID (из "Мои матчи")
async function openMatchById(id) {
  const matchIdInput = document.getElementById("matchId");
  matchIdInput.value = id;
  activeMatchId = id;
  await loadMatch();
  document.getElementById("match").scrollIntoView({ behavior: "smooth" });
}


/* ============================================================
   МОИ МАТЧИ (фильтр по игроку)
   ============================================================ */

async function showPlayerMatches(playerName) {
  try {
    const matches = await request(`${API}/matches/`);
    const playerMatches = matches.filter(m => m.players.includes(playerName));
    const block = document.getElementById("playerMatchesBlock");
    block.innerHTML = "";
    block.style.display = "block";

    // Шапка
    const header = document.createElement("div");
    header.style.display = "flex";
    header.style.justifyContent = "space-between";
    header.style.alignItems = "center";
    header.style.marginBottom = "15px";

    const title = document.createElement("h3");
    title.textContent = `🧑 Мои матчи`;
    title.style.margin = "0";
    header.appendChild(title);

    const closeBtn = document.createElement("button");
    closeBtn.textContent = "✕";
    closeBtn.style.background = "orange";
    closeBtn.style.color = "#000";
    closeBtn.style.border = "none";
    closeBtn.style.fontSize = "18px";
    closeBtn.style.cursor = "pointer";
    closeBtn.style.padding = "4px 10px";
    closeBtn.style.borderRadius = "8px";
    closeBtn.onclick = () => {
      block.style.display = "none";
      block.innerHTML = "";
    };
    header.appendChild(closeBtn);
    block.appendChild(header);

    const content = document.createElement("div");
    block.appendChild(content);

    if (playerMatches.length === 0) {
      content.innerHTML = `<div class="card">Нет матчей у игрока ${playerName}</div>`;
      return;
    }

    playerMatches.forEach(m => {
      const wrapper = document.createElement("div");
      wrapper.style.marginBottom = "20px";
      wrapper.setAttribute("data-match-id", m.match_id);
      wrapper.className = "match-wrapper";

      // Карточка матча
      const matchElement = renderMatch(m, false);
      matchElement.className = "match-card";
      wrapper.appendChild(matchElement);

      // Кнопка "Изменить счёт"
      const editBtn = document.createElement("button");
      editBtn.textContent = "✏️ Изменить счёт";
      editBtn.style.marginTop = "8px";
      editBtn.style.marginRight = "8px";

      // Контейнер для контролов (изначально скрыт)
      const controlsDiv = document.createElement("div");
      controlsDiv.style.marginTop = "10px";
      controlsDiv.style.display = "none";
      controlsDiv.style.gap = "8px";
      controlsDiv.style.flexWrap = "wrap";

      // Кнопки изменения счёта (только +1 и отмена)
      const p1 = m.players[0];
      const p2 = m.players[1];

      const btn1Plus = document.createElement("button");
      btn1Plus.textContent = `+1 ${p1}`;
      btn1Plus.onclick = () => addGame(m.match_id, p1, 1);

      const btn2Plus = document.createElement("button");
      btn2Plus.textContent = `+1 ${p2}`;
      btn2Plus.onclick = () => addGame(m.match_id, p2, 1);

      const undoBtn = document.createElement("button");
      undoBtn.textContent = `↩️ Отмена`;
      undoBtn.style.background = "orange";
      undoBtn.onclick = async () => {
        await undoMatchAction(m.match_id);
        // Обновляем карточку матча
        const updatedMatch = await request(`${API}/matches/${m.match_id}`);
        const newMatchElement = renderMatch(updatedMatch, false);
        const oldMatchElement = wrapper.querySelector(".match-card");
        if (oldMatchElement) {
          oldMatchElement.replaceWith(newMatchElement);
          newMatchElement.className = "match-card";
        }
      };

      const closeControlsBtn = document.createElement("button");
      closeControlsBtn.textContent = "❌ Закрыть";
      closeControlsBtn.style.background = "gray";
      closeControlsBtn.onclick = () => {
        controlsDiv.style.display = "none";
      };

      controlsDiv.appendChild(btn1Plus);
      controlsDiv.appendChild(btn2Plus);
      controlsDiv.appendChild(undoBtn);
      controlsDiv.appendChild(closeControlsBtn);

      // Переключение видимости контролов
      editBtn.onclick = () => {
        if (controlsDiv.style.display === "none") {
          controlsDiv.style.display = "flex";
        } else {
          controlsDiv.style.display = "none";
        }
      };

      wrapper.appendChild(editBtn);
      wrapper.appendChild(controlsDiv);
      content.appendChild(wrapper);
    });

    block.scrollIntoView({ behavior: "smooth" });
  } catch (err) {}
}

// Функция отмены действия
async function undoMatchAction(matchId) {
  try {
    await request(`${API}/matches/${matchId}/undo`, {
      method: "POST"
    });
    showToast("Действие отменено", "error");
  } catch (err) {
    showToast("Нечего отменять", "error");
  }
}

async function showRating() {
  try {
    const data = await request(`${API}/players/rating/`);
    const container = document.getElementById("rating");
    container.innerHTML = "";

    addCloseButton(container, () => {
      container.innerHTML = "";
    });

    // Пояснение
    const info = document.createElement("div");
    info.style.marginBottom = "15px";
    info.style.padding = "8px 12px";
    info.style.background = "rgba(255, 255, 255, 0.05)";
    info.style.borderRadius = "8px";
    info.style.fontSize = "14px";
    info.style.color = "var(--muted)";
    info.innerHTML = "ℹ️ 10 очков за выигранный гейм · 100 очков за выигранный сет";
    container.appendChild(info);

    if (data.length === 0) {
      container.innerHTML += `<div class="card">Нет данных</div>`;
      return;
    }

    data.forEach((p, index) => {
      const card = document.createElement("div");
      card.className = "card";
      card.style.display = "flex";
      card.style.justifyContent = "space-between";
      card.style.alignItems = "center";

      const left = document.createElement("div");

      // Добавляем медальки для 1, 2, 3 места
      let medal = "";
      if (index === 0) medal = "🥇 ";
      else if (index === 1) medal = "🥈 ";
      else if (index === 2) medal = "🥉 ";

      left.innerHTML = `${index + 1}. ${p.name}${medal}`;

      const right = document.createElement("div");
      right.textContent = `${p.rating}`;
      right.style.fontWeight = "bold";
      right.style.color = "#35ff8a";

      card.appendChild(left);
      card.appendChild(right);
      container.appendChild(card);
    });

  } catch (err) {}
}