import numpy as np
import qutip as qt
from math import sqrt


# ===============================
# ЧАСТЬ 1 — Реализация через numpy
# ===============================

def build_numpy_operators():
    """Создание словаря однокубитовых операторов."""
    X = np.array([[0, 1],
                  [1, 0]], dtype=float)

    Z = np.array([[1, 0],
                  [0, -1]], dtype=float)

    H = (1 / sqrt(2)) * np.array([[1, 1],
                                  [1, -1]], dtype=float)

    return {"X": X, "Z": Z, "H": H}


def apply_numpy_circuit(state: np.ndarray, sequence: list[str]) -> np.ndarray:
    """
    Последовательно применяет операторы из sequence к состоянию state.
    """
    ops = build_numpy_operators()
    result = state.copy()

    for gate in sequence:
        result = ops[gate] @ result

    return result


# ===============================
# ЧАСТЬ 2 — Реализация через QuTiP
# ===============================

def build_qutip_operators():
    """Создание словаря операторов QuTiP."""
    X = qt.sigmax()
    Z = qt.sigmaz()
    H = (1 / sqrt(2)) * qt.Qobj([[1, 1],
                                 [1, -1]])

    return {"X": X, "Z": Z, "H": H}


def apply_qutip_circuit(state: qt.Qobj, sequence: list[str]) -> qt.Qobj:
    """
    Последовательно применяет операторы QuTiP к состоянию.
    """
    ops = build_qutip_operators()
    result = state

    for gate in sequence:
        result = ops[gate] * result

    return result


# ===============================
# Основная программа
# ===============================

def main():

    print("Задание 2")
    print("=" * 60)

    # Базовое состояние |1>
    np_state = np.array([[0.0],
                         [1.0]])

    qt_state = qt.ket("1")

    # Наборы схем
    circuits = {
        "Z → X": ["X", "Z"],
        "H → X": ["X", "H"],
        "X → Z → H": ["H", "Z", "X"],
        "H → Z → Z → X": ["X", "Z", "Z", "H"],
        "Z → Z → H → H": ["H", "H", "Z", "Z"],
        "X → X → X": ["X", "X", "X"]
    }

    print("\n--- numpy ---\n")
    print("Исходное состояние:\n", np_state, "\n")

    for name, seq in circuits.items():
        res = apply_numpy_circuit(np_state, seq)
        print(f"{name} :")
        print(res, "\n")

    print("=" * 60)

    print("\n--- QuTiP ---\n")
    print("Исходное состояние:\n", qt_state, "\n")

    for name, seq in circuits.items():
        res = apply_qutip_circuit(qt_state, seq)
        print(f"{name} :")
        print(res, "\n")


if __name__ == "__main__":
    main()
