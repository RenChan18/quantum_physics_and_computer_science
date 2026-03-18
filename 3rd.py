import numpy as np

# гейты
X = np.array([[0, 1],
              [1, 0]])

Z = np.array([[1, 0],
              [0, -1]])

H = (1/np.sqrt(2)) * np.array([[1, 1],
                               [1, -1]])

# Комбинации гейтов (однокубитовые)
U_XZH = X @ Z @ H
U_HXZ = H @ X @ Z

# Двухкубитовое расширение
U2_XZH = np.kron(U_XZH, U_XZH)
U2_HXZ = np.kron(U_HXZ, U_HXZ)

# Начальное состояние |00>
psi = np.array([1, 0, 0, 0])

result_XZH = U2_XZH @ psi
result_HXZ = U2_HXZ @ psi

print("Результат для XZH:")
print(result_XZH)

print("\nРезультат для HXZ:")
print(result_HXZ)
