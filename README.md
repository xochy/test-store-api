# 🛒 Descripción del Proyecto: API Fake de Gestión de E-commerce

Este proyecto consiste en una **API fake** desarrollada con **Python y FastAPI** que simula la gestión básica de productos y pedidos para un e-commerce. Funciona como un backend ligero y auto-contenido, ideal para fines de desarrollo, pruebas o prototipado, sin necesidad de una base de datos real.

## ✨ Características Principales:

### 📦 **Gestión de Productos (CRUD)**
Permite **crear, leer, actualizar y eliminar** productos. Cada producto cuenta con un `id` único (generado con UUID), `nombre`, `precio` y `descripcion`.

### 🛍️ **Gestión de Pedidos (CRUD)**
Ofrece funcionalidades para **crear, leer, actualizar y eliminar** pedidos. Los pedidos tienen un `id` único, una lista de `product_id` (haciendo referencia a productos existentes), `fecha` de creación y un `estado` (por ejemplo, "pendiente", "completado").

### 📄 **Almacenamiento en JSON**
Los datos de productos y pedidos se persisten en archivos **JSON locales** (`products.json` y `orders.json`), simulando una base de datos simple.

### ⚡ **FastAPI**
Utiliza el framework FastAPI para construir una API RESTful moderna y de alto rendimiento, con validación de datos automática gracias a Pydantic y documentación interactiva (Swagger UI/OpenAPI) integrada.

### 🌐 **Manejo de CORS**
Incorpora configuración para **CORS (Cross-Origin Resource Sharing)**, permitiendo que la API sea consumida desde clientes web alojados en diferentes orígenes (incluyendo archivos locales o servidores de desarrollo como Live Server).

### 🆔 **ID Únicos (UUIDs)**
Generación de identificadores universalmente únicos para productos y pedidos, asegurando la unicidad de los registros.

---

🚀 Este proyecto proporciona una forma rápida y sencilla de tener un servidor de datos simulado para probar interfaces de usuario o desarrollar aplicaciones front-end sin depender de un backend complejo o de servicios en la nube.