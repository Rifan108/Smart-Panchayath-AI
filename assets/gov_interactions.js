/**
 * Smart AI Panchayat – High-Performance Institutional Interactions
 * Provides Native 60-120fps Hardware-Accelerated Scrolling with Lenis,
 * Instant 0ms Visual Navigation Feedback, GSAP Lifecycle Cleanup,
 * Zero-Opacity-Locking Transitions, and Accessibility Controls.
 */

// ─── 0. Lenis Smooth Scrolling Singleton (respects reduced-motion) ───
window._lenisInstance = window._lenisInstance || null;

function initLenis() {
    if (typeof Lenis === "undefined") return;
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return; // Respect accessibility settings
    }
    if (window._lenisInstance) return;

    try {
        window._lenisInstance = new Lenis({
            duration: 0.45,
            easing: (t) => 1 - Math.pow(1 - t, 3), // Responsive cubic-out without input delay
            orientation: 'vertical',
            gestureOrientation: 'vertical',
            smoothWheel: true,
            wheelMultiplier: 1.0,
            touchMultiplier: 1.0,
            syncTouch: false, // Use native touch acceleration on mobile/touch screens
        });

        if (typeof gsap !== "undefined") {
            gsap.ticker.add((time) => {
                if (window._lenisInstance) window._lenisInstance.raf(time * 1000);
            });
            gsap.ticker.lagSmoothing(500, 33);
        } else {
            function raf(time) {
                if (window._lenisInstance) window._lenisInstance.raf(time);
                requestAnimationFrame(raf);
            }
            requestAnimationFrame(raf);
        }
    } catch (e) {
        console.warn("Lenis initialization skipped:", e);
    }
}

// ─── 1. Accessibility Utility Functions ───
window.adjustFontSize = function (action) {
    const body = document.body;
    if (action === 'increase') {
        body.classList.remove('font-size-small');
        body.classList.add('font-size-large');
    } else if (action === 'decrease') {
        body.classList.remove('font-size-large');
        body.classList.add('font-size-small');
    } else {
        body.classList.remove('font-size-large', 'font-size-small');
    }
};

window.toggleHighContrast = function () {
    document.body.classList.toggle('high-contrast');
};

window.printReport = function () {
    document.body.classList.add('printing-official-report');
    const docEl = document.querySelector('.official-print-document');
    if (docEl) {
        docEl.style.display = 'block';
        docEl.style.visibility = 'visible';
    }
    window.print();
    setTimeout(function () {
        document.body.classList.remove('printing-official-report');
    }, 1500);
};

window.addEventListener('afterprint', function () {
    document.body.classList.remove('printing-official-report');
});

// ─── 2. Delegated Navigation & Accessibility Click Listener ───
document.addEventListener("click", function (e) {
    if (!e.target) return;

    // Accessibility Controls
    if (e.target.id === "btn-font-dec" || e.target.closest("#btn-font-dec")) {
        window.adjustFontSize('decrease');
    } else if (e.target.id === "btn-font-norm" || e.target.closest("#btn-font-norm")) {
        window.adjustFontSize('reset');
    } else if (e.target.id === "btn-font-inc" || e.target.closest("#btn-font-inc")) {
        window.adjustFontSize('increase');
    } else if (e.target.id === "btn-contrast-toggle" || e.target.closest("#btn-contrast-toggle")) {
        window.toggleHighContrast();
    } else if (e.target.id === "btn-print-briefing" || e.target.closest("#btn-print-briefing")) {
        window.printReport();
    }

    // Instant Visual Feedback on Navigation Links (0ms response)
    const navLink = e.target.closest(".nav-pill-link, a.nav-link, a.btn-officer-portal");
    if (navLink) {
        // Scroll to top instantly
        if (window._lenisInstance) {
            window._lenisInstance.scrollTo(0, { immediate: true });
        } else {
            window.scrollTo(0, 0);
        }

        // If it's a main pill link, immediately mark active
        if (navLink.classList.contains("nav-pill-link")) {
            document.querySelectorAll(".nav-pill-link").forEach((el) => el.classList.remove("active"));
            navLink.classList.add("active");
        }
    }
});

