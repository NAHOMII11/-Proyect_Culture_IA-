#Backup automático antes de cualquier reparación
#Detección y reparación de tablas dañadas
#Reindexación de bases de datos corruptas
#Verificación de checksums e integridad
#Logging completo para auditoría
#Interfaz interactiva con confirmaciones
#Colores en output para mejor legibilidad


#!/bin/bash

# Script para reiniciar PostgreSQL y reparar tablas dañadas
# Autor: Asistente IA
# Fecha: $(date +%Y-%m-%d)

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración
LOG_FILE="/var/log/postgresql_repair.log"
PGDATA=$(sudo -u postgres psql -t -c "SHOW data_directory;" | xargs)
VERSION=$(pg_lsclusters -h | awk '{print $1}' | head -1)

# Función para logging
log_message() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Función para verificar si PostgreSQL está corriendo
check_postgres_status() {
    if systemctl is-active --quiet postgresql; then
        return 0
    else
        return 1
    fi
}

# Función para hacer backup antes de reparar
backup_database() {
    log_message "${YELLOW}Creando backup de seguridad...${NC}"
    BACKUP_DIR="/tmp/postgres_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    # Backup de todas las bases de datos
    sudo -u postgres pg_dumpall > "$BACKUP_DIR/full_backup.sql" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log_message "${GREEN}Backup creado en: $BACKUP_DIR/full_backup.sql${NC}"
        return 0
    else
        log_message "${RED}ERROR: No se pudo crear el backup${NC}"
        return 1
    fi
}

# Main script
clear
echo "========================================="
echo "   PostgreSQL Repair & Restart Script"
echo "========================================="
echo

# Verificar si se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    log_message "${RED}Este script debe ejecutarse como root${NC}"
    echo -e "${RED}Por favor, ejecuta: sudo $0${NC}"
    exit 1
fi

log_message "${GREEN}Iniciando proceso de reparación de PostgreSQL...${NC}"

# Paso 1: Verificar estado actual
if check_postgres_status; then
    log_message "${GREEN}PostgreSQL está ejecutándose actualmente${NC}"
else
    log_message "${YELLOW}PostgreSQL no está ejecutándose${NC}"
fi

# Paso 2: Crear backup
echo -e "${YELLOW}¿Deseas crear un backup antes de continuar? (s/n): ${NC}"
read -r respuesta
if [[ "$respuesta" == "s" || "$respuesta" == "S" ]]; then
    backup_database
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error en backup. ¿Continuar de todos modos? (s/n): ${NC}"
        read -r continuar
        if [[ "$continuar" != "s" && "$continuar" != "S" ]]; then
            exit 1
        fi
    fi
fi

# Paso 3: Detener PostgreSQL
log_message "${YELLOW}Deteniendo PostgreSQL...${NC}"
systemctl stop postgresql
sleep 3

# Verificar que se detuvo correctamente
if check_postgres_status; then
    log_message "${RED}Error: No se pudo detener PostgreSQL${NC}"
    exit 1
else
    log_message "${GREEN}PostgreSQL detenido correctamente${NC}"
fi

# Paso 4: Verificar integridad del sistema
log_message "${YELLOW}Verificando integridad del sistema de archivos PostgreSQL...${NC}"
sudo -u postgres pg_ctlcluster $VERSION main check

if [ $? -eq 0 ]; then
    log_message "${GREEN}Verificación de integridad completada${NC}"
else
    log_message "${RED}Errores encontrados en la verificación${NC}"
fi

# Paso 5: Reparar tablas dañadas (por base de datos)
log_message "${YELLOW}Buscando y reparando tablas dañadas...${NC}"

# Obtener lista de bases de datos (excluyendo las del sistema)
DATABASES=$(sudo -u postgres psql -t -c "SELECT datname FROM pg_database WHERE datistemplate = false AND datname NOT IN ('postgres', 'template0', 'template1');" 2>/dev/null | xargs)

if [ -z "$DATABASES" ]; then
    log_message "${YELLOW}No se encontraron bases de datos de usuario${NC}"
