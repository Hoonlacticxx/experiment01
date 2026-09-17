import tkinter as tk
from PIL import image, ImageTk

def load_n_show(dir):
  window = tk.Tk()
  window.title("activa cam")

  window.geometry("600x400")

  image = Image.open("https://github.com/Hoonlacticxx/experiment01/blob/main/images.jpg?raw=true")
  
  canvas = tk.Canvas(window, highlightthickness=0)
  canvas.pack(fill = tk.BOTH, expand = True)

  def resize(event):
    new_len = event.width
    new_height = event.height
  
    if new_len > 10 and new_height > 10:
      r_image = image.resize(
        (new_len, new_height), Image.Resampling.LANCZOS
      )
  
      image_tk = ImageTk.PhotoImage(r_image)
  
      canvas.image = image.tk
  
      canvas.delete("all")
      canvas.create_image(0, 0, anchor=tk.NW, image=image.tk)
  
    canvas.bind("<Configure>", redimesionar_imagen)
  
    window.mainloop()

load_n_show("https://github.com/Hoonlacticxx/experiment01/blob/main/images.jpg?raw=true")
