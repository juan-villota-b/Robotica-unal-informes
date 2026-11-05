# Reporte de revisión — código de la guía CAP6

Revisión del código de la guía contra el repositorio del libro
(`RVC3-python/notebooks/scripts/chap6.py`), el texto de Corke
(`Libros/corke_txt/cap06.txt`) y el código de `roboticstoolbox 1.4.2` instalado
en `~/venvs/robotica`. **No se modificó nada**: este documento es para aprobar.

## 1. Qué se ejecutó

Los 4 scripts que no necesitan Gazebo ni RViz, tal como están:

| Script | Salida | Tiempo | Figuras |
|---|---|---|---|
| `parte1_odometria.py` | exit 0 | 1.27 s | 1 |
| `parte2_ekf.py` | exit 0 | 1.25 s | 2 |
| `parte3_ekf_landmarks.py` | exit 0 | 1.37 s | 3 (una vacía) |
| `parte4_slam.py` | exit 0 | 1.39 s | 3 (una vacía) |

Único aviso: `plt.show()` con backend `Agg` (esperado sin pantalla).

Mediciones propias usadas como evidencia:

- Parte 1, error final con `V = diag([0.2, …])**2`: **3.238 m**;
  con `V = diag([0.02, …])**2`: **0.963 m** (200 pasos).
- Parte 2, `sqrt(P150[0,0])` con `V=0.02`: **0.4081 m**, el mismo valor que
  publica el libro (§6.1.2, p. 217).
- Parte 3, `T=40`: `Pnorm` final **1.44e-05**, error de pose **0.090 m**.
  Con `T=20` (libro): **4.89e-06** y **0.064 m**.
- Parte 4: **10** landmarks estimados de 20, `Pnorm` final **9.97e-27**,
  `sqrt(det(P_pose))` final **7.25e-03**, error de pose **0.362 m**.

## 2. Resumen

| ID | Sev. | Título |
|---|---|---|
| M01 | Crítica | La parte 1 usa `V=0.2` donde el libro usa `0.02` |
| M02 | Baja | La pose ideal se integra con `robot.f` y no con `robot_ideal.f` |
| M03 | Crítica | `setup.py` con `entry_points` vacío: `ros2 run` no encuentra el nodo |
| M04 | Media | La parte 3 corre `T=40`; el libro usa `T=20` |
| M05 | Baja | Faltan `seed=` y `workspace=mapa` explícitos |
| M06 | Alta | La parte 4 no grafica el mapa estimado (`plot_map`) |
| M07 | Baja | Falta `get_transform(map)` para comparar mapa estimado y real |
| M08 | Baja | El sensor simulado no coincide con el LiDAR del TurtleBot3 |
| M09 | Alta | `get_Pnorm()` en SLAM no mide la incertidumbre de la pose |
| M10 | Media | «Divergencia» del EKF sin sensores: el error no diverge |
| M11 | Media | No se explica que `V`/`W` aparecen dos veces |
| M12 | Media | «Reducción parcial de incertidumbre» en SLAM no se sostiene |
| M13 | Media | `plt.figure()` antes de `mapa.plot()` deja una figura vacía |
| M14 | Media | La parte 2 no grafica elipses de confianza |
| M15 | Baja | Las partes 3 y 4 no tienen leyendas |
| M16 | Baja | La parte 1 no grafica el error contra el tiempo |
| M17 | Media | No se documenta `dt=0.1` ni qué significan `T=20/40` |
| M18 | Baja | No se documenta cómo cambiar la semilla |
| M19 | Media | El nodo no usa `use_sim_time` |
| M20 | Baja | `rclpy.spin` sin `try/finally` |
| M21 | Baja | Velocidades fijas en el código, sin parámetros |
| M22 | Media | `package.xml`: dependencias mal clasificadas |
| M23 | Baja | `tests_require` obsoleto y sin tests |
| M24 | Alta | `rm -rf build install log` sobre un workspace compartido |
| M25 | Baja | Launch sin argumentos configurables |
| M26 | Baja | El mapa se guarda fuera del paquete |
| M27 | Media | `import *` en las partes 3 y 4 |
| M28 | Baja | Mezcla `from math import pi` con `np.pi` |
| M29 | Baja | «Simultaneus» |
| M30 | Baja | `print(V)` sin contexto |
| M31 | Baja | `animation=None` solo en las partes 2–4 |
| M32 | Opcional | Duplicación de `V`/`P0`/`W` y del armado robot+mapa+sensor |

