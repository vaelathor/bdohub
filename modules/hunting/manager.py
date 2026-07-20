import os
import sys
import json
import csv
import argparse
from datetime import datetime, date, timedelta

# Habilita cores ANSI no Windows terminal
os.system('')
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Arquivos (agora relativos ao diretório deste arquivo)
BASE_DIR = os.path.dirname(__file__)
EXP_TABLE_FILE = os.path.join(BASE_DIR, 'tabela_exp.csv')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
HISTORY_FILE = os.path.join(BASE_DIR, 'historico.json')
HISTORY_FILE_TEST = os.path.join(BASE_DIR, 'historico_teste.json')

class HuntingManager:
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        self.history_file = HISTORY_FILE_TEST if test_mode else HISTORY_FILE
        self.exp_table = {}
        self.config = {}
        self.history = []
        self.load_data()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_today(self):
        if self.test_mode:
            # Simula que estamos em setembro na segunda etapa
            return date(2026, 9, 16)
        return date.today()

    def load_data(self):
        # Carregar config
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # Carregar historico
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

        # Carregar tabela de EXP
        if not os.path.exists(EXP_TABLE_FILE):
            print(f"Erro: Arquivo {EXP_TABLE_FILE} nao encontrado.")
            exit(1)
            
        with open(EXP_TABLE_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                nivel = row['Nivel'].strip()
                if not nivel:
                    continue
                try:
                    exp_por_nivel = int(row['Experiencia_por_nivel'])
                    exp_total = int(row['Total_de_Experiencia'])
                    self.exp_table[nivel] = {
                        'exp_por_nivel': exp_por_nivel,
                        'exp_total': exp_total
                    }
                except ValueError:
                    pass

    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

    def is_working_day(self, check_date):
        # Verifica datas especificas de folga
        if check_date.strftime("%Y-%m-%d") in self.config['folgas'].get('datas_especificas', []):
            return False

        # Verifica dia da semana (Quinta = 3)
        if check_date.weekday() in self.config['folgas'].get('dias_da_semana', []):
            return False

        # Verifica domingos alternados
        domingos_alt = self.config['folgas'].get('domingos_alternados', {})
        if domingos_alt.get('ativo', False) and check_date.weekday() == 6:
            ref_str = domingos_alt.get('domingo_trabalho_referencia')
            if ref_str:
                ref_date = datetime.strptime(ref_str, "%Y-%m-%d").date()
                diff_days = (check_date - ref_date).days
                weeks_diff = abs(diff_days) // 7
                # Se a diferenca for impar, o estado eh o inverso da referencia
                # Como a referencia eh de TRABALHO, impar = FOLGA (nao util)
                if weeks_diff % 2 != 0:
                    return False
        
        return True

    def get_stage_for_date(self, target_date):
        for etapa in self.config['etapas']:
            start = datetime.strptime(etapa['data_inicio'], "%Y-%m-%d").date()
            end = datetime.strptime(etapa['data_fim'], "%Y-%m-%d").date()
            if start <= target_date <= end:
                return etapa
        return None

    def calculate_working_days(self, start_date, end_date):
        current = start_date
        working_days = []
        while current <= end_date:
            if self.is_working_day(current):
                working_days.append(current)
            current += timedelta(days=1)
        return working_days

    def get_absolute_exp(self, nivel, porcentagem):
        if nivel not in self.exp_table:
            raise ValueError(f"Nivel '{nivel}' nao encontrado na tabela de exp.")
        base_exp = self.exp_table[nivel]['exp_total']
        exp_next = self.exp_table[nivel]['exp_por_nivel']
        
        # A % eh sobre a exp para o proximo nivel
        added_exp = int(exp_next * (porcentagem / 100.0))
        return base_exp + added_exp

    def exp_to_float_level(self, exp_abs):
        # Converte a exp crua em um nivel com casas decimais (ex: Guru 50, 50% = 50.5)
        for i in range(1, 100):
            n = f"Guru {i}"
            nx = f"Guru {i+1}"
            if n in self.exp_table and nx in self.exp_table:
                en = self.get_absolute_exp(n, 0.0)
                enx = self.get_absolute_exp(nx, 0.0)
                if en <= exp_abs < enx:
                    pct = (exp_abs - en) / (enx - en)
                    return float(i + pct)
        return 0.0

    def format_exp(self, exp):
        return f"{exp:,}".replace(',', '.')

    def get_progress_bar(self, current, total, length=40):
        if total <= 0: return f"[{'░' * length}] 0.00%"
        pct = max(0.0, min(100.0, (current / total) * 100))
        filled = int(length * (pct / 100))
        bar = '█' * filled + '░' * (length - filled)
        return f"[{bar}] {pct:.2f}%"

    def show_status(self):
        hoje = self.get_today()
        # Para testes ou para ver a meta real de hoje, se quiser pode mocar a data aqui, ex: hoje = date(2026, 5, 2)
        etapa = self.get_stage_for_date(hoje)
        
        if not etapa:
            print(f"A data atual ({hoje.strftime('%d/%m/%Y')}) não está dentro de nenhuma etapa configurada.")
            return

        print(f"\n{Colors.CYAN}{Colors.BOLD}========================================={Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD} Resumo da Etapa: {etapa['nome']}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}========================================={Colors.RESET}")
        
        start_date = datetime.strptime(etapa['data_inicio'], "%Y-%m-%d").date()
        end_date = datetime.strptime(etapa['data_fim'], "%Y-%m-%d").date()
        
        exp_inicio = self.get_absolute_exp(etapa['nivel_inicio'], 0.0)
        exp_fim = self.get_absolute_exp(etapa['nivel_fim'], 0.0)
        exp_total_meta = exp_fim - exp_inicio
        
        all_working_days = self.calculate_working_days(start_date, end_date)
        total_working_days = len(all_working_days)
        
        if total_working_days == 0:
            print("Nenhum dia util nesta etapa.")
            return
            
        exp_por_dia = exp_total_meta / total_working_days
        
        # Calcular meta atual
        # Dias uteis desde o inicio ate hoje (incluso)
        dias_passados = [d for d in all_working_days if d <= hoje]
        
        meta_atual_exp_abs = exp_inicio + (len(dias_passados) * exp_por_dia)
        
        print(f"Data de hoje......: {hoje.strftime('%d/%m/%Y')} ({'dia útil' if self.is_working_day(hoje) else 'folga'})")
        print(f"Progresso de tempo: {len(dias_passados)} dias úteis decorridos (de um total de {total_working_days} na etapa)")

        if self.history:
            ultimo_reg = self.history[-1]
            pct_fmt = f"{ultimo_reg['porcentagem']:.2f}".replace('.', ',')
            data_reg_br = datetime.strptime(ultimo_reg['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
            
            exp_atual_abs = ultimo_reg['exp_absoluta']
            delta = exp_atual_abs - meta_atual_exp_abs
            
            exp_ganha_etapa = max(0, exp_atual_abs - exp_inicio)
            
            print(f"\n{Colors.YELLOW}--> Seu Status Atual <--{Colors.RESET}")
            print(f"Último registro em {data_reg_br}:")
            print(f"{Colors.BOLD}Nível: {ultimo_reg['nivel']} | {pct_fmt}%{Colors.RESET}")
            print(f"Progresso da etapa: {self.get_progress_bar(exp_ganha_etapa, exp_total_meta)}")
            
            print(f"\n{Colors.YELLOW}-- Comparativo com a Meta --{Colors.RESET}")
            print(f"Meta ideal para hoje...: {self.format_exp(int(meta_atual_exp_abs))} Exp")
            print(f"Sua experiência atual..: {self.format_exp(int(exp_atual_abs))} Exp")
            print(f"Média exigida na etapa.: {self.format_exp(int(exp_por_dia))} Exp/dia útil")
            
            print(f"\n{Colors.BOLD}Veredito:{Colors.RESET}")
            if delta > 0:
                print(f"  {Colors.GREEN}[+] Adiantado em {self.format_exp(int(delta))} Exp.{Colors.RESET}")
                dias_adiantado = delta / exp_por_dia
                print(f"      (Aproximadamente {dias_adiantado:.1f} dias úteis adiantado)")
            elif delta < 0:
                dias_passados_ontem = [d for d in all_working_days if d < hoje]
                meta_ontem_exp_abs = exp_inicio + (len(dias_passados_ontem) * exp_por_dia)
                if exp_atual_abs >= meta_ontem_exp_abs:
                    print(f"  {Colors.YELLOW}[!] Pendente Hoje: Faltam {self.format_exp(int(abs(delta)))} Exp para atingir a meta do dia.{Colors.RESET}")
                else:
                    print(f"  {Colors.RED}[-] Atrasado em {self.format_exp(int(abs(delta)))} Exp.{Colors.RESET}")
                    dias_atrasado = abs(delta) / exp_por_dia
                    print(f"      (Aproximadamente {dias_atrasado:.1f} dias úteis atrasado)")
            else:
                print(f"  {Colors.CYAN}[=] Exatamente na meta ideal!{Colors.RESET}")
        else:
            print(f"\n-- Comparativo com a Meta --")
            print(f"Meta ideal para hoje...: {self.format_exp(int(meta_atual_exp_abs))} Exp")
            print("\nNenhum registro encontrado no histórico. Registre o progresso para ver o status.")

    def record_progress(self):
        print(f"\n{Colors.CYAN}--- Registrar Progresso ---{Colors.RESET}")
        hoje = self.get_today()
        hoje_str = hoje.strftime('%d/%m/%Y')
        
        # Obter dados de referencia (ultimo registro)
        if self.history:
            ultimo_reg = self.history[-1]
            pct_fmt = f"{ultimo_reg['porcentagem']:.2f}".replace('.', ',')
            data_reg_br = datetime.strptime(ultimo_reg['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
            
            # Ganho no ultimo dia
            idx = self.history.index(ultimo_reg)
            ganho = 0
            if idx > 0:
                ganho = ultimo_reg['exp_absoluta'] - self.history[idx-1]['exp_absoluta']
            
            # Verificar se foi acima ou abaixo da media exigida da etapa dele
            etapa_ref = self.get_stage_for_date(datetime.strptime(ultimo_reg['data'], "%Y-%m-%d").date())
            if etapa_ref:
                exp_inicio = self.get_absolute_exp(etapa_ref['nivel_inicio'], 0.0)
                exp_fim = self.get_absolute_exp(etapa_ref['nivel_fim'], 0.0)
                work_days = len(self.calculate_working_days(
                    datetime.strptime(etapa_ref['data_inicio'], "%Y-%m-%d").date(),
                    datetime.strptime(etapa_ref['data_fim'], "%Y-%m-%d").date()
                ))
                media_dia = (exp_fim - exp_inicio) / work_days if work_days > 0 else 0
                
                if ganho >= media_dia:
                    desempenho_plain = f"Acima ou na média (+ {self.format_exp(int(ganho - media_dia))} Exp)"
                else:
                    desempenho_plain = f"Abaixo da média (- {self.format_exp(int(media_dia - ganho))} Exp)"
            else:
                desempenho_plain = "N/A"

            print(f"{Colors.YELLOW}┌────────────────────────────────────────────────────────┐")
            print(f"│ Referência do Último Registro ({data_reg_br})".ljust(57) + "│")
            print(f"│ Nível Alcançado: {ultimo_reg['nivel']}".ljust(57) + "│")
            print(f"│ Porcentagem....: {pct_fmt}%".ljust(57) + "│")
            print(f"│ Exp Ganhos.....: + {self.format_exp(int(ganho))} Exp".ljust(57) + "│")
            print(f"│ Desempenho.....: {desempenho_plain[:40]}".ljust(57) + "│")
            print(f"└────────────────────────────────────────────────────────┘{Colors.RESET}")

        # Expectativa discreta para hoje
        etapa_hoje = self.get_stage_for_date(hoje)
        dica_str = ""
        if etapa_hoje:
            start_date = datetime.strptime(etapa_hoje['data_inicio'], "%Y-%m-%d").date()
            end_date = datetime.strptime(etapa_hoje['data_fim'], "%Y-%m-%d").date()
            exp_inicio = self.get_absolute_exp(etapa_hoje['nivel_inicio'], 0.0)
            exp_fim = self.get_absolute_exp(etapa_hoje['nivel_fim'], 0.0)
            all_working_days = self.calculate_working_days(start_date, end_date)
            exp_por_dia = (exp_fim - exp_inicio) / len(all_working_days) if all_working_days else 0
            
            dias_passados = [d for d in all_working_days if d <= hoje]
            meta_atual = exp_inicio + (len(dias_passados) * exp_por_dia)
            
            # Descobre o nivel equivalente da meta atual
            t_nivel = etapa_hoje['nivel_inicio']
            t_pct = 0.0
            
            # Procura de Guru 1 a Guru 100
            for i in range(1, 100):
                n = f"Guru {i}"
                nx = f"Guru {i+1}"
                if n in self.exp_table and nx in self.exp_table:
                    en = self.get_absolute_exp(n, 0.0)
                    enx = self.get_absolute_exp(nx, 0.0)
                    if en <= meta_atual < enx:
                        t_nivel = n
                        t_pct = ((meta_atual - en) / (enx - en)) * 100
                        break
            
            pct_dica = f"{t_pct:.2f}".replace('.', ',')
            dica_str = f"(Dica: A meta de hoje requer estar próximo a {t_nivel} com {pct_dica}%)"
            
        data_input = input(f"Data (DD/MM/YYYY) [Enter para {hoje_str}]: ").strip()
        if not data_input:
            data_reg = hoje.strftime("%Y-%m-%d")
        else:
            data_input = data_input.replace('-', '/')
            try:
                dt = datetime.strptime(data_input, "%d/%m/%Y")
                data_reg = dt.strftime("%Y-%m-%d")
            except ValueError:
                print("Data inválida! Use o formato DD/MM/YYYY.")
                return

        if dica_str:
            print(f"{Colors.MAGENTA}{dica_str}{Colors.RESET}")
            
        nivel = input("Nível (Ex: Guru 12): ").strip()
        if nivel not in self.exp_table:
            print("Nível não reconhecido. Verifique se digitou corretamente (ex: 'Guru 1', 'Mestre 10').")
            return

        pct_str = input("Porcentagem (Ex: 45,22): ").strip().replace(',', '.')
        try:
            pct = float(pct_str)
        except ValueError:
            print("Porcentagem inválida!")
            return

        exp_abs = self.get_absolute_exp(nivel, pct)

        registro = {
            "data": data_reg,
            "nivel": nivel,
            "porcentagem": pct,
            "exp_absoluta": exp_abs
        }

        # Atualiza o registro se for o mesmo dia, senao adiciona
        for idx, reg in enumerate(self.history):
            if reg['data'] == data_reg:
                self.history[idx] = registro
                print("Registro atualizado com sucesso!")
                break
        else:
            self.history.append(registro)
            # Ordena pelo data caso insira retroativo
            self.history.sort(key=lambda x: x['data'])
            print(f"{Colors.GREEN}Registro salvo com sucesso!{Colors.RESET}")

        self.save_history()

    def show_history(self):
        print(f"\n{Colors.CYAN}--- Histórico de Progresso (Visão Calendário) ---{Colors.RESET}")
        import calendar
        hoje = self.get_today()
        
        mes_ano_str = input(f"Ver qual mês/ano? (MM/YYYY) [Enter para {hoje.strftime('%m/%Y')}]: ").strip()
        if not mes_ano_str:
            mes_ref = hoje.month
            ano_ref = hoje.year
        else:
            try:
                dt_ref = datetime.strptime(mes_ano_str, "%m/%Y")
                mes_ref = dt_ref.month
                ano_ref = dt_ref.year
            except ValueError:
                print("Formato inválido. Use MM/YYYY.")
                return

        cal = calendar.monthcalendar(ano_ref, mes_ref)
        hist_dict = {reg['data']: reg for reg in self.history}
        
        def format_cell(dia):
            if dia == 0:
                return " " * 10, " " * 10
            
            data_atual = date(ano_ref, mes_ref, dia)
            data_str = data_atual.strftime("%Y-%m-%d")
            eh_util = self.is_working_day(data_atual)
            tem_registro = data_str in hist_dict
            
            if data_atual > hoje:
                # Futuro
                return f" {dia:02d} [ ]   ".ljust(10), " Futuro   ".ljust(10)
                
            if tem_registro:
                reg = hist_dict[data_str]
                pct_fmt = f"{reg['porcentagem']:.1f}%".replace('.', ',')
                # Encurta string como G50 10,5%
                niv_short = reg['nivel'].replace('Guru ', 'G').replace('Mestre ', 'M').replace('Artesao ', 'A').replace('Profissional ', 'P').replace('Aprendiz ', 'Ap').replace('Iniciante ', 'I')
                linha2 = f"{niv_short} {pct_fmt}"
                
                if eh_util:
                    l1 = f" {dia:02d} [X]   ".ljust(10)
                    l2 = f" {linha2}".ljust(10)[:10]
                    return f"{Colors.CYAN}{l1}{Colors.RESET}", f"{Colors.CYAN}{l2}{Colors.RESET}"
                else:
                    l1 = f" {dia:02d} [*]   ".ljust(10)
                    l2 = f" {linha2}".ljust(10)[:10]
                    return f"{Colors.GREEN}{l1}{Colors.RESET}", f"{Colors.GREEN}{l2}{Colors.RESET}"
            else:
                if eh_util:
                    l1 = f" {dia:02d} [ ]   ".ljust(10)
                    l2 = " Falta    ".ljust(10)
                    return f"{Colors.RED}{l1}{Colors.RESET}", f"{Colors.RED}{l2}{Colors.RESET}"
                else:
                    l1 = f" {dia:02d} [-]   ".ljust(10)
                    l2 = " Folga    ".ljust(10)
                    return f"{Colors.MAGENTA}{l1}{Colors.RESET}", f"{Colors.MAGENTA}{l2}{Colors.RESET}"

        print(f"\n{Colors.CYAN}{Colors.BOLD} Calendário Mensal: {mes_ref:02d}/{ano_ref}{Colors.RESET}")
        print(f"{Colors.YELLOW}+{'----------+' * 7}{Colors.RESET}")
        headers = ["   Seg    ", "   Ter    ", "   Qua    ", "   Qui    ", "   Sex    ", "   Sáb    ", "   Dom    "]
        print(f"{Colors.YELLOW}|{Colors.RESET}" + f"{Colors.YELLOW}|{Colors.RESET}".join(headers) + f"{Colors.YELLOW}|{Colors.RESET}")
        print(f"{Colors.YELLOW}+{'----------+' * 7}{Colors.RESET}")
        
        for week in cal:
            row1 = f"{Colors.YELLOW}|{Colors.RESET}"
            row2 = f"{Colors.YELLOW}|{Colors.RESET}"
            for dia in week:
                l1, l2 = format_cell(dia)
                row1 += l1 + f"{Colors.YELLOW}|{Colors.RESET}"
                row2 += l2 + f"{Colors.YELLOW}|{Colors.RESET}"
            print(row1)
            print(row2)
            print(f"{Colors.YELLOW}+{'----------+' * 7}{Colors.RESET}")
        print(f"\nLegenda: {Colors.CYAN}[X] Caça normal{Colors.RESET} | {Colors.MAGENTA}[-] Folga{Colors.RESET} | {Colors.RED}[ ] Faltou{Colors.RESET} | {Colors.GREEN}[*] Caçou na folga{Colors.RESET}\n")
        
    def show_graph(self):
        try:
            import plotext as plt
        except ImportError:
            print(f"{Colors.RED}O módulo 'plotext' não está instalado. Instale usando: pip install plotext{Colors.RESET}")
            return
            
        hoje = self.get_today()
        etapa = self.get_stage_for_date(hoje)
        if not etapa:
            print("Nenhuma etapa ativa no momento para gerar gráfico.")
            return
            
        print(f"\n{Colors.CYAN}--- Gráfico de Projeção da Etapa ---{Colors.RESET}")
        
        start_date = datetime.strptime(etapa['data_inicio'], "%Y-%m-%d").date()
        end_date = datetime.strptime(etapa['data_fim'], "%Y-%m-%d").date()
        
        exp_inicio = self.get_absolute_exp(etapa['nivel_inicio'], 0.0)
        exp_fim = self.get_absolute_exp(etapa['nivel_fim'], 0.0)
        
        all_working_days = self.calculate_working_days(start_date, end_date)
        if not all_working_days:
            print("Nenhum dia útil na etapa.")
            return
            
        exp_por_dia = (exp_fim - exp_inicio) / len(all_working_days)
        
        dates_str = []
        planned = []
        actual = []
        
        hist_dict = {datetime.strptime(r['data'], "%Y-%m-%d").date(): r['exp_absoluta'] for r in self.history}
        
        current = start_date
        current_planned_exp = exp_inicio
        
        while current <= end_date:
            dates_str.append(current.strftime("%d/%m/%Y"))
            
            if self.is_working_day(current):
                current_planned_exp += exp_por_dia

            planned.append(self.exp_to_float_level(current_planned_exp))
            
            if current in hist_dict:
                actual.append(self.exp_to_float_level(hist_dict[current]))
            elif current <= hoje and actual:
                actual.append(actual[-1])
            elif current <= hoje and not actual:
                actual.append(self.exp_to_float_level(exp_inicio))
                
            current += timedelta(days=1)
            
        plt.clf()
        plt.theme('clear')
        plt.plotsize(None, plt.terminal_height() - 5)
        plt.date_form('d/m/Y')
        plt.plot(dates_str, planned, label='Planejado (Guia)', color='blue')
        plt.plot(dates_str[:len(actual)], actual, label='Realizado', color='green')
        if actual:
            plt.scatter([dates_str[len(actual)-1]], [actual[-1]], label='Progresso Atual', color='yellow', marker='x')
        plt.title("Curva de Projeção de Nível")
        plt.xlabel("Data")
        plt.ylabel("Nível (Guru)")
        plt.show()

    def get_status_data(self):
        hoje = self.get_today()
        etapa = self.get_stage_for_date(hoje)
        
        if not etapa:
            return {"error": f"A data atual ({hoje.strftime('%d/%m/%Y')}) não está dentro de nenhuma etapa configurada."}

        start_date = datetime.strptime(etapa['data_inicio'], "%Y-%m-%d").date()
        end_date = datetime.strptime(etapa['data_fim'], "%Y-%m-%d").date()
        exp_inicio = self.get_absolute_exp(etapa['nivel_inicio'], 0.0)
        exp_fim = self.get_absolute_exp(etapa['nivel_fim'], 0.0)
        exp_total_meta = exp_fim - exp_inicio
        
        all_working_days = self.calculate_working_days(start_date, end_date)
        total_working_days = len(all_working_days)
        
        if total_working_days == 0:
            return {"error": "Nenhum dia util nesta etapa."}
            
        exp_por_dia = exp_total_meta / total_working_days
        dias_passados = [d for d in all_working_days if d <= hoje]
        meta_atual_exp_abs = exp_inicio + (len(dias_passados) * exp_por_dia)
        
        dias_passados_ontem = [d for d in all_working_days if d < hoje]
        meta_ontem_exp_abs = exp_inicio + (len(dias_passados_ontem) * exp_por_dia)

        status_data = {
            "etapa_nome": etapa['nome'],
            "hoje": hoje.strftime('%d/%m/%Y'),
            "is_working_day": self.is_working_day(hoje),
            "dias_passados": len(dias_passados),
            "total_working_days": total_working_days,
            "meta_atual_exp": meta_atual_exp_abs,
            "exp_por_dia": exp_por_dia,
            "exp_total_meta": exp_total_meta,
            "exp_inicio": exp_inicio,
            "exp_fim": exp_fim,
            "goal_date": etapa['data_fim'],
            "goal_level": etapa['nivel_fim']
        }

        if self.history:
            ultimo_reg = self.history[-1]
            exp_atual_abs = ultimo_reg['exp_absoluta']
            delta = exp_atual_abs - meta_atual_exp_abs
            exp_ganha_etapa = max(0, exp_atual_abs - exp_inicio)
            
            progresso_pct = max(0.0, min(100.0, (exp_ganha_etapa / exp_total_meta) * 100))
            
            is_pending_today = False
            if delta < 0 and exp_atual_abs >= meta_ontem_exp_abs:
                is_pending_today = True

            status_data.update({
                "has_history": True,
                "ultimo_registro_data": datetime.strptime(ultimo_reg['data'], "%Y-%m-%d").strftime("%d/%m/%Y"),
                "ultimo_registro_nivel": ultimo_reg['nivel'],
                "ultimo_registro_pct": ultimo_reg['porcentagem'],
                "exp_atual_abs": exp_atual_abs,
                "delta": delta,
                "dias_adiantado": delta / exp_por_dia if exp_por_dia > 0 else 0,
                "progresso_pct": progresso_pct,
                "is_pending_today": is_pending_today
            })
        else:
            status_data["has_history"] = False

        # Expectativa para hoje (Dica)
        t_nivel = etapa['nivel_inicio']
        t_pct = 0.0
        for i in range(1, 100):
            n = f"Guru {i}"
            nx = f"Guru {i+1}"
            if n in self.exp_table and nx in self.exp_table:
                en = self.get_absolute_exp(n, 0.0)
                enx = self.get_absolute_exp(nx, 0.0)
                if en <= meta_atual_exp_abs < enx:
                    t_nivel = n
                    t_pct = ((meta_atual_exp_abs - en) / (enx - en)) * 100
                    break
        status_data["dica_nivel"] = t_nivel
        status_data["dica_pct"] = t_pct

        return status_data

    def get_chart_data(self):
        hoje = self.get_today()
        etapa = self.get_stage_for_date(hoje)
        if not etapa:
            return {"error": "Nenhuma etapa ativa"}
            
        start_date = datetime.strptime(etapa['data_inicio'], "%Y-%m-%d").date()
        end_date = datetime.strptime(etapa['data_fim'], "%Y-%m-%d").date()
        exp_inicio = self.get_absolute_exp(etapa['nivel_inicio'], 0.0)
        exp_fim = self.get_absolute_exp(etapa['nivel_fim'], 0.0)
        
        all_working_days = self.calculate_working_days(start_date, end_date)
        if not all_working_days:
            return {"error": "Nenhum dia util"}
            
        exp_por_dia = (exp_fim - exp_inicio) / len(all_working_days)
        
        dates_str = []
        planned = []
        actual = []
        
        hist_dict = {datetime.strptime(r['data'], "%Y-%m-%d").date(): r['exp_absoluta'] for r in self.history}
        
        current = start_date
        current_planned_exp = exp_inicio
        
        while current <= end_date:
            dates_str.append(current.strftime("%d/%m/%Y"))
            
            if self.is_working_day(current):
                current_planned_exp += exp_por_dia

            planned.append(round(self.exp_to_float_level(current_planned_exp), 3))
            
            if current in hist_dict:
                actual.append(round(self.exp_to_float_level(hist_dict[current]), 3))
            elif current <= hoje and actual:
                actual.append(actual[-1])
            elif current <= hoje and not actual:
                actual.append(round(self.exp_to_float_level(exp_inicio), 3))
            else:
                actual.append(None) # Para o Chart.js não desenhar linha no futuro
                
            current += timedelta(days=1)
            
        return {
            "labels": dates_str,
            "planned": planned,
            "actual": actual
        }

    def get_history_data(self, ano, mes):
        import calendar
        cal = calendar.monthcalendar(ano, mes)
        hist_dict = {reg['data']: reg for reg in self.history}
        hoje = self.get_today()
        
        calendar_data = []
        for week in cal:
            week_data = []
            for dia in week:
                if dia == 0:
                    week_data.append(None)
                    continue
                    
                data_atual = date(ano, mes, dia)
                data_str = data_atual.strftime("%Y-%m-%d")
                eh_util = self.is_working_day(data_atual)
                tem_registro = data_str in hist_dict
                
                day_info = {
                    "dia": dia,
                    "data": data_str,
                    "eh_util": eh_util,
                    "futuro": data_atual > hoje,
                    "registro": None
                }
                
                if tem_registro:
                    reg = hist_dict[data_str]
                    day_info["registro"] = {
                        "nivel": reg['nivel'],
                        "porcentagem": reg['porcentagem']
                    }
                week_data.append(day_info)
            calendar_data.append(week_data)
            
        return calendar_data

    def get_day_details(self, date_str):
        # date_str em YYYY-MM-DD
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Data inválida."}

        etapa = self.get_stage_for_date(target_date)
        if not etapa:
            # Se não houver etapa hoje, tenta ver se a data é anterior à primeira etapa
            # ou posterior à última para dar um feedback melhor
            return {"error": "A data selecionada não faz parte de nenhuma etapa configurada."}

        start_date = datetime.strptime(etapa['data_inicio'], "%Y-%m-%d").date()
        end_date = datetime.strptime(etapa['data_fim'], "%Y-%m-%d").date()
        exp_inicio = self.get_absolute_exp(etapa['nivel_inicio'], 0.0)
        exp_fim = self.get_absolute_exp(etapa['nivel_fim'], 0.0)
        
        all_working_days = self.calculate_working_days(start_date, end_date)
        if not all_working_days:
            return {"error": "Nenhum dia util nesta etapa."}
            
        exp_por_dia = (exp_fim - exp_inicio) / len(all_working_days)
        
        # Meta para o dia (acumulada do inicio da etapa ate o dia alvo)
        dias_passados = [d for d in all_working_days if d <= target_date]
        meta_exp_abs = exp_inicio + (len(dias_passados) * exp_por_dia)
        
        # Realizado
        registro = next((r for r in self.history if r['data'] == date_str), None)
        
        # Valor real (ou último conhecido se não houver registro hoje)
        exp_real_abs = 0
        if registro:
            exp_real_abs = registro['exp_absoluta']
        else:
            # Busca o último registro antes dessa data
            for r in reversed(self.history):
                if r['data'] < date_str:
                    exp_real_abs = r['exp_absoluta']
                    break
            if exp_real_abs == 0:
                exp_real_abs = exp_inicio

        delta = exp_real_abs - meta_exp_abs
        
        # Formatar níveis para exibição (float)
        meta_nivel_float = self.exp_to_float_level(meta_exp_abs)
        real_nivel_float = self.exp_to_float_level(exp_real_abs)
        
        return {
            "data": target_date.strftime("%d/%m/%Y"),
            "is_working_day": self.is_working_day(target_date),
            "meta_exp": int(meta_exp_abs),
            "meta_nivel": round(meta_nivel_float, 2),
            "real_exp": int(exp_real_abs),
            "real_nivel": round(real_nivel_float, 2),
            "delta": int(delta),
            "has_registro": registro is not None,
            "nivel_nome": registro['nivel'] if registro else None,
            "porcentagem": registro['porcentagem'] if registro else None,
            "etapa_nome": etapa['nome']
        }

    def get_monthly_stats(self):

        hoje = self.get_today()
        etapa = self.get_stage_for_date(hoje)
        if not etapa:
            return {"error": "Nenhuma etapa ativa"}
            
        start_date = datetime.strptime(etapa['data_inicio'], "%Y-%m-%d").date()
        end_date = datetime.strptime(etapa['data_fim'], "%Y-%m-%d").date()
        exp_inicio_etapa = self.get_absolute_exp(etapa['nivel_inicio'], 0.0)
        exp_fim_etapa = self.get_absolute_exp(etapa['nivel_fim'], 0.0)
        
        all_working_days = self.calculate_working_days(start_date, end_date)
        if not all_working_days:
            return {"error": "Nenhum dia util"}
            
        exp_por_dia = (exp_fim_etapa - exp_inicio_etapa) / len(all_working_days)
        
        # Gerar lista de meses
        meses = []
        current_y = start_date.year
        current_m = start_date.month
        while current_y < end_date.year or (current_y == end_date.year and current_m <= end_date.month):
            meses.append((current_y, current_m))
            current_m += 1
            if current_m > 12:
                current_m = 1
                current_y += 1
        
        # Mapear historico por data para facilitar busca
        hist_dict = {datetime.strptime(r['data'], "%Y-%m-%d").date(): r['exp_absoluta'] for r in self.history}
        
        # Ordenar datas do historico
        hist_dates = sorted(hist_dict.keys())

        def get_exp_at_date(target_date):
            # Retorna a exp na data especifica ou a ultima registrada antes dela
            if target_date in hist_dict:
                return hist_dict[target_date]
            
            last_known_exp = exp_inicio_etapa
            for d in hist_dates:
                if d <= target_date:
                    last_known_exp = hist_dict[d]
                else:
                    break
            return last_known_exp

        labels = []
        planned_exp_gain = []
        actual_exp_gain = []
        planned_level = []
        actual_level = []
        
        mes_nomes_curto = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        
        cumulative_target_exp = exp_inicio_etapa
        
        # Para calcular ganho real, precisamos do exp do fim do mes anterior
        prev_month_last_day_exp = exp_inicio_etapa

        for y, m in meses:
            labels.append(f"{mes_nomes_curto[m-1]}/{y}")
            
            # 1. Calcular Meta do Mês
            # Primeiro e último dia do mês
            import calendar
            _, last_day = calendar.monthrange(y, m)
            
            month_start = max(start_date, date(y, m, 1))
            month_end = min(end_date, date(y, m, last_day))
            
            work_days_in_month = len(self.calculate_working_days(month_start, month_end))
            target_gain = work_days_in_month * exp_por_dia
            planned_exp_gain.append(round(target_gain, 0))
            
            cumulative_target_exp += target_gain
            planned_level.append(round(self.exp_to_float_level(cumulative_target_exp), 2))
            
            # 2. Calcular Realizado do Mês
            # Se o mês ainda não começou, real é 0 ou None
            if month_start > hoje:
                actual_exp_gain.append(None)
                actual_level.append(None)
            else:
                # Exp no fim deste mês (limitado a hoje)
                effective_end = min(hoje, month_end)
                curr_month_last_exp = get_exp_at_date(effective_end)
                
                # O ganho é a diferença entre o fim deste mês e o fim do anterior
                # Se o mês já passou completamente, usamos o exp do último dia do mês
                # Se estamos no meio do mês, usamos o exp de hoje
                gain = max(0, curr_month_last_exp - prev_month_last_day_exp)
                actual_exp_gain.append(round(gain, 0))
                actual_level.append(round(self.exp_to_float_level(curr_month_last_exp), 2))
                
                # Atualiza para o próximo mês
                # IMPORTANTE: Se o mês passou, usamos o valor do último dia do mês para o próximo cálculo
                # Mas se o mês ainda está em curso, prev_month_last_day_exp deve ser o do mês anterior "cheio"
                if effective_end == month_end:
                     prev_month_last_day_exp = curr_month_last_exp
                else:
                     # Se paramos em "hoje", para o próximo mês o ponto de partida ainda será esse "hoje"
                     prev_month_last_day_exp = curr_month_last_exp

        return {
            "labels": labels,
            "planned_gain": planned_exp_gain,
            "actual_gain": actual_exp_gain,
            "planned_level": planned_level,
            "actual_level": actual_level
        }

    def add_progress(self, data_str, nivel, pct):
        # data_str deve vir em DD/MM/YYYY ou YYYY-MM-DD
        if '/' in data_str:
            dt = datetime.strptime(data_str, "%d/%m/%Y")
            data_reg = dt.strftime("%Y-%m-%d")
        else:
            dt = datetime.strptime(data_str, "%Y-%m-%d")
            data_reg = data_str

        if nivel not in self.exp_table:
            return {"error": "Nível não reconhecido."}

        try:
            pct = float(pct)
        except ValueError:
            return {"error": "Porcentagem inválida."}

        exp_abs = self.get_absolute_exp(nivel, pct)

        registro = {
            "data": data_reg,
            "nivel": nivel,
            "porcentagem": pct,
            "exp_absoluta": exp_abs
        }

        updated = False
        for idx, reg in enumerate(self.history):
            if reg['data'] == data_reg:
                self.history[idx] = registro
                updated = True
                break
        
        if not updated:
            self.history.append(registro)
            self.history.sort(key=lambda x: x['data'])

        self.save_history()
        return {"success": True, "message": "Registro atualizado!" if updated else "Registro salvo com sucesso!"}

    def delete_progress(self, data_str):
        # data_str pode vir em DD/MM/YYYY ou YYYY-MM-DD
        if '/' in data_str:
            try:
                dt = datetime.strptime(data_str, "%d/%m/%Y")
                data_reg = dt.strftime("%Y-%m-%d")
            except ValueError:
                return {"error": "Data inválida."}
        else:
            data_reg = data_str

        original_len = len(self.history)
        self.history = [r for r in self.history if r['data'] != data_reg]
        
        if len(self.history) < original_len:
            self.save_history()
            return {"success": True, "message": f"Registro de {data_reg} removido."}
        else:
            return {"error": f"Nenhum registro encontrado para a data {data_reg}."}

    def update_stages(self, stages):
        """
        Atualiza todas as etapas de uma vez.
        Valida encadeamento e preserva dados históricos.
        """
        if len(stages) < 2:
            return {"error": "É necessário fornecer pelo menos 2 etapas."}

        # Validações
        for i, stage in enumerate(stages):
            # Valida campos obrigatórios
            required_fields = ['nome', 'data_inicio', 'data_fim', 'nivel_inicio', 'nivel_fim']
            for field in required_fields:
                if field not in stage:
                    return {"error": f"Etapa {i+1}: campo '{field}' obrigatório."}

            # Valida formato de data
            try:
                start_date = datetime.strptime(stage['data_inicio'], "%Y-%m-%d").date()
                end_date = datetime.strptime(stage['data_fim'], "%Y-%m-%d").date()
            except ValueError:
                return {"error": f"Etapa {i+1}: formato de data inválido. Use YYYY-MM-DD."}

            # Valida que data_fim > data_inicio
            if end_date <= start_date:
                return {"error": f"Etapa {i+1}: data de conclusão deve ser posterior à data de início."}

            # Valida níveis na tabela de EXP
            if stage['nivel_inicio'] not in self.exp_table:
                return {"error": f"Etapa {i+1}: nível inicial '{stage['nivel_inicio']}' não encontrado."}
            if stage['nivel_fim'] not in self.exp_table:
                return {"error": f"Etapa {i+1}: nível final '{stage['nivel_fim']}' não encontrado."}

            # Valida que nivel_fim > nivel_inicio
            exp_inicio = self.get_absolute_exp(stage['nivel_inicio'], 0.0)
            exp_fim = self.get_absolute_exp(stage['nivel_fim'], 0.0)
            if exp_fim <= exp_inicio:
                return {"error": f"Etapa {i+1}: nível final deve ser maior que nível inicial."}

        # Valida encadeamento entre etapas
        for i in range(len(stages) - 1):
            current_stage = stages[i]
            next_stage = stages[i + 1]

            current_end = datetime.strptime(current_stage['data_fim'], "%Y-%m-%d").date()
            next_start = datetime.strptime(next_stage['data_inicio'], "%Y-%m-%d").date()

            # Data de início da próxima etapa deve ser dia seguinte ao fim da atual
            expected_next_start = current_end + timedelta(days=1)
            if next_start != expected_next_start:
                return {"error": f"Etapa {i+2}: data de início deve ser {expected_next_start.strftime('%Y-%m-%d')} (dia seguinte ao fim da Etapa {i+1})."}

            # Nível inicial da próxima etapa deve ser igual ao nível final da atual
            if next_stage['nivel_inicio'] != current_stage['nivel_fim']:
                return {"error": f"Etapa {i+2}: nível inicial deve ser '{current_stage['nivel_fim']}' (mesmo nível final da Etapa {i+1})."}

        # Valida que não há registros históricos fora das novas datas
        if self.history:
            first_stage_start = datetime.strptime(stages[0]['data_inicio'], "%Y-%m-%d").date()
            last_stage_end = datetime.strptime(stages[-1]['data_fim'], "%Y-%m-%d").date()

            for registro in self.history:
                reg_date = datetime.strptime(registro['data'], "%Y-%m-%d").date()
                if reg_date < first_stage_start or reg_date > last_stage_end:
                    return {"error": f"Registro histórico em {registro['data']} está fora do período das novas etapas ({first_stage_start} a {last_stage_end}). Ajuste as datas ou remova o registro."}

        # Atualiza config
        self.config['etapas'] = stages

        # Salva no arquivo
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        # Recarrega config
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        return {"success": True, "message": "Etapas atualizadas com sucesso!"}

    def update_goal(self, data_fim, nivel_fim):
        """
        Método legado - atualiza apenas a etapa atual.
        Mantido para compatibilidade com endpoint antigo.
        Usa update_stages() internamente para garantir validação consistente.
        """
        if nivel_fim not in self.exp_table:
            return {"error": f"Nível '{nivel_fim}' não encontrado na tabela de EXP."}

        try:
            datetime.strptime(data_fim, "%Y-%m-%d")
        except ValueError:
            return {"error": "Formato de data inválido. Use YYYY-MM-DD."}

        if not self.config.get('etapas'):
            return {"error": "Nenhuma etapa configurada no arquivo de configuração."}

        # Encontra a etapa atual
        hoje = self.get_today()
        etapa_atual = self.get_stage_for_date(hoje)

        if not etapa_atual:
            return {"error": "Nenhuma etapa ativa no momento."}

        # Encontra índice da etapa atual
        etapa_idx = None
        for i, etapa in enumerate(self.config['etapas']):
            if etapa['nome'] == etapa_atual['nome']:
                etapa_idx = i
                break

        if etapa_idx is None:
            return {"error": "Não foi possível localizar a etapa para atualização."}

        # Cria cópia das etapas
        stages = [dict(e) for e in self.config['etapas']]

        # Atualiza etapa atual
        stages[etapa_idx]['data_fim'] = data_fim
        stages[etapa_idx]['nivel_fim'] = nivel_fim

        # Se houver próxima etapa, atualiza encadeamento
        if etapa_idx + 1 < len(stages):
            next_stage = stages[etapa_idx + 1]

            # Atualiza data de início da próxima etapa
            end_date = datetime.strptime(data_fim, "%Y-%m-%d").date()
            next_start = end_date + timedelta(days=1)
            next_stage['data_inicio'] = next_start.strftime("%Y-%m-%d")

            # Atualiza nível inicial da próxima etapa
            next_stage['nivel_inicio'] = nivel_fim

        # Usa o novo método para validar e salvar
        return self.update_stages(stages)
        
        return {"error": "Não foi possível localizar a etapa para atualização."}

    def menu(self):
        self.clear_screen()
        self.show_status()
        while True:
            print(f"\n{Colors.CYAN}{Colors.BOLD}===============================")
            print(" Gerenciador de Metas de Caça")
            print(f"==============================={Colors.RESET}")
            print(f"{Colors.GREEN}1.{Colors.RESET} Ver status atual")
            print(f"{Colors.GREEN}2.{Colors.RESET} Registrar progresso")
            print(f"{Colors.GREEN}3.{Colors.RESET} Ver histórico e médias")
            print(f"{Colors.GREEN}4.{Colors.RESET} Ver gráfico de projeção")
            print(f"{Colors.GREEN}5.{Colors.RESET} Remover registro")
            print(f"{Colors.GREEN}6.{Colors.RESET} Sair")
            escolha = input(f"{Colors.YELLOW}Escolha uma opção: {Colors.RESET}").strip()

            if escolha == '6':
                self.clear_screen()
                break

            self.clear_screen()

            if escolha == '1':
                self.show_status()
            elif escolha == '2':
                self.record_progress()
                input(f"\n{Colors.YELLOW}Pressione Enter para voltar ao menu...{Colors.RESET}")
                self.clear_screen()
                self.show_status()
            elif escolha == '3':
                self.show_history()
                input(f"\n{Colors.YELLOW}Pressione Enter para voltar ao menu...{Colors.RESET}")
                self.clear_screen()
                self.show_status()
            elif escolha == '4':
                self.show_graph()
                input(f"\n{Colors.YELLOW}Pressione Enter para voltar ao menu...{Colors.RESET}")
                self.clear_screen()
                self.show_status()
            elif escolha == '5':
                print(f"\n{Colors.CYAN}--- Remover Registro ---{Colors.RESET}")
                data_del = input("Data para remover (DD/MM/YYYY) [Enter para cancelar]: ").strip()
                if data_del:
                    res = self.delete_progress(data_del)
                    if "success" in res:
                        print(f"{Colors.GREEN}{res['message']}{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}{res['error']}{Colors.RESET}")
                input(f"\n{Colors.YELLOW}Pressione Enter para voltar ao menu...{Colors.RESET}")
                self.clear_screen()
                self.show_status()
            else:
                self.show_status()
                print(f"\n{Colors.RED}Opção inválida. Tente novamente.{Colors.RESET}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Gerenciador de Metas de Caca BDO")
    parser.add_argument('-t', '--test', action='store_true', help="Ativa o modo de teste com data ficticia (15/05/2026) e historico isolado")
    args = parser.parse_args()

    app = HuntingManager(test_mode=args.test)
    app.menu()
