from scipy.spatial.transform import Rotation as R


def main():
    q_des = R.from_euler('z', 90, degrees=True)
    q_act = R.from_euler('z', 45, degrees=True)

    q_error = q_des * q_act.inv()

    print("Error de orientación (euler xyz):",
          q_error.as_euler('xyz', degrees=True))


if __name__ == '__main__':
    main()
