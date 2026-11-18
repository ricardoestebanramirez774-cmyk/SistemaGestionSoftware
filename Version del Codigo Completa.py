import logging
from abc import ABC, abstractmethod

# =====================================================================
# 1. CONFIGURACIÓN DE LOGS Y EXCEPCIONES PERSONALIZADAS
# =====================================================================

# Configuración del archivo de registro de eventos y errores (sin BD)
logging.basicConfig(
    filename="sistema_software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


class ErrorSoftwareFJ(Exception):
    """Excepción base personalizada para el sistema de Software FJ."""
    pass


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando los datos personales del cliente son inválidos."""
    pass


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando un servicio o parámetro de cálculo es inválido."""
    pass


class ReservaFallidaError(ErrorSoftwareFJ):
    """Se lanza cuando ocurre un fallo al procesar o cancelar una reserva."""
    pass


def registrar_log(nivel: str, mensaje: str, excepcion: Exception = None):
    """Registra eventos informativos y errores detallados en el archivo .log."""
    if nivel == "info":
        logging.info(mensaje)
    elif nivel == "error":
        if excepcion:
            logging.error(f"{mensaje} | Detalle: {excepcion}", exc_info=True)
        else:
            logging.error(mensaje)


# =====================================================================
# 2. CLASE ABSTRACTA BASE Y CLASE CLIENTE (ENCAPSULACIÓN)
# =====================================================================

class EntidadBase(ABC):
    """Clase abstracta general para las entidades del sistema."""

    @abstractmethod
    def obtener_detalles(self) -> str:
        """Retorna una descripción detallada de la entidad."""
        pass


class Cliente(EntidadBase):
    """Representa a un cliente con validaciones estrictas y atributos privados."""

    def __init__(self, cedula: str, nombre: str, correo: str, telefono: str):
        self.__cedula = self.__validar_cedula(cedula)
        self.__nombre = self.__validar_nombre(nombre)
        self.__correo = self.__validar_correo(correo)
        self.__telefono = self.__validar_telefono(telefono)
        registrar_log("info", f"Cliente registrado: {self.__nombre} (CC: {self.__cedula})")

    # Propiedades (Getters) para garantizar encapsulación
    @property
    def cedula(self) -> str:
        return self.__cedula

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def correo(self) -> str:
        return self.__correo

    @property
    def telefono(self) -> str:
        return self.__telefono

    def __validar_cedula(self, cedula: str) -> str:
        try:
            if not cedula or not cedula.isdigit() or len(cedula) < 6:
                raise ClienteInvalidoError(f"Cédula inválida ('{cedula}'). Debe tener mínimo 6 dígitos numéricos.")
            return cedula
        except Exception as e:
            registrar_log("error", f"Fallo al validar cédula: {cedula}", e)
            raise

    def __validar_nombre(self, nombre: str) -> str:
        if not nombre or len(nombre.strip()) < 3:
            err = ClienteInvalidoError(f"Nombre inválido ('{nombre}'). Mínimo 3 caracteres.")
            registrar_log("error", "Validación de nombre fallida", err)
            raise err
        return nombre.strip()

    def __validar_correo(self, correo: str) -> str:
        if not correo or "@" not in correo or "." not in correo:
            err = ClienteInvalidoError(f"Correo electrónico inválido ('{correo}').")
            registrar_log("error", "Validación de correo fallida", err)
            raise err
        return correo.strip()

    def __validar_telefono(self, telefono: str) -> str:
        if not telefono or not telefono.isdigit() or len(telefono) < 7:
            err = ClienteInvalidoError(f"Teléfono inválido ('{telefono}'). Mínimo 7 dígitos.")
            registrar_log("error", "Validación de teléfono fallida", err)
            raise err
        return telefono.strip()

    def obtener_detalles(self) -> str:
        return f"Cliente: {self.__nombre} | CC: {self.__cedula} | Email: {self.__correo} | Tel: {self.__telefono}"


# =====================================================================
# CLASE ABSTRACTA SERVICIO
# =====================================================================

class Servicio(EntidadBase):
    """Clase base para todos los servicios de la empresa."""

    def __init__(self, codigo, nombre, precio_base, disponible=True):
        self.codigo = self.validar_codigo(codigo)
        self.nombre = self.validar_nombre(nombre)
        self.precio_base = self.validar_precio(precio_base)
        self.disponible = disponible
        registrar_log("info", f"Servicio creado: {self.nombre}")

    def validar_codigo(self, codigo):
        if not codigo or len(codigo.strip()) < 3:
            raise ServicioNoDisponibleError("El código del servicio debe tener mínimo 3 caracteres.")
        return codigo.strip().upper()

    def validar_nombre(self, nombre):
        if not nombre or len(nombre.strip()) < 3:
            raise ServicioNoDisponibleError("El nombre del servicio debe tener mínimo 3 caracteres.")
        return nombre.strip()

    def validar_precio(self, precio):
        try:
            p = float(precio)
            if p <= 0:
                raise ServicioNoDisponibleError("El precio base debe ser mayor a cero.")
            return p
        except ValueError:
            raise ServicioNoDisponibleError("El precio base debe ser un número válido.")

    @abstractmethod
    def calcular_costo(self, *args, **kwargs):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    @abstractmethod
    def validar_parametros(self, **kwargs):
        pass

    def obtener_detalles(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return f"Servicio: {self.nombre} | Código: {self.codigo} | Precio: ${self.precio_base:,.2f} | Estado: {estado}"

    def __str__(self):
        return self.obtener_detalles()


# =====================================================================
# SERVICIO 1: RESERVA DE SALAS
# =====================================================================

class ReservaSala(Servicio):

    def __init__(self, codigo, nombre, precio_base, capacidad, tipo_sala="Estándar", disponible=True):
        super().__init__(codigo, nombre, precio_base, disponible)
        self.capacidad = int(capacidad)
        self.tipo_sala = tipo_sala

    def validar_parametros(self, **kwargs):
        horas = kwargs.get("horas")
        personas = kwargs.get("personas")

        if horas is None or personas is None:
            raise ServicioNoDisponibleError("Faltan datos obligatorios (horas o personas) para la sala.")

        if float(horas) <= 0:
            raise ServicioNoDisponibleError("Las horas deben ser mayores a cero.")

        if int(personas) > self.capacidad:
            raise ServicioNoDisponibleError(f"La cantidad de personas ({personas}) supera la capacidad de la sala ({self.capacidad}).")

        return True

    def calcular_costo(self, horas=1, personas=1, descuento=0.0):
        self.validar_parametros(horas=horas, personas=personas)

        costo = self.precio_base * float(horas)

        if self.tipo_sala.lower() in ("vip", "premium"):
            costo *= 1.25

        if descuento > 0:
            costo *= (1 - descuento / 100)

        # Aplicar IVA del 19%
        costo_total = costo * 1.19
        registrar_log("info", f"Costo calculado para sala {self.nombre}: ${costo_total:,.2f}")
        return round(costo_total, 2)

    def describir_servicio(self):
        return f"Reserva de Sala: {self.nombre} ({self.tipo_sala}) - Capacidad: {self.capacidad}"


# =====================================================================
# SERVICIO 2: ALQUILER DE EQUIPOS
# =====================================================================

class AlquilerEquipo(Servicio):

    def __init__(self, codigo, nombre, precio_base, tipo_equipo, stock=1, disponible=True):
        super().__init__(codigo, nombre, precio_base, disponible)
        self.tipo_equipo = tipo_equipo
        self.stock = int(stock)

    def validar_parametros(self, **kwargs):
        dias = kwargs.get("dias")
        cantidad = kwargs.get("cantidad", 1)

        if dias is None:
            raise ServicioNoDisponibleError("Se requiere especificar los días de alquiler.")

        if int(dias) < 1:
            raise ServicioNoDisponibleError("El alquiler debe ser de al menos 1 día.")

        if int(cantidad) > self.stock:
            raise ServicioNoDisponibleError(f"No hay suficiente stock. Stock disponible: {self.stock}")

        return True

    def calcular_costo(self, dias=1, cantidad=1, descuento=0.0):
        self.validar_parametros(dias=dias, cantidad=cantidad)

        costo = self.precio_base * int(dias) * int(cantidad)

        if descuento > 0:
            costo *= (1 - descuento / 100)

        costo_total = costo * 1.19
        registrar_log("info", f"Costo calculado para equipo {self.nombre}: ${costo_total:,.2f}")
        return round(costo_total, 2)

    def describir_servicio(self):
        return f"Alquiler de Equipo: {self.nombre} ({self.tipo_equipo}) - Stock: {self.stock}"

# =====================================================================
# SERVICIO 3: ASESORÍAS ESPECIALIZADAS
# =====================================================================

class AsesoriaEspecializada(Servicio):

    def __init__(self, codigo, nombre, precio_base, especialidad, nivel="senior", disponible=True):
        super().__init__(codigo, nombre, precio_base, disponible)
        self.especialidad = especialidad
        self.nivel = nivel.lower()

    def validar_parametros(self, **kwargs):
        horas = kwargs.get("horas")
        if horas is None:
            raise ServicioNoDisponibleError("Se requieren las horas de asesoría.")
        if float(horas) <= 0:
            raise ServicioNoDisponibleError("Las horas deben ser mayores a cero.")
        return True

    def calcular_costo(self, horas=1.0, descuento=0.0, urgente=False):
        self.validar_parametros(horas=horas)

        multiplicador = 1.0
        if self.nivel == "junior":
            multiplicador = 0.8
        elif self.nivel == "senior":
            multiplicador = 1.3
        elif self.nivel == "experto":
            multiplicador = 1.6

        costo = self.precio_base * float(horas) * multiplicador

        if urgente:
            costo *= 1.30

        if descuento > 0:
            costo *= (1 - descuento / 100)

        costo_total = costo * 1.19
        registrar_log("info", f"Costo calculado para asesoría {self.nombre}: ${costo_total:,.2f}")
        return round(costo_total, 2)

    def describir_servicio(self):
        return f"Asesoría Especializada: {self.nombre} - Área: {self.especialidad} (Nivel: {self.nivel})"

# =====================================================================
# 4. CLASE RESERVA Y GESTIÓN DE ESTADOS
# =====================================================================

class Reserva:
    """Gestiona las reservas y sus cambios de estado."""

    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"

    def __init__(self, cliente, servicio, duracion, **parametros_servicio):

        # Validar que se haya recibido un objeto Cliente válido.
        if not all(hasattr(cliente, atributo)
                   for atributo in ("cedula", "nombre")):
            raise ClienteInvalidoError(
                "La reserva requiere un cliente válido."
            )

        # Comprobar que el objeto recibido sea un servicio compatible.
        if not all(hasattr(servicio, metodo)
                   for metodo in ("validar_parametros", "calcular_costo")):
            raise ServicioNoDisponibleError(
                "El servicio recibido no es válido."
            )

        # Validar duración.
        try:
            if isinstance(duracion, bool) or float(duracion) <= 0:
                raise ValueError("La duración debe ser mayor que cero.")

            self.__duracion = float(duracion)

        except (ValueError, TypeError) as error:
            raise ReservaFallidaError(
                "La duración de la reserva no es válida."
            ) from error

        self.__cliente = cliente
        self.__servicio = servicio
        self.__estado = self.PENDIENTE
        self.__costo = None

        # Adaptar la duración al parámetro que espera cada servicio.
        nombre_clase = type(servicio).__name__

        if nombre_clase == "AlquilerEquipo":
            clave_duracion = "dias"
        else:
            clave_duracion = "horas"

        self.__parametros_servicio = parametros_servicio.copy()
        self.__parametros_servicio[clave_duracion] = self.__duracion

        registrar_log(
            "info",
            f"Reserva creada para el cliente {self.__cliente.nombre}. "
            f"Estado: {self.__estado}"
        )

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def estado(self):
        return self.__estado

    @property
    def costo(self):
        return self.__costo

    def confirmar(self):
        """Valida y confirma una reserva pendiente."""

        if self.__estado != self.PENDIENTE:
            raise ReservaFallidaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        try:
            if not self.__servicio.disponible:
                raise ServicioNoDisponibleError(
                    "El servicio no se encuentra disponible."
                )

            self.__servicio.validar_parametros(
                **self.__parametros_servicio
            )

            self.__estado = self.CONFIRMADA

            registrar_log(
                "info",
                f"Reserva confirmada para {self.__cliente.nombre}."
            )

            return True

        except ServicioNoDisponibleError as error:
            registrar_log(
                "error",
                "No fue posible confirmar la reserva.",
                error
            )
            raise

        except Exception as error:
            registrar_log(
                "error",
                "Error al confirmar la reserva.",
                error
            )

            raise ReservaFallidaError(
                "No se pudo confirmar la reserva."
            ) from error

    def cancelar(self):
        """Cancela una reserva pendiente o confirmada."""

        if self.__estado not in (self.PENDIENTE, self.CONFIRMADA):
            raise ReservaFallidaError(
                "La reserva no se puede cancelar en su estado actual."
            )

        self.__estado = self.CANCELADA

        registrar_log(
            "info",
            f"Reserva cancelada para {self.__cliente.nombre}."
        )

        return True

    def procesar(self):
        """Calcula el costo y finaliza una reserva confirmada."""

        if self.__estado != self.CONFIRMADA:
            raise ReservaFallidaError(
                "Solo se pueden procesar reservas confirmadas."
            )

        try:
            self.__costo = self.__servicio.calcular_costo(
                **self.__parametros_servicio
            )

            self.__estado = self.PROCESADA

            registrar_log(
                "info",
                f"Reserva procesada para {self.__cliente.nombre}. "
                f"Costo total: ${self.__costo}"
            )

            return self.__costo

        except ServicioNoDisponibleError as error:
            registrar_log(
                "error",
                "El servicio no pudo procesar la reserva.",
                error
            )
            raise

        except Exception as error:
            registrar_log(
                "error",
                "Error durante el procesamiento de la reserva.",
                error
            )

            raise ReservaFallidaError(
                "No fue posible procesar la reserva."
            ) from error

    def obtener_detalles(self):
        """Devuelve la información de la reserva."""

        return (
            f"Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | "
            f"Duración: {self.__duracion} | "
            f"Estado: {self.__estado} | "
            f"Costo: {self.__costo}"
        )

    def __str__(self):
        return self.obtener_detalles()

# =====================================================================
# 5. CONTROLADOR Y SIMULACIÓN DE OPERACIONES
# =====================================================================

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
    )

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