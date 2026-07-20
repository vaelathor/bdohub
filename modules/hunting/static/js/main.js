let projectionChart = null;
let currentCalYear = new Date().getFullYear();
let currentCalMonth = new Date().getMonth() + 1; // 1-12

// Globals for modals
let dayModal = null;
let settingsModal = null;

document.addEventListener('DOMContentLoaded', () => {
    // Initial load
    fetchStatus();
    fetchChartData();
    fetchMonthlyChart();
    fetchHistory(currentCalYear, currentCalMonth);

    // Form submit
    document.getElementById('progress-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const data_reg = document.getElementById('data_reg').value;
        const nivel = document.getElementById('nivel_reg').value;
        const pct = document.getElementById('pct_reg').value;
        
        const btn = document.getElementById('btn-submit');
        btn.disabled = true;

        try {
            const res = await fetch('api/progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data: data_reg, nivel: nivel, pct: parseFloat(pct) })
            });
            
            const result = await res.json();
            const feedback = document.getElementById('form-feedback');
            
            if (res.ok) {
                feedback.textContent = result.message || "Registro salvo com sucesso!";
                feedback.className = "feedback-msg success";
                // Reload data
                fetchStatus();
                fetchChartData();
                fetchHistory(currentCalYear, currentCalMonth);
                
                // Limpar inputs de nível e pct, mas manter data
                document.getElementById('nivel_reg').value = '';
                document.getElementById('pct_reg').value = '';
            } else {
                feedback.textContent = result.error || "Erro ao salvar registro.";
                feedback.className = "feedback-msg error";
            }
        } catch (error) {
            console.error(error);
        } finally {
            btn.classList.add('success-pulse');
            setTimeout(() => {
                btn.classList.remove('success-pulse');
                btn.disabled = false;
            }, 1000);
        }
    });

    // Calendar Controls
    document.getElementById('btn-prev-month').addEventListener('click', () => {
        currentCalMonth--;
        if (currentCalMonth < 1) { currentCalMonth = 12; currentCalYear--; }
        fetchHistory(currentCalYear, currentCalMonth);
    });

    document.getElementById('btn-next-month').addEventListener('click', () => {
        currentCalMonth++;
        if (currentCalMonth > 12) { currentCalMonth = 1; currentCalYear++; }
        fetchHistory(currentCalYear, currentCalMonth);
    });

    // Tab Switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            // Update buttons
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update content
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(`tab-${targetTab}`).classList.add('active');
            
            // Trigger chart resize to fix display issues on hidden elements
            if (targetTab === 'daily' && projectionChart) {
                projectionChart.resize();
            } else if (targetTab === 'monthly' && window.monthlyChartObj) {
                window.monthlyChartObj.resize();
            }
        });
    });

    // Settings Modal
    settingsModal = document.getElementById('settings-modal');
    const btnOpenSettings = document.getElementById('btn-open-settings');
    const btnCloseSettings = document.getElementById('btn-close-settings');
    const settingsForm = document.getElementById('settings-form');

    // Helper function to format date from YYYY-MM-DD to DD/MM/YYYY
    function formatDate(dateStr) {
        const [y, m, d] = dateStr.split('-');
        return `${d}/${m}/${y}`;
    }

    // Helper function to convert DD/MM/YYYY to YYYY-MM-DD
    function toISODate(ddmmyyyy) {
        const [d, m, y] = ddmmyyyy.split('/');
        return `${y}-${m}-${d}`;
    }

    btnOpenSettings.addEventListener('click', async () => {
        // Load both stages
        try {
            const res = await fetch('api/config/stages');
            const data = await res.json();

            if (!data.error && data.stages && data.stages.length >= 2) {
                const stage1 = data.stages[0];
                const stage2 = data.stages[1];

                // Etapa 1 - todos os campos editáveis
                document.getElementById('stage1_start_date').value = formatDate(stage1.data_inicio);
                document.getElementById('stage1_start_level').value = stage1.nivel_inicio;
                document.getElementById('stage1_end_date').value = formatDate(stage1.data_fim);
                document.getElementById('stage1_end_level').value = stage1.nivel_fim;

                // Etapa 2 - campos automáticos preenchidos
                document.getElementById('stage2_start_date').value = formatDate(stage2.data_inicio);
                document.getElementById('stage2_start_level').value = stage2.nivel_inicio;
                document.getElementById('stage2_end_date').value = formatDate(stage2.data_fim);
                document.getElementById('stage2_end_level').value = stage2.nivel_fim;
            }
        } catch (e) {
            console.error("Erro ao carregar etapas:", e);
        }

        settingsModal.classList.add('active');
    });

    btnCloseSettings.addEventListener('click', () => {
        settingsModal.classList.remove('active');
        document.getElementById('settings-feedback').style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            settingsModal.classList.remove('active');
            document.getElementById('settings-feedback').style.display = 'none';
        }
    });

    // Auto-update Stage 2 fields when Stage 1 changes
    document.getElementById('stage1_end_date').addEventListener('change', function() {
        const stage1EndDate = this.value; // DD/MM/YYYY
        if (stage1EndDate) {
            const [d, m, y] = stage1EndDate.split('/');
            const date = new Date(y, m - 1, d);
            date.setDate(date.getDate() + 1); // Next day

            const nextDay = String(date.getDate()).padStart(2, '0');
            const nextMonth = String(date.getMonth() + 1).padStart(2, '0');
            const nextYear = date.getFullYear();

            document.getElementById('stage2_start_date').value = `${nextDay}/${nextMonth}/${nextYear}`;
        }
    });

    document.getElementById('stage1_end_level').addEventListener('input', function() {
        document.getElementById('stage2_start_level').value = this.value;
    });

    // Date picker integration for stage date fields
    document.getElementById('stage1_start_date').addEventListener('click', function() {
        openDatePicker('stage1_start_date');
    });

    document.getElementById('stage1_end_date').addEventListener('click', function() {
        openDatePicker('stage1_end_date');
    });

    document.getElementById('stage2_end_date').addEventListener('click', function() {
        openDatePicker('stage2_end_date');
    });

    // Date picker for progress form
    document.getElementById('data_reg').addEventListener('click', function() {
        openDatePicker('data_reg');
    });

    settingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Gera nomes automaticamente baseados nos níveis
        const stage1_nome = `${document.getElementById('stage1_start_level').value} a ${document.getElementById('stage1_end_level').value}`;
        const stage2_nome = `${document.getElementById('stage2_start_level').value} a ${document.getElementById('stage2_end_level').value}`;

        const stages = [
            {
                nome: stage1_nome,
                data_inicio: toISODate(document.getElementById('stage1_start_date').value),
                data_fim: toISODate(document.getElementById('stage1_end_date').value),
                nivel_inicio: document.getElementById('stage1_start_level').value,
                nivel_fim: document.getElementById('stage1_end_level').value
            },
            {
                nome: stage2_nome,
                data_inicio: toISODate(document.getElementById('stage2_start_date').value),
                data_fim: toISODate(document.getElementById('stage2_end_date').value),
                nivel_inicio: document.getElementById('stage2_start_level').value,
                nivel_fim: document.getElementById('stage2_end_level').value
            }
        ];

        const btn = document.getElementById('btn-save-settings');
        btn.disabled = true;

        try {
            const res = await fetch('api/config/stages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stages })
            });

            const result = await res.json();
            const feedback = document.getElementById('settings-feedback');

            if (res.ok) {
                feedback.textContent = result.message || "Etapas atualizadas com sucesso!";
                feedback.className = "feedback-msg success";
                feedback.style.display = 'block';
                setTimeout(() => {
                    settingsModal.classList.remove('active');
                    window.location.reload();
                }, 1000);
            } else {
                feedback.textContent = result.error || "Erro ao atualizar etapas.";
                feedback.className = "feedback-msg error";
                feedback.style.display = 'block';
            }
        } catch (error) {
            console.error(error);
            const feedback = document.getElementById('settings-feedback');
            feedback.textContent = "Erro de conexão.";
            feedback.className = "feedback-msg error";
            feedback.style.display = 'block';
        } finally {
            btn.disabled = false;
        }
    });

    // Day Details Modal
    dayModal = document.getElementById('day-modal');
    const btnCloseDay = document.getElementById('btn-close-day');

    if (btnCloseDay) {
        btnCloseDay.addEventListener('click', () => {
            dayModal.classList.remove('active');
        });
    }

    window.addEventListener('click', (e) => {
        if (e.target === dayModal) {
            dayModal.classList.remove('active');
        }
    });
});

