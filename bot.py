import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from datetime import datetime
from threading import Thread
from flask import Flask

# ----- SERVIDOR WEB PARA RENDER -----
app = Flask('')

@app.route('/')
def home():
    return "Bot de Cartas Anónimas en línea 24/7"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ----- CONFIGURACIÓN DEL BOT -----
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
contador_cartas = 0

@bot.event
async def on_ready():
    print(f'✅ Bot encendido y conectado como {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Sincronizados {len(synced)} comandos globalmente.")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}")

# ----- COMANDO: /carta -----
@bot.tree.command(name="carta", description="Envía una carta anónima al buzón del servidor.")
@app_commands.describe(
    para="Menciona al destinatario (@usuario) o escribe su nombre",
    mensaje="Escribe el contenido de tu carta anónima"
)
async def carta(interaction: discord.Interaction, para: str, mensaje: str):
    global contador_cartas
    contador_cartas += 1

    # Buscar canal 'cartas-anonimas' o 'confesiones'
    canal_buzon = discord.utils.get(interaction.guild.text_channels, name="cartas-anonimas")
    if not canal_buzon:
        canal_buzon = discord.utils.get(interaction.guild.text_channels, name="confesiones")
    if not canal_buzon:
        canal_buzon = interaction.channel

    embed = discord.Embed(
        title=f"💌 Carta Anónima #{contador_cartas}",
        description=f"**Para:** {para}\n\n{mensaje}",
        color=discord.Color.from_rgb(255, 182, 193),
        timestamp=datetime.now()
    )
    embed.set_footer(text="Enviado de forma 100% anónima ✨")

    await canal_buzon.send(content=f"📬 ¡Hay una nueva carta para {para}!", embed=embed)
    await interaction.response.send_message("✅ Tu carta anónima ha sido enviada al buzón con éxito.", ephemeral=True)

# Iniciar todo
keep_alive()
bot.run(TOKEN)
