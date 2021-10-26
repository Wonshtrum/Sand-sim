import tkinter as tk
from env import Env


win = tk.Tk()
txt = tk.StringVar()
label = tk.Label(win, textvariable=txt)
env = Env(win, 100, 50, 2, txt, bg="black")
env.can.pack()
label.pack()
for x in range(5,20):
	for y in range(5,10):
		env.draw(x, y, width=1, outline="white")

env.loop()
