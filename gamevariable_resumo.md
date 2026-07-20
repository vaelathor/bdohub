# Resumo Executivo - gamevariable.xml

## O que é?

O `gamevariable.xml` é o **arquivo de configuração principal** do Black Desert Online que armazena **todas as preferências e dados do jogador** localmente no computador.

---

## Localização

```
C:\Users\[Usuario]\Documents\Black Desert\UserCache\[ID_PERSONAGEM]\gamevariable.xml
```

**Exemplo:**
```
C:\Users\Lúcio\Documents\Black Desert\UserCache\1006413\gamevariable.xml
```

---

## Características

- **Formato:** XML (texto legível)
- **Tamanho:** ~3.9 MB (71.400 linhas)
- **Encoding:** UTF-8 com CRLF
- **Versionamento:** Cada seção tem controle de versão

---

## Principais Categorias de Dados

### 🎮 1. Configurações de Jogo
- Modo de mouse e sensibilidade
- Câmera automática
- Guias e tutoriais
- Otimização de performance
- Recusas (PvP, trocas, guild)

### 🖥️ 2. Configurações Gráficas
- Resolução e modo de janela
- Qualidade gráfica (Low/Medium/High)
- Anti-aliasing, SSAO, Tessellation
- Efeitos visuais e pós-processamento
- FOV, gamma, contraste

### 🔊 3. Configurações de Áudio
- Volume master e individuais
- Música, efeitos, vozes
- Sons de ambiente e batalha
- Voice chat (microfone e alto-falante)

### 💬 4. Interface e Chat
- 5 janelas de chat configuráveis
- Filtros de canais (Guild, Party, World, etc.)
- Macros personalizadas (10 slots)
- Posicionamento de elementos UI
- Nametags e barras de HP

### 🐾 5. Pets
- **113 pets registrados** no total
- 5-6 pets ativos simultaneamente
- 5 grupos de pets configuráveis
- Configurações: Follow, Find, GetItem
- Ordem de preferência

### 🎯 6. Interface Gráfica (UI)
- Posição de todos os elementos (minimapa, quests, buffs, etc.)
- Slots rápidos (quickslots)
- Painéis e janelas
- 3 presets personalizados + 1 padrão

### 📝 7. Outros Dados
- Memos e anotações
- Bookmarks de mapa
- Histórico de alquimia
- Workers e produção
- Skills e cooldowns
- Quests
- Itens travados no inventário

---

## Dados Específicos do Seu Personagem (ID: 1006413)

### Macros de Guild Configuradas:
1. "!Buff de vida em 1 minuto"
2. "!Soltando buff de vida"
3. "!Buff de obtenção em 1 minuto"
4. "!Soltando buff de obtenção"

### Configurações Gráficas:
- **Resolução:** 1920x1080
- **Modo:** Fullscreen Windowed
- **Qualidade:** Low1
- **Anti-aliasing:** Ativado (Index 1)
- **SSAO:** Ativado
- **Tessellation:** Desativado
- **FOV:** 70°
- **Filtro de Câmera:** OldStyle

### Configurações de Áudio:
- **Volume Master:** 5.5
- **Música:** Ativada (Volume 100)
- **Efeitos:** Volume 100
- **Fairy:** Volume 50
- **Música de Sequência:** Desativada

### Pets Ativos (5):
1. Pet #10000000003733649
2. Pet #10000000003892213
3. Pet #10000000004075504
4. Pet #10000000005066661
5. Pet #10000000005067390

Todos configurados com: Follow=true, Find=true, GetItem=true

### Nametags:
- **Próprio jogador:** Não mostrar
- **HP próprio:** Mostrar importantes
- **Outros jogadores:** Sempre mostrar
- **Monstros:** Sempre mostrar (nome e HP)
- **Party/Guild:** Sempre mostrar
- **Pets/Fairy/Maid:** Sempre mostrar

### Memo Salvo:
```
"Missão aberta em Mediah 2 (restrição de fechamento 20:20h)"
Criado em: 09/03/2024 10:32
```

---

## Estrutura de IDs

### IDs de Pets
- **Formato:** 17-19 dígitos numéricos
- **Exemplo:** 10000000003733649
- **Range:** 10000000003719811 até 10000000005126944

### IDs de Personagens
- **Formato:** Numérico de 7 dígitos
- **Exemplo:** 1006413
- **Outros encontrados:** 1464546, 1489991, 1490736, 1622082, 1622329, 1622355

### IDs de Grupos de Pets
- **Formato:** 10 dígitos
- **Exemplo:** 1878994928, 1879986814

---

## Seções Vazias (Não Utilizadas)

Estas seções existem mas não têm dados configurados:
- `CheckQuestList`
- `QuestSortType`
- `QuickSlotData`
- `ShortcutKey`
- `EquipSlotFlag`
- `BlockList` (vazio neste personagem)
- `SkillCommandLock`
- `SkillCoolTimeSlot`
- `ItemLockedInInventory`
- `QuestOption`

