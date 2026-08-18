# -*- coding: utf-8 -*-
"""Cálculo do painel de cidades/oficinas/operários do comércio de caixas.

Fonte dos dados:
  - Casas, oficinas, alojamentos e distâncias: banco de dados do Workerman
    (espelho do jogo: houseinfo, house_craft_info, houseinforeceipe,
    lodging_per_town, distances_tk2hk, worker_static, loc).
  - Coordenadas das cidades e nomes PT: cities.json (gpw v2.15 + bdocodex).
  - Nodes e custo de conexão: nodes.json (exploration.json do jogo, via
    bdo-noderouter — o mesmo dado que o Workerman usa).
  - Produção: ciclo = 5 min (workload 150 @ 150 vel) + caminhada real da casa;
    multiplicador x4 com skill de embalagem +3.
  - Transporte: tempo(min) = distância_euclidiana * 0.00015735 (calibrado com
    Valencia->Yukjo = 7h12m do usuário; validado com Trent->Valencia ~4h).

Este módulo é usado tanto pelo build_towns.py (gera towns.json) quanto pelo
app.py (recálculo dinâmico ao desligar/ligar oficinas individuais).
"""
import heapq
import json
import math
import os
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'data')

# Parâmetros padrão do usuário
WORKER_SPEED = 150       # velocidade de trabalho (workload 150 -> 5 min)
WORKER_MSPD = 7.5        # velocidade de movimento (m/s) p/ caminhada
PACK_SKILL = 3           # skill de embalagem +3 -> x4 caixas por ciclo
FREE_SLOTS = 1           # 1 operário gratuito por cidade
CYCLE_BASE = 5.0         # minutos base de trabalho (workload 150 @ 150 vel)
TRANSPORT_K = 432 / math.hypot(1026110 - (-1472040), 199132 - 1337990)  # min/unit

# affTown (Workerman) -> gpw node id (cities.json)
AFF_TO_GW = {
    5: 1, 88: 61, 32: 301, 52: 302, 77: 601, 107: 602, 120: 604, 126: 608,
    202: 1101, 221: 1141, 229: 1301, 601: 1314, 605: 1319, 619: 1343,
    693: 1380, 694: 1381, 706: 1604, 735: 1623, 873: 1649, 1124: 1750,
    1210: 1781, 1219: 1785, 1420: 1853, 1444: 1858, 1553: 2001, 955: 1691,
    1375: 1843, 1424: 1857, 1733: 2057, 218: 1834, 1246: 1795, 1219: 1785,
}

# Fixação manual de casa como alojamento (decisão do usuário):
# 735 (Grana) -> casa 3511 (Grana 10) como alojamento, 4 slots.
FORCED_LODGING = {735: ['3511']}
# Cidades onde o usuário limitou os operários em uso (ex.: Árvore da Sabedoria: só 1)
MAX_WORKERS = {706: 1}

PACK_TARGETS = {'pack_produce', 'pack_herb', 'pack_mushr'}
PACK_LABEL = {'pack_produce': 'Colheita', 'pack_herb': 'Erva', 'pack_mushr': 'Cogumelo'}


def _resolve(name):
    """Acha um arquivo de dados: data/ do módulo, raiz do módulo ou raiz do staging."""
    for base in (DATA, ROOT, os.path.join(ROOT, '..')):
        p = os.path.join(base, name)
        if os.path.exists(p):
            return p
    return os.path.join(DATA, name)


def _load_json(name):
    with open(_resolve(name), encoding='utf-8') as f:
        return json.load(f)


_loaded = None


def load():
    """Carrega (uma vez) todos os dados base do jogo."""
    global _loaded
    if _loaded is not None:
        return _loaded
    _loaded = (
        _load_json('wm_houseinfo.json'),
        _load_json('wm_house_craft_info.json'),
        _load_json('wm_houseinforeceipe.json'),
        _load_json('wm_lodging_per_town.json'),
        _load_json('wm_distances_tk2hk.json'),
        _load_json('wm_loc.json'),
        _load_json('cities.json'),
        _load_json('wm_traders.json'),
        _load_json('nodes.json'),
    )
    return _loaded


def build_craft_pack(craft_info):
    cp = {}
    for cid, info in craft_info.items():
        rp = info.get('rp', '')
        if rp.startswith('pack_'):
            cp[cid] = rp
    return cp


def house_pack_types(craftlist, receipt, craft_pack):
    packs = set()
    for use_id in craftlist or {}:
        r = receipt.get(str(use_id))
        if not r:
            continue
        for group in r.get('groups', []):
            for cid in group:
                rp = craft_pack.get(str(cid))
                if rp:
                    packs.add(rp)
    return packs