---

## 3. Errores

- [x] **M01 (Crítica) — La parte 1 usa `V=0.2` donde el libro usa `0.02`.**
  - Dónde: `simulaciones/parte1_odometria.py`, constante `V` (guía §4).
  - Problema: la varianza de velocidad es 100 veces la del libro y la de las
    partes 2–4 de la propia guía.
  - Evidencia: `chap6.py:7` usa `V = np.diag([0.02, np.deg2rad(0.5)]) ** 2`.
    Con 0.2 el error final es 3.24 m; con 0.02, 0.96 m. Además, con 0.02 la
    parte 2 reproduce el `0.4081 m` que publica el libro.
  - Propuesta: cambiar `0.2` → `0.02`. Si se quiere una desviación grande a
    propósito, dejarlo documentado como escenario de ruido alto.

- [x] **M02 (Baja) — La pose ideal se integra con `robot.f` en vez de
  `robot_ideal.f`.**
  - Dónde: bucle de simulación de la parte 1.
  - Problema: se usa el objeto equivocado; funciona solo porque ambos robots
    comparten `L=1`.
  - Propuesta: `qp_ideal = robot_ideal.f(qp_ideal, odo_ideal)`.

- [x] **M03 (Crítica) — `setup.py` deja `entry_points` vacío.**
  - Dónde: guía §11 (`setup.py`) y §20 (`ros2 run localization_lab
    simple_controller`).
  - Problema: sin console script, el paso §20 falla con «No executable found».
  - Evidencia: en la implementación se añadió
    `simple_controller = localization_lab.simple_controller:main` y recién así
    el nodo arrancó y publicó.
  - Propuesta: dejar el entry point en la guía (ya está en el laboratorio).

## 4. Inconsistencias con el libro

- [ ] **M04 (Media) — La parte 3 corre `T=40`; el libro usa `T=20`.**
  - Evidencia: `chap6.py`, §6.2 (`ekf.run(T=20)`); la guía §6 usa `T=40`.
  - Efecto medido: `Pnorm` 4.89e-06 → 1.44e-05 y error 0.064 → 0.090 m. No es
    un error, pero la guía no justifica duplicar el tiempo y se aleja del
    resultado del libro.

- [x] **M05 (Baja) — Faltan `seed=` y `workspace=mapa` explícitos.**
  - Evidencia: el libro escribe `RandomPath(workspace=map, seed=0)`,
    `RangeBearingSensor(..., seed=0)`, `LandmarkMap(..., seed=0)`
    (`chap6.py:68,71,85`). La guía los omite.
  - Efecto: los defaults son 0, así que el resultado coincide; pero el lector
    no sabe que el experimento es reproducible ni cómo variarlo (ver M18).

- [x] **M06 (Alta) — La parte 4 no grafica el mapa estimado.**
  - Dónde: `simulaciones/parte4_slam.py`, función `graficar()`.
  - Problema: el resultado esperado de la guía es «construcción progresiva del
    mapa» y «estimación simultánea de pose y landmarks», pero el código solo
    dibuja el mapa **real**, las trayectorias y las elipses. Nunca se ven los
    landmarks estimados.
  - Evidencia: el libro agrega `ekf.plot_map(); # plot estimated landmark
    position` (`chap6.py:124`).
  - Propuesta: añadir `slam.plot_map()` antes de `plot_ellipse()`. Verificado:
    dibuja los landmarks estimados como cruces.

- [x] **M07 (Baja) — Falta la comparación cuantitativa de mapas.**
  - Evidencia: el libro cierra §6.4 con
    `T = ekf.get_transform(map)` (`chap6.py:128`).
  - Propuesta: añadir esa llamada y reportar el error de alineación del mapa
    estimado contra el real (refuerza la pregunta 6 de análisis).

- [ ] **M08 (Baja) — El sensor simulado no coincide con el LiDAR del robot.**
  - Dónde: partes 3 y 4, `RangeBearingSensor(angle=[-pi/2, pi/2], range=4)`.
  - Problema: simula 180° y 4 m; el LDS-01 del TurtleBot3 burger del cap. 6
    ROS2 barre 360° y ~3.5 m.
  - Nota: el libro usa exactamente los mismos valores (`chap6.py:71`), así que
    no es un error respecto al libro, sino una incoherencia con el hardware que
    se usa en la parte ROS2 (donde `cartographer.lua` fija `max_range = 3.5`).
  - Propuesta: opcional, `angle=[-pi, pi], range=3.5` y comentarlo.

