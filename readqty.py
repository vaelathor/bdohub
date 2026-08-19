from PIL import Image
import requests, time

names = ['0,6_suspiro', '1,3_suspiro_antigo', '2,5_estrela', '2,6_garrafa', '2,7_folha', '2,8_catalisador', '3,0_iguarias']
# recorte: canto inferior direito do slot (região da quantidade)
for n in names:
    im = Image.open(f'slots7/{n}.png')  # já 6x
    w, h = im.size
    # quantidade fica no rodapé do slot: pegar faixa inferior inteira, e tbm faixa inferior-direita
    crops = {
        'baixo_todo': (0, int(h*0.55), w, h),
        'baixo_dir': (int(w*0.35), int(h*0.55), w, h),
    }
    for cname, box in crops.items():
        c = im.crop(box)
        c = c.resize((c.width*2, c.height*2), Image.LANCZOS)
        c.save(f'/tmp/q_{n}_{cname}.png')
    # OCR das duas versões
    for cname in crops:
        r = requests.post('http://localhost:5000/cp/api/ocr-inventory', files={'image': open(f'/tmp/q_{n}_{cname}.png','rb')}, timeout=60)
        j = r.json()
        txt = (j.get('raw_text') or '').strip()
        print(f'{n} [{cname}]: {txt!r}')
        time.sleep(0.4)
