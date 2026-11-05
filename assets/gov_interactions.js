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
    // Update live statutory print date to today's local client date
    const dateSpan = document.getElementById('print-official-date');
    if (dateSpan) {
        const today = new Date();
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const day = String(today.getDate()).padStart(2, '0');
        const month = months[today.getMonth()];
        const year = today.getFullYear();
        dateSpan.innerText = day + '-' + month + '-' + year;
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
window.handleDonutDirect = function(activeEl) {
    if (!activeEl) return;

    let slice = activeEl.closest ? activeEl.closest(".donut-slice") : null;
    let legend = activeEl.closest ? activeEl.closest(".donut-legend-item") : null;
    if (!slice && !legend) {
        if (activeEl.classList && activeEl.classList.contains("donut-slice")) slice = activeEl;
        if (activeEl.classList && activeEl.classList.contains("donut-legend-item")) legend = activeEl;
    }
    const el = slice || legend || activeEl;

    let idx = el.getAttribute("data-index");
    if (idx === null || idx === undefined || idx === "") {
        if (slice) {
            const allSlices = Array.from(document.querySelectorAll(".donut-slice"));
            idx = String(allSlices.indexOf(slice));
        } else if (legend) {
            const allLegends = Array.from(document.querySelectorAll(".donut-legend-item"));
            idx = String(allLegends.indexOf(legend));
        }
    }

    const targetSlice = slice || (idx !== null ? document.querySelector('.donut-slice[data-index="' + idx + '"]') : null);
    const targetLegend = legend || (idx !== null ? document.querySelector('.donut-legend-item[data-index="' + idx + '"]') : null);

    const sector = el.getAttribute("data-sector") || 
                   (targetSlice && targetSlice.getAttribute("data-sector")) || 
                   (targetLegend && targetLegend.getAttribute("data-sector")) || "Sector";

    const shortName = el.getAttribute("data-short") || 
                      (targetSlice && targetSlice.getAttribute("data-short")) || 
                      (targetLegend && targetLegend.getAttribute("data-short")) || 
                      (sector.length > 11 ? sector.split(" ")[0] : sector);

    const val = el.getAttribute("data-val") || 
                (targetSlice && targetSlice.getAttribute("data-val")) || 
                (targetLegend && targetLegend.getAttribute("data-val")) || "0%";

    const color = el.getAttribute("data-color") || 
                  (targetSlice && targetSlice.getAttribute("data-color")) || 
                  (targetLegend && targetLegend.getAttribute("data-color")) || "#142D4E";

    const amt = el.getAttribute("data-amt") || 
                (targetSlice && targetSlice.getAttribute("data-amt")) || 
                (targetLegend && targetLegend.getAttribute("data-amt")) || "";

    const desc = el.getAttribute("data-desc") || 
                 (targetSlice && targetSlice.getAttribute("data-desc")) || 
                 (targetLegend && targetLegend.getAttribute("data-desc")) || "";

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
        centerLbl.textContent = shortName;
        centerLbl.title = sector;
    }

    if (centerSub) {
        let displayAmt = amt;
        if (!displayAmt && desc.includes("(")) {
            displayAmt = desc.split("(")[1].replace(")", "");
        }
        centerSub.textContent = displayAmt || "Active";
        centerSub.style.color = color;
        centerSub.setAttribute("fill", color);
    }

    if (tooltip) {
        const displayAmt = amt || (desc.includes("(") ? desc.split("(")[1].replace(")", "") : "");
        tooltip.textContent = "📊 " + sector + ": " + val + (displayAmt ? " (" + displayAmt + ")" : "");
        tooltip.classList.add("visible");
        clearTimeout(window._donutTooltipTimer);
        window._donutTooltipTimer = setTimeout(() => {
            if (tooltip) tooltip.classList.remove("visible");
        }, 3500);
    }

    // Highlight active slice
    document.querySelectorAll(".donut-slice").forEach(s => s.classList.remove("active-slice"));
    if (targetSlice) {
        targetSlice.classList.add("active-slice");
    } else if (idx !== null) {
        const slices = document.querySelectorAll(".donut-slice");
        if (slices[idx]) slices[idx].classList.add("active-slice");
    }

    // Highlight active legend item
    document.querySelectorAll(".donut-legend-item").forEach(item => item.classList.remove("active-legend"));
    if (targetLegend) {
        targetLegend.classList.add("active-legend");
    } else if (idx !== null) {
        const legends = document.querySelectorAll(".donut-legend-item");
        if (legends[idx]) legends[idx].classList.add("active-legend");
    }
};

function handleDonutInteraction(e) {
    if (!e || !e.target) return;
    let target = e.target;
    if (!target && e.currentTarget) target = e.currentTarget;
    if (target.nodeType === 3) target = target.parentElement;
    if (!target) return;

    let slice = target.closest ? target.closest(".donut-slice") : null;
    let legend = target.closest ? target.closest(".donut-legend-item") : null;

    // Mobile touch point fallback
    if (!slice && !legend) {
        const touch = (e.touches && e.touches[0]) || (e.changedTouches && e.changedTouches[0]);
        if (touch) {
            try {
                const el = document.elementFromPoint(touch.clientX, touch.clientY);
                if (el) {
                    slice = el.closest ? el.closest(".donut-slice") : null;
                    legend = el.closest ? el.closest(".donut-legend-item") : null;
                }
            } catch (_) {}
        }
    }

    if (!slice && !legend) return;
    window.handleDonutDirect(slice || legend);
}

function attachDonutListeners() {
    // Attach directly to slices
    document.querySelectorAll(".donut-slice").forEach(slice => {
        if (!slice._hasDonutListener) {
            slice._hasDonutListener = true;
            slice.style.cursor = "pointer";
            slice.addEventListener("pointerdown", handleDonutInteraction, { passive: true });
            slice.addEventListener("click", handleDonutInteraction, { passive: true });
            slice.addEventListener("touchstart", handleDonutInteraction, { passive: true });
            slice.addEventListener("mouseover", handleDonutInteraction, { passive: true });
        }
    });

    // Attach directly to legend items
    document.querySelectorAll(".donut-legend-item").forEach(item => {
        if (!item._hasDonutListener) {
            item._hasDonutListener = true;
            item.style.cursor = "pointer";
            item.addEventListener("pointerdown", handleDonutInteraction, { passive: true });
            item.addEventListener("click", handleDonutInteraction, { passive: true });
            item.addEventListener("touchstart", handleDonutInteraction, { passive: true });
            item.addEventListener("mouseover", handleDonutInteraction, { passive: true });
        }
    });

    // Also attach to containers for delegated events
    document.querySelectorAll(".donut-markdown-container, .donut-legend-list, .interactive-donut-wrapper").forEach(el => {
        if (!el._hasDonutContainerListener) {
            el._hasDonutContainerListener = true;
            el.addEventListener("pointerdown", handleDonutInteraction, { passive: true });
            el.addEventListener("click", handleDonutInteraction, { passive: true });
            el.addEventListener("touchstart", handleDonutInteraction, { passive: true });
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

document.addEventListener("pointerdown", handleDonutInteraction, { passive: true });
document.addEventListener("click", handleDonutInteraction, { passive: true });
document.addEventListener("touchstart", handleDonutInteraction, { passive: true });
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