---

## Timestamps Importantes

Datas registradas no arquivo:

| Data | Descrição |
|------|-----------|
| 2023-02-01 | Primeiro registro (Index 187) |
| 2023-06-20 | Evento registrado (Index 18) |
| 2024-02-09 | Atividade (Index 133) |
| 2024-05-16 | Atividade (Index 16) |
| 2024-06-25 | Atividade (Index 146) |
| 2026-04-15 | Última atividade (Index 111, 218) |
| 2026-04-19 | Última sessão (Index 208) |

---

## Valores Numéricos Interessantes

Alguns valores armazenados (significado desconhecido sem documentação oficial):

```
Index 153: 791.000000
Index 154: 735.000000
Index 155: 54003.000000
Index 156: 320190.000000 (possivelmente moeda/recursos)
Index 157: 6501.000000
Index 177: 283.399872
```

---

## Configurações de Otimização

```xml
AutoOptimization: true
AutoOptimizationFrameLimit: 60 FPS
useCharacterDistUpdate: true
farPlayerOptimizationLimitDist: 1000 metros
useFarPlayerOptimization: false
useOtherPlayerUpdate: false
```

---

## Filtros de Chat Ativos

| Filtro | Status |
|--------|--------|
| 0 - Geral | ✅ Ativo |
| 1 - Sistema | ✅ Ativo |
| 2 - Combate | ✅ Ativo |
| 3 - ? | ❌ Desativado |
| 4 - Itens | ✅ Ativo |
| 9 - ? | ❌ Desativado |
| 11 - ? | ❌ Desativado |
| 14 - ? | ❌ Desativado |
| 15 - ? | ❌ Desativado |

---

## Renderização de Cores de Jogadores

| Tipo | Ativo |
|------|-------|
| Guild | ✅ Sim |
| Party | ✅ Sim |
| Enemy | ✅ Sim |
| ZoneChange | ❌ Não |
| WarAlly | ❌ Não |
| NonWarPlayer | ❌ Não |
| ShadowArenaAlly | ✅ Sim |
| ShadowArenaEnemy | ✅ Sim |

---

## Presets de UI

O arquivo contém 4 configurações de UI salvas:

1. **UISettingPreset0** - Preset personalizado 1
2. **UISettingPreset1** - Preset personalizado 2 (vazio)
3. **UISettingPreset2** - Preset personalizado 3 (vazio)
4. **UISettingRevert** - Configuração padrão do jogo

---

## Possibilidades de Uso

### ✅ Leitura de Dados
- Extrair lista de pets
- Ler configurações gráficas
- Analisar macros
- Ver posições de UI
- Verificar timestamps de atividade

### ✅ Modificação Segura
- Alterar macros de chat
- Ajustar volumes
- Modificar posições de UI
- Trocar presets gráficos
- Adicionar/remover memos

### ⚠️ Modificação com Cuidado
- Alterar IDs de pets (pode causar problemas)
- Modificar estrutura de grupos
- Mudar configurações de otimização
- Editar valores numéricos desconhecidos

### ❌ Não Recomendado
- Criar IDs falsos de pets
- Modificar timestamps arbitrariamente
- Alterar estrutura XML
- Adicionar seções não documentadas

---

## Backup e Restauração

### Como fazer backup:
```bash
# Copiar arquivo
cp "C:\Users\Lúcio\Documents\Black Desert\UserCache\1006413\gamevariable.xml" backup_gamevariable.xml

# Ou copiar pasta inteira
cp -r "C:\Users\Lúcio\Documents\Black Desert\UserCache\1006413" backup_personagem/
```

### Como restaurar:
1. Fechar o jogo completamente
2. Substituir o arquivo gamevariable.xml
3. Iniciar o jogo

---

## Sincronização entre Personagens

Para copiar configurações de um personagem para outro:

```bash
# Copiar de 1006413 para 1464546
cp "C:\Users\Lúcio\Documents\Black Desert\UserCache\1006413\gamevariable.xml" \
   "C:\Users\Lúcio\Documents\Black Desert\UserCache\1464546\gamevariable.xml"
```

**⚠️ Atenção:** Isso copiará TODAS as configurações, incluindo pets e UI.

---

## Arquivos Relacionados

Na mesma pasta do gamevariable.xml:

| Arquivo | Descrição |
|---------|-----------|
| `ColorPalette.uc` | Paleta de cores (binário) |
| `itemMarketFavoritesList.cache` | Favoritos do mercado |
| `worker.cache` | Cache de workers (binário) |

---

## Conclusão

O `gamevariable.xml` é um arquivo **completo e complexo** que armazena praticamente todas as preferências do jogador. É **seguro para leitura** e pode ser **modificado com cuidado** para personalização avançada ou backup de configurações.

**Recomendação:** Sempre faça backup antes de modificar!

---

**Documento gerado em:** 2026-05-06
**Personagem analisado:** ID 1006413
**Arquivo fonte:** gamevariable.xml (71.400 linhas)
