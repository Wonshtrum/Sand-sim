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
		chunk.mat[x%self.w][y%self.w] = cell
		chunk.empty = False

	def update(self):
		self.current_update += 1
		chunks = list(self.chunks.values())
		for chunk in chunks:
			chunk.update(self)
			if chunk.empty:
				del self.chunks[(chunk.x, chunk.y)]

	def draw(self, ctx):
		ctx.clear()
		for chunk in self.chunks.values():
			chunk.draw(ctx)


class Chunk:
	def __init__(self, x, y, w):
		self.x = x
		self.y = y
		self.w = w
		self.mat = [[None]*w for _ in range(w)]
		self.empty = True

	def update(self, world):
		ox = self.x*self.w
		oy = self.y*self.w
		self.empty = True
		for x in range(self.w):
			for y in range(self.w):
				cell = self.mat[x][y]
				if cell is not None:
					self.empty = False
					xy = cell._update(ox+x, oy+y, world)
					if xy is not None:
						self.mat[x][y] = None
						world.set_cell(*xy, cell)

	def draw(self, ctx):
		ox = self.x*self.w
		oy = self.y*self.w
		for x in range(self.w):
			for y in range(self.w):
				cell = self.mat[x][y]
				if cell is not None:
					ctx.draw(ox+x, oy+y, fill=cell.COLOR)
		ctx.draw(ox, oy, self.w, self.w, fill="", outline="lime", width=3)
