from layout_builder import LayoutBuilder
from local_types import NpVector, NpArray1D, NpArray2D, T_NpData
import numpy as np


class MatrixBasedLayoutBuilder(LayoutBuilder):
	__costs_freqs_1d: list[
		tuple[NpVector, NpVector]
	]  # [(key costs, char frequencies), …]
	__costs_freqs_2d: list[
		tuple[NpArray2D, NpArray2D]
	]  # [(interkey costs, char pair frequencies), …]

	def add_key_costs(
		self, key_costs: NpVector | NpArray1D, char_frequencies: NpVector | NpArray1D
	):
		# TODO should ensure conversion from matrix to vector
		# TODO should assert valid size
		self.__add_to_data(self.__costs_freqs_1d, key_costs, char_frequencies)

	def add_interkey_costs(
		self, interkey_costs: NpArray2D, char_pair_frequencies: NpArray2D
	):
		# TODO should assert valid size
		self.__add_to_data(self.__costs_freqs_2d, interkey_costs, char_pair_frequencies)

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
