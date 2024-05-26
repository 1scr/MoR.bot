# from cairosvg import svg2png
from io import BytesIO
import re
import xml.etree.ElementTree as svg

import discord

def hexToDec(hex_color):
    decimal_color = int(hex_color[1:], 16)
    return decimal_color

def rgbDistance(hex_color1, hex_color2):
    color1 = hexToDec(hex_color1)
    color2 = hexToDec(hex_color2)
    
    r1, g1, b1 = (color1 >> 16) & 0xFF, (color1 >> 8) & 0xFF, color1 & 0xFF
    r2, g2, b2 = (color2 >> 16) & 0xFF, (color2 >> 8) & 0xFF, color2 & 0xFF
    
    distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
    
    return distance

def compareColors(hex_color1, hex_color2):
    """
    L'idée c'est d'utiliser cette fonction pour éviter que les équipes créent des couleurs similaires.
    """

    return rgbDistance(hex_color1, hex_color2) > 128


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