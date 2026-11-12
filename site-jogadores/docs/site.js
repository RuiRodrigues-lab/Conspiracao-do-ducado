// Mapa clicável: tocar num lugar mostra a descrição por baixo do mapa.
(function () {
  var map = document.querySelector(".map");
  var panel = document.getElementById("painel");
  if (!map || !panel) return;

  function show(id, scroll) {
    var card = document.getElementById(id);
    if (!card) return;
    document.querySelectorAll(".pin.active, .place.active").forEach(function (el) { el.classList.remove("active"); });
    var pin = map.querySelector('.pin[data-lugar="' + id + '"]');
    if (pin) pin.classList.add("active");
    card.classList.add("active");
    var copy = card.cloneNode(true);
    var link = copy.querySelector(".ver-no-mapa");
    if (link) link.parentNode.removeChild(link);
    var title = copy.querySelector(".card-top strong");
    var h = document.createElement("h3");
    h.textContent = title ? title.textContent : "";
    panel.innerHTML = "";
    panel.appendChild(h);
    Array.prototype.slice.call(copy.children, 1).forEach(function (el) { panel.appendChild(el); });
    var more = document.createElement("p");
    more.className = "note";
    more.innerHTML = '<a href="#' + id + '">Ver na lista de lugares</a>';
    panel.appendChild(more);
    panel.hidden = false;
    try { history.replaceState(null, "", "#" + id); } catch (e) {}
    if (scroll) map.scrollIntoView({ block: "start" });
  }

  map.addEventListener("click", function (e) {
    var pin = e.target.closest(".pin");
    if (pin) show(pin.getAttribute("data-lugar"), false);
  });
  document.querySelectorAll(".ver-no-mapa").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      show(a.getAttribute("data-lugar"), true);
    });
  });
  if (location.hash.indexOf("#lugar-") === 0) show(location.hash.slice(1), false);
})();

// Filtros por tipo de lugar (mapa e lista).
(function () {
  var buttons = document.querySelectorAll(".filter");
  if (!buttons.length) return;
  buttons.forEach(function (b) {
    b.addEventListener("click", function () {
      var f = b.getAttribute("data-filtro");
      var x = window.scrollX, y = window.scrollY;
      buttons.forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
      document.querySelectorAll(".pin[data-cat], .place[data-cat]").forEach(function (el) {
        el.hidden = !(f === "todos" || el.getAttribute("data-cat") === f);
      });
      // Cada grupo da lista (título + cartões) só aparece se tiver lugares visíveis.
      var alvo = null;
      document.querySelectorAll(".place-list").forEach(function (list) {
        var head = list.previousElementSibling;
        var visivel = list.querySelector(".place:not([hidden])") !== null;
        list.hidden = !visivel;
        if (head && head.tagName === "H3") {
          head.hidden = !visivel;
          if (visivel && !alvo) alvo = head;
        }
      });
      // Um tipo escolhido leva à sua secção em Lugares; "Todos" deixa a página onde está.
      if (f !== "todos" && alvo) alvo.scrollIntoView({ block: "start", behavior: "instant" });
      else window.scrollTo(x, y);
    });
  });
})();
