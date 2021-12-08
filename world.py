from random import randrange
import struct


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
		free_water = lambda cell: isinstance(cell, Water) and cell.last_update != world.current_update
		free = lambda cell: cell is None or free_water(cell)
		if free(world.get_cell(x, y+1, False)):
			return x, y+1
		left  = world.free_cells(free, (x-1, y+1), (x-1, y))
		right = world.free_cells(free, (x+1, y+1), (x+1, y))
		if left and right:
			if randrange(2):
				return x-1, y+1
			return x+1, y+1
		if left:
			return x-1, y+1
		if right:
			return x+1, y+1


class Water(Cell):
	COLOR = "#55F"
	need_update = True
	def __init__(self):
		super().__init__()
		self.last_dir = randrange(2)
	def update(self, x, y, world):
		free = lambda cell: cell is None
		free_or_water = lambda cell: cell is None or isinstance(cell, Water)
		free_sand = lambda cell: isinstance(cell, Sand) and cell.last_update != world.current_update
		if world.get_cell(x, y+1) is None:
			return x, y+1
		left_up  = world.get_cell(x-1, y, False)
		right_up = world.get_cell(x+1, y, False)
		left  = world.get_cell(x-1, y+1, False)
		right = world.get_cell(x+1, y+1, False)

		if free_sand(right_up) and free_or_water(left_up) and free_or_water(left):
			return x+1, y
		if free_sand(left_up) and free_or_water(right_up) and free_or_water(right):
			return x-1, y
		left_up  = free(left_up)
		right_up = free(right_up)
		left  = left_up and free(left)
		right = right_up and free(right)
		if left and right:
			if randrange(2):
				return x-1, y+1
			return x+1, y+1
		if left:
			self.last_dir = randrange(2)
			return x-1, y+1
		if right:
			self.last_dir = randrange(2)
			return x+1, y+1
		if left_up and right_up:
			if self.last_dir:
				return x-1, y
			return x+1, y
		if left_up:
			self.last_dir = 1
			return x-1, y
		if right_up:
			self.last_dir = 0
			return x+1, y


class World:
	MAGIC = b"\x5a\xd0\x01"
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
		#ctx.update()

	def save(self, path):
		to_id_map = {
			type(None): 0,
			Stone: 1,
			Sand: 2,
			Water: 3
		}
		to_id = lambda cell: to_id_map[type(cell)]
		bits = 8
		max_count = 8
		buffer = self.MAGIC
		buffer += struct.pack("h", self.w)
		for (x, y), chunk in self.chunks.items():
			chunk.empty = True
			if chunk.verify():
				continue
			buffer += struct.pack("2h", x, y)
			last = to_id(chunk.mat[0][0])
			count = 0
			for line in chunk.mat:
				for cell in line:
					current = to_id(cell)
					if current == last:
						count += 1
					else:
						while count > 0:
							buffer += struct.pack("2B", last, min(max_count, count)-1)
							count -= max_count
						last = current
						count = 1
			buffer += struct.pack("2B", last, count-1)
		with open(path, "wb") as f:
			f.write(buffer)
		print(f"Successfully saved to: {path}")

	def load(path):
		to_cell_map = {
			0: Air,
			1: Stone,
			2: Sand,
			3: Water
		}
		with open(path, "rb") as f:
			buffer = f.read()
		if not buffer.startswith(World.MAGIC):
			raise ValueError("Magic number doesn't match, wrong file type.")
		try:
			cursor = len(World.MAGIC)
			w, = struct.unpack_from("h", buffer, cursor)
			world = World(w)
			size = w*w
			cursor += 2
			while cursor < len(buffer):
				x, y = struct.unpack_from("2h", buffer, cursor)
				ox, oy = x*w, y*w
				cursor += 4
				count = 0
				chunk = Chunk(x, y, w)
				while count < size:
					cell, c = struct.unpack_from("2B", buffer, cursor)
					for i in range(count, count+c+1):
						chunk.mat[i//w][i%w] = to_cell_map[cell]()
					cursor += 2
					count += c+1
				chunk.reset_bound()
				chunk.need_update = True
				chunk.mx = 0
				chunk.my = 0
				chunk.Mx = w-1
				chunk.My = w-1
				world.chunks[(x, y)] = chunk
			return world
		except Exception as e:
			print(e)
			raise Exception("Wrong file format")


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
