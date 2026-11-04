# FSOCIETY Framework

Herramientas modulares de ciberseguridad defensiva, monitoreo local y análisis forense. La interfaz usa Typer y Rich; los análisis de archivos, contraseñas y unidades son locales. El diseño gráfico es original y no utiliza logotipos ni recursos de la serie Mr. Robot.

## Requisitos

- Python 3.11 o superior (desarrollado y verificado con Python 3.12 en Windows).
- Windows 10/11, Kali Linux o Arch Linux.
- Dependencias: Rich, Typer y psutil. Pytest se instala con el extra `dev`.

## Instalación

Desde la raíz del repositorio:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Kali / Arch Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
```

En Windows puede ser necesario permitir la activación local del entorno virtual según la política de PowerShell del equipo. No requiere permisos de administrador.

## Uso

```text
fsociety                 Menú interactivo
fsociety --version       Versión
fsociety info            Sistema, CPU, RAM y discos
fsociety processes       Procesos visibles
fsociety connections     Conexiones locales visibles
fsociety network scan 192.168.1.0/24
fsociety forensic ./evidence.bin
fsociety usb
fsociety usb --path E:\\
fsociety password audit
fsociety integrity baseline ./carpeta
fsociety integrity check ./carpeta data/reports/integrity_baseline.json
fsociety awareness
```

La mayoría de comandos guardan informes JSON en `data/reports/`. Los logs están en `data/logs/`. `forensic` acepta un archivo o directorio; no altera la evidencia. USB permite inventario estático y hashes, sin ejecutar archivos. Los comandos de procesos y conexiones muestran solo los datos permitidos al usuario actual por el sistema operativo.

### Inventario de red autorizado

1. Edita `config/scope.txt` y registra cada red IPv4 privada autorizada, una por línea, por ejemplo `192.168.1.0/24`.
2. Ejecuta el comando y confirma en el prompt o usa `--yes` explícitamente:

```bash
fsociety network scan 192.168.1.0/24
fsociety network scan 192.168.1.0/24 --ports 22,80,443 --yes
```

Se rechazan redes fuera de RFC 1918, redes que no estén contenidas en el alcance registrado y prefijos más amplios que `/24`. El módulo solo intenta conexiones TCP a los puertos solicitados; no explota servicios ni realiza fuerza bruta. Los resultados de puertos cerrados/filtrados no distinguen entre ambos estados.

### Auditoría de contraseña

`fsociety password audit` solicita el texto con entrada oculta. La función trabaja en memoria, no registra ni guarda el valor y devuelve solo longitud, clases, patrones, estimación orientativa y recomendaciones. No pegues secretos de producción en terminales compartidas; se recomienda auditar ejemplos o frases candidatas localmente.

### Integridad

La línea base guarda hashes SHA-256 bajo rutas relativas a la raíz para detectar cambios, altas y eliminaciones independientemente de la ruta absoluta de la carpeta. Guarda la línea base en un lugar separado de los archivos observados:

```bash
fsociety integrity baseline ./carpeta --output ./baseline.json
fsociety integrity check ./carpeta ./baseline.json
```

## Arquitectura

- `core`: configuración, logs, validación del alcance, detección de plataforma y registro de módulos.
- `modules`: red, sistema, análisis forense, USB, auditoría de contraseñas, integridad y formación.
- `platform_adapters`: inventario común con psutil y detección USB específica de Windows/Linux.
- `utils`: validadores, salida Rich y escritura de reportes JSON.
- `config`: configuración predeterminada y alcance de red.
- `data`: logs, reportes y espacio para evidencias.

El adaptador Linux consulta `lsblk` con `subprocess.run` usando una lista de argumentos, sin shell. Las operaciones de archivos son de lectura; no siguen enlaces simbólicos al inventariar. La disponibilidad de modelo USB y ciertos campos depende de los permisos y datos que exponga cada sistema.

## Pruebas

```bash
python -m pytest -q
```

Las pruebas usan archivos temporales y no acceden a redes externas. La comprobación de inventario de procesos solo consulta el proceso local.

## Limitaciones y seguridad

- Uso previsto: aprendizaje, investigación y auditorías autorizadas.
- No hay explotación, fuerza bruta, propagación, recolección de credenciales ni envío de mensajes.
- Los datos de CPU, procesos, conexiones, USB y metadatos varían entre sistemas y por permisos.
- El escaneo acepta únicamente redes RFC 1918 registradas en el alcance; verifica siempre que cada CIDR configurado corresponda a activos bajo tu autorización.
- Las reglas de phishing y extensiones sospechosas son indicadores estáticos, no un veredicto antimalware.
- La estimación de entropía de contraseñas es aproximada y no reemplaza un gestor ni políticas de autenticación.
- Las líneas base no están firmadas. Protégelas contra cambios no autorizados y conserva copias separadas.

## Solución de errores

- `fsociety` no se reconoce: activa el entorno virtual o ejecuta `python -m pip install -e .`.
- El escaneo rechaza una red: valida que sea privada, `/24` o más pequeña y esté registrada en `config/scope.txt`.
- Un inventario aparece vacío: el sistema puede ocultar datos por permisos, el dispositivo puede no estar montado o `lsblk` puede no estar disponible.
- Error al escribir reportes: confirma que el usuario actual tenga permiso de escritura en `data/`.

## Licencia

MIT. Consulta [LICENSE](LICENSE).