async function showDayDetails(dateStr) {
    try {
        const res = await fetch(`api/day-details?data=${dateStr}`);
        const data = await res.json();
        
        if (data.error) return;

        document.getElementById('detail-date').textContent = data.data;
        document.getElementById('detail-etapa').textContent = data.etapa_nome;
        
        // Meta
        document.getElementById('detail-meta-level').textContent = `Guru ${data.meta_nivel.toFixed(2)}`;
        document.getElementById('detail-meta-exp').textContent = formatNumber(data.meta_exp) + ' Exp';
        
        // Real
        const realLevel = data.has_registro ? `${data.nivel_nome} (${data.porcentagem.toFixed(2)}%)` : `Guru ${data.real_nivel.toFixed(2)}`;
        document.getElementById('detail-real-level').textContent = realLevel;
        document.getElementById('detail-real-exp').textContent = formatNumber(data.real_exp) + ' Exp';
        
        const box = document.getElementById('detail-result-box');
        const verdict = document.getElementById('detail-verdict');
        const diff = document.getElementById('detail-diff');
        
        if (data.delta > 0) {
            verdict.textContent = "ADIANTADO";
            box.style.background = "rgba(16, 185, 129, 0.2)";
            box.style.color = "var(--success)";
            box.style.border = "1px solid rgba(16, 185, 129, 0.4)";
            diff.textContent = `+${formatNumber(data.delta)} Exp acima da meta`;
        } else if (data.delta < 0) {
            verdict.textContent = "ATRASADO";
            box.style.background = "rgba(239, 68, 68, 0.2)";
            box.style.color = "var(--danger)";
            box.style.border = "1px solid rgba(239, 68, 68, 0.4)";
            diff.textContent = `${formatNumber(Math.abs(data.delta))} Exp abaixo da meta`;
        } else {
            verdict.textContent = "NA META";
            box.style.background = "rgba(56, 189, 248, 0.2)";
            box.style.color = "var(--accent-primary)";
            box.style.border = "1px solid rgba(56, 189, 248, 0.4)";
            diff.textContent = "Exatamente no planejado";
        }
        
        dayModal.classList.add('active');
    } catch (err) {
        console.error("Erro ao carregar detalhes do dia:", err);
    }
}

