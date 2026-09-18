
import tkinter as tk
from PIL import Image, ImageTk
import vlc
import os
import sys
import random
import keyboard
import threading
import time

# =========================================================
# CONFIGURACIÓN
# =========================================================

IMAGE_FILE = "imagen.jpg"
AUDIO_FILE = "audio.mp3"

ANCHO = 450
ALTO = 300

# Tiempo entre nuevas ventanas
INTERVALO_VENTANA = 300

# Volumen que tendrá Windows mientras el programa esté activo
VOLUMEN = 0.50

activo = True
ventanas = []

# =========================================================
# RUTAS PARA PYTHON Y PARA EL EXE
# =========================================================

def ruta_archivo(nombre):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base, nombre)


# =========================================================
# CONTROL DE VOLUMEN
# =========================================================

def configurar_volumen():
    try:
        from pycaw.pycaw import AudioUtilities

        dispositivos = AudioUtilities.GetSpeakers()
        volumen = dispositivos.EndpointVolume

        # Desmutear
        volumen.SetMute(0, None)

        # Poner volumen al 50%
        volumen.SetMasterVolumeLevelScalar(VOLUMEN, None)

        print("Volumen establecido al 50%")

    except Exception as e:
        print("No se pudo controlar el volumen:", e)


def vigilar_volumen():
    """
    Mientras el programa esté activo:
    - Mantiene el volumen en 50%.
    - Si alguien mutea la PC, la vuelve a desmutear.
    """

    try:
        from pycaw.pycaw import AudioUtilities

        dispositivos = AudioUtilities.GetSpeakers()
        volumen = dispositivos.EndpointVolume

        while activo:

            # Si está muteado, quitar mute
            if volumen.GetMute():
                volumen.SetMute(0, None)

            # Mantener volumen en 50%
            volumen.SetMasterVolumeLevelScalar(VOLUMEN, None)

            time.sleep(0.2)

    except Exception as e:
        print("Error vigilando volumen:", e)


# =========================================================
# CERRAR TODO
# =========================================================

def detener_todo():
    global activo

    if not activo:
        return

    print("C + M DETECTADO")
    print("Deteniendo programa...")

    activo = False

    # Detener audio
    try:
        player.stop()
    except:
        pass

    # Cerrar todas las ventanas
    for ventana in ventanas[:]:
        try:
            ventana.destroy()
        except:
            pass

    ventanas.clear()

    # Quitar hotkey
    try:
        keyboard.remove_hotkey("c+m")
    except:
        pass

    print("Programa detenido.")


# =========================================================
# CREAR VENTANA
# =========================================================

def crear_ventana():

    if not activo:
        return

    try:
        ventana = tk.Toplevel(root)

        ventana.overrideredirect(True)
        ventana.attributes("-topmost", True)

        # -------------------------------------------------
        # TAMAÑO DE LA PANTALLA
        # -------------------------------------------------

        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()

        # -------------------------------------------------
        # POSICIÓN ALEATORIA
        # -------------------------------------------------

        x = random.randint(
            0,
            max(0, pantalla_ancho - ANCHO)
        )

        y = random.randint(
            0,
            max(0, pantalla_alto - ALTO)
        )

        ventana.geometry(
            f"{ANCHO}x{ALTO}+{x}+{y}"
        )

        # -------------------------------------------------
        # IMAGEN
        # -------------------------------------------------

        ruta_imagen = ruta_archivo(IMAGE_FILE)

        imagen = Image.open(ruta_imagen)
        imagen = imagen.resize(
            (ANCHO, ALTO)
        )

        foto = ImageTk.PhotoImage(imagen)

        etiqueta = tk.Label(
            ventana,
            image=foto,
            borderwidth=0
        )

        etiqueta.image = foto
        etiqueta.pack(
            fill="both",
            expand=True
        )

        # Guardar referencia
        ventanas.append(ventana)

        # -------------------------------------------------
        # SI LA VENTANA SE CIERRA MANUALMENTE
        # -------------------------------------------------

        def cerrar():
            try:
                if ventana in ventanas:
                    ventanas.remove(ventana)

                ventana.destroy()

            except:
                pass

        ventana.protocol(
            "WM_DELETE_WINDOW",
            cerrar
        )

    except Exception as e:
        print("Error creando ventana:", e)


# =========================================================
# CREAR VENTANAS CONTINUAMENTE
# =========================================================

def generar_ventanas():

    if not activo:
        return

    crear_ventana()

    root.after(
        INTERVALO_VENTANA,
        generar_ventanas
    )


# =========================================================
# AUDIO
# =========================================================

ruta_audio = ruta_archivo(AUDIO_FILE)

instancia_vlc = vlc.Instance()

player = instancia_vlc.media_player_new()

media = instancia_vlc.media_new(
    ruta_audio
)

player.set_media(media)


def iniciar_audio():

    try:
        player.play()

        # Esperar a que VLC inicialice
        time.sleep(1)

        # Repetir indefinidamente
        while activo:

            estado = player.get_state()

            if estado == vlc.State.Ended:
                player.stop()
                player.play()

            time.sleep(0.5)

    except Exception as e:
        print("Error con el audio:", e)


# =========================================================
# VENTANA PRINCIPAL
# =========================================================

root = tk.Tk()

root.withdraw()

# =========================================================
# CONFIGURAR VOLUMEN
# =========================================================

configurar_volumen()

# =========================================================
# VIGILAR VOLUMEN EN SEGUNDO PLANO
# =========================================================

hilo_volumen = threading.Thread(
    target=vigilar_volumen,
    daemon=True
)

hilo_volumen.start()

# =========================================================
# HOTKEY GLOBAL
# =========================================================

keyboard.add_hotkey(
    "c+m",
    detener_todo
)

# =========================================================
# INICIAR AUDIO
# =========================================================

hilo_audio = threading.Thread(
    target=iniciar_audio,
    daemon=True
)

hilo_audio.start()

# =========================================================
# EMPEZAR A GENERAR VENTANAS
# =========================================================

root.after(
    100,
    generar_ventanas
)

# =========================================================
# EJECUTAR
# =========================================================

try:
    root.mainloop()

finally:

    activo = False

    try:
        player.stop()
    except:
        pass

    try:
        keyboard.remove_hotkey("c+m")
    except:
        pass

