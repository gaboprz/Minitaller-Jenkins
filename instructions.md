# Instrucciones del Proyecto Buscaminas

Este proyecto esta modularizado para separar la interfaz grafica Tkinter de la
logica del juego. La idea es que Jenkins pueda ejecutar pruebas unitarias sin
necesitar abrir ventanas ni depender del entorno grafico.

## Estructura principal

- `buscaminas.py`: archivo principal para ejecutar la aplicacion.
- `src/buscaminas_app/domain.py`: logica del tablero, minas, validaciones y revelado.
- `src/buscaminas_app/ranking.py`: logica para cargar, guardar y ordenar rankings.
- `src/buscaminas_app/gui.py`: interfaz grafica hecha con Tkinter.
- `tests/`: pruebas unitarias de la logica del juego y ranking.
- `Dockerfile`: contiene los ambientes separados `develop` y `unit-test`.
- `Jenkinsfile`: pipeline para automatizar build y pruebas.

## Ejecutar la aplicacion localmente

Desde la raiz del proyecto:

```bash
python3 buscaminas.py
```

Si falta Pillow, se puede instalar el proyecto en modo editable:

```bash
python3 -m pip install -e .
```

## Ejecutar pruebas unitarias localmente

Las pruebas no dependen de Tkinter porque validan la logica separada en modulos:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Resultado esperado:

```text
Ran 9 tests

OK
```

## Docker para unit tests

Construir la imagen de pruebas:

```bash
docker build --target unit-test -t buscaminas-unit-test .
```

Ejecutar las pruebas dentro del contenedor:

```bash
docker run --rm buscaminas-unit-test
```

Este target es el recomendado para Jenkins porque no necesita interfaz grafica.

## Docker para desarrollo

Construir la imagen de desarrollo:

```bash
docker build --target develop -t buscaminas-develop .
```

Ejecutar con Docker Compose:

```bash
docker compose run --rm develop
```

Nota: como la aplicacion usa Tkinter, para verla desde Docker se necesita tener
configurado el servidor grafico del sistema anfitrion.

## Pipeline con Jenkins

El archivo `Jenkinsfile` define tres etapas:

1. Construir la imagen de pruebas con el target `unit-test`.
2. Ejecutar las pruebas unitarias dentro del contenedor.
3. Construir la imagen de desarrollo con el target `develop`.

Flujo esperado:

```text
Codigo -> Jenkins -> Docker build unit-test -> Unit tests -> Docker build develop
```

## Razon de la modularizacion

Antes, la logica del juego estaba mezclada con Tkinter. Eso hacia dificil probar
el proyecto automaticamente porque las pruebas podian depender de ventanas,
botones o variables globales.

Ahora la logica importante esta separada:

- Jenkins prueba `domain.py` y `ranking.py`.
- Tkinter queda aislado en `gui.py`.
- `buscaminas.py` solo funciona como punto de entrada.

Esto permite aplicar CI/CD de forma mas limpia y facilita agregar nuevas pruebas
sin tocar la interfaz grafica.

## Comandos utiles

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
docker build --target unit-test -t buscaminas-unit-test .
docker run --rm buscaminas-unit-test
docker build --target develop -t buscaminas-develop .
```
