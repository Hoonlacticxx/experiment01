import tkinter as tk
from PIL import Image, ImageTk
import vlc
import os
import sys


# ==========================================
# CONFIGURACIÓN
# ==========================================

IMAGE_FILE = "imagen.jpg"
AUDIO_FILE = "audio.mp3"

NUM_VENTANAS = 10


# ==========================================
# RUTA DE ARCHIVOS
# ==========================================

def obtener_ruta(archivo):

    if getattr(sys, "frozen", False):
        carpeta = sys._MEIPASS
    else:
        carpeta = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        carpeta,
        archivo
    )


# ==========================================
# AUDIO
# ==========================================

reproductor = None


def reproducir_audio():

    global reproductor

    ruta_audio = obtener_ruta(AUDIO_FILE)

    if not os.path.exists(ruta_audio):

        print("No se encontró el audio:")
        print(ruta_audio)

        return

    reproductor = vlc.MediaPlayer(
        ruta_audio
    )

    reproductor.audio_set_volume(100)

    reproductor.play()


def detener_audio():

    global reproductor

    if reproductor is not None:

        reproductor.stop()


# ==========================================
# CARGAR IMAGEN
# ==========================================

def cargar_imagen():

    ruta = obtener_ruta(IMAGE_FILE)

    return Image.open(ruta)


# ==========================================
# PROGRAMA
# ==========================================

def iniciar_broma():

    try:

        imagen_original = cargar_imagen()

    except Exception as error:

        print("No se pudo cargar la imagen:")
        print(error)

        return


    ventana_principal = tk.Tk()

    ventana_principal.withdraw()

    ventanas = []


    # ======================================
    # CERRAR TODO CON ESC
    # ======================================

    def cerrar_todo(event=None):

        detener_audio()

        for ventana in ventanas:

            try:

                ventana.destroy()

            except tk.TclError:

                pass

        ventana_principal.destroy()


    ventana_principal.bind_all(
        "<Escape>",
        cerrar_todo
    )


    # ======================================
    # CREAR VENTANAS
    # ======================================

    for i in range(NUM_VENTANAS):

        ventana = tk.Toplevel(
            ventana_principal
        )

        ventana.title("ACTIVA CAM")

        ventana.geometry("500x350")


        canvas = tk.Canvas(
            ventana,
            highlightthickness=0
        )

        canvas.pack(
            fill=tk.BOTH,
            expand=True
        )


        def redimensionar(
            event,
            canvas=canvas
        ):

            if event.width <= 10 or event.height <= 10:

                return


            imagen = imagen_original.copy()

            imagen = imagen.resize(
                (
                    event.width,
                    event.height
                ),
                Image.Resampling.LANCZOS
            )


            imagen_tk = ImageTk.PhotoImage(
                imagen
            )

            canvas.image = imagen_tk

            canvas.delete("all")

            canvas.create_image(
                0,
                0,
                anchor=tk.NW,
                image=imagen_tk
            )


        canvas.bind(
            "<Configure>",
            redimensionar
        )

        ventanas.append(ventana)


    # ======================================
    # REPRODUCIR AUDIO
    # ======================================

    reproducir_audio()


    ventana_principal.mainloop()


# ==========================================
# EJECUTAR
# ==========================================

if __name__ == "__main__":

    iniciar_broma()