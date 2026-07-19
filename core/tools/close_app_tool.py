import psutil
import difflib

from core.tools.system_tool import SystemTool, NivelRiesgo


class CloseAppTool(SystemTool):
    nombre = "cerrar_programa"
    descripcion = "Cierra un programa en ejecución. Requiere confirmación del usuario antes de actuar."
    nivel_riesgo = NivelRiesgo.ALTO

    def ejecutar(self, nombre_app: str, confirmado: bool = False, **kwargs) -> str:
            procesos = self._buscar_procesos(nombre_app.lower().strip())

            if not procesos:
                return f"No encontré ningún programa en ejecución parecido a '{nombre_app}'."

            if not confirmado:
                nombre_real = procesos[0].name()
                cantidad = f" ({len(procesos)} procesos)" if len(procesos) > 1 else ""
                return (
                    f"CONFIRMACION_REQUERIDA: Encontré '{nombre_real}'{cantidad} en ejecución. "
                    f"Pregúntale al usuario si de verdad quiere cerrarlo antes de proceder — "
                    f"no lo cierres todavía."
                )

            cerrados = 0
            for proceso in procesos:
                try:
                    proceso.terminate()
                    cerrados += 1
                except Exception:
                    continue

            return f"Se cerraron {cerrados} de {len(procesos)} proceso(s) de '{nombre_app}'."
    
    @staticmethod
    def _buscar_procesos(nombre_buscado: str) -> list:
        nombres_procesos: dict[str, list] = {}
        for proc in psutil.process_iter(["name"]):
            try:
                nombre_real = proc.info["name"]
                if nombre_real:
                    nombres_procesos.setdefault(nombre_real.lower(), []).append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if nombre_buscado in nombres_procesos:
            return nombres_procesos[nombre_buscado]

        contenidos = [n for n in nombres_procesos if nombre_buscado in n]
        if contenidos:
            mejor = min(contenidos, key=len)
            return nombres_procesos[mejor]

        coincidencias = difflib.get_close_matches(nombre_buscado, nombres_procesos.keys(), n=1, cutoff=0.7)
        return nombres_procesos[coincidencias[0]] if coincidencias else []