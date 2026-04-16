# qubit_transfer.py - Симуляция передачи кубитов между пользователями

import numpy as np
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from typing import List, Tuple

# ==================== ИНТЕРФЕЙСЫ ====================

class Qubit(metaclass=ABCMeta):
    """Абстрактный класс кубита"""
    
    @abstractmethod
    def h(self):
        """Операция Адамара"""
        pass
    
    @abstractmethod
    def x(self):
        """Операция NOT (X)"""
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
        pass
    
    @abstractmethod
    def deallocate_qubit(self, qubit: Qubit):
        pass
    
    @contextmanager
    def using_qubit(self):
        qubit = self.allocate_qubit()
        try:
            yield qubit
        finally:
            self.deallocate_qubit(qubit)


# ==================== СИМУЛЯТОР ====================

KET_0 = np.array([[1], [0]], dtype=complex)
KET_1 = np.array([[0], [1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)  # Адамар
X = np.array([[0, 1], [1, 0]], dtype=complex)  # NOT операция


class SimulatedQubit(Qubit):
    """Симулированный кубит"""
    
    def __init__(self):
        self.state = KET_0.copy()
    
    def h(self):
        self.state = H @ self.state
    
    def x(self):
        self.state = X @ self.state
    
    def measure(self) -> bool:
        pr0 = np.abs(self.state[0, 0]) ** 2
        sample = np.random.random() <= pr0
        return bool(0 if sample else 1)
    
    def reset(self):
        self.state = KET_0.copy()


class SingleQubitSimulator(QuantumDevice):
    """Симулятор квантового устройства"""
    
    def __init__(self):
        self._available_qubits = []
    
    def allocate_qubit(self) -> SimulatedQubit:
        if self._available_qubits:
            return self._available_qubits.pop()
        return SimulatedQubit()
    
    def deallocate_qubit(self, qubit: SimulatedQubit):
        qubit.reset()
        self._available_qubits.append(qubit)


# ==================== КВАНТОВАЯ КОММУНИКАЦИЯ ====================

def encode_message(bit: bool, basis: bool, q: Qubit) -> None:
    """
    Кодирование бита сообщения в кубит с использованием заданного базиса
    
    Параметры:
    - bit: бит сообщения (0 или 1)
    - basis: базис кодирования (False = Z-базис, True = X-базис)
    - q: кубит для кодирования (начинается в |0⟩)
    """
    # Если бит = 1, применяем NOT для переворота
    if bit:
        q.x()
    
    # Если используется X-базис, применяем Адамара
    if basis:
        q.h()


def decode_message(basis: bool, q: Qubit) -> bool:
    """
    Декодирование кубита для получения бита сообщения
    
    Параметры:
    - basis: базис декодирования
    - q: кубит для декодирования
    
    Возвращает:
    - декодированный бит
    """
    # Если используется X-базис, применяем Адамара перед измерением
    if basis:
        q.h()
    
    result = q.measure()
    q.reset()
    return result


def transfer_single_bit(
    sender_device: QuantumDevice,
    receiver_device: QuantumDevice,
    message_bit: bool,
    sender_basis: bool,
    receiver_basis: bool
) -> Tuple[bool, bool, bool]:
    """
    Передача одного бита от отправителя к получателю
    
    Возвращает: (отправленный_бит, базис_отправителя, полученный_бит)
    """
    # Отправитель кодирует сообщение
    with sender_device.using_qubit() as q:
        encode_message(message_bit, sender_basis, q)
        # Имитация передачи кубита (в симуляции просто передаем ссылку)
        
        # Получатель декодирует
        received_bit = decode_message(receiver_basis, q)
        
    return (message_bit, sender_basis, received_bit)


# ==================== ТЕСТИРОВАНИЕ ====================

def test_qubit_transfer():
    """Тестирование передачи кубитов между пользователями"""
    print("=" * 60)
    print("ЗАДАНИЕ 5: ПЕРЕДАЧА КУБИТОВ МЕЖДУ ПОЛЬЗОВАТЕЛЯМИ")
    print("=" * 60)
    
    sender = SingleQubitSimulator()
    receiver = SingleQubitSimulator()
    
    print("\nТест 1: Передача битов с использованием одинаковых базисов")
    print("-" * 50)
    
    for msg_bit in [False, True]:
        for basis in [False, True]:
            sent, s_basis, received = transfer_single_bit(
                sender, receiver, msg_bit, basis, basis
            )
            status = "✓" if sent == received else "✗"
            bit_name = "0" if msg_bit else "1"
            basis_name = "Z" if not basis else "X"
            print(f"  Бит {bit_name} в базисе {basis_name}: "
                  f"отправлен={int(sent)}, получен={int(received)} {status}")
    
    print("\nТест 2: Передача битов с использованием разных базисов")
    print("-" * 50)
    
    # Таблица возможных комбинаций базисов
    for msg_bit in [False, True]:
        for sender_basis in [False, True]:
            for receiver_basis in [False, True]:
                if sender_basis == receiver_basis:
                    continue
                sent, s_basis, received = transfer_single_bit(
                    sender, receiver, msg_bit, sender_basis, receiver_basis
                )
                status = "✓" if sent == received else "✗"
                bit_name = "0" if msg_bit else "1"
                s_basis_name = "Z" if not sender_basis else "X"
                r_basis_name = "Z" if not receiver_basis else "X"
                print(f"  Бит {bit_name} (отпр.{s_basis_name}, пол.{r_basis_name}): "
                      f"отправлен={int(sent)}, получен={int(received)} {status}")
    
    print("\n" + "=" * 60)
    
    # Демонстрация вероятностного характера при разных базисах
    print("\nДемонстрация: при разных базисах результат случайный")
    print("-" * 50)
    
    stats = {0: 0, 1: 0}
    for _ in range(100):
        sent, _, received = transfer_single_bit(
            sender, receiver, True, True, False  # X-базис -> Z-базис
        )
        stats[int(received)] += 1
    
    print(f"  Из 100 попыток отправки '1' в X-базисе с приемом в Z-базисе:")
    print(f"    Получено '0': {stats[0]} раз")
    print(f"    Получено '1': {stats[1]} раз")
    print(f"    Вероятность правильного декодирования: {stats[1]}%")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_qubit_transfer()
