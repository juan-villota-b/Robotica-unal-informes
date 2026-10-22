"""Parte A: vehículo Braitenberg de la guía.

La ley de control es exactamente la de la guía:

    v     = -Kv * (sL + sR)
    omega =  Ks * (sR - sL)

No es la ley del libro de Corke (``v = 2 - sR - sL``). Esa diferencia es
deliberada: el informe analiza por qué la ley de la guía no se detiene en el
objetivo.
"""

import numpy as np

# Parámetros de la guía.
DT = 0.1
KS = 17.0
KV = 14.0
X0, Y0, THETA0 = 10.0, 10.0, 0.0
GOAL = (60.0, 90.0)


def sensorfield(x, y):
    """Campo escalar de la guía: máximo en (60, 90)."""
    xc, yc = (60.0, 90.0)
    return 1000.0 / ((x - xc) ** 2 + (y - yc) ** 2 + 50.0)


def simular(T=222, dt=DT, Ks=KS, Kv=KV, x0=X0, y0=Y0, theta0=THETA0):
    """Integra el vehículo durante ``T`` iteraciones.

    Devuelve un diccionario con las trayectorias y las señales de control.
    Los sensores están separados lateralmente una distancia ``d = 2``.
    """
    x, y, theta = float(x0), float(y0), float(theta0)
    xs = np.empty(T, dtype=float)
    ys = np.empty(T, dtype=float)
    thetas = np.empty(T, dtype=float)
    sL_arr = np.empty(T, dtype=float)
    sR_arr = np.empty(T, dtype=float)
    v_arr = np.empty(T, dtype=float)
    omega_arr = np.empty(T, dtype=float)

    d = 2.0
    for i in range(T):
        sL = sensorfield(x - d * np.sin(theta), y + d * np.cos(theta))
        sR = sensorfield(x + d * np.sin(theta), y - d * np.cos(theta))

        v = -Kv * (sL + sR)
        omega = Ks * (sR - sL)

        x += v * np.cos(theta) * dt
        y += v * np.sin(theta) * dt
        theta += omega * dt

        xs[i] = x
        ys[i] = y
        thetas[i] = theta
        sL_arr[i] = sL
        sR_arr[i] = sR
        v_arr[i] = v
        omega_arr[i] = omega

    distancia = np.hypot(xs - GOAL[0], ys - GOAL[1])
    return {
        "x": xs,
        "y": ys,
        "theta": thetas,
        "sL": sL_arr,
        "sR": sR_arr,
        "v": v_arr,
        "omega": omega_arr,
        "distancia": distancia,
    }
