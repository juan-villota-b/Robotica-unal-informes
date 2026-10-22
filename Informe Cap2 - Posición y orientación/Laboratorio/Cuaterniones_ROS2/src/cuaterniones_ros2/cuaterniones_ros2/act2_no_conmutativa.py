from scipy.spatial.transform import Rotation as R
import numpy as np

def main():
    r1 = R.from_euler('z', 90, degrees=True)
    r2 = R.from_euler('x', 90, degrees=True)

    rz_rx = r1 * r2
    rx_rz = r2 * r1

    print("Rz·Rx:\n", rz_rx.as_matrix())
    print("Rx·Rz:\n", rx_rz.as_matrix())
    print("¿Iguales?", np.allclose(rz_rx.as_matrix(), rx_rz.as_matrix()))

if __name__ == '__main__':
    main()