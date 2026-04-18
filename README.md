# Minesweeper Solver
Python-based solver/tool for any minesweeper grid. Looks for shared tiles of known squares to locate tiles that are definitely bombs, and similarly can mark tiles that are known safe.
Currently highlights the squares on a cv2 window to show you where to click (Future plan is to make it solve the grid based on this!)
You may notice some inconsistencies, especially if you click very quickly, as my code is not the most efficient so takes ~200ms to estimate correctly. Also, due to how I handle deciding a tiles state, more tiles will be marked as bombs/safe as you progress.
You will have to manually click to first start (ie find a starting area) and also if there are no more known safe squares.
GUI:
<img width="399" height="318" alt="image" src="https://github.com/user-attachments/assets/2f9fab07-821d-4835-8486-c39005dd2129" />
Actual Grid:
<img width="624" height="323" alt="image" src="https://github.com/user-attachments/assets/8fb07728-1264-4baa-9cae-2d93fe279b59" />
