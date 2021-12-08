import tkinter as tk


def int_(x):
	return int(x//1)


class Env:
	def __init__(self, win, col, row, scale, label=None, **kwargs):
		self.win = win
		self.scale = 2**scale
		self.ox = 0
		self.oy = 0
		self.width = col*self.scale
		self.height = row*self.scale
		self.label = label
		self.key_bound = {}

		self.can = tk.Canvas(
			win,
			width=self.width,
			height=self.height,
			xscrollincrement=1,
			yscrollincrement=1,
			**kwargs)

		self.bind("Button-1", self.scroll_start)
		self.bind("B1-Motion", self.scroll_move)
		self.bind("Button-4", self.zoom)
		self.bind("Button-5", self.zoom)
		self.bind("MouseWheel", self.zoom)
		self.bind("Motion", self.position)
		self.win.bind("<Key>", self.key_dispatcher)
		self.background = kwargs.get("bg", "black")

	def bind_mouse(self, event, callback):
		self.bind(event, lambda event: callback(*self.position(event)))

	def bind_key(self, key, callback):
		if key in self.key_bound:
			self.key_bound[key].append(callback)
		else:
			self.key_bound[key] = [callback]

	def bind(self, event, callback):
		self.can.bind(f"<{event}>", callback, add="+")

	def position(self, event):
		x, y = int_((event.x+self.ox-1)/self.scale), int_((event.y+self.oy-1)/self.scale)
		if self.label is not None:
			self.label.set(f"({x} ; {y})")
		return x, y

	def key_dispatcher(self, event):
		self.label.set(f"Key: {event.keycode}")
		for callback in self.key_bound.get(event.keycode, []):
			callback()

	def clear(self):
		self.can.delete("all")
		self.can.create_rectangle(self.ox, self.oy, self.ox+self.width+1, self.oy+self.height+1, fill=self.background, width=0)

	def update(self):
		self.can.update()

	def draw(self, x, y, w=1, h=1, **kwargs):
		if "width" not in kwargs:
			kwargs["width"] = 0
		ox, oy, s = self.ox, self.oy, self.scale
		return self.can.create_rectangle(x*s, y*s, (x+w)*s, (y+h)*s, **kwargs)

	def zoom(self, event):
		direction = event.num == 4 or event.delta>0
		factor = 2 if direction else 1/2
		new_scale = min(max(self.scale*factor, 1), 128)
		if new_scale != self.scale:
			self.scale = new_scale
			dx = event.x+self.ox
			dy = event.y+self.oy
			self.can.scale("all", 0, 0, factor, factor)
			self.can.xview_scroll(int(dx*(factor-1)), "units")
			self.can.yview_scroll(int(dy*(factor-1)), "units")
			self.update_origin()

	def update_origin(self):
		self.ox = self.can.canvasx(0)
		self.oy = self.can.canvasy(0)

	def scroll_start(self, event):
		self.can.scan_mark(event.x, event.y)
	def scroll_move(self, event):
		self.can.scan_dragto(event.x, event.y, gain=1)
		self.update_origin()

	def loop(self):
		self.win.mainloop()
