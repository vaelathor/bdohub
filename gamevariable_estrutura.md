# Estrutura do gamevariable.xml - Black Desert Online

## Visão Geral
O arquivo `gamevariable.xml` é o principal arquivo de configuração do Black Desert Online, contendo todas as preferências do jogador, configurações de UI, dados de pets, macros, e muito mais.

**Localização:** `C:\Users\Lúcio\Documents\Black Desert\UserCache\[ID_PERSONAGEM]\gamevariable.xml`

**Tamanho:** ~71.400 linhas (3.9 MB)

---

## 1. MACROS DE CHAT (ChattingMacro)

Macros personalizadas para mensagens rápidas no chat:

```xml
<ChattingMacro Index="0" MacroNo="0" ChatType="Guild" Message="!Buff de vida em 1 minuto"/>
<ChattingMacro Index="1" MacroNo="1" ChatType="Guild" Message="!Soltando buff de vida"/>
<ChattingMacro Index="2" MacroNo="2" ChatType="Guild" Message="!Buff de obtenção em 1 minuto"/>
<ChattingMacro Index="3" MacroNo="3" ChatType="Guild" Message="!Soltando buff de obtenção"/>
```

**Campos:**
- `Index`: Índice da macro (0-9)
- `MacroNo`: Número da macro
- `ChatType`: Tipo de chat (Guild, Public, Party, etc.)
- `Message`: Mensagem a ser enviada

---

## 2. CONFIGURAÇÕES DE INTERFACE (UIData)

### 2.1 Janelas de Chat (Index="32")

Múltiplas janelas de chat configuráveis (WindowIndex 0-4):

**Janela Principal (WindowIndex="0"):**
- Posição: X=2, Y=222
- Tamanho: 592x222 pixels
- Canais ativos: Notice, Public, Private, Party, Guild, Battle, GuildManager

**Janela de Sistema (WindowIndex="4"):**
- Posição: X=2, Y=444
- Tamanho: 591x222 pixels
- Canais ativos: System, PrivateItem

**Tipos de Chat Disponíveis:**
- Notice, World, Public, Private, System
- Party, Guild, Alliance, Friend
- Battle, LocalWar, RolePlay, Arsha
- Channel, Team, GM, Messenger
- DeadMessage, Sign, SolareCustom

### 2.2 Posicionamento de Elementos UI

Cada elemento UI tem:
- `Index`: ID do elemento
- `IsShow`: Visível ou não (true/false)
- `PendingType`: Âncora (LeftTop, RightTop, LeftBottom, RightBottom)
- `PosX/PosY`: Posição absoluta
- `RelativePosX/RelativePosY`: Posição relativa (0-1)
- `SizeX/SizeY`: Dimensões (quando aplicável)

**Exemplos de Elementos:**
- Index 9: Minimapa
- Index 21: Painel de Quest
- Index 113: Painel de Buff
- Index 100-110: Slots rápidos (quickslots)

---

## 3. CONFIGURAÇÕES DE JOGO (GameOption)

### 3.1 Controles e Câmera

```xml
<GameOption Type="GameMouseMode" DataValue="true"/>
<GameOption Type="MouseSensitivityX" DataValue="1"/>
<GameOption Type="MouseSensitivityY" DataValue="1"/>
<GameOption Type="AutoRunCamera" DataValue="true"/>
<GameOption Type="AutoRunCameraRotation" DataValue="1"/>
```

### 3.2 Interface e Visualização

```xml
<GameOption Type="ShowComboGuide" DataValue="true"/>
<GameOption Type="ShowKeyGuide" DataValue="true"/>
<GameOption Type="ShowGameTip" DataValue="true"/>
<GameOption Type="NavPathEffectType" DataValue="1"/>
```

### 3.3 Renderização de Jogadores

```xml
<GameOption Type="RenderPlayerColor" ColorType="Guild" DataValue="true"/>
<GameOption Type="RenderPlayerColor" ColorType="Party" DataValue="true"/>
<GameOption Type="RenderPlayerColor" ColorType="Enemy" DataValue="true"/>
```

### 3.4 Otimização

```xml
<GameOption Type="AutoOptimization" DataValue="true"/>
<GameOption Type="AutoOptimizationFrameLimit" DataValue="60"/>
<GameOption Type="useCharacterDistUpdate" DataValue="true"/>
<GameOption Type="farPlayerOptimizationLimitDist" DataValue="1000"/>
```

### 3.5 Recusas e Privacidade

