# BDOHub Design System — Guia Definitivo de Referência

> **Versão:** 1.0  
> **Autor:** Buffy (Codebuff)  
> **Data:** Ago 2026  
> **Objetivo:** Referência única e definitiva para construir, manter e reformular qualquer página do BDOHub com consistência visual, responsividade e elegância.

---

## Índice

1. [Filosofia](#1-filosofia)
2. [Arquitetura de Layout](#2-arquitetura-de-layout)
3. [Sistema de Cores](#3-sistema-de-cores)
4. [Sistema Tipográfico](#4-sistema-tipográfico)
5. [Sistema de Espaçamento](#5-sistema-de-espaçamento)
6. [Componentes](#6-componentes)
7. [Grids e Layout Responsivo](#7-grids-e-layout-responsivo)
8. [Mobile Breakpoints](#8-mobile-breakpoints)
9. [Animações e Transições](#9-animações-e-transições)
10. [Temas (Dark/Light)](#10-temas-darklight)
11. [Padrões por Módulo](#11-padrões-por-módulo)
12. [Checklist de Implementação](#12-checklist-de-implementação)

---

## 1. Filosofia

### Princípios
- **Dark-first**: o tema padrão é escuro. Light é opcional.
- **Glassmorphism sutil**: painéis com fundo semitransparente, borda leve, sombra difusa.
- **Consistência visual**: todos os módulos compartilham o mesmo DNA visual.
- **Minimalismo funcional**: mostrar o necessário, esconder o acessório.
- **Mobile-first nos padrões**: o `@media` corrige para mobile, o base é desktop.

### O que NÃO fazer
- Nunca usar `height: 100vh` no body sem override mobile.
- Nunca usar `overflow: hidden` no body sem `overflow-y: auto` no mobile.
- Nunca misturar frameworks CSS (Bootstrap, Tailwind etc.).
- Nunca definir `font-size` com valores arbitrários — usar a escala do sistema.
- Nunca usar `!important` sem justificativa (exceto em `@media` overrides).

---

## 2. Arquitetura de Layout

### Shell (templates/index.html)
O shell é o invólucro. Ele contém:
- **Sidebar** (desktop): barra lateral fixa à esquerda, 70px de largura.
- **Bottom Tab Bar** (mobile): barra fixa no fundo, 56px de altura.
- **iframe**: carrega o módulo ativo, preenche o espaço restante.

```
┌─────────┬──────────────────────────┐
│  SIDE   │                          │
│  NAV    │       iframe             │
│  70px   │       (módulo)           │
│         │                          │
└─────────┴──────────────────────────┘

MOBILE:
┌────────────────────────────────────┐
│                                    │
│          iframe (módulo)           │
│          height: calc(100vh-56px)  │
│                                    │
├────────────────────────────────────┤
│  BOTTOM TAB BAR — 56px            │
└────────────────────────────────────┘
```

### Shell CSS Variables
```css
:root {
    --bg-base: #0f172a;
    --bg-panel: #1e293b;
    --accent-primary: #38bdf8;
    --glass-border: #334155;
    --muted: #64748b;
    --text-main: #f8fafc;
}
```

### Shell Mobile Overrides
```css
@media (max-width: 768px) {
    body { flex-direction: column; }
    .side-nav {
        position: fixed; bottom: 0; left: 0; right: 0;
        width: 100%; height: 56px;
        flex-direction: row; justify-content: space-around;
        border-right: none; border-top: 1px solid var(--glass-border);
        background: rgba(15, 23, 42, 0.98); z-index: 1000;
    }
    .content-frame { width: 100%; height: calc(100vh - 56px); flex: none; }
}
```

### Módulo (dentro do iframe)
Cada módulo é uma página HTML autônoma dentro do iframe. O body do módulo NÃO tem controle sobre o shell — o iframe define a viewport.

**Regra de ouro:** O iframe tem `height: calc(100vh - 56px)` no mobile. Qualquer conteúdo que ultrapasse essa altura precisa ser rolável. O `padding-bottom` no body compensa a bottom nav (56px).

---

## 3. Sistema de Cores

### Paleta Base (Dark Theme)
| Token | Hex | Uso |
|-------|-----|-----|
| `--bg-base` | `#0f172a` | Fundo da página |
| `--bg-panel` | `#1e293b` | Fundo de cards/painéis |
| `--bg-panel-hover` | `#334155` | Hover de cards |
| `--bg-input` | `#0b1220` | Fundo de campos de input |
| `--glass-border` | `#334155` | Bordas de painéis e separadores |

### Cores de Texto
| Token | Hex | Uso |
|-------|-----|-----|
| `--text-main` | `#f8fafc` | Texto principal, títulos |
| `--text-sec` | `#cbd5e1` | Texto secundário, labels |
| `--muted` | `#64748b` | Texto desabilitado, hints, timestamps |

### Cores de Acento
| Token | Hex | Uso |
|-------|-----|-----|
| `--accent-primary` | `#38bdf8` | Ação principal, links, destaques |
| `--accent-primary-hover` | `#0ea5e9` | Hover de elementos de ação |
| `--accent-glow` | `rgba(56,189,248,0.5)` | Brilho/sombra de acento |
| `--accent-gold` | `#e0b457` | Ouro, premiums, moedas (Market/Trade) |

### Cores de Status
| Token | Hex | Uso |
|-------|-----|-----|
| `--success` | `#10b981` | Sucesso, valores positivos, confirmação |
| `--ok` | `#34d399` | Variação de sucesso (Market/Trade) |
| `--danger` | `#ef4444` | Erro, exclusão, valores negativos |
| `--bad` | `#f87171` | Variação de perigo (Market/Trade) |
| `--warning` | `#f59e0b` | Aviso, badges de alerta |

### Cores Derivadas (opacidades)
```css
/* Fundo de cards internos */
background: rgba(15, 23, 42, 0.4);

/* Borda de hover */
border-color: rgba(56, 189, 248, 0.3);

/* Fundo de glow */
background: rgba(56, 189, 248, 0.08);

/* Fundo de glow forte */
background: rgba(56, 189, 248, 0.15);
```

### Regra de Combinação
- **Fundo escuro + texto claro**: sempre.
- **Acento azul** em fondos escuros: sempre com opacidade baixa (0.08-0.15).
- **Sucesso/Perigo**: nunca usar sozinhos — sempre com borda ou fundo sutil.
- **Gold**: apenas para elementos de valor/monetário.

---

## 4. Sistema Tipográfico

### Fontes
| Fonte | Uso | Peso |
|-------|-----|------|
| **Outfit** | Fonte principal de todo o sistema | 300, 400, 500, 600, 700 |
| **Web Pearl** | Títulos de página (h1) — decorative | Normal |

### Fallback Stack
```css
--font-main: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
```

### Escala de Tamanhos (Desktop)

| Nível | Token | Tamanho | Peso | Uso |
|-------|-------|---------|------|-----|
| **Display** | `--fs-display` | `2.5rem` (40px) | 700 | Valor grande destaque (barganha, CP projetado) |
| **H1** | `--fs-h1` | `1.8rem` (28.8px) | 600 | Título da página |
| **H2** | `--fs-h2` | `1.2rem` (19.2px) | 500 | Título de seção/painel |
| **H3** | `--fs-h3` | `1rem` (16px) | 600 | Subtítulo, card header |
| **Body** | `--fs-body` | `0.9rem` (14.4px) | 400 | Texto corrido, parágrafos |
| **Body-sm** | `--fs-body-sm` | `0.8rem` (12.8px) | 400 | Texto secundário em cards |
| **Caption** | `--fs-caption` | `0.75rem` (12px) | 500 | Labels, legendas, badges |
| **Micro** | `--fs-micro` | `0.65rem` (10.4px) | 600 | Tags, indicadores minúsculos |

### Escala de Tamanhos (Mobile)

| Nível | Tamanho Mobile | Notas |
|-------|---------------|-------|
| **Display** | `2rem` | Reduzido de 2.5rem |
| **H1** | `1.3rem` | Reduzido de 1.8rem |
| **H2** | `1rem` | Reduzido de 1.2rem |
| **H3** | `0.9rem` | Reduzido de 1rem |
| **Body** | `0.85rem` | Reduzido de 0.9rem |
| **Body-sm** | `0.78rem` | Reduzido de 0.8rem |
| **Caption** | `0.7rem` | Reduzido de 0.75rem |
| **Micro** | `0.6rem` | Reduzido de 0.65rem |

### Regras Tipográficas
- **H1** usa `Web Pearl` + gradiente branco→azul:
  ```css
  h1 {
      font-family: 'Web Pearl', 'Outfit', sans-serif;
      background: linear-gradient(90deg, #fff, var(--accent-primary));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
  }
  ```
- **H2** (section-title): `color: var(--text-sec)`, borda inferior com `var(--glass-border)`.
- **Labels**: sempre `text-transform: uppercase`, `letter-spacing: 0.5px`, cor `var(--muted)`.
- **Valores numéricos**: sempre `font-weight: 700`, cor `var(--accent-primary)`.
- **Mono/monospace**: usar para valores quantitativos (preços, quantidades).

---

## 5. Sistema de Espaçamento

### Escala (8px base)

| Token | Valor | Uso |
|-------|-------|-----|
| `--sp-1` | `0.25rem` (4px) | Espaçamento entre ícones e texto |
| `--sp-2` | `0.5rem` (8px) | Gap interno de cards pequenos |
| `--sp-3` | `0.75rem` (12px) | Padding de inputs, gap de listas |
| `--sp-4` | `1rem` (16px) | Padding padrão de cards, gap de grids |
| `--sp-5` | `1.25rem` (20px) | Padding de glass-panel desktop |
| `--sp-6` | `1.5rem` (24px) | Gap entre seções, margin de painéis |
| `--sp-8` | `2rem` (32px) | Padding de app-container desktop |
| `--sp-10` | `2.5rem` (40px) | Espaçamento entre grandes blocos |

### Regras de Espaçamento

| Contexto | Desktop | Mobile |
|----------|---------|--------|
| **App container padding** | `2rem` | `0.8rem` |
| **Glass panel padding** | `1.25rem` | `0.8rem` |
| **Gap entre glass panels** | `1.5rem` | `0.8rem` |
| **Gap entre cards do mesmo grid** | `1rem` | `0.6rem` |
| **Padding interno de card** | `1rem` | `0.6rem` |
| **Gap entre seções (stat-grid → main)** | `1.5rem` | `0.8rem` |
| **Margin-bottom do header (top-nav)** | `2rem` | `0.8rem` |
| **Padding-bottom (bottom nav compensation)** | N/A | `70px` |

### Bottom Nav Compensation
Todo módulo DEVE ter `padding-bottom: 70px` no body no mobile:
```css
@media (max-width: 768px) {
    /* Compensar bottom nav bar (56px) */
    body { padding-bottom: 70px !important; }
    .app-container { padding-bottom: 70px !important; }
}
```

**Por que 70px?** A bottom nav tem 56px. O extra 14px cria um respiro visual para o último elemento não ficar colado na barra.

---

## 6. Componentes

### 6.1 Glass Panel (Card Principal)
O componente base de todos os módulos.

```css
.glass-panel {
    background: var(--bg-panel);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 1.25rem;           /* Desktop */
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

@media (max-width: 768px) {
    .glass-panel { padding: 0.8rem !important; }
}
```

### 6.2 Section Title (H2 dentro de painel)
```css
.section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.1rem;          /* var(--fs-h2) */
    font-weight: 500;
    color: var(--text-sec);
    border-bottom: 1px solid var(--glass-border);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.section-title svg {
    color: var(--accent-primary);
    width: 20px;
}
```

### 6.3 Stat Card (Card de métrica)
```css
.stat-card {
    background: var(--bg-panel);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 1.25rem;           /* Desktop */
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.stat-label {
    color: var(--text-sec);
    font-size: 0.75rem;         /* var(--fs-caption) */
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
```

### 6.4 Stat Bar (Barra de métricas compacta)
Usado no Trade para mostrar resumo em uma linha.
```css
.stat-bar {
    display: flex;
    gap: 1rem;
    padding: 0.8rem;
    background: var(--bg-panel);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    border-right: 1px solid var(--glass-border);
    padding: 0.5rem 0;
}

.stat-item:last-child { border-right: none; }
```

**Mobile:** `flex-wrap: wrap` para quebrar em 2 linhas se necessário.

### 6.5 Button Primary
```css
.btn-primary {
    width: 50px;
    height: 50px;
    background: var(--accent-primary);
    color: #0f172a;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4px 15px var(--accent-glow);
    margin: 0 auto;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary:hover {
    background: var(--accent-primary-hover);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px var(--accent-glow);
}

.btn-primary:active { transform: scale(0.95); }
.btn-primary svg { width: 24px; height: 24px; stroke-width: 3px; }
```

### 6.6 Input Fields
```css
/* Input genérico */
input[type="number"], input[type="text"] {
    background: transparent;
    border: none;
    color: var(--accent-primary);
    font-weight: 700;
    font-family: inherit;
    text-align: right;
    outline: none;
    padding: 0.25rem 0;
    font-size: 1.1rem;          /* var(--fs-body) */
}

input:focus { color: var(--text-main); }

/* Input de destaque (grande) */
.large-input {
    font-size: 2.8rem;          /* var(--fs-display) */
    font-weight: 700;
    border: none;
    background: transparent;
    padding: 0;
    color: var(--accent-primary);
    outline: none;
}

/* Input médio */
.large-input-sm {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent-primary);
    text-align: center;
}
```

### 6.7 Toggle Switch
```css
.switch {
    position: relative;
    display: inline-block;
    width: 42px;
    height: 22px;
}

.switch input { opacity: 0; width: 0; height: 0; }

.slider {
    position: absolute;
    inset: 0;
    background: var(--muted);
    border-radius: 34px;
    transition: 0.3s;
    cursor: pointer;
}

.slider::before {
    content: "";
    position: absolute;
    width: 18px; height: 18px;
    left: 2px; bottom: 2px;
    background: white;
    border-radius: 50%;
    transition: 0.3s;
}

.switch input:checked + .slider { background: var(--accent-primary); }
.switch input:checked + .slider::before { transform: translateX(20px); }
```

### 6.8 Modal
```css
.modal {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(4px);
    z-index: 1000;
    justify-content: center;
    align-items: center;
}

.modal.active { display: flex; }

.modal-content {
    width: 100%;
    max-width: 400px;           /* Desktop */
    padding: 2rem;
    background: var(--bg-panel);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    animation: modalAppear 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes modalAppear {
    from { opacity: 0; transform: translateY(20px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

@media (max-width: 768px) {
    .modal-content { max-width: 95vw !important; padding: 1.2rem !important; }
}
```

### 6.9 Badge
```css
.badge {
    background: var(--warning);
    color: #000;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
```

### 6.10 Progress Bar
```css
.progress-bar-container {
    height: 12px;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 6px;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-primary), #818cf8);
    transition: width 1s ease-out;
}
```

### 6.11 Quick Button (Botão de ação rápida)
```css
.quick-btn {
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid var(--glass-border);
    color: var(--accent-primary);
    font-family: inherit;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 0.25rem 0.6rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    width: fit-content;
}

.quick-btn:hover {
    background: rgba(56, 189, 248, 0.15);
    border-color: var(--accent-primary);
    transform: translateY(-1px);
}
```

---

## 7. Grids e Layout Responsivo

### Grid System

| Contexto | Desktop | Mobile |
|----------|---------|--------|
| **Dashboard grid** (2 colunas) | `grid-template-columns: 2fr 1fr` | `1fr` |
| **Status row** (2 cards lado a lado) | `grid-template-columns: 1fr 1fr` | `1fr` |
| **Stat grid** (3+ cards) | `grid-template-columns: repeat(3, 1fr)` | `1fr` |
| **Stat grid** (4+ cards) | `grid-template-columns: repeat(4, 1fr)` | `repeat(2, 1fr)` |
| **Calendário** | `repeat(7, 1fr)` | `repeat(7, 1fr)` (com fonte menor) |
| **Trade towns** | `repeat(auto-fill, minmax(min(340px, 100%), 1fr))` | `1fr` |
| **Itens grid** (inventário) | `repeat(3, 1fr)` | `repeat(2, 1fr)` |

### Flex Layouts

| Contexto | Desktop | Mobile |
|----------|---------|--------|
| **Status inputs** (2 campos) | `display: flex; gap: 1rem` | `flex-direction: column` |
| **Summary footer** | `display: flex; gap: 2rem; justify-content: center` | `flex-direction: column; align-items: center; gap: 0.5rem` |
| **Bargain row** | `display: flex` | `flex-direction: column` |
| **Header (top-nav)** | `display: flex; justify-content: space-between` | `flex-wrap: wrap; gap: 0.5rem` |

### Regra de Empilhamento
No mobile, grids com mais de 1 coluna DEVEM empilhar para `1fr`. A exceção é o calendário (7 colunas) e itens (2 colunas).

```css
@media (max-width: 768px) {
    /* Empilhar grids */
    .dashboard-grid { grid-template-columns: 1fr !important; }
    .status-row { grid-template-columns: 1fr !important; }
    .stat-grid { grid-template-columns: 1fr !important; }
    
    /* Empilhar flex */
    .status-inputs { flex-direction: column !important; }
    .summary-footer { flex-direction: column !important; align-items: center !important; }
}
```

---

## 8. Mobile Breakpoints

### Breakpoint Único
```css
@media (max-width: 768px) { /* ... */ }
```

Não usar múltiplos breakpoints. O design é binário: desktop (>768px) e mobile (≤768px).

### Checklist Mobile Completo

Todo módulo DEVE ter estas regras no `@media`:

```css
@media (max-width: 768px) {
    /* 1. RESET de body */
    html { overflow-x: hidden !important; }
    body {
        overflow-y: auto !important;
        overflow-x: hidden !important;
        padding: 0.8rem !important;
        height: auto !important;
        padding-bottom: 70px !important;  /* Bottom nav */
    }
    
    /* 2. RESET de container (se existir .app-container) */
    .app-container {
        padding: 0.8rem !important;
        overflow-x: hidden !important;
        width: 100% !important;
        max-width: 100vw !important;
        height: auto !important;
        min-height: auto !important;
        display: block !important;         /* Se era flex no desktop */
    }
    
    /* 3. Empilhar grids */
    /* ... */
    
    /* 4. Reduzir fontes */
    /* ... */
    
    /* 5. Compensar bottom nav (no FINAL do @media) */
    body { padding-bottom: 70px !important; }
    .app-container { padding-bottom: 70px !important; }
}
```

### Erros Comuns (e como evitar)

| Erro | Causa | Solução |
|------|-------|---------|
| Conteúdo cortado pela bottom nav | Falta `padding-bottom: 70px` | Adicionar no body E no .app-container |
| Fonte não muda no mobile | `input[type="text"]` tem especificidade maior | Usar `input.large-input` (mesma especificidade + !important) |
| Card vaza para a direita | `overflow-x: hidden` não aplicado | Adicionar em body, html, e containers |
| Grid não empilha | Seletor errado no media query | Verificar o nome exato da classe no HTML |
| Layout quebra | `display: flex` removido no mobile | Só remover display:flex se o layout não depender dele |
| Body não rola | `height: 100vh` sem override | Usar `height: auto !important` |

---

## 9. Animações e Transições

### Transições Padrão
```css
/* Transição suave (padrão) */
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

/* Transição lenta (para barras de progresso) */
transition: width 1s ease-out;

/* Transição de modal */
animation: modalAppear 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

### Keyframes Padrão
```css
@keyframes modalAppear {
    from { opacity: 0; transform: translateY(20px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes successPulse {
    0% { background-color: var(--accent-primary); transform: scale(1); }
    50% { background-color: var(--success); transform: scale(1.05); }
    100% { background-color: var(--accent-primary); transform: scale(1); }
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
```

### Hover Effects
```css
/* Card hover */
.card:hover {
    border-color: var(--accent-primary);
    background: rgba(15, 23, 42, 0.6);
}

/* Botão hover */
.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px var(--accent-glow);
}

/* Botão active */
.btn:active { transform: scale(0.95); }

/* Item de lista hover */
.list-item:hover {
    transform: translateX(5px);
    border-color: var(--accent-primary);
}
```

### JavaScript — Animações Sutis
```javascript
// Fade in ao carregar
element.style.opacity = '0';
element.style.transform = 'translateY(10px)';
requestAnimationFrame(() => {
    element.style.transition = 'opacity 0.3s, transform 0.3s';
    element.style.opacity = '1';
    element.style.transform = 'translateY(0)';
});

// Counter animado
function animateValue(el, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        el.textContent = Math.round(start + range * eased).toLocaleString('pt-BR');
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// Auto-save indicator
function showSaved() {
    const el = document.getElementById('save-text');
    el.textContent = '✓ Salvo';
    el.style.color = 'var(--success)';
    setTimeout(() => {
        el.textContent = 'Dados sincronizados';
        el.style.color = 'var(--muted)';
    }, 2000);
}
```

---

## 10. Temas (Dark/Light)

### Estrutura
O sistema é dark-first. Para suportar light theme, usar `data-theme` no `<html>`:

```css
/* Dark (padrão) */
:root {
    --bg-base: #0f172a;
    --bg-panel: #1e293b;
    --text-main: #f8fafc;
    --text-sec: #cbd5e1;
    --muted: #64748b;
    --glass-border: #334155;
    --accent-primary: #38bdf8;
}

/* Light */
[data-theme="light"] {
    --bg-base: #f8fafc;
    --bg-panel: #ffffff;
    --text-main: #0f172a;
    --text-sec: #475569;
    --muted: #94a3b8;
    --glass-border: #e2e8f0;
    --accent-primary: #0284c7;
    --accent-glow: rgba(2, 132, 199, 0.3);
    --glass-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05),
                    0 2px 4px -1px rgba(0, 0, 0, 0.03);
}
```

### Toggle de Tema
```javascript
function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('bdo-theme', next);
}

// Inicializar
const saved = localStorage.getItem('bdo-theme') || 'dark';
document.documentElement.setAttribute('data-theme', saved);
```

### Regras para Light Theme
- `background: transparent` em inputs (herda fundo do painel).
- Sombras mais leves.
- Bordas mais suaves.
- Acento azul mais escuro (`#0284c7` em vez de `#38bdf8`).
- Gradiente do H1: `#0f172a` → `#0284c7`.

---

## 11. Padrões por Módulo

### Dashboard (`/dashboard/`)
- **Layout**: 2 colunas (2fr 1fr) → 1 coluna no mobile.
- **Stats**: 4 cards em row → 2x2 no mobile.
- **Calendário**: Grid 7 colunas (mantém no mobile, fonte reduz).
- **Fontes maiores**: Calendário usa 0.6rem-0.75rem no mobile.

### Bartering (`/bartering/`)
- **Layout**: Stat grid (3 cards) + Dashboard grid (2fr 1fr) → empilha tudo.
- **Componentes**: Routes grid (2 colunas → 1), Exp calculator, Modal de tabela.
- **Padrão de referência**: Este módulo tem o mobile mais bem resolvido.

### Hunting (`/hunting/`)
- **Layout**: Flex column com cards empilhados.
- **Calendar page**: Página separada com grid auto-fit.
- **CSS separado**: Usa `static/css/style.css` externo.

### CP (`/cp/`)
- **Layout**: 3 colunas (350px 1fr 350px) → 1 coluna no mobile.
- **Status row**: 2 cards lado a lado → empilha.
- **OCR**: Paste zone com drag & drop.

### Market (`/market/`)
- **Layout**: Flex column com lista + detalhe.
- **Grids**: Auto-fill com minmax.
- **Cores extras**: `--accent-gold`, `--ok`, `--bad`.

### Trade (`/trade/`)
- **Layout**: Stat bar + Toolbar + Town grid.
- **Body é flex column**: NÃO mudar display no mobile.
- **Accordion**: Cards colapsados por padrão no mobile.
- **Grid towns**: `repeat(auto-fill, minmax(min(340px, 100%), 1fr))` → `1fr`.

---

## 12. Checklist de Implementação

Antes de entregar qualquer módulo, verificar:

- [ ] **CSS Variables**: Todas as cores usam tokens `--*`, não hex hardcoded.
- [ ] **Fontes**: Todos os tamanhos seguem a escala do sistema.
- [ ] **Espaçamento**: Todos os valores seguem a escala `--sp-*`.
- [ ] **Glass panels**: Usam o padrão `background + border + border-radius + shadow`.
- [ ] **Mobile body**: `overflow-y: auto`, `height: auto`, `padding-bottom: 70px`.
- [ ] **Mobile container**: `height: auto`, `min-height: auto`, `display: block` (se era flex).
- [ ] **Mobile grids**: Todos empilham para `1fr`.
- [ ] **Mobile fonts**: Reduzidos conforme a escala mobile.
- [ ] **Mobile spacing**: `0.8rem` para containers, `0.6rem` para gaps.
- [ ] **Bottom nav**: `padding-bottom: 70px` no body E no container.
- [ ] **Transições**: Todos os interactive elements têm `transition: all 0.2s`.
- [ ] **Hover states**: Cards, botões, items têm hover.
- [ ] **Modais**: `max-width: 95vw` no mobile.
- [ ] **Overflow**: `overflow-x: hidden` em body, html, e containers principais.
- [ ] **No-cache**: `Cache-Control: no-store` no Flask para evitar problemas de cache.

---

## Template Base — Copiar e Colar

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BDO Module Name</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @font-face {
            font-family: 'Web Pearl';
            src: url('...') format('truetype');
        }

        :root {
            --bg-base: #0f172a;
            --bg-panel: #1e293b;
            --bg-panel-hover: #334155;
            --bg-input: #0b1220;
            --accent-primary: #38bdf8;
            --accent-primary-hover: #0ea5e9;
            --accent-glow: rgba(56, 189, 248, 0.5);
            --accent-gold: #e0b457;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --muted: #64748b;
            --text-main: #f8fafc;
            --text-sec: #cbd5e1;
            --glass-border: #334155;
            --glass-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            --font-main: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-base);
            color: var(--text-main);
            font-family: var(--font-main);
            line-height: 1.6;
            overflow: hidden;
            height: 100vh;
        }

        .app-container {
            max-width: 1700px;
            margin: 0 auto;
            padding: 2rem;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }

        h1 {
            font-family: 'Web Pearl', 'Outfit', sans-serif;
            font-size: 1.8rem;
            background: linear-gradient(90deg, #fff, var(--accent-primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--glass-border);
        }

        .glass-panel {
            background: var(--bg-panel);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: var(--glass-shadow);
        }

        .section-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--text-sec);
            border-bottom: 1px solid var(--glass-border);
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }

        .section-title svg { color: var(--accent-primary); width: 20px; }

        /* ===== MOBILE ===== */
        @media (max-width: 768px) {
            html { overflow-x: hidden !important; }
            body {
                overflow-y: auto !important;
                overflow-x: hidden !important;
                padding: 0.8rem !important;
                height: auto !important;
            }
            .app-container {
                padding: 0.8rem !important;
                overflow-x: hidden !important;
                width: 100% !important;
                max-width: 100vw !important;
                height: auto !important;
                min-height: auto !important;
                display: block !important;
            }
            .top-nav {
                margin-bottom: 0.8rem !important;
                padding-bottom: 0.5rem !important;
                flex-wrap: wrap !important;
                gap: 0.5rem !important;
            }
            h1 { font-size: 1.3rem !important; }
            .glass-panel { padding: 0.8rem !important; }
            .section-title { font-size: 1rem !important; margin-bottom: 0.8rem !important; }

            /* Compensar bottom nav bar (56px) */
            body { padding-bottom: 70px !important; }
            .app-container { padding-bottom: 70px !important; }
        }
    </style>
</head>
<body class="dark-theme">
    <div class="app-container">
        <header class="top-nav">
            <div class="logo-area">
                <i data-lucide="icon-name" class="logo-icon"></i>
                <h1>Module Title</h1>
            </div>
            <div class="nav-info">Descrição</div>
        </header>

        <main class="dashboard-grid">
            <!-- Conteúdo do módulo -->
        </main>
    </div>

    <script>lucide.createIcons();</script>
</body>
</html>
```

---

> **Este documento é a referência.** Qualquer alteração visual no BDOHub deve starting aqui. Se algo não está documentado, documente antes de implementar.
