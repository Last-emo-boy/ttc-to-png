import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk
from fontTools.ttLib import TTFont, TTCollection
from pathlib import Path


def render_char_to_png(font_path, char, output_folder, font_size=40):
    font = ImageFont.truetype(str(font_path), font_size)
    image = Image.new('RGB', (font_size, font_size), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    text_width, text_height = draw.textsize(char, font=font)
    text_x = (font_size - text_width) / 2
    text_y = (font_size - text_height) / 2
    draw.text((text_x, text_y), char, font=font, fill=(0, 0, 0))
    output_path = Path(output_folder) / f'{char}.png'
    image.save(output_path)

# 主 UI 类
class FontRendererApp:
    def __init__(self, root):
        self.root = root
        root.title("Font Renderer")
        self.setup_ui()

    def setup_ui(self):
        # Grid configuration for dynamic resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # TTC File Selection
        tk.Label(self.root, text="Select TTC File:").grid(row=0, column=0, sticky="w")
        self.ttc_file_label = tk.Label(self.root, text="No file selected")
        self.ttc_file_label.grid(row=0, column=1, sticky="ew")
        tk.Button(self.root, text="Browse", command=self.browse_ttc_file).grid(row=0, column=2, sticky="ew")

        # Output Folder Selection
        tk.Label(self.root, text="Select Output Folder:").grid(row=1, column=0, sticky="w")
        self.output_folder_label = tk.Label(self.root, text="No folder selected")
        self.output_folder_label.grid(row=1, column=1, sticky="ew")
        tk.Button(self.root, text="Browse", command=self.browse_output_folder).grid(row=1, column=2, sticky="ew")

        # Font Selection Combobox
        tk.Label(self.root, text="Select Font:").grid(row=2, column=0, sticky="w")
        self.font_combo = ttk.Combobox(self.root, state="readonly")
        self.font_combo.grid(row=2, column=1, columnspan=2, sticky="ew")

        # 字体大小选择
        tk.Label(self.root, text="Font Size:").grid(row=5, column=0, sticky="w")
        self.font_size_scale = tk.Scale(self.root, from_=10, to=100, orient="horizontal")
        self.font_size_scale.set(40)  # 默认字体大小
        self.font_size_scale.grid(row=5, column=1, sticky="ew")

        # Character Entry
        tk.Label(self.root, text="Enter Character:").grid(row=3, column=0, sticky="w")
        self.char_entry = tk.Entry(self.root)
        self.char_entry.grid(row=3, column=1, columnspan=2, sticky="ew")

        # Render Button
        tk.Button(self.root, text="Render Character", command=self.render_character).grid(row=4, column=1, sticky="ew")

        # 字体预览
        self.preview_canvas = tk.Canvas(self.root, width=100, height=100)
        self.preview_canvas.grid(row=6, column=0, columnspan=3)

        # 批量生成按钮
        tk.Button(self.root, text="Batch Generate Characters", command=self.batch_generate).grid(row=7, column=1, sticky="ew")

        # Set the minimum size of the window
        self.root.update()
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())


    def browse_ttc_file(self):
        filetypes = [("Font Files", "*.ttc;*.ttf"), ("TTC Files", "*.ttc"), ("TTF Files", "*.ttf")]
        self.font_file_path = filedialog.askopenfilename(filetypes=filetypes)
        if self.font_file_path:
            self.ttc_file_label.config(text=Path(self.font_file_path).name)
            self.update_font_list()

    def update_font_list(self):
        if self.font_file_path.lower().endswith(".ttc"):
            try:
                ttc = TTCollection(self.font_file_path)
                font_names = [f"{font['name'].getName(1, 3, 1, 1033)}" for font in ttc.fonts]
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        elif self.font_file_path.lower().endswith(".ttf"):
            try:
                ttf = TTFont(self.font_file_path)
                font_name = f"{ttf['name'].getName(1, 3, 1, 1033)}"
                font_names = [font_name]
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        else:
            messagebox.showerror("Error", "Unsupported file type.")
            return

        self.font_combo['values'] = font_names
        if font_names:
            self.font_combo.current(0)
    
    

    def update_preview(self, char, font_path):
        # 清除旧预览
        self.preview_canvas.delete("all")

        # 创建新预览
        font_size = self.font_size_scale.get()
        font = self.load_font(font_path, font_size)
        if font is None:
            return  # 如果字体加载失败，退出函数

        image = Image.new('RGB', (100, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), char, font=font, fill=(0, 0, 0))

        # 在画布上显示预览
        self.preview_image = ImageTk.PhotoImage(image)
        self.preview_canvas.create_image(50, 50, image=self.preview_image)

    def render_char_to_individual_png(self, font_path, char, output_folder):
        font_size = self.font_size_scale.get()
        font = self.load_font(font_path, font_size)
        if font is None:
            return  # 如果字体加载失败，退出函数

        image = Image.new('RGB', (font_size, font_size), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), char, font=font, fill=(0, 0, 0))
        output_path = Path(output_folder) / f'{ord(char)}.png'
        image.save(output_path)

    def load_font(self, font_path, font_size):
        try:
            font_path_str = str(font_path)
            if font_path_str.lower().endswith(".ttc"):
                ttc = TTCollection(font_path_str)
                font = ttc.fonts[0]  # 使用 TTC 中的第一个字体
                temp_font_path = Path(self.output_folder) / "temp_font.ttf"
                font.save(str(temp_font_path))
                return ImageFont.truetype(str(temp_font_path), font_size)
            else:
                return ImageFont.truetype(font_path_str, font_size)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None


    def browse_output_folder(self):
        self.output_folder = filedialog.askdirectory()
        if self.output_folder:
            self.output_folder_label.config(text=Path(self.output_folder).name)

    def render_character(self):
        char = self.char_entry.get()
        if not char:
            messagebox.showerror("Error", "Please enter a character.")
            return
        if not self.font_file_path or not self.output_folder:
            messagebox.showerror("Error", "Please select a font file and output folder.")
            return

        selected_font_index = self.font_combo.current()
        if selected_font_index == -1:
            messagebox.showerror("Error", "Please select a font from the list.")
            return

        try:
            if self.font_file_path.lower().endswith(".ttc"):
                ttc = TTCollection(self.font_file_path)
                font = ttc.fonts[selected_font_index]  # 使用用户选择的字体
            elif self.font_file_path.lower().endswith(".ttf"):
                font = TTFont(self.font_file_path)
            else:
                messagebox.showerror("Error", "Unsupported file type.")
                return

            font_path = Path(self.output_folder) / "temp_font.ttf"
            font.save(str(font_path))
            render_char_to_png(font_path, char, self.output_folder)
            messagebox.showinfo("Success", f"Character '{char}' rendered successfully.")
            font_path.unlink()  # 删除临时字体文件
        except Exception as e:
            messagebox.showerror("Error", str(e))

        self.update_preview(char, font_path)

    def batch_generate(self):
        if not self.font_file_path or not self.output_folder:
            messagebox.showerror("Error", "Please select a font file and output folder.")
            return

        try:
            characters = self.get_supported_characters(self.font_file_path)
            for char in characters:
                self.render_char_to_individual_png(self.font_file_path, char, self.output_folder)
            messagebox.showinfo("Success", f"{len(characters)} characters rendered successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_supported_characters(self, font_path):
        characters = []
        font = TTFont(font_path)
        for cmap in font['cmap'].tables:
            if cmap.isUnicode():
                characters.extend([chr(code) for code in cmap.cmap.keys()])
        return set(characters)  # 使用集合去重

    def render_char_to_individual_png(self, font_path, char, output_folder):
        font_size = self.font_size_scale.get()
        font = ImageFont.truetype(font_path, font_size)
        image = Image.new('RGB', (font_size, font_size), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), char, font=font, fill=(0, 0, 0))
        output_path = Path(output_folder) / f'{ord(char)}.png'
        image.save(output_path)




# 创建和运行应用
if __name__ == "__main__":
    root = tk.Tk()
    app = FontRendererApp(root)
    root.mainloop()