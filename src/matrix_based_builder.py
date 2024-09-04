from layout_builder import LayoutBuilder
from local_types import NpVector, NpArray1D, NpArray2D, T_NpData
import numpy as np


class MatrixBasedLayoutBuilder(LayoutBuilder):
	_costs_freqs_1d: list[tuple[NpVector, NpVector]]
	"""[(key costs, char frequencies), …]"""
	_costs_freqs_2d: list[tuple[NpArray2D, NpArray2D]]
	"""[(interkey costs, char pair frequencies), …]"""

	__costs_freqs_1d_current: list[tuple[NpVector, NpVector]]
	__costs_freqs_2d_current: list[tuple[NpArray2D, NpArray2D]]
	__fixed_chars: list[int]

	def __init__(self):
		super().__init__()
		self._costs_freqs_1d = []
		self._costs_freqs_2d = []

	def add_key_costs(
		self,
		key_costs: NpVector | NpArray1D | list[float],
		char_frequencies: NpVector | NpArray1D | list[float],
	):
		"""
		Add a key costs matrix and its associated character frequencies.
		"""
		key_costs = self.__as_vector(key_costs)
		char_frequencies = self.__as_vector(char_frequencies)
		self.__add_to_data(self._costs_freqs_1d, key_costs, char_frequencies)
		self.__assert_compatible_sizes()

	def add_interkey_costs(
		self,
		interkey_costs: NpArray2D | list[list[float]],
		char_pair_frequencies: NpArray2D | list[list[float]],
	):
		"""
		Add an interkey costs matrix and its associated bigram frequencies.
		"""
		interkey_costs = self.__as_array(interkey_costs)
		char_pair_frequencies = self.__as_array(char_pair_frequencies)
		self.__add_to_data(self._costs_freqs_2d, interkey_costs, char_pair_frequencies)
		self.__assert_compatible_sizes()

	def score(self, open_chars_order: tuple[int, ...] = []) -> float:
		self.__precompute_if_needed()
		score = 0
		chars = self.__fixed_chars + list(open_chars_order)
		for costs, freqs in self.__costs_freqs_1d_current:
			score += np.sum(costs * freqs[chars])
		for costs, freqs in self.__costs_freqs_2d_current:
			score += np.sum(costs * freqs[chars, :][:, chars])
		return float(score)

	@staticmethod
	def __as_vector(data: NpVector | NpArray1D | list[float]) -> NpVector:
		if not isinstance(data, np.ndarray):
			data = np.array(data)
		if data.ndim == 1:
			return data
		shape = data.shape
		data = data.flatten()
		if data.size != max(shape):
			raise ValueError(
				"Expected a vector of 1D array (i.e. sized 1 in all dimensions but one)"
			)
		return data

	@staticmethod
	def __as_array(data: NpArray2D | list[list[float]]) -> NpVector:
		original = True
		if not isinstance(data, np.ndarray):
			data = np.array(data)
			original = False
		if data.ndim == 2:
			return np.copy(data) if original else data
		raise ValueError("Expected a 2D array")

	@staticmethod
	def __add_to_data(
		data: list[tuple[T_NpData, T_NpData]], costs: T_NpData, frequencies: T_NpData
	):
		for d_costs, d_freqs in data:
			if np.array_equal(d_freqs, frequencies):
				d_costs += costs
				return
			if np.array_equal(d_costs, costs):
				d_freqs += frequencies
				return
		data.append((np.copy(costs), np.copy(frequencies)))

	def __assert_compatible_sizes(self) -> None:
		n_costs: None | int = None
		n_freqs: None | int = None
		for costs, freqs in self._costs_freqs_1d:
			if n_costs is None:
				n_costs = costs.size
				n_freqs = freqs.size
			if costs.shape != (n_costs,):
				raise ValueError("Mismatch in cost vector sizes.")
			if freqs.shape != (n_freqs,):
				raise ValueError("Mismatch in frequency vector sizes.")
		for costs, freqs in self._costs_freqs_2d:
			if n_costs is None:
				n_costs = costs.shape[0]
				n_freqs = freqs.shape[0]
			if costs.shape != (n_costs, n_costs):
				raise ValueError("Mismatch in cost matrix sizes.")
			if freqs.shape != (n_freqs, n_freqs):
				raise ValueError("Mismatch in frequency n_freqs sizes.")

	def __precompute_if_needed(self) -> None:
		if self._config_changed:
			self.__precompute()
			self._config_changed = False

	def __precompute(self) -> None:
		keys = list(self._fixed.keys()) + self._opened_keys
		self.__costs_freqs_1d_current = [
			(costs[keys], freqs) for costs, freqs in self._costs_freqs_1d
		]
		self.__costs_freqs_2d_current = [
			(costs[keys, :][:, keys], freqs) for costs, freqs in self._costs_freqs_2d
		]
		self.__fixed_chars = list(self._fixed.values())
