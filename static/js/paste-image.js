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
 * Captura sob demanda (arm/disarm):
 *   O Ctrl+V SÓ é interceptado enquanto um alvo estiver "armado" — por
 *   exemplo, enquanto um modal de colagem dedicado está aberto. Com nada
 *   armado, o listener não interfere no comportamento normal do navegador
 *   (colar texto em inputs, etc.). Assim, cada área da página decide quando
 *   quer receber o print, sem conflito entre elas.
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
 *   })
 *   PasteImage.arm('id')        // passa a interceptar o Ctrl+V para este handler
 *   PasteImage.disarm()         // para de interceptar
 *   PasteImage.isArmed('id')
 *   PasteImage.detach('id')
 *
 * Exemplo (modal de colagem):
 *   PasteImage.attach('profissoes', { onImage: (f) => uploadOcrImage(f) });
 *   // ao abrir o modal:
 *   PasteImage.arm('profissoes');
 *   // ao fechar o modal:
 *   PasteImage.disarm();
 */
(function (global) {
    'use strict';

    const handlers = new Map(); // id -> { onImage, onHint, onNoImage }
    let armedId = null;         // id do alvo que está interceptando o Ctrl+V
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
        // Sem alvo armado: deixa o navegador tratar o paste normalmente.
        const target = armedId ? handlers.get(armedId) : null;
        if (!target) return;

        const clipboardData = event.clipboardData;
        const file = firstImageFrom(clipboardData);

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
            });
            if (!listenerAttached) {
                // captura no window: pega o evento mesmo se algo parar a propagação
                window.addEventListener('paste', onPaste, true);
                listenerAttached = true;
            }
        },
        arm(id) {
            armedId = handlers.has(id) ? id : null;
        },
        disarm() {
            armedId = null;
        },
        isArmed(id) {
            return armedId === id;
        },
        detach(id) {
            handlers.delete(id);
            if (armedId === id) armedId = null;
        },
    };
})(window);
