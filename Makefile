SHELL := /bin/sh
COMPOSE := docker compose

APP_SERVICES := frontend api-gateway ms-auth ms-catalogos ms-chatbot ms-clientes \
                ms-company ms-compras ms-finanzas ms-inventario ms-notificaciones \
                ms-reportes ms-ventas

.DEFAULT_GOAL := help

.PHONY: help up down restart ps status logs logs-tail build rebuild \
        $(addprefix build-,$(APP_SERVICES)) \
        $(addprefix rebuild-,$(APP_SERVICES)) \
        $(addprefix logs-,$(APP_SERVICES)) \
        $(addprefix restart-,$(APP_SERVICES)) \
        $(addprefix shell-,$(APP_SERVICES)) \
        frontend backend clean prune-volumes seed-info urls \
        tunnel-chatbot logs-tunnel

## ---- Ciclo de vida general -------------------------------------------------

up: ## Levanta todos los servicios en background
	$(COMPOSE) up -d

down: ## Detiene y elimina todos los contenedores (conserva volumenes)
	$(COMPOSE) down

restart: ## Reinicia todos los servicios sin rebuild
	$(COMPOSE) restart

ps: ## Muestra el estado de los contenedores
	$(COMPOSE) ps

status: ps ## Alias de ps

build: ## Reconstruye TODAS las imagenes (sin reiniciar)
	$(COMPOSE) build

rebuild: build up ## Reconstruye todas las imagenes y reinicia los contenedores

## ---- Build/rebuild por servicio --------------------------------------------
## Usar cuando se edita codigo de un microservicio o el frontend.
## Este proyecto NO tiene hot-reload: hay que rebuildear el contenedor
## despues de cada cambio de codigo para verlo reflejado.

$(addprefix build-,$(APP_SERVICES)): build-%: ## build-<servicio>: reconstruye la imagen de un servicio (ej. make build-frontend)
	$(COMPOSE) build $*

$(addprefix rebuild-,$(APP_SERVICES)): rebuild-%: ## rebuild-<servicio>: reconstruye y reinicia un servicio (ej. make rebuild-ms-ventas)
	$(COMPOSE) build $*
	$(COMPOSE) up -d $*

frontend: rebuild-frontend ## Atajo: reconstruye y reinicia solo el frontend

backend: ## Reconstruye y reinicia todos los microservicios backend (sin frontend ni DBs)
	$(COMPOSE) build $(filter-out frontend,$(APP_SERVICES))
	$(COMPOSE) up -d $(filter-out frontend,$(APP_SERVICES))

## ---- Logs -------------------------------------------------------------------

logs: ## Sigue los logs de todos los servicios
	$(COMPOSE) logs -f

logs-tail: ## Muestra las ultimas 200 lineas de logs de todos los servicios
	$(COMPOSE) logs --tail=200

$(addprefix logs-,$(APP_SERVICES)): logs-%: ## logs-<servicio>: sigue los logs de un servicio (ej. make logs-ms-ventas)
	$(COMPOSE) logs -f $*

## ---- Restart / shell por servicio -------------------------------------------

$(addprefix restart-,$(APP_SERVICES)): restart-%: ## restart-<servicio>: reinicia un servicio sin rebuild (ej. make restart-ms-inventario)
	$(COMPOSE) restart $*

$(addprefix shell-,$(APP_SERVICES)): shell-%: ## shell-<servicio>: abre una shell dentro del contenedor (ej. make shell-ms-ventas)
	docker exec -it $* sh

## ---- Utilidades --------------------------------------------------------------

urls: ## Muestra las URLs principales del proyecto
	@echo "Frontend:    http://localhost:5173"
	@echo "API Gateway: http://localhost:8000"
	@echo "RabbitMQ UI: http://localhost:15672"

tunnel-chatbot: ## [legacy] Alternativa manual via cloudflared local; normalmente el tunnel ya corre solo (servicio tunnel-chatbot en docker-compose)
	mkdir -p .tunnel
	rm -f .tunnel/chatbot.log
	cloudflared tunnel --url http://localhost:8011 2>&1 | tee .tunnel/chatbot.log

logs-tunnel: ## Sigue los logs del contenedor tunnel-chatbot (URL publica aparece ahi)
	$(COMPOSE) logs -f tunnel-chatbot

clean: down ## Detiene contenedores y elimina imagenes huerfanas
	docker image prune -f

prune-volumes: ## PELIGRO: elimina contenedores y TODOS los volumenes (borra datos de las DB)
	$(COMPOSE) down -v

help: ## Muestra esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Comandos por servicio (sustituir <servicio> por uno de):"
	@echo "  $(APP_SERVICES)" | fold -s -w 90 | sed 's/^/    /'
	@echo ""
	@echo "  build-<servicio>     reconstruye la imagen de ese servicio"
	@echo "  rebuild-<servicio>   reconstruye y reinicia ese servicio"
	@echo "  restart-<servicio>   reinicia ese servicio sin rebuild"
	@echo "  logs-<servicio>      sigue los logs de ese servicio"
	@echo "  shell-<servicio>     abre una shell dentro del contenedor"
	@echo ""
	@echo "  Ejemplos: make rebuild-frontend | make logs-ms-ventas | make shell-ms-inventario"
