import tkinter as tk
from env import Env
from world import World, Stone, Sand
from time import sleep


win = tk.Tk()
txt = tk.StringVar()
label = tk.Label(win, textvariable=txt)
env = Env(win, 100, 50, 4, txt, bg="black")
env.can.pack()
label.pack()

world = World(8)
for x in range(5,20):
	for y in range(5,10):
		world.set_cell(x, y, Sand())
for x in range(25):
	world.set_cell(x, 15, Stone())

def update_cell(cell):
	return
	old = cell.COLOR
	cell.COLOR = "red"
	world.draw(env)
	sleep(0.01)
	cell.COLOR = old

def add_cell(x, y):
	world.set_cell(x, y, Sand())

def change_update(x, y):
	global UPDATE
	UPDATE = not UPDATE

UPDATE = False
def loop():
	if UPDATE:
		world.update(update_cell)
	world.draw(env)
	env.win.after(20, loop)

env.add_callback("Button-3", add_cell)
env.add_callback("B3-Motion", add_cell)
env.add_callback("Button-2", change_update)

loop()
env.loop()
