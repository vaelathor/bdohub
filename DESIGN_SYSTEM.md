# BDOHub Design System — Guia Definitivo

> **Versão:** 2.1  
> **Autor:** Buffy (Codebuff)  
> **Data:** Ago 2026  
> **Referências:** Binance, Coinbase, Cal.com, Airtable, ClickHouse  
> **Objetivo:** Referência única e definitiva para construir, manter e reformular qualquer página do BDOHub. Este documento é lido por agentes AI para gerar UI consistente.

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura de Tokens](#2-arquitetura-de-tokens)
3. [Cores](#3-cores)
4. [Tipografia](#4-tipografia)
5. [Espaçamento](#5-espaçamento)
6. [Formas (Border Radius)](#6-formas-border-radius)
7. [Elevação e Profundidade](#7-elevação-e-profundidade)
8. [Componentes](#8-componentes)
9. [Layout e Grid](#9-layout-e-grid)
10. [Comportamento Responsivo](#10-comportamento-responsivo)
11. [Animações e Transições](#11-animações-e-transições)
12. [Temas (Dark/Light)](#12-temas-darklight)
13. [Acessibilidade](#13-acessibilidade)
14. [Padrões por Módulo](#14-padrões-por-módulo)
15. [Guia de Iteração](#15-guia-de-iteração)
16. [Do's and Don'ts](#16-dos-and-donts)
17. [Gaps Conhecidos](#17-gaps-conhecidos)
18. [Template Base](#18-template-base)

---

## 1. Visão Geral

### Princípios Fundamentais

1. **Dark-first**: O tema padrão é escuro. Light é opcional e compartilha os mesmos tokens.
2. **Tokens sobre valores hardcoded**: Toda cor, tamanho, espaçamento e forma é um token nomeado. Nunca usar hex/px direto no componente.
3. **Um acento por vez**: Azul (`--accent-primary`) é o único cor de ação. Ouro (`--accent-gold`) aparece apenas em contextos monetários. Verde/vermelho são semânticos (sucesso/erro), não decorativos.
4. **Consistência visual**: Todos os módulos compartilham o mesmo DNA. Trocar de módulo não deve parecer trocar de site.
5. **Flat surfaces com cor-block separation**: Profundidade vem do contraste entre camadas de cor, não de sombras pesadas ou glassmorphism exagerado.
6. **Mobile-first nos padrões**: O `@media` corrige para mobile. O base é desktop.

### O que NÃO fazer

- Nunca usar `height: 100vh` no body sem override mobile.
- Nunca usar `overflow: hidden` no body sem `overflow-y: auto` no mobile.
- Nunca misturar frameworks CSS.
- Nunca definir `font-size` com valores fora da escala do sistema.
- Nunca usar `!important` sem justificativa (exceto em `@media` overrides).
- Nunca usar cores hardcoded — sempre usar tokens.
- Nunca mudar `display: flex` no mobile se o layout depender dele.
- Nunca usar sombras em cards sobre fundo escuro (usar contraste de cor).

---

## 2. Arquitetura de Tokens

### O que é um Token

Um token é um valor nomeado que referencia outro token. Tokens criam uma linguagem compartilhada entre design e código. NUNCA usar valores hardcoded em componentes — sempre referenciar tokens.

### Hierarquia de Tokens

```
Primitive Tokens (valores brutos)
  → Semantic Tokens (significado)
    → Component Tokens (uso específico)
```

**Primitive:** `#0f172a`  
**Semantic:** `var(--bg-base)` → "este é o fundo da página"  
**Component:** `var(--glass-bg)` → "este é o fundo de um painel glass" (= `var(--bg-panel)`)

### Token Categories

| Categoria | Tokens | Exemplo |
|-----------|--------|---------|
| **Cores** | `--bg-*`, `--text-*`, `--accent-*`, `--status-*` | `--bg-panel: #1e293b` |
| **Tipografia** | `--fs-*` | `--fs-h1: 1.8rem` |
| **Espaçamento** | `--sp-*` | `--sp-4: 1rem` |
| **Formas** | `--radius-*` | `--radius-lg: 12px` |
| **Sombras** | `--shadow-*` | `--shadow-card: 0 4px 6px ...` |
| **Componentes** | `--comp-*` | `--comp-btn-height: 44px` |
| **Ícones** | `--icon-*` | `--icon-md: 20px` |
| **Z-Index** | `--z-*` | `--z-modal: 1000` |

### Referência entre Tokens

```css
/* Componente referencia token semântico */
.glass-panel {
    background: var(--bg-panel);           /* semantic */
    border: 1px solid var(--glass-border); /* semantic */
    border-radius: var(--radius-lg);       /* shape */
    box-shadow: var(--shadow-card);        /* elevation */
    padding: var(--sp-5);                  /* spacing */
}
```

---

## 3. Cores

### Paleta Base (Dark Theme)

#### Superfícies
| Token | Hex | Uso |
|-------|-----|-----|
| `--bg-base` | `#0f172a` | Fundo da página (canvas) |
| `--bg-panel` | `#1e293b` | Fundo de cards/painéis (surface-card) |
| `--bg-panel-hover` | `#253349` | Hover de cards |
| `--bg-input` | `#0b1220` | Fundo de campos de input |
| `--bg-elevated` | `#334155` | Superfícies elevadas (modais, dropdowns) |
| `--bg-inset` | `#0a1020` | Fundo interno de inputs e seções recuadas |

#### Bordas
| Token | Hex | Uso |
|-------|-----|-----|
| `--glass-border` | `#334155` | Bordas de painéis, separadores |
| `--glass-border-hover` | `#475569` | Borda em estado hover |
| `--border-strong` | `#64748b` | Bordas de destaque (input focus) |

#### Texto
| Token | Hex | Uso |
|-------|-----|-----|
| `--text-main` | `#f8fafc` | Texto principal, títulos |
| `--text-sec` | `#cbd5e1` | Texto secundário, labels |
| `--muted` | `#64748b` | Texto desabilitado, hints, timestamps |
| `--text-on-accent` | `#0f172a` | Texto sobre fundo de acento (azul) |
| `--text-on-danger` | `#ffffff` | Texto sobre fundo de perigo (vermelho) |

#### Acento
| Token | Hex | Uso |
|-------|-----|-----|
| `--accent-primary` | `#38bdf8` | Ação principal, links, destaques |
| `--accent-primary-hover` | `#0ea5e9` | Hover de elementos de ação |
| `--accent-primary-muted` | `rgba(56,189,248,0.15)` | Fundo sutil de acento |
| `--accent-primary-soft` | `rgba(56,189,248,0.08)` | Fundo very subtle de acento |
| `--accent-gold` | `#e0b457` | Ouro, premiums, moedas (Market/Trade) |

#### Status
| Token | Hex | Uso |
|-------|-----|-----|
| `--success` | `#10b981` | Sucesso, valores positivos, confirmação |
| `--danger` | `#ef4444` | Erro, exclusão, valores negativos |
| `--warning` | `#f59e0b` | Aviso, badges de alerta |
| `--info` | `#3b82f6` | Informação, focus ring |
| `--ok` | `#22c55e` | Status positivo suave (quantidade disponível, estoque ok) |
| `--bad` | `#f87171` | Status negativo suave (estoque baixo, atenção menor que danger) |

> **Nota sobre `--ok` e `--bad`**: Estes tokens são intencionalmente mais suaves que `--success` e `--danger`. `--ok` (#22c55e) é ligeiramente mais brilhante que `--success` (#10b981), indicando um estado positivo "de rotina" (estoque suficiente, item disponível). `--bad` (#f87171) é mais claro que `--danger` (#ef4444), indicando atenção moderada (estoque baixo, preço acima do mercado) sem o peso visual de uma falha crítica. Usados no módulo Market e Trade para diferenciação sutil entre severidades.

### Paleta Light Theme

| Token | Dark | Light |
|-------|------|-------|
| `--bg-base` | `#0f172a` | `#f8fafc` |
| `--bg-panel` | `#1e293b` | `#ffffff` |
| `--bg-input` | `#0b1220` | `#f1f5f9` |
| `--text-main` | `#f8fafc` | `#0f172a` |
| `--text-sec` | `#cbd5e1` | `#475569` |
| `--muted` | `#64748b` | `#94a3b8` |
| `--glass-border` | `#334155` | `#e2e8f0` |
| `--accent-primary` | `#38bdf8` | `#0284c7` |
| `--accent-glow` | `rgba(56,189,248,0.5)` | `rgba(2,132,199,0.3)` |

### Regras de Combinação

- **Fundo escuro + texto claro**: sempre no dark theme.
- **Acento azul em fundo escuro**: sempre com opacidade baixa (0.08-0.15).
- **Sucesso/Perigo**: nunca usar sozinhos — sempre com borda ou fundo sutil.
- **Gold**: apenas para elementos de valor/monetário.
- **Nunca usar verde/vermelho como fundo de card** — são semânticos de status, não decorativos.
- **Hairline borders**: usar `var(--glass-border)` para 1px separadores.

---

## 4. Tipografia

### Fontes

| Fonte | Uso | Peso | Fallback |
|-------|-----|------|----------|
| **Outfit** | Fonte principal (body, UI, títulos) | 300, 400, 500, 600, 700 | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` |

> **Nota**: O sistema usa **apenas Outfit** como fonte carregada. Para títulos H1, usa-se Outfit 700 com gradiente branco→azul para crear destaque visual sem precisar de uma segunda fonte.

### Escala Tipográfica (Desktop)

| Token | Tamanho | Peso | Line Height | Letter Spacing | Uso |
|-------|---------|------|-------------|----------------|-----|
| `--fs-display` | `2.5rem` (40px) | 700 | 1.1 | -0.5px | Número de destaque (barganha, CP projetado) |
| `--fs-h1` | `1.8rem` (28.8px) | 600 | 1.2 | 0 | Título da página |
| `--fs-h2` | `1.2rem` (19.2px) | 500 | 1.3 | 0 | Título de seção/painel |
| `--fs-h3` | `1rem` (16px) | 600 | 1.4 | 0 | Subtítulo, card header |
| `--fs-body` | `0.9rem` (14.4px) | 400 | 1.5 | 0 | Texto corrido |
| `--fs-body-sm` | `0.8rem` (12.8px) | 400 | 1.5 | 0 | Texto secundário em cards |
| `--fs-caption` | `0.75rem` (12px) | 500 | 1.4 | 0.5px | Labels, legendas, badges |
| `--fs-micro` | `0.65rem` (10.4px) | 600 | 1.3 | 0.5px | Tags, indicadores minúsculos |

### Escala Tipográfica (Mobile)

| Token | Desktop | Mobile | Delta |
|-------|---------|--------|-------|
| `--fs-display` | 2.5rem | 2rem | -20% |
| `--fs-h1` | 1.8rem | 1.3rem | -28% |
| `--fs-h2` | 1.2rem | 1rem | -17% |
| `--fs-h3` | 1rem | 0.9rem | -10% |
| `--fs-body` | 0.9rem | 0.85rem | -6% |
| `--fs-body-sm` | 0.8rem | 0.78rem | -3% |
| `--fs-caption` | 0.75rem | 0.7rem | -7% |
| `--fs-micro` | 0.65rem | 0.6rem | -8% |

### Regras Tipográficas

1. **H1** usa Outfit 700 + gradiente branco→azul para destaque visual.
2. **H2** (section-title): `color: var(--text-sec)`, borda inferior com `var(--glass-border)`.
3. **Labels**: sempre `text-transform: uppercase`, `letter-spacing: 0.5px`, cor `var(--muted)`.
4. **Valores numéricos**: sempre `font-weight: 700`, cor `var(--accent-primary)`.
5. **Display numbers**: usar `var(--fs-display)` para números de destaque.
6. **Nunca usar font-weight 700 em body text** — reservado para headings e números.

### Font Substitutes

| Fonte Original | Substituto | Notas |
|----------------|------------|-------|
| Outfit | Inter | Ajustar line-height +0.05 |
| JetBrains Mono (monospace) | ui-monospace | Para valores tabulares |

---

## 5. Espaçamento

### Escala (4px base)

| Token | Valor | Uso |
|-------|-------|-----|
| `--sp-1` | `0.25rem` (4px) | Gap entre ícones e texto |
| `--sp-2` | `0.5rem` (8px) | Gap interno de cards pequenos |
| `--sp-3` | `0.75rem` (12px) | Padding de inputs, gap de listas |
| `--sp-4` | `1rem` (16px) | Padding padrão de cards, gap de grids |
| `--sp-5` | `1.25rem` (20px) | Padding de glass-panel desktop |
| `--sp-6` | `1.5rem` (24px) | Gap entre seções, margin de painéis |
| `--sp-8` | `2rem` (32px) | Padding de app-container desktop |
| `--sp-10` | `2.5rem` (40px) | Espaçamento entre grandes blocos |

### Regras Desktop vs Mobile

| Contexto | Desktop | Mobile |
|----------|---------|--------|
| App container padding | `var(--sp-8)` (2rem) | `var(--sp-4)` (1rem) |
| Glass panel padding | `var(--sp-5)` (1.25rem) | `var(--sp-4)` (1rem) |
| Gap entre glass panels | `var(--sp-6)` (1.5rem) | `var(--sp-4)` (1rem) |
| Gap entre cards do mesmo grid | `var(--sp-4)` (1rem) | `var(--sp-3)` (0.75rem) |
| Gap entre seções | `var(--sp-6)` (1.5rem) | `var(--sp-4)` (1rem) |
| Header margin-bottom | `var(--sp-8)` (2rem) | `var(--sp-4)` (1rem) |
| Padding-bottom (bottom nav) | N/A | 70px |

### Bottom Nav Compensation

Todo módulo DEVE ter `padding-bottom: 70px` no body no mobile:

```css
@media (max-width: 768px) {
    body { padding-bottom: 70px !important; }
    .app-container { padding-bottom: 70px !important; }
}
```

**Por que 70px?** A bottom nav tem 56px + 14px de respiro visual.

---

## 6. Formas (Border Radius)

### Escala

| Token | Valor | Uso |
|-------|-------|-----|
| `--radius-xs` | `4px` | Tags inline, badges pequenos |
| `--radius-sm` | `6px` | Botões pequenos, inline actions |
| `--radius-md` | `8px` | Inputs, botões padrão |
| `--radius-lg` | `12px` | Cards, painéis glass, modais |
| `--radius-xl` | `16px` | Cards elevados, CTAs bands |
| `--radius-pill` | `9999px` | Botões prominentes, badges pill |
| `--radius-full` | `50%` | Avatares, ícones circulares |

### Regras

- **Cards e painéis**: sempre `--radius-lg` (12px).
- **Botões**: `--radius-md` (8px) padrão, `--radius-pill` para CTAs importantes.
- **Inputs**: `--radius-md` (8px).
- **Badges pill**: `--radius-pill` (9999px).
- **Avatares/ícones**: `--radius-full` (50%).
- **Nunca usar 0px (sharp corners)** em elementos interativos.

---

## 7. Elevação e Profundidade

### Níveis de Elevação

| Nível | Tratamento | Uso |
|-------|-----------|-----|
| **Flat** | Sem sombra, sem borda | Body, nav, hero bands |
| **Hairline** | 1px `var(--glass-border)` | Inputs, separadores, bordas de cards |
| **Card** | `var(--shadow-card)` | Cards, painéis glass |
| **Elevated** | `var(--shadow-elevated)` | Modais, dropdowns, tooltips |
| **Focus** | `0 0 0 2px var(--info)` | Focus ring de teclado |

### Tokens de Sombra

```css
:root {
    /* Card padrão */
    --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                   0 2px 4px -1px rgba(0, 0, 0, 0.06);
    
    /* Elevado (modais, dropdowns, tooltips) */
    --shadow-elevated: 0 10px 15px -3px rgba(0, 0, 0, 0.2),
                       0 4px 6px -2px rgba(0, 0, 0, 0.1);
    
    /* Glow de acento */
    --shadow-glow: 0 4px 15px var(--accent-glow);
}
```

### Filosofia

BDOHub usa **flat surfaces com cor-block separation**. Profundidade vem do contraste entre camadas de cor (ex: `--bg-base` vs `--bg-panel`), não de sombras pesadas. Sombras são sutis e usadas apenas para indicar elevação funcional (cards, modais).

- **NUNCA usar glassmorphism pesado** (blur, transparência exagerada).
- **NUNCA usar sombras coloridas** (exceto glow de acento em botões).
- **Hairline borders** são o principal mecanismo de separação visual.

---

## 8. Componentes

### 8.1 Glass Panel (Card Principal)

O componente base de todos os módulos.

```css
.glass-panel {
    background: var(--bg-panel);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);        /* 12px */
    padding: var(--sp-5);                    /* 1.25rem desktop */
    box-shadow: var(--shadow-card);
}

/* Variantes */
.glass-panel.inset {
    background: var(--bg-inset);
    border-color: transparent;
}

.glass-panel.elevated {
    background: var(--bg-elevated);
    box-shadow: var(--shadow-elevated);
}

@media (max-width: 768px) {
    .glass-panel { padding: var(--sp-4) !important; }  /* 1rem */
}
```

### 8.2 Section Title (H2)

```css
.section-title {
    display: flex;
    align-items: center;
    gap: var(--sp-2);                       /* 0.5rem */
    font-size: var(--fs-h2);                /* 1.2rem */
    font-weight: 500;
    color: var(--text-sec);
    border-bottom: 1px solid var(--glass-border);
    padding-bottom: var(--sp-2);
    margin-bottom: var(--sp-4);
}

.section-title svg {
    color: var(--accent-primary);
    width: var(--icon-md);                  /* 20px */
    height: var(--icon-md);
}

@media (max-width: 768px) {
    .section-title {
        font-size: 1rem !important;
        margin-bottom: var(--sp-4) !important;
    }
}
```

### 8.3 Stat Card (Métrica)

```css
.stat-card {
    background: var(--bg-panel);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: var(--sp-5);
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
}

.stat-label {
    color: var(--text-sec);
    font-size: var(--fs-caption);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stat-value {
    color: var(--accent-primary);
    font-size: var(--fs-h2);
    font-weight: 700;
}

.stat-change {
    font-size: var(--fs-caption);
    font-weight: 600;
}

.stat-change.positive { color: var(--success); }
.stat-change.negative { color: var(--danger); }
```

### 8.4 Stat Bar (Métricas Compacta)

```css
.stat-bar {
    display: flex;
    gap: var(--sp-4);
    padding: var(--sp-4);
    background: var(--bg-panel);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    border-right: 1px solid var(--glass-border);
    padding: var(--sp-2) 0;
}

.stat-item:last-child { border-right: none; }

.stat-item-icon {
    font-size: 1.5rem;
    margin-bottom: var(--sp-1);
}

.stat-item-value {
    font-size: var(--fs-body);
    font-weight: 700;
    color: var(--accent-primary);
}

.stat-item-label {
    font-size: var(--fs-micro);
    color: var(--muted);
    text-transform: uppercase;
}

@media (max-width: 768px) {
    .stat-bar { flex-wrap: wrap; gap: var(--sp-3); }
    .stat-item { flex: 0 0 calc(50% - var(--sp-3)); border-right: none; }
    .stat-item:nth-child(2) { border-right: none; }
}
```

### 8.5 Buttons

```css
.btn {
    height: var(--comp-btn-height);
    font-family: var(--font-main);
    font-size: var(--fs-body);
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--sp-2);
    padding: 0 var(--sp-4);
    border: none;
    border-radius: var(--radius-md);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* --- Primary --- */
.btn-primary {
    background: var(--accent-primary);
    color: var(--text-on-accent);
    box-shadow: var(--shadow-glow);
}

.btn-primary:hover {
    background: var(--accent-primary-hover);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px var(--accent-glow);
}

.btn-primary:active {
    transform: scale(0.97);
    transition-duration: 0.1s;
}

.btn-primary:disabled {
    background: var(--muted);
    color: var(--bg-panel);
    box-shadow: none;
    cursor: not-allowed;
    transform: none;
}

/* --- Secondary --- */
.btn-secondary {
    background: transparent;
    color: var(--text-main);
    border: 1px solid var(--glass-border);
    box-shadow: none;
}

.btn-secondary:hover {
    border-color: var(--accent-primary);
    background: var(--accent-primary-soft);
}

.btn-secondary:active {
    transform: scale(0.97);
    transition-duration: 0.1s;
}

.btn-secondary:disabled {
    background: transparent;
    color: var(--muted);
    border-color: var(--bg-inset);
    cursor: not-allowed;
    transform: none;
}

/* --- Danger --- */
.btn-danger {
    background: var(--danger);
    color: var(--text-on-danger);
    box-shadow: none;
}

.btn-danger:hover {
    background: #dc2626;
    transform: translateY(-2px);
}

.btn-danger:active {
    transform: scale(0.97);
    transition-duration: 0.1s;
}

.btn-danger:disabled {
    background: var(--bg-inset);
    color: var(--muted);
    cursor: not-allowed;
    transform: none;
}

/* --- Ghost --- */
.btn-ghost {
    background: transparent;
    color: var(--accent-primary);
    box-shadow: none;
    padding: var(--sp-1) var(--sp-3);
}

.btn-ghost:hover {
    background: var(--accent-primary-soft);
}

.btn-ghost:disabled {
    color: var(--muted);
    cursor: not-allowed;
    transform: none;
}

/* --- Tamanhos --- */
.btn-sm { height: 32px; font-size: var(--fs-caption); padding: 0 var(--sp-3); }
.btn-lg { height: 52px; font-size: var(--fs-h3); padding: 0 var(--sp-6); }
```

### 8.6 Input Fields

```css
/* Input genérico */
input[type="number"],
input[type="text"],
input[type="search"] {
    background: var(--bg-input);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    color: var(--text-main);
    font-family: var(--font-main);
    font-size: var(--fs-body);
    padding: var(--sp-3);
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    width: 100%;
}

input:focus {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 2px var(--accent-primary-soft);
}

input::placeholder {
    color: var(--muted);
}

/* --- Estado de erro --- */
input.input-error,
input[type="number"].input-error,
input[type="text"].input-error {
    border-color: var(--danger);
    box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.15);
}

input.input-error:focus {
    border-color: var(--danger);
    box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.25);
}

/* --- Estado de sucesso --- */
input.input-success,
input[type="number"].input-success,
input[type="text"].input-success {
    border-color: var(--success);
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.15);
}

input.input-success:focus {
    border-color: var(--success);
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.25);
}

/* --- Estado desabilitado --- */
input:disabled {
    background: var(--bg-inset);
    color: var(--muted);
    cursor: not-allowed;
    opacity: 0.6;
}

/* --- Input de destaque (grande) --- */
.input-display {
    font-size: var(--fs-display);
    font-weight: 700;
    color: var(--accent-primary);
    background: transparent;
    border: none;
    text-align: center;
    padding: var(--sp-2) 0;
}

/* --- Input médio --- */
.input-lg {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent-primary);
    text-align: center;
    background: transparent;
    border: none;
}
```

**⚠️ REGRA DE ESPECIFICIDADE**: No mobile, regras genéricas como `input[type="text"]` podem ter especificidade maior que classes como `.input-display`. Para forçar override, usar:
```css
input.input-display { font-size: var(--fs-display) !important; }
```

### 8.7 Toggle Switch

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
    border-radius: var(--radius-pill);
    transition: 0.3s;
    cursor: pointer;
}

.slider::before {
    content: "";
    position: absolute;
    width: 18px; height: 18px;
    left: 2px; bottom: 2px;
    background: white;
    border-radius: var(--radius-full);
    transition: 0.3s;
}

.switch input:checked + .slider { background: var(--accent-primary); }
.switch input:checked + .slider::before { transform: translateX(20px); }
```

### 8.8 Modal

```css
.modal {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(4px);
    z-index: var(--z-modal);
    justify-content: center;
    align-items: center;
}

.modal.active { display: flex; }

.modal-content {
    width: 100%;
    max-width: 400px;
    padding: var(--sp-8);
    background: var(--bg-panel);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-elevated);
    animation: modalAppear 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes modalAppear {
    from { opacity: 0; transform: translateY(20px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

@media (max-width: 768px) {
    .modal-content {
        max-width: 95vw !important;
        padding: var(--sp-5) !important;
        max-height: 85vh;
        overflow-y: auto;
    }
}
```

### 8.9 Badge

```css
.badge {
    display: inline-flex;
    align-items: center;
    gap: var(--sp-1);
    padding: var(--sp-1) var(--sp-3);
    border-radius: var(--radius-pill);
    font-size: var(--fs-caption);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-primary { background: var(--accent-primary-muted); color: var(--accent-primary); }
.badge-success { background: rgba(16,185,129,0.15); color: var(--success); }
.badge-danger { background: rgba(239,68,68,0.15); color: var(--danger); }
.badge-warning { background: rgba(245,158,11,0.15); color: var(--warning); }
.badge-gold { background: rgba(224,180,87,0.15); color: var(--accent-gold); }
```

### 8.10 Progress Bar

```css
.progress-bar-container {
    height: 12px;
    background: var(--bg-inset);
    border-radius: var(--radius-pill);
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-primary), #818cf8);
    border-radius: var(--radius-pill);
    transition: width 1s ease-out;
}
```

### 8.11 Quick Button (Ação Rápida)

```css
.quick-btn {
    background: var(--accent-primary-soft);
    border: 1px solid var(--glass-border);
    color: var(--accent-primary);
    font-family: var(--font-main);
    font-size: var(--fs-body);
    font-weight: 600;
    padding: var(--sp-1) var(--sp-3);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    width: fit-content;
}

.quick-btn:hover {
    background: var(--accent-primary-muted);
    border-color: var(--accent-primary);
    transform: translateY(-1px);
}
```

### 8.12 Accordion (Cards Colapsáveis)

```css
/* Mobile: cards compactos com expansão */
@media (max-width: 768px) {
    .town-card > .town-head { cursor: pointer; }
    .town-card > .town-tags { display: none !important; }
    .town-card > .town-workshops { display: none !important; }
    .town-card > .town-nodes { display: none !important; }
    .town-card > .town-route { display: none !important; }
    
    .town-card.expanded > .town-tags,
    .town-card.expanded > .town-workshops,
    .town-card.expanded > .town-nodes,
    .town-card.expanded > .town-route {
        display: flex !important;
    }
}
```

### 8.13 Tabela de Dados (Data Table)

```css
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--fs-body-sm);
}

.data-table thead th {
    text-align: left;
    font-size: var(--fs-caption);
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: var(--sp-3) var(--sp-4);
    border-bottom: 1px solid var(--glass-border);
    white-space: nowrap;
}

/* Valores numéricos alinhados à direita */
.data-table thead th.num,
.data-table tbody td.num {
    text-align: right;
    font-family: ui-monospace, 'JetBrains Mono', monospace;
    font-variant-numeric: tabular-nums;
}

.data-table tbody tr {
    border-bottom: 1px solid var(--glass-border);
    transition: background 0.15s;
}

.data-table tbody tr:hover {
    background: var(--bg-panel-hover);
}

.data-table tbody td {
    padding: var(--sp-3) var(--sp-4);
    color: var(--text-main);
    vertical-align: middle;
}

/* Valores positivos/negativos */
.data-table .val-positive { color: var(--success); }
.data-table .val-negative { color: var(--danger); }
.data-table .val-ok { color: var(--ok); }
.data-table .val-bad { color: var(--bad); }

/* Mobile: scroll horizontal */
@media (max-width: 768px) {
    .data-table-wrap {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    .data-table {
        min-width: 600px;  /* Largura mínima para manter legibilidade */
    }
    
    .data-table thead th,
    .data-table tbody td {
        padding: var(--sp-2) var(--sp-3);
        font-size: var(--fs-caption);
    }
}
```

### 8.14 Tooltip

```css
.tooltip-wrap {
    position: relative;
    display: inline-flex;
}

.tooltip-wrap .tooltip {
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg-elevated);
    color: var(--text-main);
    font-size: var(--fs-caption);
    font-weight: 400;
    text-transform: none;
    letter-spacing: 0;
    padding: var(--sp-2) var(--sp-3);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-elevated);
    white-space: nowrap;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.15s, transform 0.15s;
    z-index: var(--z-tooltip);
}

.tooltip-wrap .tooltip::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: var(--bg-elevated);
}

.tooltip-wrap:hover .tooltip,
.tooltip-wrap:focus-within .tooltip {
    opacity: 1;
    transform: translateX(-50%) translateY(-2px);
}

/* Mobile: tooltip embaixo do elemento */
@media (max-width: 768px) {
    .tooltip-wrap .tooltip {
        bottom: auto;
        top: calc(100% + 8px);
    }
    
    .tooltip-wrap .tooltip::after {
        top: auto;
        bottom: 100%;
        border-top-color: transparent;
        border-bottom-color: var(--bg-elevated);
    }
}
```

### 8.15 Tabs de Navegação

```css
.tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid var(--glass-border);
    margin-bottom: var(--sp-4);
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.tab {
    padding: var(--sp-3) var(--sp-4);
    font-size: var(--fs-body-sm);
    font-weight: 500;
    color: var(--muted);
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    transition: color 0.2s, border-color 0.2s;
    white-space: nowrap;
    font-family: var(--font-main);
}

.tab:hover {
    color: var(--text-sec);
}

.tab.active {
    color: var(--accent-primary);
    border-bottom-color: var(--accent-primary);
    font-weight: 600;
}

.tab:disabled {
    color: var(--bg-inset);
    cursor: not-allowed;
}

@media (max-width: 768px) {
    .tabs {
        gap: 0;
        margin-bottom: var(--sp-3);
    }
    
    .tab {
        padding: var(--sp-2) var(--sp-3);
        font-size: var(--fs-caption);
        flex-shrink: 0;
    }
}
```

### 8.16 Empty State

```css
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--sp-10) var(--sp-4);
    text-align: center;
    gap: var(--sp-4);
}

.empty-state-icon {
    width: var(--icon-xl);
    height: var(--icon-xl);
    color: var(--muted);
    opacity: 0.5;
}

.empty-state-title {
    font-size: var(--fs-h3);
    font-weight: 600;
    color: var(--text-sec);
}

.empty-state-desc {
    font-size: var(--fs-body-sm);
    color: var(--muted);
    max-width: 400px;
    line-height: 1.5;
}

.empty-state .btn {
    margin-top: var(--sp-2);
}

@media (max-width: 768px) {
    .empty-state {
        padding: var(--sp-8) var(--sp-4);
    }
    
    .empty-state-icon {
        width: var(--icon-lg);
        height: var(--icon-lg);
    }
    
    .empty-state-title {
        font-size: var(--fs-body);
    }
}
```

### 8.17 Loading / Skeleton State

```css
/* --- Skeleton pulsante --- */
.skeleton {
    background: var(--bg-inset);
    border-radius: var(--radius-md);
    position: relative;
    overflow: hidden;
}

.skeleton::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0.04) 50%,
        transparent 100%
    );
    animation: skeletonShimmer 1.5s infinite;
}

@keyframes skeletonShimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

/* Variantes de tamanho */
.skeleton-text {
    height: 1em;
    width: 100%;
}

.skeleton-text-sm {
    height: 0.75em;
    width: 60%;
}

.skeleton-title {
    height: 1.5em;
    width: 40%;
    margin-bottom: var(--sp-2);
}

.skeleton-circle {
    border-radius: var(--radius-full);
}

.skeleton-card {
    height: 120px;
    border-radius: var(--radius-lg);
}

/* --- Spinner --- */
.spinner {
    width: 24px;
    height: 24px;
    border: 2px solid var(--glass-border);
    border-top-color: var(--accent-primary);
    border-radius: var(--radius-full);
    animation: spin 0.6s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.spinner-sm { width: 16px; height: 16px; }
.spinner-lg { width: 40px; height: 40px; border-width: 3px; }

@media (max-width: 768px) {
    .skeleton-card { height: 80px; }
}
```

---

## 9. Layout e Grid

### Shell (templates/index.html)

```
DESKTOP:
┌─────────┬──────────────────────────┐
│  SIDE   │                          │
│  NAV    │       iframe             │
│  70px   │       (módulo)           │
│         │                          │
└─────────┴──────────────────────────┘

MOBILE:
┌────────────────────────────────────┐
│          iframe (módulo)           │
│          height: calc(100vh-56px)  │
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
        background: rgba(15, 23, 42, 0.98); z-index: var(--z-nav);
    }
    .content-frame { width: 100%; height: calc(100vh - 56px); flex: none; }
}
```

### Grid System

| Contexto | Desktop | Mobile |
|----------|---------|--------|
| Dashboard grid (2 colunas) | `grid-template-columns: 2fr 1fr` | `1fr` |
| Status row (2 cards) | `grid-template-columns: 1fr 1fr` | `1fr` |
| Stat grid (3+ cards) | `repeat(3, 1fr)` | `1fr` |
| Stat grid (4+ cards) | `repeat(4, 1fr)` | `repeat(2, 1fr)` |
| Calendário | `repeat(7, 1fr)` | `repeat(7, 1fr)` (fonte menor) |
| Trade towns | `repeat(auto-fill, minmax(min(340px, 100%), 1fr))` | `1fr` |
| Itens grid | `repeat(3, 1fr)` | `repeat(2, 1fr)` |

### Flex Layouts

| Contexto | Desktop | Mobile |
|----------|---------|--------|
| Status inputs (2 campos) | `flex; gap: var(--sp-4)` | `flex-direction: column` |
| Summary footer | `flex; gap: var(--sp-8); justify-content: center` | `flex-direction: column; align-items: center; gap: var(--sp-2)` |
| Bargain row | `flex` | `flex-direction: column` |
| Header (top-nav) | `flex; justify-content: space-between` | `flex-wrap: wrap; gap: var(--sp-2)` |
| Stat bar | `flex` | `flex-wrap: wrap` |

### Regra de Empilhamento

No mobile, grids com mais de 1 coluna DEVEM empilhar para `1fr`. Exceções: calendário (7 colunas), itens (2 colunas).

---

## 10. Comportamento Responsivo

### Breakpoint Único

```css
@media (max-width: 768px) { /* ... */ }
```

O design é binário: desktop (>768px) e mobile (≤768px).

### Checklist Mobile Completo

Todo módulo DEVE ter estas regras no `@media`:

```css
@media (max-width: 768px) {
    /* 1. RESET de body */
    html { overflow-x: hidden !important; }
    body {
        overflow-y: auto !important;
        overflow-x: hidden !important;
        padding: var(--sp-4) !important;    /* 1rem */
        height: auto !important;
    }
    
    /* 2. RESET de container (se existir .app-container) */
    .app-container {
        padding: var(--sp-4) !important;
        overflow-x: hidden !important;
        width: 100% !important;
        max-width: 100vw !important;
        height: auto !important;
        min-height: auto !important;
    }
    
    /* 3. Empilhar grids */
    .dashboard-grid { grid-template-columns: 1fr !important; }
    .status-row { grid-template-columns: 1fr !important; }
    .stat-grid { grid-template-columns: 1fr !important; }
    
    /* 4. Empilhar flex */
    .status-inputs { flex-direction: column !important; }
    .summary-footer { flex-direction: column !important; align-items: center !important; }
    
    /* 5. Compensar bottom nav (NO FINAL do @media) */
    body { padding-bottom: 70px !important; }
    .app-container { padding-bottom: 70px !important; }
}
```

### Touch Targets

| Elemento | Tamanho Mínimo | WCAG |
|----------|---------------|------|
| Botão primário | 44 × 44px | AAA |
| Botão secundário | 36 × 36px | AA |
| Toggle switch | 42 × 22px | AA |
| Ícone clicável | 40 × 40px | AAA |
| Link em texto | Área de toque 44px | AAA |

### Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| Conteúdo cortado pela bottom nav | Falta `padding-bottom: 70px` | Adicionar no body E no .app-container |
| Fonte não muda no mobile | `input[type="text"]` tem especificidade maior | Usar `input.input-class` (mesma especificidade) |
| Card vaza para a direita | `overflow-x: hidden` não aplicado | Adicionar em body, html e containers |
| Grid não empilha | Seletor errado no media query | Verificar nome exato da classe no HTML |
| Layout quebra | `display: flex` removido no mobile | Só remover se layout não depender dele |
| Body não rola | `height: 100vh` sem override | Usar `height: auto !important` |
| Cache do navegador | Flask servindo template antigo | Adicionar `Cache-Control: no-store` |

---

## 11. Animações e Transições

### Transição Padrão

```css
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
```

### Keyframes

```css
@keyframes modalAppear {
    from { opacity: 0; transform: translateY(20px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes skeletonShimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
```

### Hover Effects

```css
/* Card hover */
.card:hover {
    border-color: var(--accent-primary);
    background: var(--bg-panel-hover);
}

/* Botão hover */
.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px var(--accent-glow);
}

/* Botão active */
.btn:active { transform: scale(0.97); transition-duration: 0.1s; }

/* Item de lista hover */
.list-item:hover {
    transform: translateX(4px);
    border-color: var(--accent-primary);
}
```

### Reduced Motion

Usuários que preferem reduzir movimento devem ter todas as transições e animações desativadas ou minimizadas:

```css
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
    
    .btn:hover { transform: none; }
    .btn:active { transform: none; }
    .list-item:hover { transform: none; }
    .tooltip-wrap:hover .tooltip { transform: translateX(-50%); }
    .progress-bar-fill { transition: none; }
}
```

> **Regra**: Todo `transition` e `animation` no sistema deve ser desativado por esta regra. Não usar `transition: none` individualmente — a regra global cobre todos os casos.

### JavaScript — Animações Sutis

```javascript
// Fade in ao carregar
function fadeIn(el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(10px)';
    requestAnimationFrame(() => {
        el.style.transition = 'opacity 0.3s, transform 0.3s';
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
    });
}

// Counter animado
function animateValue(el, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + range * eased).toLocaleString('pt-BR');
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// Debounce para resize
function debounce(fn, ms = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), ms);
    };
}
```

---

## 12. Temas (Dark/Light)

### Estrutura

O sistema é dark-first. Para suportar light theme, usar `data-theme` no `<html>`:

```css
:root {
    /* Dark (padrão) — todos os tokens aqui */
    --bg-base: #0f172a;
    --bg-panel: #1e293b;
    /* ... */
}

[data-theme="light"] {
    --bg-base: #f8fafc;
    --bg-panel: #ffffff;
    --bg-input: #f1f5f9;
    --text-main: #0f172a;
    --text-sec: #475569;
    --muted: #94a3b8;
    --glass-border: #e2e8f0;
    --accent-primary: #0284c7;
    --accent-glow: rgba(2, 132, 199, 0.3);
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

- Inputs usam `background: var(--bg-input)` (herda do token, não hardcoded).
- Sombras mais leves.
- Bordas mais suaves (`--glass-border: #e2e8f0`).
- Acento azul mais escuro (`#0284c7` em vez de `#38bdf8`).
- Gradiente do H1: `#0f172a` → `#0284c7`.

---

## 13. Acessibilidade

### Contrast Ratios (WCAG AA)

| Combinação | Ratio | Status |
|------------|-------|--------|
| `--text-main` sobre `--bg-base` | 14.5:1 | ✅ AAA |
| `--text-sec` sobre `--bg-base` | 8.2:1 | ✅ AAA |
| `--muted` sobre `--bg-base` | 4.6:1 | ✅ AA |
| `--accent-primary` sobre `--bg-base` | 5.8:1 | ✅ AA |
| `--text-on-accent` sobre `--accent-primary` | 7.2:1 | ✅ AAA |
| `--text-on-danger` sobre `--danger` | 4.8:1 | ✅ AA |

### Focus Rings

```css
:focus-visible {
    outline: 2px solid var(--info);
    outline-offset: 2px;
}
```

### Screen Reader

- Usar `aria-label` em botões sem texto visível.
- Usar `aria-expanded` em accordions.
- Usar `role="dialog"` em modais.
- Usar `aria-live="polite"` para atualizações dinâmicas.

### Keyboard Navigation

- Tab deve percorrer todos os elementos interativos.
- Escape deve fechar modais.
- Enter/Space deve ativar botões.

---

## 14. Padrões por Módulo

### Dashboard (`/dashboard/`)

- **Layout**: 2 colunas (2fr 1fr) → 1 coluna no mobile.
- **Stats**: 4 cards em row → 2x2 no mobile.
- **Calendário**: Grid 7 colunas (mantém no mobile, fonte reduzida para 0.6rem).
- **CSS externo**: `static/css/dashboard.css`.

```html
<div class="app-container">
  <header class="top-nav">
    <h1>Dashboard</h1>
    <div class="nav-info">...</div>
  </header>
  <div class="stat-grid">           <!-- 4 stat-cards -->
    <div class="stat-card">...</div>
    <div class="stat-card">...</div>
    <div class="stat-card">...</div>
    <div class="stat-card">...</div>
  </div>
  <main class="dashboard-grid">     <!-- 2fr 1fr → 1fr -->
    <div class="glass-panel calendar">...</div>
    <div class="glass-panel tasks">...</div>
  </main>
</div>
```

### Bartering (`/bartering/`)

- **Layout**: Stat grid (3 cards) + Dashboard grid (2fr 1fr) → empilha tudo.
- **Componentes**: Routes grid (2 colunas → 1), Exp calculator, Modal de tabela.
- **Referência**: Este módulo tem o mobile mais bem resolvido.

```html
<div class="app-container">
  <header class="top-nav">
    <h1>Bartering</h1>
    <div class="nav-info">...</div>
  </header>
  <div class="stat-grid">           <!-- 3 stat-cards -->
    <div class="stat-card">...</div>
    <div class="stat-card">...</div>
    <div class="stat-card">...</div>
  </div>
  <main class="dashboard-grid">     <!-- 2fr 1fr → 1fr -->
    <div class="glass-panel routes-grid">
      <div class="route-item">...</div>
      <div class="route-item">...</div>
    </div>
    <div class="glass-panel barganha">
      <input class="input-display" />
      <div class="rem-row">...</div>
    </div>
  </main>
  <div class="glass-panel exp-calc">...</div>
</div>
```

### Hunting (`/hunting/`)

- **Layout**: Flex column com cards empilhados.
- **Calendar page**: Página separada com grid auto-fit.
- **CSS separado**: Usa `static/css/style.css` externo.

```html
<div class="app-container">
  <header class="top-nav">
    <h1>Hunting</h1>
    <div class="nav-info">...</div>
  </header>
  <main class="dashboard-grid">     <!-- flex column, cards empilhados -->
    <div class="glass-panel hunt-info">...</div>
    <div class="glass-panel hunt-exp">
      <div class="progress-bar-container">...</div>
    </div>
  </main>
</div>
```

### CP (`/cp/`)

- **Layout**: 3 colunas (350px 1fr 350px) → 1 coluna no mobile.
- **Status row**: 2 cards lado a lado → empilha.
- **OCR**: Paste zone com drag & drop.

```html
<div class="app-container">
  <header class="top-nav">
    <h1>Contribution Points</h1>
    <div class="nav-info">...</div>
  </header>
  <main class="dashboard-grid">     <!-- 3 colunas → 1 -->
    <div class="glass-panel status-inputs">
      <input class="input-lg" />
      <input class="input-lg" />
    </div>
    <div class="glass-panel lifeskills-panel">
      <div class="prof-card">...</div>
      <div class="subprodutos-grid">...</div>
    </div>
    <div class="glass-panel summary-footer">
      <div class="status-row">...</div>
    </div>
  </main>
</div>
```

### Market (`/market/`)

- **Layout**: Flex column com lista + detalhe.
- **Grids**: Auto-fill com minmax.
- **Cores extras**: `--accent-gold`, `--ok`, `--bad`.

```html
<div class="app-container">
  <header class="top-nav">
    <h1>Market</h1>
    <input class="search-input" type="search" />
  </header>
  <main class="dashboard-grid">     <!-- flex column -->
    <div class="glass-panel items-grid">
      <div class="item-card">...</div>
      <div class="item-card">...</div>
    </div>
    <div class="glass-panel detail-panel">
      <div class="chart-flex">...</div>
    </div>
  </main>
</div>
```

### Trade (`/trade/`)

- **Layout**: Stat bar + Toolbar + Town grid.
- **Body é flex column**: NÃO mudar display no mobile.
- **Accordion**: Cards colapsados por padrão no mobile.
- **Grid towns**: `repeat(auto-fill, minmax(min(340px, 100%), 1fr))` → `1fr`.

```html
<body class="dark-theme">    <!-- flex column, NÃO mudar no mobile -->
  <header class="top-nav">
    <h1>Trade</h1>
    <div class="toolbar">...</div>
  </header>
  <div class="stat-bar">     <!-- flex, wrap no mobile -->
    <div class="stat-item">...</div>
    <div class="stat-item">...</div>
    <div class="stat-item">...</div>
    <div class="stat-item">...</div>
    <div class="stat-item">...</div>
  </div>
  <div class="towns-scroll">
    <div class="town-grid">  <!-- auto-fill 340px → 1fr -->
      <div class="town-card">
        <div class="town-head">...</div>
        <div class="town-tags">...</div>
        <div class="town-workshops">...</div>
        <div class="town-nodes">...</div>
        <div class="town-route">...</div>
      </div>
    </div>
  </div>
</body>
```

---

## 15. Guia de Iteração

### Para Criar um Novo Componente

1. **Definir o tokens necessários** — Quais cores, espaçamentos, fontes o componente usa? Referenciar tokens existentes.
2. **Especificar dimensões exatas** — Altura, padding, gap, border-radius. Usar tokens `--sp-*`, `--radius-*`, `--fs-*`.
3. **Definir estados** — Default, hover, active, disabled, focus. Cada estado é uma variante separada.
4. **Definir variantes** — primary, secondary, ghost, danger. Cada variante é uma entrada separada no CSS.
5. **Documentar responsividade** — Como o componente se adapta no mobile. Usar `@media (max-width: 768px)`.
6. **Verificar acessibilidade** — Focus ring, contrast ratio, touch target size, aria attributes.

### Para Modificar um Componente Existente

1. **Localizar o componente** nesta referência.
2. **Verificar se a mudança afeta outros módulos** — componentes são compartilhados.
3. **Aplicar a mudança usando tokens** — nunca hardcoded values.
4. **Testar no mobile E no desktop** — sempre ambos.
5. **Verificar especificidade CSS** — regras genéricas (`input[type="text"]`) podem ter especificidade maior que classes.

### Regras de Especificidade

```
Classe simples:         .my-class          (0,1,0)
Classe + estado:        .my-class:hover    (0,2,0)
Elemento + classe:      input.my-class     (0,1,1)
Elemento + atributo:    input[type="text"] (0,1,1)
Media query:            @media (...)       (não afeta especificidade)
!important:             força prioridade   (usar com cautela)
```

**Regra de ouro**: Se `input[type="text"]` e `.my-class` têm a mesma especificidade (0,1,1), a que aparece DEPOIS no CSS vence. Posicionar classes específicas DEPOIS de regras genéricas.

---

## 16. Do's and Don'ts

### Cores
- ✅ Usar tokens `var(--*)` para todas as cores.
- ✅ Usar `--accent-primary` para ações principais.
- ✅ Usar `--accent-gold` apenas para contextos monetários.
- ✅ Usar `--ok`/`--bad` para status suaves, `--success`/`--danger` para status fortes.
- ❌ Nunca usar hex hardcoded em componentes.
- ❌ Nunca usar verde/vermelho como fundo de card.
- ❌ Nunca usar acento azul em texto corrido.

### Tipografia
- ✅ Seguir a escala `--fs-*` do sistema.
- ✅ Usar `font-weight: 700` apenas para números e headings.
- ✅ Usar `text-transform: uppercase` em labels.
- ❌ Nunca usar font-size fora da escala.
- ❌ Nunca usar font-weight 700 em body text.

### Espaçamento
- ✅ Usar tokens `--sp-*` para todos os espaçamentos.
- ✅ Manter gaps uniformes entre cards do mesmo grid.
- ✅ Usar `padding-bottom: 70px` no mobile para compensar bottom nav.
- ❌ Nunca usar valores hardcoded de padding/margin.
- ❌ Nunca pular níveis da escala (ex: ir de --sp-2 para --sp-8).

### Componentes
- ✅ Usar componentes documentados nesta referência.
- ✅ Adicionar hover/active states em todos os elementos interativos.
- ✅ Usar `transition: all 0.2s` em todos os elementos interativos.
- ✅ Usar `:disabled` em botões e inputs quando aplicável.
- ❌ Nunca inventar um componente que já existe.
- ❌ Nunca usar `!important` sem justificativa.
- ❌ Nunca mudar display:flex no mobile se layout depender dele.

### Responsividade
- ✅ Testar sempre no mobile E no desktop.
- ✅ Usar `overflow-x: hidden` em body e containers.
- ✅ Usar `height: auto` no mobile (nunca 100vh).
- ❌ Nunca assumir que "funciona no desktop, funciona no mobile".
- ❌ Nunca usar `display: block` para resetar `display: flex` sem verificar o layout.

---

## 17. Gaps Conhecidos

- **Dark/Light toggle persistente**: O toggle salva em localStorage mas não sincroniza entre abas.
- **Print styles**: Não há regras para impressão.
- **RTL support**: Não há suporte para layout da direita para esquerda.
- **High contrast mode**: Não há regras para `prefers-contrast: high`.
- **Animações complexas**: Page transitions, scroll-triggered animations e parallax não estão cobertas (apenas transições básicas e hover).

---

## 18. Template Base

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BDOHub — Module Name</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        :root {
            /* === Superfícies === */
            --bg-base: #0f172a;
            --bg-panel: #1e293b;
            --bg-panel-hover: #253349;
            --bg-input: #0b1220;
            --bg-elevated: #334155;
            --bg-inset: #0a1020;

            /* === Bordas === */
            --glass-border: #334155;
            --glass-border-hover: #475569;
            --border-strong: #64748b;

            /* === Texto === */
            --text-main: #f8fafc;
            --text-sec: #cbd5e1;
            --muted: #64748b;
            --text-on-accent: #0f172a;
            --text-on-danger: #ffffff;

            /* === Acento === */
            --accent-primary: #38bdf8;
            --accent-primary-hover: #0ea5e9;
            --accent-primary-muted: rgba(56,189,248,0.15);
            --accent-primary-soft: rgba(56,189,248,0.08);
            --accent-gold: #e0b457;

            /* === Status === */
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --info: #3b82f6;
            --ok: #22c55e;
            --bad: #f87171;

            /* === Tipografia === */
            --fs-display: 2.5rem;
            --fs-h1: 1.8rem;
            --fs-h2: 1.2rem;
            --fs-h3: 1rem;
            --fs-body: 0.9rem;
            --fs-body-sm: 0.8rem;
            --fs-caption: 0.75rem;
            --fs-micro: 0.65rem;

            /* === Espaçamento === */
            --sp-1: 0.25rem;
            --sp-2: 0.5rem;
            --sp-3: 0.75rem;
            --sp-4: 1rem;
            --sp-5: 1.25rem;
            --sp-6: 1.5rem;
            --sp-8: 2rem;
            --sp-10: 2.5rem;

            /* === Formas === */
            --radius-xs: 4px;
            --radius-sm: 6px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --radius-xl: 16px;
            --radius-pill: 9999px;
            --radius-full: 50%;

            /* === Sombras === */
            --shadow-card: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            --shadow-elevated: 0 10px 15px -3px rgba(0,0,0,0.2), 0 4px 6px -2px rgba(0,0,0,0.1);
            --shadow-glow: 0 4px 15px rgba(56,189,248,0.5);

            /* === Componentes === */
            --comp-btn-height: 44px;

            /* === Ícones === */
            --icon-sm: 16px;
            --icon-md: 20px;
            --icon-lg: 24px;
            --icon-xl: 40px;

            /* === Z-Index === */
            --z-base: 0;
            --z-dropdown: 100;
            --z-sticky: 200;
            --z-nav: 500;
            --z-modal: 1000;
            --z-toast: 1100;
            --z-tooltip: 1200;

            /* === Fonte === */
            --font-main: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-base);
            color: var(--text-main);
            font-family: var(--font-main);
            font-size: var(--fs-body);
            line-height: 1.6;
            overflow: hidden;
            height: 100vh;
        }

        .app-container {
            max-width: 1700px;
            margin: 0 auto;
            padding: var(--sp-8);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }

        h1 {
            font-size: var(--fs-h1);
            font-weight: 700;
            background: linear-gradient(90deg, #fff, var(--accent-primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--sp-8);
            padding-bottom: var(--sp-4);
            border-bottom: 1px solid var(--glass-border);
        }

        .glass-panel {
            background: var(--bg-panel);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: var(--sp-5);
            box-shadow: var(--shadow-card);
        }

        .section-title {
            display: flex;
            align-items: center;
            gap: var(--sp-2);
            font-size: var(--fs-h2);
            font-weight: 500;
            color: var(--text-sec);
            border-bottom: 1px solid var(--glass-border);
            padding-bottom: var(--sp-2);
            margin-bottom: var(--sp-4);
        }

        .section-title svg {
            color: var(--accent-primary);
            width: var(--icon-md);
            height: var(--icon-md);
        }

        /* ===== MOBILE ===== */
        @media (max-width: 768px) {
            html { overflow-x: hidden !important; }
            body {
                overflow-y: auto !important;
                overflow-x: hidden !important;
                padding: var(--sp-4) !important;
                height: auto !important;
            }
            .app-container {
                padding: var(--sp-4) !important;
                overflow-x: hidden !important;
                width: 100% !important;
                max-width: 100vw !important;
                height: auto !important;
                min-height: auto !important;
            }
            .top-nav {
                margin-bottom: var(--sp-4) !important;
                padding-bottom: var(--sp-2) !important;
                flex-wrap: wrap !important;
                gap: var(--sp-2) !important;
            }
            h1 { font-size: 1.3rem !important; }
            .glass-panel { padding: var(--sp-4) !important; }
            .section-title { font-size: 1rem !important; margin-bottom: var(--sp-4) !important; }

            /* Compensar bottom nav bar (56px) */
            body { padding-bottom: 70px !important; }
            .app-container { padding-bottom: 70px !important; }
        }

        /* ===== REDUCED MOTION ===== */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
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
            <div class="nav-info">Description</div>
        </header>

        <main class="dashboard-grid">
            <!-- Module content -->
        </main>
    </div>

    <script>lucide.createIcons();</script>
</body>
</html>
```

---

> **Este documento é a referência.** Qualquer alteração visual no BDOHub deve começar aqui. Se algo não está documentado, documente antes de implementar. Quando criar novos componentes, seguir o [Guia de Iteração](#15-guia-de-iteração). Quando em dúvida, consultar [Do's and Don'ts](#16-dos-and-donts).
