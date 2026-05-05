const moduleData = Array.isArray(window.moduleMeta) ? window.moduleMeta : [];
const moduleMap = Object.fromEntries(moduleData.map((item) => [item.key, item]));
const select = document.getElementById('module-select');

function syncModuleFields() {
    if (!select) {
        return;
    }
    const current = moduleMap[select.value];
    if (!current) {
        return;
    }
    const metricLabel = document.getElementById('metric-label');
    const amountLabel = document.getElementById('amount-label');
    const unitInput = document.getElementById('unit-input');
    if (metricLabel) {
        metricLabel.textContent = current.primary_metric_label;
    }
    if (amountLabel) {
        amountLabel.textContent = current.amount_label;
    }
    if (unitInput && !unitInput.value) {
        unitInput.value = current.default_unit;
    }
}

if (select) {
    select.addEventListener('change', syncModuleFields);
    syncModuleFields();
}
