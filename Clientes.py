from abc import ABC, abstractmethod
from Excepciones import ClienteInvalidoError, registrar_log

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