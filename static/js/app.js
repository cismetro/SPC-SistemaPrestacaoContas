const toastStack = document.getElementById("toast-stack");

function toast(message, type = "info") {
  if (!toastStack) return;
  const el = document.createElement("div");
  el.className = "toast";
  el.setAttribute("role", "status");
  el.textContent = message;
  if (type === "success") el.style.borderLeftColor = "#79b24a";
  if (type === "danger") el.style.borderLeftColor = "#e81d51";
  if (type === "warning") el.style.borderLeftColor = "#f2823c";
  toastStack.appendChild(el);
  setTimeout(() => el.remove(), 4600);
}

document.querySelectorAll("[data-flash]").forEach((n) => {
  toast(n.dataset.flash, n.dataset.type || "info");
});

const sidebar = document.querySelector(".sidebar");
const toggle = document.querySelector(".menu-toggle");
if (toggle && sidebar) {
  toggle.addEventListener("click", () => sidebar.classList.toggle("open"));
}

document.querySelectorAll("[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (ev) => {
    if (!window.confirm(form.dataset.confirm)) ev.preventDefault();
  });
});
