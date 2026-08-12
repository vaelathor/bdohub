import json
import os
import re
import time
import threading
import unicodedata
import requests
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

# Caches em memória
_cache = {'market': None, 'ts': 0.0}
_items = {}  # id -> {'data': [...], 'ts': float}
_bids = {}   # (id, sid) -> {'data': [...], 'ts': float}
BID_TTL = 3 * 60  # ofertas ativas (cache curto; a própria arsha já cacheia ~30 min)
_lock = threading.Lock()


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
    """Snapshot do mercado SA (nomes em PT-BR), cacheado por 15 minutos."""
    with _lock:
        if not force and _cache['market'] is not None and (time.time() - _cache['ts']) < CACHE_TTL:
            return _cache['market']

    data = _get(f'{ARSH_API}/v2/{REGION}/market', {'lang': 'pt'})

    with _lock:
        _cache['market'] = data
        _cache['ts'] = time.time()
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
    """Níveis de aprimoramento com cache local de 30 min; v2 com fallback para v1."""
    with _lock:
        cached = _items.get(item_id)
        if cached and (time.time() - cached['ts']) < ITEM_TTL:
            return cached['data']

    try:
        data = _get_item_v2(item_id)
        if not isinstance(data, list) or len(data) == 0:
            raise RuntimeError('resposta v2 vazia')
    except Exception:
        data = _get_item_v1(item_id)

    with _lock:
        _items[item_id] = {'data': data, 'ts': time.time()}
    return data


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
        # Em falha da API, tenta servir o cache antigo
        with _lock:
            stale = _cache['market']
        if stale is not None:
            snapshot = stale
        else:
            return jsonify({'items': [], 'count': 0, 'error': str(exc)}), 502

    items = [i for i in snapshot if nq in _norm(i.get('name', ''))]
    # Relevância: itens que começam com a busca primeiro; depois por volume de negócios
    items.sort(key=lambda i: (
        0 if _norm(i['name']).startswith(nq) else 1,
        -i.get('totalTrades', 0)
    ))
    return jsonify({'items': items[:50], 'count': len(items), 'error': None})


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

    return jsonify({'levels': levels, 'error': None})


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
        return jsonify({'error': str(exc), 'orders': []}), 502

    with _lock:
        _bids[key] = {'data': orders, 'ts': time.time()}
    return jsonify({'orders': orders, 'error': None})
