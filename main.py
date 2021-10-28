import tkinter as tk
from env import Env
from world import World, Stone, Sand


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
for x in range(5, 20):
	world.set_cell(x, 15, Stone())

env.add_callback("Button-3", lambda x, y: world.set_cell(x, y, Sand()) or world.draw(env))
env.add_callback("Button-2", lambda x, y: world.update() or world.draw(env))

world.draw(env)
env.loop()
