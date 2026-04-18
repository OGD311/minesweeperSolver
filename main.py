from mss.darwin import MSS as mss
import cv2
import numpy as np

from PIL import Image
from PIL import ImageDraw
import os
import time

import random
import pyautogui
import math


gridSizeX = 31
gridSizeY = 16
gridSize = 20

grid = [[None for i in range(gridSizeX)] for j in range(gridSizeY)]

startPosX = 821
startPosY = 408

restartX = 1240
restartY = 750

shouldClick = True

def printGrid():
    for row in grid:
        print(" ".join("." if cell is None else str(cell) for cell in row))


def insert(x, y, value):
    grid[y][x] = value
    
def getValue(x, y):
    return grid[y][x]

def cosine_similarity(c1, c2):
    dot = sum(a*b for a, b in zip(c1, c2))
    norm1 = math.sqrt(sum(a*a for a in c1))
    norm2 = math.sqrt(sum(b*b for b in c2))
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)

COLOR_MAP = {
    (0, 0, 0): -1,
    (0, 0, 245): 1,
    (53, 121, 32): 2,
    (234, 51, 35): 3,
    (100, 100, 156): 4,
    (116, 27, 20): 5,
    (44, 103, 103): 6,
    (53, 121, 122): 7
}

def colourToValue(color):
    if color == (0, 0, 0):
        return -1
    
    max_similarity = -1
    closest_value = 0
    for ref_color, value in COLOR_MAP.items():
        similarity = cosine_similarity(color, ref_color)
        if similarity > max_similarity:
            max_similarity = similarity
            closest_value = value

    return closest_value if max_similarity >= 0.95 else 0


def findAdjacent(x, y):
    directions = [(-1, 1), (-1, 0), (-1, -1), (0, 1), (0, -1), (1, 1), (1, 0), (1, -1)]
    
    positions = {}
    
    for dir in directions:
        try:
            newX = x + dir[0]
            newY = y + dir[1]
            
            if (newX < 0 or newY < 0):
                continue
            
            val = grid[newY][newX]
            
            positions[newX, newY] = val
            
        except:
            pass
        
    return positions
        
  
def restart():
    global grid
    grid = [[None for i in range(gridSizeX)] for j in range(gridSizeY)]

    pyautogui.click(x=restartX, y=restartY, duration=0)
    time.sleep(0.5)

    global shouldClick
    shouldClick = True
    
    # Click randomly to start next round
    x0 = random.randint(1, gridSizeX - 1) * gridSize
    y0 = random.randint(1, gridSizeY - 1) * gridSize
    pyautogui.click(startPosX + x0 + ((gridSize / 20) * 5), startPosY + y0 + ((gridSize / 20) * 5), duration=0)



