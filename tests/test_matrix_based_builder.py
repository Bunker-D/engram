from pytest_dparam import d_parametrize
from pytest import raises
import numpy as np
from matrix_based_builder import MatrixBasedLayoutBuilder


class Test_add_key_costs:
	input_formats = {
		"from_list": {
			"key_costs": [1, 2, 3],
			"char_freqs": [1, 2, 3, 4],
		},
		"from_np_vector": {
			"key_costs": np.array([1, 2, 3]),
			"char_freqs": np.array([1, 2, 3, 4]),
		},
		"from_np_array": [
			{
				"key_costs": np.array([[1, 2, 3]]),
				"char_freqs": np.array([[1, 2, 3, 4]]),
			},
			{
				"key_costs": np.array([[1], [2], [3]]),
				"char_freqs": np.array([[1], [2], [3], [4]]),
			},
		],
	}

	@d_parametrize(input_formats)
	def test_store_provided_data(self, key_costs, char_freqs):
		builder = MatrixBasedLayoutBuilder()

		builder.add_key_costs(key_costs, char_freqs)

		assert len(builder._costs_freqs_1d) == 1
		costs, freqs = builder._costs_freqs_1d[0]
		assert np.array_equal(costs, [1, 2, 3])
		assert np.array_equal(freqs, [1, 2, 3, 4])

	@d_parametrize(input_formats)
	def test_store_as_np_vectors(self, key_costs, char_freqs):
		builder = MatrixBasedLayoutBuilder()

		builder.add_key_costs(key_costs, char_freqs)

		costs, freqs = builder._costs_freqs_1d[0]
		assert type(costs).__name__ == "ndarray"
		assert type(freqs).__name__ == "ndarray"
		assert costs.shape == (3,)
		assert freqs.shape == (4,)

	def test_store_a_copy(self):
		builder = MatrixBasedLayoutBuilder()
		costs = np.array([1, 2, 3])
		freqs = np.array([1, 2, 3, 4])

		builder.add_key_costs(costs, freqs)
		costs[1] = 0
		freqs[1] = 0

		stored_costs, stored_freqs = builder._costs_freqs_1d[0]
		assert np.array_equal(stored_costs, [1, 2, 3])
		assert np.array_equal(stored_freqs, [1, 2, 3, 4])

	def test_store_successive_added_pairs(self):
		builder = MatrixBasedLayoutBuilder()
		costs_0 = [1, 2, 3]
		freqs_0 = [1, 2, 3, 4]
		costs_1 = [10, 20, 30]
		freqs_1 = [10, 20, 30, 40]

		builder.add_key_costs(costs_0, freqs_0)
		builder.add_key_costs(costs_1, freqs_1)

		stored_costs_0, stored_freqs_0 = builder._costs_freqs_1d[0]
		stored_costs_1, stored_freqs_1 = builder._costs_freqs_1d[1]
		assert np.array_equal(costs_0, stored_costs_0)
		assert np.array_equal(freqs_0, stored_freqs_0)
		assert np.array_equal(costs_1, stored_costs_1)
		assert np.array_equal(freqs_1, stored_freqs_1)

	def test_combine_when_same_costs(self):
		builder = MatrixBasedLayoutBuilder()
		costs = [1, 2, 3]
		freqs_0 = [1, 2, 3, 4]
		freqs_1 = [10, 20, 30, 40]
		freqs_total = [11, 22, 33, 44]

		builder.add_key_costs(costs, freqs_0)
		builder.add_key_costs(costs, freqs_1)

		assert len(builder._costs_freqs_1d) == 1
		stored_costs, stored_freqs = builder._costs_freqs_1d[0]
		assert np.array_equal(stored_costs, costs)
		assert np.array_equal(stored_freqs, freqs_total)

	def test_combine_when_same_freqs(self):
		builder = MatrixBasedLayoutBuilder()
		freqs = [1, 2, 3, 4]
		costs_0 = [1, 2, 3]
		costs_1 = [10, 20, 30]
		costs_total = [11, 22, 33]

		builder.add_key_costs(costs_1, freqs)
		builder.add_key_costs(costs_0, freqs)

		assert len(builder._costs_freqs_1d) == 1
		costs, freqs = builder._costs_freqs_1d[0]
		assert np.array_equal(costs, costs_total)
		assert np.array_equal(freqs, freqs)

	@d_parametrize(
		{
			"costs_is_list_of_lists": [
				{
					"costs": [[1, 2], [3, 4]],
					"freqs": [1, 2, 3, 4],
				},
				{
					"costs": [[1, 2], [3]],
					"freqs": [1, 2, 3, 4],
				},
			],
			"costs_is_np_2d_array": {
				"costs": np.array([[1, 2], [3, 4]]),
				"freqs": [1, 2, 3, 4],
			},
			"freqs_is_list_of_lists": [
				{
					"costs": [1, 2, 3],
					"freqs": [[1, 2], [3, 4]],
				},
				{
					"costs": [1, 2, 3],
					"freqs": [[1, 2], [3]],
				},
			],
			"freqs_is_np_2d_array": {
				"costs": [1, 2, 3],
				"freqs": np.array([[1, 2], [3, 4]]),
			},
		}
	)
	def test_invalid_size_raise_valueerror(self, costs, freqs):
		builder = MatrixBasedLayoutBuilder()

		with raises(ValueError):
			builder.add_key_costs(costs, freqs)

	@d_parametrize(
		{
			"costs_size": {
				"costs": [1, 2, 3],  # instead of size 2
				"freqs": [10, 20, 30],
			},
			"costs_size_same_freqs": {
				"costs": [1, 2, 3],  # instead of size 2
				"freqs": [1, 2, 3],  # same as pre-registered
			},
			"freqs_size": {
				"costs": [10, 20],
				"freqs": [1, 2],  # instead of size 3
			},
			"freqs_size_same_costs": {
				"costs": [1, 2],  # same as pre-registered
				"freqs": [1, 2],  # instead of size 3
			},
		}
	)
	def test_inconsistent_1d_sizes_raise_valueerror(self, costs, freqs):
		builder = MatrixBasedLayoutBuilder()
		builder.add_key_costs(
			key_costs=[1, 2],
			char_frequencies=[1, 2, 3],
		)

		with raises(ValueError):
			builder.add_key_costs(costs, freqs)

	@d_parametrize(
		{
			"costs_size": {
				"costs": [1, 2, 3],  # instead of size 2
				"freqs": [1, 2, 3],  # same as pre-registered
			},
			"freqs_size": {
				"costs": [1, 2],  # same as pre-registered
				"freqs": [1, 2],  # instead of size 3
			},
		}
	)
	def test_inconsistent_1d_2d_sizes_raise_valueerror(self, costs, freqs):
		builder = MatrixBasedLayoutBuilder()
		builder.add_interkey_costs(
			interkey_costs=[[1, 2], [3, 4]],
			char_pair_frequencies=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
		)

		with raises(ValueError):
			builder.add_key_costs(costs, freqs)


