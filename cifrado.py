# ============================================================
#  cifrado.py — Motor de cifrado avanzado personalizado
#  Pipeline: ASCII → Padding Cíclico → Shuffle por Bloques → XOR Dinámico → AES-256 CBC
# ============================================================

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datetime import datetime

def registrar_evento(accion: str, detalle: str):
    """Registra logs en la consola del servidor."""
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ahora}] [CORE-CRYPTO] {accion.upper()} -> {detalle}")

def clave_a_ascii(clave: str) -> list[int]:
    """Transforma la clave en valores ASCII."""
    return [ord(c) for c in clave]

def aplicar_padding(valores_ascii: list[int], longitud: int = 32) -> list[int]:
    """Completa el arreglo mediante repetición cíclica hasta alcanzar 32 bytes (AES-256)."""
    resultado = []
    i = 0
    while len(resultado) < longitud:
        resultado.append(valores_ascii[i % len(valores_ascii)])
        i += 1
    return resultado[:longitud]

def transponer(valores: list[int]) -> list[int]:
    """
    Invierte el arreglo completo y realiza un intercambio posicional 
    de los primeros 4 bytes por los últimos 4 bytes. Rompe patrones lineales.
    """
    copia = list(valores)
    copia.reverse()  # Inversión de toda la secuencia
    # Intercambio de bloques (primeros 4 por los últimos 4)
    copia[:4], copia[-4:] = copia[-4:], copia[:4]
    return copia

def aplicar_salt(valores: list[int], clave_usuario: str) -> list[int]:
    """
    El salt se calcula algebraicamente en base a la longitud de la clave del usuario 
    mediante aritmética modular. Evita firmas estáticas para claves similares.
    """
    salt_dinamico = (len(clave_usuario) * 17) % 251
    if salt_dinamico == 0:
        salt_dinamico = 11  # Valor alternativo de seguridad
    return [(v ^ salt_dinamico) for v in valores]

def construir_llave(clave_usuario: str) -> bytes:
    """Coordina secuencialmente la preparación de la llave en memoria."""
    ascii_vals  = clave_a_ascii(clave_usuario)
    padded      = aplicar_padding(ascii_vals, 32)
    transpuesta = transponer(padded)
    salted      = aplicar_salt(transpuesta, clave_usuario)
    return bytes(salted)

def cifrar(mensaje: str, clave_usuario: str) -> str:
    """Cifra en AES-256 CBC y empaqueta IV + Cifrado en Base64."""
    registrar_evento("CIFRADO_INICIO", f"Procesando trama entrante de {len(mensaje)} caracteres.")
    llave  = construir_llave(clave_usuario)
    cipher = AES.new(llave, AES.MODE_CBC)  # Generación automática del IV
    
    ct = cipher.encrypt(pad(mensaje.encode('utf-8'), AES.block_size))
    resultado = base64.b64encode(cipher.iv + ct).decode('utf-8')
    
    registrar_evento("CIFRADO_FIN", "Trama encapsulada en Base64 de forma segura.")
    return resultado

def descifrar(mensaje_cifrado: str, clave_usuario: str) -> str:
    """Aísla el IV de los primeros 16 bytes y descifra el mensaje."""
    registrar_evento("DESCIFRADO_INICIO", "Recuperando flujo de bytes desde el canal de transporte.")
    llave      = construir_llave(clave_usuario)
    raw        = base64.b64decode(mensaje_cifrado)
    
    iv         = raw[:16]  # Segmentación estricta del IV
    ct         = raw[16:]  # Aislamiento del cuerpo cifrado
    
    cipher     = AES.new(llave, AES.MODE_CBC, iv=iv)
    texto      = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
    registrar_evento("DESCIFRADO_FIN", "Texto plano restaurado en memoria correctamente.")
    return texto

def info_clave(clave_usuario: str) -> str:
    """Genera un reporte del estado de las variables para pruebas de escritorio."""
    ascii_vals  = clave_a_ascii(clave_usuario)
    padded      = aplicar_padding(ascii_vals, 32)
    transpuesta = transponer(padded)
    salted      = aplicar_salt(transpuesta, clave_usuario)
    salt_usado  = (len(clave_usuario) * 17) % 251
    if salt_usado == 0: salt_usado = 11

    lineas = [
        "🔐 *Auditoría de Pipeline de Llave Personalizada:*",
        f"• Entrada original: `{clave_usuario}` (Long: {len(clave_usuario)})",
        f"• Paso 1 – Estado ASCII:    `{ascii_vals}`",
        f"• Paso 2 – Padding Cíclico: `{padded}`",
        f"• Paso 3 – Shuffle Bloques: `{transpuesta}`",
        f"• Paso 4 – Salt XOR ({salt_usado}): `{salted}`",
        f"• Llave Final (Hexadecimal): `{bytes(salted).hex()}`",
    ]
    return "\n".join(lineas)