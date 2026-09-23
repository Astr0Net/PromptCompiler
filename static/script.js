const categoryNames = {
    'Text-out models': 'مدل‌های متنی (Text)',
    'Multi-modal generative models': 'مدل‌های چندحالته',
    'Live API': 'Live API',
    'Other models': 'سایر مدل‌ها',
    'Agents': 'Agents'
};

const resultCategoryNames = {
    image_generation: '🖼️ ساخت تصویر',
    research: '📚 ریسرچ / تحقیق',
    coding: '💻 برنامه‌نویسی',
    debugging: '🐛 دیباگ / رفع خطا',
    writing: '✍️ نوشتن',
    translation: '🔁 ترجمه',
    data_analysis: '📊 تحلیل داده',
    planning: '🗺️ برنامه‌ریزی',
    automation: '🤖 اتوماسیون',
    general: '📋 عمومی'
};

const resultCategoryLabels = {
    image_generation: 'image_generation',
    research: 'research',
    coding: 'coding',
    debugging: 'debugging',
    writing: 'writing',
    translation: 'translation',
    data_analysis: 'data_analysis',
    planning: 'planning',
    automation: 'automation',
    general: 'general'
};

const DEFAULT_MODEL = window.DEFAULT_MODEL || 'gemini-3.5-flash';

let MODELS = [];
let usageData = null;

