import json
import os
import re
import time
import threading
import unicodedata
import requests
import backup_utils
from flask import Blueprint, render_template, request, jsonify, send_file

market_bp = Blueprint('market', __name__, template_folder='templates', static_folder='static')

ARSH_API = 'https://api.arsha.io'
REGION = 'sa'
CACHE_TTL = 15 * 60      # snapshot do mercado (15 min, igual ao cache do arsha)
ITEM_TTL = 30 * 60       # detalhes de item (30 min)
MAX_ATTEMPTS = 3         # tentativas por fonte de dados
RETRY_DELAY = 1.0        # segundos entre tentativas

# Ícones reais dos itens (fonte: BDOCodex, cache local em disco)
_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(_MOD_DIR, 'static', 'icons')
CODE_BASE = 'https://bdocodex.com'
CODE_UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
with open(os.path.join(_MOD_DIR, 'codex_slots.json'), encoding='utf-8') as _f:
    _SLOTS = json.load(_f)  # "mainCategory-subCategory" -> caminho base do ícone

PINNED_PATH = os.path.join(_MOD_DIR, 'pinned.json')
WATCHED_PATH = os.path.join(_MOD_DIR, 'watched.json')
CHECK_INTERVAL = 5 * 60  # checagem de disponibilidade dos níveis vigiados
_last_check = [0.0]


