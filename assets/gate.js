(function () {
  var c = window.CC_GATE;
  if (!c || !c.endpoint) return;
  var ok = false;
  try { ok = localStorage.getItem(c.storageKey) === "1"; } catch (e) {}
  if (/[?&]ccpass=1/.test(location.search)) { try { localStorage.setItem(c.storageKey, "1"); } catch (e) {} ok = true; }
  if (ok) return;
  var css = ".ccg{position:fixed;inset:0;z-index:99999;background:rgba(19,32,43,.55);display:flex;align-items:center;justify-content:center;padding:16px;font-family:Inter,system-ui,sans-serif}" +
    ".ccg-box{background:#fff;border-radius:12px;max-width:380px;width:100%;overflow:hidden;color:#13202B}" +
    ".ccg-top{background:#E6F6FF;border-bottom:4px solid #66C4FF;padding:16px;display:flex;gap:12px;align-items:center}" +
    ".ccg-logo{width:40px;height:40px;border-radius:10px;background:#1E6FD9;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:500}" +
    ".ccg-top b{font-weight:500;font-size:17px}" +
    ".ccg-b{padding:16px}.ccg-b p{margin:0 0 12px;font-size:14px;line-height:1.5;color:#3A4D5C}" +
    ".ccg-b input[type=email]{width:100%;box-sizing:border-box;font:inherit;font-size:16px;padding:10px 12px;border:1px solid #BFD9EE;border-radius:8px;margin-bottom:10px}" +
    ".ccg-b button{width:100%;font:inherit;font-size:15px;font-weight:500;background:#1E6FD9;color:#fff;border:0;border-radius:8px;padding:11px;cursor:pointer}" +
    ".ccg-err{color:#A32D2D;font-size:13px;margin:0 0 8px;min-height:0}.ccg-hp{position:absolute;left:-9999px}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  var d = document.createElement("div"); d.className = "ccg"; d.setAttribute("role", "dialog"); d.setAttribute("aria-modal", "true");
  d.innerHTML = '<form class="ccg-box" novalidate><div class="ccg-top"><div class="ccg-logo">CC</div><b></b></div><div class="ccg-b"><p class="ccg-body"></p>' +
    '<p class="ccg-err" role="alert"></p><input type="email" name="' + c.field + '" placeholder="name@email.com" autocomplete="email" aria-label="Email address" required>' +
    '<input class="ccg-hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true"><button type="submit"></button></div></form>';
  d.querySelector("b").textContent = c.title; d.querySelector(".ccg-body").textContent = c.body; d.querySelector("button").textContent = c.button;
  var prevOverflow = document.documentElement.style.overflow;
  function mount() { document.body.appendChild(d); document.documentElement.style.overflow = "hidden"; d.querySelector("input[type=email]").focus(); }
  if (document.body) mount(); else document.addEventListener("DOMContentLoaded", mount);
  var form = d.querySelector("form"), err = d.querySelector(".ccg-err");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var email = form.elements[c.field].value.trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { err.textContent = "Enter a valid email address"; return; }
    if (form.elements.website.value) return;
    err.textContent = "";
    var done = function () {
      try { localStorage.setItem(c.storageKey, "1"); } catch (x) {}
      document.documentElement.style.overflow = prevOverflow; d.remove();
    };
    var body = new URLSearchParams(); body.set(c.field, email);
    fetch(c.endpoint, { method: "POST", mode: "no-cors", body: body }).then(done, done);
  });
})();
