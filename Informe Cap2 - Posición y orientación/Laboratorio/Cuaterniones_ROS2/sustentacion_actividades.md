# Sustentación — Representación de Pose y Cuaterniones en ROS2 (Cap. 2 – Corke)

Explicación de comprensión de cada actividad y de la discusión final.

---

## PARTE 1 — Representaciones de orientación

### Actividad 1: Conversión de representaciones

**Qué se hizo:** Se generó una rotación de 90° alrededor del eje Z con SciPy y se obtuvieron sus dos representaciones: el cuaternión `[0, 0, 0.707, 0.707]` (orden `[x, y, z, w]`) y la matriz de rotación 3×3

```
R = [[ 0, -1, 0],
     [ 1,  0, 0],
     [ 0,  0, 1]]
```

**¿Por qué son equivalentes?** Las dos no son más que "el mismo giro escrito en dos idiomas". La verificación se hizo de dos formas:

1. **Aplicación a un vector:** al rotar `v = [1, 0, 0]` (un punto sobre el eje X), tanto el cuaternión (`r.apply(v)`) como la matriz (`R @ v`) dan `[0, 1, 0]`: el eje X quedó apuntando en Y, que es exactamente lo que significa girar 90° en Z. Si ambas rutas producen el mismo resultado para cualquier vector, representan la misma rotación.
2. **Propiedades de la matriz:** `R·Rᵀ = I` (ortogonalidad: la rotación no deforma ni escala) y `det(R) = +1` (es una rotación propia, sin reflejos). Estas condiciones son necesarias y suficientes para que una matriz 3×3 sea una rotación válida.

**Comprensión clave:** el cuaternión `[0, 0, sin(45°), cos(45°)]` recuerda la forma general `q = [n·sin(θ/2), cos(θ/2)]` con θ = 90° → θ/2 = 45°. Esa mitad del ángulo es la razón profunda por la que el cuaternión "esconde" el giro completo: por eso la mitad del valor (0.707) aparece en z y w.

### Actividad 2: No conmutatividad

**Qué se hizo:** Se definieron dos rotaciones — `r1` = 90° en Z, `r2` = 90° en X — y se calcularon las dos composiciones `r1 * r2` (primero X, luego Z) y `r2 * r1` (primero Z, luego X). Las matrices resultantes **no son iguales** (`np.allclose` → `False`).

**¿Por qué no conmutan?** Componer rotaciones es como "vestirse": poner los zapatos y luego la chaqueta ≠ chaqueta y luego zapatos (con la chaqueta larga se nota). Matemáticamente, la multiplicación de matrices no conmuta (`AB ≠ BA` en general). Físicamente: si giras 90° en Z y luego 90° en X, acabas mirando en una dirección; si inviertes el orden, acabas en otra distinta.

**Orden en SciPy:** en `r1 * r2`, SciPy aplica **primero `r2` y luego `r1`** (igual que con matrices: `(AB)v = A(Bv)`). Este detalle es la fuente #1 de errores en este tipo de laboratorios.

**Comprensión clave:** la no conmutatividad es precisamente la razón por la que en robótica el *orden* de las transformaciones importa, y por la que la composición de orientaciones debe llevarse con cuidado (cuaterniones, no Euler).

---

## PARTE 2 — ROS2: publicación de pose

### Actividad 3: Nodo publicador

**Qué se hizo:** Un nodo ROS2 (`pose_publisher`) publica en el tópico `/pose` (mensaje `geometry_msgs/Pose`) cada 0.5 s: posición fija `(1, 2, 0)` y orientación 90° en Z convertida a cuaternión.

**¿Cómo funciona?** El nodo crea un *publisher* sobre `/pose` y un temporizador. Cada tic del temporizador construye el mensaje (posición + cuaternión de SciPy copiado a los campos `orientation.x/w`) y lo publica. El cuaternión "viaja" por la red de DDS de ROS2 tal cual salió de la actividad 1.

