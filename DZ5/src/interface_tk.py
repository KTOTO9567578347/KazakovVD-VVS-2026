import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import validators
from tkinter import messagebox
from PIL import ImageTk

from vis import generate_integral_image
from calculus import calculate_riemann_sum

class Interface(tk.Tk):
    
    class LabeledEntry(tk.Frame):
        def __init__(self, master=None, label_text='Подпись:', **kwargs):
            super().__init__(master)

            self.label = tk.Label(self, text=label_text, anchor='w')
            self.label.pack(fill='x', pady=2)

            self.entry = tk.Entry(self, **kwargs)
            self.entry.pack(fill='x')
        def get(self):
            return self.entry.get()

    def __init__(self):
        super().__init__()

        self.title("Интеграллотрон")
        self.geometry("1000x650")
        self.configure(background="#16ff01")

        self.result_frame = tk.Frame(self, bg="#ff0000", bd=1, relief="solid")
        self.result_frame.pack(side="top", fill="x", padx=10, pady=(10, 5))

        self.text1 = tk.Label(self.result_frame, text="Интегрирование :(", font=("Arial", 12, "bold"), bg="#0946ec")
        self.text1.pack(side="left", padx=15, pady=10)

        self.left_bound = tk.StringVar(self, name="left_bound")
        self.right_bound = tk.StringVar(self, name="right_bound")
        self.n = tk.StringVar(self, name="box_cnts")
        self.result_var = tk.DoubleVar(self, name="resultvar")

        self.res_label = tk.Label(self.result_frame, textvariable=self.result_var, font=("Courier", 14, "bold"), fg="#ff0800", bg="#00ccff")
        self.res_label.pack(side="left", padx=5, pady=10)

        self.plot_container = tk.Frame(self, bg="#d9ff00", bd=1, relief="solid")
        self.plot_container.pack(side="top", expand=True, fill="both", padx=10, pady=5)

        self.image_label = tk.Label(self.plot_container, bg="#fa02fa")
        self.image_label.pack(expand=True, fill="both", padx=5, pady=5)

        self.input_frame = tk.LabelFrame(self, text=" Панель управления ", padx=10, pady=10, bg="#ff7b00")
        self.input_frame.pack(side="bottom", fill="x", padx=10, pady=(5, 10))

        self.method_frame = tk.Frame(self.input_frame)
        self.method_frame.pack(side="left", padx=(0, 15))
        self.method = tk.StringVar(self, name="method_selected", value=validators.MODES)
        self.listbox1 = tk.Listbox(self.method_frame, name="method_selector", width=12, height=3, listvariable=self.method, exportselection=False)
        self.listbox1.pack(anchor='w')
        self.listbox1.selection_set(validators.DEFAULT)
        self.listbox1.activate(validators.DEFAULT)

        self.lbound_inp = self.LabeledEntry(self.input_frame, label_text='Левая граница', textvariable=self.left_bound)
        self.lbound_inp.pack(side="left", padx=10, anchor='n')

        self.rbound_inp = self.LabeledEntry(self.input_frame, label_text='Правая граница', textvariable=self.right_bound)
        self.rbound_inp.pack(side="left", padx=10, anchor='n')

        self.n_inp = self.LabeledEntry(self.input_frame, label_text='Кол-во прямоугольников', textvariable=self.n)
        self.n_inp.pack(side="left", padx=10, anchor='n')

        self.start_button = tk.Button(self.input_frame, text="Старт!", command=self.run, bg="#000000", fg="white", font=("Arial", 10, "bold"), padx=10)
        self.start_button.pack(side="left", padx=15, pady=15, anchor='n')

        self.f_frame = tk.Frame(self.input_frame)
        self.f_frame.pack(side="left", expand=True, fill="x", padx=(10, 0), anchor='n')
        tk.Label(self.f_frame, text="Формула f(x):", font=("Arial", 9, "bold")).pack(anchor="w")
        
        self.f_inp = tk.Text(self.f_frame, height=2, wrap="word", font=("Courier", 11, "bold"))
        self.f_inp.pack(fill="x", expand=True, pady=2)

        self.mainloop()

    def show_error_window(self, error_text):
        messagebox.showerror(title="Ошибка!", message=error_text)
    
    def run(self):
        from validators import is_nat, is_mode, check_bounds;

        data = {
            "method": self.listbox1.get(self.listbox1.curselection()[0]),
            "L": self.left_bound.get(),
            "R": self.right_bound.get(),
            "N": self.n.get(),
            "F": self.f_inp.get("1.0", tk.END).strip(),
        }

        if (not check_bounds(data['L'], data['R'])):
            self.show_error_window("Неверные границы.")
            return;
    
        data['L'] = float(data['L'])
        data['R'] = float(data['R'])

        if (not is_nat(data['N'])):
            self.show_error_window("Неверное число прямоугольников.")
            return;
        data['N'] = int(data['N'])

        if (not is_mode(data['method'])):
            self.show_error_window("Неверный режим (чзх).")
            return;

        f = lambda x: x;
        try:
            f = validators.create_vectorized_function(data['F'])
            f(1)
        except Exception as e:
            self.show_error_window("Проверьте корректность функции.")
            return;
        data["F"] = f

        integral_value, x_eval, y_eval, x_bar_pos, align, dx = calculate_riemann_sum(**data)
        pil_image = generate_integral_image(data['F'], data['L'], data['R'], data['N'], data['method'], integral_value, x_eval, y_eval, x_bar_pos, align, dx)
        tk_image = ImageTk.PhotoImage(pil_image)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image
        self.result_var.set(f"{integral_value:.5f}")

Interface()