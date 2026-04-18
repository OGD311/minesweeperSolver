from mss.darwin import MSS as mss
import cv2
import numpy as np

from PIL import Image
from PIL import ImageDraw
import os
import time

import random
import pyautogui

gridSizeX = 8
gridSizeY = 8
gridSize = 20

grid = [[None for i in range(gridSizeX)] for j in range(gridSizeY)]

startPosX = 1052
startPosY = 445

restartX = 1135
restartY = 630

shouldClick = True

def printGrid():
    for row in grid:
        print(row)


def insert(x, y, value):
    grid[y][x] = value
    
def getValue(x, y):
    return grid[y][x]
    
def colourToValue(color):
    match color:
        case (0, 0, 0):
            return -1
        case (0, 0, 245):
            return 1
        case (53, 121, 32):
            return 2
        case (234, 51, 35):
            return 3
        case (0, 0, 118):
            return 4
        case (112, 19, 11):
            return 5
        case (44, 103, 103):
            return 6
        case (53, 121, 122):
            return 7
        
        case _:
            return 0
    
    
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
                
                
    draw = ImageDraw.Draw(img)
    for bomb in definiteBombs:
        x0 = bomb[0] *gridSize
        y0 = bomb[1] *gridSize
        x1 = x0 + int(19 * gridSize / 20)
        y1 = y0 + int(19 * gridSize / 20)
        
        draw.rectangle((x0, y0, x1, y1), outline=(255, 0, 0), width=2)
        
        
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
                unsure_probabilities[pos] = unsure_probabilities[pos] + prob
            else:
                unsure_probabilities[pos] = prob
    
    
    for pos, prob in unsure_probabilities.items():
        x0 = pos[0] * gridSize
        y0 = pos[1] * gridSize
        x1 = x0 + int(19 * gridSize / 20)
        y1 = y0 + int(19 * gridSize / 20)
        
        draw.text((x0 + 2, y0), f"{float(max(min(round(prob, 2), 1), 0))}", fill=(255, 0, 0))
        draw.rectangle((x0, y0, x1, y1), outline=(255, 165, 0), width=2)
    
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
                    

    for cell in safe_cells:
        x0 = cell[0]*gridSize
        y0 = cell[1]*gridSize
        x1 = x0 + int(19 * gridSize / 20)
        y1 = y0 + int(19 * gridSize / 20)
        
        
        draw.rectangle((x0, y0, x1, y1), outline=(0, 255, 0), width=2)
        
        
    for cell in safe_cells:
        x0 = cell[0]*gridSize
        y0 = cell[1]*gridSize
        if (shouldClick):
            pyautogui.click(startPosX + x0 + ((gridSize / 20) * 5), startPosY + y0 + ((gridSize / 20) * 5), duration=0)
    
    if len(safe_cells) == 0 and len(unsure_probabilities) > 0 and shouldClick:
        pos, prob = min(unsure_probabilities.items(), key=lambda item: item[1])
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
        
    if len(definiteBombs) == 0 and len(safe_cells) == 0 and len(unsure_probabilities) == 0:
        restart()
    
    # printGrid()

    # img.show()
    
    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv2.imshow("Screenshot", frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break