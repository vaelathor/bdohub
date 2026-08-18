import json
import os
from flask import Blueprint, render_template, jsonify, request

trade_bp = Blueprint('trade', __name__, template_folder='templates')

_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_MOD_DIR, 'data', 'crates.json')
CITIES_PATH = os.path.join(_MOD_DIR, 'data', 'cities.json')
TOWNS_PATH = os.path.join(_MOD_DIR, 'data', 'towns.json')
DISABLED_PATH = os.path.join(_MOD_DIR, 'disabled_towns.json')
DISABLED_WS_PATH = os.path.join(_MOD_DIR, 'disabled_workshops.json')
CONNECTED_NODES_PATH = os.path.join(_MOD_DIR, 'connected_nodes.json')

try:
    from .towncalc import compute_town  # quando importado como modules.trade.app
    from . import towncalc
    towncalc_module = towncalc
except ImportError:
    import towncalc as towncalc_module  # quando rodado standalone (staging)
    compute_town = towncalc_module.compute_town


def load_crates():
    """Base de caixas de comércio (receitas + preços base) extraída da planilha gpw v2.15."""
    with open(DATA_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_cities():
    """Cidades com coordenadas e nomes PT-BR (fonte: bdocodex), para a calculadora de rotas."""
    with open(CITIES_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_towns():
    """Painel de cidades/oficinas/operários gerado por build_towns.py."""
    with open(TOWNS_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_disabled_towns():
    """Cidades desligadas pelo usuário (não entram na contagem de caixas)."""
    try:
        with open(DISABLED_PATH, encoding='utf-8') as f:
            return set(json.load(f).get('towns', []))
    except (OSError, ValueError):
        return set()


def save_disabled_towns(disabled):
    """Persiste a lista de cidades desligadas."""
    with open(DISABLED_PATH, 'w', encoding='utf-8') as f:
        json.dump({'towns': sorted(disabled)}, f, ensure_ascii=False, indent=1)


def load_disabled_workshops():
    """Oficinas desligadas por cidade: {nome_cidade: [house_key, ...]}."""
    try:
        with open(DISABLED_WS_PATH, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_disabled_workshops(data):
    """Persiste o mapa de oficinas desligadas por cidade."""
    with open(DISABLED_WS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def load_connected_nodes():
    """Nodes que o jogador JÁ conectou no jogo (não pagam CP de novo)."""
    try:
        with open(CONNECTED_NODES_PATH, encoding='utf-8') as f:
            return set(json.load(f).get('nodes', []))
    except (OSError, ValueError):
        return set()


def save_connected_nodes(nodes):
    """Persiste a lista de nodes conectados."""
    with open(CONNECTED_NODES_PATH, 'w', encoding='utf-8') as f:
        json.dump({'nodes': sorted(nodes)}, f, ensure_ascii=False, indent=1)


_pt_cache = None


def _pt_names():
    """Mapa house -> namePt (tradução já aplicada no towns.json), para o recálculo
    dinâmico preservar os nomes PT das oficinas/alojamentos."""
    global _pt_cache
    if _pt_cache is not None:
        return _pt_cache
    pt = {}
    try:
        data = load_towns()
        for t in data.get('towns', []):
            for w in t.get('workshops', []):
                if w.get('namePt'):
                    pt[w['house']] = w['namePt']
            for grp in ('forced', 'chosen'):
                for c in t.get('lodging', {}).get(grp, []):
                    if c.get('namePt'):
                        pt[c['house']] = c['namePt']
    except OSError:
        pass
    _pt_cache = pt
    return pt


def _recalc_town(town, disabled_ws):
    """Recalcula uma cidade com as oficinas desligadas e nodes já conectados,
    preservando os campos dinâmicos (disabled) que o frontend injeta e
    marcando os alojamentos que deixaram de ser necessários (o mais custoso
    sai primeiro)."""
    aff = town.get('affTown')
    if aff is None:
        return town
    try:
        rec = compute_town(aff, frozenset(disabled_ws), pt_names=_pt_names(),
                           connected_nodes=load_connected_nodes())
    except Exception:
        return town
    if rec is None:
        return town

    # alojamentos que existiam no chosen original e saíram no recálculo
    original = town.get('lodging', {}).get('chosen', [])
    current = {c.get('house') for c in rec['lodging'].get('chosen', [])}
    removed = [c for c in original if c.get('house') not in current]
    removed.sort(key=lambda c: (-(c.get('cp') or 0), -(c.get('slots') or 0)))
    rec['lodging']['removed'] = removed

    rec['disabled'] = town.get('disabled', False)
    rec['disabledWs'] = sorted(disabled_ws)
    return rec


@trade_bp.route('/')
def index():
    return render_template('trade_index.html')


@trade_bp.route('/api/crates')
def crates():
    data = load_crates()
    return jsonify({'crates': data.get('crates', []), 'source': data.get('generatedFrom'), 'error': None})


@trade_bp.route('/api/cities')
def cities():
    data = load_cities()
    return jsonify({'cities': data.get('cities', []), 'error': None})


@trade_bp.route('/api/towns')
def towns():
    data = load_towns()
    disabled = load_disabled_towns()
    ws_map = load_disabled_workshops()
    connected = load_connected_nodes()
    out = []
    for t in data.get('towns', []):
        t['disabled'] = t.get('name') in disabled
        t['disabledWs'] = sorted(ws_map.get(t['name'], []))
        # recálculo quando há oficinas desligadas OU nodes já conectados
        if t['disabledWs'] or (connected and t.get('conn_detail')):
            t = _recalc_town(t, t['disabledWs'])
        out.append(t)
    return jsonify({'params': data.get('params', {}), 'towns': out, 'error': None})


@trade_bp.route('/api/towns/toggle', methods=['POST'])
def towns_toggle():
    """Liga/desliga uma cidade na contagem de caixas."""
    req = request.get_json(silent=True) or {}
    name = req.get('town')
    disabled = req.get('disabled')
    if not name:
        return jsonify({'error': 'town ausente'}), 400
    current = load_disabled_towns()
    if disabled:
        current.add(name)
    else:
        current.discard(name)
    save_disabled_towns(current)
    return jsonify({'ok': True, 'town': name, 'disabled': name in current, 'error': None})


@trade_bp.route('/api/towns/toggle_ws', methods=['POST'])
def towns_toggle_ws():
    """Liga/desliga uma oficina individual; recalcula a cidade em tempo real
    (operários, alojamentos escolhidos, CP de casas + conexão de nodes, caixas/dia)."""
    req = request.get_json(silent=True) or {}
    name = req.get('town')
    house = req.get('house')
    disabled = req.get('disabled')
    if not name or not house:
        return jsonify({'error': 'town/house ausentes'}), 400

    data = load_towns()
    town = next((t for t in data.get('towns', []) if t.get('name') == name), None)
    if town is None:
        return jsonify({'error': 'cidade não encontrada'}), 404

    ws_map = load_disabled_workshops()
    lst = set(ws_map.get(name, []))
    if disabled:
        lst.add(house)
    else:
        lst.discard(house)
    ws_map[name] = sorted(lst)
    if not ws_map[name]:
        ws_map.pop(name, None)
    save_disabled_workshops(ws_map)

    rec = _recalc_town(town, ws_map.get(name, []))
    return jsonify({'ok': True, 'town': rec, 'error': None})


@trade_bp.route('/api/towns/toggle_node', methods=['POST'])
def towns_toggle_node():
    """Marca/desmarca um node como já conectado no jogo; o CP dele deixa de
    ser contado na conexão da cidade."""
    req = request.get_json(silent=True) or {}
    node = str(req.get('node'))
    connected = req.get('connected')
    if not node:
        return jsonify({'error': 'node ausente'}), 400
    current = load_connected_nodes()
    if connected:
        current.add(node)
    else:
        current.discard(node)
    save_connected_nodes(current)

    # recalcula TODAS as cidades afetadas (um node pode aparecer em várias)
    data = load_towns()
    ws_map = load_disabled_workshops()
    disabled = load_disabled_towns()
    out = []
    for t in data.get('towns', []):
        t['disabled'] = t.get('name') in disabled
        t['disabledWs'] = sorted(ws_map.get(t['name'], []))
        if t.get('conn_detail'):
            t = _recalc_town(t, t['disabledWs'])
        out.append(t)
    return jsonify({'ok': True, 'node': node, 'connected': connected,
                    'towns': out, 'error': None})
