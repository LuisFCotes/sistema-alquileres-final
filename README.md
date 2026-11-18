# Sistema de Alquileres de Vehículos

Aplicación web para gestionar el alquiler de una flota de vehículos: clientes,
vehículos con su tarifa por día, servicios adicionales, seguros y el registro
completo de cada alquiler con su liquidación.

**Tercer corte.** En el segundo corte toda la información se capturaba desde el
panel de administración. En este corte el sistema ya tiene **interfaz propia**
(plantillas con un framework de CSS, navegación, filtros y un tablero) y el
**proceso principal —registrar un alquiler— funciona de punta a punta desde esa
interfaz**: listar, crear, consultar el detalle, editar y eliminar con
confirmación. El panel de administración del segundo corte **sigue funcionando y
no se modificó** (modelos, migraciones y base de datos quedan igual).

El proyecto usa Django y un panel de una sola app por tabla, de modo que cada
tabla del diagrama entidad-relación corresponde con una app y un modelo.

## Descripción

El sistema registra el proceso de alquiler de vehículos de una agencia:

1. Se selecciona el **cliente** y el **vehículo** que se va a entregar.
2. Se indica la **fecha de inicio** y la **cantidad de días**.
3. Se agregan los **servicios adicionales** (GPS, silla para bebé, conductor
   adicional, entrega a domicilio) con su cantidad: cada línea crea una fila en
   la tabla intermedia de la relación N:M.
4. Se captura el **seguro** del alquiler (entidad débil, relación 1:1): tipo y
   cobertura, desde la misma pantalla.
5. El sistema **calcula el total** automáticamente
   (`tarifa por día × días + Σ(precio de servicio × cantidad)`) y lo guarda en
   `alq_total`. El total también se ve en vivo mientras se diligencia el
   formulario.

Reglas de negocio aplicadas en los formularios:

- Un **vehículo no se puede entregar dos veces** en fechas que se traslapan.
- No se aceptan **servicios repetidos** en el mismo alquiler.
- Si se escribe el tipo del seguro, se exige también la cobertura (y viceversa).
- Un cliente o un vehículo con alquileres **no se puede borrar**: la llave
  foránea está en `PROTECT` y la interfaz lo explica en lugar de dar un error.
- Al eliminar un alquiler se advierte que también se van sus servicios
  (`CASCADE`) y su seguro (entidad débil).

**Para quién:** personal de counter de la agencia (registro y edición del
proceso), área de consulta y reportes (solo lectura), y administrador del
sistema (catálogos, usuarios, roles y panel de administración).

## Integrantes
- Luis Felipe Cotes – _usuario de GitHub:_ `@______`
- Alana Marcela Lemus Mendoza – _usuario de GitHub:_ `@______`
- Samir Iguaran – _usuario de GitHub:_ `@______`

> ⚠️ Ajusten los tres usuarios de GitHub y la URL del repositorio antes de subir
> el commit del tercer corte.

## Tecnologías

| Tecnología | Uso |
|---|---|
| **Django 5.2.18** | Backend, modelos, ORM, vistas y formularios |
| **django-jazzmin 3.0.5** | Tema del panel de administración (segundo corte) |
| **Bootstrap 5.3.3** | Framework de CSS de la interfaz, **incluido por CDN** (`bootstrap.min.css` + `bootstrap.bundle.min.js` en `templates/base.html`) |
| **Bootstrap Icons 1.11.3** | Iconografía de la interfaz, **por CDN** |
| **Chart.js 4.4.3** | Gráfico de alquileres por mes del tablero, **por CDN** |
| **Python 3.10+** | Lenguaje del servidor |
| **SQLite (`db.sqlite3`)** | Base de datos con datos de prueba |
| **whitenoise / gunicorn** | Archivos estáticos y despliegue (ver `build.sh`) |

No se instalaron dependencias nuevas de Python en este corte: **el CSS entra por
CDN**, así que `requirements.txt` es el mismo del segundo corte.

### Paleta de colores