```xml
<GameOption Type="RefuseRequests" DataValue="false"/>
<GameOption Type="PvpRefuse" DataValue="false"/>
<GameOption Type="ExchangeRefuse" DataValue="false"/>
<GameOption Type="GuildRefuse" DataValue="false"/>
```

---

## 4. CONFIGURAÇÕES GRÁFICAS GLOBAIS (GameOptionGlobal)

### 4.1 Vídeo

```xml
<Adaptor Value="0"/>
<WindowMode Value="FullScreenWindowed"/>
<Resolution Width="1920" Height="1080"/>
<GraphicOption Value="Low1"/>
```

### 4.2 Qualidade Gráfica

```xml
<Dof Value="false"/>
<AntiAliasing Value="true"/>
<AntiAliasingIndex Value="1"/>
<SSAO Value="true"/>
<Tessellation Value="false"/>
<PostFilter Value="2"/>
<TextureQuality Value="Medium"/>
```

### 4.3 Efeitos Visuais

```xml
<CharacterEffect Value="true"/>
<LensBlood Value="true"/>
<BloodEffect Value="2"/>
<SelfEffectAlpha Value="1"/>
<EffectAlpha Value="1"/>
<SkillPostEffect Value="1"/>
```

### 4.4 Câmera e FOV

```xml
<Fov Value="70"/>
<Gamma Value="1.5605"/>
<Contrast Value="-1"/>
<CameraLUTFilter Value="OldStyle"/>
```

### 4.5 Efeitos de Câmera

```xml
<CameraEffect 
    CameraShakePower="0.2" 
    CameraEffectMaster="0.2" 
    CameraFovPower="0.2" 
    CameraTranslatePower="0.2" 
    MotionBlurPower="0.2"/>
```

---

## 5. CONFIGURAÇÕES DE ÁUDIO (SoundOnOff e Volume)

### 5.1 Ativação de Sons

```xml
<SoundOnOff 
    Sound="true" 
    Music="true" 
    EnvSound="true" 
    RidingMusic="true" 
    WhisperMusic="true" 
    TraySound="false" 
    FairySound="true" 
    AroundPlayMusic="true" 
    SequenceSound="false"/>
```

### 5.2 Volumes

```xml
<Volume 
    MasterVolume="5.5" 
    FxVolume="100" 
    EnvVolume="100" 
    VoiceVolume="100" 
    MusicVolume="100" 
    HitFxVolume="100" 
    OtherPlayerVolume="100" 
    HitFxWeight="100" 
    FairyVolume="50" 
    AroundPlayMusicVolume="100" 
    SequenceMusicVolume="0"/>
```

---

## 6. CONFIGURAÇÕES DE NAMETAGS

```xml
<SelfPlayerNameTagVisible Value="NoShow"/>
<HPGaugeVisible Value="ImportantShow"/>
<OtherPlayerNameTagVisible Value="AllwaysShow"/>
<MonsterNameTagVisible Value="AllwaysShow"/>
<MonsterHPGaugeVisible Value="AllwaysShow"/>
<PartyPlayerNameTagVisible Value="AllwaysShow"/>
<GuildPlayerNameTagVisible Value="AllwaysShow"/>
<RankingPlayerNameTagVisible Value="NoShow"/>
<PetNameTagVisible Value="AllwaysShow"/>
<FairyNameTagVisible Value="AllwaysShow"/>
<MaidActorNameTagVisible Value="AllwaysShow"/>
```

**Valores possíveis:**
- `NoShow`: Nunca mostrar
- `ImportantShow`: Mostrar apenas importantes
- `AllwaysShow`: Sempre mostrar

---

## 7. INFORMAÇÕES DE PETS (PetInfo)

### 7.1 Pets Ativos

```xml
<PetInfo PetNo="10000000003733649" Follow="true" Find="true" GetItem="true"/>
<PetInfo PetNo="10000000003892213" Follow="true" Find="true" GetItem="true"/>
<PetInfo PetNo="10000000004075504" Follow="true" Find="true" GetItem="true"/>
<PetInfo PetNo="10000000005066661" Follow="true" Find="true" GetItem="true"/>
<PetInfo PetNo="10000000005067390" Follow="true" Find="true" GetItem="true"/>
```

**Campos:**
- `PetNo`: ID único do pet
- `Follow`: Pet segue o jogador
- `Find`: Pet procura recursos
- `GetItem`: Pet coleta itens

### 7.2 Ordem dos Pets (PetOrderList)

Lista com ordem de todos os pets (113 pets registrados):

```xml
<PetOrderList PetNo="10000000003719811" Order="26"/>
<PetOrderList PetNo="10000000004399711" Order="1"/>
<PetOrderList PetNo="10000000004399722" Order="2"/>
```

