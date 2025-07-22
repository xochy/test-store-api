# 📚 Guía Completa del Proyecto: API Fake de Gestión de E-commerce

Este documento resume el desarrollo de una API fake para simular la gestión de productos y pedidos en un entorno de e-commerce. La API está construida con Python 3.10.6 y el framework FastAPI, utilizando archivos JSON locales para la persistencia de datos. Incluye todas las operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para ambos modelos y está preparada para ser ejecutada tanto localmente como desplegada en servicios como Railway.app.

## 🎯 1. Descripción del Proyecto

La API fake de E-commerce es un backend ligero diseñado para propósitos de desarrollo, pruebas o prototipado. Simula las funcionalidades básicas de una tienda online:

- **📦 Gestión de Productos**: Permite administrar productos con atributos como id (UUID), nombre, precio y descripcion.
- **📋 Gestión de Pedidos**: Facilita la administración de pedidos, incluyendo id (UUID), una lista de product_id (referenciando productos existentes), fecha de creación y estado (ej. "pendiente").
- **💾 Persistencia de Datos**: Los datos se guardan en archivos JSON (products.json y orders.json) en el sistema de archivos local, actuando como una "base de datos" simple.
- **🌐 API RESTful**: Implementa una interfaz RESTful completa con FastAPI, ofreciendo validación de datos (Pydantic) y documentación interactiva automática (Swagger UI/OpenAPI).
- **🔄 CORS Habilitado**: Configurada para permitir solicitudes de origen cruzado, esencial para interactuar con clientes web (frontends) desde diferentes dominios, tanto en desarrollo local como en producción.

## 📁 2. Estructura del Proyecto

Tu proyecto debe tener la siguiente estructura de archivos en el mismo directorio:

```
tu_proyecto/
├── main.py
├── products.json  (se creará automáticamente si no existe)
└── orders.json    (se creará automáticamente si no existe)
└── requirements.txt
```

## 💻 3. Código Fuente Completo (main.py)

A continuación, se presenta el código completo de tu API de FastAPI, incluyendo la configuración de CORS para permitir la comunicación con tu frontend, tanto localmente como en un entorno desplegado (ej. Railway.app).

