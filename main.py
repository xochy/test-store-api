# main.py
import uvicorn
import json
from uuid import uuid4
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from fastapi.middleware.cors import CORSMiddleware

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
origins = [
    "http://localhost",
    "http://localhost:8080", # Si tu cliente web corre en este puerto
    "http://127.0.0.1",
    "http://127.0.0.1:5500", # Por ejemplo, si usas Live Server de VS Code
    "null", # Permite el acceso desde archivos locales (origin 'null')
    # Puedes añadir más orígenes específicos aquí, como "http://tu-dominio.com"
    # O para permitir cualquier origen (NO RECOMENDADO EN PRODUCCIÓN): "*"
    "https://test-store-front-production.up.railway.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Lista de orígenes permitidos
    allow_credentials=True,      # Permite cookies y encabezados de autenticación
    allow_methods=["*"],         # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],         # Permite todos los encabezados
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