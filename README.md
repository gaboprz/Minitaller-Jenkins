# Minitaller-Jenkins

Material de apoyo para un mini-taller tecnico enfocado en el uso de Jenkins como
herramienta de automatizacion para procesos de integracion y entrega continua.

## Estructura

- `buscaminas.py`: punto de entrada para ejecutar la interfaz grafica.
- `src/buscaminas_app/domain.py`: reglas puras del juego, generacion y revelado del tablero.
- `src/buscaminas_app/ranking.py`: lectura, escritura y reglas del ranking.
- `src/buscaminas_app/gui.py`: adaptador Tkinter.
- `tests/`: pruebas unitarias sin dependencia de la interfaz grafica.
- `Dockerfile`: targets separados para `develop` y `unit-test`.
- `Jenkinsfile`: pipeline basico para construir imagenes y correr pruebas.

## Ejecutar localmente

```bash
python3 buscaminas.py
```

## Pruebas unitarias

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Docker

Construir y correr pruebas:

```bash
docker build --target unit-test -t buscaminas-unit-test .
docker run --rm buscaminas-unit-test
```

Construir imagen de desarrollo:

```bash
docker build --target develop -t buscaminas-develop .
```

Tambien se puede usar Compose:

```bash
docker compose run --rm unit-test
docker compose run --rm develop
```