def closure_of(hk, houses):
    res, seen = [], set()
    cur = hk
    while cur and cur not in seen:
        seen.add(cur)
        res.append(cur)
        h = houses.get(cur)
        if not h:
            break
        nxt = str(h.get('needHouseKey', 0))
        if nxt == '0' or nxt not in houses:
            break
        cur = nxt
    return res


def optimize_lodging(tk, houses, slots, is_workshop, forced_lodging, free_slots,
                     workshops=None):
    """Escolha ótima de alojamentos (min CP) cobrindo target, com casas forçadas.

    `workshops` = lista de oficinas ATIVAS (já sem as desligadas pelo usuário).
    """
    def is_wk(hk):
        return is_workshop(hk) and hk not in forced_lodging

    forced = [hk for hk in forced_lodging if hk in houses and slots.get(hk, 0) > 0]

    if workshops is None:
        workshops = [hk for hk in houses if is_workshop(hk)]
    base = set(forced)
    for w in workshops:
        base.update(closure_of(w, houses))
    base_slots = sum(slots.get(x, 0) for x in base if not is_wk(x))

    target = max(0, len(workshops) - free_slots - base_slots)
    out = {
        'workshops': sorted(workshops),
        'n_workshops': len(workshops),
        'forced_lodging': sorted(forced),
        'forced_slots': sum(slots.get(x, 0) for x in forced),
        'base_slots': base_slots,
        'target': target,
    }
    if target <= 0:
        out.update({'cp': 0, 'chosen': [], 'slots': 0, 'insufficient': False})
        return out

    candidates = [hk for hk in houses
                  if slots.get(hk, 0) > 0 and not is_wk(hk) and hk not in base]

    # componentes conexas via dependência
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for hk in candidates:
        for pre in closure_of(hk, houses):
            union(hk, pre)

    comps = {}
    for hk in candidates:
        comps.setdefault(find(hk), []).append(hk)

    def comp_options(keys):
        keys = list(keys)
        opts = {}
        for mask in range(1 << len(keys)):
            chosen = {keys[i] for i in range(len(keys)) if (mask >> i) & 1}
            if not chosen:
                continue
            closed = set()
            for hk in chosen:
                closed.update(closure_of(hk, houses))
            cost = sum(houses[x].get('CP', 0) for x in closed if x not in base)
            sl = sum(slots.get(x, 0) for x in closed if x not in base and not is_wk(x))
            if cost < opts.get(sl, (10 ** 9, None))[0]:
                opts[sl] = (cost, closed)
        return opts

    dp = {0: (0, set())}
    for keys in comps.values():
        opts = comp_options(keys)
        ndp = dict(dp)
        for s1, (c1, ch1) in dp.items():
            for s2, (c2, ch2) in opts.items():
                ns = s1 + s2
                nc = c1 + c2
                nch = ch1 | ch2
                if nc < ndp.get(ns, (10 ** 9, None))[0]:
                    ndp[ns] = (nc, nch)
        dp = ndp

    best = None
    for s, (c, ch) in dp.items():
        if s >= target and (best is None or c < best[1]):
            best = (s, c, ch)

    if best is None:
        allc = sum(houses[x].get('CP', 0) for x in candidates)
        alls = sum(slots.get(x, 0) for x in candidates)
        out.update({'cp': allc, 'chosen': candidates, 'slots': alls, 'insufficient': True})
        return out

    out.update({'cp': best[1], 'chosen': sorted(best[2]), 'slots': best[0], 'insufficient': False})
    return out


class NodeGraph:
    """Grafo de nodes do jogo: caminhos mínimos (por CP) da base town até cada node."""

    def __init__(self, nodes):
        self.N = {str(k): v for k, v in nodes.items()}
        self._cache = {}

    def _dijkstra(self, base):
        if base in self._cache:
            return self._cache[base]
        N = self.N
        dist = {base: 0}
        prev = {}
        pq = [(0, base)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, 1e18):
                continue
            for v in N[u]['link_list']:
                v = str(v)
                if v not in N:
                    continue
                nd = d + N[v].get('need_exploration_point', 0)
                if nd < dist.get(v, 1e18):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
        self._cache[base] = (dist, prev)
        return dist, prev

    def path_to(self, base, target):
        """Caminho (excluindo a base) de nodes + CP de cada node, até `target`."""
        dist, prev = self._dijkstra(base)
        if target not in prev:
            return None
        path = []
        cur = target
        while cur != base:
            path.append({'id': cur, 'cp': self.N[cur].get('need_exploration_point', 0)})
            cur = prev[cur]
        return path[::-1]

    def connect_cost(self, base, targets):
        """Custo de conectar a UNIÃO dos caminhos até `targets` (nodes compartilhados pagam 1x)."""
        if not targets:
            return 0, []
        dist, prev = self._dijkstra(base)
        taken = []
        taken_set = set()
        for t in targets:
            if t not in prev:
                continue
            cur = t
            while cur != base and cur not in taken_set:
                taken.append(cur)
                taken_set.add(cur)
                cur = prev[cur]
        cost = sum(self.N[x].get('need_exploration_point', 0) for x in taken)
        return cost, sorted(taken, key=int)


