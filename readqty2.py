from PIL import Image
import requests, time

names = ['0,6_suspiro', '1,3_suspiro_antigo', '2,5_estrela', '2,6_garrafa', '2,7_folha', '2,8_catalisador', '3,0_iguarias']
for n in names:
    im = Image.open(f'slots7/{n}.png')  # 6x
    w, h = im.size
    # número fica no rodapé: faixa estreita inferior
    c = im.crop((0, int(h*0.72), w, h))
    c = c.resize((c.width*3, c.height*3), Image.LANCZOS)
    c.save(f'/tmp/r_{n}.png')
    r = requests.post('http://localhost:5000/cp/api/ocr-inventory', files={'image': open(f'/tmp/r_{n}.png','rb')}, timeout=60)
    j = r.json()
    print(f'{n}: {(j.get("raw_text") or "").strip()!r}')
    time.sleep(0.4)