### 7.3 Grupos de Pets (PetGroupInfo)

5 grupos configuráveis com 5 pets cada:

```xml
<PetGroupInfo GroupIndex="1" PetNo="1878994928"/>
<PetGroupInfo GroupIndex="1" PetNo="1879986814"/>
<PetGroupInfo GroupIndex="1" PetNo="1879319146"/>
```

---

## 8. VOICE CHAT (VoiceChatInfo)

```xml
<VoiceChatOption 
    GuildNo="0" 
    IsVoiceMicOnOff="false" 
    IsVoiceSpeakerOnOff="false" 
    IsVoicePushToTalk="false" 
    VoiceMicVolume="50" 
    VoiceMicSensitivity="50" 
    VoiceSpeakerVolume="50" 
    VoiceMicAdjustment="1"/>
```

---

## 9. FILTROS DE MENSAGEM (MessageFilter)

16 tipos de filtros (Index 0-15):

```xml
<MessageFilter Index="0" IsOn="true"/>   <!-- Mensagens gerais -->
<MessageFilter Index="3" IsOn="false"/>  <!-- Desativado -->
<MessageFilter Index="9" IsOn="false"/>  <!-- Desativado -->
```

---

## 10. LISTA DE BLOQUEIO (BlockList)

Lista vazia no arquivo principal, mas pode conter jogadores bloqueados:

```xml
<BlockList Version="2"/>
```

Em outros personagens:
```xml
<BlockChattingNickName Name="Konosuba"/>
<BlockChattingNickName Name="OcarroDaPamonha"/>
<BlockChattingNickName Name="Fenndi"/>
```

---

## 11. VALORES DE UI (UIValue)

Valores numéricos, booleanos e timestamps para diversos elementos:

### 11.1 Números (Number)

```xml
<Number Index="39" Value="2.000000" StorageType="1"/>
<Number Index="153" Value="791.000000" StorageType="1"/>
<Number Index="154" Value="735.000000" StorageType="1"/>
<Number Index="155" Value="54003.000000" StorageType="1"/>
<Number Index="156" Value="320190.000000" StorageType="1"/>
```

### 11.2 Booleanos (Bool)

```xml
<Bool Index="71" Value="true" StorageType="1"/>
<Bool Index="72" Value="true" StorageType="1"/>
<Bool Index="61" Value="false" StorageType="1"/>
```

### 11.3 Timestamps (Time)

```xml
<Time Index="18" year="2023" month="6" day="20" hour="0" minute="0" second="0" StorageType="1"/>
<Time Index="111" year="2026" month="4" day="15" hour="0" minute="0" second="0" StorageType="1"/>
<Time Index="208" year="2026" month="4" day="19" hour="0" minute="0" second="0" StorageType="1"/>
```

---

## 12. PRESETS DE UI (UISettingPreset)

3 presets salvos (Preset0, Preset1, Preset2) + Revert:

- **UISettingPreset0**: Configuração personalizada 1
- **UISettingPreset1**: Configuração personalizada 2
- **UISettingPreset2**: Configuração personalizada 3
- **UISettingRevert**: Configuração padrão do jogo
- **UISettingBattlePreset**: Preset para combate

---

## 13. MEMOS (MemoList)

Notas criadas pelo jogador:

```xml
<MemoInfo 
    MemoNo="2" 
    Content="Missão aberta em Mediah 2 (restrição de fechamento 20:20h)" 
    On="0" 
    PosX="1611" 
    PosY="756" 
    SizeX="300" 
    SizeY="212" 
    Alpha="0" 
    Color="0" 
    UpdateTime="202403091032"/>
```

---

## 14. OUTRAS SEÇÕES IMPORTANTES

### 14.1 Skills e Atalhos
- `SkillCommandLock`: Bloqueio de comandos de skill
- `SkillCoolTimeSlot`: Slots de cooldown de skills
- `SkillPresetMemo`: Memos de presets de skills
- `SkillCoolTimeMemo`: Memos de cooldown

### 14.2 Quests
- `CheckQuestList`: Lista de quests verificadas
- `QuestSortType`: Tipo de ordenação de quests
- `QuestSelectType`: Tipo de seleção de quests
- `QuestOption`: Opções de quest

### 14.3 Inventário e Itens
- `ItemLockedInInventory`: Itens travados no inventário
- `RecentAlchemyHistory`: Histórico de alquimia recente
- `ExchangeCoinBookmark`: Favoritos de troca de moedas

### 14.4 Workers e Produção
- `WorkerNameChange`: Mudanças de nome de workers
- `WorkerAutoRecovery`: Recuperação automática de workers