## 5. Métricas y conceptos

- [x] **M09 (Alta) — `get_Pnorm()` no mide la incertidumbre de la pose en SLAM.**
  - Dónde: parte 4, figura «Evolución de incertidumbre en SLAM».
  - Problema: `get_Pnorm()` es `sqrt(det(P))` sobre **todo** el estado
    (`EKF.py:1361`). En SLAM el estado crece `3+2N`; cada landmark añade un
    determinante pequeño y la curva se desploma aunque la pose empeore.
  - Evidencia: `Pnorm` final 9.97e-27 con pose final 7.25e-03. El libro solo
    usa `get_Pnorm` en §6.1.2 con estado fijo de 3 (`chap6.py:44`) y **no** la
    usa en §6.4. El propio libro advierte que `P` mezcla m² y rad².
  - Propuesta: graficar `sqrt(det(P[:3,:3]))` (o `P[0,0]` y `P[1,1]`) y dejar
    `get_Pnorm()` solo como referencia. Así la pregunta «¿por qué la
    incertidumbre no desaparece?» se responde con la pose, no con el determinante.

- [ ] **M10 (Media) — «Divergencia entre trayectoria real y estimada» (parte 2)
  es engañoso.**
  - Problema: sin sensores el EKF **es** la odometría; no diverge por falta de
    corrección, solo acumula el mismo ruido. La guía lo presenta como si el
    filtro fallara.
  - Evidencia: el error de pose final medido es 0.606 m, del orden del ruido de
    odometría, no una divergencia exponencial.
  - Propuesta: reemplazar la frase por «el EKF replica la odometría y su
    covarianza crece; no hay innovación que corrija», y añadir
    `ekf.plot_error()` (existe en `EKF`, dibuja el error con bandas de
    confianza) para cuantificarlo.

- [ ] **M11 (Media) — No se explica que `V` y `W` aparecen dos veces.**
  - Dónde: partes 2–4; `Bicycle(covar=V)` + `EKF(robot=(robot, V))` y
    `RangeBearingSensor(covar=W)` + `EKF(sensor=(sensor, W))`.
  - Problema: es la confusión más común del capítulo. El primer `V`/`W` es el
    ruido **real** que se simula; el segundo es la **creencia** del filtro.
  - Evidencia: el libro le dedica un cuadro explícito («V versus V», §6.1.2).
  - Propuesta: comentario de dos líneas en cada parte.

- [x] **M12 (Media) — «Reducción parcial de incertidumbre» en SLAM no se
  sostiene.**
  - Problema: con mapa conocido (`parte 3`) la pose termina en 1.44e-05; en
    SLAM, en 7.25e-03. Es decir, la incertidumbre de la pose en SLAM es **mayor**,
    como era de esperar. Lo que baja es el determinante global (M09).
  - Propuesta: reformular el resultado esperado: «la incertidumbre de la pose
    crece más que con mapa conocido; los landmarks reducen el crecimiento pero
    no lo eliminan».

## 6. Visualización

- [x] **M13 (Media) — `plt.figure()` antes de `mapa.plot()` deja una figura
  vacía.**
  - Dónde: partes 3 y 4.
  - Evidencia: `LandmarkMap.plot()` llama a `plotvol2`, que abre su propia
    figura. Verificado: 1 figura antes, 2 después → la ventana creada por
    `plt.figure(figsize=(8, 6))` queda en blanco. El libro no crea la figura
    antes (`chap6.py:77-81`).
  - Propuesta: quitar el `plt.figure()` previo y fijar el tamaño sobre la
    figura que abre `mapa.plot()` (`plt.gcf().set_size_inches(8, 6)`), o
    reordenar para que `mapa.plot()` sea la primera llamada.

- [x] **M14 (Media) — La parte 2 no grafica elipses de confianza.**
  - Evidencia: el libro las agrega con
    `ekf.plot_ellipse(filled=True, facecolor="g", alpha=0.3)`
    (`chap6.py:41`); es la evidencia visual del crecimiento que pide la guía.
  - Propuesta: añadirlas a la figura de trayectorias.