class Test_add_interkey_costs:
	input_formats = {
		"from_list_of_lists": {
			"key_costs": [[1, 2], [3, 4]],
			"char_freqs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
		},
		"from_np_array": {
			"key_costs": np.array([[1, 2], [3, 4]]),
			"char_freqs": np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
		},
	}

	@d_parametrize(input_formats)
	def test_store_provided_data(self, key_costs, char_freqs):
		builder = MatrixBasedLayoutBuilder()

		builder.add_interkey_costs(key_costs, char_freqs)

		assert len(builder._costs_freqs_2d) == 1
		costs, freqs = builder._costs_freqs_2d[0]
		assert np.array_equal(costs, [[1, 2], [3, 4]])
		assert np.array_equal(freqs, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

	@d_parametrize(input_formats)
	def test_store_as_np_arrays(self, key_costs, char_freqs):
		builder = MatrixBasedLayoutBuilder()

		builder.add_interkey_costs(key_costs, char_freqs)

		costs, freqs = builder._costs_freqs_2d[0]
		assert type(costs).__name__ == "ndarray"
		assert type(freqs).__name__ == "ndarray"
		assert costs.shape == (2, 2)
		assert freqs.shape == (3, 3)

	def test_store_a_copy(self):
		builder = MatrixBasedLayoutBuilder()
		costs = np.array([[1, 2], [3, 4]])
		freqs = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

		builder.add_interkey_costs(costs, freqs)
		costs[1][1] = 0
		freqs[1][1] = 0

		stored_costs, stored_freqs = builder._costs_freqs_2d[0]
		assert np.array_equal(stored_costs, [[1, 2], [3, 4]])
		assert np.array_equal(stored_freqs, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

	def test_store_successive_added_pairs(self):
		builder = MatrixBasedLayoutBuilder()
		costs_0 = [[1, 2], [3, 4]]
		freqs_0 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
		costs_1 = [[10, 20], [30, 40]]
		freqs_1 = [[10, 20, 30], [40, 50, 60], [70, 80, 90]]

		builder.add_interkey_costs(costs_0, freqs_0)
		builder.add_interkey_costs(costs_1, freqs_1)

		stored_costs_0, stored_freqs_0 = builder._costs_freqs_2d[0]
		stored_costs_1, stored_freqs_1 = builder._costs_freqs_2d[1]
		assert np.array_equal(costs_0, stored_costs_0)
		assert np.array_equal(freqs_0, stored_freqs_0)
		assert np.array_equal(costs_1, stored_costs_1)
		assert np.array_equal(freqs_1, stored_freqs_1)

	def test_combine_when_same_costs(self):
		builder = MatrixBasedLayoutBuilder()
		costs = [[1, 2], [3, 4]]
		freqs_0 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
		freqs_1 = [[10, 20, 30], [40, 50, 60], [70, 80, 90]]
		freqs_total = [[11, 22, 33], [44, 55, 66], [77, 88, 99]]

		builder.add_interkey_costs(costs, freqs_0)
		builder.add_interkey_costs(costs, freqs_1)

		assert len(builder._costs_freqs_2d) == 1
		stored_costs, stored_freqs = builder._costs_freqs_2d[0]
		assert np.array_equal(stored_costs, costs)
		assert np.array_equal(stored_freqs, freqs_total)

	def test_combine_when_same_freqs(self):
		builder = MatrixBasedLayoutBuilder()
		freqs = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
		costs_0 = [[1, 2], [3, 4]]
		costs_1 = [[10, 20], [30, 40]]
		costs_total = [[11, 22], [33, 44]]

		builder.add_interkey_costs(costs_1, freqs)
		builder.add_interkey_costs(costs_0, freqs)

		assert len(builder._costs_freqs_2d) == 1
		costs, freqs = builder._costs_freqs_2d[0]
		assert np.array_equal(costs, costs_total)
		assert np.array_equal(freqs, freqs)

	@d_parametrize(
		{
			"cost_is_1d_list": {
				"costs": [1, 2, 3, 4],
				"freqs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
			},
			"cost_is_np_vector": {
				"costs": np.array([1, 2, 3, 4]),
				"freqs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
			},
			"costs_is_not_square_list_of_lists": [
				{
					"costs": [[1, 2], [3, 4], [5, 6]],
					"freqs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
				},
				{
					"costs": [[1, 2], [3, 4], [5]],
					"freqs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
				},
			],
			"costs_is_not_square_2d_np_array": {
				"costs": np.array([[1, 2], [3, 4], [5, 6]]),
				"freqs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
			},
			"freqs_is_1d_list": {
				"costs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
				"freqs": [1, 2, 3, 4],
			},
			"freqs_is_np_vector": {
				"costs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
				"freqs": np.array([1, 2, 3, 4]),
			},
			"freqs_is_not_square_list_of_lists": [
				{
					"costs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
					"freqs": [[1, 2], [3, 4], [5, 6]],
				},
				{
					"costs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
					"freqs": [[1, 2], [3, 4], [5]],
				},
			],
			"freqs_is_not_square_2d_np_array": {
				"costs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
				"freqs": np.array([[1, 2], [3, 4], [5, 6]]),
			},
		}
	)
	def test_invalid_size_raise_valueerror(self, costs, freqs):
		builder = MatrixBasedLayoutBuilder()

		with raises(ValueError):
			builder.add_interkey_costs(costs, freqs)

	@d_parametrize(
		{
			"costs_size": {
				"costs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],  # instead of 2x2
				"freqs": [[10, 20, 30], [40, 50, 60], [70, 80, 90]],
			},
			"costs_size_same_freqs": {
				"costs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],  # instead of 2x2
				"freqs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],  # same as pre-registered
			},
			"freqs_size": {
				"costs": [[10, 20], [30, 40]],
				"freqs": [[1, 2], [3, 4]],  # instead of 3x3
			},
			"freqs_size_same_costs": {
				"costs": [[1, 2], [3, 4]],  # same as pre-registered
				"freqs": [[1, 2], [3, 4]],  # instead of 3x3
			},
		}
	)
	def test_inconsistent_2d_sizes_raise_valueerror(self, costs, freqs):
		builder = MatrixBasedLayoutBuilder()
		builder.add_interkey_costs(
			interkey_costs=[[1, 2], [3, 4]],
			char_pair_frequencies=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
		)

		with raises(ValueError):
			builder.add_interkey_costs(costs, freqs)

	@d_parametrize(
		{
			"costs_size": {
				"costs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],  # instead of 2x2
				"freqs": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
			},
			"freqs_size": {
				"costs": [[1, 2], [3, 4]],
				"freqs": [[1, 2], [3, 4]],  # instead of 3x3
			},
		}
	)
	def test_inconsistent_1d_2d_sizes_raise_valueerror(self, costs, freqs):
		builder = MatrixBasedLayoutBuilder()
		builder.add_key_costs(
			key_costs=[1, 2],
			char_frequencies=[1, 2, 3],
		)

		with raises(ValueError):
			builder.add_interkey_costs(costs, freqs)
