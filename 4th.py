# qrng.py - Квантовый генератор случайных чисел

import numpy as np
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from typing import List

# ==================== ИНТЕРФЕЙСЫ ====================

class Qubit(metaclass=ABCMeta):
    """Абстрактный класс кубита"""
    
    @abstractmethod
    def h(self):
        """Операция Адамара"""
        pass
    
    @abstractmethod
    def measure(self) -> bool:
        """Измерение кубита"""
        pass
    
    @abstractmethod
    def reset(self):
        """Сброс кубита в состояние |0⟩"""
        pass


class QuantumDevice(metaclass=ABCMeta):
    """Абстрактный класс квантового устройства"""
    
    @abstractmethod
    def allocate_qubit(self) -> Qubit:
        """Выделение кубита"""
        pass
    
    @abstractmethod
    def deallocate_qubit(self, qubit: Qubit):
        """Освобождение кубита"""
        pass
    
    @contextmanager
    def using_qubit(self):
        """Контекстный менеджер для безопасного использования кубита"""
        qubit = self.allocate_qubit()
        try:
            yield qubit
        finally:
            self.deallocate_qubit(qubit)


# ==================== СИМУЛЯТОР ====================

# Константы для симуляции
KET_0 = np.array([[1], [0]], dtype=complex)  # |0⟩ состояние
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)  # Матрица Адамара


class SimulatedQubit(Qubit):
    """Симулированный кубит"""
    
    def __init__(self):
        self.state = KET_0.copy()
    
    def h(self):
        """Применение операции Адамара"""
        self.state = H @ self.state
    
    def measure(self) -> bool:
        """Измерение кубита"""
        # Вероятность получить 0
        pr0 = np.abs(self.state[0, 0]) ** 2
        # Случайный выбор результата
        sample = np.random.random() <= pr0
        return bool(0 if sample else 1)
    
    def reset(self):
        """Сброс в состояние |0⟩"""
        self.state = KET_0.copy()


class SingleQubitSimulator(QuantumDevice):
    """Симулятор квантового устройства с одним кубитом"""
    
    def __init__(self):
        self._available_qubits = []
    
    def allocate_qubit(self) -> SimulatedQubit:
        if self._available_qubits:
            return self._available_qubits.pop()
        return SimulatedQubit()
    
    def deallocate_qubit(self, qubit: SimulatedQubit):
        qubit.reset()
        self._available_qubits.append(qubit)


# ==================== QRNG ====================

def qrng(device: QuantumDevice) -> bool:
    """
    Квантовый генератор случайных чисел
    Шаги:
    1. Выделить кубит в состоянии |0⟩
    2. Применить операцию Адамара для создания суперпозиции |+⟩
    3. Измерить кубит
    """
    with device.using_qubit() as q:
        q.h()  # Применяем Адамара
        return q.measure()  # Измеряем


# ==================== ТЕСТИРОВАНИЕ ====================

def test_qrng():
    """Тестирование QRNG-генератора"""
    print("=" * 60)
    print("ЗАДАНИЕ 4: QRNG-ГЕНЕРАТОР")
    print("=" * 60)
    
    # Создаем симулятор
    simulator = SingleQubitSimulator()
    
    # Генерируем 20 случайных битов
    print("\nСгенерированные случайные биты:")
    results = []
    for i in range(20):
        bit = qrng(simulator)
        results.append(bit)
        print(f"  Бит {i+1:2d}: {int(bit)}")
    
    # Статистика
    zeros = results.count(False)
    ones = results.count(True)
    print(f"\nСтатистика:")
    print(f"  Нулей (0): {zeros}")
    print(f"  Единиц (1): {ones}")
    print(f"  Вероятность 1: {ones/len(results)*100:.1f}%")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_qrng()