function formatNumber(num) {
    return new Intl.NumberFormat('pt-BR').format(Math.floor(num));
}

async function fetchStatus() {
    try {
        const res = await fetch('api/status');
        const data = await res.json();
        
        if (data.error) {
            document.getElementById('nav-stage-info').textContent = data.error;
            return;
        }

        document.getElementById('nav-stage-info').textContent = `Etapa: ${data.etapa_nome} | ${data.hoje}`;
        
        // Form Hints
        const hintEl = document.getElementById('form-hint');
        if (hintEl) {
            hintEl.textContent = `Dica: A meta para hoje requer estar próximo a ${data.dica_nivel} com ${data.dica_pct.toFixed(2)}%`;
        }

        if (!data.has_history) {
            document.getElementById('current-exp').textContent = "--";
            document.getElementById('status-verdict').textContent = "Sem Registros";
        } else {
            document.getElementById('current-exp').textContent = formatNumber(data.exp_atual_abs);
            
            // Progress Bar
            const bar = document.getElementById('stage-progress-fill');
            const pctText = document.getElementById('stage-progress-text');
            bar.style.width = `${data.progresso_pct}%`;
            pctText.textContent = `${data.progresso_pct.toFixed(2)}%`;
            
            // Verdict
            const verdictEl = document.getElementById('status-verdict');
            const subEl = document.getElementById('status-sub');
            
            if (data.delta > 0) {
                verdictEl.textContent = `Adiantado`;
                verdictEl.className = "stat-value success";
                subEl.textContent = `+${formatNumber(data.delta)} Exp (~${data.dias_adiantado.toFixed(1)} dias)`;
            } else if (data.delta < 0) {
                if (data.is_pending_today) {
                    verdictEl.textContent = `Pendente Hoje`;
                    verdictEl.className = "stat-value warning"; // Assumindo que existe uma classe warning ou podemos usar highlight
                    verdictEl.style.color = "var(--warning, #f59e0b)"; // Fallback se classe warning não existir
                    subEl.textContent = `Faltam ${formatNumber(Math.abs(data.delta))} Exp para a meta do dia`;
                } else {
                    verdictEl.textContent = `Atrasado`;
                    verdictEl.className = "stat-value danger";
                    subEl.textContent = `${formatNumber(Math.abs(data.delta))} Exp (~${Math.abs(data.dias_adiantado).toFixed(1)} dias)`;
                }
            } else {
                verdictEl.textContent = `Na Meta`;
                verdictEl.className = "stat-value highlight";
                subEl.textContent = `Exatamente no planejado!`;
            }
        }

        document.getElementById('target-exp').textContent = formatNumber(data.meta_atual_exp);
        document.getElementById('req-avg').textContent = `${formatNumber(data.exp_por_dia)} / dia útil`;

    } catch (err) {
        console.error("Erro ao buscar status:", err);
    }
}

