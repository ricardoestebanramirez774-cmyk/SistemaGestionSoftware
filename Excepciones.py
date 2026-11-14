import logging

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