// ─── 3. GSAP Institutional Smooth Entrances (Zero lag, Snappy, Clean Lifecycle) ───
function triggerPageEntranceAnimations() {
    if (typeof gsap === "undefined") return;
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    // Kill any active tweens to prevent memory leaks and conflicts
    gsap.killTweensOf(".hero-main-title, .hero-main-description, .hero-action-buttons, .state-card-recreated, .horizontal-stat-card, .about-hero-title");

    const heroTitle = document.querySelector(".hero-main-title");
    if (heroTitle) {
        gsap.fromTo(heroTitle, 
            { y: 12, opacity: 0.2 },
            { y: 0, opacity: 1, duration: 0.25, ease: "power1.out", clearProps: "all" }
        );

        const heroDesc = document.querySelector(".hero-main-description");
        if (heroDesc) {
            gsap.fromTo(heroDesc,
                { y: 8, opacity: 0.3 },
                { y: 0, opacity: 1, duration: 0.2, ease: "power1.out", clearProps: "all" }
            );
        }

        const heroActions = document.querySelector(".hero-action-buttons");
        if (heroActions) {
            gsap.fromTo(heroActions,
                { y: 6, opacity: 0.4 },
                { y: 0, opacity: 1, duration: 0.2, ease: "power1.out", clearProps: "all" }
            );
        }
    }

    // State cards subtle entrance (no long delay, cards remain visible)
    const stateCards = document.querySelectorAll(".state-card-recreated");
    if (stateCards.length > 0) {
        gsap.fromTo(stateCards,
            { y: 8, opacity: 0.4 },
            { y: 0, opacity: 1, duration: 0.2, stagger: 0.02, ease: "power1.out", clearProps: "all" }
        );
    }

    // Horizontal KPIs
    const kpis = document.querySelectorAll(".horizontal-stat-card");
    if (kpis.length > 0) {
        gsap.fromTo(kpis,
            { y: 8, opacity: 0.4 },
            { y: 0, opacity: 1, duration: 0.2, stagger: 0.02, ease: "power1.out", clearProps: "all" }
        );
    }
}

// ─── 4. High-Performance Route Transition Handler ───
let lastHandledPath = window.location.pathname;

function handleRouteChange() {
    // Scroll to top immediately on page change
    if (window._lenisInstance) {
        window._lenisInstance.scrollTo(0, { immediate: true });
    } else {
        window.scrollTo(0, 0);
    }

    // Trigger subtle entrance animations without blocking
    requestAnimationFrame(triggerPageEntranceAnimations);
}

// Window load initialization
window.addEventListener("DOMContentLoaded", () => {
    initLenis();
    requestAnimationFrame(triggerPageEntranceAnimations);

    // Watch for Dash SPA page-content updates safely
    const pageContentEl = document.getElementById("page-content");
    if (pageContentEl) {
        let timer = null;
        const pageObserver = new MutationObserver(() => {
            if (timer) clearTimeout(timer);
            timer = setTimeout(() => {
                const currentPath = window.location.pathname;
                if (currentPath !== lastHandledPath) {
                    lastHandledPath = currentPath;
                    handleRouteChange();
                }
            }, 30);
        });
        pageObserver.observe(pageContentEl, { childList: true });
    }
});

// Popstate listener for forward/backward browser buttons
window.addEventListener("popstate", () => {
    handleRouteChange();
});

