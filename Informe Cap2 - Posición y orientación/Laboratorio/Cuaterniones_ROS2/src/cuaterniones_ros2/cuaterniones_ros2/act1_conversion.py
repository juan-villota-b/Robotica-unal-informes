from scipy.spatial.transform import Rotation as R
import numpy as np


def main():
    r = R.from_euler('z', 90, degrees=True)
    q = r.as_quat()      # [x, y, z, w]
    R_mat = r.as_matrix()

    print("Cuaternión:", q)
    print("Matriz:\n", R_mat)

    # Verificación de equivalencia: ambos deben mapear un vector igual
    v = np.array([1.0, 0.0, 0.0])
    print("vía cuaternión:", r.apply(v))
    print("vía matriz:    ", R_mat @ v)
    print("¿Equivalentes?", np.allclose(r.apply(v), R_mat @ v))

    # Propiedad de toda matriz de rotación: ortogonal y det = +1
    print("R @ R.T =\n", R_mat @ R_mat.T)
    print("det(R) =", np.linalg.det(R_mat))


if __name__ == '__main__':
    main()