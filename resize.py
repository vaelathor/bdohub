from PIL import Image
img = Image.open('grid_big.png')
img.thumbnail((700,700))
img.save('grid_small.png')
print('ok')