def compute_town(aff_tk, disabled_workshops=frozenset(), pt_names=None):
    """Calcula uma cidade (mesma estrutura do towns.json) com oficinas desligadas.

    `disabled_workshops`: set de house keys desligadas pelo usuário.
    `pt_names`: dict house -> namePt (tradução já aplicada), para preservar
    os nomes PT nas oficinas/alojamentos durante o recálculo dinâmico.
    """
    houseinfo, craft_info, receipt, lodging, distances, loc, cities, traders, nodes = load()
    craft_pack = build_craft_pack(craft_info)
    gw_id = AFF_TO_GW.get(aff_tk)
    if not gw_id:
        return None
    city_by_gw = {c['id']: c for c in cities['cities']}
    city = city_by_gw.get(gw_id)
    if not city:
        return None

    slots = {}
    for _tk, v in lodging.items():
        for h in v.get('houses') or []:
            slots[str(h.get('key'))] = h.get('lodgingSpaces', 0)

    house_names = loc['en']['char']
    houses = {hk: h for hk, h in houseinfo.items() if h.get('affTown') == aff_tk}
    pt_names = pt_names or {}

    def is_workshop(hk):
        h = houses.get(hk)
        if not h:
            return False
        return bool(house_pack_types(h.get('CraftList'), receipt, craft_pack) & PACK_TARGETS)

    def nm(hk):
        return pt_names.get(hk) or house_names.get(hk, hk)

    workshops = [hk for hk in houses if is_workshop(hk)]
    if not workshops:
        return None

    forced = [hk for hk in FORCED_LODGING.get(aff_tk, []) if hk in houses]
    # oficinas ativas = todas menos as desligadas e menos as forçadas como alojamento
    active = [hk for hk in workshops if hk not in forced and hk not in disabled_workshops]
    opt = optimize_lodging(aff_tk, houses, slots, is_workshop, forced, FREE_SLOTS,
                           workshops=active)

    # oficinas em uso: as de colheita/cogumelo, exceto as forçadas como alojamento
    workshops_use = active[:]
    # lista exibida: TODAS as oficinas (ativas + desligadas), desligadas marcadas
    display_ws = [hk for hk in workshops]

    # operários: 1 grátis + alojamentos (forçados + escolhidos + base)
    workers = FREE_SLOTS + opt['base_slots'] + opt['slots']
    workers = min(workers, MAX_WORKERS.get(aff_tk, 10 ** 9))

    # produção: ciclo por oficina = 5 + caminhada real (ida+volta ao armazém)
    dmap = distances.get(str(aff_tk), {})
    per_workshop = []
    # prioriza colheita/erva (mais baratas), depois cogumelo
    def prio(w):
        packs = house_pack_types(houses[w].get('CraftList'), receipt, craft_pack) & PACK_TARGETS
        return (0 if packs & {'pack_produce', 'pack_herb'} else 1, w)

    staffed = workshops_use[:]
    if workers < len(staffed):
        staffed = sorted(staffed, key=prio)[:workers]
    staffed = set(staffed)
    total_day = 0.0
    for w in display_ws:
        dist = dmap.get(w, 0)
        walk = 2 * dist / WORKER_MSPD / 60 if dist and dist < 1e6 else 0.8
        cycle = CYCLE_BASE + walk
        crates_day = (24 * 60 / cycle) * (1 + PACK_SKILL)
        disabled = (w in forced) or (w in disabled_workshops)
        per_workshop.append({
            'house': w,
            'name': nm(w),
            'namePt': nm(w),
            'cp': houses[w].get('CP', 0),
            'packs': sorted({PACK_LABEL[p] for p in
                             house_pack_types(houses[w].get('CraftList'), receipt, craft_pack) & PACK_TARGETS}),
            'walkMin': round(walk, 2),
            'cycleMin': round(cycle, 2),
            'cratesDay': round(crates_day),
            'inUse': w in staffed,
            'disabled': disabled,
        })
        if w in staffed:
            total_day += crates_day

    # transporte: destinos de comércio (gerentes de comércio do jogo)
    city_by_tid = {str(c['id']): c for c in cities['cities']}
    city_by_name = {c['name']: c for c in cities['cities']}

    def distxp(d):
        if d / 100 > 500:
            f = math.sqrt(d / 100 / 1000) * 0.7 + 0.3
        else:
            f = math.sqrt(d / 100 / 1000) * 0.95
        return math.floor(f * 1000000)

    cx, cy = city['x'], city['y']
    destinations = []
    for tid, (tx, ty) in traders.items():
        tcity = city_by_tid.get(str(tid))
        if not tcity:
            continue
        d = math.hypot(tx - cx, ty - cy)
        destinations.append({
            'id': tid,
            'name': tcity['name'],
            'namePt': tcity.get('namePt', tcity['name']),
            'min': round(d * TRANSPORT_K),
            'h': round(d * TRANSPORT_K / 60, 1),
            'dist': round(d),
            'distXP': distxp(d),
        })
    destinations.sort(key=lambda x: -x['distXP'])
    for i, dst in enumerate(destinations):
        dst['best'] = (i == 0)
        # bônus de distância real (gpw v2.15), sem teto — o jogo capa a
        # 150% só no preço; o EXP usa o valor real (186,7% p/ Valência->Yukjo)
        dst['expPct'] = round(dst['dist'] * 68 / 1e6, 1)

    # CP de conexão de nodes das oficinas em uso (staffed)
    graph = NodeGraph(nodes)
    base_node = None
    pns = Counter(str(h.get('parentNode')) for h in houses.values())
    for pn, c in pns.most_common():
        nd = graph.N.get(pn)
        if nd and nd.get('is_base_town'):
            base_node = pn
            break
    if base_node is None and pns:
        base_node = pns.most_common(1)[0][0]

    # node/caminho por oficina
    for w in per_workshop:
        h = houses.get(w['house'])
        pn = str(h.get('parentNode')) if h else None
        w['node'] = pn
        if base_node and pn:
            path = graph.path_to(base_node, pn)
            w['connPath'] = path or []
            w['nodeCp'] = sum(x['cp'] for x in (path or []))
        else:
            w['connPath'] = []
            w['nodeCp'] = 0

    # conexão considera só as oficinas realmente em uso (staffed) e não desligadas
    targets = {w['node'] for w in per_workshop if w['inUse'] and not w['disabled'] and w.get('node')}
    conn_cp, conn_nodes = graph.connect_cost(base_node, targets) if base_node else (0, [])

    # compatibilidade com o formato antigo (Valencia/Yukjo) p/ fallback
    transport = {}
    for dname, (dx, dy) in {
        'Valencia': (1026110, 199132),
        'Yukjo (LoML)': (-1472040, 1337990),
        'Dalbeol (LoML)': (-1130090, 1271810),
    }.items():
        d = math.hypot(dx - cx, dy - cy)
        transport[dname] = {
            'min': round(d * TRANSPORT_K),
            'h': round(d * TRANSPORT_K / 60, 1),
        }

    return {
        'affTown': aff_tk,
        'gpwId': gw_id,
        'name': city['name'],
        'namePt': city.get('namePt', city['name']),
        'x': cx,
        'y': cy,
        'workshops': per_workshop,
        'n_workshops': len(workshops_use),
        'n_disabled_ws': len(display_ws) - len(workshops_use),
        'n_colheita': sum(1 for w in per_workshop if w['inUse'] and ('Colheita' in w['packs'] or 'Erva' in w['packs'])),
        'n_cogumelo': sum(1 for w in per_workshop if w['inUse'] and 'Cogumelo' in w['packs']),
        'lodging': {
            'forced': [{'house': x, 'name': nm(x), 'namePt': nm(x), 'cp': houses[x].get('CP', 0),
                        'slots': slots.get(x, 0)} for x in opt['forced_lodging']],
            'chosen': [{'house': x, 'name': nm(x), 'namePt': nm(x), 'cp': houses[x].get('CP', 0),
                        'slots': slots.get(x, 0)} for x in opt['chosen']],
            'cp': opt['cp'],
            'slots': opt['slots'],
            'base_slots': opt['base_slots'],
            'target': opt['target'],
            'insufficient': opt.get('insufficient', False),
            'free_slots': FREE_SLOTS,
        },
        'workers': workers,
        'n_staffed': len([w for w in per_workshop if w['inUse']]),
        'cp_total': sum(houses[w].get('CP', 0) for w in workshops_use) + opt['cp'],
        'conn_cp': conn_cp,
        'conn_nodes': conn_nodes,
        'base_node': base_node,
        'crates_day': round(total_day),
        'transport': transport,
        'destinations': destinations,
        'best_dest': destinations[0] if destinations else None,
    }