while True:
    sct = mss()
    
    monitor = {"top": startPosY, "left": startPosX, "width": gridSizeX *gridSize, "height": gridSizeY *gridSize}
    # monitor = sct.monitors[1]
    sct_img = sct.grab(monitor)

    img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
    
    positions = {}
    

    pixels = img.load()
    pixelColours = set()
    for x in range(sct_img.width):
        for y in range(sct_img.height):
            gridX = x //gridSize
            gridY = y //gridSize
            
            
            if (x %gridSize == 0 and y %gridSize == 0):
                sample = img.getpixel((x + 11, y + 10))
                
                pixelColours.add(sample)
                
                isClicked = img.getpixel((x + int(15 * gridSize / 20), y + int(19 * gridSize / 20))) != (123, 123, 123)
                
                isFlagged = img.getpixel((x + int(6 * gridSize / 20), y + int(8 * gridSize / 20))) == (234, 51, 35)
                
                if colourToValue(sample) == 0 and isFlagged:
                    positions[(gridX, gridY)] = "FLAG"
                elif isClicked:
                    positions[(gridX, gridY)] = colourToValue(sample)
                else:
                    positions[(gridX, gridY)] = None
                
                # Center
                img.putpixel((x + int(11 * gridSize / 20), y + int(10 * gridSize / 20)), (0, 255, 0))
                # Flag
                img.putpixel((x + int(6 * gridSize / 20), y + int(8 * gridSize / 20)), (0, 0, 255)) 
                # Clicked
                img.putpixel((x + int(15 * gridSize / 20), y + int(19 * gridSize / 20)), (255, 0, 0))
    
    
    # find definite bomb cells
    definiteBombs = set()
    
    for key, value in positions.items():
        x = key[0]
        y = key[1]
        insert(x, y, value)
        
        if value is None or value == "FLAG":
            continue
        
        if value is not None and value != "FLAG":
            adjacents = findAdjacent(x, y)
            unknown = {k: v for k, v in adjacents.items() if v is None}
            flags = {k: v for k, v in adjacents.items() if v == "FLAG"}

            if value - len(flags) == len(unknown) and value - len(flags) > 0:
                definiteBombs.update(unknown.keys())
                # print(f"{(key[0], key[1])}: {adjacents}")
                
    # draw bomb cells
    draw = ImageDraw.Draw(img)
    for bomb in definiteBombs:
        x0 = bomb[0] *gridSize
        y0 = bomb[1] *gridSize
        x1 = x0 + int(19 * gridSize / 20)
        y1 = y0 + int(19 * gridSize / 20)
        
        draw.rectangle((x0, y0, x1, y1), outline=(255, 0, 0), width=2)
        
    # find unsure cells
    unsure_probabilities = {}
    for key, value in positions.items():
        x, y = key
        if value is None or value == "FLAG" or value == 0:
            continue
        
        adjacents = findAdjacent(x, y)
        unknown_neighbors = {pos for pos, val in adjacents.items() if val is None and pos not in definiteBombs}
        flagged_neighbors = {pos for pos, val in adjacents.items() if val == "FLAG" or pos in definiteBombs}

        remaining_mines = value - len(flagged_neighbors)
        if remaining_mines <= 0:
            continue

        for pos in unknown_neighbors:
            prob = remaining_mines / len(unknown_neighbors)
            if pos in unsure_probabilities:
                unsure_probabilities[pos] =  min(max(unsure_probabilities[pos] + prob, 0), 1)
            else:
                unsure_probabilities[pos] =  min(max(prob, 0), 1)
                
                
    weighted_probs = {}

    for pos, prob in unsure_probabilities.items():
        x, y = pos
        adjacents = findAdjacent(x, y)
        neighbor_probs = []
        for (nx, ny), val in adjacents.items():
            if val not in [None, "FLAG"]:
                flags = sum(1 for p, v in findAdjacent(nx, ny).items() if v == "FLAG")
                unknowns = [p for p, v in findAdjacent(nx, ny).items() if v is None]
                remaining = val - flags
                if pos in unknowns and len(unknowns) > 0:
                    neighbor_prob = remaining / len(unknowns)
                    neighbor_probs.append(neighbor_prob)
        
        if neighbor_probs:
            combined_prob = max(neighbor_probs)
        else:
            combined_prob = prob
        
        weighted_probs[pos] = combined_prob
    
    # draw unsure cells + probabilities
    for pos, prob in weighted_probs.items():
        x0 = pos[0] * gridSize
        y0 = pos[1] * gridSize
        x1 = x0 + int(19 * gridSize / 20)
        y1 = y0 + int(19 * gridSize / 20)
        
        probability = max(0.0, min(float(prob), 1.0))
        draw.text((x0 + 2, y0), f"{probability:.0%}", fill=(255, 0, 0))
        draw.rectangle((x0, y0, x1, y1), outline=(255, 165, 0), width=2)
    
    # define safe cells
    safe_cells = set()
        
    for key, value in positions.items():
        x, y = key
        if value is None or value == "FLAG":
            continue
        if value == 0:
            continue

        adjacents = findAdjacent(x, y)
        unknown_neighbors = {pos for pos, val in adjacents.items() if val is None and pos not in definiteBombs}
        flagged_neighbors = {pos for pos, val in adjacents.items() if val == "FLAG" or pos in definiteBombs}

        remaining_mines = value - len(flagged_neighbors)

        if remaining_mines == 0:
            safe_cells.update(unknown_neighbors)
                    

    # draw rectangle around safe cell
    for cell in safe_cells:
        x0 = cell[0]*gridSize
        y0 = cell[1]*gridSize
        x1 = x0 + int(19 * gridSize / 20)
        y1 = y0 + int(19 * gridSize / 20)
        
        
        draw.rectangle((x0, y0, x1, y1), outline=(0, 255, 0), width=2)
        
    # click on all safe cells
    for cell in safe_cells:
        x0 = cell[0]*gridSize
        y0 = cell[1]*gridSize
        if (shouldClick):
            pyautogui.click(startPosX + x0 + ((gridSize / 20) * 5), startPosY + y0 + ((gridSize / 20) * 5), duration=0)
    
    # Click on lowest probability unsure    
    if len(safe_cells) == 0 and len(weighted_probs) > 0 and shouldClick:
        pos, prob = min(weighted_probs.items(), key=lambda item: item[1])
        x0 = pos[0] * gridSize
        y0 = pos[1] * gridSize
        pyautogui.click(startPosX + x0 + ((gridSize / 20) * 5), startPosY + y0 + ((gridSize / 20) * 5), duration=0)
                
        
    if any(-1 in row for row in grid):
        print("Mine hit! Game Over")
        
        print("==== UNSURE COLOURS ====")
        for sample in pixelColours:
            out = colourToValue(sample)
            if (out == 0):
                print(sample)
        shouldClick = False
        
        restart()
        # print("\033c", end="")
        # exit(0)
    else:
        shouldClick = True
        
    if len(definiteBombs) == 0 and len(safe_cells) == 0 and len(weighted_probs) == 0:
        restart()
    
    # printGrid()

    # img.show()
    
    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv2.imshow("Screenshot", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    
    # printGrid()
    # print("\033c", end="")