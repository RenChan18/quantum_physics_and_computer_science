# bb84.py - Симуляция квантового распределения ключей по протоколу BB84

import numpy as np
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from typing import List, Tuple, Optional
import random

# ==================== ИНТЕРФЕЙСЫ ====================

class Qubit(metaclass=ABCMeta):
    @abstractmethod
    def h(self):
        pass
    
    @abstractmethod
    def x(self):
        pass
    
    @abstractmethod
    def measure(self) -> bool:
        pass
    
    @abstractmethod
    def reset(self):
        pass


class QuantumDevice(metaclass=ABCMeta):
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
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)


class SimulatedQubit(Qubit):
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
    def __init__(self):
        self._available_qubits = []
    
    def allocate_qubit(self) -> SimulatedQubit:
        if self._available_qubits:
            return self._available_qubits.pop()
        return SimulatedQubit()
    
    def deallocate_qubit(self, qubit: SimulatedQubit):
        qubit.reset()
        self._available_qubits.append(qubit)


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def sample_random_bit(device: QuantumDevice) -> bool:
    """Генерация случайного бита с использованием QRNG"""
    with device.using_qubit() as q:
        q.h()
        result = q.measure()
        q.reset()
        return result


def prepare_message_qubit(message: bool, basis: bool, q: Qubit) -> None:
    """Подготовка кубита сообщения"""
    if message:
        q.x()
    if basis:
        q.h()


def measure_message_qubit(basis: bool, q: Qubit) -> bool:
    """Измерение кубита сообщения"""
    if basis:
        q.h()
    result = q.measure()
    q.reset()
    return result


def bits_to_hex(bits: List[bool]) -> str:
    """Преобразование списка битов в шестнадцатеричную строку"""
    hex_str = ""
    for i in range(0, len(bits), 4):
        chunk = bits[i:i+4]
        value = 0
        for j, bit in enumerate(chunk):
            if bit:
                value |= (1 << (3 - j))
        hex_str += format(value, 'x')
    return hex_str


def string_to_bits(text: str) -> List[bool]:
    """Преобразование строки в список битов"""
    bits = []
    for char in text:
        # Получаем UTF-8 байты
        for byte in char.encode('utf-8'):
            for i in range(7, -1, -1):
                bits.append(bool((byte >> i) & 1))
    return bits


def bits_to_string(bits: List[bool]) -> str:
    """Преобразование списка битов обратно в строку"""
    bytes_list = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte = 0
            for j, bit in enumerate(bits[i:i+8]):
                if bit:
                    byte |= (1 << (7 - j))
            bytes_list.append(byte)
    return bytes(bytes_list).decode('utf-8', errors='ignore')


# ==================== BB84 ПРОТОКОЛ ====================

def send_single_bit_with_bb84(
    alice_device: QuantumDevice,
    bob_device: QuantumDevice
) -> Tuple[Tuple[bool, bool], Tuple[bool, bool]]:
    """
    Передача одного бита по протоколу BB84
    
    Возвращает:
    - (бит_Алисы, базис_Алисы)
    - (результат_Боба, базис_Боба)
    """
    # Алиса генерирует случайный бит и случайный базис
    alice_message = sample_random_bit(alice_device)
    alice_basis = sample_random_bit(alice_device)
    
    # Боб генерирует случайный базис для измерения
    bob_basis = sample_random_bit(bob_device)
    
    with alice_device.using_qubit() as q:
        # Алиса подготавливает кубит
        prepare_message_qubit(alice_message, alice_basis, q)
        
        # Имитация передачи кубита (через квантовый канал)
        
        # Боб измеряет кубит в своем базисе
        bob_result = measure_message_qubit(bob_basis, q)
    
    return ((alice_message, alice_basis), (bob_result, bob_basis))


def simulate_bb84_key_exchange(
    alice_device: QuantumDevice,
    bob_device: QuantumDevice,
    key_length: int
) -> List[bool]:
    """
    Симуляция протокола BB84 для генерации ключа заданной длины
    """
    key = []
    rounds = 0
    
    print(f"Генерация {key_length}-битового ключа...")
    
    while len(key) < key_length:
        rounds += 1
        
        # Отправляем один бит
        (alice_msg, alice_basis), (bob_result, bob_basis) = \
            send_single_bit_with_bb84(alice_device, bob_device)
        
        # Если базисы совпадают, бит добавляется в ключ
        if alice_basis == bob_basis:
            # В идеальном канале сообщения должны совпадать
            if alice_msg != bob_result:
                print(f"  Предупреждение: несоответствие битов в раунде {rounds}")
            key.append(alice_msg)
    
    print(f"Потребовалось {rounds} раундов для генерации {key_length}-битового ключа")
    return key


# ==================== ШИФРОВАНИЕ ====================

