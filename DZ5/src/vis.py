import io
import colorsys
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageFile

def generate_integral_image(F, L: float, R: float, N: int, method: str, 
                            integral_value: float, x_eval, y_eval, x_bar_pos, align: str, dx: float) -> ImageFile:
    """
    Чистый генератор картинок с кастомным неоново-радужным оформлением.
    """
    with plt.style.context('dark_background'):
        fig, ax = plt.subplots(figsize=(6, 4.5), dpi=100)
        
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        ax.grid(True, linestyle="--", alpha=0.6, color='green')

        pad = (R - L) * 0.15 if R - L > 0 else 1
        x_smooth = np.linspace(L - pad, R + pad, 300)
        
        try:
            ax.plot(x_smooth, F(x_smooth), color="red", lw=4, label="f(x)")
        except Exception:
            x_smooth = np.linspace(L, R, 300)
            ax.plot(x_smooth, F(x_smooth), color="red", lw=4, label="f(x)")

        valid_y = y_eval[np.isfinite(y_eval)]
        if len(valid_y) > 0:
            y_max = np.max(np.abs(valid_y)) * 1.5
            if y_max == 0: y_max = 1.0
            ax.set_ylim(-y_max, y_max)

        ax.bar(
            x_bar_pos, y_eval, width=dx, align=align,
            alpha=0.4, color="#00E5FF", edgecolor="#00BFFF", lw=1.5,
            label=f"Сумма ({method})"
        )

        ax.axvline(L, color="#FF00FF", linestyle="--", lw=2.5, label="Граница L")
        ax.axvline(R, color="#FF00FF", linestyle="--", lw=2.5, label="Граница R")
        
        ax.set_title(f"Метод: {method} прямоугольники (N = {N})\nЗначение: {integral_value:.5f}")

        fig.canvas.draw()

        x_labels = ax.get_xticklabels()
        num_x = len(x_labels)
        for i, label in enumerate(x_labels):
            rgb = colorsys.hsv_to_rgb(i / max(1, num_x), 1.0, 1.0)
            label.set_color(rgb)
            label.set_weight('bold')

        y_labels = ax.get_yticklabels()
        num_y = len(y_labels)
        for i, label in enumerate(y_labels):
            rgb = colorsys.hsv_to_rgb(i / max(1, num_y), 1.0, 1.0)
            label.set_color(rgb)
            label.set_weight('bold')

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor='none')
        buf.seek(0)
        plt.close(fig)

    pil_image = Image.open(buf)
    return pil_image
