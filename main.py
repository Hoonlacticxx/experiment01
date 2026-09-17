
import tkinter as tk
from PIL import Image, ImageTk
import vlc
import os
import sys
import random
import keyboard


# ==========================================
# CONFIGURACIÓN
# ==========================================

IMAGE_FILE = "imagen.jpg"
AUDIO_FILE = "audio.mp3"

# Cada cuánto aparece una ventana
INTERVALO_VENTANA = 300

ANCHO = 450
ALTO = 300


# ==========================================
# VARIABLES
# ==========================================

activo = True
ventanas = []

reproductor = None
root = None
imagen_original = None


# ==========================================
# RUTA
# ==========================================

def ruta_archivo(nombre):

    if getattr(sys, "frozen", False):
        carpeta = sys._MEIPASS
    else:
        carpeta = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        carpeta,
        nombre
    )


# ==========================================
# AUDIO
# ==========================================

def iniciar_audio():

    global reproductor

    ruta = ruta_archivo(AUDIO_FILE)

    if not os.path.exists(ruta):
        print("No existe:", ruta)
        return

    reproductor = vlc.MediaPlayer(ruta)

    reproductor.audio_set_volume(100)

    reproductor.play()

    revisar_audio()


def revisar_audio():

    if not activo:
        return

    if reproductor is not None:

        estado = reproductor.get_state()

        if estado == vlc.State.Ended:

            reproductor.stop()

            reproductor.set_media(
                vlc.Media(
                    ruta_archivo(AUDIO_FILE)
                )
            )

            reproductor.play()

    if activo:
        root.after(
            300,
            revisar_audio
        )


def detener_audio():

    global reproductor

    if reproductor is not None:

        try:
            reproductor.stop()
            reproductor.release()
        except:
            pass

        reproductor = None


# ==========================================
# POSICIÓN ALEATORIA
# ==========================================

def posicion_random():

    pantalla_ancho = root.winfo_screenwidth()
    pantalla_alto = root.winfo_screenheight()

    max_x = pantalla_ancho - ANCHO
    max_y = pantalla_alto - ALTO

    x = random.randint(
        0,
        max(0, max_x)
    )

    y = random.randint(
        0,
        max(0, max_y)
    )

    return x, y


# ==========================================
# CREAR VENTANA
# ==========================================

def crear_ventana():

    if not activo:
        return

    # Crear ventana
    ventana = tk.Toplevel(root)

    # ======================================
    # QUITAR COMPLETAMENTE LA BARRA
    # ======================================

    ventana.overrideredirect(True)

    # Mantener encima
    ventana.attributes(
        "-topmost",
        True
    )

    # ======================================
    # POSICIÓN ALEATORIA
    # ======================================

    x, y = posicion_random()

    ventana.geometry(
        "{}x{}+{}+{}".format(
            ANCHO,
            ALTO,
            x,
            y
        )
    )

    # Forzar a Windows a aplicar
    # inmediatamente la posición
    ventana.update_idletasks()

    # ======================================
    # CANVAS
    # ======================================

    canvas = tk.Canvas(
        ventana,
        highlightthickness=0,
        bd=0
    )

    canvas.pack(
        fill="both",
        expand=True
    )

    # ======================================
    # IMAGEN
    # ======================================

    imagen = imagen_original.copy()

    imagen.thumbnail(
        (
            ANCHO,
            ALTO
        ),
        Image.Resampling.LANCZOS
    )

    imagen_tk = ImageTk.PhotoImage(
        imagen
    )

    canvas.create_image(
        ANCHO // 2,
        ALTO // 2,
        image=imagen_tk,
        anchor="center"
    )

    # Guardar referencia
    ventana.imagen = imagen_tk

    # Guardar ventana
    ventanas.append(
        ventana
    )

    # ======================================
    # CREAR OTRA VENTANA
    # ======================================

    if activo:

        root.after(
            INTERVALO_VENTANA,
            crear_ventana
        )


# ==========================================
# DETENER TODO
# ==========================================

def detener_todo():

    global activo

    if not activo:
        return

    print()
    print("C + M DETECTADO")
    print("DETENIENDO TODO...")

    activo = False

    # Detener audio
    detener_audio()

    # Cancelar futuras ventanas
    # y cerrar todas las existentes
    for ventana in ventanas:

        try:
            ventana.destroy()
        except:
            pass

    ventanas.clear()

    # Cerrar programa
    try:
        root.destroy()
    except:
        pass


# ==========================================
# COMBINACIÓN GLOBAL C + M
# ==========================================

keyboard.add_hotkey(
    "c+m",
    detener_todo
)


# ==========================================
# CARGAR IMAGEN
# ==========================================

try:

    imagen_original = Image.open(
        ruta_archivo(
            IMAGE_FILE
        )
    )

except Exception as error:

    print(
        "Error cargando imagen:"
    )

    print(error)

    try:
        keyboard.remove_hotkey(
            "c+m"
        )
    except:
        pass

    sys.exit()


# ==========================================
# ROOT
# ==========================================

root = tk.Tk()

root.withdraw()


# ==========================================
# INICIAR
# ==========================================

iniciar_audio()

crear_ventana()


# ==========================================
# LOOP
# ==========================================

root.mainloop()


# ==========================================
# LIMPIEZA
# ==========================================

try:

    keyboard.remove_hotkey(
        "c+m"
    )

except:
    pass

detener_audio()

print("Programa terminado.")