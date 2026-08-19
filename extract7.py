from PIL import Image
img = Image.open('test_subprodutos.png').convert('RGB')
col_b = [0, 49, 99, 151, 202, 257, 305, 355, 407, 450, 468]
row_b = [0, 54, 105, 156, 201, 219]
col_r = [(col_b[i], col_b[i+1]) for i in range(len(col_b)-1)]
row_r = [(row_b[i], row_b[i+1]) for i in range(len(row_b)-1)]

# 0-based positions from user mapping (1-based row,col)
targets = {
    '0,6_suspiro': (0, 6),
    '1,3_suspiro_antigo': (1, 3),
    '2,5_estrela': (2, 5),
    '2,6_garrafa': (2, 6),
    '2,7_folha': (2, 7),
    '2,8_catalisador': (2, 8),
    '3,0_iguarias': (3, 0),
}
import os
os.makedirs('slots7', exist_ok=True)
for name, (ri, ci) in targets.items():
    c0, c1 = col_r[ci]
    r0, r1 = row_r[ri]
    slot = img.crop((c0, r0, c1, r1))
    slot = slot.resize((slot.width*6, slot.height*6), Image.LANCZOS)
    slot.save(f'slots7/{name}.png')
    print(name, 'crop', (c0, r0, c1, r1), '->', slot.size)
