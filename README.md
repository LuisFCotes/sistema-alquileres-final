# Sistema de Alquiler de Vehículos

## Descripción

Sistema web desarrollado con **Django** para gestionar el alquiler de vehículos: clientes,
vehículos, alquileres, seguros asociados a cada alquiler y servicios adicionales contratados.

El proyecto (`sistema_alquileres`) usa una **arquitectura multi-app**: cada tabla del modelo
entidad-relación vive en su propia aplicación Django, y el directorio de configuración se llama `config/`.

| App | Modelo | Descripción |
|---|---|---|
| `clientes` | `Cliente` | Personas que alquilan vehículos |
| `vehiculos` | `Vehiculo` | Flota disponible y su tarifa por día |
| `alquileres` | `Alquiler` | Alquiler de un vehículo por un cliente (FK a `Cliente` y `Vehiculo`) |
| `seguros` | `Seguro` | **Entidad débil**: relación 1:1 con `Alquiler` |
| `servicios` | `Servicio` | Catálogo de servicios adicionales |
| `detalles_alquiler` | `AlquilerServicio` | **Tabla intermedia** de la relación N:M entre `Alquiler` y `Servicio` |

> **Versión con diseño mejorado:** esta variante del proyecto usa
> [django-jazzmin](https://github.com/farridav/django-jazzmin) para un panel de administración
> más moderno (tema claro/oscuro, iconos, menú superior, inlines en pestañas). La lógica,
> los modelos y los datos son idénticos a la versión con el diseño estándar de Django.

### Panel de administración

- `Cliente`, `Vehiculo`, `Alquiler` y `Servicio` se registran en el `admin.py` de su app, con
  `list_display`, `search_fields` y `list_filter`.
- `Seguro` (entidad débil) y `AlquilerServicio` (tabla intermedia) **no se registran sueltos**: se editan
  dentro del formulario de `Alquiler` como `StackedInline` y `TabularInline` (ver `alquileres/admin.py`).
- Las llaves foráneas usan `autocomplete_fields`.

## Estructura del proyecto

```
sistema_alquileres/
├── config/               
├── clientes/
├── vehiculos/
├── alquileres/
├── seguros/
├── servicios/
├── detalles_alquiler/
├── docs/                 # diagramas ER
├── manage.py
├── requirements.txt      # Django + django-jazzmin
├── .gitignore
├── README.md
└── db.sqlite3            # base de datos para probar
```

## Instrucciones de ejecución

Requisitos: Python 3.10 o superior.

1. **Crear el entorno virtual**

   ```bash
   python -m venv venv
   ```

2. **Activar el entorno virtual**

   - Windows (PowerShell / CMD): `venv\Scripts\activate`
   - Linux / macOS: `source venv/bin/activate`

3. **Instalar las dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Iniciar el servidor**

   ```bash
   python manage.py runserver
   ```

5. Abrir <http://127.0.0.1:8000/admin/> en el navegador.

> La base de datos `db.sqlite3` ya incluye las migraciones aplicadas y los datos de prueba,
> por lo que no es necesario ejecutar `migrate`. Si se parte de una base de datos vacía:
> `python manage.py migrate`.

## Credenciales del superusuario

| Usuario | Clave |
|---|---|
| `admin` | `admin123` |

## Datos de prueba incluidos

4 clientes, 4 vehículos, 4 alquileres, 4 seguros, 4 servicios y 6 detalles de alquiler.

## Integrantes

- Luis Felipe Cotes
- Alana Marcela Lemus Mendoza
- Samir Iguaran
