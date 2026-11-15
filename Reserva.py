
from Excepciones import (
    ClienteInvalidoError,
    ServicioNoDisponibleError,
    ReservaFallidaError,
    registrar_log
)


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
