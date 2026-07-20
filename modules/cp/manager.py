import os
import json
from datetime import datetime

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

# Level Table and CP Table will be loaded in the class
LEVEL_TABLE_RAW = """Iniciante 1	400	100
Iniciante 2	600	500
Iniciante 3	1.200	1.100
Iniciante 4	1.900	2.300
Iniciante 5	2.900	4.200
Iniciante 6	4.000	7.100
Iniciante 7	5.400	11.100
Iniciante 8	6.900	16.500
Iniciante 9	8.600	23.400
Iniciante 10	10.600	32.000
Aprendiz 1	13.100	42.600
Aprendiz 2	15.900	55.700
Aprendiz 3	18.800	71.600
Aprendiz 4	22.000	90.400
Aprendiz 5	25.400	112.400
Aprendiz 6	29.100	137.800
Aprendiz 7	33.000	166.900
Aprendiz 8	37.100	199.900
Aprendiz 9	41.500	237.000
Aprendiz 10	46.100	278.500
Proficiente 1	52.300	324.600
Proficiente 2	58.800	376.900
Proficiente 3	65.600	435.700
Proficiente 4	72.700	501.300
Proficiente 5	80.100	574.000
Proficiente 6	87.800	654.100
Proficiente 7	95.800	741.900
Proficiente 8	104.100	837.700
Proficiente 9	117.400	941.800
Proficiente 10	131.200	1.059.200
Profissional 1	150.200	1.190.400
Profissional 2	174.600	1.340.600
Profissional 3	204.600	1.515.200
Profissional 4	245.100	1.719.800
Profissional 5	296.500	1.964.900
Profissional 6	363.900	2.261.400
Profissional 7	452.600	2.625.300
Profissional 8	568.100	3.077.900
Profissional 9	720.800	3.646.000
Profissional 10	873.600	4.366.800
Artesão 1	1.074.400	5.240.400
Artesão 2	1.339.100	6.314.800
Artesão 3	1.641.000	7.653.900
Artesão 4	1.990.900	9.294.900
Artesão 5	2.452.600	11.285.800
Artesão 6	3.015.300	13.738.400
Artesão 7	3.663.100	16.753.700
Artesão 8	4.470.600	20.416.800
Artesão 9	5.490.800	24.887.400
Artesão 10	6.511.100	30.378.200
Mestre 1	7.536.500	36.889.300
Mestre 2	8.567.100	44.425.800
Mestre 3	9.603.000	52.992.900
Mestre 4	10.644.300	62.595.900
Mestre 5	11.691.100	73.240.200
Mestre 6	12.743.500	84.931.300
Mestre 7	13.801.600	97.674.800
Mestre 8	14.865.500	111.476.400
Mestre 9	15.935.300	126.341.900
Mestre 10	17.011.100	142.277.200
Mestre 11	18.093.000	159.288.300
Mestre 12	19.181.100	177.381.300
Mestre 13	20.275.500	196.562.400
Mestre 14	21.376.300	216.837.900
Mestre 15	22.483.600	238.214.200
Mestre 16	23.597.500	260.697.800
Mestre 17	24.718.100	284.295.300
Mestre 18	25.845.500	309.013.400
Mestre 19	26.979.800	334.858.900
Mestre 20	28.121.100	361.838.700
Mestre 21	29.269.500	389.959.800
Mestre 22	30.425.100	419.229.300
Mestre 23	31.588.000	449.654.400
Mestre 24	32.758.300	481.242.400
Mestre 25	33.936.100	514.000.700
Mestre 26	35.121.500	547.936.800
Mestre 27	36.314.600	583.058.300
Mestre 28	37.515.500	619.372.900
Mestre 29	38.724.300	656.888.400
Mestre 30	39.941.100	695.612.700
Guru 1	41.166.000	735.553.800
Guru 2	42.399.100	776.719.800
Guru 3	43.640.500	819.118.900
Guru 4	44.890.300	862.759.400
Guru 5	46.148.600	907.649.700
Guru 6	47.415.500	953.798.300
Guru 7	48.691.100	1.001.213.800
Guru 8	49.975.500	1.049.904.900
Guru 9	51.268.800	1.099.880.400
Guru 10	52.571.100	1.151.149.200
Guru 11	53.882.500	1.203.720.300
Guru 12	55.203.100	1.257.602.800
Guru 13	56.533.000	1.312.805.900
Guru 14	57.872.300	1.369.338.900
Guru 15	59.221.100	1.427.211.200
Guru 16	60.579.500	1.486.432.300
Guru 17	61.947.600	1.547.011.800
Guru 18	63.325.500	1.608.959.400
Guru 19	64.713.300	1.672.284.900
Guru 20	66.101.100	1.736.998.200
Guru 21	74.694.200	1.803.099.300
Guru 22	84.404.400	1.877.793.500
Guru 23	95.377.000	1.962.197.900
Guru 24	107.776.000	2.057.574.900
Guru 25	121.786.900	2.165.350.900
Guru 26	137.619.200	2.287.137.800
Guru 27	155.509.700	2.424.757.000
Guru 28	175.726.000	2.580.266.700
Guru 29	198.570.400	2.755.992.700
Guru 30	224.384.600	2.954.563.100
Guru 31	253.554.600	3.178.947.700
Guru 32	286.516.700	3.432.502.300
Guru 33	323.763.900	3.719.019.000
Guru 34	365.853.200	4.042.782.900
Guru 35	413.414.100	4.408.636.100
Guru 36	467.157.900	4.822.050.200
Guru 37	527.888.400	5.289.208.100
Guru 38	596.513.900	5.817.096.500
Guru 39	674.060.700	6.413.610.400
Guru 40	761.688.600	7.087.671.100
Guru 41	860.708.100	7.849.359.700
Guru 42	972.600.200	8.710.067.800
Guru 43	1.099.038.200	9.682.668.000
Guru 44	1.241.913.200	10.781.706.200
Guru 45	1.403.361.900	12.023.619.400
Guru 46	1.585.798.900	13.426.981.300
Guru 47	1.791.952.800	15.012.780.200
Guru 48	2.024.906.700	16.804.733.000
Guru 49	2.288.144.600	18.829.639.700
Guru 50	2.585.603.400	21.117.784.300
Guru 51	2.921.731.800	23.703.387.700
Guru 52	3.301.556.900	26.625.119.500
Guru 53	3.730.759.300	29.926.676.400
Guru 54	4.215.758.000	33.657.435.700
Guru 55	4.763.806.500	37.873.193.700
Guru 56	5.383.101.300	42.637.000.200
Guru 57	6.082.904.500	48.020.101.500
Guru 58	6.873.682.100	54.103.006.000
Guru 59	7.767.260.800	60.976.688.100
Guru 60	8.777.004.700	68.743.948.900
Guru 61	9.918.015.300	77.520.953.600
Guru 62	11.207.357.300	87.438.968.900
Guru 63	12.664.313.700	98.646.326.200
Guru 64	14.310.674.500	111.310.639.900
Guru 65	16.171.062.200	125.621.314.400
Guru 66	18.273.300.300	141.792.376.600
Guru 67	20.648.829.300	160.065.676.900
Guru 68	23.333.177.100	180.714.506.200
Guru 69	26.366.490.100	204.047.683.300
Guru 70	29.794.133.800	230.414.173.400
Guru 71	33.667.371.200	260.208.307.200
Guru 72	38.044.129.500	293.875.678.400
Guru 73	42.989.866.300	331.919.807.900
Guru 74	48.578.548.900	374.909.674.200
Guru 75	54.893.760.300	423.488.223.100
Guru 76	62.029.949.100	478.381.983.400
Guru 77	70.093.842.500	540.411.932.500
Guru 78	79.206.042.000	610.505.775.000
Guru 79	89.502.827.500	689.711.817.000
Guru 80	101.138.195.100	779.214.644.500
Guru 81	114.286.160.500	880.352.839.600
Guru 82	129.143.361.400	994.639.000.100
Guru 83	145.931.998.400	1.123.782.361.500
Guru 84	164.903.158.200	1.269.714.359.900
Guru 85	186.340.568.800	1.434.617.518.100
Guru 86	210.564.842.700	1.620.958.086.900
Guru 87	237.938.272.300	1.831.522.929.600
Guru 88	268.870.247.700	2.069.461.201.900
Guru 89	303.823.379.900	2.338.331.449.600
Guru 90	343.320.419.300	2.642.154.829.500
Guru 91	387.952.073.800	2.985.475.248.800
Guru 92	438.385.843.400	3.373.427.322.600
Guru 93	495.376.003.000	3.811.813.166.000
Guru 94	559.774.883.400	4.307.189.169.000
Guru 95	632.545.618.200	4.866.964.052.400
Guru 96	714.776.548.600	5.499.509.670.600
Guru 97	807.697.499.900	6.214.286.219.200
Guru 98	912.698.174.900	7.021.983.719.100
Guru 99	1.031.348.937.600	7.934.681.894.000
Guru 100	1.165.424.299.500	8.966.030.831.600"""

