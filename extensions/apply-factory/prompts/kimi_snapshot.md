# Kimi: capture form state before submit

Run this JavaScript in the browser tab to snapshot every visible form field.
Save the returned JSON to the path specified by the caller.

```javascript
(() => {
  const labelFor = (el) => {
    if (el.id) {
      const l = document.querySelector(`label[for="${el.id}"]`);
      if (l) return l.innerText.trim();
    }
    const wrap = el.closest('label');
    if (wrap) return wrap.innerText.trim();
    if (el.getAttribute('aria-label')) return el.getAttribute('aria-label').trim();
    const labelledBy = el.getAttribute('aria-labelledby');
    if (labelledBy) {
      const l = document.getElementById(labelledBy);
      if (l) return l.innerText.trim();
    }
    const fs = el.closest('fieldset');
    if (fs) {
      const lg = fs.querySelector('legend');
      if (lg) return lg.innerText.trim();
    }
    return el.placeholder || el.name || '';
  };

  const fieldType = (el) => {
    if (el.tagName === 'TEXTAREA') return 'textarea';
    if (el.tagName === 'SELECT') return 'select';
    if (el.type === 'radio') return 'radio';
    if (el.type === 'checkbox') return 'checkbox';
    if (el.type === 'file') return 'file';
    if (el.type === 'hidden') return 'hidden';
    return 'text';
  };

  const groups = {};
  const fields = [];

  document.querySelectorAll('input, select, textarea').forEach((el) => {
    const type = fieldType(el);
    const label = labelFor(el);
    if (!label) return;

    if (type === 'radio') {
      const key = el.name || label;
      if (!groups[key]) groups[key] = { label, field_type: 'radio', options: [], value: null };
      const optLabel = labelFor(el) || el.value;
      groups[key].options.push(optLabel);
      if (el.checked) groups[key].value = optLabel;
      return;
    }
    if (type === 'checkbox') {
      fields.push({ label, field_type: 'checkbox',
                    value: el.checked ? 'Yes' : 'No', options: ['Yes', 'No'] });
      return;
    }
    if (type === 'select') {
      const opts = Array.from(el.options).map((o) => o.text.trim()).filter(Boolean);
      fields.push({ label, field_type: 'select',
                    value: el.options[el.selectedIndex]?.text?.trim() || '', options: opts });
      return;
    }
    if (type === 'file') {
      fields.push({ label, field_type: 'file',
                    value: el.files.length ? el.files[0].name : '' });
      return;
    }
    if (type === 'hidden') return;
    fields.push({ label, field_type: type, value: el.value || '' });
  });

  Object.values(groups).forEach((g) => fields.push(g));

  return {
    url: location.href,
    captured_at: new Date().toISOString(),
    fields,
  };
})();
```

After running, merge in the `was_prefilled` and `prefilled_value` fields from
your internal record of what you filled in Phase 1. Final shape:

```json
{
  "url": "https://...",
  "captured_at": "2026-...",
  "fields": [
    {
      "label": "Are you an Indian Citizen?",
      "field_type": "radio",
      "value": "Yes",
      "options": ["Yes", "No"],
      "was_prefilled": false,
      "prefilled_value": null
    }
  ]
}
```
