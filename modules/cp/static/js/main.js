let userData = {
    items: {},
    ignored_items: [],
    user_cp: 0,
    user_cp_pct: 0.0,
    professions: {}
};

let saveTimeout = null;

// === OCR: utilitários compartilhados (usados pelos fluxos de upload) ===

// Aviso discreto: quando uma chave/API de OCR falhou e o resultado veio de outra
function setOcrWarnings(el, warnings, failed) {
    if (!el) return;
    if (warnings && warnings.length) {
        el.title = warnings.join('\n');
        if (failed) {
            el.textContent = '\u26a0 ' + warnings.join(' \u00b7 ');
        } else {
            const n = warnings.length;
            el.textContent = '\u26a0 ' + (n === 1
                ? '1 tentativa falhou; resultado obtido na 2\u00aa'
                : n + ' tentativas falharam; resultado obtido na ' + (n + 1) + '\u00aa');
        }
        el.style.display = 'block';
    } else {
        el.style.display = 'none';
    }
}

// Fluxo comum de envio de imagem ao OCR: spinner no botão, status, fetch e avisos.
// `btn` é opcional — quando ausente (ex.: colagem via modal), não há spinner de botão.
async function uploadOcrImage(file, { btn, statusEl, warnEl, dotsKey, endpoint, applyResult }) {
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i data-lucide="loader" class="spin"></i>';
        lucide.createIcons();
    }
    if (statusEl) {
        statusEl.classList.remove('success', 'error');
        statusEl.classList.add('loading');
        statusEl.style.display = 'block';
        let dots = 0;
        window[dotsKey] = setInterval(() => {
            dots = (dots + 1) % 4;
            statusEl.textContent = 'Processando' + '.'.repeat(dots);
        }, 400);
    }
    try {
        const formData = new FormData();
        formData.append('image', file);
        const res = await fetch(endpoint, { method: 'POST', body: formData });
        const result = await res.json();

        if (result.success) {
            applyResult(result);
            setOcrWarnings(warnEl, result.warnings, false);
        } else {
            if (statusEl) {
                statusEl.style.display = 'block';
                statusEl.classList.remove('loading', 'success');
                statusEl.classList.add('error');
                statusEl.textContent = '\u2717 Nao foi possivel extrair dados';
            }
            setOcrWarnings(warnEl, result.warnings, true);
            if (result.raw_text) {
                console.log('OCR raw text:', result.raw_text);
            }
        }
    } catch (err) {
        if (statusEl) {
            statusEl.classList.remove('loading', 'success');
            statusEl.classList.add('error');
            statusEl.textContent = '\u2717 Erro ao processar imagem';
        }
        setOcrWarnings(warnEl, null, false);
        console.error('OCR error:', err);
    } finally {
        if (window[dotsKey]) {
            clearInterval(window[dotsKey]);
            window[dotsKey] = null;
        }
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i data-lucide="scan"></i>';
            lucide.createIcons();
        }
    }
}

// Zona de colagem reutilizável: clique abre o seletor, arrastar-e-soltar envia.
function wirePasteZone(zoneId, { fileInput, upload }) {
    const zone = document.getElementById(zoneId);
    if (!zone || !fileInput) return zone;
    zone.addEventListener('click', () => fileInput.click());
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        const file = [...(e.dataTransfer.files || [])].find((f) => f.type && f.type.indexOf('image/') === 0);
        if (file) upload(file);
    });
    return zone;
}

// Destaque visual ao colar com Ctrl+V: pisca a borda da zona ativa
function flashPasteZone(zone) {
    if (!zone) return;
    zone.classList.remove('flash');
    void zone.offsetWidth; // reinicia a animação
    zone.classList.add('flash');
}

