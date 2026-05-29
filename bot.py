# ============================================================
#  bot.py — Bot de Telegram con cifrado AES-256 personalizado
#  Ejecutar: python bot.py
# ============================================================

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)
from cifrado import cifrar, descifrar, info_clave

# ── CONFIGURACIÓN ────────────────────────────────────────────
TOKEN = "8905517262:AAHwpEDcnzsh2jmLcA1Q7WUdH8HlvYP841Y"   

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Estados de la conversación
MENU, ESPERAR_CLAVE, ESPERAR_MENSAJE, ESPERAR_CLAVE_DESC, ESPERAR_CIFRADO = range(5)


# ── /start ───────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [["🔒 Cifrar mensaje", "🔓 Descifrar mensaje"], ["🔍 Ver transformación de clave"]]
    reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)
    await update.message.reply_text(
        "👋 *Bienvenido al Bot de Cifrado AES-256*\n\n"
        "Este bot usa un algoritmo personalizado que transforma tu clave\n"
        "mediante: *ASCII → Padding → Transposición → Salt → AES-256*\n\n"
        "¿Qué quieres hacer?",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return MENU


# ── MENÚ PRINCIPAL ───────────────────────────────────────────
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text

    if texto == "🔒 Cifrar mensaje":
        await update.message.reply_text(
            "🔑 *Paso 1/2 — Cifrado*\n\nEscribe tu *clave secreta* (cualquier texto):",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['modo'] = 'cifrar'
        return ESPERAR_CLAVE

    elif texto == "🔓 Descifrar mensaje":
        await update.message.reply_text(
            "🔑 *Paso 1/2 — Descifrado*\n\nEscribe la *clave secreta* que usaste para cifrar:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['modo'] = 'descifrar'
        return ESPERAR_CLAVE_DESC

    elif texto == "🔍 Ver transformación de clave":
        await update.message.reply_text(
            "🔑 Escribe una clave para ver cómo se transforma internamente:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['modo'] = 'info'
        return ESPERAR_CLAVE

    else:
        await update.message.reply_text("Usa los botones del menú. Escribe /start para volver.")
        return MENU


# ── RECIBIR CLAVE (para cifrar o ver info) ───────────────────
async def recibir_clave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clave = update.message.text
    context.user_data['clave'] = clave

    if context.user_data['modo'] == 'info':
        # Mostrar transformación y volver al menú
        info = info_clave(clave)
        teclado = [["🔒 Cifrar mensaje", "🔓 Descifrar mensaje"], ["🔍 Ver transformación de clave"]]
        reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)
        await update.message.reply_text(info, parse_mode="Markdown", reply_markup=reply_markup)
        return MENU

    # Si el modo es cifrar, pedir el mensaje
    await update.message.reply_text(
        f"✅ Clave recibida: `{clave}`\n\n"
        "📝 *Paso 2/2 — Cifrado*\n\nAhora escribe el *mensaje* que quieres cifrar:",
        parse_mode="Markdown"
    )
    return ESPERAR_MENSAJE


# ── RECIBIR MENSAJE Y CIFRAR ─────────────────────────────────
async def recibir_mensaje_y_cifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje  = update.message.text
    clave    = context.user_data.get('clave', '')

    try:
        cifrado  = cifrar(mensaje, clave)
        teclado  = [["🔒 Cifrar mensaje", "🔓 Descifrar mensaje"], ["🔍 Ver transformación de clave"]]
        reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)

        await update.message.reply_text(
            "✅ *Mensaje cifrado exitosamente*\n\n"
            f"📨 *Texto original:*\n`{mensaje}`\n\n"
            f"🔒 *Texto cifrado (AES-256 + Base64):*\n`{cifrado}`\n\n"
            "💡 _Comparte el texto cifrado. Solo quien tenga la clave puede leerlo._",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error al cifrar: {e}")

    return MENU


# ── RECIBIR CLAVE PARA DESCIFRAR ─────────────────────────────
async def recibir_clave_descifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['clave'] = update.message.text
    await update.message.reply_text(
        "📋 *Paso 2/2 — Descifrado*\n\nPega el *texto cifrado* que quieres descifrar:",
        parse_mode="Markdown"
    )
    return ESPERAR_CIFRADO


# ── RECIBIR TEXTO CIFRADO Y DESCIFRAR ────────────────────────
async def recibir_cifrado_y_descifrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_cifrado = update.message.text
    clave         = context.user_data.get('clave', '')

    try:
        descifrado = descifrar(texto_cifrado, clave)
        teclado    = [["🔒 Cifrar mensaje", "🔓 Descifrar mensaje"], ["🔍 Ver transformación de clave"]]
        reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)

        await update.message.reply_text(
            "✅ *Mensaje descifrado exitosamente*\n\n"
            f"🔒 *Texto cifrado recibido:*\n`{texto_cifrado[:60]}...`\n\n"
            f"📨 *Mensaje original:*\n`{descifrado}`",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(
            "❌ *No se pudo descifrar.*\n"
            "Verifica que la clave sea exactamente la misma que usaste para cifrar.",
            parse_mode="Markdown"
        )

    return MENU


# ── CANCELAR ─────────────────────────────────────────────────
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operación cancelada. Escribe /start para volver.")
    return ConversationHandler.END


# ── MAIN ─────────────────────────────────────────────────────
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

    print("🤖 Bot corriendo... Presiona Ctrl+C para detener.")
    app.run_polling()


if __name__ == "__main__":
    main()