**Comprensión clave:** ROS2 separa *quién produce* y *quién consume* información: el nodo no sabe ni le importa quién escucha. `ros2 topic echo /pose` en otra terminal demuestra el flujo en vivo. Una pose de ROS2 siempre es **posición + orientación**: la orientación es un cuaternión porque es la representación nativa (sin gimbal lock, lista para componer).

---

## PARTE 3 — Transformaciones con TF2

### Actividad 4: Árbol de transformaciones

**Qué se hizo:** Un nodo (`tf_publisher`) publica 10 veces por segundo la transformación `world → robot` con `TransformBroadcaster` de `tf2_ros`: traslación fija `(2, 0, 0)` y rotación creciente sobre Z (`self.t += 0.05` rad por tic) convertida a cuaternión. Se visualiza con RViz (`Fixed Frame: world`, añadir TF y Axes) o `view_frames`.

**¿Qué es TF2?** Es el sistema de ROS2 que mantiene y encadena transformaciones entre *frames* (marcos de referencia). Cada `TransformStamped` lleva sello de tiempo, frame padre, frame hijo, traslación y rotación (cuaternión). El sello temporal es esencial: ROS2 usa los timestamps para calcular la transformación correcta en cualquier instante (por eso el robot "girando" se ve fluido en RViz aunque los mensajes lleguen discretos).

**Comprensión clave:** la actividad 3 publica *datos de pose en un tópico cualquiera*; la actividad 4 publica *relaciones entre marcos en el árbol TF*. TF2 es el puente entre las transformaciones SE(3) del capítulo 2 (posición + orientación) y la ejecución real en ROS2: cada `TransformStamped` **es** una transformación SE(3) del libro, y `sendTransform` la inserta en el árbol world→robot→… en tiempo real.

---

## PARTE 4 — Error de orientación

### Actividad 5: Cálculo de error

**Qué se hizo:** Orientación deseada `q_des` = 90° en Z, actual `q_act` = 45° en Z. Se calculó `q_error = q_des * q_act.inv()` y se imprimió como Euler: **`[0, 0, 45]`**.

**¿Qué significa?** `q_act.inv()` es la rotación inversa (girar −45°). Componer "deseada × inversa de actual" responde a: *"¿qué giro único me llevaría de donde estoy a donde quiero estar?"* — y ese giro es exactamente 45° sobre Z (y 0 en X, 0 en Y).

**¿Y en la práctica?** Este error es la base de todo **control de orientación**: un controlador (por ejemplo, P sobre el cuaternión de error) hace que el error tienda a cero, es decir, que el robot realice el giro faltante hasta igualar la orientación de referencia. En robótica, "error de orientación" no es un fallo: es la **señal de control**.

**Comprensión clave:** trabajar con cuaterniones permite invertir y componer orientaciones sin singularidades; el resultado en Euler `[0, 0, 45]` es solo la lectura legible para humanos del resultado interno en cuaternión.

---

## PARTE 5 — Interpolación de orientación

### Actividad 6: SLERP

**Qué se hizo:** Se interpoló entre 0° y 90° en Z con `Slerp` de SciPy usando 7 tiempos (`np.linspace(0, 1, 7)` → 5 puntos intermedios + 2 extremos). Salida: `0, 15, 30, 45, 60, 75, 90` grados en Z.

**¿Qué es SLERP?** *Spherical Linear Interpolation*: interpolación lineal **sobre la esfera** de cuaterniones. A diferencia de una interpolación lineal normal (lerp), que recorta por la cuerda y altera la norma, SLERP recorre el **arco** de la esfera: cada punto intermedio es un cuaternión normalizado (una rotación válida) y el paso angular es constante.

**¿Por qué pasos de 15°?** 90° ÷ 6 intervalos = 15° exactos: velocidad angular uniforme, sin aceleraciones ni deceleraciones fantasma. Por eso la salida es una escalera perfecta de 15 en 15.

**Comprensión clave:** SLERP es lo que hace que las transiciones de orientación en animación/robótica se vean *suaves y naturales*. Es una ventaja directa de trabajar con cuaterniones: interpolación con significado geométrico claro (arco de círculo máximo), imposible de hacer así con ángulos de Euler (donde interpolar roll-pitch-yaw produce trayectorias distorsionadas y saltos).

