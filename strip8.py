from PIL import Image, ImageDraw
names = ['0,6_suspiro', '1,3_suspiro_antigo', '2,5_estrela', '2,6_garrafa', '2,7_folha', '2,8_catalisador', '3,0_iguarias']
imgs = [Image.open(f'slots7/{n}.png').resize((150, 150), Image.LANCZOS) for n in names]
pad = 8
W = sum(i.width for i in imgs) + pad*(len(imgs)+1)
H = 150 + 30
strip = Image.new('RGB', (W, H), (20, 20, 20))
d = ImageDraw.Draw(strip)
x = pad
for n, im in zip(names, imgs):
    strip.paste(im, (x, 30))
    d.text((x, 6), n, fill=(255, 255, 0))
    x += im.width + pad
strip.save('strip8.png')
print('saved', strip.size)