```python
# main.py
import uvicorn
import json
from uuid import uuid4
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware # Importación de CORS
from pydantic import BaseModel, Field

# --- Modelos Pydantic ---

class ProductBase(BaseModel):
    nombre: str = Field(..., example="Laptop Gamer")
    precio: float = Field(..., gt=0, example=1200.50)
    descripcion: str = Field(..., example="Potente laptop para gaming con RTX 3080.")

class ProductCreate(ProductBase):
    pass

class ProductInDB(ProductBase):
    id: str = Field(..., example="a1b2c3d4-e5f6-7890-1234-567890abcdef")

    class Config:
        from_attributes = True

class OrderItem(BaseModel):
    product_id: str = Field(..., example="a1b2c3d4-e5f6-7890-1234-567890abcdef")

class OrderCreate(BaseModel):
    products: List[OrderItem] = Field(..., min_length=1)

class OrderInDB(BaseModel):
    id: str = Field(..., example="fedcba98-7654-3210-fedc-ba9876543210")
    products: List[str] = Field(..., example=["a1b2c3d4-e5f6-7890-1234-567890abcdef", "b2c3d4e5-f6a7-8901-2345-67890abcdef0"])
    fecha: datetime = Field(..., example="2024-07-21T18:30:00.000000")
    estado: str = Field(..., example="pendiente")

    class Config:
        from_attributes = True

# --- Rutas de Archivos JSON ---
PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"

# --- Funciones Auxiliares para Archivos JSON ---

def _load_data(filename: str) -> List[Dict[str, Any]]:
    """Carga datos desde un archivo JSON."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Advertencia: El archivo '{filename}' está corrupto o vacío. Iniciando con datos vacíos.")
        return []

def _save_data(filename: str, data: List[Dict[str, Any]]):
    """Guarda datos en un archivo JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_products_data() -> List[Dict[str, Any]]:
    return _load_data(PRODUCTS_FILE)

def save_products_data(data: List[Dict[str, Any]]):
    _save_data(PRODUCTS_FILE, data)

def get_orders_data() -> List[Dict[str, Any]]:
    return _load_data(ORDERS_FILE)

def save_orders_data(data: List[Dict[str, Any]]):
    _save_data(ORDERS_FILE, data)

# --- Inicialización de FastAPI ---
app = FastAPI(
    title="Fake E-commerce API",
    description="API fake para simulación de gestión de productos y pedidos con datos en JSON.",
    version="1.0.0",
)

# --- Configuración CORS ---
# Lista de orígenes permitidos para acceder a tu API
origins = [
    "http://localhost",
    "http://localhost:8080", # Puerto común para desarrollo de frontends
    "http://127.0.0.1",
    "http://127.0.0.1:5500", # Ejemplo si usas Live Server de VS Code
    "null", # Permite el acceso desde archivos HTML abiertos directamente (origin 'null')
    "https://test-store-front-production.up.railway.app" # URL de tu frontend desplegado en Railway
    # Si tienes más orígenes de frontend, añádelos aquí
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Orígenes permitidos
    allow_credentials=True,      # Permite cookies y encabezados de autenticación
    allow_methods=["*"],         # Permite todos los métodos HTTP (GET, POST, PUT, DELETE)
    allow_headers=["*"],         # Permite todos los encabezados HTTP
)

# --- Endpoints para Productos ---

@app.get("/products/", response_model=List[ProductInDB], summary="Obtener todos los productos")
async def get_all_products():
    """
    Recupera una lista de todos los productos disponibles.
    """
    products = get_products_data()
    return products

@app.get("/products/{product_id}", response_model=ProductInDB, summary="Obtener producto por ID")
async def get_product_by_id(product_id: str):
    """
    Recupera un producto específico utilizando su ID.
    """
    products = get_products_data()
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Producto con ID '{product_id}' no encontrado"
    )

@app.post("/products/", response_model=ProductInDB, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo producto")
async def create_product(product: ProductCreate):
    """
    Crea un nuevo producto con un ID único.
    """
    products = get_products_data()
    new_product = product.model_dump()
    new_product["id"] = str(uuid4())
    products.append(new_product)
    save_products_data(products)
    return new_product

@app.put("/products/{product_id}", response_model=ProductInDB, summary="Actualizar un producto existente")
async def update_product(product_id: str, product_update: ProductCreate):
    """
    Actualiza los detalles de un producto existente.
    """
    products = get_products_data()
    for i, product in enumerate(products):
        if product["id"] == product_id:
            updated_product = product_update.model_dump()
            updated_product["id"] = product_id  # Aseguramos que el ID no cambie
            products[i] = updated_product
            save_products_data(products)
            return updated_product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Producto con ID '{product_id}' no encontrado"
    )

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un producto")
async def delete_product(product_id: str):
    """
    Elimina un producto de la lista.
    """
    products = get_products_data()
    initial_len = len(products)
    products = [p for p in products if p["id"] != product_id]
    if len(products) == initial_len:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID '{product_id}' no encontrado"
        )
    save_products_data(products)
    return {"message": "Producto eliminado exitosamente"}

# --- Endpoints para Pedidos (Orders) ---

@app.get("/orders/", response_model=List[OrderInDB], summary="Obtener todos los pedidos")
async def get_all_orders():
    """
    Recupera una lista de todos los pedidos realizados.
    """
    orders = get_orders_data()
    return orders

@app.get("/orders/{order_id}", response_model=OrderInDB, summary="Obtener pedido por ID")
async def get_order_by_id(order_id: str):
    """
    Recupera un pedido específico utilizando su ID.
    """
    orders = get_orders_data()
    for order in orders:
        if order["id"] == order_id:
            return order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Pedido con ID '{order_id}' no encontrado"
    )

@app.post("/orders/", response_model=OrderInDB, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo pedido")
async def create_order(order: OrderCreate):
    """
    Crea un nuevo pedido con una lista de IDs de productos.
    Verifica que los productos existan.
    """
    products_in_db = get_products_data()
    existing_product_ids = {p["id"] for p in products_in_db}
    
    # Validar que todos los product_id en el pedido existan
    requested_product_ids = [item.product_id for item in order.products]
    for p_id in requested_product_ids:
        if p_id not in existing_product_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Producto con ID '{p_id}' no encontrado. No se puede crear el pedido."
            )

    orders = get_orders_data()
    new_order_data = {
        "id": str(uuid4()),
        "products": requested_product_ids,
        "fecha": datetime.now().isoformat(),
        "estado": "pendiente"  # Estado inicial por defecto
    }
    orders.append(new_order_data)
    save_orders_data(orders)
    return new_order_data

@app.put("/orders/{order_id}", response_model=OrderInDB, summary="Actualizar un pedido existente")
async def update_order(order_id: str, updated_order_data: Dict[str, Any]):
    """
    Actualiza el estado u otros detalles de un pedido existente.
    Permite actualizar 'estado' y la lista de 'products'.
    La fecha no es actualizable.
    """
    orders = get_orders_data()
    products_in_db = get_products_data()
    existing_product_ids = {p["id"] for p in products_in_db}

    for i, order in enumerate(orders):
        if order["id"] == order_id:
            # Validar y actualizar productos si se proporcionan
            if "products" in updated_order_data:
                requested_product_ids = updated_order_data["products"]
                for p_id in requested_product_ids:
                    if p_id not in existing_product_ids:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Producto con ID '{p_id}' no encontrado. No se puede actualizar el pedido."
                        )
                order["products"] = requested_product_ids
            
            # Actualizar estado si se proporciona
            if "estado" in updated_order_data:
                order["estado"] = updated_order_data["estado"]
            
            orders[i] = order
            save_orders_data(orders)
            return order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Pedido con ID '{order_id}' no encontrado"
    )


@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un pedido")
async def delete_order(order_id: str):
    """
    Elimina un pedido de la lista.
    """
    orders = get_orders_data()
    initial_len = len(orders)
    orders = [o for o in orders if o["id"] != order_id]
    if len(orders) == initial_len:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido con ID '{order_id}' no encontrado"
        )
    save_orders_data(orders)
    return {"message": "Pedido eliminado exitosamente"}


if __name__ == "__main__":
    # Asegúrate de que los archivos JSON existan con contenido inicial si están vacíos
    # Esto es útil para la primera ejecución
    _ = get_products_data() # Carga para crear el archivo si no existe
    _ = get_orders_data()   # Carga para crear el archivo si no existe

    print("\nAPI Fake lista para usarse.")
    print("Accede a la documentación interactiva en: http://127.0.0.1:8000/docs")
    print("Para detener el servidor, presiona CTRL+C en la terminal.")
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

## 📋 4. Dependencias del Proyecto (requirements.txt)

Este archivo lista todas las librerías de Python que tu proyecto necesita para funcionar. Crea un archivo llamado `requirements.txt` en el mismo directorio que `main.py` y copia el siguiente contenido:

```txt
fastapi
uvicorn
pydantic
pydantic-settings
typing-extensions
```

*(Nota: `pip freeze > requirements.txt` puede generar más líneas, pero estas son las esenciales para el funcionamiento básico del proyecto.)*

## 🚀 5. Guía de Ejecución Local

Sigue estos pasos para poner en marcha tu API fake en tu máquina local:

### a. ⚙️ Requisitos Previos

- **🐍 Python 3.10.6** (o una versión compatible, Python 3.8+ generalmente funciona bien con FastAPI).
- **📦 Pip** (gestor de paquetes de Python), que viene incluido con Python.

### b. 📂 Preparación de Archivos

1. Crea una carpeta para tu proyecto (ej. `mi_api_fake`).
2. Guarda el código de `main.py` (el que se muestra arriba) dentro de esta carpeta.
3. Crea el archivo `requirements.txt` con el contenido proporcionado en el punto 4, y guárdalo en la misma carpeta.

### c. 🔧 Instalación de Dependencias

1. Abre tu terminal o línea de comandos.
2. Navega hasta la carpeta de tu proyecto usando el comando `cd`:
   ```bash
   cd ruta/a/tu/carpeta/mi_api_fake
   ```
   *(Reemplaza `ruta/a/tu/carpeta/mi_api_fake` con la ruta real de tu carpeta).*
3. Una vez dentro de la carpeta, instala todas las dependencias listadas en `requirements.txt` ejecutando:
   ```bash
   pip install -r requirements.txt
   ```
   Esto descargará e instalará FastAPI, Uvicorn, Pydantic y sus dependencias.

### d. ▶️ Ejecución de la API

Desde la misma terminal y dentro de la carpeta de tu proyecto, ejecuta el siguiente comando para iniciar la API:

```bash
python main.py
```

Deberías ver una salida similar a esta en tu terminal:

```
INFO:     Will watch for changes in these directories: ['/ruta/a/tu/carpeta/mi_api_fake']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

