from PIL import Image
img = Image.open('test_subprodutos.png').convert('L')
w, h = img.size
px = img.load()

# Perfil de coluna: média por coluna. Slots são mais claros que o painel; bordas escuras.
colprof = [sum(px[x, y] for y in range(h)) / h for x in range(w)]

# Achar bordas: vales fortes no perfil (painel ~40, slots ~80-110)
def valleys(profile, width, min_gap=3):
    out = []
    i = 0
    while i < width:
        if profile[i] < 52:  # abaixo disso é gap entre slots
            j = i
            while j < width and profile[j] < 52:
                j += 1
            mid = (i + j - 1) // 2
            if j - i >= min_gap:
                out.append(mid)
            i = j
        else:
            i += 1
    return out

col_seps = valleys(colprof, w)
# O painel tem borda esquerda/direita; remover seps muito próximas da borda
col_seps = [c for c in col_seps if 15 < c < w - 15]
print('separadores de coluna (px):', col_seps)

# Linhas
rowprof = [sum(px[x, y] for x in range(w)) / w for y in range(h)]
row_seps = valleys(rowprof, h)
row_seps = [r for r in row_seps if 15 < r < h - 15]
print('separadores de linha (px):', row_seps)

# Construir grade
cols = [0] + col_seps + [w]
rows = [0] + row_seps + [h]
col_ranges = [(cols[i], cols[i+1]) for i in range(len(cols)-1)]
row_ranges = [(rows[i], rows[i+1]) for i in range(len(rows)-1)]
print('colunas:', col_ranges)
print('linhas:', row_ranges)