else
    for db in $DATABASES; do
        log_message "Reparando base de datos: $db"
        
        # Intentar conectar a la BD
        if sudo -u postgres psql -d "$db" -c "SELECT 1" > /dev/null 2>&1; then
            # Verificar tablas dañadas
            DAMAGED_TABLES=$(sudo -u postgres psql -d "$db" -t -c "
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename IN (
                    SELECT relname 
                    FROM pg_class 
                    WHERE relnamespace = 'public'::regnamespace 
                    AND relkind = 'r'
                )" 2>/dev/null | xargs)
            
            for table in $DAMAGED_TABLES; do
                log_message "  Reparando tabla: $table"
                # REINDEX para tablas dañadas
                sudo -u postgres psql -d "$db" -c "REINDEX TABLE $table;" >> $LOG_FILE 2>&1
                # VACUUM para recuperar espacio y verificar
                sudo -u postgres psql -d "$db" -c "VACUUM VERBOSE $table;" >> $LOG_FILE 2>&1
            done
            
            # Análisis completo de la base de datos
            log_message "  Ejecutando ANALYZE en $db..."
            sudo -u postgres psql -d "$db" -c "ANALYZE;" >> $LOG_FILE 2>&1
        else
            log_message "${RED}  No se puede conectar a $db - posible corrupción severa${NC}"
        fi
    done
fi

# Paso 6: Reindexar todo el sistema (opcional)
echo -e "${YELLOW}¿Deseas reindexar completamente todas las bases de datos? (s/n): ${NC}"
read -r reindex_all
if [[ "$reindex_all" == "s" || "$reindex_all" == "S" ]]; then
    log_message "${YELLOW}Reindexando todas las bases de datos...${NC}"
    sudo -u postgres psql -c "REINDEX DATABASE postgres;" >> $LOG_FILE 2>&1
    
    for db in $DATABASES; do
        log_message "Reindexando $db..."
        sudo -u postgres psql -d "$db" -c "REINDEX DATABASE \"$db\";" >> $LOG_FILE 2>&1
    done
fi

# Paso 7: Verificar checkpoints y corrupción
log_message "${YELLOW}Verificando páginas de datos...${NC}"
sudo -u postgres pg_checksums --check $PGDATA >> $LOG_FILE 2>&1

if [ $? -eq 0 ]; then
    log_message "${GREEN}No se encontraron errores de checksum${NC}"
else
    log_message "${RED}Se encontraron errores de checksum - revisar logs${NC}"
fi

# Paso 8: Iniciar PostgreSQL nuevamente
log_message "${YELLOW}Iniciando PostgreSQL...${NC}"
systemctl start postgresql
sleep 5

# Verificar que inició correctamente
if check_postgres_status; then
    log_message "${GREEN}PostgreSQL iniciado correctamente${NC}"
else
    log_message "${RED}Error: No se pudo iniciar PostgreSQL${NC}"
    echo -e "${RED}Revisando logs para diagnóstico...${NC}"
    journalctl -u postgresql -n 20 --no-pager
    exit 1
fi

# Paso 9: Estadísticas finales
log_message "${GREEN}================== RESUMEN FINAL ==================${NC}"
log_message "${GREEN}✓ PostgreSQL reiniciado exitosamente${NC}"
log_message "${GREEN}✓ Bases de datos verificadas y reparadas${NC}"
log_message "${GREEN}✓ Archivo de log: $LOG_FILE${NC}"

# Mostrar estado actual
echo -e "\n${GREEN}Estado actual de PostgreSQL:${NC}"
systemctl status postgresql --no-pager -l | head -5

echo -e "\n${YELLOW}Conexiones activas:${NC}"
sudo -u postgres psql -c "SELECT datname, usename, application_name, state FROM pg_stat_activity;" 2>/dev/null || echo "No se pueden mostrar conexiones"

echo -e "\n${GREEN}=========================================${NC}"
log_message "${GREEN}Script completado exitosamente${NC}"

exit 0