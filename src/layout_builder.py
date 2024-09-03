from typing import Iterable
from itertools import permutations


class LayoutBuilder:
	_fixed: dict[int, int]
	_opened_keys: list[int]
	_opened_chars: list[int]
	_config_changed: bool

	def __init__(self) -> None:
		self._fixed = {}
		self._opened_keys = []
		self._opened_chars = []
		self._config_changed = True

	def fix(self, keys: Iterable[int], chars: Iterable[int]):
		"""
		Assign the characters given by `chars` to the keys given by `keys`.
		Characters and keys are given as identifying indices, in matching orders.
		"""
		for k, c in zip(keys, chars):
			self._fixed[k] = c
		self.__remove_fixed_from_opened()
		self._config_changed = True

	assign = fix

	def open(self, keys: Iterable[int], chars: Iterable[int]):
		"""
		Open the keys `keys` to the possible characters `chars`.
		Characters and keys are given as identifying indices.
		"""
		for k in keys:
			if k not in self._opened_keys:
				self._opened_keys.append(k)
		for c in chars:
			if c not in self._opened_chars:
				self._opened_chars.append(c)
		self.__remove_opened_from_fixed()
		self._config_changed = True

	def optimal_fill(
		keys_to_fill: Iterable[int] | int,
		fill_with: Iterable[int] | None = None,
		remap: bool = False,
	):
		"""
		Optimally fills a given set of keys with a given set of characters.
		“Optimally” is defined by the highest score, as given by the `.score(…)` method.
		Arguments are:
		- `keys_to_fill`: The set of keys to fill, as identified by their index.
		If instead, an single integer *n* is provided, then the first *n* usable keys
		(by increasing index) are used.
		(“Usable” ⇔ “unmapped” if `remap = False` (default), “any” else.)
		- `fill_with`: The set of characters to use to fill the keys, as identified by their index.
		If instead, `None` is provided (default), then the first *n* usable characters
		(by increasing index) are used.
		(“Usable” ⇔ “unmapped” if `remap = False` (default), “any” else.)
		- `remap`: If `False` (default), already set keys and characters are ignored/untouched.
		"""
		# TODO Is it needed? This would be a shorthand for various step, but is it really useful?
		pass

	def score(self, open_chars_order: tuple[int, ...] = []) -> float:
		"""
		Score the provided layout.\n
		⚠ This method must be implemented by a subclass.\n
		The layout is defined by:
		- the fixed assignment defined with the method `.fix(…)` (or `.assign(…)`),
		- the temporary assignment for the opened keys provided by `open_chars_order`.
		  (The open keys are declared with the method `.open(…)`.)\n
		By default, `open_chars_order` is given as raw identifying indices.
		However, the `score` method can use something else
		(typically, indices for `._opened_chars` as defined through `open(…)`),
		provided that `.opened_permutations()` is overwritten accordingly.\n
		If precomputation should be done once for a given set of fixed and opened keys and characters,
		the method can use `self._config_changed` to know when such precomputation is needed,
		as `._config_changed` is set to `True` by `.fix(…)`/`.assign(…)` and `.open(…)`. Typically:
		```python
		def score(self, open_chars_order: tuple[int, ...] = []) -> float:
			if self._config_changed:
				# Precomputation
				self._config_changed = False
			# Computation
		```
		"""
		raise NotImplementedError()

	def opened_permutations(self) -> Iterable[tuple[int, ...]]:
		"""
		Provide all the permutations of opened characters,
		in a format compatible with the `.score(…)` method.\n
		(By default, each permutation is given as the ordered tuple of the character identifying indices.
		If instead for example, the `.score(…)` method uses the indices of the characters within
		`self._opened_chars`, `.opened_permutations()` should be overwritten to:
		`return permutations(range(self._opened_chars))`.)
		"""
		return permutations(self._opened_chars)

	def __remove_fixed_from_opened(self):
		self._opened_keys = [k for k in self._opened_keys if k not in self._fixed]
		set_chars = set(self._fixed.values())
		self._opened_chars = [k for k in self._opened_chars if k not in set_chars]

	def __remove_opened_from_fixed(self):
		for k in self._opened_keys:
			if k in self._fixed:
				del self._fixed[k]
