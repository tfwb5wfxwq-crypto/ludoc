(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Révélation au scroll (stagger) ---- */
  var targets = document.querySelectorAll(
    ".hero, .section-head, .card, .sec-title, .prod"
  );

  if (reduce || !("IntersectionObserver" in window)) {
    targets.forEach(function (el) { el.classList.add("in"); });
  } else {
    targets.forEach(function (el) { el.classList.add("reveal"); });
    // décalage progressif au sein de chaque grille
    document.querySelectorAll(".grid, .prod-grid").forEach(function (grid) {
      Array.prototype.forEach.call(grid.children, function (child, i) {
        child.style.setProperty("--d", (i % 14) * 55 + "ms");
      });
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add("in");
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -7% 0px" });
    targets.forEach(function (el) { io.observe(el); });
  }

  if (reduce) return;

  /* ---- Parallax bannière + dérive des orbes (rAF) ---- */
  var hero = document.querySelector(".page-hero");
  var orbs = document.querySelector(".bg-orbs");
  var sy = window.scrollY, mx = 0, my = 0, ticking = false;

  function render() {
    if (hero) hero.style.setProperty("--p", (sy * 0.22).toFixed(1));
    if (orbs) orbs.style.transform =
      "translate3d(" + (mx * 22 - sy * 0.04).toFixed(1) + "px," +
      (my * 22 + sy * 0.06).toFixed(1) + "px,0)";
    ticking = false;
  }
  function request() { if (!ticking) { ticking = true; requestAnimationFrame(render); } }

  window.addEventListener("scroll", function () { sy = window.scrollY; request(); }, { passive: true });
  window.addEventListener("pointermove", function (e) {
    mx = (e.clientX / window.innerWidth) - 0.5;
    my = (e.clientY / window.innerHeight) - 0.5;
    request();
  }, { passive: true });

  /* ---- Tilt léger des cartes au survol ---- */
  var canHover = window.matchMedia("(hover: hover)").matches;
  if (canHover) {
    document.querySelectorAll(".card, .prod").forEach(function (c) {
      c.addEventListener("pointermove", function (e) {
        var r = c.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        c.style.transform =
          "translateY(-6px) perspective(700px) rotateX(" +
          (-py * 4).toFixed(2) + "deg) rotateY(" + (px * 4).toFixed(2) + "deg)";
      });
      c.addEventListener("pointerleave", function () { c.style.transform = ""; });
    });
  }

  render();
})();
