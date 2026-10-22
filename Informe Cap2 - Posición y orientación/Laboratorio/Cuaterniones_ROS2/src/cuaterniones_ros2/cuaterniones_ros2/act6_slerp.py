from scipy.spatial.transform import Rotation as R, Slerp
import numpy as np


def main():
    key_times = [0, 1]
    rots = R.from_euler('z', [0, 90], degrees=True)

    slerp = Slerp(key_times, rots)

    # 7 puntos = 5 intermedios + los 2 extremos (0° y 90°)
    times = np.linspace(0, 1, 7)
    interp = slerp(times)

    print("Interpolación SLERP (0° → 90° en Z):")
    print(interp.as_euler('xyz', degrees=True))


if __name__ == '__main__':
    main()
