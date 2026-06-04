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

El archivo `Jenkinsfile` define un Pipeline Declarativo con `agent none` global y
agentes por etapa:

1. `Checkout`: descarga el codigo con `checkout scm` y lo guarda con `stash`.
2. `Static Analysis`: construye el target Docker `lint` y ejecuta `flake8`.
3. `Unit Tests`: construye el target Docker `unit-test` y ejecuta `pytest`.
4. `Build App Image`: construye la imagen Docker de desarrollo `buscaminas-develop`.

Flujo esperado:

```text
Repo Git -> checkout scm -> Docker lint -> Docker pytest + JUnit XML -> Docker develop
```

Los tests generan el archivo `reports/unit-tests.xml` dentro del contenedor.
Jenkins lo copia al workspace y lo procesa con `junit` en el bloque `post`, lo
que permite ver resultados y tendencias desde la interfaz.

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

## Primera prueba local con Jenkins

Esta opcion levanta Jenkins dentro de Docker para hacer una prueba rapida del
pipeline en una computadora local.

1. Construir y levantar Jenkins:

```bash
docker compose up -d jenkins
```

2. Obtener la contrasena inicial:

```bash
docker compose logs jenkins
```

Busca una linea parecida a:

```text
Please use the following password to proceed to installation:
```

3. Abrir Jenkins en el navegador:

```text
http://localhost:8081
```

4. Instalar los plugins sugeridos por Jenkins.

5. Crear el primer usuario administrador.

6. Crear un nuevo job:

- Seleccionar `New Item`.
- Nombre sugerido: `buscaminas-pipeline`.
- Tipo: `Pipeline`.
- Seleccionar `OK`.

7. En la seccion `Pipeline`, seleccionar `Pipeline script from SCM`.

8. Configurar el repositorio Git del proyecto.

9. En `Script Path`, dejar:

```text
Jenkinsfile
```

10. Guardar y ejecutar con `Build Now`.

Si todo esta correcto, Jenkins debe mostrar las etapas en verde y una seccion de
resultados de pruebas publicada por JUnit.

Para una prueba manual rapida sin Git remoto, tambien se puede crear un job tipo
`Pipeline` y pegar el contenido del `Jenkinsfile`, pero esa opcion no deja el
pipeline versionado junto al codigo.

## Comandos utiles

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
python3 -m pip install -r requirements-dev.txt
flake8 .
pytest tests/test_domain.py tests/test_ranking.py --junitxml=reports/unit-tests.xml
docker build --target unit-test -t buscaminas-unit-test .
docker run --rm buscaminas-unit-test
docker build --target lint -t buscaminas-ci-lint .
docker run --rm buscaminas-ci-lint
docker build --target develop -t buscaminas-develop .
docker compose up -d jenkins
```
