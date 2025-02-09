"""
CONCLUSIONS:

Regarding mismatches with original 32×32 flow matrices:
- outward:
    Original implementation mistakenly ignored side keys.
- skip_row_1away:
    Original implementation mistakenly included 4↔27 (L1↑↔L1↘) and 13↔30 (R1↑↔R1↙)
    (which are already included in skip_row_0away!),
    instead of 4↔27 (L2↑↔L1↘) and 14↔30 (R2↑↔R1↙).
- skip_row_2away:
    Original implementation forgot 2↔27 (L3↑↔L1↘) and 15↔30 (R3↑↔R1↙)
    (while 10↔25 (L3↓↔L1↗) and 23↔28 (R3↓↔R1↖) are included!).
- skip_row_3away:
    Original implementation forgot 1↔27 (L4↑↔L1↘)
    (while 9↔25 (L4↓↔L1↗) and 16↔30 (R4↑↔R1↙) are included!).
We also ignore:
- shorter_above:
    It is very badly defined, and covered through more accurate penalties.
"""

# ruff:noqa: E731

from typing import Callable, Literal

import numpy as np
from numpy.typing import NDArray
from og_flow_matrix_code import create_32x32_flow_matrix as og_flow_matrix

_VERBOSE_WARNING: bool = False


class Key:
    name: str
    hand: Literal["L", "R"]
    finger: Literal[0, 1, 2, 3, 4]
    dx: int
    dy: int

    def __init__(self, name: str) -> None:
        self.name = name
        hand, finger, dir = name
        self.hand = hand  # type:ignore
        self.finger = int(finger)  # type:ignore
        assert self.hand in ["L", "R"]
        assert self.finger in [0, 1, 2, 3, 4]
        self.dx, self.dy = {
            "↖": (-1,+1), "↑": (0,+1), "↗": (+1,+1),
            "←": (-1, 0), "•": (0, 0), "→": (+1, 0),
            "↙": (-1,-1), "↓": (0,-1), "↘": (+1,-1),
        }[dir]  # fmt:skip
        if self.hand == "R":
            self.dx *= -1

    def __str__(self) -> str:
        return self.name


# Keys covered by the original code, in the order it uses:
keys = [
    Key(k)
    for k in """
        L4↑ L3↑ L2↑ L1↑ L4• L3• L2• L1• L4↓ L3↓ L2↓ L1↓
        R1↑ R2↑ R3↑ R4↑ R1• R2• R3• R4• R1↓ R2↓ R3↓ R4↓
        L1↗ L1→ L1↘ R1↖ R1← R1↙ R4↗ R4→
    """.split()
]


# >  List of the original penalties  (condition-based rewrite)


type KeyPenaltyCondition = Callable[[Key], bool]
type PairPenaltyCondition = Callable[[Key, Key], bool]

# ▾ Actually a parameter with no effect (not penalty computed)
no_penalties: list[str] = ["adjacent_offset"]

# ▼ Condition tested for each key of the bigram.
#   Penalty applied twice if condition applies twice.
key_penalties: dict[str, KeyPenaltyCondition] = {
    "lateral": lambda k: k.dx != 0,
    "not_home_row": lambda k: k.dy != 0,
    "side_top": lambda k: k.dy > 0 and k.finger in [1, 4],
    "inside_top": lambda k: k.finger == 1 and k.dy > 0,
}

# ▼ Condition tested for the bigram.
pair_penalties: dict[str, PairPenaltyCondition] = {  # Same hand is assumed!
    "outward": lambda k0, k1: k0.hand == k1.hand and k1.finger > k0.finger,
    "same_hand": lambda k0, k1: k0.hand == k1.hand,
    "skip_row_0away": lambda k0, k1: (
        k0.hand == k1.hand and k0.finger == k1.finger and abs(k0.dy - k1.dy) > 1
    ),
    "skip_row_1away": lambda k0, k1: (
        k0.hand == k1.hand
        and abs(k0.finger - k1.finger) == 1
        and abs(k0.dy - k1.dy) > 1
    ),
    "skip_row_2away": lambda k0, k1: (
        k0.hand == k1.hand
        and abs(k0.finger - k1.finger) == 2
        and abs(k0.dy - k1.dy) > 1
    ),
    "skip_row_3away": lambda k0, k1: (
        k0.hand == k1.hand
        and abs(k0.finger - k1.finger) == 3
        and abs(k0.dy - k1.dy) > 1
    ),
    "same_finger": lambda k0, k1: (
        k0.hand == k1.hand and k0.finger == k1.finger and k0 != k1
    ),
}

