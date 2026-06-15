# micro-mvp

Microservicios MVP con API Gateway, autenticación, catálogos e inventario.

## Arquitectura

| Servicio              | Puerto | Descripción                              |
|-----------------------|--------|------------------------------------------|
| `api-gateway`         | 8000   | Punto de entrada, proxy y validación JWT |
| `ms-auth`             | 8003   | Autenticación, usuarios, roles y permisos |
| `ms-catalogos`        | 8001   | Categorías, marcas, productos, UOM       |
| `ms-inventario`       | 8002   | Almacenes, existencias y movimientos     |
| `postgres-auth`       | 5434   | Base de datos de autenticación           |
| `postgres-catalogos`  | 5432   | Base de datos de catálogos               |
| `postgres-inventario` | 5433   | Base de datos de inventario              |

## Requisitos

- Docker y Docker Compose

## Inicio rápido

```bash
cp .env.example .env
docker compose up --build
```

Servicios disponibles:

- API Gateway: http://localhost:8000
- ms-auth: http://localhost:8003/docs
- ms-catalogos: http://localhost:8001/docs
- ms-inventario: http://localhost:8002/docs

Usuario admin inicial (seed): `admin` / `Admin123456`

## Variables de entorno

Copia `.env.example` a `.env` y ajusta los valores según tu entorno. **No subas `.env` al repositorio.**

## Estructura

```
micro-mvp/
├── api-gateway/       # Gateway con proxy y middleware JWT
├── ms-auth/           # Microservicio de autenticación
├── ms-catalogos/      # Microservicio de catálogos
├── ms-inventario/     # Microservicio de inventario
├── docker-compose.yml
└── .env.example
```