def load_pinned():
    """Lista de itens favoritados persistida em disco."""
    if os.path.exists(PINNED_PATH):
        try:
            with open(PINNED_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            items = data.get('items') if isinstance(data, dict) else None
            if isinstance(items, list):
                return items
        except (ValueError, OSError):
            pass
    return []


def save_pinned(items):
    """Grava a lista de favoritos (com backup automático, padrão do hub)."""
    with open(PINNED_PATH, 'w', encoding='utf-8') as f:
        json.dump({'items': items}, f, indent=4, ensure_ascii=False)
    backup_utils.backup_single_file('modules/market/pinned.json')

# Caches em memória
_cache = {'market': None, 'ts': 0.0}
_items = {}  # id -> {'data': [...], 'ts': float}
_bids = {}   # (id, sid) -> {'data': [...], 'ts': float}
_hist = {}   # (id, sid) -> {'data': [...], 'ts': float}  (histórico diário)
BID_TTL = 3 * 60  # ofertas ativas (cache curto; a própria arsha já cacheia ~30 min)
HIST_TTL = 6 * 3600  # histórico de preços: dados diários, cache longo
_lock = threading.Lock()

# Cache em disco: a API do arsha é instável (503/500 com frequência), então
# guardamos uma cópia local para continuar servindo dados (possivelmente
# antigos) quando a fonte externa cai.
_CACHE_DIR = os.path.join(_MOD_DIR, '.cache')
_SNAP_FILE = os.path.join(_CACHE_DIR, f'market_{REGION}.json')
_ITEM_DIR = os.path.join(_CACHE_DIR, 'items')
_BID_DIR = os.path.join(_CACHE_DIR, 'bids')
_HIST_DIR = os.path.join(_CACHE_DIR, 'history')


def _write_disk(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except OSError:
        pass


def _read_disk(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _norm(text):
    """Minúsculas e sem acentos, para busca tolerante (ex.: 'kzarka' casa com 'Kzarka')."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', text.lower())
        if unicodedata.category(c) != 'Mn'
    )


def _get(url, params, attempts=MAX_ATTEMPTS):
    """GET com retry; os endpoints do mercado são protegidos por WAF e falham às vezes."""
    last_exc = None
    for i in range(attempts):
        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            last_exc = RuntimeError(f'{resp.status_code} {resp.reason}')
        except requests.RequestException as exc:
            last_exc = exc
        if i < attempts - 1:
            time.sleep(RETRY_DELAY * (i + 1))
    raise last_exc


def get_market_snapshot(force=False):
    """Snapshot do mercado SA (nomes em PT-BR), cacheado por 15 minutos.

    Se a API estiver fora do ar, serve a última cópia salva em disco.
    """
    with _lock:
        if not force and _cache['market'] is not None and (time.time() - _cache['ts']) < CACHE_TTL:
            return _cache['market']

    try:
        data = _get(f'{ARSH_API}/v2/{REGION}/market', {'lang': 'pt'})
    except Exception:
        disk = _read_disk(_SNAP_FILE)
        if disk is not None:
            # mantém o horário original da coleta para sinalizar dados antigos
            with _lock:
                _cache['market'] = disk.get('data', disk)
                _cache['ts'] = float(disk.get('ts', 0))
            return _cache['market']
        raise

    with _lock:
        _cache['market'] = data
        _cache['ts'] = time.time()
    _write_disk(_SNAP_FILE, {'ts': _cache['ts'], 'data': data})
    return data


def _get_item_v2(item_id):
    """Detalhes via v2 (JSON com nomes em PT)."""
    return _get(
        f'{ARSH_API}/v2/{REGION}/item',
        {'id': item_id, 'lang': 'pt'}
    )


def _get_item_v1(item_id):
    """Fallback via v1 GetWorldMarketSubList (pipe-separated, sem nome).

    Formato real de cada linha: mainKey-subKey-maxEnhance-price-stock-
    totalTrades-priceMin-priceMax-lastSoldPrice-lastSoldTime.
    O nível inicial (minEnhance) é derivado: começa em 0 e cada linha
    cobre do nível seguinte até maxEnhance (linhas agrupam níveis com o
    mesmo preço, ex.: Kzarka +0~+7 numa linha só).
    """
    data = _get(f'{ARSH_API}/v1/{REGION}/GetWorldMarketSubList', {'id': item_id})
    raw = data.get('resultMsg', '')
    levels = []
    prev_max = -1
    for row in raw.split('|'):
        parts = row.split('-')
        if len(parts) < 10:
            continue
        try:
            max_enh = int(parts[2])
            levels.append({
                'sid': int(parts[1]),
                'minEnhance': prev_max + 1,
                'maxEnhance': max_enh,
                'basePrice': int(parts[3]),
                'currentStock': int(parts[4]),
                'totalTrades': int(parts[5]),
                'priceMin': int(parts[6]),
                'priceMax': int(parts[7]),
                'lastSoldPrice': int(parts[8]),
                'lastSoldTime': int(parts[9]),
            })
            prev_max = max_enh
        except (ValueError, IndexError):
            continue
    return levels


def get_item_levels(item_id):
    """Níveis de aprimoramento com cache local de 30 min; v2 → v1 → disco."""
    with _lock:
        cached = _items.get(item_id)
        if cached and (time.time() - cached['ts']) < ITEM_TTL:
            return cached['data']

    try:
        data = _get_item_v2(item_id)
        if not isinstance(data, list) or len(data) == 0:
            raise RuntimeError('resposta v2 vazia')
    except Exception:
        try:
            data = _get_item_v1(item_id)
        except Exception:
            disk = _read_disk(os.path.join(_ITEM_DIR, f'{item_id}.json'))
            if disk is None:
                raise
            # marca como antigo para o cliente sinalizar dados em cache
            with _lock:
                _items[item_id] = {'data': disk, 'ts': time.time() - ITEM_TTL - 1}
            return disk

    with _lock:
        _items[item_id] = {'data': data, 'ts': time.time()}
    _write_disk(os.path.join(_ITEM_DIR, f'{item_id}.json'), data)
    return data


# ---- Alertas de disponibilidade (níveis vigiados) ----
#
# O usuário escolhe níveis de aprimoramento específicos de um item (ex.: Cinto
# Prione OCT ou ENE) para ser avisado quando eles ENTRAREM no mercado. Uma
# thread de fundo verifica o estoque desses níveis a cada 5 min e registra o
# momento da entrada (transição de estoque 0 -> > 0).


def load_watched():
    """Lista de níveis vigiados persistida em disco."""
    if os.path.exists(WATCHED_PATH):
        try:
            with open(WATCHED_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            watched = data.get('watched') if isinstance(data, dict) else None
            if isinstance(watched, list):
                return watched
        except (ValueError, OSError):
            pass
    return []


def save_watched(watched):
    """Grava os níveis vigiados (com backup automático, padrão do hub)."""
    with open(WATCHED_PATH, 'w', encoding='utf-8') as f:
        json.dump({'watched': watched}, f, indent=4, ensure_ascii=False)
    backup_utils.backup_single_file('modules/market/watched.json')


def _watch_key(w):
    return (w.get('id'), w.get('sid'))


def _refresh_watch_state(w):
    """Atualiza o estado de um nível vigiado (estoque/entrada).

    A primeira checagem apenas registra o estado atual sem disparar alerta
    (senão todo nível recém-vigiado que já está no mercado alertaria na hora).
    Retorna True se algo mudou.
    """
    try:
        levels = get_item_levels(w['id'])
    except Exception:
        return False
    lvl = next((l for l in levels if l.get('sid') == w.get('sid')), None)
    if lvl is None:
        return False
    cur = lvl.get('currentStock') or 0
    st = w.setdefault('state', {})
    if 'stock' not in st:
        st['stock'] = cur
        st['lastEntry'] = None
        st['new'] = False
    else:
        prev = st['stock'] or 0
        if prev == 0 and cur > 0:
            st['lastEntry'] = time.time()
            st['new'] = True
        st['stock'] = cur
    if cur > 0:
        # menor preço de venda listado (preço real, não o base) — best-effort
        lowest = _lowest_ask(w['id'], w['sid'])
        if lowest is not None:
            st['lowestAsk'] = lowest
    # tendência de 7 dias (série diária): último ponto vs o de 7 dias atrás
    hist = get_history(w['id'], w['sid'])
    if len(hist) >= 8:
        base = hist[-8]
        if base:
            st['trend7'] = round((hist[-1] - base) / base * 100, 1)
    return True


def check_watched():
    """Checa a disponibilidade de todos os níveis vigiados e salva o estado."""
    watched = load_watched()
    _last_check[0] = time.time()
    if not watched:
        return
    changed = False
    for w in watched:
        if _refresh_watch_state(w):
            changed = True
    if changed:
        save_watched(watched)


def _watched_loop():
    """Thread de fundo: verifica os níveis vigiados a cada CHECK_INTERVAL."""
    time.sleep(5)  # espera o servidor subir antes da primeira checagem
    while True:
        try:
            check_watched()
        except Exception:
            pass
        time.sleep(CHECK_INTERVAL)


threading.Thread(target=_watched_loop, daemon=True).start()


@market_bp.route('/')
def index():
    return render_template('market_index.html')


@market_bp.route('/api/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'items': [], 'count': 0, 'error': None})

    nq = _norm(q)
    try:
        snapshot = get_market_snapshot()
    except Exception as exc:
        return jsonify({'items': [], 'count': 0, 'error': str(exc)}), 502

    with _lock:
        stale = (time.time() - _cache['ts']) > CACHE_TTL
        stale_ts = int(_cache['ts']) if stale else None

    items = [i for i in snapshot if nq in _norm(i.get('name', ''))]
    # Relevância: itens que começam com a busca primeiro; depois por volume de negócios
    items.sort(key=lambda i: (
        0 if _norm(i['name']).startswith(nq) else 1,
        -i.get('totalTrades', 0)
    ))
    return jsonify({'items': items[:50], 'count': len(items), 'error': None,
                    'stale': stale, 'staleTs': stale_ts})


@market_bp.route('/api/item')
def item():
    """Níveis de aprimoramento de um item com preços (sub-lista do mercado)."""
    item_id = request.args.get('id', type=int)
    if not item_id:
        return jsonify({'error': 'Parâmetro id é obrigatório.'}), 400

    try:
        levels = get_item_levels(item_id)
    except Exception as exc:
        return jsonify({'error': str(exc), 'levels': []}), 502

    with _lock:
        entry = _items.get(item_id)
        item_stale = entry is not None and (time.time() - entry['ts']) > ITEM_TTL
    return jsonify({'levels': levels, 'error': None, 'stale': bool(item_stale)})


def _get_bids_v1(item_id, sid):
    """Ofertas ativas de um nível: cada ordem é preço-vendedores-compradores."""
    data = _get(f'{ARSH_API}/v1/{REGION}/GetBiddingInfoList', {'id': item_id, 'sid': sid})
    raw = data.get('resultMsg', '')
    orders = []
    for row in raw.split('|'):
        parts = row.split('-')
        if len(parts) < 3:
            continue
        try:
            orders.append({
                'price': int(parts[0]),
                'sellers': int(parts[1]),
                'buyers': int(parts[2]),
            })
        except (ValueError, IndexError):
            continue
    return orders


def _lowest_ask(item_id, sid):
    """Menor preço de venda listado no livro de ofertas (best-effort, 1 tentativa).

    Cada ordem do GetBiddingInfoList é 'preço-vendedores-compradores'; o menor
    preço com vendedores > 0 é a oferta mais barata disponível agora. Usado nos
    alertas de disponibilidade para mostrar quanto custa de fato o item.
    """
    try:
        resp = requests.get(
            f'{ARSH_API}/v1/{REGION}/GetBiddingInfoList',
            params={'id': item_id, 'sid': sid}, timeout=8)
        if resp.status_code != 200:
            return None
        raw = resp.json().get('resultMsg', '')
    except (requests.RequestException, ValueError):
        return None
    best = None
    for row in raw.split('|'):
        parts = row.split('-')
        if len(parts) < 3:
            continue
        try:
            if int(parts[1]) > 0:
                p = int(parts[0])
                best = p if best is None else min(best, p)
        except (ValueError, IndexError):
            continue
    return best


def get_history(item_id, sid):
    """Série de preços diária dos últimos ~90 dias de um nível (gráfico in-game).

    Cacheada 6h em memória + disco; 1 tentativa curta (dados diários não
    precisam de retry). Retorna lista vazia se a fonte estiver fora do ar e
    não houver cópia em disco.
    """
    key = (item_id, sid)
    with _lock:
        cached = _hist.get(key)
        if cached and (time.time() - cached['ts']) < HIST_TTL:
            return cached['data']
    prices = None
    for _ in range(2):  # retry curto (a arsha falha às vezes)
        try:
            resp = requests.get(
                f'{ARSH_API}/v1/{REGION}/GetMarketPriceInfo',
                params={'id': item_id, 'sid': sid}, timeout=15)
            if resp.status_code == 200:
                raw = resp.json().get('resultMsg', '')
                prices = [int(x) for x in raw.split('-') if x]
                if prices:
                    break
        except (requests.RequestException, ValueError):
            pass
        time.sleep(RETRY_DELAY)
    if not prices:
        disk = _read_disk(os.path.join(_HIST_DIR, f'{item_id}_{sid}.json'))
        if disk is None:
            return []
        with _lock:
            _hist[key] = {'data': disk, 'ts': time.time() - HIST_TTL - 1}
        return disk
    with _lock:
        _hist[key] = {'data': prices, 'ts': time.time()}
    _write_disk(os.path.join(_HIST_DIR, f'{item_id}_{sid}.json'), prices)
    return prices


def _icon_path(item_id, main_cat, sub_cat):
    """Caminho local do ícone; baixa do BDOCodex na primeira vez (e cacheia em disco)."""
    path = os.path.join(ICON_DIR, f'{item_id}.webp')
    if os.path.exists(path):
        return path

    def _save(resp):
        if resp.status_code != 200 or resp.content[:4] != b'RIFF':
            return None
        os.makedirs(ICON_DIR, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(resp.content)
        return path

    # Equipamento: o caminho é derivável da categoria (padrão estável do codex)
    slot = _SLOTS.get(f'{main_cat}-{sub_cat}')
    if slot:
        try:
            resp = requests.get(
                f'{CODE_BASE}/items/new_icon/{slot}/{item_id:08d}.webp',
                timeout=15, headers=CODE_UA)
            found = _save(resp)
            if found:
                return found
        except requests.RequestException:
            pass

    # Fallback: raspar a página do item para achar a URL exata do ícone
    try:
        html = requests.get(f'{CODE_BASE}/us/item/{item_id}/', timeout=20, headers=CODE_UA).text
        m = re.search(r'https://bdocodex\.com/items/new_icon/[^"\' ]+\.webp', html)
        if m:
            resp = requests.get(m.group(0), timeout=15, headers=CODE_UA)
            found = _save(resp)
            if found:
                return found
    except requests.RequestException:
        pass
    return None


@market_bp.route('/api/icon/<int:item_id>')
def icon(item_id):
    """Ícone real do item (baixado e servido localmente; 404 = sem ícone)."""
    main_cat = request.args.get('m', type=int, default=0)
    sub_cat = request.args.get('s', type=int, default=0)
    path = _icon_path(item_id, main_cat, sub_cat)
    if not path:
        return '', 404
    return send_file(path, mimetype='image/webp', max_age=30 * 24 * 3600)


@market_bp.route('/api/pinned')
def pinned_list():
    """Favoritos com preço/estoque atuais do snapshot (quando disponíveis)."""
    items = load_pinned()
    snapshot = None
    try:
        snapshot = get_market_snapshot()
    except Exception:
        pass
    by_id = {i['id']: i for i in snapshot} if snapshot else {}
    out = []
    for it in items:
        cur = by_id.get(it['id'], {})
        out.append({
            'id': it['id'],
            'name': it.get('name') or cur.get('name') or '',
            'mainCategory': it.get('mainCategory', cur.get('mainCategory', 0)),
            'subCategory': it.get('subCategory', cur.get('subCategory', 0)),
            'pinnedAt': it.get('pinnedAt'),
            'price': cur.get('basePrice'),
            'stock': cur.get('currentStock'),
            'trades': cur.get('totalTrades'),
        })
    return jsonify({'items': out, 'error': None})


@market_bp.route('/api/pinned/toggle', methods=['POST'])
def pinned_toggle():
    """Favorita/desfavorita um item (recebe id + dados básicos do item)."""
    data = request.json or {}
    item_id = data.get('id')
    if not item_id:
        return jsonify({'error': 'id é obrigatório.'}), 400

    items = load_pinned()
    if any(i['id'] == item_id for i in items):
        items = [i for i in items if i['id'] != item_id]
        pinned = False
    else:
        items.append({
            'id': item_id,
            'name': data.get('name'),
            'mainCategory': data.get('mainCategory', 0),
            'subCategory': data.get('subCategory', 0),
            'pinnedAt': time.time(),
        })
        pinned = True
    save_pinned(items)
    return jsonify({'pinned': pinned, 'ids': [i['id'] for i in items], 'error': None})


@market_bp.route('/api/watched')
def watched_list():
    """Níveis vigiados com estado de disponibilidade (atualizado pela thread de fundo)."""
    if time.time() - _last_check[0] > CHECK_INTERVAL * 2:
        try:
            check_watched()  # refresh pontual se a thread estiver atrasada (ex.: pós-restart)
        except Exception:
            pass
    watched = load_watched()
    return jsonify({'watched': watched, 'checkedAt': int(_last_check[0]), 'error': None})


@market_bp.route('/api/watched/toggle', methods=['POST'])
def watched_toggle():
    """Vigia/para de vigiar um nível de aprimoramento específico."""
    data = request.json or {}
    item_id = data.get('id')
    sid = data.get('sid')
    if not item_id or sid is None:
        return jsonify({'error': 'id e sid são obrigatórios.'}), 400

    watched = load_watched()
    existing = next((w for w in watched if _watch_key(w) == (item_id, sid)), None)
    if existing:
        watched = [w for w in watched if _watch_key(w) != (item_id, sid)]
        watching = False
    else:
        w = {
            'id': item_id,
            'sid': sid,
            'name': data.get('name'),
            'label': data.get('label'),
            'mainCategory': data.get('mainCategory', 0),
            'subCategory': data.get('subCategory', 0),
            'addedAt': time.time(),
            'state': {},
        }
        _refresh_watch_state(w)  # baseline imediato (best-effort)
        watched.append(w)
        watching = True
    save_watched(watched)
    return jsonify({'watching': watching, 'count': len(watched), 'error': None})


@market_bp.route('/api/watched/ack', methods=['POST'])
def watched_ack():
    """Marca um alerta como visto (some o selo 'novo')."""
    data = request.json or {}
    item_id = data.get('id')
    sid = data.get('sid')
    watched = load_watched()
    for w in watched:
        if w.get('id') == item_id and w.get('sid') == sid:
            w.setdefault('state', {})['new'] = False
            break
    save_watched(watched)
    return jsonify({'error': None})


@market_bp.route('/api/history')
def history():
    """Histórico de preços diário (~90 dias) de um nível de aprimoramento."""
    item_id = request.args.get('id', type=int)
    sid = request.args.get('sid', type=int, default=0)
    if not item_id:
        return jsonify({'error': 'Parâmetro id é obrigatório.'}), 400
    prices = get_history(item_id, sid)
    return jsonify({'history': prices, 'error': None})


@market_bp.route('/api/bids')
def bids():
    """Livro de ofertas de um nível de aprimoramento (vendedores x compradores)."""
    item_id = request.args.get('id', type=int)
    sid = request.args.get('sid', type=int, default=0)
    if not item_id:
        return jsonify({'error': 'Parâmetro id é obrigatório.'}), 400

    key = (item_id, sid)
    with _lock:
        cached = _bids.get(key)
        if cached and (time.time() - cached['ts']) < BID_TTL:
            return jsonify({'orders': cached['data'], 'error': None})

    try:
        orders = _get_bids_v1(item_id, sid)
    except Exception as exc:
        disk = _read_disk(os.path.join(_BID_DIR, f'{item_id}_{sid}.json'))
        if disk is None:
            return jsonify({'error': str(exc), 'orders': []}), 502
        with _lock:
            _bids[key] = {'data': disk, 'ts': time.time() - BID_TTL - 1}
        return jsonify({'orders': disk, 'error': None, 'stale': True})

    with _lock:
        _bids[key] = {'data': orders, 'ts': time.time()}
    _write_disk(os.path.join(_BID_DIR, f'{item_id}_{sid}.json'), orders)
    return jsonify({'orders': orders, 'error': None, 'stale': False})
