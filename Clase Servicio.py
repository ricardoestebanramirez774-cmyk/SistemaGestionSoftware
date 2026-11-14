from abc import ABC, abstractmethod
from Excepciones import ServicioNoDisponibleError, registrar_log
from Clientes import EntidadBase

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