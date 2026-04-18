from mss.darwin import MSS as mss
import cv2
import numpy as np

from PIL import Image
from PIL import ImageDraw
import os
import time


import pyautogui

gridSize = 16

grid = [[None for i in range(gridSize)] for j in range(gridSize)]

startPosX = 972
startPosY = 407

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
        case (6, 6, 120):
            return 4
        case (112, 19, 11):
            return 5
        
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
        
    


while True:
    sct = mss()
    
    monitor = {"top": startPosY, "left": startPosX, "width": gridSize * 20, "height": gridSize * 20}
    # monitor = sct.monitors[1]
    sct_img = sct.grab(monitor)

    img = Image.new("RGB", sct_img.size)

    pixels = zip(sct_img.raw[2::4], sct_img.raw[1::4], sct_img.raw[::4])
    img.putdata(list(pixels))
    
    positions = {}
    
    pyautogui.moveTo(startPosX, startPosY)
    

    pixels = img.load()
    for x in range(sct_img.width):
        for y in range(sct_img.height):
            gridX = x // 20
            gridY = y // 20
            
            
            if (x % 20 == 0 and y % 20 == 0):
                sample = img.getpixel((x + 11, y + 10))
                
                isClicked = img.getpixel((x + 15, y + 19)) != (123, 123, 123)
                
                isFlagged = img.getpixel((x + 6, y + 6)) == (234, 51, 35)
                
                if isFlagged:
                    positions[(gridX, gridY)] = "FLAG"
                elif isClicked:
                    positions[(gridX, gridY)] = colourToValue(sample)
                else:
                    positions[(gridX, gridY)] = None
                
                # Center
                img.putpixel((x + 11, y + 10), (0, 255, 0))
                # Flag
                img.putpixel((x + 6, y + 6), (0, 0, 255)) 
                # Clicked
                img.putpixel((x + 15, y + 19), (255, 0, 0))
                

                # draw = ImageDraw.Draw(img)
                # draw.text(
                #     (x + 2, y),
                #     f"{gridX},{gridY}",
                #     fill=(255, 0, 0),
                # )

    
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
                print(unknown)
                definiteBombs.update(unknown.keys())
                # print(f"{(key[0], key[1])}: {adjacents}")
                
                
    draw = ImageDraw.Draw(img)
    for bomb in definiteBombs:
        x0 = bomb[0] * 20
        y0 = bomb[1] * 20
        x1 = x0 + 19
        y1 = y0 + 19
        draw.rectangle((x0, y0, x1, y1), outline=(255, 0, 0), width=2)
        
        
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
                    
                    
    
    draw = ImageDraw.Draw(img)
    for cell in safe_cells:
        x0 = cell[0]*20
        y0 = cell[1]*20
        x1 = x0 + 19
        y1 = y0 + 19
        draw.rectangle((x0, y0, x1, y1), outline=(0, 255, 0), width=2)
        
    if any(-1 in row for row in grid):
        print("Mine hit! Game Over")
        # exit(0)
    
    printGrid()
    
    time.sleep(0.5)
    # img.show()
    
    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv2.imshow("Screenshot", frame)
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break
    
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')