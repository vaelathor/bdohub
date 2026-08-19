from PIL import Image
import glob
names = ['0,6_suspiro', '1,3_suspiro_antigo', '2,5_estrela', '2,6_garrafa', '2,7_folha', '2,8_catalisador', '3,0_iguarias']
imgs = [Image.open(f'slots7/{n}.png') for n in names]
# faixa horizontal com rótulo
pad = 6
W = sum(i.width for i in imgs) + pad*(len(imgs)+1)
H = max(i.height for i in imgs) + 40
strip = Image.new('RGB', (W, H), (20, 20, 20))
from PIL import ImageDraw
d = ImageDraw.Draw(strip)
x = pad
for n, im in zip(names, imgs):
    strip.paste(im, (x, 40))
    d.text((x, 4), n, fill=(255, 255, 0))
    x += im.width + pad
strip.save('strip7.png')
print('saved', strip.size)
