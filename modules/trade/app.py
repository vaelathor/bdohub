import json
import os
from flask import Blueprint, render_template, jsonify

trade_bp = Blueprint('trade', __name__, template_folder='templates')

_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_MOD_DIR, 'data', 'crates.json')
CITIES_PATH = os.path.join(_MOD_DIR, 'data', 'cities.json')


def load_crates():
    """Base de caixas de comércio (receitas + preços base) extraída da planilha gpw v2.15."""
    with open(DATA_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_cities():
    """Cidades com coordenadas e nomes PT-BR (fonte: bdocodex), para a calculadora de rotas."""
    with open(CITIES_PATH, encoding='utf-8') as f:
        return json.load(f)


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