Definida una sola vez como variables CSS en `static/css/estilo.css` y usada de
forma coherente en navbar, menú lateral, botones, tarjetas, tablas, insignias de
estado y pie de página:

| Variable | Color | Dónde se usa |
|---|---|---|
| `--azul-900` `#0B2233` | azul profundo | menú lateral y pie de página |
| `--azul-800` `#123C5A` | primario | navbar, botones, títulos, cabecera de tabla |
| `--azul-600` `#1B6CA8` | secundario | enlaces, hover, gráfico y barras |
| `--ambar` `#F2A03D` | acento | botón «Registrar alquiler», avatar, importes destacados |
| `--exito` `#2E8B57` | verde | estado **Vigente** y confirmaciones |
| `--peligro` `#C0392B` | rojo | errores y botones de eliminar |
| `--fondo` `#F4F6F9` | fondo gris claro | fondo de toda la página |

### Estructura del proyecto

```
sistema-alquileres-final/
├── config/
│   ├── settings.py          # templates/, static/, login y MESSAGE_TAGS
│   ├── urls.py              # incluye una url por app + /admin/ + /accounts/
│   ├── mixins.py            # mixin de borrado protegido y de contexto
│   └── vistas.py            # página 403 personalizada
├── alquileres/              # ⭐ proceso principal (CRUD completo)
│   ├── forms.py             # AlquilerForm + formset de servicios (N:M)
│   ├── logica.py            # cálculo de total, días, estado y traslapes
│   ├── views.py             # tablero, listar, crear, detalle, editar, eliminar
│   ├── urls.py              # app_name = "alquileres"
│   ├── templatetags/        # filtros pesos, estado_alquiler, fecha_corta
│   ├── management/commands/ # crear_usuarios_demo, cargar_datos_demo
│   ├── tests.py             # 13 pruebas del CRUD y de la lógica
│   └── admin.py             # (2.º corte, intacto)
├── clientes/ vehiculos/ servicios/   # catálogos, también con CRUD propio
├── seguros/ detalles_alquiler/       # entidad débil y tabla intermedia
├── templates/
│   ├── base.html            # plantilla base: navbar, aside, contenido, footer
│   ├── partials/            # _menu_lateral, _mensajes, _paginacion,
│   │                        # formulario.html y confirmar_eliminar.html
│   ├── registration/login.html
│   ├── 403.html
│   ├── alquileres/          # dashboard, lista, formulario, detalle, eliminar
│   ├── clientes/  vehiculos/  servicios/
├── static/css/estilo.css    # paleta y componentes
├── static/js/alquiler.js    # filas dinámicas y total en vivo
├── docs/                    # diagrama_actores.png, diagrama_er.png (+ fuentes)
├── db.sqlite3               # datos de prueba, incluido en el repo
└── requirements.txt
```

Las plantillas viven en `templates/` (carpeta del proyecto declarada en
`TEMPLATES['DIRS']`), **organizadas por app**, y todas parten de `base.html` con
`{% extends %}`. Cada app tiene su propio `urls.py` con `app_name`, y todos los
enlaces se construyen con `{% url %}`.

## Tablas principales

| Tabla | Descripción |
| --- | --- |
| `clientes_cliente` | Cliente que toma un vehículo (`pk_cli_id`, nombre, documento único, teléfono). Padre de la relación 1:N con alquileres (`PROTECT`). |
| `vehiculos_vehiculo` | Vehículo de la flota: placa única, marca y **tarifa por día**, la base del cálculo del total. |
| `servicios_servicio` | Catálogo de servicios adicionales con su precio (GPS, silla para bebé, etc.). |
| `alquileres_alquiler` | **Proceso principal**: fecha de inicio, total calculado y las dos llaves foráneas (cliente y vehículo). |
| `seguros_seguro` | **Entidad débil**: relación 1:1 con el alquiler (`OneToOneField`, `CASCADE`); tipo y cobertura. No existe sin su alquiler. |
| `detalles_alquiler_alquilerservicio` | **Tabla intermedia** que resuelve la relación N:M entre alquiler y servicio; guarda la cantidad de cada servicio. |

