# Minesweeper Solver
Python-based solver/tool for any minesweeper grid. Looks for shared tiles of known squares to locate tiles that are definitely bombs, and similarly can mark tiles that are known safe.<br/>
Currently highlights the squares on a cv2 window to show you where to click (Future plan is to make it solve the grid based on this!)<br/>
You may notice some inconsistencies, especially if you click very quickly, as my code is not the most efficient so takes ~200ms to estimate correctly. 
Also, due to how I handle deciding a tiles state, more tiles will be marked as bombs/safe as you progress.<br/>
You will have to manually click to first start (ie find a starting area) and also if there are no more known safe squares.<br/><br/>
### GUI:
<img width="399" height="318" alt="image" src="https://github.com/user-attachments/assets/2f9fab07-821d-4835-8486-c39005dd2129" /><br/>

### Exposed Grid:
<img width="624" height="323" alt="image" src="https://github.com/user-attachments/assets/8fb07728-1264-4baa-9cae-2d93fe279b59" />


## How to use
I use `uv` as my package manager (highly recommend!).
Once you install all packages, you will need to modify: 
- `gridSizeX`
- `gridSizeY`
- `gridSize`
- `startPosX`
- `startPosY`

I highly recommend [CardGamesIO](https://cardgames.io/minesweeper/) for using this. It was the site I used to develop and test this.
