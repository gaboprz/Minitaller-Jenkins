# Minitaller-Jenkins

Material de apoyo para un mini-taller tecnico enfocado en el uso de Jenkins como
herramienta de automatizacion para procesos de integracion y entrega continua.

## Estructura

- `buscaminas.py`: punto de entrada para ejecutar la interfaz grafica.
- `src/buscaminas_app/domain.py`: reglas puras del juego, generacion y revelado del tablero.
- `src/buscaminas_app/ranking.py`: lectura, escritura y reglas del ranking.
- `src/buscaminas_app/gui.py`: adaptador Tkinter.
- `tests/`: pruebas unitarias sin dependencia de la interfaz grafica.
- `Dockerfile`: targets separados para `lint`, `unit-test` y `develop`.
- `Jenkinsfile`: pipeline declarativo para checkout, lint, tests y build.

## Vista previa

![Pipeline](img/pipeline.png)

## Ejecutar localmente

```bash
python3 buscaminas.py
```

## Pruebas unitarias

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
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

## Reproducir el flujo con Jenkins

Estos pasos levantan Jenkins localmente con Docker y ejecutan el `Jenkinsfile`
del repositorio.

### 0. Hacer fork del repositorio (participantes del taller)

Cada participante debe trabajar sobre su propia copia del repositorio para que
sus commits disparen su propio pipeline sin interferir con los demas.

1. Entrar al repositorio original en GitHub.
2. Hacer clic en el boton `Fork` (esquina superior derecha).
3. Seleccionar tu cuenta como destino y confirmar.

A partir de aqui, usa la URL de **tu fork** en todos los pasos siguientes.

### 1. Clonar el repositorio

Clonar **tu fork** (no el repo original):

```bash
git clone <URL_DE_TU_FORK>
cd Minitaller-Jenkins
```

### 2. Levantar Jenkins

```bash
docker compose up -d jenkins
```

### 3. Abrir Jenkins

Entrar desde el navegador:

```text
http://localhost:8081
```
### 4. Obtener la contraseña inicial
```bash
docker compose logs jenkins
```
![Password](img/psswrd.png)
### 5. Configurar Jenkins

En el asistente inicial:

1. Pegar la contrasena inicial.
![local_host_password](img/local_host_password.png)
2. Seleccionar `Install suggested plugins`.
![local_host_in](img/local_host_in.png)
3. Crear el usuario administrador.
![local_host_create_user](img/local_host_create_user.png)
4. Confirmar la URL `http://localhost:8081/`.
![local_host_instance_configuration](img/local_host_instance_configuration.png)

### 6. Crear el pipeline

En Jenkins:

1. Entrar a `New Item`.
![new_item](img/new_item.png)
2. Nombre sugerido: `buscaminas-pipeline`.
3. Tipo: `Pipeline`.
4. Seleccionar `OK`.

En la configuracion del job:

```text
Definition: Pipeline script from SCM
SCM: Git
Repository URL: <URL_DE_TU_FORK>
```
![git_config](img/git_config.png)
```
Branch Specifier: */main
Script Path: Jenkinsfile
```
![git_config](img/branch_config.png)


Si la rama principal del repositorio se llama `master`, usar:

```text
*/master
```

### 7. Activar ejecucion automatica

En `Build Triggers`, activar:

```text
Poll SCM
```

Para una demo presencial, usar:

```text
* * * * *
```
![trigger](img/trigger.png)
Esto hace que Jenkins revise cambios cada minuto.

### 8. Ejecutar primera prueba

Guardar el job y ejecutar:

```text
Build Now
```

El pipeline debe mostrar estas etapas:

```text
Checkout
Static Analysis
Unit Tests
Build App Image
```

### 9. Probar el trigger con un commit

Hacer un cambio pequeno, por ejemplo en este README, y subirlo:

```bash
git add README.md
git commit -m "Test Jenkins pipeline trigger"
git push
```

Jenkins debe detectar el cambio y ejecutar el pipeline automaticamente.

### 10. Demo: subir un test con error

Esta prueba sirve para demostrar que Jenkins bloquea una version rota.

Abrir `tests/test_domain.py` y cambiar temporalmente esta validacion:

```python
self.assertEqual(mine_count, 10)
```

por esta version incorrecta:

```python
self.assertEqual(mine_count, 99)
```

Subir el cambio al repositorio:

```bash
git add tests/test_domain.py
git commit -m "Demo failing unit test"
git push
```

Resultado esperado en Jenkins:

```text
Checkout        -> verde
Static Analysis -> verde
Unit Tests      -> rojo
Build App Image -> no se ejecuta
```

Esto pasa porque Jenkins detecta que la funcionalidad esperada del tablero ya no
se cumple. Como los tests fallan, la imagen final `buscaminas-develop` no se
construye para esa version.

### 11. Demo: arreglar el error

Volver a dejar el test correcto:

```python
self.assertEqual(mine_count, 10)
```

Subir la correccion:

```bash
git add tests/test_domain.py
git commit -m "Fix failing unit test"
git push
```

Resultado esperado en Jenkins:

```text
Checkout        -> verde
Static Analysis -> verde
Unit Tests      -> verde
Build App Image -> verde
```

Con esto se demuestra el flujo completo:

```text
commit roto -> Jenkins falla -> se corrige -> Jenkins pasa -> se genera imagen
```

## Que hace Jenkins

```text
Checkout: descarga el codigo desde Git.
Static Analysis: construye y ejecuta el target Docker lint con flake8.
Unit Tests: construye y ejecuta el target Docker unit-test con pytest.
JUnit: publica reports/unit-tests.xml como resultado de pruebas.
Build App Image: construye la imagen Docker final buscaminas-develop.
```

Si `Static Analysis` o `Unit Tests` fallan, Jenkins no construye la imagen final.
