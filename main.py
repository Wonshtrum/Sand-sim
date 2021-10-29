import tkinter as tk
from env import Env
from world import World, Air, Stone, Sand, Water
from time import sleep, time


def pre_params(f, *args, **kwargs):
	def wrapper(*args_, **kwargs_):
		return f(*args, *args_, **kwargs, **kwargs_)
	return wrapper


def update_cell(cell):
	return
	old = cell.COLOR
	cell.COLOR = "red"
	world.draw(env)
	sleep(0.01)
	cell.COLOR = old


BLOCK = Sand
def change_block(block):
	global BLOCK
	BLOCK = block


def add_cell(x, y):
	world.set_cell(x, y, BLOCK())


def change_update(x, y):
	global UPDATE
	UPDATE = not UPDATE


UPDATE = False
DEBUG = False
def loop():
	if UPDATE:
		start = time()
		world.update(update_cell)
		env.win.title(f"{int((time()-start)*1000)}ms")
	world.draw(env, DEBUG)
	env.win.after(1, loop)


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

env.bind_mouse("Button-3", add_cell)
env.bind_mouse("B3-Motion", add_cell)
env.bind_mouse("Button-2", change_update)

keys = [90, 87, 88, 89, 83, 84, 85, 79, 80, 81]
blocks = [Air, Stone, Sand, Water]
for key, block in zip(keys, blocks):
	env.bind_key(key, pre_params(change_block, block))

loop()
env.loop()