// Modal de colagem: enquanto aberto, o Ctrl+V (PasteImage) é capturado para
// aquela área (arm). Ao fechar (X, ESC, clique fora), desarma e volta ao normal.
function setupPasteModal({ modalId, pasteId, onOpen }) {
    const modal = document.getElementById(modalId);
    if (!modal || !window.PasteImage) return null;

    function open() {
        PasteImage.arm(pasteId);
        modal.classList.add('active');
        if (onOpen) onOpen();
    }
    function close() {
        PasteImage.disarm();
        modal.classList.remove('active');
    }

    const closeBtn = modal.querySelector('.btn-close');
    if (closeBtn) closeBtn.addEventListener('click', close);
    modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });

    return { open, close };
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial fetch of user data
    fetchData();

    // Event Listeners for inputs
    document.querySelectorAll('.item-qty-input, #current-cp, #current-cp-pct').forEach(input => {
        input.addEventListener('input', () => {
            updateCalculations();
        });
    });

    // Event Listeners for Ignore buttons
    document.querySelectorAll('.btn-toggle-ignore').forEach(btn => {
        btn.addEventListener('click', () => {
            const item = btn.getAttribute('data-item');
            const targetId = btn.getAttribute('data-target');
            const group = document.getElementById(targetId);
            
            if (userData.ignored_items.includes(item)) {
                userData.ignored_items = userData.ignored_items.filter(i => i !== item);
                group.classList.remove('ignored');
                btn.innerHTML = '<i data-lucide="eye"></i>';
            } else {
                userData.ignored_items.push(item);
                group.classList.add('ignored');
                btn.innerHTML = '<i data-lucide="eye-off"></i>';
            }
            lucide.createIcons();
            updateCalculations();
        });
    });

    // Modal logic
    const modal = document.getElementById('prof-modal');
    const settingsModal = document.getElementById('settings-modal');
    const btnOpenSettings = document.getElementById('btn-open-settings');
    const btnCloseSettings = document.getElementById('btn-close-settings');
    const settingsForm = document.getElementById('settings-form');
    const btnClose = document.querySelector('.btn-close');
    const btnSaveProf = document.getElementById('btn-save-prof');

    if (btnOpenSettings) {
        btnOpenSettings.addEventListener('click', () => {
            document.getElementById('input-goal-cp').value = userData.goal_cp || 600;
            settingsModal.classList.add('active');
        });
    }

    if (btnCloseSettings) {
        btnCloseSettings.addEventListener('click', () => settingsModal.classList.remove('active'));
    }

    if (settingsForm) {
        settingsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const newGoal = parseInt(document.getElementById('input-goal-cp').value) || 600;
            userData.goal_cp = newGoal;
            
            const feedback = document.getElementById('settings-feedback');
            feedback.textContent = "Salvando...";
            feedback.className = "feedback-msg";

            try {
                await saveData();
                feedback.textContent = "Meta atualizada!";
                feedback.className = "feedback-msg success";
                setTimeout(() => {
                    settingsModal.classList.remove('active');
                    feedback.textContent = "";
                    updateCalculations();
                }, 1000);
            } catch (err) {
                feedback.textContent = "Erro ao salvar.";
                feedback.className = "feedback-msg error";
            }
        });
    }

    btnClose.addEventListener('click', () => modal.classList.remove('active'));
    window.addEventListener('click', (e) => { 
        if (e.target === modal) modal.classList.remove('active'); 
        if (e.target === settingsModal) settingsModal.classList.remove('active');
    });

    btnSaveProf.addEventListener('click', () => {
        const prof = modal.getAttribute('data-prof');
        const level = document.getElementById('modal-prof-level').value;
        const pct = parseFloat(document.getElementById('modal-prof-pct').value) || 0.0;
        
        userData.professions[prof] = { level, pct };
        modal.classList.remove('active');
        updateCalculations();
    });

    // === OCR de profissões (níveis) ===
    const btnOcr = document.getElementById('btn-ocr-upload');
    const fileInput = document.getElementById('ocr-image-input');
    const statusEl = document.getElementById('ocr-status');
    const warnEl = document.getElementById('ocr-warning');

    if (btnOcr && fileInput) {
        // Aplica o resultado do OCR nas profissões e mostra no status indicado
        const applyProfResult = (statusTarget) => (result) => {
            let imported = 0;
            for (const [prof, data] of Object.entries(result.data_dict || {})) {
                if (!userData.professions[prof]) {
                    userData.professions[prof] = {};
                }
                userData.professions[prof].level = data.level;
                userData.professions[prof].pct = data.pct;
                imported++;
            }
            if (statusTarget) {
                statusTarget.style.display = 'block';
                statusTarget.classList.remove('loading', 'error');
                statusTarget.classList.add('success');
                statusTarget.textContent = '\u2713 ' + imported + ' profissoes importadas';
            }
            updateCalculations();
        };

        // Fluxo do painel: upload por arquivo (botão de scan)
        const ocrOpts = {
            endpoint: 'api/ocr',
            btn: btnOcr,
            statusEl,
            warnEl,
            dotsKey: '_ocrDotsInterval',
            applyResult: applyProfResult(statusEl),
        };

        // Fluxo do modal: colagem (Ctrl+V/arrastar) — status dentro do modal
        const pasteStatusEl = document.getElementById('paste-prof-status');
        const pasteWarnEl = document.getElementById('paste-prof-warning');
        const pasteOpts = {
            endpoint: 'api/ocr',
            btn: null,
            statusEl: pasteStatusEl,
            warnEl: pasteWarnEl,
            dotsKey: '_ocrDotsInterval',
            applyResult: applyProfResult(pasteStatusEl),
        };

        const uploadProf = (file) => uploadOcrImage(file, ocrOpts);
        const uploadProfModal = (file) => uploadOcrImage(file, pasteOpts);
        const zoneProf = wirePasteZone('paste-zone-prof', { fileInput, upload: uploadProfModal });

        btnOcr.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            fileInput.value = '';
            uploadProf(file);
        });

        // Colar imagem da área de transferência (Ctrl+V) — só enquanto o modal
        // de colagem de profissões estiver aberto (PasteImage.arm/disarm)
        if (window.PasteImage) {
            PasteImage.attach('profissoes', {
                onImage: uploadProfModal,
                onHint: (texto) => {
                    flashPasteZone(zoneProf);
                    if (pasteStatusEl) {
                        pasteStatusEl.classList.remove('success', 'error');
                        pasteStatusEl.classList.add('loading');
                        pasteStatusEl.style.display = 'block';
                        pasteStatusEl.textContent = texto;
                    }
                },
                onNoImage: () => {
                    if (pasteStatusEl) {
                        pasteStatusEl.classList.remove('loading', 'success');
                        pasteStatusEl.classList.add('error');
                        pasteStatusEl.style.display = 'block';
                        pasteStatusEl.textContent = '\u26a0 Nenhuma imagem na \u00e1rea de transfer\u00eancia — tire o print (Win+Shift+S) e cole de novo';
                    }
                },
            });
        }

        // Botão clipboard: abre o modal de colagem (arma o Ctrl+V para profissões)
        const btnPasteProf = document.getElementById('btn-paste-prof');
        if (btnPasteProf) {
            const pasteProf = setupPasteModal({
                modalId: 'paste-prof-modal',
                pasteId: 'profissoes',
                onOpen: () => flashPasteZone(zoneProf),
            });
            btnPasteProf.addEventListener('click', () => pasteProf && pasteProf.open());
        }
    }
});

            // === Inventory OCR ===
            const btnOcrInv = document.getElementById('btn-ocr-inventory');
            const fileInputInv = document.getElementById('ocr-inventory-input');
            const statusElInv = document.getElementById('ocr-inventory-status');
            const warnElInv = document.getElementById('ocr-inventory-warning');
        
            if (btnOcrInv && fileInputInv) {
                // Aplica o resultado do OCR nos campos de subprodutos e mostra no status indicado
                const applyInvResult = (statusTarget) => (result) => {
                    let imported = 0;
                    for (const [itemName, qty] of Object.entries(result.data || {})) {
                        const input = document.querySelector("input[data-item=\"" + itemName + "\"]");
                        if (input) {
                            input.value = qty;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            imported++;
                        }
                    }
                    if (statusTarget) {
                        statusTarget.classList.remove('loading', 'error');
                        statusTarget.classList.add('success');
                        statusTarget.textContent = '\u2713 ' + imported + ' itens importados';
                    }
                };

                // Fluxo do painel: upload por arquivo (botão de scan)
                const ocrInvOpts = {
                    endpoint: 'api/ocr-inventory',
                    btn: btnOcrInv,
                    statusEl: statusElInv,
                    warnEl: warnElInv,
                    dotsKey: '_ocrInvDotsInterval',
                    applyResult: applyInvResult(statusElInv),
                };

                // Fluxo do modal: colagem (Ctrl+V/arrastar) — status dentro do modal
                const pasteStatusElInv = document.getElementById('paste-inventory-status');
                const pasteWarnElInv = document.getElementById('paste-inventory-warning');
                const pasteInvOpts = {
                    endpoint: 'api/ocr-inventory',
                    btn: null,
                    statusEl: pasteStatusElInv,
                    warnEl: pasteWarnElInv,
                    dotsKey: '_ocrInvDotsInterval',
                    applyResult: applyInvResult(pasteStatusElInv),
                };

                const uploadInv = (file) => uploadOcrImage(file, ocrInvOpts);
                const uploadInvModal = (file) => uploadOcrImage(file, pasteInvOpts);
                const zoneInv = wirePasteZone('paste-zone-inventory', { fileInput: fileInputInv, upload: uploadInvModal });

                btnOcrInv.addEventListener('click', () => {
                    fileInputInv.click();
                });

                fileInputInv.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (!file) return;
                    fileInputInv.value = '';
                    uploadInv(file);
                });

                // Colar imagem da área de transferência (Ctrl+V) — só enquanto o modal
                // de colagem de inventário estiver aberto (PasteImage.arm/disarm)
                if (window.PasteImage) {
                    PasteImage.attach('inventario', {
                        onImage: uploadInvModal,
                        onHint: (texto) => {
                            flashPasteZone(zoneInv);
                            if (pasteStatusElInv) {
                                pasteStatusElInv.classList.remove('success', 'error');
                                pasteStatusElInv.classList.add('loading');
                                pasteStatusElInv.style.display = 'block';
                                pasteStatusElInv.textContent = texto;
                            }
                        },
                        onNoImage: () => {
                            if (pasteStatusElInv) {
                                pasteStatusElInv.classList.remove('loading', 'success');
                                pasteStatusElInv.classList.add('error');
                                pasteStatusElInv.style.display = 'block';
                                pasteStatusElInv.textContent = '\u26a0 Nenhuma imagem na \u00e1rea de transfer\u00eancia — tire o print (Win+Shift+S) e cole de novo';
                            }
                        },
                    });
                }

                // Botão clipboard: abre o modal de colagem (arma o Ctrl+V para o inventário)
                const btnPasteInv = document.getElementById('btn-paste-inventory');
                if (btnPasteInv) {
                    const pasteInv = setupPasteModal({
                        modalId: 'paste-inventory-modal',
                        pasteId: 'inventario',
                        onOpen: () => flashPasteZone(zoneInv),
                    });
                    btnPasteInv.addEventListener('click', () => pasteInv && pasteInv.open());
                }
            }


