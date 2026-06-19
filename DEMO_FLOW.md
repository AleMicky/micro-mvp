# Flujo de demostración — Plataforma distribuida supermercados

Requisitos: `docker compose up -d` con todos los servicios healthy.

Variables:
```bash
export API=http://localhost:8000
export TOKEN=$(curl -s -X POST "$API/auth/login" -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
export AUTH="Authorization: Bearer $TOKEN"
```

## 1. Crear supermercado OXXO Bolivia (si no existe en seed)
```bash
curl -s -X POST "$API/companias" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"codigo":"OXXO-BOL2","nombre":"OXXO Bolivia","nit":"987654321","activo":true}'
```

## 2. Crear sucursales Prado y El Alto
```bash
# Obtener compañía OXXO (id del seed o creada)
COMPANIA_ID=$(curl -s "$API/companias" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(next(x['id'] for x in d if 'OXXO' in x['nombre']))")

curl -s -X POST "$API/sucursales" -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"codigo\":\"SUC-PRADO2\",\"nombre\":\"Sucursal Prado\",\"compania_id\":$COMPANIA_ID,\"ciudad_id\":1,\"direccion\":\"El Prado\"}"

curl -s -X POST "$API/sucursales" -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"codigo\":\"SUC-ALTO2\",\"nombre\":\"Sucursal El Alto\",\"compania_id\":$COMPANIA_ID,\"ciudad_id\":1,\"direccion\":\"El Alto\"}"
```

## 3. Registrar producto Leche Pil 980cc
```bash
curl -s -X POST "$API/catalogos/productos" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{
    "codigo":"LECHE-PIL-980",
    "codigo_barras":"7790310980123",
    "nombre":"Leche Pil 980cc",
    "descripcion":"Leche entera",
    "categoria_id":1,
    "unidad_medida_id":1,
    "precio_base":"18.50",
    "estado":"ACTIVO",
    "activo":true
  }'
```

## 4. Registrar lote inicial 100 unidades en Sucursal Prado
```bash
PRODUCTO_ID=$(curl -s "$API/catalogos/productos/codigo/LECHE-PIL-980" -H "$AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Crear almacén vinculado a sucursal Prado si no existe
curl -s -X POST "$API/inventario/almacenes" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"codigo":"ALM-PRADO","nombre":"Almacén Sucursal Prado","direccion":"El Prado","activo":true}'

ALMACEN_ID=$(curl -s "$API/inventario/almacenes" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(next(x['id'] for x in d if 'Prado' in x['nombre']))")

curl -s -X POST "$API/inventario/stock/ingreso" -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"producto_id\":$PRODUCTO_ID,\"almacen_id\":$ALMACEN_ID,\"cantidad\":\"100\",\"observaciones\":\"Lote inicial Prado Bs 18.50\"}"
```

## 5–9. Venta a Juanito Pérez (2 unidades) — flujo completo
```bash
CLIENTE_ID=$(curl -s "$API/clientes" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(next(x['id'] for x in d if 'Juanito' in x['nombre']))")

curl -s -X POST "$API/ventas/ventas" -H "$AUTH" -H "Content-Type: application/json" \
  -d "{
    \"cliente_id\":$CLIENTE_ID,
    \"almacen_id\":$ALMACEN_ID,
    \"detalles\":[{\"producto_id\":$PRODUCTO_ID,\"cantidad\":\"2\",\"precio_unitario\":\"18.50\"}]
  }"
```

Esto ejecuta automáticamente: validación catálogo/stock, descuento inventario, factura, CXC, puntos y eventos `SaleCompleted` / `PointsAssigned`.

## 10. Verificar notificación
```bash
sleep 2
curl -s "$API/notificaciones/cliente/$CLIENTE_ID" -H "$AUTH"
```

## 11. Transferir 50 unidades Prado → El Alto
```bash
ALMACEN_ALTO=$(curl -s -X POST "$API/inventario/almacenes" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"codigo":"ALM-ALTO","nombre":"Almacén Sucursal El Alto","activo":true}' 2>/dev/null; \
  curl -s "$API/inventario/almacenes" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(next(x['id'] for x in d if 'Alto' in x['nombre']))")

curl -s -X POST "$API/inventario/stock/transferencia" -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"almacen_origen_id\":$ALMACEN_ID,\"almacen_destino_id\":$ALMACEN_ALTO,\"detalles\":[{\"producto_id\":$PRODUCTO_ID,\"cantidad\":\"50\"}],\"observaciones\":\"Traslado Prado a El Alto\"}"
```

## 12. Saldo consolidado por producto
```bash
curl -s "$API/inventario/stock/consolidado/producto/$PRODUCTO_ID" -H "$AUTH"
```

## 13. Reporte de ventas del día
```bash
curl -s "$API/ventas/ventas/reporte/dia" -H "$AUTH"
```

## Carga masiva Excel (opcional)
Columnas: `codigo`, `producto`, `sucursal`, `cantidad`, `costo`, `precio`

```bash
curl -s -X POST "$API/inventario/loadExcel" -H "$AUTH" -F "file=@scripts/inventario_demo.xlsx"
```

## Health checks
```bash
curl -s "$API/health"
curl -s http://localhost:8008/health  # ms-company
curl -s http://localhost:8009/health  # ms-clientes
curl -s http://localhost:8010/health  # ms-notificaciones
```

## RabbitMQ Management
- URL: http://localhost:15672 (guest/guest)
- Exchange: `micro_mvp_events` (topic)