async function fetchChartData() {
    try {
        const res = await fetch('api/chart');
        const data = await res.json();
        
        if (data.error) return;

        const ctx = document.getElementById('projectionChart').getContext('2d');
        
        if (projectionChart) {
            projectionChart.destroy();
        }

        Chart.defaults.color = '#cbd5e1';
        Chart.defaults.font.family = "'Outfit', sans-serif";

        projectionChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Planejado (Guia)',
                        data: data.planned,
                        borderColor: 'rgba(56, 189, 248, 0.5)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0,
                        tension: 0.1
                    },
                    {
                        label: 'Realizado',
                        data: data.actual,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        pointRadius: 2,
                        pointHoverRadius: 6,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1,
                        padding: 10,
                        displayColors: true,
                    }
                },
                scales: {
                    x: {
                        grid: { 
                            display: false, // Remove as linhas verticais para limpar o visual
                            drawBorder: false 
                        },
                        ticks: {
                            maxTicksLimit: 8, // Mostra no máximo 8 datas, evitando poluição
                            font: { size: 10 }
                        }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            font: { size: 10 },
                            callback: function(value) { return 'G' + value; } // Abrevia "Guru" para "G"
                        }
                    }
                },
                layout: {
                    padding: {
                        left: 0,
                        right: 10,
                        top: 0,
                        bottom: 0
                    }
                }
            }
        });
    } catch (err) {
        console.error("Erro ao buscar dados do gráfico:", err);
    }
}

async function fetchMonthlyChart() {
    try {
        const res = await fetch('api/monthly_stats');
        const data = await res.json();
        
        if (data.error) return;

        const ctx = document.getElementById('monthlyChart').getContext('2d');
        
        // Formata os números para o tooltip
        const formatExp = (val) => val === null ? "Pendente" : formatNumber(val) + " Exp";

        if (window.monthlyChartObj) {
            window.monthlyChartObj.destroy();
        }

        window.monthlyChartObj = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Meta de Exp',
                        data: data.planned_gain,
                        backgroundColor: 'rgba(56, 189, 248, 0.2)',
                        borderColor: '#38bdf8',
                        borderWidth: 1,
                        borderRadius: 4
                    },
                    {
                        label: 'Realizado',
                        data: data.actual_gain,
                        backgroundColor: 'rgba(16, 185, 129, 0.6)',
                        borderColor: '#10b981',
                        borderWidth: 1,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) {
                                    label += formatExp(context.parsed.y);
                                    
                                    // Adicionar o nível projetado/real no tooltip
                                    const idx = context.dataIndex;
                                    if (context.datasetIndex === 0) {
                                        label += ` (Nível Final: ${data.planned_level[idx]})`;
                                    } else {
                                        if (data.actual_level[idx]) {
                                            label += ` (Nível Final: ${data.actual_level[idx]})`;
                                        }
                                    }
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 10 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            font: { size: 10 },
                            callback: function(value) { return 'G' + value; }
                        }
                    }
                },
                layout: {
                    padding: { left: 0, right: 10, top: 0, bottom: 0 }
                }
            }
        });
    } catch (err) {
        console.error("Erro ao buscar dados mensais:", err);
    }
}

