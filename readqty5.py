from PIL import Image
import requests, time
from collections import Counter

def find_digits(im):
    g = im.convert('L')
    w, h = g.size
    px = g.load()
    rows = []
    for y in range(int(h*0.55), h):
        cnt = sum(1 for x in range(w) if px[x, y] > 150)
        rows.append((y, cnt))
    bright_rows = [y for y, c in rows if c >= 3]
    if not bright_rows:
        return None
    y0, y1 = min(bright_rows), max(bright_rows)
    cols = []
    for x in range(w):
        cnt = sum(1 for y in range(y0, y1+1) if px[x, y] > 150)
        cols.append((x, cnt))
    bright_cols = [x for x, c in cols if c >= 2]
    if not bright_cols:
        return None
    x0, x1 = min(bright_cols), max(bright_cols)
    pad = 4
    return im.crop((max(0, x0-pad), max(0, y0-pad), min(w, x1+pad), min(h, y1+pad)))

names = ['0,6_suspiro', '1,3_suspiro_antigo', '2,5_estrela', '2,6_garrafa', '2,7_folha', '2,8_catalisador', '3,0_iguarias']
for n in names:
    im = Image.open(f'slots7/{n}.png')  # 6x
    dig = find_digits(im)
    if dig is None:
        print(n, 'SEM DIGITOS'); continue
    dig = dig.resize((dig.width*3, dig.height*3), Image.LANCZOS)
    dig.save(f'/tmp/dd_{n}.png')
    reads = []
    for _ in range(3):
        try:
            r = requests.post('http://localhost:5000/cp/api/ocr-inventory', files={'image': open(f'/tmp/dd_{n}.png','rb')}, timeout=90)
            j = r.json()
            reads.append((j.get('raw_text') or '').strip())
        except Exception as e:
            reads.append(f'ERR {type(e).__name__}')
        time.sleep(0.6)
    print(n, Counter(reads))