- [x] **M15 (Baja) — Las partes 3 y 4 no tienen leyenda.**
  - Problema: `robot.plot_xy(color="blue")` y `ekf.plot_xy(color="red")` no
    llevan `label=`; el lector no sabe qué curva es cuál (la parte 1 sí usa
    leyenda).
  - Propuesta: `label="Trayectoria real"` / `"Trayectoria estimada"` y
    `plt.legend()`.

- [x] **M16 (Baja) — La parte 1 no grafica el error contra el tiempo.**
  - Problema: el indicador declarado es «error creciente con el tiempo», pero
    solo hay dos trayectorias.
  - Propuesta: segunda figura con `error = hypot(x_real-x_ideal, y_real-y_ideal)`.

## 7. Reproducibilidad y documentación

- [ ] **M17 (Media) — No se documenta `dt` ni el significado de `T`.**
  - Evidencia: `EKF.run(T=20)` produce **200 pasos** con `dt=0.1` (`Vehicle`
    usa `dt=0.1` por defecto). Los estudiantes no pueden saber cuántas muestras
    hay ni por qué `T=40` en la parte 3.
  - Propuesta: comentar `T` en segundos y `dt=0.1` en cada script.

- [ ] **M18 (Baja) — No se documenta cómo cambiar la semilla.**
  - Evidencia: el ruido usa un generador privado de `Vehicle` con `seed=0`
    (`Vehicle.py:127,193`); `np.random.seed(...)` **no** lo afecta. Verificado:
    `Bicycle(covar=V, seed=7)` cambia la trayectoria (2.88 m de diferencia final).
  - Propuesta: nota corta con `Bicycle(..., seed=n)`, `RandomPath(..., seed=n)`,
    `LandmarkMap(..., seed=n)`, `RangeBearingSensor(..., seed=n)`.

## 8. ROS 2

- [x] **M19 (Media) — El nodo no usa `use_sim_time`.**
  - Problema: `msg.header.stamp = self.get_clock().now()` toma el reloj de
    pared, no `/clock` de Gazebo. El DiffDrive ignora el `stamp`, pero el
    mensaje es incoherente con la simulación.
  - Propuesta: declarar `use_sim_time` (o lanzar con `--ros-args -p
    use_sim_time:=true`) y dejar que el reloj lo tome el nodo.

- [x] **M20 (Baja) — `rclpy.spin` sin `try/finally`.**
  - Problema: con Ctrl+C no se ejecutan `destroy_node()` ni `shutdown()`.
  - Propuesta: `try: rclpy.spin(node) except KeyboardInterrupt: pass finally:
    node.destroy_node(); rclpy.shutdown()`.

- [x] **M21 (Baja) — Velocidades fijas.**
  - Propuesta: `declare_parameter('linear_speed', 0.2)` y
    `declare_parameter('angular_speed', 0.1)`.

- [x] **M22 (Media) — `package.xml` con dependencias mal clasificadas.**
  - `cartographer_ros` se usa en runtime, no en build → `<exec_depend>`.
  - `sensor_msgs` y `nav_msgs` se declaran pero no se usan en el código.
  - Falta `<test_depend>` para pytest.

- [x] **M23 (Baja) — `tests_require` obsoleto y sin tests.**
  - Evidencia: `colcon build` emite `UserWarning: Unknown distribution option:
    'tests_require'`; `colcon test` no ejecuta nada porque no hay `test/`.
  - Propuesta: `extras_require={'test': ['pytest']}` y un test mínimo del nodo.

- [x] **M24 (Alta) — `rm -rf build install log` sobre un workspace compartido.**
  - Dónde: guía §15, con `~/ros2_ws` como workspace.
  - Problema: si ese workspace tiene otros paquetes, el paso borra todos los
    artefactos de compilación, no solo los de `localization_lab`.
  - Propuesta: usar `colcon build --packages-select localization_lab` o un
    workspace propio (`~/ros2_ws_cap6`). En el laboratorio el workspace es
    propio, así que no aplica.

- [x] **M25 (Baja) — Launch sin argumentos configurables.**
  - Problema: `use_sim_time` y `resolution` están fijos en
    `cartographer.launch.py`.
  - Propuesta: `DeclareLaunchArgument('use_sim_time', default_value='true')` y
    `LaunchConfiguration`.

- [ ] **M26 (Baja) — El mapa se guarda en el directorio de ejecución.**
  - Problema: `map_saver_cli -f my_map` deja el mapa donde esté el usuario; el
    paquete no tiene carpeta `maps/`.
  - Propuesta: `maps/` en el paquete y `-f src/localization_lab/maps/cap6`
    (con `--symlink-install` se refleja en el share).