async function fetchData() {
    try {
        const res = await fetch('api/data');
        const data = await res.json();
        
        userData = data;
        if (!userData.ignored_items) userData.ignored_items = [];
        
        // Fill inputs and visual state
        for (const [item, qty] of Object.entries(data.items)) {
            const input = document.querySelector(`[data-item="${item}"].item-qty-input`);
            if (input) {
                input.value = qty;
                
                // Set initial ignore state
                if (userData.ignored_items.includes(item)) {
                    const btn = document.querySelector(`.btn-toggle-ignore[data-item="${item}"]`);
                    const group = document.getElementById(btn.getAttribute('data-target'));
                    group.classList.add('ignored');
                    btn.innerHTML = '<i data-lucide="eye-off"></i>';
                }
            }
        }
        
        document.getElementById('current-cp').value = data.user_cp;
        document.getElementById('current-cp-pct').value = data.user_cp_pct;
        
        updateCalculations();
    } catch (err) {
        console.error("Erro ao buscar dados:", err);
    }
}

function formatNumber(n) {
    return new Intl.NumberFormat('pt-BR').format(Math.floor(n));
}

async function updateCalculations() {
    // Sync local userData from inputs
    document.querySelectorAll('.item-qty-input').forEach(input => {
        userData.items[input.getAttribute('data-item')] = parseInt(input.value) || 0;
    });
    userData.user_cp = parseInt(document.getElementById('current-cp').value) || 0;
    userData.user_cp_pct = parseFloat(document.getElementById('current-cp-pct').value) || 0.0;

    try {
        const res = await fetch('api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData) 
       });
        
        const results = await res.json();
        displayResults(results);

        // Auto-save
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            saveData();
        }, 500);
        
    } catch (err) {
        console.error("Erro ao calcular:", err);
    }
}

