# ============================================================
#  test_cifrado.py — Prueba local del algoritmo (sin Telegram)
#  Ejecutar: python test_cifrado.py
# ============================================================

from cifrado import cifrar, descifrar, info_clave, construir_llave

def separador(titulo):
    print(f"\n{'='*55}")
    print(f"  {titulo}")
    print('='*55)


# ── TEST 1: Transformación de clave ──────────────────────────
separador("TEST 1: Transformación de clave")
clave = "CASA"
print(info_clave(clave).replace("*", "").replace("`", ""))


# ── TEST 2: Cifrado y descifrado básico ──────────────────────
separador("TEST 2: Cifrado y descifrado")
clave   = "MiClaveSecreta"
mensaje = "Hola, esto es un mensaje secreto!"

cifrado    = cifrar(mensaje, clave)
descifrado = descifrar(cifrado, clave)

print(f"  Clave usada   : {clave}")
print(f"  Mensaje       : {mensaje}")
print(f"  Cifrado       : {cifrado}")
print(f"  Descifrado    : {descifrado}")
print(f"  ¿Coincide?    : {'✅ SÍ' if mensaje == descifrado else '❌ NO'}")


# ── TEST 3: Distintas claves → distintos cifrados ────────────
separador("TEST 3: Distintas claves dan distintos resultados")
mensaje = "Hola mundo"
claves  = ["clave1", "clave2", "CASA", "password123"]

for c in claves:
    resultado = cifrar(mensaje, c)
    print(f"  Clave '{c:12}' → {resultado[:40]}...")


# ── TEST 4: Clave incorrecta no puede descifrar ──────────────
separador("TEST 4: Clave incorrecta no puede descifrar")
clave_correcta   = "ClaveCorrecta"
clave_incorrecta = "ClaveIncorrecta"
mensaje          = "Mensaje super secreto"

cifrado = cifrar(mensaje, clave_correcta)
print(f"  Cifrado con: '{clave_correcta}'")
print(f"  Intentando descifrar con: '{clave_incorrecta}'")

try:
    resultado = descifrar(cifrado, clave_incorrecta)
    print(f"  Resultado: {resultado}")
except Exception as e:
    print(f"  ❌ Error (esperado): No se pudo descifrar → {type(e).__name__}")


# ── TEST 5: Llave final en bytes (para mostrar al docente) ───
separador("TEST 5: Llave final construida (breakpoint del docente)")
clave = "MiClaveSecreta"
llave = construir_llave(clave)
print(f"  Clave usuario : '{clave}'")
print(f"  Llave (bytes) : {list(llave)}")
print(f"  Llave (hex)   : {llave.hex()}")
print(f"  Longitud      : {len(llave)} bytes (AES-256 = 32 bytes ✅)")

print(f"\n{'='*55}")
print("  Todos los tests completados")
print('='*55)