## 9. Estilo y estructura

- [x] **M27 (Media) — `import *` en las partes 3 y 4.**
  - Problema: las partes 1 y 2 usan imports explícitos; las 3 y 4 usan
    `from roboticstoolbox import *`. Oculta dependencias y puede pisar nombres.
  - Propuesta: imports explícitos (`Bicycle, EKF, LandmarkMap, RandomPath,
    RangeBearingSensor`).

- [x] **M28 (Baja) — Mezcla de `pi` y `np.pi`.**
  - Propuesta: unificar en `np.pi` o mantener `math.pi` en todo.

- [ ] **M29 (Baja) — «Simultaneus Localization and mapping».**
  - Dónde: título de la parte 4. Debería ser «Simultaneous Localization and
    Mapping».

- [ ] **M30 (Baja) — `print(V)` sin contexto.**
  - Propuesta: `print("Covarianza de odometría V =\n", V)` o quitarlo.

- [ ] **M31 (Baja) — `animation=None` solo en las partes 2–4.**
  - Nota: el default ya es `None` (`Vehicle`), así que la parte 1 no anima.
    Es solo consistencia de estilo.

- [ ] **M32 (Opcional) — Duplicación de parámetros y del armado.**
  - `V`, `P0`, `W` se repiten en las 4 partes; las partes 3 y 4 repiten el
    armado robot+mapa+sensor.
  - Propuesta: módulo `comun.py` con las covarianzas y fábricas
    (`crear_robot()`, `crear_mapa()`, `crear_sensor()`). Es la única propuesta
    que cambia la estructura; si se prefiere mantener 4 scripts autónomos,
    descartarla.

## 10. Verificado: no hace falta cambiar

- `TwistStamped` en `/cmd_vel` es **correcto**: el bridge de TurtleBot3 2.3.7
  (rama Jazzy) usa `geometry_msgs/msg/TwistStamped`.
- `plot_ellipse()` dibuja `N=10` elipses equiespaciadas (`EKF.py:1101,1125`),
  no 400. No hay problema de rendimiento.
- La simulación es **determinista** por defecto (`seed=0` en `Vehicle`), no
  aleatoria en cada corrida.
- `LandmarkMap(20, workspace=10)` es válido: el primer parámetro acepta el
  número de landmarks.
- `T=20` son 200 pasos y `T=40` son 400 (`dt=0.1`).
- `np.diag([desv, ...])**2` es correcto: eleva la desviación al cuadrado para
  obtener la varianza.
- `P0` de 3×3 sigue siendo válido en SLAM: el EKF amplía la matriz al añadir
  landmarks.
- `map=None` significa mapa desconocido (SLAM), no «sin mapa».
- `animation=None` por defecto: la parte 1 no abre animación.

## 11. Corrección al README del laboratorio

El README tenía una afirmación **mía** que resultó falsa: decía que «cada
ejecución produce trayectorias y mapas distintos». No es así: `Vehicle`,
`RandomPath`, `LandmarkMap` y `RangeBearingSensor` usan `seed=0` por defecto y
el resultado es reproducible. Ya está corregido en el README.

## 12. Estado de aplicación

Aplicados y verificados: M01, M02, M03, M05, M06, M07, M09, M12, M13, M14,
M15, M16, M19, M20, M21, M22, M23, M25, M28.

Ya se cumplían, sin cambios: M24 (este workspace es propio y el README no borra
`build/install/log`) y M27 (las cuatro partes ya usaban imports explícitos).

Sin aprobar, quedan como están: M04, M08, M10, M11, M17, M18, M26, M29, M30,
M31, M32.

Verificación posterior a los cambios:

- Los 4 scripts de simulación terminan con exit 0 (2 figuras cada uno; ninguna
  vacía).
- `colcon build --symlink-install`: OK.
- `colcon test`: **2 tests, 0 fallos**.
- Nodo: `use_sim_time=true` por defecto; con `-p use_sim_time:=false
  -p linear_speed:=0.35` publica `TwistStamped` con `linear.x = 0.35`.
- Launch: `--show-args` lista `use_sim_time` y `resolution`.

## 13. Cómo aprobar

Responder con la lista de IDs, por ejemplo:

```
aprueba M01 M03 M06 M09 M13 M24 M27
```

o marcar los `[ ]` de este archivo. Las que no se aprueben quedan como están.
