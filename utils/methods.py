# from cairosvg import svg2png
# from io import BytesIO
# import xml.etree.ElementTree as svg

def hexToDec(hex_color: str | int) -> int:
    decimal_color = int(hex_color, 16)
    return decimal_color

def rgbDistance(clr1: str | int, clr2: str | int) -> int:
    color1 = hexToDec(clr1)
    color2 = hexToDec(clr2)
    
    r1, g1, b1 = (color1 >> 16) & 0xFF, (color1 >> 8) & 0xFF, color1 & 0xFF
    r2, g2, b2 = (color2 >> 16) & 0xFF, (color2 >> 8) & 0xFF, color2 & 0xFF
    
    distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
    
    return distance

def fillCountry(src: str, color: str, ids: list[int]):
    with open(src) as _basedata:
        content = _basedata.read()
        items = content.split('\n')
    
    newItems = []
    
    for id in ids:
        for item in items:
            if item.startswith(f'<path id="c{id}"') or item.startswith(f'<g id="c{id}"'):
                newItems.append(item.replace('fill="#6CAF54"', f'fill="{color}"'))
            else:
                newItems.append(item)
    
    return '\n'.join(newItems)

def editCount(src: str, text: str, id: int):
    with open(src) as _basedata:
        content = _basedata.read()
        items = content.split('\n')
    
    newItems = []
    
    for item in items:
        if item.startswith(f'<text id="n{id}"'):
            newItems.append(item.replace(f'>{id}<', f'>{id} ({text})<'))
        else:
            newItems.append(item)

    return '\n'.join(newItems)

"""
def getAttachmentFromSvg(data: str, name: str = 'image') -> discord.File:
    pngdata = BytesIO(svg2png(data))

    return discord.File(pngdata, filename = f'{name}.png')
"""