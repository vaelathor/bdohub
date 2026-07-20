from flask import Blueprint, render_template, jsonify, request
import os
import json
import sys
from .manager import BarteringManager

bartering_bp = Blueprint('bartering', __name__, 
                         template_folder='templates', 
                         static_folder='static')

# Caminhos baseados no diretório deste arquivo
BASE_DIR = os.path.dirname(__file__)
DATA_CSV = os.path.join(BASE_DIR, 'dados.csv')
SESSION_CSV = os.path.join(BASE_DIR, 'bartering.csv')
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
EXP_TABLE_PATH = os.path.join(BASE_DIR, 'exp_table.json')

manager = BarteringManager(DATA_CSV, SESSION_CSV)

def level_sort_key(level_name):
    # Dicionário de pesos para os ranks principais
    rank_order = {
        "Iniciante": 10, "Aprendiz": 20, "Habilidoso": 30, 
        "Profissional": 40, "Artesão": 50, "Mestre": 60, "Guru": 70
    }
    
    parts = level_name.split()
    rank = parts[0]
    # Se tiver número (ex: Artesão 5), o sub_level é 5. Se não, é 0.
    sub_level = int(parts[1]) if len(parts) > 1 else 0
    
    # Retorna uma tupla (peso_do_rank, sub_nivel) para ordenação correta
    return (rank_order.get(rank, 999), sub_level)

# Dados de teste para modo -t
TEST_EXP_TABLE = [
    {"level": "Artesão 1", "trades": 120, "base_exp_pct": 1.0, "bonus_exp": 420},
    {"level": "Artesão 2", "trades": 200, "base_exp_pct": 0.8, "bonus_exp": 430},
    {"level": "Artesão 3", "trades": 310, "base_exp_pct": 0.6, "bonus_exp": 440},
    {"level": "Artesão 4", "trades": 450, "base_exp_pct": 0.5, "bonus_exp": 450},
    {"level": "Mestre 1",  "trades": 580, "base_exp_pct": 0.4, "bonus_exp": 452},
    {"level": "Mestre 2",  "trades": 740, "base_exp_pct": 0.3, "bonus_exp": 452},
]

def load_exp_table():
    # Modo teste: retorna dados de exemplo sem persistência
    if '-t' in sys.argv:
        return TEST_EXP_TABLE

    if os.path.exists(EXP_TABLE_PATH):
        with open(EXP_TABLE_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_exp_table(table):
    if '-t' in sys.argv:
        return  # Não persiste em modo teste
    with open(EXP_TABLE_PATH, 'w', encoding='utf-8') as f:
        json.dump(table, f, indent=4, ensure_ascii=False)

def load_local_config():
    default = {
        "level": "Artesão 4",
        "vp": True,
        "cleia": False,
        "bargain": "157.360",
        "trades": {}
    }
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            try:
                conf = json.load(f)
                if "trades" not in conf: conf["trades"] = {}
                return conf
            except:
                return default
    return default

def save_local_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

@bartering_bp.route('/')
def index():
    return render_template('bartering_index.html', is_test=('-t' in sys.argv))

@bartering_bp.route('/api/status')
def get_status():
    config = load_local_config()
    calc_data = manager.calculate_costs(
        config['level'], 
        config['vp'], 
        config['cleia'], 
        config['bargain'], 
        config['trades']
    )
    calc_data['user_config'] = config
    return jsonify(calc_data)

@bartering_bp.route('/api/calculate', methods=['POST'])
def calculate():
    req = request.json
    calc_data = manager.calculate_costs(
        req['level'], 
        req['vp'], 
        req['cleia'], 
        req['bargain'], 
        req.get('trades', {})
    )
    return jsonify(calc_data)

@bartering_bp.route('/api/levels')
def get_levels():
    rank_order = {"Novato": 0, "Iniciante": 0, "Aprendiz": 1, "Habilidoso": 2, "Hábil": 2, "Profissional": 3, "Artesão": 4, "Mestre": 5, "Guru": 6}
    def sort_key(l):
        parts = l.split()
        rank = parts[0]
        num = int(parts[1]) if len(parts) > 1 else 0
        return (rank_order.get(rank, 99), num)
    levels = sorted(list(manager.levels_map.keys()), key=sort_key)
    return jsonify(levels)

@bartering_bp.route('/api/save_config', methods=['POST'])
def save_config():
    config = request.json
    save_local_config(config)
    return jsonify({"status": "success"})

@bartering_bp.route('/api/exp_table')
def get_exp_table():
    table = load_exp_table()
    # Ordena a tabela com base na ordem canônica dos níveis
    table.sort(key=lambda x: level_sort_key(x['level']), reverse=True)
    return jsonify(table)

@bartering_bp.route('/api/save_exp_record', methods=['POST'])
def save_exp_record():
    data = request.json
    level = data.get('level', '')
    new_trades = int(data.get('trades', 0))
    new_base_exp = float(data.get('base_exp_pct', 0))
    bonus_exp = float(data.get('bonus_exp', 0))

    table = load_exp_table()

    # Procura registro existente para este nível
    existing = next((r for r in table if r['level'] == level), None)

    if existing:
        # Média ponderada pelo número de permutas
        total_trades = existing['trades'] + new_trades
        weighted_exp = (
            (existing['base_exp_pct'] * existing['trades']) +
            (new_base_exp * new_trades)
        ) / total_trades if total_trades > 0 else 0

        existing['trades'] = total_trades
        existing['base_exp_pct'] = round(weighted_exp, 5)
        existing['bonus_exp'] = bonus_exp  # Atualiza sempre com o valor mais recente
    else:
        table.append({
            "level": level,
            "trades": new_trades,
            "base_exp_pct": round(new_base_exp, 5),
            "bonus_exp": bonus_exp
        })

    table.sort(key=lambda r: level_sort_key(r.get('level', '')))
    save_exp_table(table)
    return jsonify({"status": "success", "table": table})

@bartering_bp.route('/api/update_exp_bonus', methods=['POST'])
def update_exp_bonus():
    """Atualiza apenas o bônus de exp de um nível (campo editável da tabela)."""
    data = request.json
    level = data.get('level', '')
    bonus_exp = float(data.get('bonus_exp', 0))

    table = load_exp_table()
    existing = next((r for r in table if r['level'] == level), None)
    if existing:
        existing['bonus_exp'] = bonus_exp
        save_exp_table(table)
        return jsonify({"status": "success"})
    return jsonify({"status": "not_found"}), 404
@bartering_bp.route('/api/delete_exp_record', methods=['POST'])
def delete_exp_record():
    data = request.json
    level = data.get('level', '')
    
    table = load_exp_table()
    # Filtra mantendo apenas os níveis que NÃO são o alvo da deleção
    new_table = [r for r in table if r['level'] != level]
    
    if len(new_table) < len(table):
        save_exp_table(new_table)
        return jsonify({"status": "success"})
    return jsonify({"status": "not_found"}), 404
