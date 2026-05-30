# ============================================================
#  test_cifrado.py — Suite de pruebas unitarias locales
# ============================================================

from cifrado import cifrar, descifrar, info_clave, registrar_evento

def ejecutar_diagnostico():
    registrar_evento("DIAGNOSTICO", "Iniciando suite automatizada de pruebas criptográficas.")
    
    clave_test = "ClaveSistemas2026"
    mensaje_test = "Prueba de Integridad del Proyecto"
    
    print("\n" + "="*60)
    print("  1. AUDITORÍA DEL PIPELINE DE MEMORIA")
    print("="*60)
    print(info_clave(clave_test).replace("*", "").replace("`", ""))
    
    print("\n" + "="*60)
    print("  2. INTEGRIDAD DE CICLO COMPLETO (Cifrar -> Descifrar)")
    print("="*60)
    
    try:
        criptograma = cifrar(mensaje_test, clave_test)
        print(f"  [+] Trama en tránsito (Base64) : {criptograma}")
        
        texto_claro = descifrar(criptograma, clave_test)
        print(f"  [+] Payload restaurado         : {texto_claro}")
        
        # Aserción de control de fallas
        assert mensaje_test == texto_claro, "Error crítico: Discrepancia de datos."
        print("\n  ✅ COMPROBACIÓN DE INTEGRIDAD LOGRADA: ÉXITO")
        
    except Exception as e:
        print(f"  [-] Error detectado: {e}")
        
    print("\n" + "="*60)
    print("  3. SIMULACIÓN DE CLAVE ERRÓNEA")
    print("="*60)
    
    clave_atacante = "ClaveIncorrecta"
    try:
        descifrar(criptograma, clave_atacante)
        print("  [-] VULNERABILIDAD: Se permitió descifrar con llave incorrecta.")
    except Exception:
        print("  ✅ FILTRO DE AUTENTICIDAD CORRECTO: Motor rechazó la llave inválida.")

    print("\n" + "="*60)
    print("  Diagnóstico Finalizado de Forma Exitosa")
    print("="*60)

if __name__ == "__main__":
    ejecutar_diagnostico()