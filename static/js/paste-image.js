/**
 * PasteImage — utilitário reutilizável do hub: "colar imagem da área de transferência".
 *
 * Padrão documentado (web.dev "How to paste files"; MDN "paste event"):
 * um listener global do evento `paste` inspeciona `clipboardData.items` e,
 * quando encontra um arquivo de imagem, entrega-o via `getAsFile()` ao
 * handler registrado. É o mesmo mecanismo usado por buscadores de imagem
 * (ex.: Yandex) e funciona em Chrome/Edge/Firefox (incl. Zen) no Windows
 * 10/11 — sem permissões especiais e sem diálogo de arquivo.
 *
 * Colagens de texto não são afetadas: o listener só reage quando a área de
 * transferência contém uma imagem.
 *
 * API:
 *   PasteImage.attach('id', { onImage(file), onHint(text), active })
 *   PasteImage.activate('id')   // o próximo Ctrl+V vai para este handler
 *   PasteImage.detach('id')
 *
 * Exemplo:
 *   PasteImage.attach('profissoes', {
 *       active: true,                 // alvo padrão do Ctrl+V
 *       onImage: (file) => uploadOcrImage(file),
 *       onHint:  (texto) => mostrarStatus(texto),
 *   });
 */
(function (global) {
    'use strict';

    const handlers = new Map(); // id -> { onImage, onHint, active }
    let listenerAttached = false;

    /** Retorna o primeiro arquivo de imagem da área de transferência, ou null. */
    function firstImageFrom(clipboardData) {
        if (!clipboardData || !clipboardData.items) return null;
        for (const item of clipboardData.items) {
            if (item.kind === 'file' && item.type && item.type.indexOf('image/') === 0) {
                const file = item.getAsFile ? item.getAsFile() : null;
                if (file) return file;
            }
        }
        return null;
    }

    function onPaste(event) {
        const file = firstImageFrom(event.clipboardData);
        if (!file) return; // sem imagem: deixa o navegador tratar normalmente

        const active = [...handlers.values()].find((h) => h.active);
        const target = active || [...handlers.values()][handlers.size - 1];
        if (!target) return;

        event.preventDefault();
        if (target.onHint) target.onHint('Imagem colada — processando...');
        target.onImage(file);
    }

    global.PasteImage = {
        attach(id, options) {
            handlers.set(id, {
                onImage: options.onImage,
                onHint: options.onHint || null,
                active: !!options.active,
            });
            if (!listenerAttached) {
                document.addEventListener('paste', onPaste);
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
