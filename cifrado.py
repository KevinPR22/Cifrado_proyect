# ============================================================
#  cifrado.py — Motor de cifrado personalizado
#  Algoritmo compuesto: ASCII → Padding → Transposición → AES-256
# ============================================================

import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


# ── 1. CONVERSIÓN A ASCII ────────────────────────────────────
def clave_a_ascii(clave: str) -> list[int]:
    """
    Convierte cada carácter de la clave a su valor ASCII.
    Ejemplo: 'CASA' → [67, 65, 83, 65]
    """
    return [ord(c) for c in clave]


# ── 2. PADDING ───────────────────────────────────────────────
def aplicar_padding(valores_ascii: list[int], longitud: int = 32) -> list[int]:
    """
    Repite los valores ASCII hasta alcanzar exactamente `longitud` elementos.
    AES-256 necesita una clave de 32 bytes.
    Ejemplo: [67, 65, 83, 65] → se repite hasta tener 32 valores.
    """
    resultado = []
    i = 0
    while len(resultado) < longitud:
        resultado.append(valores_ascii[i % len(valores_ascii)])
        i += 1
    return resultado[:longitud]


# ── 3. TRANSPOSICIÓN ─────────────────────────────────────────
def transponer(valores: list[int]) -> list[int]:
    """
    Aplica una transposición: divide la lista en dos mitades
    y las intercala (par/impar).
    Ejemplo: [A, B, C, D, E, F] → [A, D, B, E, C, F]
    Esto le da 'personalidad' a la clave antes de cifrar.
    """
    mitad = len(valores) // 2
    primera = valores[:mitad]
    segunda = valores[mitad:]
    transpuesta = []
    for i in range(mitad):
        transpuesta.append(primera[i])
        if i < len(segunda):
            transpuesta.append(segunda[i])
    return transpuesta


# ── 4. SALTING ───────────────────────────────────────────────
def aplicar_salt(valores: list[int], salt: int = 7) -> list[int]:
    """
    XOR de cada byte con un valor fijo (salt).
    Hace que claves similares generen resultados muy distintos.
    Ejemplo: 67 XOR 7 = 68
    """
    return [(v ^ salt) for v in valores]


# ── 5. CONSTRUCCIÓN DE LA LLAVE FINAL ───────────────────────
def construir_llave(clave_usuario: str) -> bytes:
    """
    Pipeline completo de transformación de clave:
    Texto → ASCII → Padding(32) → Transposición → Salt → bytes
    """
    ascii_vals  = clave_a_ascii(clave_usuario)        # paso 1
    padded      = aplicar_padding(ascii_vals, 32)     # paso 2
    transpuesta = transponer(padded)                  # paso 3
    salted      = aplicar_salt(transpuesta, salt=7)   # paso 4
    llave_bytes = bytes(salted)                       # 32 bytes exactos → AES-256
    return llave_bytes


# ── 6. CIFRADO AES-256 ───────────────────────────────────────
def cifrar(mensaje: str, clave_usuario: str) -> str:
    """
    Cifra un mensaje de texto plano con AES-256 en modo CBC.
    Devuelve el resultado en Base64 para que viaje limpio por Telegram.

    Flujo:
      mensaje (texto) → bytes → AES-256 CBC → Base64 (texto seguro)
    """
    llave  = construir_llave(clave_usuario)           # clave procesada
    cipher = AES.new(llave, AES.MODE_CBC)             # IV aleatorio automático
    ct     = cipher.encrypt(pad(mensaje.encode('utf-8'), AES.block_size))

    # Guardamos IV + ciphertext juntos en Base64
    resultado = base64.b64encode(cipher.iv + ct).decode('utf-8')
    return resultado


# ── 7. DESCIFRADO AES-256 ────────────────────────────────────
def descifrar(mensaje_cifrado: str, clave_usuario: str) -> str:
    """
    Descifra un mensaje cifrado con la misma clave.
    Extrae primero el IV (primeros 16 bytes) y luego el ciphertext.

    Flujo:
      Base64 → bytes → separa IV/CT → AES-256 CBC decrypt → texto plano
    """
    llave      = construir_llave(clave_usuario)
    raw        = base64.b64decode(mensaje_cifrado)
    iv         = raw[:16]                             # los primeros 16 bytes son el IV
    ct         = raw[16:]                             # el resto es el mensaje cifrado
    cipher     = AES.new(llave, AES.MODE_CBC, iv=iv)
    texto      = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
    return texto


# ── 8. RESUMEN VISUAL DE LA CLAVE ────────────────────────────
def info_clave(clave_usuario: str) -> str:
    """
    Muestra paso a paso cómo se transforma la clave.
    Útil para mostrar en Telegram y para explicar al docente.
    """
    ascii_vals  = clave_a_ascii(clave_usuario)
    padded      = aplicar_padding(ascii_vals, 32)
    transpuesta = transponer(padded)
    salted      = aplicar_salt(transpuesta, salt=7)

    lineas = [
        "🔐 *Transformación de tu clave:*",
        f"• Texto original: `{clave_usuario}`",
        f"• Paso 1 – ASCII:        `{ascii_vals}`",
        f"• Paso 2 – Padding(32): `{padded}`",
        f"• Paso 3 – Transposición: `{transpuesta}`",
        f"• Paso 4 – Salt(XOR 7):  `{salted}`",
        f"• Llave final (hex):     `{bytes(salted).hex()}`",
    ]
    return "\n".join(lineas)
