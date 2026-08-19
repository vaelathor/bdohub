from PIL import Image, ImageDraw
img = Image.open('test_subprodutos.png').convert('RGB')
w, h = img.size
px = img.convert('L').load()

# Detectar bordas: agrupar vales próximos (cada borda de slot tem ~2-3px)
colprof = [sum(px[x, y] for y in range(h)) / h for x in range(w)]
rowprof = [sum(px[x, y] for x in range(w)) / w for y in range(h)]

def cluster(valleys, gap=12):
    clusters = []
    for v in valleys:
        if clusters and v - clusters[-1][-1] <= gap:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    return [int(sum(c)/len(c)) for c in clusters]

def valleys(profile, n, thresh=55):
    out = []
    i = 0
    while i < n:
        if profile[i] < thresh:
            j = i
            while j < n and profile[j] < thresh:
                j += 1
            if j - i >= 2:
                out.append((i + j - 1) // 2)
            i = j
        else:
            i += 1
    return out

col_seps = cluster([c for c in valleys(colprof, w) if 12 < c < w - 12])
row_seps = cluster([r for r in valleys(rowprof, h) if 12 < r < h - 12])
print('colunas separadores:', col_seps)
print('linhas separadores:', row_seps)

# Grade
col_b = [0] + col_seps + [w]
row_b = [0] + row_seps + [h]
col_r = [(col_b[i], col_b[i+1]) for i in range(len(col_b)-1)]
row_r = [(row_b[i], row_b[i+1]) for i in range(len(row_b)-1)]
print('colunas:', col_r)
print('linhas:', row_r)

# Anotar
d = ImageDraw.Draw(img)
for ri, (r0, r1) in enumerate(row_r):
    for ci, (c0, c1) in enumerate(col_r):
        d.rectangle([c0, r0, c1-1, r1-1], outline=(255, 60, 60), width=1)
        d.text((c0+1, r0+1), f'{ri},{ci}', fill=(255, 255, 0))
img = img.resize((img.width*2, img.height*2), Image.LANCZOS)
img.save('grid2.png')
print('saved grid2.png', img.size)
