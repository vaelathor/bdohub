from PIL import Image
img = Image.open('grid_big.png')
img.thumbnail((500,500))
img.convert('RGB').save('grid_small.jpg', quality=80)
print('ok')
