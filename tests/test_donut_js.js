/**
 * Node.js test simulating DOM interactions with the Donut Chart and Legend
 */
const fs = require('fs');
const path = require('path');
const assert = require('assert');

// Read gov_interactions.js
const jsCode = fs.readFileSync(path.join(__dirname, '..', 'assets', 'gov_interactions.js'), 'utf8');

// Minimal DOM mock
class MockElement {
    constructor(tagName, id = '', className = '') {
        this.tagName = tagName.toUpperCase();
        this.nodeName = this.tagName;
        this.id = id;
        this.className = className;
        this.classList = {
            _classes: new Set(className.split(' ').filter(Boolean)),
            contains(cls) { return this._classes.has(cls); },
            add(cls) { this._classes.add(cls); },
            remove(cls) { this._classes.delete(cls); }
        };
        this.attributes = {};
        this.style = {};
        this.textContent = '';
        this.parentElement = null;
        this.children = [];
    }

    setAttribute(key, val) { this.attributes[key] = String(val); }
    getAttribute(key) { return this.attributes[key] !== undefined ? this.attributes[key] : null; }
    hasAttribute(key) { return key in this.attributes; }

    closest(selector) {
        let cur = this;
        while (cur) {
            if (selector.startsWith('.') && cur.classList.contains(selector.slice(1))) return cur;
            if (selector.startsWith('#') && cur.id === selector.slice(1)) return cur;
            cur = cur.parentElement;
        }
        return null;
    }

    addEventListener() {}
}

const docElements = {};
const elementsByClass = {};

function registerEl(el) {
    if (el.id) docElements[el.id] = el;
    el.classList._classes.forEach(cls => {
        if (!elementsByClass[cls]) elementsByClass[cls] = [];
        elementsByClass[cls].push(el);
    });
}

// Build mock document
const centerVal = new MockElement('span', 'donut-center-val', 'donut-center-val');
const centerLbl = new MockElement('span', 'donut-center-lbl', 'donut-center-lbl');
const centerSub = new MockElement('span', 'donut-center-sub', 'donut-center-sub');
const tooltip = new MockElement('div', 'donut-hover-tooltip', 'donut-tooltip');

registerEl(centerVal);
registerEl(centerLbl);
registerEl(centerSub);
registerEl(tooltip);

// Create 5 slices
const slices = [];
const legends = [];
const sectors = [
    { name: "Economic Development", pct: "16%", amt: "₹4.7 Cr", color: "#142D4E" },
    { name: "Agriculture & Food Security", pct: "15%", amt: "₹4.4 Cr", color: "#245B91" },
    { name: "Environment & Disaster Mgmt", pct: "14%", amt: "₹4.1 Cr", color: "#E99A36" },
    { name: "Health & Sanitation", pct: "14%", amt: "₹4.1 Cr", color: "#25845A" },
    { name: "Others", pct: "41%", amt: "₹12.1 Cr", color: "#64748B" },
];

sectors.forEach((sec, idx) => {
    const slice = new MockElement('path', '', `donut-slice ${idx === 0 ? 'active-slice' : ''}`);
    slice.setAttribute('data-index', idx);
    slice.setAttribute('data-sector', sec.name);
    slice.setAttribute('data-val', sec.pct);
    slice.setAttribute('data-color', sec.color);
    slice.setAttribute('data-amt', sec.amt);
    slices.push(slice);
    registerEl(slice);

    const legend = new MockElement('div', '', `donut-legend-item ${idx === 0 ? 'active-legend' : ''}`);
    legend.setAttribute('data-index', idx);
    legend.setAttribute('data-sector', sec.name);
    legend.setAttribute('data-val', sec.pct);
    legend.setAttribute('data-color', sec.color);
    legend.setAttribute('data-amt', sec.amt);

    const spanText = new MockElement('span', '', 'legend-label');
    spanText.textContent = sec.name;
    spanText.parentElement = legend;
    legend.children.push(spanText);

    legends.push(legend);
    registerEl(legend);
});

// Setup global mock
global.window = { location: { pathname: '/dashboard/' }, addEventListener() {} };
global.document = {
    getElementById(id) { return docElements[id] || null; },
    querySelector(sel) {
        if (sel.startsWith('#')) return docElements[sel.slice(1)] || null;
        if (sel.includes('[data-index="')) {
            const match = sel.match(/\.([a-z-]+)\[data-index="(\d+)"\]/);
            if (match) {
                const cls = match[1];
                const idx = match[2];
                return (elementsByClass[cls] || []).find(e => e.getAttribute('data-index') === idx) || null;
            }
        }
        return null;
    },
    querySelectorAll(sel) {
        if (sel.startsWith('.')) {
            const cls = sel.slice(1).split(',')[0].trim();
            return elementsByClass[cls] || [];
        }
        return [];
    },
    addEventListener() {},
    body: new MockElement('body')
};

// Evaluate the JS code in context
eval(jsCode);

console.log("▶ Testing initial state...");
assert.strictEqual(typeof handleDonutInteraction, 'function', 'handleDonutInteraction must be defined');

console.log("▶ Simulating TAP on Legend Item 1 (Agriculture & Food Security)...");
const targetSpan = legends[1].children[0]; // tap inside the span of the legend item
handleDonutInteraction({ target: targetSpan });

console.log("  Center val:", centerVal.textContent);
console.log("  Center lbl:", centerLbl.textContent);
console.log("  Center sub:", centerSub.textContent);
console.log("  Center color:", centerVal.style.color);

assert.strictEqual(centerVal.textContent, "15%", "Center value should update to 15%");
assert.strictEqual(centerVal.style.color, "#245B91", "Center value color should update to #245B91");
assert.ok(centerLbl.textContent.includes("Agriculture"), "Center label should show Agriculture");
assert.strictEqual(centerSub.textContent, "₹4.4 Cr", "Center amount should update to ₹4.4 Cr");
assert.ok(slices[1].classList.contains("active-slice"), "Slice 1 must be active");
assert.ok(!slices[0].classList.contains("active-slice"), "Slice 0 must not be active");
assert.ok(legends[1].classList.contains("active-legend"), "Legend 1 must be active");
assert.ok(!legends[0].classList.contains("active-legend"), "Legend 0 must not be active");

console.log("▶ Simulating TAP on Slice 4 (Others 41%)...");
handleDonutInteraction({ target: slices[4] });

console.log("  Center val:", centerVal.textContent);
console.log("  Center lbl:", centerLbl.textContent);
console.log("  Center sub:", centerSub.textContent);

assert.strictEqual(centerVal.textContent, "41%", "Center value should update to 41%");
assert.strictEqual(centerVal.style.color, "#64748B", "Center value color should update to #64748B");
assert.strictEqual(centerLbl.textContent, "Others", "Center label should show Others");
assert.strictEqual(centerSub.textContent, "₹12.1 Cr", "Center amount should update to ₹12.1 Cr");
assert.ok(slices[4].classList.contains("active-slice"), "Slice 4 must be active");
assert.ok(legends[4].classList.contains("active-legend"), "Legend 4 must be active");

console.log("\n✅ ALL DONUT TAP & INTERACTION TESTS PASSED PERFECTLY!");
