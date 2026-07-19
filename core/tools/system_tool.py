from abc import ABC, abstractmethod
from enum import Enum


class NivelRiesgo(Enum):
    BAJO = "bajo"    # reversible, no destructivo — se ejecuta directo
    ALTO = "alto"     # requiere confirmación explícita del usuario


class SystemTool(ABC):
    """Contrato para cualquier herramienta que interactúe con el sistema operativo."""

    nombre: str
    descripcion: str
    nivel_riesgo: NivelRiesgo

    @abstractmethod
    def ejecutar(self, **kwargs) -> str:
        """Ejecuta la acción y devuelve un mensaje de resultado."""
        raise NotImplementedError