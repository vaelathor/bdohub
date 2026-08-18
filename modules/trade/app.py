import json
import os
from flask import Blueprint, render_template, jsonify, request

trade_bp = Blueprint('trade', __name__, template_folder='templates')

_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_MOD_DIR, 'data', 'crates.json')
CITIES_PATH = os.path.join(_MOD_DIR, 'data', 'cities.json')
TOWNS_PATH = os.path.join(_MOD_DIR, 'data', 'towns.json')
DISABLED_PATH = os.path.join(_MOD_DIR, 'disabled_towns.json')


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
    for t in data.get('towns', []):
        t['disabled'] = t.get('name') in disabled
    return jsonify({'params': data.get('params', {}), 'towns': data.get('towns', []), 'error': None})


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
