import time
import threading
import unicodedata
import requests
from flask import Blueprint, render_template, request, jsonify

market_bp = Blueprint('market', __name__, template_folder='templates', static_folder='static')

ARSH_API = 'https://api.arsha.io'
REGION = 'sa'
CACHE_TTL = 15 * 60      # snapshot do mercado (15 min, igual ao cache do arsha)
ITEM_TTL = 30 * 60       # detalhes de item (30 min)
MAX_ATTEMPTS = 3         # tentativas por fonte de dados
RETRY_DELAY = 1.0        # segundos entre tentativas

# Caches em memória
_cache = {'market': None, 'ts': 0.0}
_items = {}  # id -> {'data': [...], 'ts': float}
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
