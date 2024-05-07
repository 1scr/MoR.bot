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