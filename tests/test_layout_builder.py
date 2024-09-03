from pytest_dparam import d_parametrize
from layout_builder import LayoutBuilder
from math import factorial


class Test_fix:
	def test_base_case(self):
		builder = LayoutBuilder()

		builder.fix([1, 3, 5], [8, 7, 6])

		assert builder._fixed == {1: 8, 3: 7, 5: 6}

	def test_config_change_recorded(self):
		builder = LayoutBuilder()
		builder._config_changed = False

		builder.fix([1, 3, 5], [8, 7, 6])

		assert builder._config_changed

	def test_successive_use(self):
		builder = LayoutBuilder()

		builder.fix([1, 3, 5], [8, 7, 6])
		builder.fix([2, 4], [9, 0])

		assert builder._fixed == {1: 8, 3: 7, 5: 6, 2: 9, 4: 0}

	def test_successive_use_with_intersect(self):
		builder = LayoutBuilder()

		builder.fix([1, 3, 5], [8, 7, 6])
		builder.fix([2, 3, 4], [9, 5, 0])

		assert builder._fixed == {1: 8, 3: 5, 5: 6, 2: 9, 4: 0}

	def test_works_with_open(self):
		builder = LayoutBuilder()
		builder.open([1, 2, 3], [6, 7, 9])

		builder.fix([1, 3, 5], [8, 7, 6])

		assert builder._fixed == {1: 8, 3: 7, 5: 6}

	def test_remove_from_opened(self):
		builder = LayoutBuilder()
		builder.open([1, 2, 3], [6, 7, 9])

		builder.fix([1, 3, 5], [8, 7, 6])

		assert builder._opened_keys == [2]
		assert builder._opened_chars == [9]

	def test_assign_as_alias(self):
		builder = LayoutBuilder()
		assert builder.fix == builder.assign


class Test_open:
	def test_base_case(self):
		builder = LayoutBuilder()

		builder.open([1, 3, 5], [8, 7, 6])

		assert sorted(builder._opened_keys) == [1, 3, 5]
		assert sorted(builder._opened_chars) == [6, 7, 8]

	def test_config_change_recorded(self):
		builder = LayoutBuilder()
		builder._config_changed = False

		builder.open([1, 3, 5], [8, 7, 6])

		assert builder._config_changed

	def test_successive_use(self):
		builder = LayoutBuilder()

		builder.open([1, 3, 5], [8, 7, 6])
		builder.open([2, 4], [9, 0])

		assert sorted(builder._opened_keys) == [1, 2, 3, 4, 5]
		assert sorted(builder._opened_chars) == [0, 6, 7, 8, 9]

	def test_successive_use_with_intersect(self):
		builder = LayoutBuilder()

		builder.open([1, 3, 5], [8, 7, 6])
		builder.open([2, 3, 4], [9, 7, 0])

		assert sorted(builder._opened_keys) == [1, 2, 3, 4, 5]
		assert sorted(builder._opened_chars) == [0, 6, 7, 8, 9]

	def test_works_with_fix(self):
		builder = LayoutBuilder()
		builder.fix([1, 2, 3], [6, 7, 8])

		builder.open([1, 3, 5], [8, 6, 9])

		assert sorted(builder._opened_keys) == [1, 3, 5]
		assert sorted(builder._opened_chars) == [6, 8, 9]

	def test_remove_from_fixed(self):
		builder = LayoutBuilder()
		builder.fix([1, 2, 3], [6, 7, 8])

		builder.open([1, 3, 5], [8, 6, 9])

		assert builder._fixed == {2: 7}


def test_opened_permutations():
	builder = LayoutBuilder()
	keys = [0, 1, 2, 3, 4]
	chars = [3, 6, 8, 4, 9]
	builder.open(keys, chars)

	permutations = builder.opened_permutations()

	chars_set = set(chars)
	perm_set = set()
	for p in permutations:
		assert set(p) == chars_set
		perm_set.add(p)
	assert len(perm_set) == factorial(len(chars))
