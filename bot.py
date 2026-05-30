# ============================================================
#  bot.py — Interfaz de Usuario y Servidor de Mensajería vía Telegram
# ============================================================

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
from cifrado import cifrar, descifrar, info_clave, registrar_evento

# ── CONFIGURACIÓN ────────────────────────────────────────────
TOKEN = "8905517262:AAHwpEDcnzsh2jmLcA1Q7WUdH8HlvYP841Y"  

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

MENU, ESPERAR_CLAVE, ESPERAR_MENSAJE, ESPERAR_CLAVE_DESC, ESPERAR_CIFRADO = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = update.message.from_user.username or update.message.from_user.first_name
    registrar_evento("CONEXION_CLIENTE", f"Usuario '{usuario}' inicializó sesión.")
    
    teclado = [["🔒 Cifrar mensaje", "🔓 Descifrar mensaje"], ["🔍 Ver transformación de clave"]]
    reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)
    await update.message.reply_text(
        "👋 *Plataforma de Cifrado Híbrido Personalizado*\n\n"
        "Arquitectura del pipeline de seguridad:\n"
        "`ASCII → Padding → Shuffle de Bloques → XOR Dinámico → AES-256 CBC`\n\n"
        "Seleccione una operación:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text

    if texto == "🔒 Cifrar mensaje":
        await update.message.reply_text(
            "🔑 *Fase 1: Configuración*\n\nEscriba la *clave secreta* para la derivación:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['modo'] = 'cifrar'
        return ESPERAR_CLAVE

    elif texto == "🔓 Descifrar mensaje":
        await update.message.reply_text(
            "🔑 *Fase 1: Autenticación*\n\nEscriba la *clave secreta* original:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['modo'] = 'descifrar'
        return ESPERAR_CLAVE_DESC

    elif texto == "🔍 Ver transformación de clave":
        await update.message.reply_text(
            "🔬 *Modo Auditoría*\n\nIngrese una clave para visualizar el pipeline en memoria:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['modo'] = 'info'
        return ESPERAR_CLAVE
    else:
        await update.message.reply_text("Usa los botones del menú. Escribe /start para volver.")
        return MENU

async def recibir_clave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clave = update.message.text
    context.user_data['clave'] = clave

    if context.user_data['modo'] == 'info':
        info = info_clave(clave)
        teclado = [["🔒 Cifrar mensaje", "🔓 Descifrar mensaje"], ["🔍 Ver transformación de clave"]]
        reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)
        await update.message.reply_text(info, parse_mode="Markdown", reply_markup=reply_markup)
        return MENU

    await update.message.reply_text(
        f"✅ Llave cargada en el búfer.\n\n"
        "📝 *Fase 2: Entrada de Payload*\n\nEscriba el *mensaje plano* que desea procesar:",
        parse_mode="Markdown"
    )
    return ESPERAR_MENSAJE

async def recibir_mensaje_y_cifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje  = update.message.text
    clave    = context.user_data.get('clave', '')

    try:
        cifrado  = cifrar(mensaje, clave)
        teclado  = [["🔒 Cifrar mensaje", "🔓 Descifrar mensaje"], ["🔍 Ver transformación de clave"]]
        reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)

        await update.message.reply_text(
            "🔒 *Criptograma Generado Exitosamente*\n\n"
            f"📨 *Mensaje Original:*\n`{mensaje}`\n\n"
            f"📦 *Trama Cifrada Segura (Base64):*\n`{cifrado}`",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        registrar_evento("EXCEPTION_ERROR", f"Fallo en el cifrado: {str(e)}")
        await update.message.reply_text(f"❌ Error en la capa criptográfica: {e}")

    return MENU

async def recibir_clave_descifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['clave'] = update.message.text
    await update.message.reply_text(
        "📋 *Fase 2: Recepción de Criptograma*\n\nPega la trama alfanumérica cifrada en Base64:",
        parse_mode="Markdown"
    )
    return ESPERAR_CIFRADO

async def recibir_cifrado_y_descifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_cifrado = update.message.text
    clave         = context.user_data.get('clave', '')

    try:
        descifrado = descifrar(texto_cifrado, clave)
        teclado    = [["🔒 Cifrar mensaje", "🔓 Descifrar mensaje"], ["🔍 Ver transformación de clave"]]
        reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)

        await update.message.reply_text(
            "🔓 *Mensaje Descifrado e Integridad Verificada*\n\n"
            f"📨 *Payload Recuperado:*\n`{descifrado}`",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        registrar_evento("AUTH_FAILURE", "Intento fallido de descifrado o corrupción de trama.")
        await update.message.reply_text(
            "❌ *Violación de Integridad / Clave Incorrecta.*\n"
            "El descifrado falló. Verifique la llave simétrica y que la trama esté completa.",
            parse_mode="Markdown"
        )
    return MENU

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Conexión abortada. Envíe /start para reanudar.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            ESPERAR_CLAVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_clave)],
            ESPERAR_MENSAJE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_mensaje_y_cifrar)],
            ESPERAR_CLAVE_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_clave_descifrar)],
            ESPERAR_CIFRADO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_cifrado_y_descifrar)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv_handler)
    registrar_evento("SERVER_START", "Escuchando tramas entrantes...")
    app.run_polling()

if __name__ == "__main__":
    main()