import importlib
from Clientes import Cliente
from Reserva import Reserva
from Excepciones import (
    ErrorSoftwareFJ,
    ClienteInvalidoError,
    ServicioNoDisponibleError,
    ReservaFallidaError,
    registrar_log
)

# Importacion compatible con el nombre de archivo "Clase Servicio.py"
modulo_servicios = importlib.import_module("Clase Servicio")
ReservaSala = modulo_servicios.ReservaSala
AlquilerEquipo = modulo_servicios.AlquilerEquipo
AsesoriaEspecializada = modulo_servicios.AsesoriaEspecializada


class SistemaGestionSoftwareFJ:
    """Controlador principal del sistema en memoria (sin base de datos)."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []
        registrar_log("info", "=== INICIO DE EJECUCION DEL SISTEMA SOFTWARE FJ ===")

    def registrar_cliente(self, cedula: str, nombre: str, correo: str, telefono: str):
        """Registra un cliente usando try/except/else."""
        try:
            nuevo_cliente = Cliente(cedula, nombre, correo, telefono)
        except ClienteInvalidoError as e:
            print(f"[ERROR CLIENTE] No se pudo registrar a '{nombre}': {e}")
            return None
        else:
            self.clientes.append(nuevo_cliente)
            print(f"[OK] {nuevo_cliente.obtener_detalles()}")
            return nuevo_cliente

    def registrar_servicio(self, servicio_obj):
        """Agrega un servicio valido a la lista interna."""
        if servicio_obj is not None:
            self.servicios.append(servicio_obj)
            print(f"[OK] {servicio_obj.describir_servicio()}")

    def crear_y_procesar_reserva(self, cliente, servicio, duracion, confirmar=True, procesar=True, **kwargs):
        """Gestiona el ciclo completo de una reserva usando try/except/else/finally."""
        reserva = None
        try:
            reserva = Reserva(cliente, servicio, duracion, **kwargs)
            self.reservas.append(reserva)

            if confirmar:
                reserva.confirmar()

            if procesar:
                costo = reserva.procesar()
                print(f"[OK RESERVA PROCESADA] {reserva.obtener_detalles()}")
                return costo

        except (ClienteInvalidoError, ServicioNoDisponibleError, ReservaFallidaError) as e:
            registrar_log("error", "Fallo controlado en flujo de reserva", e)
            print(f"[ERROR RESERVA] Operacion rechazada: {e}")
            return None

        except Exception as e:
            # Encadenamiento de excepciones ante fallos imprevistos
            error_encadenado = ReservaFallidaError("Error inesperado al gestionar la reserva.")
            registrar_log("error", "Error critico encadenado en reserva", e)
            print(f"[ERROR CRITICO] {error_encadenado}")
            raise error_encadenado from e

        else:
            if not procesar:
                print(f"[OK RESERVA PENDIENTE/CONFIRMADA] {reserva.obtener_detalles()}")

        finally:
            registrar_log("info", "Intento de operacion de reserva finalizado.")


def ejecutar_simulacion():
    print("=" * 70)
    print(" SISTEMA INTEGRAL DE GESTION - SOFTWARE FJ (SIMULACION DE OPERACIONES) ")
    print("=" * 70)

    sistema = SistemaGestionSoftwareFJ()

    # ------------------------------------------------------------------
    #  REGISTRO DE CLIENTES (VALIDOS E INVALIDOS)
    # ------------------------------------------------------------------
    print("\n--- 1. GESTION DE CLIENTES ---")
    # Operacion 1: Cliente valido 1
    c1 = sistema.registrar_cliente("1005487963", "Laura Gomez", "laura.gomez@correo.com", "3104567890")

    # Operacion 2: Cliente valido 2
    c2 = sistema.registrar_cliente("1098765432", "Carlos Mendoza", "cmendoza@empresa.co", "3209876543")

    # Operacion 3: Cliente invalido (cedula muy corta y correo sin @)
    sistema.registrar_cliente("123", "Juan Error", "juan.correo.com", "3001112233")

    # Operacion 4: Cliente invalido (telefono con letras)
    sistema.registrar_cliente("1020304050", "Ana Prueba", "ana@mail.com", "315ABC99")

    # ------------------------------------------------------------------
    #CREACION DE SERVICIOS (VALIDOS E INVALIDOS)
    # ------------------------------------------------------------------
    print("\n--- 2. GESTION DE SERVICIOS ---")
    # Operacion 5: Creacion correcta de Sala VIP
    sala_vip = None
    try:
        sala_vip = ReservaSala("SAL01", "Sala Ejecutiva Norte", 120000, capacidad=10, tipo_sala="VIP")
    except ServicioNoDisponibleError as e:
        print(f"[ERROR SERVICIO] {e}")
    else:
        sistema.registrar_servicio(sala_vip)

    # Operacion 6: Creacion correcta de Alquiler de Equipos
    equipos_pc = None
    try:
        equipos_pc = AlquilerEquipo("EQU01", "Portatiles Workstation", 45000, tipo_equipo="Laptop i7", stock=5)
    except ServicioNoDisponibleError as e:
        print(f"[ERROR SERVICIO] {e}")
    else:
        sistema.registrar_servicio(equipos_pc)

    # Creacion correcta de Asesoria Especializada
    asesoria_cloud = None
    try:
        asesoria_cloud = AsesoriaEspecializada("ASE01", "Arquitectura Cloud", 90000, especialidad="AWS/Azure", nivel="experto")
    except ServicioNoDisponibleError as e:
        print(f"[ERROR SERVICIO] {e}")
    else:
        sistema.registrar_servicio(asesoria_cloud)

    #  Creacion de servicio no disponible (para pruebas de rechazo)
    sala_mantenimiento = ReservaSala("SAL02", "Auditorio Sur", 200000, capacidad=50, disponible=False)
    sistema.registrar_servicio(sala_mantenimiento)

    #  Creacion invalida de servicio (precio negativo)
    try:
        AlquilerEquipo("EQU99", "Proyector 4K", -15000, tipo_equipo="Audiovisual", stock=2)
    except ServicioNoDisponibleError as e:
        registrar_log("error", "Fallo controlado al crear servicio con precio negativo", e)
        print(f"[ERROR SERVICIO] No se pudo crear el equipo: {e}")

    # ------------------------------------------------------------------
    #  RESERVAS EXITOSAS Y FALLIDAS
    # ------------------------------------------------------------------
    print("\n--- 3. PROCESAMIENTO DE RESERVAS ---")

    # Operacion 10: Reserva exitosa de Sala VIP con descuento del 10%
    sistema.crear_y_procesar_reserva(
        cliente=c1,
        servicio=sala_vip,
        duracion=3,
        personas=6,
        descuento=10.0
    )

    #  Reserva exitosa de Alquiler de Equipos (2 dias, 3 equipos)
    sistema.crear_y_procesar_reserva(
        cliente=c2,
        servicio=equipos_pc,
        duracion=2,
        cantidad=3
    ): # type: ignore

    # Reserva exitosa de Asesoria Urgente
    sistema.crear_y_procesar_reserva(
        cliente=c1,
        servicio=asesoria_cloud,
        duracion=4,
        urgente=True
    )

    # Reserva fallida (excede la capacidad de la sala)
    sistema.crear_y_procesar_reserva(
        cliente=c2,
        servicio=sala_vip,
        duracion=2,
        personas=25  # Capacidad maxima es 10
    )

    #  Reserva fallida (servicio marcado como no disponible)
    sistema.crear_y_procesar_reserva( 
        cliente=c1,
        servicio=sala_mantenimiento,
        duracion=2,
        personas=15
    )

    #  Reserva fallida (intentar procesar sin confirmar previamente)
    sistema.crear_y_procesar_reserva(
        cliente=c2,
        servicio=equipos_pc,
        duracion=1,
        cantidad=1,
        confirmar=False,
        procesar=True
    )

    #  Cancelacion controlada de una reserva confirmada
    print("\n--- 4. CANCELACION DE RESERVA ---")
    try:
        reserva_cancelable = Reserva(c1, equipos_pc, 1, cantidad=1)
        reserva_cancelable.confirmar()
        reserva_cancelable.cancelar()
        sistema.reservas.append(reserva_cancelable)
        print(f"[OK CANCELACION] {reserva_cancelable.obtener_detalles()}")
    except ErrorSoftwareFJ as e:
        print(f"[ERROR CANCELACION] {e}") 
    finally:
        registrar_log("info", "Prueba de cancelacion completada.")

    # ------------------------------------------------------------------
    # RESUMEN FINAL EN MEMORIA
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"RESUMEN FINAL: {len(sistema.clientes)} Clientes | {len(sistema.servicios)} Servicios | {len(sistema.reservas)} Reservas registradas")
    print("Registro detallado de eventos y errores guardado en: sistema_software_fj.log")
    print("=" * 70)
    registrar_log("info", "=== FIN DE EJECUCION DEL SISTEMA SOFTWARE FJ ===")


if __name__ == "__main__":
    ejecutar_simulacion()