def xor_encrypt_decrypt(message_bits: List[bool], key_bits: List[bool]) -> List[bool]:
    """
    Шифрование/дешифрование с использованием XOR (одноразовый блокнот)
    """
    if len(message_bits) != len(key_bits):
        raise ValueError("Длина сообщения и ключа должны совпадать")
    
    return [msg_bit ^ key_bit for msg_bit, key_bit in zip(message_bits, key_bits)]


# ==================== ПОЛНЫЙ ПРОТОКОЛ ====================

def run_bb84_protocol(
    alice_device: QuantumDevice,
    bob_device: QuantumDevice,
    message: str
) -> Tuple[bool, str, str, str, str]:
    """
    Полный протокол BB84: обмен ключом, шифрование и дешифрование сообщения
    
    Возвращает:
    - success: успешно ли расшифровано сообщение
    - key_hex: ключ в hex
    - encrypted_hex: зашифрованное сообщение в hex
    - decrypted_message: расшифрованное сообщение
    - original_message: исходное сообщение
    """
    print("\n" + "=" * 60)
    print("BB84 ПРОТОКОЛ - КВАНТОВОЕ РАСПРЕДЕЛЕНИЕ КЛЮЧЕЙ")
    print("=" * 60)
    
    # Шаг 1: Преобразование сообщения в биты
    message_bits = string_to_bits(message)
    print(f"\n1. Исходное сообщение: '{message}'")
    print(f"   Длина сообщения: {len(message_bits)} бит")
    
    # Шаг 2: Обмен ключом через BB84
    print("\n2. Обмен ключом через BB84...")
    key = simulate_bb84_key_exchange(alice_device, bob_device, len(message_bits))
    key_hex = bits_to_hex(key)
    print(f"   Сгенерированный ключ (hex): {key_hex}")
    
    # Шаг 3: Шифрование сообщения
    print("\n3. Шифрование сообщения...")
    encrypted_bits = xor_encrypt_decrypt(message_bits, key)
    encrypted_hex = bits_to_hex(encrypted_bits)
    print(f"   Зашифрованное сообщение (hex): {encrypted_hex}")
    
    # Шаг 4: Передача зашифрованного сообщения (классический канал)
    print("\n4. Передача зашифрованного сообщения...")
    
    # Шаг 5: Дешифрование сообщения
    print("\n5. Дешифрование сообщения...")
    decrypted_bits = xor_encrypt_decrypt(encrypted_bits, key)
    decrypted_message = bits_to_string(decrypted_bits)
    print(f"   Расшифрованное сообщение: '{decrypted_message}'")
    
    # Шаг 6: Сравнение
    print("\n6. Сравнение сообщений:")
    print(f"   Исходное сообщение:    '{message}'")
    print(f"   Расшифрованное:        '{decrypted_message}'")
    
    success = (message == decrypted_message)
    print(f"   Результат: {'✓ УСПЕШНО' if success else '✗ ОШИБКА'}")
    
    return success, key_hex, encrypted_hex, decrypted_message, message


# ==================== ТЕСТИРОВАНИЕ ====================

def test_bb84():
    """Тестирование полного протокола BB84"""
    
    # Создаем устройства для Алисы и Боба
    alice_device = SingleQubitSimulator()
    bob_device = SingleQubitSimulator()
    
    # Тестовые сообщения
    test_messages = [
        "Привет, мир!",
        "Quantum cryptography is awesome!",
        "BB84 protocol",
        "🔐 Секретное сообщение"
    ]
    
    results = []
    for msg in test_messages:
        success, key_hex, encrypted_hex, decrypted, original = run_bb84_protocol(
            alice_device, bob_device, msg
        )
        results.append((msg, success))
        print()
    
    # Сводка
    print("\n" + "=" * 60)
    print("СВОДКА РЕЗУЛЬТАТОВ")
    print("=" * 60)
    for msg, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {msg[:30]}...")


def test_bb84_with_random_keys():
    """Тестирование BB84 с генерацией ключей разной длины"""
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ С РАЗНОЙ ДЛИНОЙ КЛЮЧА")
    print("=" * 60)
    
    alice_device = SingleQubitSimulator()
    bob_device = SingleQubitSimulator()
    message = "Тестовое сообщение для проверки BB84"
    message_bits = string_to_bits(message)
    
    key_lengths = [32, 64, 128, 256]
    
    for key_len in key_lengths:
        print(f"\nДлина ключа: {key_len} бит")
        print("-" * 40)
        
        if key_len >= len(message_bits):
            key = simulate_bb84_key_exchange(alice_device, bob_device, len(message_bits))
            key_hex = bits_to_hex(key)
            print(f"  Ключ (первые 32 бита в hex): {key_hex[:8]}...")
        else:
            print(f"  Длина ключа ({key_len}) меньше длины сообщения ({len(message_bits)})")
            print(f"  Необходим ключ длиной не менее {len(message_bits)} бит")


if __name__ == "__main__":
    # Установка seed для воспроизводимости (опционально)
    np.random.seed(42)
    random.seed(42)
    
    # Запуск всех тестов
    test_bb84()
    test_bb84_with_random_keys()