---

## DISCUSIÓN FINAL

### 1. ¿Por qué ROS2 usa cuaterniones en lugar de ángulos de Euler?

- **Sin gimbal lock:** los Euler tienen singularidades (pierden un grado de libertad cuando el eje central se alinea ±90°); el cuaternión es continuo y válido en toda la esfera de rotaciones.
- **Composición e inversa triviales:** multiplicar cuaterniones compone rotaciones (como en la act 5) y el inverso es solo cambiar un signo — sin trigonometría de tres ejes acoplados.
- **Interpolación correcta:** SLERP (act 6) solo está bien definido sobre cuaterniones; con Euler la interpolación no respeta la geometría real de las rotaciones.
- **Eficiencia y unicidad:** 4 números (x,y,z,w) normalizados, sin cálculos `atan2/asin` por conversión, y `±q` representan el mismo giro (uniqueness de doble cubierta).

Euler no desaparece: ROS2 lo usa solo en interfaces de visualización; **el transporte y el cálculo siempre son cuaterniones**.

### 2. ¿Qué problema evitan los cuaterniones?

El problema central es el **gimbal lock** (bloqueo de guiñada): en la representación Z-Y-X de Euler, cuando el pitch llega a ±90°, los ejes de yaw y roll se alinean y **colapsan en uno solo** → se pierde un grado de libertad: hay infinitas combinaciones (yaw, roll) para la misma orientación. Geométricamente, la parametrización de Euler "cospe" en los polos de la esfera de orientaciones.

Además evitan: discontinuidades numéricas (yaw salta de +180° a −180°), interpolaciones sin sentido entre ángulos, y acumulación de errores en cadenas de transformaciones. El cuaternión `[x,y,z,w]` (con `‖q‖=1`) es una representación **continua, compacta y sin singularidades** de SO(3) — con la dualidad `q ≡ −q`, que es el único "pequeño" inconveniente y se maneja normalizando el signo (w ≥ 0).

### 3. ¿Qué relación existe entre TF2 y las transformaciones del capítulo 2?

El capítulo 2 (Corke) modela la pose como un elemento de **SE(3)**: una rotación R (SO(3)) **compuesta con** una traslación t — es decir, 3 filas de rotación + 3 de traslación, o lo equivalente: **cuaternión + vector 3D**.

TF2 es **exactamente esa misma estructura, implementada en runtime en ROS2**:

| Capítulo 2 (teoría) | TF2 (ROS2) |
|---|---|
| Transformación SE(3) (R, t) | `TransformStamped` (rotation como cuaternión + translation como Vector3) |
| Composición de transformaciones T₁·T₂ | Encadenamiento en el árbol (world→robot→sensor…) |
| Rotación como matriz o cuaternión | Siempre cuaternión (`geometry_msgs/Quaternion`) |
| Marco de referencia (frame) | `frame_id` / `child_frame_id` |

En la actividad 4, cada `sendTransform` publica **una transformación SE(3) del capítulo 2** (2 m en X + rotación en Z) y TF2 la encadena con timestamping para que cualquier nodo —o RViz— pueda consultar "¿dónde está robot respecto a world en el instante t?". **TF2 es el puente operativo** entre la matemática de transformaciones del capítulo y la arquitectura de comunicación de ROS2: sin TF2, la teoría de SE(3) no tendría cómo moverse entre nodos en tiempo real.

---

## Resumen en una línea por actividad

1. **Act 1** — La misma rotación, dos idiomas (cuaternión y matriz), demostrados equivalentes.
2. **Act 2** — El orden de los giros importa: las rotaciones no conmutan.
3. **Act 3** — ROS2 transporta poses (posición + cuaternión) por tópicos.
4. **Act 4** — TF2 transporta transformaciones SE(3) entre frames en tiempo real (visible en RViz).
5. **Act 5** — El error de orientación (cuaternión × inverso) es la señal de control de cualquier sistema de giro.
6. **Act 6** — SLERP interpola rotaciones de forma suave y uniforme gracias a los cuaterniones.
