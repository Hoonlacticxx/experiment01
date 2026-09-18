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

# Tiempo entre nuevas ventanas (milisegundos)
INTERVALO_VENTANA = 300

# Volumen de Windows mientras el programa esté activo
# 1.0 = 100%
# 0.5 = 50%
VOLUMEN = 1.0

activo = True
ventanas = []


# =========================================================
# RUTAS PARA PYTHON Y PARA EL EXE
# =========================================================

def ruta_archivo(nombre):

    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(base, nombre)


# =========================================================
# BLOQUEAR CIERRES
# =========================================================

def bloquear_cierre():
    """
    No permite cerrar el programa mediante
    métodos normales de Windows.
    """
    pass


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

        # Establecer volumen
        volumen.SetMasterVolumeLevelScalar(
            VOLUMEN,
            None
        )

        print(
            f"Volumen establecido al {int(VOLUMEN * 100)}%"
        )

    except Exception as e:

        print(
            "No se pudo controlar el volumen:",
            e
        )


def vigilar_volumen():

    """
    Mientras el programa esté activo:

    - Mantiene el volumen configurado.
    - Si alguien mutea la PC, vuelve a quitar el mute.
    """

    try:

        from pycaw.pycaw import AudioUtilities

        dispositivos = AudioUtilities.GetSpeakers()
        volumen = dispositivos.EndpointVolume

        while activo:

            # Quitar mute
            if volumen.GetMute():
                volumen.SetMute(0, None)

            # Mantener volumen
            volumen.SetMasterVolumeLevelScalar(
                VOLUMEN,
                None
            )

            time.sleep(0.2)

    except Exception as e:

        print(
            "Error vigilando volumen:",
            e
        )


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

    # -----------------------------------------------------
    # DETENER AUDIO
    # -----------------------------------------------------

    try:
        player.stop()

    except:
        pass

    # -----------------------------------------------------
    # CERRAR TODAS LAS VENTANAS
    # -----------------------------------------------------

    for ventana in ventanas[:]:

        try:
            ventana.destroy()

        except:
            pass

    ventanas.clear()

    # -----------------------------------------------------
    # QUITAR HOTKEYS
    # -----------------------------------------------------

    try:
        keyboard.remove_hotkey("c+m")

    except:
        pass

    try:
        keyboard.remove_hotkey("alt+f4")

    except:
        pass

    try:
        keyboard.remove_hotkey("esc")

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

        # -------------------------------------------------
        # QUITAR BARRA DE TÍTULO
        # -------------------------------------------------

        ventana.overrideredirect(True)

        # Mantener encima
        ventana.attributes(
            "-topmost",
            True
        )

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
            max(
                0,
                pantalla_ancho - ANCHO
            )
        )

        y = random.randint(
            0,
            max(
                0,
                pantalla_alto - ALTO
            )
        )

        ventana.geometry(
            f"{ANCHO}x{ALTO}+{x}+{y}"
        )

        # -------------------------------------------------
        # IMAGEN
        # -------------------------------------------------

        ruta_imagen = ruta_archivo(
            IMAGE_FILE
        )

        imagen = Image.open(
            ruta_imagen
        )

        imagen = imagen.resize(
            (ANCHO, ALTO)
        )

        foto = ImageTk.PhotoImage(
            imagen
        )

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

        # -------------------------------------------------
        # GUARDAR REFERENCIA
        # -------------------------------------------------

        ventanas.append(
            ventana
        )

        # -------------------------------------------------
        # BLOQUEAR CIERRE
        # -------------------------------------------------

        def cerrar():

            # No hacer nada
            # La ventana solo puede cerrarse
            # mediante C + M
            pass

        ventana.protocol(
            "WM_DELETE_WINDOW",
            cerrar
        )

    except Exception as e:

        print(
            "Error creando ventana:",
            e
        )


# =========================================================
# CREAR VENTANAS CONTINUAMENTE
# =========================================================

def generar_ventanas():

    if not activo:
        return

    crear_ventana()

    if activo:

        root.after(
            INTERVALO_VENTANA,
            generar_ventanas
        )


# =========================================================
# AUDIO
# =========================================================

ruta_audio = ruta_archivo(
    AUDIO_FILE
)

instancia_vlc = vlc.Instance()

player = instancia_vlc.media_player_new()

media = instancia_vlc.media_new(
    ruta_audio
)

player.set_media(
    media
)


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

        print(
            "Error con el audio:",
            e
        )


# =========================================================
# VENTANA PRINCIPAL
# =========================================================

root = tk.Tk()

# Ocultar ventana principal
root.withdraw()


# =========================================================
# BLOQUEAR CIERRE DE ROOT
# =========================================================

root.protocol(
    "WM_DELETE_WINDOW",
    bloquear_cierre
)


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
# HOTKEY GLOBAL PARA DETENER
# =========================================================

keyboard.add_hotkey(
    "c+m",
    detener_todo,
    suppress=True
)


# =========================================================
# BLOQUEAR ALT + F4
# =========================================================

keyboard.add_hotkey(
    "alt+f4",
    bloquear_cierre,
    suppress=True
)


# =========================================================
# BLOQUEAR ESC
# =========================================================

keyboard.add_hotkey(
    "esc",
    bloquear_cierre,
    suppress=True
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

    # -----------------------------------------------------
    # DETENER TODO
    # -----------------------------------------------------

    activo = False

    try:
        player.stop()

    except:
        pass

    # -----------------------------------------------------
    # QUITAR HOTKEYS
    # -----------------------------------------------------

    try:
        keyboard.remove_hotkey("c+m")

    except:
        pass

    try:
        keyboard.remove_hotkey("alt+f4")

    except:
        pass

    try:
        keyboard.remove_hotkey("esc")

    except:
        pass

    # -----------------------------------------------------
    # CERRAR VENTANAS
    # -----------------------------------------------------

    for ventana in ventanas[:]:

        try:
            ventana.destroy()

        except:
            pass

    ventanas.clear()