Enlace del repositorio (mismo del segundo corte):
`https://github.com/<usuario>/<repositorio>`

## Diagramas

- **Actores:** `docs/diagrama_actores.png` — con límite del sistema, 5 actores
  (asistente, administrador, analista de consulta, cliente y compañía de
  seguros), cada uno conectado con tres o más casos de uso. Fuente editable:
  `docs/diagrama_actores.puml`.
- **Entidad-relación:** `docs/diagrama_er.png` — las seis tablas con las mismas
  columnas, tipos, `PK`/`FK`/`UNIQUE` y relaciones que tienen los modelos de
  Django, incluidas la 1:N, la N:M resuelta con su tabla intermedia y la entidad
  débil 1:1. Fuente editable: `docs/diagrama_er.mmd`.

**Corregido respecto al segundo corte:**

1. En el ER: se ajustaron los tipos de dato y la notación de las claves para que
   el diagrama coincida exactamente con `models.py`/`migrations/`, y se marcó la
   regla de borrado de cada llave foránea (`PROTECT` / `CASCADE`). No se creó ni
   se unificó ninguna tabla: los actores siguen siendo datos de Django `auth`,
   no una tabla propia, así que el ER no cambia de forma.
2. En el de casos de uso: se trazó el rectángulo del **límite del sistema**, se
   llegó a **tres o más casos de uso por actor** con sus conexiones, se
   agregaron los casos de la interfaz nueva (iniciar/cerrar sesión, tablero,
   búsqueda y filtros, CRUD del alquiler) y los **actores secundarios** que
   participan del proceso.
3. La convención de nombres de columna sigue intacta: `pk_*`, `fk_*` y prefijo
   de tabla (`cli_`, `veh_`, `alq_`, `ser_`, `seg_`, `ase_`).

## Funcionalidades

### Proceso con CRUD completo (desde la interfaz, no desde el admin)

Proceso elegido: **registrar un alquiler: cliente + vehículo + días + servicios
adicionales + seguro** (involucra 5 tablas relacionadas).

| Acción | Ruta | Plantilla |
| --- | --- | --- |
| **Listar** (buscador, filtros por marca/seguro/fecha, orden y paginación) | `/alquileres/` | `alquileres/alquiler_list.html` |
| **Crear** | `/alquileres/registrar/` | `alquileres/alquiler_form.html` |
| **Detalle** (ficha con cliente, vehículo, periodo, servicios, seguro y liquidación) | `/alquileres/<id>/` | `alquileres/alquiler_detail.html` |
| **Editar** (recalcula el total y actualiza servicios y seguro) | `/alquileres/<id>/editar/` | `alquileres/alquiler_form.html` |
| **Eliminar** con página de confirmación previa | `/alquileres/<id>/eliminar/` | `alquileres/alquiler_confirm_delete.html` |
| Datos para el cálculo en vivo (JSON) | `/alquileres/datos-calculo/` | — |

Al guardar, la misma pantalla escribe en `alquileres_alquiler`,
`detalles_alquiler_alquilerservicio` (una fila por servicio) y
`seguros_seguro`, todo dentro de una transacción.

### Interfaz

- `base.html` con **navbar**, **menú lateral (`aside`)** que en pantallas pequeñas
  se vuelve un *offcanvas*, **contenido en tarjetas y tablas** y **pie de página**.
- Paleta de colores definida en `static/css/estilo.css` y aplicada en todo el sitio.
- Formularios con validación en el servidor y **mensajes de éxito/error** en pantalla.
- Cada app tiene su `urls.py` con `app_name` y todas las rutas se resuelven con
  `{% url %}`.

### Adicionales (valor agregado)

- **Inicio y cierre de sesión** con las vistas de `django.contrib.auth`.
- **Roles y permisos** de Django: los menús y los botones aparecen o se ocultan
  según los permisos del usuario (`{% if perms... %}`), y las vistas restringidas
  responden con **403** usando `PermissionRequiredMixin` + `LoginRequiredMixin`.