function displayResults(results) {
    // CP Projection
    document.getElementById('disp-current-cp').textContent = userData.user_cp;
    document.getElementById('disp-final-cp').textContent = results.projection.final_cp;
    document.getElementById('disp-final-pct').textContent = results.projection.final_pct.toFixed(2) + '%';
    document.getElementById('cp-progress-fill').style.width = results.projection.final_pct + '%';
    
    document.getElementById('total-deliveries').textContent = formatNumber(results.projection.total_deliveries);
    document.getElementById('total-cp-xp').textContent = formatNumber(results.gains.total_cp_xp);
    
    // Dynamic Goal
    document.getElementById('display-goal-cp').textContent = results.goal_cp;
    document.getElementById('missing-goal-text').textContent = formatNumber(results.missing_goal);
          
    // Professions
    const profList = document.getElementById('professions-list');
    profList.innerHTML = '';
    
    results.prof_advancement.forEach(adv => {
        const card = document.createElement('div');
        card.className = 'prof-card';
        card.innerHTML = `
            <div class="prof-header">
                <span class="prof-name">${adv.profession}</span>
                <span class="prof-xp-gain">${formatNumber(adv.gained_xp)} XP</span>
            </div>
            <div class="prof-advance">
                <span class="prof-lvl-start">${adv.start_level} (${adv.start_pct.toFixed(1)}%)</span>
                <i data-lucide="chevron-right" class="prof-arrow-small"></i>
                <span class="prof-lvl-final">${adv.final_level} (${adv.final_pct.toFixed(1)}%)</span>
            </div>
        `;
        
        card.addEventListener('click', () => {
            openProfModal(adv.profession, adv.start_level, adv.start_pct);
        });
        
        profList.appendChild(card);
    });
    
    lucide.createIcons();
}

function openProfModal(prof, level, pct) {
    const modal = document.getElementById('prof-modal');
    modal.setAttribute('data-prof', prof);
    document.getElementById('modal-prof-title').textContent = `Configurar ${prof}`;
    document.getElementById('modal-prof-level').value = level;
    document.getElementById('modal-prof-pct').value = pct;
    modal.classList.add('active');
}

async function saveData() {
    try {
        const res = await fetch('api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
    } catch (err) {
        console.error("Erro ao salvar:", err);
    }
}
