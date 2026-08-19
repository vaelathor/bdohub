from PIL import Image
import requests, time
from collections import Counter

names = ['0,6_suspiro', '1,3_suspiro_antigo', '2,5_estrela', '2,6_garrafa', '2,7_folha', '2,8_catalisador', '3,0_iguarias']
for n in names:
    im = Image.open(f'slots7/{n}.png')  # 6x
    w, h = im.size
    variants = {
        'slot': im,
        'baixo': im.crop((0, int(h*0.5), w, h)),
    }
    reads = []
    for vname, v in variants.items():
        v = v.resize((int(v.width*1.5), int(v.height*1.5)), Image.LANCZOS)
        v.save(f'/tmp/v_{n}.png')
        for _ in range(3):
            try:
                r = requests.post('http://localhost:5000/cp/api/ocr-inventory', files={'image': open(f'/tmp/v_{n}.png','rb')}, timeout=90)
                j = r.json()
                reads.append((j.get('raw_text') or '').strip())
            except Exception as e:
                reads.append(f'ERR {type(e).__name__}')
            time.sleep(0.6)
    print(n, Counter(reads))
