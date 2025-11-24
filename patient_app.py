import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk, ImageDraw  

FONT_NAME = "Calibri" 
FONT_SIZE = 10
ROW_HEIGHT = 20
BG_COLOR = "#AFEEEE"      
LIST_BG_COLOR = "#E0FFFF" 

try:
    from faker import Faker
    fake = Faker('ru_RU')
except ImportError:
    fake = None

DATA_FILE = "patients.json"

class PatientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система учёта пациентов")
        self.root.geometry("1100x700")
        
        self.root.configure(bg=BG_COLOR)
        self.root.option_add("*Font",  f"{FONT_NAME} {FONT_SIZE}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.patients = []
        self.load_data()


        self.cloud_img = self.create_cloud_icon(width=190, height=75)


        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG_COLOR)
        style.configure("Treeview", font=(FONT_NAME, FONT_SIZE), rowheight=ROW_HEIGHT,
                        fieldbackground=LIST_BG_COLOR, background=LIST_BG_COLOR)
        style.configure("Treeview.Heading", font=(FONT_NAME, FONT_SIZE + 1, 'bold'),
                        background="#B0E0E6")


        toolbar = tk.Frame(self.root, bd=0, bg=BG_COLOR)
        toolbar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        buttons_data = [
            ("Добавить", self.open_add_window),
            ("Изменить", self.open_edit_window),
            ("Удалить", self.delete_patient),
            ("Статистика", self.show_statistics),
            ("Генерация", self.generate_fake)
        ]

        for text, func in buttons_data:
            btn = tk.Button(toolbar, 
                            text=text, 
                            image=self.cloud_img,     
                            compound="center",        
                            command=func,
                            bg=BG_COLOR,             
                            activebackground=BG_COLOR,
                            bd=0,                    
                            highlightthickness=0,
                            fg="black",              
                            font=(FONT_NAME, 11, 'bold'), 
                            cursor="hand2")
            
           
            btn.pack(side=tk.TOP, pady=8)

  
        columns = ("fullname", "age", "gender", "height", "weight", "bmi")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        
        headers = ["ФИО", "Возраст", "Пол", "Рост (см)", "Вес (кг)", "ИМТ"]
        widths = [300, 80, 60, 100, 100, 80]
        
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor=tk.CENTER if col != "fullname" else tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_table()

    def create_cloud_icon(self, width, height):
        """
        Рисует белое облако на прозрачном фоне.
        """
       
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        white = (255, 255, 255, 255)

        
  
        draw.ellipse([width*0.1, height*0.35, width*0.9, height*0.95], fill=white)
        

        draw.ellipse([width*0.15, height*0.20, width*0.45, height*0.70], fill=white)
        
    
        draw.ellipse([width*0.35, height*0.05, width*0.70, height*0.80], fill=white)
        
    
        draw.ellipse([width*0.60, height*0.20, width*0.90, height*0.70], fill=white)
        
        return ImageTk.PhotoImage(img)


    def on_closing(self):
        self.root.destroy()
        plt.close('all')
        sys.exit()

    def calculate_bmi(self, height_cm, weight_kg):
        try:
            return round(weight_kg / ((height_cm / 100) ** 2), 2)
        except: return 0

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in self.patients:
            self.tree.insert("", tk.END, values=(p['fullname'], p['age'], p['gender'], p['height'], p['weight'], p['bmi']))

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.patients, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.patients = json.load(f)
            except: pass

    def open_form(self, patient=None, index=None):
        top = tk.Toplevel(self.root)
        top.geometry("400x450")
        top.configure(bg=BG_COLOR) 

        fields = [("ФИО", "fullname"), ("Возраст", "age"), ("Пол (M/F)", "gender"), ("Рост (см)", "height"), ("Вес (кг)", "weight")]
        entries = {}

        for label_text, key in fields:
            tk.Label(top, text=label_text, bg=BG_COLOR).pack(pady=5)
            entry = tk.Entry(top)
            entry.pack(pady=2)
            if patient:
                entry.insert(0, patient[key])
            entries[key] = entry
        
        def submit():
            try:
                data = {k: entries[k].get() for k in entries}
                if not data["age"] or not data["height"] or not data["weight"]:
                     raise ValueError("Заполните все числовые поля")

                data["age"] = int(data["age"])
                data["height"] = float(data["height"])
                data["weight"] = float(data["weight"])
                data["gender"] = data["gender"].upper().strip()
                
                data["bmi"] = self.calculate_bmi(data["height"], data["weight"])

                if index is not None:
                    self.patients[index] = data
                else:
                    self.patients.append(data)
                
                self.save_data()
                self.refresh_table()
                top.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Проверьте данные!\n{e}")

        tk.Button(top, text="Сохранить", command=submit, bg="#4CAF50", fg="white").pack(pady=20, fill=tk.X, padx=30)

    def open_add_window(self):
        self.open_form()

    def open_edit_window(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пациента")
            return
        index = self.tree.index(selected[0]) 
        self.open_form(self.patients[index], index)

    def delete_patient(self):
        selected = self.tree.selection()
        if selected:
            if messagebox.askyesno("Подтверждение", "Удалить запись?"):
                del self.patients[self.tree.index(selected[0])]
                self.save_data()
                self.refresh_table()

    def generate_fake(self):
        if not fake: return
        for _ in range(5):
            h = fake.random_int(150, 200)
            w = fake.random_int(50, 120)
            g = fake.random_element(["M", "F"])
            self.patients.append({
                "fullname": fake.name(), 
                "age": fake.random_int(18, 90), 
                "gender": g, "height": h, "weight": w,
                "bmi": self.calculate_bmi(h, w)
            })
        self.save_data()
        self.refresh_table()

    def show_statistics(self):
        if not self.patients:
            messagebox.showinfo("Инфо", "Нет данных")
            return

        stats_win = tk.Toplevel(self.root)
        stats_win.title("Статистика")
        stats_win.geometry("1000x800")
        

        stats_win.configure(bg=BG_COLOR)

        def close_stats():
            plt.close(fig)
            stats_win.destroy()
        stats_win.protocol("WM_DELETE_WINDOW", close_stats)

        ages = [p['age'] for p in self.patients]
        genders = [p['gender'] for p in self.patients]
        bmis = [p['bmi'] for p in self.patients]
        
        fig, axs = plt.subplots(2, 2, figsize=(10, 8))
        
     
        fig.patch.set_facecolor(BG_COLOR)
        
        fig.tight_layout(pad=5.0)


        count_m = genders.count('M')
        count_f = genders.count('F')
        if count_m + count_f > 0:
            axs[0, 0].pie([count_m, count_f], labels=['М', 'Ж'], autopct='%1.1f%%')
        axs[0, 0].set_title("Пол")


        axs[0, 1].hist(ages, bins=10, color='skyblue', edgecolor='black')
        axs[0, 1].set_title("Возраст")


        bmi_m = [p['bmi'] for p in self.patients if p['gender'] == 'M']
        bmi_f = [p['bmi'] for p in self.patients if p['gender'] == 'F']
        data = []
        lbls = []
        if bmi_m: data.append(bmi_m); lbls.append('М')
        if bmi_f: data.append(bmi_f); lbls.append('Ж')
            
        if data:
            axs[1, 0].boxplot(data, tick_labels=lbls)
        axs[1, 0].set_title("ИМТ по полу")


        axs[1, 1].scatter(ages, bmis, alpha=0.6, c='green')
        axs[1, 1].set_title("ИМТ / Возраст")

        canvas = FigureCanvasTkAgg(fig, master=stats_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = PatientApp(root)
    root.mainloop()
