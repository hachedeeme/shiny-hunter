
# Shiny Hunter
Automatiza la cacería de shinies por soft reset en emuladores, fue testeado más que nada en Epilogue Playback usando el GB Operator con cartuchos originales. No lee la memoria ni toca el RNG: manda las teclas en una secuencia, espera a que aparezcan unos píxeles y compara su color. Si el sprite se ve distinto al de un pokemon normal, suena y deja de tocar el teclado.

## Requisitos
- Python 3.14 o superior
-  [uv](https://docs.astral.sh/uv/) para instalar el proyecto y las dependencias
- Epilogue Playback o cualquier emulador abierto, con la ventana siempre en el mismo lugar y tamaño
- En Windows, el script y Playback tienen que correr con los mismos privilegios. Si Playback está "como administrador" y el script no, las teclas no llegan

El proceso se declara DPI-aware al importar el paquete, así las coordenadas del mouse y las de la captura coinciden con el escalado de pantalla (125 %, 150 %, etc.).

## Instalación
En la carpeta del proyecto:
```powershell
uv sync
```
Eso crea `.venv`, instala el paquete en editable y baja las dependencias:
-  `mss` y `pynput`, para capturar la pantalla y leer o enviar teclas
-  `pytest` y `ruff`, del grupo de desarrollo

Los comandos de abajo usan `uv run`, que ejecuta dentro de ese entorno.

## Uso
Dejá Playback visible. Durante la cuenta regresiva de `check` y `hunt`, hacé clic en esa ventana para que quede enfocada: las teclas simuladas van a la ventana que tiene el foco.

Para cortar en cualquier momento, la tecla es `stop_key` de la config (por defecto F12). Funciona aunque la terminal no esté enfocada.

### 1. Calibrar
```powershell
uv run shiny-hunter calibrate
```
Mové el mouse sobre un píxel. La terminal muestra `x`, `y` y el color RGB. F9 anota una línea lista para pegar en el JSON. F12 sale.

`--mark-key` y `--stop-key` cambian esas teclas (por defecto `f9` y `f12`).

Medí dos clases de píxel, con un pokemon **normal** en pantalla:
-  `ready_pixels`: algo que se ve igual en shiny y no shiny, y que aparece cuando el sprite ya está. Un borde del cuadro de texto alcanza. Que sea un color sólido, no un píxel que parpadee.
-  `shiny_pixels`: un punto del sprite que cambie en la versión shiny. Anotá el color que tiene en la versión normal. Si ponés varios, todos tienen que cambiar para que cuente como shiny.

### 2. Configurar
Los JSON viven en `configs/`. Podés tener uno por pokemon. [`configs/example.json`](configs/example.json) es la plantilla: copiala y reemplazá los píxeles con lo que anotó `calibrate`.
`check` solo necesita los píxeles. `hunt` además exige `sequence`.

| Campo | Qué hace | Default |
|---|---|---|
| `sequence` | Pasos `{"keys", "wait", "hold"}`. `keys` puede ser una combinación con `+`. `wait` es la pausa después de soltar. `hold` es cuánto se mantienen apretadas; si no está, usa `key_hold` | `[]` |
| `ready_pixels` | Píxeles que confirman que la pantalla ya cargó | `[]` |
| `shiny_pixels` | Píxeles del sprite, con el color de un pokemon normal. Obligatorio | |
| `tolerance` | Diferencia máxima por canal RGB para considerar el mismo color | `12` |
| `key_hold` | Segundos que se mantiene cada tecla si el paso no trae `hold` | `0.05` |
| `ready_timeout` | Segundos máximos esperando `ready_pixels` | `20` |
| `poll_interval` | Cada cuánto se vuelve a mirar la pantalla mientras espera | `0.1` |
| `settle_time` | Espera extra después de "listo", antes de evaluar el shiny | `0.5` |
| `confirm_captures` | Relecturas extra antes de dar el shiny por válido | `3` |
| `confirm_interval` | Segundos entre esas relecturas | `0.25` |
| `stop_key` | Tecla global para detener | `f12` |

Teclas en `keys` y en `stop_key`: una letra o un número, `ctrl`, `shift`, `alt`, `enter`, `space`, `tab`, `esc`, `backspace`, `up`, `down`, `left`, `right` y `f1`–`f20`. Con `+` se aprietan todas juntas (`z+x+enter+backspace`).

Las claves que el programa no conoce se ignoran.

### 3. Probar la detección
Con Playback mostrando un pokemon normal:
```powershell
uv run shiny-hunter check -c configs/example.json
```
Tiene que imprimir `Resultado: normal`. Si la pantalla lista no coincide, no evalúa el shiny. Si todos los `shiny_pixels` difieren del color normal, imprime `Resultado: SHINY`.

`--countdown` es la espera inicial, en segundos (default `5`).

### 4. Cazar
```powershell
uv run shiny-hunter hunt -c configs/example.json
```
En cada intento manda la `sequence`, espera los `ready_pixels` y mira el sprite. Si la pantalla esperada no aparece dentro de `ready_timeout`, lo cuenta como desincronizado y reinicia: nunca lo interpreta como shiny. Si parece shiny, lo relee `confirm_captures` veces. Si se confirma, suena y deja de mandar teclas.

```powershell
uv run shiny-hunter hunt -c configs/example.json --max-attempts 1
```
`--max-attempts` en `0` no tiene límite. `--countdown` funciona igual que en `check`.

## Tests y lint
```powershell
uv run pytest
uv run ruff check src tests
uv run ruff format src tests
```
`pytest` cubre la comparación de color, la carga del JSON y el bucle de cacería con un teclado y una pantalla falsos. No abre Playback.
`ruff check` mira errores, imports y unos bugs habituales. `ruff format` deja el indentado en 2 espacios y las líneas en 100 caracteres, como está en `pyproject.toml`.
