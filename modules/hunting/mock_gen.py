import os
import sys
import json
import random
from datetime import date, timedelta, datetime
sys.path.append(r'c:\Users\Lúcio\Projetos\bdo\hunting')
from manager import HuntingManager

app = HuntingManager(test_mode=True)
history = []

# Etapa 1: 01/05 a 31/05
start_date_1 = date(2026, 5, 1)
end_date_1 = date(2026, 5, 31)

exp_inicio_1 = app.get_absolute_exp("Guru 1", 0.0)
exp_fim_1 = app.get_absolute_exp("Guru 50", 0.0)
exp_total_1 = exp_fim_1 - exp_inicio_1

work_days_1 = app.calculate_working_days(start_date_1, end_date_1)
exp_per_day_1 = exp_total_1 / len(work_days_1)

current_exp = exp_inicio_1

curr_date = start_date_1
while curr_date <= end_date_1:
    if app.is_working_day(curr_date):
        current_exp += exp_per_day_1
        
        # Acha o nivel e % exatos
        t_nivel = "Guru 1"
        t_pct = 0.0
        for i in range(1, 51):
            n = f"Guru {i}"
            nx = f"Guru {i+1}" if i < 50 else "Guru 50"
            en = app.get_absolute_exp(n, 0.0)
            if i == 50:
                if current_exp >= en:
                    t_nivel = "Guru 50"
                    t_pct = 0.0
                break
            enx = app.get_absolute_exp(nx, 0.0)
            if en <= current_exp < enx:
                t_nivel = n
                t_pct = ((current_exp - en) / (enx - en)) * 100
                break
        
        history.append({
            "data": curr_date.strftime("%Y-%m-%d"),
            "nivel": t_nivel,
            "porcentagem": t_pct,
            "exp_absoluta": current_exp
        })
    else:
        # Simulando uma cacada numa folga pra mostrar a funcionalidade! (dia 07/05 eh quinta)
        if curr_date == date(2026, 5, 7):
            current_exp += (exp_per_day_1 * 0.5) # farmou metade do normal
            history.append({
                "data": curr_date.strftime("%Y-%m-%d"),
                "nivel": "Guru 10",
                "porcentagem": 0.0,
                "exp_absoluta": current_exp
            })
            
    curr_date += timedelta(days=1)


# Etapa 2: 01/06 a 15/09 (ate a data do mock)
start_date_2 = date(2026, 6, 1)
end_date_2 = date(2027, 4, 17)
hoje_mock = date(2026, 9, 15)

exp_inicio_2 = app.get_absolute_exp("Guru 50", 0.0)
exp_fim_2 = app.get_absolute_exp("Guru 72", 0.0)
exp_total_2 = exp_fim_2 - exp_inicio_2

work_days_2 = app.calculate_working_days(start_date_2, end_date_2)
exp_per_day_2 = exp_total_2 / len(work_days_2)

curr_date = start_date_2
missed_days = 0

# Randomizar de leve
random.seed(42)

while curr_date <= hoje_mock:
    if app.is_working_day(curr_date):
        # Simula alguns dias que esquecemos de farmar
        if curr_date in [date(2026, 7, 20), date(2026, 7, 21), date(2026, 8, 10)]:
            missed_days += 1
        else:
            daily_gain = exp_per_day_2 * random.uniform(0.9, 1.1)
            
            # Recupera os dias perdidos aos poucos
            if missed_days > 0:
                daily_gain += (exp_per_day_2 * 1.5) # Farma um monte extra pra compensar
                missed_days -= 1
                
            current_exp += daily_gain
            
            t_nivel = "Guru 50"
            t_pct = 0.0
            for i in range(50, 72):
                n = f"Guru {i}"
                nx = f"Guru {i+1}" if i < 71 else "Guru 72"
                en = app.get_absolute_exp(n, 0.0)
                enx = app.get_absolute_exp(nx, 0.0)
                if i == 71 and current_exp >= enx:
                    t_nivel = "Guru 72"
                    t_pct = 0.0
                    break
                if en <= current_exp < enx:
                    t_nivel = n
                    t_pct = ((current_exp - en) / (enx - en)) * 100
                    break
            
            history.append({
                "data": curr_date.strftime("%Y-%m-%d"),
                "nivel": t_nivel,
                "porcentagem": t_pct,
                "exp_absoluta": current_exp
            })
    curr_date += timedelta(days=1)

with open('historico_teste.json', 'w', encoding='utf-8') as f:
    json.dump(history, f, indent=4)
    
print(f"Mocked {len(history)} calendar entries into historico_teste.json")
