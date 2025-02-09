import pytest
from pytest_dparam import d_parametrize

from engram.scoring import Key


class Test_Key:
    class Test_Init:
        def test_basic_case(self) -> None:
            key = Key("L3", 0, 0)
            assert key.hand == "L"
            assert key.finger == 3
            key = Key("R1", 0, 0)
            assert key.hand == "R"
            assert key.finger == 1

        def test_thumb(self) -> None:
            key = Key("LT", 0, 0)
            assert key.finger == 0

        def test_lower_case_input(self) -> None:
            key = Key("l3", 0, 0)
            assert key.hand == "L"
            assert key.finger == 3
            key = Key("r1", 0, 0)
            assert key.hand == "R"
            assert key.finger == 1
            key = Key("lt", 0, 0)
            assert key.hand == "L"
            assert key.finger == 0

        def test_ignore_extra_char(self) -> None:
            key = Key("L3*", 0, 0)
            assert key.hand == "L"
            assert key.finger == 3
            key = Key("R1*", 0, 0)
            assert key.hand == "R"
            assert key.finger == 1

        @d_parametrize(
            {
                "invalid_hand": {"input": "B3"},
                "invalid_finger_number": {"input": "L6"},
                "invalid_finger_str": {"input": "LX"},
                "missing_hand": {"input": "3"},
                "missing_finger": {"input": "L"},
            }
        )
        def test_raise_ValueError_if_invalid(self, input: str) -> None:
            with pytest.raises(ValueError):
                Key(input, 0, 0)

        def test_store_v_dist_and_h_dist(self) -> None:
            key = Key("L3", 5, 8)
            assert key.dx == 5
            assert key.dy == 8
            key = Key("L3", dx=5, dy=8)
            assert key.dx == 5
            assert key.dy == 8

    class Test_Str:
        @d_parametrize(
            {
                "LT": {"finger": "LT"},
                "L1": {"finger": "L1"},
                "R2": {"finger": "R2"},
                "L3": {"finger": "L3"},
                "R4": {"finger": "R4"},
            }
        )
        def test_proper_finger(self, finger: str) -> None:
            key = Key(finger, 0, 0)
            assert str(key)[:2] == finger

        @d_parametrize(
            {
                "L3 00 00": {"finger": "L3", "x": 00, "y": 00, "expected": "L3●"},
                "L3 00 +1": {"finger": "L3", "x": 00, "y": +1, "expected": "L3↑"},
                "L3 00 -1": {"finger": "L3", "x": 00, "y": -1, "expected": "L3↓"},
                "R3 00 00": {"finger": "R3", "x": 00, "y": 00, "expected": "R3●"},
                "R3 00 +1": {"finger": "R3", "x": 00, "y": +1, "expected": "R3↑"},
                "R3 00 -1": {"finger": "R3", "x": 00, "y": -1, "expected": "R3↓"},
                "L1 +1 00": {"finger": "L1", "x": +1, "y": 00, "expected": "L1→"},
                "R1 +1 00": {"finger": "R1", "x": +1, "y": 00, "expected": "R1←"},
                "L4 -1 00": {"finger": "L4", "x": -1, "y": 00, "expected": "L4←"},
                "R4 -1 00": {"finger": "R4", "x": -1, "y": 00, "expected": "R4→"},
                "L1 +1 +1": {"finger": "L1", "x": +1, "y": +1, "expected": "L1↗"},
                "L1 +1 -1": {"finger": "L1", "x": +1, "y": -1, "expected": "L1↘"},
                "R1 +1 +1": {"finger": "R1", "x": +1, "y": +1, "expected": "R1↖"},
                "R1 +1 -1": {"finger": "R1", "x": +1, "y": -1, "expected": "R1↙"},
                "L4 -1 +1": {"finger": "L4", "x": -1, "y": +1, "expected": "L4↖"},
                "L4 -1 -1": {"finger": "L4", "x": -1, "y": -1, "expected": "L4↙"},
                "R4 -1 +1": {"finger": "R4", "x": -1, "y": +1, "expected": "R4↗"},
                "R4 -1 -1": {"finger": "R4", "x": -1, "y": -1, "expected": "R4↘"},
                "L1 +2 00": {"finger": "L1", "x": +2, "y": 00, "expected": "L1→→"},
                "L1 +2 +1": {"finger": "L1", "x": +2, "y": +1, "expected": "L1↗→"},
                "L1 +1 +2": {"finger": "L1", "x": +1, "y": +2, "expected": "L1↗↑"},
                "L1 +2 +2": {"finger": "L1", "x": +2, "y": +2, "expected": "L1↗↗"},
                "R4 -2 00": {"finger": "R4", "x": -2, "y": 00, "expected": "R4→→"},
                "R4 -2 -1": {"finger": "R4", "x": -2, "y": -1, "expected": "R4↘→"},
                "R4 -1 -2": {"finger": "R4", "x": -1, "y": -2, "expected": "R4↘↓"},
                "R4 -2 -2": {"finger": "R4", "x": -2, "y": -2, "expected": "R4↘↘"},
            }
        )  # fmt: skip
        def test_with_movement(
            self, finger: str, x: int, y: int, expected: str
        ) -> None:
            key = Key(finger, 0, 0)
            key.dx = x
            key.dy = y
            assert str(key) == expected
