from PIL import Image, ImageDraw
items = [
    ('0,6 Suspiro de Fada', 'slots7/0,6_suspiro.png'),
    ('1,3 Suspiro antigo', 'slots7/1,3_suspiro_antigo.png'),
    ('2,5 Estrela Silvestre', 'slots7/2,5_estrela.png'),
    ('2,6 Garrafa Vidro', 'slots7/2,6_garrafa.png'),
    ('2,7 Folha Rosa', 'slots7/2,7_folha.png'),
    ('2,8 Catalisador', 'slots7/2,8_catalisador.png'),
    ('3,0 Iguarias Bruxa', 'slots7/3,0_iguarias.png'),
]
pad = 10
W = sum(Image.open(p).width for _, p in items) + pad*(len(items)+1)
H = 220
strip = Image.new('RGB', (W, H), (18, 18, 18))
d = ImageDraw.Draw(strip)
x = pad
for label, path in items:
    im = Image.open(path)
    strip.paste(im, (x, 30))
    d.text((x, 6), label, fill=(255, 255, 0))
    x += im.width + pad
strip.save('strip9.png')
print('saved', strip.size)
