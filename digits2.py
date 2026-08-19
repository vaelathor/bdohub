from PIL import Image, ImageDraw
names = ['0,6_suspiro', '1,3_suspiro_antigo', '2,5_estrela', '2,6_garrafa', '2,7_folha', '2,8_catalisador', '3,0_iguarias']
imgs = []
for n in names:
    try:
        im = Image.open(f'/tmp/dd_{n}.png')
    except Exception:
        im = None
    imgs.append((n, im))
cols, rows = 2, 4
cell_w, cell_h = 300, 110
W, H = cols*cell_w, rows*cell_h
grid = Image.new('RGB', (W, H), (16, 16, 16))
d = ImageDraw.Draw(grid)
for i, (n, im) in enumerate(imgs):
    r, c = divmod(i, cols)
    x0, y0 = c*cell_w, r*cell_h
    d.rectangle([x0, y0, x0+cell_w-1, y0+cell_h-1], outline=(60, 60, 60))
    d.text((x0+4, y0+4), n, fill=(255, 255, 0))
    if im:
        im2 = im.copy()
        im2.thumbnail((cell_w-10, cell_h-40))
        grid.paste(im2, (x0+5, y0+36))
grid.save('digits2.png')
print('saved', grid.size)
