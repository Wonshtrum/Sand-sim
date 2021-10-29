from random import randrange


class Cell:
	COLOR = "#FFF"
	need_update = False
	def __init__(self):
		self.last_update = None

	def _update(self, x, y, world):
		if self.last_update == world.current_update:
			return
		result =  self.update(x, y, world)
		if result is not None:
			self.last_update = world.current_update
		return result

	def update(self, x, y, world):
		pass


def Air():
	return None


class Stone(Cell):
	COLOR = "#AAA"


class Sand(Cell):
	COLOR = "#FF8"
	need_update = True
	def update(self, x, y, world):
		free = lambda cell: cell is None or (isinstance(cell, Water) and cell.last_update != world.current_update)
		if free(world.get_cell(x, y+1, False)):
			return x, y+1
		left  = world.free_cells(free, (x-1, y+1), (x-1, y))
		right = world.free_cells(free, (x+1, y+1), (x+1, y))
		if left and right:
			if randrange(2):
				return x-1, y+1
			return x+1, y+1
		elif left:
			return x-1, y+1
		elif right:
			return x+1, y+1


class Water(Cell):
	COLOR = "#55F"
	need_update = True
	def update(self, x, y, world):
		if world.get_cell(x, y+1) is None:
			return x, y+1
		left_up  = world.get_cell(x-1, y, False) is None
		right_up = world.get_cell(x+1, y, False) is None
		left  = left_up  and world.get_cell(x-1, y+1, False) is None
		right = right_up and world.get_cell(x+1, y+1, False) is None
		if left and right:
			if randrange(2):
				return x-1, y
			return x+1, y+1
		elif left:
			return x-1, y+1
		elif right:
			return x+1, y+1
		if left_up and right_up:
			if randrange(2):
				return x-1, y
			return x+1, y
		elif left_up:
			return x-1, y
		elif right_up:
			return x+1, y


class World:
	def __init__(self, w):
		self.w = w
		self.chunks = {}
		self.current_update = 0

	def get_chunk(self, x, y, create=True):
		key = (x//self.w, y//self.w)
		chunk = self.chunks.get(key)
		if chunk is None and create:
			self.chunks[key] = chunk = Chunk(*key, self.w)
		return chunk

	def get_cell(self, x, y, create=True):
		chunk = self.get_chunk(x, y, create)
		if chunk is None:
			return None
		return chunk.mat[x%self.w][y%self.w]

	def set_cell(self, x, y, cell):
		chunk = self.get_chunk(x, y)
		nx = x%self.w
		ny = y%self.w
		chunk.mat[nx][ny] = cell
		chunk.bound(nx, ny, cell)

	def free_cells(self, predicate, *positions):
		if predicate is None:
			predicate = lambda cell: cell is None
		return all(predicate(self.get_cell(*position)) for position in positions)

	def update(self, callback=None):
		if callback is None:
			callback = lambda cell: None
		self.current_update += 1
		chunks = sorted(self.chunks.values(), key=lambda chunk: -chunk.y)
		for chunk in chunks:
			chunk.update(self, callback)
			if chunk.empty and chunk.verify():
				del self.chunks[(chunk.x, chunk.y)]

	def draw(self, ctx, debug=True):
		ctx.clear()
		for chunk in self.chunks.values():
			chunk.draw(ctx, self, debug)
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
		if not self.need_update:
			return
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
						old = world.get_cell(*xy, False)
						if old is not None:
							old.last_update = world.current_update
							self.bound(x, y, old)
						self.mat[x][y] = old
						world.set_cell(*xy, cell)
						callback(cell)
					else:
						self.bound(x, y, cell)

	def verify(self):
		for x in range(self.w):
			for y in range(self.w):
				if self.mat[x][y] is not None:
					self.empty = False
		return self.empty

	def reset_bound(self):
		self.need_update = False
		self.empty = True
		self.mx = self.w
		self.my = self.w
		self.Mx = 0
		self.My = 0
		return
		self.mx = 0
		self.my = 0
		self.Mx = self.w-1
		self.My = self.w-1

	def bound(self, x, y, cell):
		self.need_update = True
		if cell is None:
			return
		self.empty = False
		if cell.need_update:
			self.mx = min(self.mx, x)
			self.my = min(self.my, y)
			self.Mx = max(self.Mx, x)
			self.My = max(self.My, y)

	def draw(self, ctx, world, debug):
		ox = self.x*self.w
		oy = self.y*self.w
		for x in range(self.w):
			for y in range(self.w):
				cell = self.mat[x][y]
				if cell is not None:
					ctx.draw(ox+x, oy+y, fill=cell.COLOR)
		if debug:
			if self.need_update:
				ctx.draw(ox+self.mx, oy+self.my, self.Mx-self.mx+1, self.My-self.my+1, fill="", outline="blue", width=3)
				ctx.draw(ox, oy, self.w, self.w, fill="", outline="lime", width=3)
			else:
				ctx.draw(ox, oy, self.w, self.w, fill="", outline="red", width=3)
