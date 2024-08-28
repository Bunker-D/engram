from typing import Iterable


class LayoutBuilder:
	layout: list[int]

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
		# TODO identify proper indices
		# TODO reduce_keyboard(…)
		# TODO for each permutation: score
		# TODO keep best
		pass

	def reduce_keyboard(self):
		raise NotImplementedError()

	def score(self) -> float:
		raise NotImplementedError()