- **Tablero de indicadores** (`/`): KPIs de alquileres, ingresos totales y del
  mes, flota, catálogo, gráfico de alquileres por mes (Chart.js), marcas más
  alquiladas y alquileres recientes con su estado (Reservado / Vigente /
  Finalizado).
- **Búsquedas y filtros** en alquileres (cliente, documento, placa, marca,
  seguro, rango de fechas, orden) con paginación que conserva los filtros.
- **CRUD de los tres catálogos** (clientes, vehículos, servicios) con páginas de
  ficha que muestran la historia de alquileres de cada registro.
- **Estados derivados** del alquiler sin agregar columnas: periodo, días y estado
  se calculan a partir de la tarifa, el total y los servicios (`alquileres/logica.py`).
- **Validaciones de negocio:** traslapes de vehículo, servicios repetidos,
  seguro incompleto, placa/documento/servicio duplicados, teléfono y tarifas
  fuera de rango.
- **13 pruebas automatizadas** del CRUD, de la lógica del total, de los roles y
  de que el panel de administración del segundo corte sigue funcionando.
- Comando **`crear_usuarios_demo`** que crea roles y usuarios, y **`cargar_datos_demo`**
  que agrega tres alquileres (vigente, reservado y finalizado) calculados con la
  lógica de la interfaz.

## Cómo ejecutar el proyecto

Requisitos: **Python 3.10 o superior**.

1. `git clone <url-del-repositorio>`
2. `cd sistema-alquileres-final`
3. `python -m venv venv`
4. `venv\Scripts\activate`   (Linux/macOS: `source venv/bin/activate`)
5. `pip install -r requirements.txt`
6. `python manage.py migrate`
   *(la base `db.sqlite3` ya trae las migraciones aplicadas y los datos de
   prueba, así que este paso se puede omitir si se usa la base incluida)*
7. `python manage.py runserver`
8. Abrir **<http://127.0.0.1:8000/>** → la página pide inicio de sesión.

Opcional, útil para la socialización:

```bash
python manage.py crear_usuarios_demo        # roles y usuarios de la interfaz
python manage.py cargar_datos_demo          # alquileres con estado vigente/reservado/finalizado
python manage.py test                        # 13 pruebas del CRUD y de la lógica
```

El panel del segundo corte sigue disponible en **<http://127.0.0.1:8000/admin/>**.

## Usuarios de prueba

| Usuario | Contraseña | Rol | Qué puede hacer |
| --- | --- | --- | --- |
| `admin` | `admin123` | Superusuario del admin | Todo, incluido `/admin/` y eliminar registros |
| `vendedor` | `vendedor123` | Asistente de alquiler | Ver, crear y editar alquileres y catálogos; **no puede eliminar** (recibe la página 403) |
| `consultor` | `consultor123` | Consulta y reportes | **Solo lectura**: listados, detalle, filtros y tablero |

> Los roles se crean con `python manage.py crear_usuarios_demo`, que agrega los
> grupos **Asistente de alquiler** (view/add/change) y **Consulta y reportes**
> (view) sobre las seis tablas del proyecto.

## Notas del tercer corte

- **No se cambió el esquema de la base de datos del segundo corte**: ni modelos,
  ni migraciones, ni columnas. Todo lo nuevo son plantillas, estilos, formularios
  y vistas. `python manage.py makemigrations --check` responde `No changes detected`.
- El número de días de alquiler no es una columna: se captura en el formulario y
  con él se calcula `alq_total`. Al editar o listar, los días se deducen de la
  fórmula; si un total registrado a mano desde el admin no da un número exacto de
  días, la interfaz muestra el valor aproximado con `~`.
- Los diagramas del segundo corte no estaban en el ZIP entregado; si en el
  repositorio todavía existen, conservenlos con otro nombre (por ejemplo
  `docs/diagrama_actores_v2.png` y `docs/diagrama_er_v2.png`) para no mezclarlos
  con las versiones corregidas.
- El `.gitignore` excluye el entorno virtual, `__pycache__/` y `staticfiles/`;
  `db.sqlite3` se versiona a propósito porque el entregable pide datos de prueba.
