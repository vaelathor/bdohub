import os
import sys
import json
from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, request, jsonify

# Setup parent path to import prata.py
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from prata import jogo_hoje
except ImportError:
    def jogo_hoje():
        return 0, 0.0

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'dashboard.json')

# Timezone UTC-3 (Brasília)
BRT = timezone(timedelta(hours=-3))

def get_now():
    """Retorna datetime atual em UTC-3 (Brasília)."""
    return datetime.now(BRT)

# Mapeamento de dias da semana
WEEKDAY_MAP = {
    'Seg': 0, 'Ter': 1, 'Qua': 2, 'Qui': 3,
    'Sex': 4, 'Sáb': 5, 'Dom': 6
}

def load_data():
    data = {
        "todos": [],
        "notes": [],
        "config": {
            "last_daily_reset": None,
            "daily_reset_time": "00:00"
        }
    }
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                loaded = json.load(f)

                # Migração: se notes for string, converte para lista
                if isinstance(loaded.get('notes'), str):
                    loaded['notes'] = [{"id": 1, "text": loaded['notes'], "status": "active"}] if loaded['notes'].strip() else []

                # Migração: se todos for dicionário (estrutura antiga), converte para lista
                if isinstance(loaded.get('todos'), dict):
                    old_todos = loaded['todos']
                    new_todos = []

                    # Converte tarefas diárias
                    for task in old_todos.get('diariamente', []):
                        new_todos.append({
                            'text': task.get('text', ''),
                            'done': task.get('done', False),
                            'dueDate': None,
                            'recurrence': {'type': 'daily'},
                            'created': get_now().isoformat()
                        })

                    # Converte tarefas semanais
                    for task in old_todos.get('semanalmente', []):
                        new_todos.append({
                            'text': task.get('text', ''),
                            'done': task.get('done', False),
                            'dueDate': None,
                            'recurrence': {'type': 'weekly'},
                            'created': get_now().isoformat()
                        })

                    # Converte tarefas eventuais
                    for task in old_todos.get('eventualmente', []):
                        new_todos.append({
                            'text': task.get('text', ''),
                            'done': task.get('done', False),
                            'dueDate': None,
                            'recurrence': None,
                            'created': get_now().isoformat()
                        })

                    loaded['todos'] = new_todos

                data.update(loaded)

                # Garante que config existe
                if 'config' not in data:
                    data['config'] = {"last_daily_reset": None, "daily_reset_time": "00:00"}
            except json.JSONDecodeError:
                pass
    return data

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def should_reset_daily(last_reset_date):
    """Verifica se deve resetar tarefas diárias."""
    if not last_reset_date:
        return True

    today = get_now().date().isoformat()
    return last_reset_date != today

def should_reset_weekly(task, last_reset_date):
    """Verifica se deve resetar tarefa semanal."""
    if not last_reset_date:
        return True

    # Verifica se o dia da semana atual corresponde ao dia da tarefa
    today_weekday = get_now().weekday()
    task_weekday = WEEKDAY_MAP.get(task.get('due_day'))

    if task_weekday is None:
        return False

    # Se hoje é o dia correto e ainda não resetou hoje
    today = get_now().date().isoformat()
    return today_weekday == task_weekday and last_reset_date != today

def reset_todos(data):
    """Reseta tarefas com base na recorrência."""
    config = data.get('config', {})
    last_daily_reset = config.get('last_daily_reset')
    today = get_now().date()
    today_str = today.isoformat()

    for task in data.get('todos', []):
        recurrence = task.get('recurrence')

        if not recurrence or not task.get('done'):
            continue

        # Reset diário
        if recurrence.get('type') == 'daily':
            if task.get('dueDate'):
                # Parse da data de conclusão
                due_parts = task['dueDate'].split('/')
                if len(due_parts) == 3:
                    due_day, due_month, due_year = due_parts
                    due_date = datetime(int(due_year), int(due_month), int(due_day), tzinfo=BRT).date()

                    # Se a data passou, reseta e atualiza para hoje
                    if due_date < today:
                        task['done'] = False
                        task['dueDate'] = today.strftime('%d/%m/%Y')
                        task['last_reset'] = today_str

        # Reset semanal
        elif recurrence.get('type') == 'weekly':
            if task.get('dueDate'):
                # Parse da data de conclusão
                due_parts = task['dueDate'].split('/')
                if len(due_parts) == 3:
                    due_day, due_month, due_year = due_parts
                    due_date = datetime(int(due_year), int(due_month), int(due_day), tzinfo=BRT).date()

                    # Se a data passou, reseta e adiciona 7 dias
                    if due_date < today:
                        task['done'] = False
                        new_due_date = due_date + timedelta(days=7)
                        task['dueDate'] = new_due_date.strftime('%d/%m/%Y')
                        task['last_reset'] = today_str

        # Reset customizado (a cada X dias)
        elif recurrence.get('type') == 'custom':
            days_interval = recurrence.get('days', 1)

            if task.get('dueDate'):
                # Parse da data de conclusão
                due_parts = task['dueDate'].split('/')
                if len(due_parts) == 3:
                    due_day, due_month, due_year = due_parts
                    due_date = datetime(int(due_year), int(due_month), int(due_day), tzinfo=BRT).date()

                    # Se a data passou, reseta e adiciona X dias
                    if due_date < today:
                        task['done'] = False
                        new_due_date = due_date + timedelta(days=days_interval)
                        task['dueDate'] = new_due_date.strftime('%d/%m/%Y')
                        task['last_reset'] = today_str

    if should_reset_daily(last_daily_reset):
        config['last_daily_reset'] = today_str

    data['config'] = config
    return data

@dashboard_bp.route('/')
def index():
    days, silver = jogo_hoje()
    data = load_data()
    data = reset_todos(data)
    save_data(data)
    return render_template('dashboard.html', silver=silver, todos=data.get('todos'), notes=data.get('notes'))

@dashboard_bp.route('/api/save', methods=['POST'])
def save():
    data = request.json
    save_data(data)
    return jsonify({"status": "success"})

@dashboard_bp.route('/api/check_resets', methods=['GET'])
def check_resets():
    """Verifica e retorna tarefas que precisam ser resetadas."""
    data = load_data()
    data = reset_todos(data)
    save_data(data)
    return jsonify({"todos": data.get('todos', [])})
