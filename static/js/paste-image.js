/**
 * PasteImage — utilitário reutilizável do hub: "colar imagem da área de transferência".
 *
 * Padrão documentado (web.dev "How to paste files"; MDN "paste event"):
 * um listener global do evento `paste` inspeciona a área de transferência e,
 * quando encontra uma imagem, entrega-a ao handler registrado. É o mesmo
 * mecanismo usado por buscadores de imagem (ex.: Yandex) e funciona em
 * Chrome/Edge/Firefox (incl. Zen) no Windows 10/11 — sem permissões
 * especiais e sem diálogo de arquivo.
 *
 * Robustez cross-browser:
 *  - O Firefox (e o Zen, que é baseado nele) nem sempre popula
 *    `clipboardData.items` em eventos de paste no Windows 10. Por isso o
 *    arquivo é procurado primeiro em `clipboardData.files` e depois em
 *    `clipboardData.items` + `getAsFile()` — cobre Chrome, Edge e Firefox.
 *  - O listener é registrado no `window` em fase de captura, então chega
 *    mesmo que algum elemento da página interrompa a propagação.
 *
 * Colagens de texto não são afetadas: o listener só reage quando há imagem
 * (ou um arquivo que não é imagem — nesse caso chama `onNoImage`, para a
 * interface poder orientar o usuário).
 *
 * API:
 *   PasteImage.attach('id', {
 *       onImage(file),          // obrigatório — recebe a imagem colada
 *       onHint(text),           // opcional — chamado ao detectar a imagem
 *       onNoImage(),            // opcional — havia arquivo, mas não era imagem
 *       active,                 // true = alvo padrão do Ctrl+V
 *   })
 *   PasteImage.activate('id')   // o próximo Ctrl+V vai para este handler
 *   PasteImage.detach('id')
 *
 * Exemplo:
 *   PasteImage.attach('profissoes', {
 *       active: true,
 *       onImage: (file) => uploadOcrImage(file),
 *       onHint:  () => flashPasteZone(zoneEl),
 *   });
 */
(function (global) {
    'use strict';

    const handlers = new Map(); // id -> { onImage, onHint, onNoImage, active }
    let listenerAttached = false;

    /** Retorna o primeiro arquivo de imagem da área de transferência, ou null. */
    function firstImageFrom(clipboardData) {
        if (!clipboardData) return null;

        // 1º: `files` — é o que o Firefox/Zen realmente popula no paste
        if (clipboardData.files) {
            for (const file of clipboardData.files) {
                if (file.type && file.type.indexOf('image/') === 0) return file;
            }
        }

        // 2º: `items` + getAsFile() — caminho clássico do Chrome/Edge
        if (clipboardData.items) {
            for (const item of clipboardData.items) {
                if (item.kind === 'file' && item.type && item.type.indexOf('image/') === 0) {
                    const file = item.getAsFile ? item.getAsFile() : null;
                    if (file) return file;
                }
            }
        }

        return null;
    }

    /** Havia algum arquivo (qualquer tipo) na área de transferência? */
    function hasAnyFile(clipboardData) {
        if (!clipboardData) return false;
        if (clipboardData.files && clipboardData.files.length) return true;
        if (clipboardData.items) {
            for (const item of clipboardData.items) {
                if (item.kind === 'file') return true;
            }
        }
        return false;
    }

    function onPaste(event) {
        const clipboardData = event.clipboardData;
        const file = firstImageFrom(clipboardData);

        const active = [...handlers.values()].find((h) => h.active);
        const target = active || [...handlers.values()][handlers.size - 1];
        if (!target) return;

        if (!file) {
            // Só avisa quando havia um arquivo que não era imagem —
            // colagens de texto comum seguem normais, sem ruído.
            if (hasAnyFile(clipboardData)) {
                event.preventDefault();
                if (target.onNoImage) target.onNoImage();
            }
            return;
        }

        event.preventDefault();
        if (target.onHint) target.onHint('Imagem colada — processando...');
        target.onImage(file);
    }

    global.PasteImage = {
        attach(id, options) {
            handlers.set(id, {
                onImage: options.onImage,
                onHint: options.onHint || null,
                onNoImage: options.onNoImage || null,
                active: !!options.active,
            });
            if (!listenerAttached) {
                // captura no window: pega o evento mesmo se algo parar a propagação
                window.addEventListener('paste', onPaste, true);
                listenerAttached = true;
            }
        },
        activate(id) {
            for (const [key, handler] of handlers) {
                handler.active = (key === id);
            }
        },
        detach(id) {
            handlers.delete(id);
        },
    };
})(window);
