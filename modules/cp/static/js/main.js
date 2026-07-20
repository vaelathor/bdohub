let userData = {
    items: {},
    ignored_items: [],
    user_cp: 0,
    user_cp_pct: 0.0,
    professions: {}
};

let saveTimeout = null;

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

    // === OCR Image Upload ===
    const btnOcr = document.getElementById('btn-ocr-upload');
    const fileInput = document.getElementById('ocr-image-input');
    const statusEl = document.getElementById('ocr-status');

    if (btnOcr && fileInput) {
        btnOcr.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            btnOcr.disabled = true;
            btnOcr.innerHTML = '<i data-lucide="loader" class="spin"></i>';
            lucide.createIcons();
            if (statusEl) {
                statusEl.className = 'ocr-status loading';
                statusEl.style.display = 'block';
                let dots = 0;
                window._ocrDotsInterval = setInterval(() => {
                    dots = (dots + 1) % 4;
                    statusEl.textContent = 'Processando' + '.'.repeat(dots);
                }, 400);
            }

            try {
                const formData = new FormData();
                formData.append('image', file);

                const res = await fetch('api/ocr', { method: 'POST', body: formData });
                const result = await res.json();

                if (result.success && result.data_dict) {
                    let imported = 0;
                    for (const [prof, data] of Object.entries(result.data_dict)) {
                        if (!userData.professions[prof]) {
                            userData.professions[prof] = {};
                        }
                        userData.professions[prof].level = data.level;
                        userData.professions[prof].pct = data.pct;
                        imported++;
                    }
                    if (statusEl) {
                        statusEl.style.display = 'block';
                        statusEl.className = 'ocr-status success';
                        statusEl.textContent = '\u2713 ' + imported + ' profissoes importadas';
                    }
                    updateCalculations();
                } else {
                    if (statusEl) {
                        statusEl.style.display = 'block';
                        statusEl.className = 'ocr-status error';
                        statusEl.textContent = '\u2717 Nao foi possivel extrair dados';
                    }
                    if (result.raw_text) {
                        console.log('OCR raw text:', result.raw_text);
                    }
                }
            } catch (err) {
                if (statusEl) {
                    statusEl.className = 'ocr-status error';
                    statusEl.textContent = '\u2717 Erro ao processar imagem';
                }
                console.error('OCR error:', err);
            }

            if (window._ocrDotsInterval) {
                clearInterval(window._ocrDotsInterval);
                window._ocrDotsInterval = null;
            }
            btnOcr.disabled = false;
            btnOcr.innerHTML = '<i data-lucide="scan"></i>';
            lucide.createIcons();
            fileInput.value = '';
        });
    }
});

            // === Inventory OCR ===
            const btnOcrInv = document.getElementById('btn-ocr-inventory');
            const fileInputInv = document.getElementById('ocr-inventory-input');
            const statusElInv = document.getElementById('ocr-inventory-status');
        
            if (btnOcrInv && fileInputInv) {
                btnOcrInv.addEventListener('click', () => fileInputInv.click());
        
                fileInputInv.addEventListener('change', async (e) => {
                    const file = e.target.files[0];
                    if (!file) return;
        
                    btnOcrInv.disabled = true;
                    btnOcrInv.innerHTML = '<i data-lucide="loader" class="spin"></i>';
                    lucide.createIcons();
                    if (statusElInv) {
                        statusElInv.className = 'ocr-status loading';
                        statusElInv.style.display = 'block';
                        let dots = 0;
                        window._ocrInvDotsInterval = setInterval(() => {
                            dots = (dots + 1) % 4;
                            statusElInv.textContent = 'Processando' + '.'.repeat(dots);
                        }, 400);
                    }
        
                    try {
                        const formData = new FormData();
                        formData.append('image', file);
        
                        const res = await fetch('api/ocr-inventory', { method: 'POST', body: formData });
                        const result = await res.json();
        
                        if (result.success && result.data) {
                            let imported = 0;
                            for (const [itemName, qty] of Object.entries(result.data)) {
                                const input = document.querySelector("input[data-item=\"" + itemName + "\"]");
                                if (input) {
                                    input.value = qty;
                                    input.dispatchEvent(new Event('input', { bubbles: true }));
                                    imported++;
                                }
                            }
                            if (statusElInv) {
                                statusElInv.className = 'ocr-status success';
                                statusElInv.textContent = '\u2713 ' + imported + ' itens importados';
                            }
                        } else {
                            if (statusElInv) {
                                statusElInv.className = 'ocr-status error';
                                statusElInv.textContent = '\u2717 Nao foi possivel extrair dados';
                            }
                            if (result.raw_text) {
                                console.log('OCR raw text:', result.raw_text);
                            }
                        }
                    } catch (err) {
                        if (statusElInv) {
                            statusElInv.className = 'ocr-status error';
                            statusElInv.textContent = '\u2717 Erro ao processar imagem';
                        }
                        console.error('OCR error:', err);
                    }
        
                    if (window._ocrInvDotsInterval) {
                        clearInterval(window._ocrInvDotsInterval);
                        window._ocrInvDotsInterval = null;
                    }
        
                    btnOcrInv.disabled = false;
                    btnOcrInv.innerHTML = '<i data-lucide="scan"></i>';
                    lucide.createIcons();
                    fileInputInv.value = '';
                });
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
