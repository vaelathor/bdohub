from flask import Blueprint, render_template, jsonify, request
import os
import sys

# Importa a classe do manager
from .manager import HuntingManager

hunting_bp = Blueprint('hunting', __name__, 
                       template_folder='templates', 
                       static_folder='static')

# O manager será instanciado na execução principal baseada nos argumentos
manager = None

def init_manager(test_mode=False):
    global manager
    manager = HuntingManager(test_mode=test_mode)

@hunting_bp.route('/')
def index():
    return render_template('hunting_index.html', test_mode=manager.test_mode)

@hunting_bp.route('/calendar')
def full_calendar():
    # Obtém a etapa atual para saber o período total
    hoje = manager.get_today()
    etapa = manager.get_stage_for_date(hoje)
    
    if not etapa:
        return "Nenhuma etapa ativa no momento para mostrar o calendário.", 404
        
    from datetime import datetime
    start = datetime.strptime(etapa['data_inicio'], "%Y-%m-%d").date()
    end = datetime.strptime(etapa['data_fim'], "%Y-%m-%d").date()
    
    # Lista de meses na etapa (ano, mes)
    meses = []
    current_y = start.year
    current_m = start.month
    while current_y < end.year or (current_y == end.year and current_m <= end.month):
        meses.append((current_y, current_m))
        current_m += 1
        if current_m > 12:
            current_m = 1
            current_y += 1
            
    # Busca os dados de cada mês
    calendarios = []
    mes_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    for a, m in meses:
        dados_mes = manager.get_history_data(a, m)
        calendarios.append({
            "ano": a,
            "mes": m,
            "nome_mes": mes_nomes[m-1],
            "dados": dados_mes
        })
        
    return render_template('calendar.html', test_mode=manager.test_mode, etapa=etapa, calendarios=calendarios)

@hunting_bp.route('/api/status')
def api_status():
    data = manager.get_status_data()
    return jsonify(data)

@hunting_bp.route('/api/chart')
def api_chart():
    data = manager.get_chart_data()
    return jsonify(data)

@hunting_bp.route('/api/monthly_stats')
def api_monthly_stats():
    data = manager.get_monthly_stats()
    return jsonify(data)

@hunting_bp.route('/api/history')
def api_history():
    ano = request.args.get('ano', type=int)
    mes = request.args.get('mes', type=int)
    
    if not ano or not mes:
        hoje = manager.get_today()
        ano = hoje.year
        mes = hoje.month
        
    data = manager.get_history_data(ano, mes)
    return jsonify(data)

@hunting_bp.route('/api/progress', methods=['POST'])
def api_progress():
    req_data = request.json
    
    data_str = req_data.get('data')
    nivel = req_data.get('nivel')
    pct = req_data.get('pct')
    
    if not data_str or not nivel or pct is None:
        return jsonify({"error": "Dados incompletos"}), 400
        
    result = manager.add_progress(data_str, nivel, pct)
    return jsonify(result)

@hunting_bp.route('/api/progress/delete', methods=['POST'])
def api_progress_delete():
    req_data = request.json
    data_str = req_data.get('data')
    
    if not data_str:
        return jsonify({"error": "Data não informada"}), 400
        
    result = manager.delete_progress(data_str)
    if "error" in result:
        return jsonify(result), 400
        
    return jsonify(result)

@hunting_bp.route('/api/config/goal', methods=['POST'])
def api_config_goal():
    req_data = request.json
    data_fim = req_data.get('data_fim')
    nivel_fim = req_data.get('nivel_fim')

    if not data_fim or not nivel_fim:
        return jsonify({"error": "Dados incompletos"}), 400

    result = manager.update_goal(data_fim, nivel_fim)
    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

@hunting_bp.route('/api/config/stages', methods=['GET'])
def api_config_stages_get():
    """Retorna todas as etapas configuradas."""
    stages = manager.config.get('etapas', [])
    return jsonify({"stages": stages})

@hunting_bp.route('/api/config/stages', methods=['POST'])
def api_config_stages_post():
    """Atualiza todas as etapas."""
    req_data = request.json
    stages = req_data.get('stages')

    if not stages or not isinstance(stages, list):
        return jsonify({"error": "Dados de etapas inválidos"}), 400

    result = manager.update_stages(stages)
    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)

@hunting_bp.route('/api/day-details')
def api_day_details():
    data_str = request.args.get('data')
    if not data_str:
        return jsonify({"error": "Data não informada"}), 400
        
    result = manager.get_day_details(data_str)
    if "error" in result:
        return jsonify(result), 400
        
    return jsonify(result)
