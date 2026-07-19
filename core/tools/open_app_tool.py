import os
import subprocess
import difflib

from core.tools.system_tool import SystemTool, NivelRiesgo


class OpenAppTool(SystemTool):
    nombre = "abrir_programa"
    descripcion = "Abre una aplicación instalada en el sistema, dado su nombre."
    nivel_riesgo = NivelRiesgo.BAJO

    APPS_CONOCIDAS = {
        "bloc de notas": "notepad.exe",
        "notepad": "notepad.exe",
        "calculadora": "calc.exe",
        "calculator": "calc.exe",
        "explorador de archivos": "explorer.exe",
        "explorador": "explorer.exe",
        "vscode": "code",
        "visual studio code": "code",
    }

    PERFIL_CHROME_DEFAULT = "profile 4"

    CARPETAS_BUSQUEDA = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.join(os.path.expanduser("~"), "Desktop"),
        r"C:\Users\Public\Desktop",
    ]

    def ejecutar(self, nombre_app: str, **kwargs) -> str:
        nombre_normalizado = nombre_app.lower().strip()

        if nombre_normalizado in ("chrome", "navegador", "google chrome"):
            comando = f'start chrome --profile-directory="{self.PERFIL_CHROME_DEFAULT}"'
            return self._ejecutar_comando(comando, nombre_app)

        if nombre_normalizado in self.APPS_CONOCIDAS:
            return self._ejecutar_comando(self.APPS_CONOCIDAS[nombre_normalizado], nombre_app)

        acceso, nombre_encontrado = self._buscar_acceso_directo(nombre_normalizado)
        if acceso:
            try:
                os.startfile(acceso)
                return f"Se abrió '{nombre_encontrado}' (coincidencia para '{nombre_app}')."
            except Exception as e:
                return f"No se pudo abrir '{nombre_app}': {e}"

        return self._ejecutar_comando(nombre_app, nombre_app)

    def _buscar_acceso_directo(self, nombre_buscado: str) -> tuple[str | None, str | None]:
        candidatos = {}
        for carpeta in self.CARPETAS_BUSQUEDA:
            if not os.path.isdir(carpeta):
                continue
            for raiz, _, archivos in os.walk(carpeta):
                for archivo in archivos:
                    if archivo.lower().endswith(".lnk"):
                        nombre_sin_ext = archivo[:-4].lower()
                        candidatos[nombre_sin_ext] = os.path.join(raiz, archivo)

        # 1. Coincidencia exacta
        if nombre_buscado in candidatos:
            return candidatos[nombre_buscado], nombre_buscado

        # 2. El nombre buscado está contenido en el nombre real (ej: "zoom" en "zoom workplace")
        contenidos = [n for n in candidatos if nombre_buscado in n]
        if contenidos:
            mejor = min(contenidos, key=len)  # el más corto = coincidencia más directa
            return candidatos[mejor], mejor

        # 3. Última opción: parecido difuso, con umbral más estricto que antes
        coincidencias = difflib.get_close_matches(nombre_buscado, candidatos.keys(), n=1, cutoff=0.7)
        if coincidencias:
            return candidatos[coincidencias[0]], coincidencias[0]

        return None, None

    @staticmethod
    def _ejecutar_comando(comando: str, nombre_original: str) -> str:
        try:
            subprocess.Popen(comando, shell=True)
            return f"Se abrió '{nombre_original}' correctamente."
        except Exception as e:
            return f"No se pudo abrir '{nombre_original}': {e}"