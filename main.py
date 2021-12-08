import tkinter as tk
from env import Env
from world import World, Air, Stone, Sand, Water
from time import sleep, time
from PIL import Image
from io import BytesIO
from os import urandom
import re


def pre_params(f, *args, **kwargs):
	def wrapper(*args_, **kwargs_):
		return f(*args, *args_, **kwargs, **kwargs_)
	return wrapper


def save_frame_(canvas):
	fileName = f"frames/frame_{save_frame.frame_count}.png"
	print(fileName)
	postscript = canvas.postscript()
	stream = BytesIO(postscript.encode())
	img = Image.open(stream)
	img.save(fileName, 'png')
	save_frame.frame_count += 1
#save_frame.frame_count = 0


def save_frame(canvas):
	postscript = canvas.postscript()
	postscript = re.sub(r"fill.*?stroke", "fill", postscript, flags=re.DOTALL)
	open("lol.esp", "w").write(postscript)
	stream = BytesIO(postscript.encode())
	img = Image.open(stream)
	save_frame.frames.append(img)
save_frame.frames = []
def save_video():
	if len(save_frame.frames) < 2:
		return
	img, *imgs = save_frame.frames
	fileName = f"videos/{urandom(16).hex()}.gif"
	print(fileName)
	img.save(fp=fileName, format='GIF', append_images=imgs, save_all=True, optimize=True, duration=20, loop=0)


def update_cell(cell):
	return
	old = cell.COLOR
	cell.COLOR = "red"
	world.draw(env)
	sleep(0.05)
	cell.COLOR = old


def add_cell(x, y):
	world.set_cell(x, y, BLOCK())
	if not UPDATE:
		world.draw(env, DEBUG)


BLOCK = Sand
UPDATE = False
DEBUG = False
SAVE = False
def change_block(block):
	global BLOCK
	BLOCK = block
def change_update(x, y):
	global UPDATE
	UPDATE = not UPDATE
def change_save():
	global SAVE
	if SAVE:
		save_video()
	SAVE = not SAVE
	print("SAVE:", SAVE)


def step():
	start = time()
	world.update(update_cell)
	env.win.title(f"{int((time()-start)*1000)}ms")
	world.draw(env, DEBUG)
	if SAVE:
		save_frame(env.can)

	
def loop():
	if UPDATE:
		step()
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
env.bind_key(65, step)
env.bind_key(39, change_save)

world.draw(env, DEBUG)
loop()
env.loop()
