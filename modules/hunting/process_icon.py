import os
from PIL import Image

def process_favicon():
    img_path = 'mosquete.png'
    out_path = 'static/favicon.png'
    
    if not os.path.exists(img_path):
        print(f"Erro: {img_path} não encontrado.")
        return
        
    img = Image.open(img_path).convert("RGBA")
    data = img.getdata()
    
    # Assume que a cor de fundo é a cor do pixel (0,0)
    bg_color = data[0]
    
    new_data = []
    # Tolerância para a cor de fundo (para casos de compressão jpeg etc)
    tolerance = 30
    
    for item in data:
        # Verifica se o pixel é próximo à cor de fundo
        diff = abs(item[0] - bg_color[0]) + abs(item[1] - bg_color[1]) + abs(item[2] - bg_color[2])
        if diff < tolerance:
            # Fundo -> transparente
            new_data.append((255, 255, 255, 0))
        else:
            # Objeto -> branco sólido
            # Verifica se o alpha não é 0 originalmente
            if item[3] > 0:
                new_data.append((255, 255, 255, 255))
            else:
                new_data.append((255, 255, 255, 0))
                
    img.putdata(new_data)
    
    # Redimensiona para um tamanho legal de favicon se for muito grande
    img.thumbnail((128, 128), Image.Resampling.LANCZOS)
    
    img.save(out_path, "PNG")
    print(f"Favicon salvo em {out_path}!")

if __name__ == '__main__':
    process_favicon()