# ▼ Condition tested for the bigram and its reversion.
#   Penalty applied twice if condition applies twice.
sym_pair_penalties: dict[str, PairPenaltyCondition] = {
    # ▲ Will be swapped too. Same hand is assumed!
    "side_above_1away": lambda k0, k1: (
        k0.hand == k1.hand
        and (k0.finger, k1.finger) in ((1, 2), (4, 3))
        # ▲ ⇔ k0.finger in [1, 4] and abs(k1.finger - k0.finger) == 1
        and k0.dy > k1.dy
    ),
    "side_above_2away": lambda k0, k1: (
        k0.hand == k1.hand
        and (k0.finger, k1.finger) in ((1, 3), (4, 2))
        # ▲ ⇔ k0.finger in [1, 4] and abs(k1.finger - k0.finger) == 2
        and k0.dy > k1.dy
    ),
    "side_above_3away": lambda k0, k1: (
        k0.hand == k1.hand and (k0.finger, k1.finger) == (1, 4) and k0.dy != k1.dy
        # ⇔ k0.finger in [1, 4] and abs(k1.finger - k0.finger) == 3 and k0.dy > k1.dy
    ),  # 💡 It's index and little finger. This rule is questionable.
    "index_above": lambda k0, k1: (
        k0.finger == 1
        and k0.dy > 0
        and (k1.hand != k0.hand or k0 == k1 or k1.dy < k0.dy)
    ),
    "middle_above_ring": lambda k0, k1: (
        k0.hand == k1.hand and (k0.finger, k1.finger) == (2, 3) and k0.dy > k1.dy
    ),  # 💡 Not an issue for me?
    "ring_above_middle": lambda k0, k1: (
        k0.hand == k1.hand and (k0.finger, k1.finger) == (2, 3) and k0.dy < k1.dy
    ),
}

# ▼ Knowingly ignored penalties
ignore_penalties: list[str] = ["shorter_above"]


# >  Comparison with what the original code gives


def penalty_application_str(flow_matrix: NDArray) -> str:
    """Return a string representing to which key pairs the penalty applies."""
    char = lambda x: "·" if x == 1 else "█"
    s: list[list[float]] = flow_matrix.tolist()  # type: ignore
    return "\n".join("".join(map(char, line)) for line in s)


def application_mismatch_str(expected: NDArray, obtained: NDArray) -> str:
    applied_str: Callable[[float], str] = lambda x: "█" if x < 1 else "·"
    diff_str: Callable[[float], str] = lambda x: (
        "\033[42m+\033[0m" if x < 0 else "\033[41m-\033[0m" if x > 0 else "·"
    )
    exp: NDArray = np.vectorize(applied_str)(expected)
    obt: NDArray = np.vectorize(applied_str)(obtained)
    diff: NDArray = np.vectorize(diff_str)(obtained - expected)
    n = exp.shape[1]
    lines = [f"{'Expected:':{n}}   {'Got:':{n}}   {'Diff:':{n}}"]
    for i, mat_lines in enumerate(zip(exp, obt, diff)):
        lines.append(f"{'   '.join(''.join(line) for line in mat_lines)}   {i + 1}")
    for k in [0, 1]:
        d = [f"{i} "[k] for i in range(1, n + 1)]
        lines.append("   ".join(["".join(d)] * 3))
    d = [str(i)[0] for i in range(1, n + 1)]
    return "\033[0m" + "\n".join(lines)


def expected_with_penalty(penalty: str) -> NDArray:
    og_flow_args = og_flow_matrix.__code__.co_varnames[
        : og_flow_matrix.__code__.co_argcount
    ]
    args = {a: 1.0 for a in og_flow_args}
    args[penalty] = 0.5
    expected = og_flow_matrix(**args)
    return expected


def check_no_penalties() -> None:
    for penalty in no_penalties:
        expected = expected_with_penalty(penalty)
        assert np.all(expected == 1)


def check_key_penalties() -> None:
    for penalty, condition in key_penalties.items():
        expected = expected_with_penalty(penalty)
        s = np.array([[int(condition(k)) for k in keys]])
        s = s + s.T
        s = 0.5**s
        __assert_matrix_matching(s, expected, name=penalty)


def check_pair_penalties() -> None:
    for penalty_col, symmetry in ((pair_penalties, False), (sym_pair_penalties, True)):
        for penalty, condition in penalty_col.items():
            expected = expected_with_penalty(penalty)
            s = np.array([[int(condition(k0, k1)) for k1 in keys] for k0 in keys])
            if symmetry:
                s += np.array([[int(condition(k1, k0)) for k1 in keys] for k0 in keys])
            s = 0.5**s
            __assert_matrix_matching(s, expected, name=penalty)


def __assert_matrix_matching(obtained: NDArray, expected: NDArray, name: str) -> None:
    if not np.array_equal(obtained, expected):
        assert np.array_equal(obtained[:24, :24], expected[:24, :24]), (
            f"{name}:\n\n{application_mismatch_str(expected, obtained)}"
        )
        descr = (
            "\n" + application_mismatch_str(expected, obtained)
            if _VERBOSE_WARNING
            else ""
        )
        print(
            f"\033[93m⚠ \033[92m{name}\033[93m: "
            + f"Mismatch for 32 keys (but not 24)\033[0m{descr}"
        )


def report_penalty_coverage() -> None:
    og_flow_args = og_flow_matrix.__code__.co_varnames[
        : og_flow_matrix.__code__.co_argcount
    ]
    uncovered = set(og_flow_args)
    for penalty_col in (
        no_penalties,
        key_penalties,
        pair_penalties,
        sym_pair_penalties,
        ignore_penalties,
    ):
        uncovered -= set(penalty_col)
    if not uncovered:
        print("\nAll penalties covered. ✅\n")
        return
    print("\nUncovered penalties:\n" + "".join(f"   {p}\n" for p in uncovered))


if __name__ == "__main__":
    # _VERBOSE_WARNING = True
    check_no_penalties()
    check_key_penalties()
    check_pair_penalties()
    report_penalty_coverage()
