from flask import Blueprint, render_template, jsonify, request
import os
from .manager import CPManager, ITEMS_DATA
from .ocr_reader import ocr_from_image, ocr_inventory_from_image

cp_bp = Blueprint('cp', __name__, 
                  template_folder='templates', 
                  static_folder='static')

manager = CPManager()

@cp_bp.route('/')
def index():
    return render_template('cp_index.html', items_data=ITEMS_DATA)

@cp_bp.route('/api/data')
def get_data():
    return jsonify(manager.data)

@cp_bp.route('/api/calculate', methods=['POST'])
def calculate():
    req_data = request.json
    quantities = req_data.get('items', {})
    ignored_items = req_data.get('ignored_items', [])
    current_cp = req_data.get('user_cp', 0)
    current_cp_pct = req_data.get('user_cp_pct', 0.0)
    
    # Calculate gains
    gains = manager.calculate_gains(quantities, ignored_items)
    
    # Simulate CP advance
    projection = manager.simulate_cp_advance(current_cp, current_cp_pct, quantities, ignored_items)
    
    # Calculate missing for goal
    goal_cp = manager.data.get('goal_cp', 600)
    missing_goal = manager.calculate_missing_for_goal(current_cp, current_cp_pct, goal_cp)
    
    # Life Skill Simulations
    professions_status = req_data.get('professions', {})
    prof_advancement = []
    
    seen_profs = set()
    for item_key, item_info in ITEMS_DATA.items():
        prof = item_info['profession']
        if prof in seen_profs:
            continue
        seen_profs.add(prof)
        
        gained_xp = gains['prof_exp'].get(prof, 0)
        status = professions_status.get(prof, {"level": "Iniciante 1", "pct": 0.0})
        start_xp = manager.get_xp_from_level(status['level'], status['pct'])
        final_xp = start_xp + gained_xp
        
        new_level, new_pct = manager.find_level_by_xp(final_xp)
        
        prof_advancement.append({
            "profession": prof,
            "gained_xp": gained_xp,
            "start_level": status['level'],
            "start_pct": status['pct'],
            "final_level": new_level['name'],
            "final_pct": new_pct
        })

    return jsonify({
        "gains": gains,
        "projection": projection,
        "goal_cp": goal_cp,
        "missing_goal": missing_goal,
        "prof_advancement": prof_advancement
    })

@cp_bp.route('/api/ocr', methods=['POST'])
def ocr_scan():
    """Receive an uploaded screenshot of BDO life skills, run OCR to extract profession levels."""
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "Nenhuma imagem enviada"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"success": False, "error": "Arquivo vazio"}), 400
    try:
        image_bytes = file.read()
        result = ocr_from_image(image_bytes)
        if result["success"]:
            profs_dict = {}
            for p in result["data"]:
                profs_dict[p["profession"]] = {"level": p["level"], "pct": p["pct"]}
            result["data_dict"] = profs_dict
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@cp_bp.route('/api/ocr-inventory', methods=['POST'])
def ocr_inventory():
    """OCR endpoint for inventory/subproduct quantities."""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
    
    try:
        image_file = request.files['image']
        image_bytes = image_file.read()
        result = ocr_inventory_from_image(image_bytes)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@cp_bp.route('/api/save', methods=['POST'])
def save():
    req_data = request.json
    manager.save_data(req_data)
    return jsonify({"success": True})