### 14.5 Mundo e Navegação
- `WorldMapQuickScreenPosition`: Posições rápidas no mapa
- `ConsoleWorldMapBookMark`: Marcadores do mapa
- `JournalBookmark`: Favoritos do jornal

### 14.6 Customização
- `FairySettingData`: Configurações de fairy
- `PhotoMode`: Configurações de modo foto
- `DynamicPanelScale`: Escala dinâmica de painéis
- `ButtonShortcutsList`: Lista de atalhos de botões

### 14.7 Grupos e Social
- `PetGroupName`: Nomes de grupos de pets
- `CharacterOrderList`: Ordem dos personagens

### 14.8 Outros
- `ArtifactBagPresetInfo`: Presets de bolsa de artefatos
- `JewelPresetNameData`: Nomes de presets de joias
- `EmployeePresetNameInfo`: Informações de presets de empregados
- `ContentsCeremony`: Cerimônias de conteúdo
- `CommonMemo`: Memos comuns
- `UniqueEffectEquip`: Equipamentos com efeitos únicos

---

## 15. ESTRUTURA HIERÁRQUICA COMPLETA

```
gamevariable.xml
├── CheckQuestList
├── QuestSortType
├── QuestSelectType
├── QuickSlotData
├── ShortcutKey
├── ChattingMacro (10 macros)
├── UIData (múltiplas janelas e elementos)
│   ├── Chat Windows (5 janelas)
│   ├── UI Elements (160+ elementos)
│   └── WorldMapFilter
├── GameOption (100+ opções)
├── EquipSlotFlag
├── BlockList
├── MessageFilter (16 filtros)
├── GameOptionGlobal
│   ├── Vídeo
│   ├── Gráficos
│   ├── Áudio
│   └── Nametags
├── UIValue
│   ├── Number (200+ valores)
│   ├── Bool (50+ valores)
│   └── Time (10+ timestamps)
├── VoiceChatInfo
├── PetInfo
│   ├── Active Pets (6 pets)
│   ├── PetOrderList (113 pets)
│   └── PetGroupInfo (5 grupos)
├── SkillCommandLock
├── SkillCoolTimeSlot
├── ItemLockedInInventory
├── QuestOption
├── UISettingPreset (4 presets)
├── PetOrderList
├── PetGroupInfo
├── MemoList
├── GameOptionCustomize
├── ButtonShortcutsList
├── FairySettingData
├── ConsoleQuickMenu
├── ConsoleWorldMapBookMark
├── BlackSpiritSkillBlock
├── JournalBookmark
├── DynamicPanelScale
├── VehicleSkillCommandLock
├── SkillPresetMemo
├── MonsterChaseData
├── WorkerNameChange
├── RecentAlchemyHistory
├── UISortOption
├── ArtifactBagPresetInfo
├── SelectCollectTypeChange
├── PhotoMode
├── WorldMapQuickScreenPosition
├── AutoUseBuffItemInfo
├── ChatProcessMacro
├── JewelPresetNameData
├── WorkerAutoRecovery
├── QuickMenuPreset
├── PetGroupName
├── SkillCoolTimeMemo
├── UniqueEffectEquip
├── ExchangeCoinBookmark
├── CharacterOrderList
├── EmployeePresetNameInfo
├── ContentsCeremony
└── CommonMemo
```

---

## 16. OBSERVAÇÕES IMPORTANTES

1. **IDs Únicos**: Todos os pets, personagens e itens têm IDs únicos de 17-19 dígitos
2. **Posicionamento Relativo**: A UI usa tanto posições absolutas quanto relativas (0-1)
3. **Versionamento**: Cada seção tem um número de versão para compatibilidade
4. **Timestamps**: Datas são armazenadas em formato year/month/day/hour/minute/second
5. **Valores Booleanos**: Representados como "true"/"false" em strings
6. **Encoding**: O arquivo usa UTF-8 com CRLF (Windows)

---

## 17. POSSÍVEIS USOS PARA DESENVOLVIMENTO

- **Backup de Configurações**: Salvar e restaurar configurações completas
- **Análise de Pets**: Listar todos os pets e suas configurações
- **Macros Personalizadas**: Criar/editar macros programaticamente
- **UI Customizada**: Modificar posições de elementos da interface
- **Estatísticas**: Extrair dados de uso (timestamps, valores)
- **Sincronização**: Copiar configurações entre personagens
- **Presets**: Criar presets de configuração para diferentes situações

---

**Última atualização:** 2026-05-06
**Versão do arquivo analisado:** ID de personagem 1006413