document.addEventListener('DOMContentLoaded', function () {
    const translateBtn = document.getElementById('translate-btn');
    const copyBtn = document.getElementById('copy-btn');
    const manageSettings = document.getElementById('manage-settings');
    const closeModal = document.getElementById('close-modal');
    const settingsModal = document.getElementById('settings-modal');
    const settingsForm = document.getElementById('settings-form');
    const modelSelect = document.getElementById('model-select');
    const activeModel = document.getElementById('active-model');
    const toast = document.getElementById('toast');
    const output = document.getElementById('output');
    const outputPersian = document.getElementById('output-persian');
    const copyPersianBtn = document.getElementById('copy-persian-btn');
    const purpose = document.getElementById('purpose');
    const suggestionsList = document.getElementById('suggestions-list');
    const categoryBadge = document.getElementById('category-badge');
    const subcategoryBadge = document.getElementById('subcategory-badge');
    const requirementsList = document.getElementById('requirements-list');
    const assumptionsList = document.getElementById('assumptions-list');
    const missingList = document.getElementById('missing-list');
    const usageContent = document.getElementById('usage-content');
    const toggleSidebar = document.getElementById('toggle-sidebar');
    const closeSidebar = document.getElementById('close-sidebar');
    const sidebar = document.getElementById('usage-sidebar');
    const sidebarBackdrop = document.getElementById('sidebar-backdrop');
    const usageHeaderTotal = document.querySelector('.usage-header-total');
    const usageHeaderRequests = document.querySelector('.usage-header-requests');

    let currentResult = null;
    let lastRequestModel = '';

    function showToast(message) {
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }

    function formatTokens(n) {
        if (n === null || n === undefined) return '—';
        if (n >= 1e6) return (n / 1e6).toFixed(2).replace(/\.00$/, '') + 'M';
        if (n >= 1e3) return (n / 1e3).toFixed(1).replace(/\.0$/, '') + 'K';
        return String(n);
    }

    function fmtInt(n) {
        return (n || 0).toLocaleString('fa-IR');
    }

    function openSidebar() {
        sidebar.classList.add('open');
        sidebarBackdrop.style.display = 'block';
        toggleSidebar.setAttribute('aria-expanded', 'true');
    }

    function closeSidebarFn() {
        sidebar.classList.remove('open');
        sidebarBackdrop.style.display = 'none';
        toggleSidebar.setAttribute('aria-expanded', 'false');
    }

    toggleSidebar.addEventListener('click', openSidebar);
    closeSidebar.addEventListener('click', closeSidebarFn);
    sidebarBackdrop.addEventListener('click', closeSidebarFn);

    async function fetchModels() {
        try {
            const resp = await fetch('/models');
            MODELS = await resp.json();
            populateModelSelect();
            updateActiveModel(modelSelect.value);
        } catch (e) {
            showToast('خطا در دریافت لیست مدل‌ها');
        }
    }

    function populateModelSelect() {
        modelSelect.innerHTML = '';
        const groups = {};
        MODELS.forEach(m => (groups[m.category] = groups[m.category] || []).push(m));

        const enabledGroup = document.createElement('optgroup');
        enabledGroup.label = 'مدل‌های قابل استفاده (Text — generateContent)';

        const disabledGroup = document.createElement('optgroup');
        disabledGroup.label = 'سایر مدل‌ها (غیرقابل استفاده در این اپ)';
        let hasDisabled = false;

        Object.keys(groups).forEach(cat => {
            groups[cat].forEach(m => {
                const o = document.createElement('option');
                o.value = m.id;
                if (m.generate) {
                    o.textContent = m.name;
                    enabledGroup.appendChild(o);
                } else {
                    const note = m.note ? ' — ' + m.note : '';
                    o.textContent = m.name + ' ✕' + note;
                    o.disabled = true;
                    disabledGroup.appendChild(o);
                    hasDisabled = true;
                }
            });
        });

        modelSelect.appendChild(enabledGroup);
        if (hasDisabled) modelSelect.appendChild(disabledGroup);

        let foundDefault = false;
        for (let i = 0; i < modelSelect.options.length; i++) {
            if (modelSelect.options[i].value === DEFAULT_MODEL && !modelSelect.options[i].disabled) {
                modelSelect.selectedIndex = i;
                foundDefault = true;
                break;
            }
        }
        if (!foundDefault) {
            modelSelect.selectedIndex = 0;
        }
    }

    function getModelName(id) {
        const m = MODELS.find(x => x.id === id);
        return m ? m.name : id;
    }

    function updateActiveModel(id) {
        activeModel.textContent = getModelName(id);
    }

    modelSelect.addEventListener('change', function () {
        updateActiveModel(modelSelect.value);
        renderUsage();
    });

    function parseResult(content) {
        try {
            const cleaned = content.replace(/```json\n?/g, '').replace(/```/g, '').trim();
            const parsed = JSON.parse(cleaned);
            return {
                detected_category: parsed.detected_category || 'general',
                detected_subcategory: parsed.detected_subcategory || parsed.detectedSubcategory || '',
                detected_purpose: parsed.detected_purpose || '',
                persian_prompt: parsed.persian_prompt || parsed.persianPrompt || '',
                english_prompt: parsed.english_prompt || parsed.englishPrompt || content,
                preserved_requirements: parsed.preserved_requirements || [],
                assumptions: parsed.assumptions || [],
                missing_information: parsed.missing_information || [],
                suggestions: parsed.suggestions || []
            };
        } catch (e) {
            return {
                detected_category: 'general',
                detected_subcategory: '',
                detected_purpose: '',
                persian_prompt: '',
                english_prompt: content,
                preserved_requirements: [],
                assumptions: [],
                missing_information: [],
                suggestions: []
            };
        }
    }

    function renderAnalysisList(container, items) {
        container.innerHTML = '';
        if (!items || !items.length) {
            const div = document.createElement('div');
            div.className = 'analysis-empty';
            div.textContent = 'موردی ثبت نشده است.';
            container.appendChild(div);
            return;
        }
        items.forEach(function (s) {
            const div = document.createElement('div');
            div.className = 'analysis-item';
            div.textContent = s;
            container.appendChild(div);
        });
    }

    translateBtn.addEventListener('click', async function () {
        const prompt = document.getElementById('persian-prompt').value.trim();
        if (!prompt) {
            showToast('لطفاً یک پرامپت فارسی بنویس');
            return;
        }

        const modelId = modelSelect.value;
        lastRequestModel = modelId;

        translateBtn.disabled = true;
        translateBtn.textContent = 'در حال تبدیل...';

        try {
            const resp = await fetch('/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt, model: modelId })
            });

            const data = await resp.json();

            if (!resp.ok) {
                showToast(data.error || 'خطا در تبدیل');
                return;
            }

            currentResult = data.parsed || parseResult(data.result);

            categoryBadge.textContent = resultCategoryNames[currentResult.detected_category] || resultCategoryLabels[currentResult.detected_category] || 'عمومی';
            if (currentResult.detected_subcategory) {
                subcategoryBadge.textContent = currentResult.detected_subcategory;
                subcategoryBadge.classList.remove('hidden');
            } else {
                subcategoryBadge.textContent = '';
                subcategoryBadge.classList.add('hidden');
            }
            purpose.textContent = currentResult.detected_purpose || '';
            outputPersian.textContent = currentResult.persian_prompt || '—';
            output.textContent = currentResult.english_prompt;

            if (!currentResult.persian_prompt) {
                copyPersianBtn.disabled = true;
            } else {
                copyPersianBtn.disabled = false;
            }

            renderAnalysisList(suggestionsList, currentResult.suggestions);
            renderAnalysisList(requirementsList, currentResult.preserved_requirements);
            renderAnalysisList(assumptionsList, currentResult.assumptions);
            renderAnalysisList(missingList, currentResult.missing_information);

            fetchUsage();
        } catch (err) {
            showToast('خطا در ارتباط با سرور');
        } finally {
            translateBtn.disabled = false;
            translateBtn.textContent = 'تبدیل کن';
        }
    });

    function copyText(text) {
        if (navigator.clipboard && window.isSecureContext) {
            return navigator.clipboard.writeText(text);
        }
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        const ok = document.execCommand('copy');
        document.body.removeChild(ta);
        return Promise.resolve(ok ? undefined : Promise.reject());
    }

    copyBtn.addEventListener('click', function () {
        if (!currentResult) return;
        copyText(currentResult.english_prompt).then(function () {
            showToast('پرامپت انگلیسی کپی شد ✓');
        }).catch(function () {
            showToast('خطا در کپی');
        });
    });

    copyPersianBtn.addEventListener('click', function () {
        if (!currentResult || !currentResult.persian_prompt) return;
        copyText(currentResult.persian_prompt).then(function () {
            showToast('پرامپت فارسی کپی شد ✓');
        }).catch(function () {
            showToast('خطا در کپی');
        });
    });

    output.addEventListener('click', function () {
        if (!currentResult) return;
        copyText(currentResult.english_prompt).then(function () {
            showToast('پرامپت انگلیسی کپی شد ✓');
        }).catch(function () {
            showToast('خطا در کپی');
        });
    });

    outputPersian.addEventListener('click', function () {
        if (!currentResult || !currentResult.persian_prompt) return;
        copyText(currentResult.persian_prompt).then(function () {
            showToast('پرامپت فارسی کپی شد ✓');
        }).catch(function () {
            showToast('خطا در کپی');
        });
    });

    manageSettings.addEventListener('click', function () {
        settingsModal.style.display = 'flex';
    });

    closeModal.addEventListener('click', function () {
        settingsModal.style.display = 'none';
    });

    settingsModal.addEventListener('click', function (e) {
        if (e.target === settingsModal) settingsModal.style.display = 'none';
    });

    settingsForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const saveStatus = document.getElementById('save-status');

        const formData = new FormData(settingsForm);
        try {
            const resp = await fetch('/settings', {
                method: 'POST',
                body: formData
            });
            const data = await resp.json();

            if (resp.ok) {
                saveStatus.textContent = '✓ تنظیمات ذخیره شد';
                saveStatus.className = 'save-status success';
                setTimeout(function () {
                    settingsModal.style.display = 'none';
                    saveStatus.textContent = '';
                }, 1200);
            } else {
                saveStatus.textContent = data.error || 'خطا در ذخیره';
                saveStatus.className = 'save-status error';
            }
        } catch (err) {
            saveStatus.textContent = 'خطا در ارتباط با سرور';
            saveStatus.className = 'save-status error';
        }
    });

    function handleAgentUse(agent) {
        if (!currentResult) return;
        const prompt = currentResult.english_prompt;
        copyText(prompt).then(function () {
            showToast('پرامپت کپی شد — حالا در ترمینال ' + (agent === 'claude' ? 'Claude Code' : 'OpenCode') + ' پیست کن');
        }).catch(function () {
            showToast('خطا در کپی');
        });
    }

    document.getElementById('use-in-claude').addEventListener('click', function () {
        handleAgentUse('claude');
    });

    document.getElementById('use-in-opencode').addEventListener('click', function () {
        handleAgentUse('opencode');
    });

    // ---------- سایدبار مصرف توکن ----------

    function meterBar(label, used, limit, unit) {
        let caption;
        if (limit === null || limit === undefined) {
            caption = '<span class="meter-used">' + formatTokens(used) + ' ' + unit + '</span>' +
                      '<span class="meter-remaining">نامحدود</span>';
        } else {
            const pct = limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
            const remaining = Math.max(0, limit - used);
            caption = '<span class="meter-used">' + fmtInt(used) + ' / ' + formatTokens(limit) + ' ' + unit + '</span>' +
                      '<span class="meter-remaining">باقی‌مانده: ' + fmtInt(remaining) + '</span>';
        }
        const widthPct = limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
        const barClass = widthPct >= 90 ? 'bar-danger' : (widthPct >= 70 ? 'bar-warn' : '');
        return '<div class="meter">' +
            '<div class="meter-head"><span class="meter-label">' + label + '</span>' + caption + '</div>' +
            '<div class="meter-track"><div class="meter-bar ' + barClass + '" style="width:' + widthPct.toFixed(1) + '%"></div></div>' +
            '</div>';
    }

    function renderHeaderUsage() {
        if (!usageData || !usageData.today) return;
        const today = usageData.today;
        usageHeaderTotal.textContent = formatTokens(today.total) + ' توکن';
        usageHeaderRequests.textContent = fmtInt(today.requests) + ' درخواست';
    }

    function renderUsage() {
        if (!usageData) return;

        renderHeaderUsage();

        const t = usageData.today;
        const selectedId = modelSelect.value;
        const sel = usageData.models.find(x => x.id === selectedId) || usageData.models[0];

        let html = '';

        html += '<div class="usage-summary">';
        html += '<div class="sum-cell"><span class="sum-num">' + fmtInt(t.requests) + '</span><span class="sum-lbl">درخواست امروز</span></div>';
        html += '<div class="sum-cell"><span class="sum-num">' + formatTokens(t.input) + '</span><span class="sum-lbl">توکن ورودی</span></div>';
        html += '<div class="sum-cell"><span class="sum-num">' + formatTokens(t.output) + '</span><span class="sum-lbl">توکن خروجی</span></div>';
        html += '<div class="sum-cell"><span class="sum-num">' + formatTokens(t.total) + '</span><span class="sum-lbl">جمع کل</span></div>';
        html += '</div>';

        if (sel) {
            html += '<div class="usage-model-card">';
            html += '<div class="umc-title">مدل منتخب: <strong>' + sel.name + '</strong></div>';
            html += meterBar('درخواست امروز (RPD)', sel.today_requests, sel.rpd, '');
            html += meterBar('توکن در دقیقه (TPM)', sel.minute_tokens, sel.tpm, 'توکن');
            html += meterBar('درخواست در دقیقه (RPM)', sel.minute_requests, sel.rpm, '');
            html += '</div>';
        }

        const used = usageData.models.filter(m => m.today_requests > 0).sort((a, b) => b.today_tokens - a.today_tokens);
        if (used.length) {
            html += '<div class="usage-model-list">';
            html += '<div class="uml-title">مصرف امروز مدل‌ها</div>';
            used.forEach(m => {
                html += '<div class="uml-row"><span class="uml-name" title="' + m.name + '">' + m.name + '</span>' +
                        '<span class="uml-val">' + fmtInt(m.today_requests) + ' درخواست</span>' +
                        '<span class="uml-tok">' + formatTokens(m.today_tokens) + ' توکن</span></div>';
            });
            html += '</div>';
        } else {
            html += '<div class="usage-empty">هنوز مصرفی ثبت نشده — اولین درخواست خود را ارسال کنید.</div>';
        }

        usageContent.innerHTML = html;
    }

    async function fetchUsage() {
        try {
            const resp = await fetch('/usage');
            usageData = await resp.json();
            renderHeaderUsage();
            renderUsage();
        } catch (e) {
            usageContent.innerHTML = '<div class="usage-empty">خطا در دریافت آمار مصرف</div>';
        }
    }

    fetchModels();
    fetchUsage();
    setInterval(fetchUsage, 5000);
});