CP_TABLE_RAW = """0-50	1.1
50-75	1.4
75-100	1.8
100-125	2.3
125-150	3.0
150-175	3.9
175-200	5.1
200-225	7.1
225-250	10.0
250-275	15.0
275-300	22.5
300-325	56.2
325-350	101.1
350-375	252.9
375-400	455.2
400-425	1137.9
425-450	2048.3
450-475	3072.4
475-500	4608.6
500-525	6351.0
525-550	10161.7
550-575	16258.7
575-600	26013.9
600-650	41622.2"""

BASE_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

class CPManager:
    def __init__(self):
        self.level_db = self._parse_level_table()
        self.cp_db = self._parse_cp_table()
        self.data = self._load_data()

    def _parse_level_table(self):
        levels = []
        for line in LEVEL_TABLE_RAW.split("\n"):
            parts = line.split("\t")
            if len(parts) >= 3:
                name = parts[0].strip()
                try:
                    next_req = int(parts[1].replace(".", "").strip())
                    total_xp = int(parts[2].replace(".", "").strip())
                    levels.append({
                        "name": name, 
                        "next_req": next_req, 
                        "total_xp": total_xp
                    })
                except ValueError:
                    continue
        return levels

    def _parse_cp_table(self):
        cp_ranges = []
        for line in CP_TABLE_RAW.split("\n"):
            parts = line.split("\t")
            if len(parts) >= 2: 
                try:
                    bracket_str = parts[0].strip()
                    range_parts = bracket_str.split("-")
                    start = int(range_parts[0])
                    end = int(range_parts[1])
                    cost = float(parts[1].strip())
                    
                    cp_ranges.append({
                        "start": start,
                        "end": end,
                        "raw_cost": cost
                    })
                except ValueError:
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
