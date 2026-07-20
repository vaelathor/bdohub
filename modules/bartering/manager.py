import csv
import os
import math

class BarteringManager:
    def __init__(self, data_csv_path, session_csv_path):
        self.data_csv_path = data_csv_path
        self.session_csv_path = session_csv_path
        self.levels_map = {}
        self.base_costs = {}
        self.load_data_table()

    def parse_float(self, value):
        if not value: return 0.0
        try:
            clean_val = value.replace('%', '').replace('"', '').replace('.', '').replace(',', '.')
            return float(clean_val) / 100.0
        except ValueError:
            return 0.0

    def parse_int(self, value):
        if not value: return 0
        try:
            clean_val = str(value).replace('.', '').replace(',', '').replace('"', '')
            return int(clean_val)
        except ValueError:
            return 0

    def load_data_table(self):
        if not os.path.exists(self.data_csv_path): return
        with open(self.data_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) > 1 and row[0] and row[1]:
                    # Usamos strip() para evitar erros com espaços invisíveis no CSV
                    self.base_costs[row[0].strip()] = self.parse_int(row[1])
                if len(row) > 4 and row[3] and row[4]:
                    lvl_name = row[3].replace('. ', ' ').strip()
                    self.levels_map[lvl_name] = self.parse_float(row[4])

    def calculate_costs(self, level_name, has_vp, has_cleia, current_bargain_str, trades_dict=None):
        if trades_dict is None: trades_dict = {}
        
        lvl_discount = self.levels_map.get(level_name, 0.0)
        vp_bonus = 0.10 if has_vp else 0.0
        cleia_bonus = 0.10 if has_cleia else 0.0 
        total_discount = lvl_discount + vp_bonus + cleia_bonus
        
        bargain_total = self.parse_int(current_bargain_str)
        
        results = []
        final_costs_map = {}
        total_bargain_used_by_list = 0
        
        # Criamos a lista baseada na ordem do CSV (usando enumerate para guardar a ordem original)
        for i, (destino, base) in enumerate(self.base_costs.items()):
            cost_final = int(base * (1 - total_discount))
            num_trocas = trades_dict.get(destino, 0)
            barganha_usada = num_trocas * cost_final
            
            total_bargain_used_by_list += barganha_usada
            
            results.append({
                "original_index": i,
                "destino": destino, 
                "base": base, 
                "final": cost_final,
                "num_trocas": num_trocas,
                "barganha_usada": barganha_usada
            })
            final_costs_map[destino] = cost_final

        # Ordenação: 
        # 1. Primeiro critério: 'is_priority' (0 para normal, 1 para as que vão pro final)
        # 2. Segundo critério: 'original_index' (mantém a ordem do CSV para as demais)
        priority_routes = ["T4 > T5", "T5 > T6", "T6 > T7"]
        
        for r in results:
            r['is_priority'] = r['destino'].strip() in priority_routes

        results.sort(key=lambda x: (x['is_priority'], x['original_index']))
            
        # Nova Lógica: Subtrai o gasto da lista da barganha total
        bargain_liquida = bargain_total - total_bargain_used_by_list
        if bargain_liquida < 0: bargain_liquida = 0
            
        # Cálculos de Permutas Restantes baseados na Barganha Líquida
        cost_t4t5 = final_costs_map.get("T4 > T5", 1)
        rem_itens = math.floor(bargain_liquida / cost_t4t5) if cost_t4t5 > 0 else 0
        
        cost_mat = final_costs_map.get("Material", 1)
        rem_mats = math.floor(bargain_liquida / cost_mat) if cost_mat > 0 else 0
        
        cost_coin = final_costs_map.get("Material (Moedas Corvo)", 1)
        rem_coins = math.floor(bargain_liquida / cost_coin) if cost_coin > 0 else 0
            
        return {
            "total_discount_pct": f"{(total_discount * 100):.2f}%".replace('.', ','),
            "level_bonus_pct": f"{(lvl_discount * 100):.2f}%".replace('.', ','),
            "costs": results,
            "rem_itens": rem_itens,
            "rem_mats": rem_mats,
            "rem_coins": rem_coins,
            "total_gasto_lista": total_bargain_used_by_list,
            "bargain_liquida": bargain_liquida
        }