API Fake lista para usarse.
Accede a la documentación interactiva en: http://127.0.0.1:8000/docs
Para detener el servidor, presiona CTRL+C en la terminal.
```

### e. 📖 Acceso a la Documentación Interactiva (Swagger UI)

Abre tu navegador web y ve a la dirección: `http://127.0.0.1:8000/docs`

Aquí encontrarás la interfaz Swagger UI, que es la documentación interactiva de tu API. Podrás ver todos los endpoints (`/products/`, `/orders/`, etc.), sus métodos (GET, POST, PUT, DELETE), los modelos de datos esperados y las respuestas. ¡Incluso puedes probar las solicitudes directamente desde esta interfaz!

### f. 📄 Archivos JSON de Datos

- Cuando ejecutes `main.py` por primera vez, si los archivos `products.json` y `orders.json` no existen, se crearán automáticamente en el mismo directorio.
- Estos archivos se actualizarán cada vez que realices operaciones de creación, actualización o eliminación a través de la API. Puedes abrirlos con un editor de texto para ver los datos.

## ☁️ 6. Resumen del Despliegue en Railway.app (Contexto)

Aunque esta guía se centra en la ejecución local, es importante recordar que este proyecto también ha sido preparado para el despliegue en Railway.app.

- **📋 Preparación**: Se creó un archivo `requirements.txt` para que Railway sepa qué dependencias instalar.
- **🚢 Despliegue**: La aplicación se puede desplegar fácilmente desde un repositorio de GitHub o usando la CLI de Railway.
- **🔄 CORS en Producción**: Se añadió la URL de tu frontend desplegado (`https://test-store-front-production.up.railway.app`) a la lista `allow_origins` en el CORSMiddleware de FastAPI. Esto asegura que tu frontend pueda comunicarse con tu API una vez que ambos estén en Railway, resolviendo los errores de CORS en un entorno de producción.

---

¡Con esta guía, tienes un panorama completo del proyecto y todas las herramientas necesarias para ejecutar y probar tu API fake de e-commerce localmente! Si tienes más preguntas o necesitas alguna modificación, no dudes en consultarme.