// ─── 5. Interactive Donut Chart Tap / Click / Hover Value Inspector ───
function handleDonutInteraction(e) {
    if (!e || !e.target) return;
    const target = e.target;

    // Fast path: if not an SVG element or legend item, exit immediately (0.00ms)
    const isSvgEl = target.nodeName === "path" || target.nodeName === "circle" || target.nodeName === "text";
    const isLegend = target.classList && (target.classList.contains("donut-legend-item") || (target.closest && target.closest(".donut-legend-item")));
    if (!isSvgEl && !isLegend) {
        return;
    }

    let slice = target.closest ? target.closest(".donut-slice") : null;
    let legend = target.closest ? target.closest(".donut-legend-item") : null;

    if (!slice && !legend && e.touches && e.touches.length > 0) {
        const el = document.elementFromPoint(e.touches[0].clientX, e.touches[0].clientY);
        if (el && el.closest) {
            slice = el.closest(".donut-slice");
            legend = el.closest(".donut-legend-item");
        }
    }
    if (!slice && !legend) return;

    let targetSector = "";
    let targetSlice = null;

    if (slice) {
        targetSlice = slice;
        targetSector = slice.getAttribute("data-sector");
    } else if (legend) {
        targetSector = legend.getAttribute("data-sector");
        targetSlice = document.querySelector(`.donut-slice[data-sector="${targetSector}"]`);
    }

    if (!targetSlice) return;

    const sector = targetSlice.getAttribute("data-sector") || "Water";
    const val = targetSlice.getAttribute("data-val") || "32%";
    const color = targetSlice.getAttribute("data-color") || "#142D4E";
    const desc = targetSlice.getAttribute("data-desc") || "";

    const centerVal = document.getElementById("donut-center-val");
    const centerLbl = document.getElementById("donut-center-lbl");
    const centerSub = document.getElementById("donut-center-sub");
    const tooltip = document.getElementById("donut-hover-tooltip");

    if (centerVal) {
        centerVal.textContent = val;
        centerVal.style.color = color;
        centerVal.setAttribute("fill", color);
        centerVal.classList.remove("donut-pop");
        void centerVal.offsetWidth;
        centerVal.classList.add("donut-pop");
    }
    if (centerLbl) {
        centerLbl.textContent = sector;
    }
    if (centerSub) {
        centerSub.textContent = desc.includes("(") ? desc.split("(")[1].replace(")", "") : "Active";
        centerSub.style.color = color;
        centerSub.setAttribute("fill", color);
    }
    if (tooltip) {
        tooltip.textContent = `📊 ${sector}: ${val} (${desc.includes("(") ? desc.split("(")[1].replace(")", "") : desc})`;
        tooltip.classList.add("visible");
        clearTimeout(window._donutTooltipTimer);
        window._donutTooltipTimer = setTimeout(() => {
            if (tooltip) tooltip.classList.remove("visible");
        }, 3500);
    }

    // Highlight active slice
    document.querySelectorAll(".donut-slice").forEach(s => s.classList.remove("active-slice"));
    targetSlice.classList.add("active-slice");

    // Also highlight matching legend item
    document.querySelectorAll(".donut-legend-item").forEach(item => {
        if (item.getAttribute("data-sector") === targetSector) {
            item.classList.add("active-legend");
        } else {
            item.classList.remove("active-legend");
        }
    });
}

function attachDonutListeners() {
    document.querySelectorAll(".donut-markdown-container, .donut-legend-list").forEach(el => {
        if (!el._hasDonutListener) {
            el._hasDonutListener = true;
            el.addEventListener("mouseover", handleDonutInteraction, { passive: true });
        }
    });
    // Set native lazy loading on images dynamically
    document.querySelectorAll("img").forEach(img => {
        if (!img.hasAttribute("loading")) {
            img.setAttribute("loading", "lazy");
            img.setAttribute("decoding", "async");
        }
    });
}

document.addEventListener("pointerdown", handleDonutInteraction);
document.addEventListener("click", handleDonutInteraction);
document.addEventListener("DOMContentLoaded", attachDonutListeners);

if (typeof MutationObserver !== "undefined") {
    const donutObserver = new MutationObserver(() => {
        attachDonutListeners();
    });
    if (document.body) {
        donutObserver.observe(document.body, { childList: true, subtree: true });
    } else {
        document.addEventListener("DOMContentLoaded", () => {
            donutObserver.observe(document.body, { childList: true, subtree: true });
        });
    }
}