const monthNames = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];

async function fetchHistory(year, month) {
    try {
        document.getElementById('current-month-display').textContent = `${monthNames[month - 1]} ${year}`;
        
        const res = await fetch(`api/history?ano=${year}&mes=${month}`);
        const data = await res.json();
        
        const calBody = document.getElementById('calendar-body');
        calBody.innerHTML = '';
        
        data.forEach(week => {
            week.forEach(day => {
                const dayEl = document.createElement('div');
                
                if (day === null) {
                    dayEl.className = 'cal-day empty';
                } else {
                    dayEl.className = `cal-day ${day.futuro ? 'future' : ''}`;
                    dayEl.style.cursor = 'pointer';
                    dayEl.onclick = () => showDayDetails(day.data);
                    
                    const dateSpan = document.createElement('span');
                    dateSpan.className = 'cal-date';
                    dateSpan.textContent = day.dia;
                    dayEl.appendChild(dateSpan);
                    
                    const badge = document.createElement('div');
                    badge.className = 'cal-badge';
                    
                    const content = document.createElement('div');
                    content.className = 'cal-content';

                    if (day.registro) {
                        const lvlShort = day.registro.nivel;
                        content.innerHTML = `<b>${lvlShort}</b> ${day.registro.porcentagem.toFixed(1)}%`;
                        
                        if (day.eh_util) {
                            badge.classList.add('badge-normal');
                        } else {
                            badge.classList.add('badge-extra');
                        }

                        // Botão de deletar
                        const delBtn = document.createElement('button');
                        delBtn.className = 'btn-delete-record';
                        delBtn.innerHTML = '<i data-lucide="trash-2"></i>';
                        delBtn.title = 'Remover este registro';
                        delBtn.onclick = (e) => {
                            e.stopPropagation();
                            deleteRecord(day.data);
                        };
                        dayEl.appendChild(delBtn);
                    } else {
                        // Sem registro - verificar se é hoje, passado ou futuro
                        const today = new Date();
                        today.setHours(0, 0, 0, 0);
                        const dayDate = new Date(currentCalYear, currentCalMonth - 1, day.dia);
                        dayDate.setHours(0, 0, 0, 0);

                        if (dayDate.getTime() === today.getTime()) {
                            // Hoje sem registro = Pendente
                            if (day.eh_util) {
                                badge.classList.add('badge-pendente');
                                content.textContent = "Pendente";
                            } else {
                                badge.classList.add('badge-folga');
                                content.textContent = "Folga";
                            }
                        } else if (dayDate < today) {
                            // Dia passado sem registro
                            if (day.eh_util) {
                                badge.classList.add('badge-falta');
                                content.textContent = "Falta";
                            } else {
                                badge.classList.add('badge-folga');
                                content.textContent = "Folga";
                            }
                        } else {
                            // Dia futuro
                            if (!day.eh_util) {
                                badge.classList.add('badge-folga');
                            }
                        }
                    }
                    
                    dayEl.appendChild(badge);
                    dayEl.appendChild(content);
                }
                
                calBody.appendChild(dayEl);
            });
        });
        
        lucide.createIcons(); // Recria ícones para os botões de lixeira
    } catch (err) {
        console.error("Erro ao buscar histórico:", err);
    }
}

async function deleteRecord(dateStr) {
    if (!confirm(`Tem certeza que deseja remover o registro de ${dateStr}?`)) {
        return;
    }

    try {
        const res = await fetch('api/progress/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: dateStr })
        });

        const result = await res.json();
        const feedback = document.getElementById('form-feedback');

        if (res.ok) {
            feedback.textContent = result.message || "Registro removido com sucesso!";
            feedback.className = "feedback-msg success";
            // Recarregar dados
            fetchStatus();
            fetchChartData();
            fetchHistory(currentCalYear, currentCalMonth);
        } else {
            feedback.textContent = result.error || "Erro ao remover registro.";
            feedback.className = "feedback-msg error";
        }
    } catch (error) {
        console.error("Erro ao deletar registro:", error);
    }
}
