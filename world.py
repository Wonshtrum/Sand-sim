from random import randrange


class Cell:
	COLOR = "#FFF"
	def __init__(self):
		self.last_update = None

	def _update(self, x, y, world):
		if self.last_update == world.current_update:
			return
		self.last_update = world.current_update
		return self.update(x, y, world)

	def update(self, x, y, world):
		pass


class Stone(Cell):
	COLOR = "#AAA"


class Sand(Cell):
	COLOR = "#FF8"
	def update(self, x, y, world):
		if world.get_cell(x, y+1) is None:
			return x, y+1
		left  = world.get_cell(x-1, y+1)
		right = world.get_cell(x+1, y+1)
		if left is None and right is None:
			if randrange(2):
				return x-1, y
			return x+1, y
		elif left is None:
			return x-1, y
		elif right is None:
			return x+1, y


class World:
	def __init__(self, w):
		self.w = w
		self.chunks = {}
		self.current_update = 0

	def get_chunk(self, x, y):
		key = (x//self.w, y//self.w)
		chunk = self.chunks.get(key)
		if chunk is None:
			self.chunks[key] = chunk = Chunk(*key, self.w)
		return chunk

	def get_cell(self, x, y):
		chunk = self.get_chunk(x, y)
		return chunk.mat[x%self.w][y%self.w]

	def set_cell(self, x, y, cell):
		chunk = self.get_chunk(x, y)
		nx = x%self.w
		ny = y%self.w
		chunk.mat[nx][ny] = cell
		chunk.bound(nx, ny)

	def update(self, callback=None):
		if callback is None:
			callback = lambda cell: None
		self.current_update += 1
		chunks = sorted(self.chunks.values(), key=lambda chunk: -chunk.y)
		for chunk in chunks:
			chunk.update(self, callback)
			if chunk.empty:
				del self.chunks[(chunk.x, chunk.y)]

	def draw(self, ctx):
		ctx.clear()
		for chunk in self.chunks.values():
			chunk.draw(ctx)
		ctx.update()


class Chunk:
	def __init__(self, x, y, w):
		self.x = x
		self.y = y
		self.w = w
		self.reset_bound()
		self.mat = [[None]*w for _ in range(w)]
		self.empty = True

	def update(self, world, callback):
		ox = self.x*self.w
		oy = self.y*self.w
		mx, my, Mx, My = self.mx, self.my, self.Mx, self.My
		self.reset_bound()
		for y in range(My, my-1, -1):
			for x in range(mx, Mx+1):
				cell = self.mat[x][y]
				if cell is not None:
					xy = cell._update(ox+x, oy+y, world)
					if xy is not None:
						self.mat[x][y] = None
						world.set_cell(*xy, cell)
						callback(cell)
					else:
						self.bound(x, y)

	def reset_bound(self):
		self.empty = True
		self.mx = self.w
		self.my = self.w
		self.Mx = 0
		self.My = 0

	def bound(self, x, y):
		self.empty = False
		self.mx = min(self.mx, x)
		self.my = min(self.my, y)
		self.Mx = max(self.Mx, x)
		self.My = max(self.My, y)

	def draw(self, ctx):
		ox = self.x*self.w
		oy = self.y*self.w
		for x in range(self.w):
			for y in range(self.w):
				cell = self.mat[x][y]
				if cell is not None:
					ctx.draw(ox+x, oy+y, fill=cell.COLOR)
		ctx.draw(ox+self.mx, oy+self.my, self.Mx-self.mx+1, self.My-self.my+1, fill="", outline="red", width=3)
		ctx.draw(ox, oy, self.w, self.w, fill="", outline="lime", width=3)
