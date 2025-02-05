"""
We typically have a 26×26 or 30×30 frequency matrix,
from which we extract 8, 16, or 24 lines and columns.

❓ Is it significantly faster to extract those n lines and columns
from a n×n matrix rather than a 26×26 or 30×30 one? (n = 8, 16, 24)
👉 No major difference in speed.

The used indices will be built by combining a fixed list for n-8 indices
and a permutation of the 8 others, given as a tuple.
We also know that using a numpy array to address a matrix is faster than using a list.
❓ Is it overall faster to use numpy array in his situation?
👉 No difference.
"""

import numpy as np
from numpy.typing import NDArray
from benchmark import Benchmark

full_matrix: NDArray  # n_total × n_total
full_indices: list[int] | NDArray[np.intp]
small_matrix: NDArray  # n_extracted × n_extracted
small_indices: list[int] | NDArray[np.intp]


def rand_indices(max: int, number: int) -> list[int]:
    return np.argsort(np.random.rand(max))[:number].tolist()  # type: ignore


def setup_full_v_small(n_total: int, n_extracted: int, np_idx: bool = True):
    global full_matrix, full_indices, small_matrix, small_indices
    n_total = n_total
    n_extracted = n_extracted
    full_matrix = np.random.rand(n_total, n_total)
    full_indices = rand_indices(n_total, n_extracted)
    sorted_indices = sorted(full_indices)
    small_matrix = full_matrix[sorted_indices, :][:, sorted_indices]
    small_indices = [sorted_indices.index(i) for i in full_indices]
    if np_idx:
        full_indices = np.array(full_indices)
        small_indices = np.array(small_indices)


def extract_full():
    """from full matrix"""
    return full_matrix[full_indices, :][:, full_indices]


def extract_small():
    """from small matrix"""
    return small_matrix[small_indices, :][:, small_indices]


matrix: NDArray
list_indices_fixed: list[int]
np_indices_fixed: NDArray[np.intp]
np8_indices_fixed: NDArray[np.int8]
tuple_indices_moved: tuple[int, ...]


def setup_numpy_v_list_idx(n_total: int, n_extracted: int):
    global matrix, list_indices_fixed, np_indices_fixed, np8_indices_fixed, tuple_indices_moved
    matrix = np.random.rand(n_total, n_total)
    indices = rand_indices(n_total, n_extracted)
    tuple_indices_moved = tuple(indices[-8:])
    list_indices_fixed = indices[:-8]
    np_indices_fixed = np.array(list_indices_fixed)
    np8_indices_fixed = np.array(list_indices_fixed, dtype=np.int8)


def list_idx():
    """with list indices"""
    indices = list_indices_fixed + list(tuple_indices_moved)
    return matrix[indices, :][:, indices]


def numpy_idx():
    """with numpy indices"""
    indices = np.append(np_indices_fixed, tuple_indices_moved)
    return matrix[indices, :][:, indices]


def numpy_idx_int8():
    """with numpy indices built from list"""
    indices = np.append(np8_indices_fixed, tuple_indices_moved)
    return matrix[indices, :][:, indices]


if __name__ == "__main__":
    bm = Benchmark(sets_per_test=1000, runs_per_set=1000)
    for n_total in [26, 30]:
        for n_extracted in [8, 16, 24]:
            for np_idx in [True, False]:
                setup_full_v_small(n_total, n_extracted, np_idx)
                assert np.all(extract_full() == extract_small())
                r = " (NP)" if np_idx else ""
                bm.add_case(
                    f"{n_extracted} of {n_total}{r}",
                    eval(
                        f"lambda: setup_full_v_small({n_total},{n_extracted},{np_idx})"
                    ),
                )
    bm.set_functions([extract_full, extract_small])
    print("\n")
    bm.report()
    print()
    bm.report(normalize_with=0)
    # ▲ No major improvement when extracting from smaller matrices

    bm = Benchmark(sets_per_test=1000, runs_per_set=1000)
    for n_total in [26, 30]:
        for n_extracted in [8, 16, 24]:
            setup_numpy_v_list_idx(n_total, n_extracted)
            assert np.all(list_idx() == numpy_idx())
            assert np.all(list_idx() == numpy_idx_int8())
            bm.add_case(
                f"{n_extracted} of {n_total}",
                eval(f"lambda: setup_numpy_v_list_idx({n_total},{n_extracted})"),
            )
    bm.set_functions([list_idx, numpy_idx, numpy_idx_int8])
    print("\n")
    bm.report()
    print()
    bm.report(normalize_with=0)
    # ▲ No difference between indexing methods
