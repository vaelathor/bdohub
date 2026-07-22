import os
import csv
import json
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
LEVEL_TABLE_PATH = os.path.join(BASE_DIR, "data", "level_table.tsv")
CP_TABLE_PATH = os.path.join(BASE_DIR, "data", "cp_table.tsv")

# Item Definitions
ITEMS_DATA = {
    "Suspiro de Fada": {"profession": "Coleta", "req": 10, "icon": "leaf"},
    "Garrafa de Vidro Descartada": {"profession": "Pesca", "req": 5, "icon": "waves"},
    "Estrela Silvestre": {"profession": "Caça", "req": 10, "icon": "target"},
    "Iguarias de Bruxa": {"profession": "Culinária", "req": 10, "icon": "utensils"},
    "Catalisador Desconhecido": {"profession": "Alquimia", "req": 10, "icon": "flask-conical"},
    "Folha Rosa": {"profession": "Cultivo", "req": 20, "icon": "sprout"},
}

CP_PER_DELIVERY = 900
PROF_EXP_PER_DELIVERY = 30000

class CPManager:
    def __init__(self):
        self.level_db = self._parse_level_table()
        self.cp_db = self._parse_cp_table()
        self.data = self._load_data()

    def _read_tsv(self, path):
        """Read a TSV file and return rows as list of dicts."""
        rows = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                rows.append(row)
        return rows

    def _parse_level_table(self):
        levels = []
        for row in self._read_tsv(LEVEL_TABLE_PATH):
            name = row.get("level", "").strip()
            try:
                next_req = int(row.get("next_req", "0").replace(".", ""))
                total_xp = int(row.get("total_xp", "0").replace(".", ""))
                levels.append({
                    "name": name,
                    "next_req": next_req,
                    "total_xp": total_xp
                })
            except (ValueError, KeyError):
                continue
        return levels

    def _parse_cp_table(self):
        cp_ranges = []
        for row in self._read_tsv(CP_TABLE_PATH):
            bracket_str = row.get("cp_range", "").strip()
            try:
                range_parts = bracket_str.split("-")
                start = int(range_parts[0])
                end = int(range_parts[1])
                cost = float(row.get("cost", "0"))
                cp_ranges.append({
                    "start": start,
                    "end": end,
                    "raw_cost": cost
                })
            except (ValueError, IndexError, KeyError):
                continue
        return cp_ranges

    def _load_data(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        
        # Default data
        return {
            "items": {item: 0 for item in ITEMS_DATA},
            "user_cp": 0,
            "user_cp_pct": 0.0,
            "goal_cp": 600,
            "professions": {} # Stores current level and % for each
        }

    def save_data(self, data):
        # Merge incoming data with current to ensure goal_cp is preserved if not sent
        new_data = self.data.copy()
        new_data.update(data)
        self.data = new_data
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def calculate_gains(self, quantities, ignored_items=None):
        if ignored_items is None: ignored_items = []
        total_cp_xp = 0
        prof_exp = {}
        items_summary = []

        for item, qty in quantities.items():
            if item not in ITEMS_DATA or item in ignored_items: continue
            
            data = ITEMS_DATA[item]
            deliveries = qty // data["req"]
            cp_gain = deliveries * CP_PER_DELIVERY
            exp_gain = deliveries * PROF_EXP_PER_DELIVERY
            
            total_cp_xp += cp_gain
            prof = data["profession"]
            prof_exp[prof] = prof_exp.get(prof, 0) + exp_gain
            
            items_summary.append({
                "name": item,
                "qty": qty,
                "deliveries": deliveries,
                "cp_xp": cp_gain,
                "prof_xp": exp_gain,
                "profession": prof,
                "icon": data["icon"]
            })
            
        return {
            "total_cp_xp": total_cp_xp,
            "prof_exp": prof_exp,
            "items": items_summary
        }

    def simulate_cp_advance(self, current_cp, current_pct, quantities, ignored_items=None):
        if ignored_items is None: ignored_items = []
        # Calculate Total Deliveries
        total_deliveries = 0
        for item, qty in quantities.items():
            if item in ITEMS_DATA and item not in ignored_items:
                total_deliveries += qty // ITEMS_DATA[item]["req"]

        remaining = float(total_deliveries)
        sim_cp = current_cp
        sim_pct = current_pct
        
        # Handle first partial point
        range_cost = self._get_cp_cost(sim_cp)
        if range_cost > 0:
            cost_in_del = range_cost / 10.0
            already_filled = cost_in_del * (sim_pct / 100.0)
            needed = cost_in_del - already_filled
            
            if remaining >= needed:
                remaining -= needed
                sim_cp += 1
                sim_pct = 0.0
            else:
                added_pct = (remaining / cost_in_del) * 100.0
                sim_pct += added_pct
                remaining = 0

        # Subsequent points
        while remaining > 0 and sim_cp < 650:
            range_cost = self._get_cp_cost(sim_cp)
            if range_cost == 0: break
            
            cost_in_del = range_cost / 10.0
            if remaining >= cost_in_del:
                remaining -= cost_in_del
                sim_cp += 1
            else:
                sim_pct = (remaining / cost_in_del) * 100.0
                remaining = 0
                break
                
        return {
            "final_cp": sim_cp,
            "final_pct": round(sim_pct, 2),
            "total_deliveries": total_deliveries
        }

    def _get_cp_cost(self, cp):
        for r in self.cp_db:
            if r['start'] <= cp < r['end']:
                return r['raw_cost']
        return 0

    def find_level_by_xp(self, target_xp):
        current_best = self.level_db[0]
        if target_xp < current_best['total_xp']:
            return current_best, 0.0

        for lvl in self.level_db:
            if lvl['total_xp'] <= target_xp:
                current_best = lvl
            else:
                break
                
        xp_in_level = target_xp - current_best['total_xp']
        if current_best['next_req'] > 0:
            percentage = (xp_in_level / current_best['next_req']) * 100
        else:
            percentage = 100.0
            
        return current_best, round(percentage, 2)

    def get_xp_from_level(self, level_name, pct):
        target = None
        for lvl in self.level_db:
            if lvl['name'].lower() == level_name.lower():
                target = lvl
                break
        
        if not target: return 0
        return target['total_xp'] + (target['next_req'] * (pct / 100.0))

    def calculate_missing_for_goal(self, start_cp, start_pct, goal_cp):
        if start_cp >= goal_cp: return 0
        
        needed_deliveries = 0
        
        # First partial
        cost = self._get_cp_cost(start_cp)
        if cost > 0:
            cost_del = cost / 10.0
            needed_deliveries += cost_del * (1 - (start_pct / 100.0))
            
        curr = start_cp + 1
        while curr < goal_cp:
            cost = self._get_cp_cost(curr)
            if cost == 0: break
            needed_deliveries += (cost / 10.0)
            curr += 1
            
        return int(needed_deliveries)
