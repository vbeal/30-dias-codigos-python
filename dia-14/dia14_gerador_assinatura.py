# ###################################################################
#          🎯 Projeto: Gerador de Assinatura (Dia 14)              #
# ###################################################################
# 📁 Caminho: dia-14/dia14_gerador_assinatura.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas:  tkinter (interface gráfica),
#                   Pillow (exportar PNG transparente)
# 🔗 Instalação: pip install pillow
# ###################################################################

import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageDraw


BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "assinaturas")
os.makedirs(OUTPUT_DIR, exist_ok=True)


PEN_STYLES = {
	"Caneta fina": {"width_factor": 0.9, "alpha": 255},
	"Caneta normal": {"width_factor": 1.4, "alpha": 255},
	"Caneta marcador": {"width_factor": 2.2, "alpha": 235},
}

COLOR_OPTIONS = {
	"Preta": "#111111",
	"Azul Bic": "#005BAC",
}


def _distance(p1, p2):
	return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5


class SignatureApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Dia 14 — Gerador de Assinatura")
		self.root.minsize(1100, 700)

		self.pen_color_name = tk.StringVar(value="Preta")
		self.pen_style_name = tk.StringVar(value="Caneta normal")
		self.brush_size = tk.IntVar(value=4)

		self.strokes = []
		self.current_stroke = None
		self.live_stroke_item = None

		self._build_ui()
		self._bind_events()

	def _build_ui(self):
		self.root.configure(bg="#f4f6fb")

		container = ttk.Frame(self.root, padding=16)
		container.pack(fill=tk.BOTH, expand=True)
		container.columnconfigure(0, weight=0)
		container.columnconfigure(1, weight=1)
		container.rowconfigure(0, weight=1)

		sidebar = ttk.Frame(container, padding=16)
		sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 16))

		ttk.Label(sidebar, text="Gerador de Assinatura", font=("Segoe UI", 16, "bold")).pack(anchor="w")
		ttk.Label(
			sidebar,
			text="Desenhe com o mouse e salve em PNG com fundo transparente.",
			wraplength=250,
		).pack(anchor="w", pady=(8, 18))

		ttk.Label(sidebar, text="Cor da caneta").pack(anchor="w")
		for label, value in COLOR_OPTIONS.items():
			ttk.Radiobutton(
				sidebar,
				text=label,
				value=label,
				variable=self.pen_color_name,
			).pack(anchor="w", pady=2)

		ttk.Separator(sidebar).pack(fill=tk.X, pady=16)

		ttk.Label(sidebar, text="Modelo da caneta").pack(anchor="w")
		pen_style = ttk.Combobox(
			sidebar,
			textvariable=self.pen_style_name,
			values=list(PEN_STYLES.keys()),
			state="readonly",
			width=22,
		)
		pen_style.pack(anchor="w", pady=(4, 12), fill=tk.X)

		ttk.Label(sidebar, text="Tamanho da ponta").pack(anchor="w")
		size_frame = ttk.Frame(sidebar)
		size_frame.pack(fill=tk.X, pady=(4, 4))
		ttk.Scale(size_frame, from_=2, to=22, orient=tk.HORIZONTAL, variable=self.brush_size).pack(fill=tk.X)
		self.size_label = ttk.Label(sidebar, text="4 px")
		self.size_label.pack(anchor="w", pady=(4, 12))

		btn_frame = ttk.Frame(sidebar)
		btn_frame.pack(fill=tk.X, pady=(8, 8))

		ttk.Button(btn_frame, text="Limpar", command=self.clear_canvas).pack(fill=tk.X, pady=(0, 8))
		ttk.Button(btn_frame, text="Salvar PNG", command=self.save_signature).pack(fill=tk.X)

		self.status_var = tk.StringVar(value="Pronto para desenhar.")
		ttk.Label(sidebar, textvariable=self.status_var, wraplength=250).pack(anchor="w", pady=(16, 0))

		canvas_box = ttk.Frame(container, padding=10)
		canvas_box.grid(row=0, column=1, sticky="nsew")
		canvas_box.rowconfigure(0, weight=1)
		canvas_box.columnconfigure(0, weight=1)

		ttk.Label(canvas_box, text="Área de assinatura").grid(row=0, column=0, sticky="w", pady=(0, 8))
		self.canvas = tk.Canvas(
			canvas_box,
			bg="white",
			width=900,
			height=520,
			highlightthickness=1,
			highlightbackground="#d8dce6",
		)
		self.canvas.grid(row=1, column=0, sticky="nsew")

		hint = ttk.Label(
			canvas_box,
			text="Clique e arraste o mouse para assinar.",
			foreground="#555",
		)
		hint.grid(row=2, column=0, sticky="w", pady=(8, 0))

		self.root.after(50, self._refresh_size_label)

	def _bind_events(self):
		self.canvas.bind("<ButtonPress-1>", self.on_press)
		self.canvas.bind("<B1-Motion>", self.on_move)
		self.canvas.bind("<ButtonRelease-1>", self.on_release)

	def _refresh_size_label(self):
		self.size_label.config(text=f"{int(self.brush_size.get())} px")
		self.root.after(80, self._refresh_size_label)

	def _current_color(self):
		return COLOR_OPTIONS.get(self.pen_color_name.get(), "#111111")

	def _current_style(self):
		return PEN_STYLES.get(self.pen_style_name.get(), PEN_STYLES["Caneta normal"])

	def _stroke_width(self, stroke):
		style = PEN_STYLES.get(stroke["style"], PEN_STYLES["Caneta normal"])
		return max(1, int(stroke["base_width"] * style["width_factor"]))

	def _interpolate_points(self, points, steps_per_segment=14):
		if len(points) < 2:
			return points[:]

		smoothed = [points[0]]
		for index in range(len(points) - 1):
			start = points[index]
			end = points[index + 1]
			distance = _distance(start, end)
			steps = max(2, int(distance / 2), steps_per_segment)
			for step in range(1, steps + 1):
				ratio = step / steps
				x = start[0] + (end[0] - start[0]) * ratio
				y = start[1] + (end[1] - start[1]) * ratio
				smoothed.append((x, y))
		return smoothed

	def _smoothed_points(self, points):
		if len(points) < 3:
			return points[:]

		smoothed = [points[0]]
		for index in range(1, len(points) - 1):
			prev_x, prev_y = points[index - 1]
			curr_x, curr_y = points[index]
			next_x, next_y = points[index + 1]
			smoothed.append(
				(
					(prev_x + curr_x * 2 + next_x) / 4,
					(prev_y + curr_y * 2 + next_y) / 4,
				)
			)
		smoothed.append(points[-1])
		return smoothed

	def _draw_thick_point(self, draw, point, fill, width):
		radius = max(1, width // 2)
		x, y = point
		draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=fill)

	def _draw_smoothed_stroke(self, draw, stroke):
		points = self._smoothed_points(stroke["points"])
		if len(points) < 2:
			return

		style = PEN_STYLES.get(stroke["style"], PEN_STYLES["Caneta normal"])
		width = self._stroke_width(stroke)
		rgba = self.root.winfo_rgb(stroke["color"])
		fill = (
			rgba[0] // 256,
			rgba[1] // 256,
			rgba[2] // 256,
			style["alpha"],
		)

		for start, end in zip(points, points[1:]):
			draw.line([start, end], fill=fill, width=width)

		for point in self._interpolate_points(points, steps_per_segment=28):
			self._draw_thick_point(draw, point, fill, width)

	def on_press(self, event):
		self.current_stroke = {
			"points": [(event.x, event.y)],
			"color": self._current_color(),
			"base_width": int(self.brush_size.get()),
			"style": self.pen_style_name.get(),
		}
		self.status_var.set("Desenhando assinatura...")

	def on_move(self, event):
		if not self.current_stroke:
			return

		points = self.current_stroke["points"]
		points.append((event.x, event.y))

		style = self._current_style()
		width = max(1, int(self.current_stroke["base_width"] * style["width_factor"]))

		if self.live_stroke_item is not None:
			self.canvas.delete(self.live_stroke_item)

		display_points = self._smoothed_points(points)
		coords = []
		for x, y in display_points:
			coords.extend([x, y])

		self.live_stroke_item = self.canvas.create_line(
			*coords,
			fill=self.current_stroke["color"],
			width=width,
			capstyle=tk.ROUND,
			joinstyle=tk.ROUND,
			smooth=True,
			splinesteps=72,
		)

	def on_release(self, event):
		if not self.current_stroke:
			return

		self.current_stroke["points"].append((event.x, event.y))
		if len(self.current_stroke["points"]) > 1:
			self.strokes.append(self.current_stroke)
		self.live_stroke_item = None
		self.current_stroke = None
		self.status_var.set("Assinatura pronta. Você pode salvar em PNG.")

	def clear_canvas(self):
		self.canvas.delete("all")
		self.strokes.clear()
		self.current_stroke = None
		self.live_stroke_item = None
		self.status_var.set("Tela limpa.")

	def _draw_stroke(self, draw, stroke):
		self._draw_smoothed_stroke(draw, stroke)

	def _build_signature_image(self):
		self.root.update_idletasks()
		canvas_width = max(1, self.canvas.winfo_width())
		canvas_height = max(1, self.canvas.winfo_height())

		image = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))
		draw = ImageDraw.Draw(image, "RGBA")

		for stroke in self.strokes:
			self._draw_stroke(draw, stroke)

		bbox = image.getbbox()
		if bbox:
			pad = 24
			left = max(0, bbox[0] - pad)
			top = max(0, bbox[1] - pad)
			right = min(image.width, bbox[2] + pad)
			bottom = min(image.height, bbox[3] + pad)
			image = image.crop((left, top, right, bottom))

		return image

	def save_signature(self):
		if not self.strokes:
			messagebox.showwarning(
				"Sem assinatura",
				"Desenhe a assinatura antes de salvar.",
				parent=self.root,
			)
			return

		image = self._build_signature_image()
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		filename = f"assinatura_{timestamp}.png"
		path = os.path.join(OUTPUT_DIR, filename)
		image.save(path)

		self.status_var.set(f"Assinatura salva em {path}")
		messagebox.showinfo(
			"Assinatura salva",
			f"PNG transparente salvo com sucesso:\n{path}",
			parent=self.root,
		)


def main():
	root = tk.Tk()
	ttk.Style().theme_use("clam")
	SignatureApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()


