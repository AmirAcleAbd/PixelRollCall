import math
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
from tkinter import ttk
from PIL import Image
import time
import pickle

class PixelRollCall:
    def __init__(self, master):
        self.master = master
        self.image_path = None
        self.start_time = None
        self.image_size = None 

        master.title('Pixel Roll Call')
        master.geometry('1000x700')

        self.color_locations = {}

        top_button_frame = tk.Frame(master)
        top_button_frame.pack(pady=10)

        self.select_button = tk.Button(top_button_frame, text='Select PNG', command=self.select_image)
        self.select_button.pack(side=tk.LEFT, padx=5)

        self.analyze_button = tk.Button(top_button_frame, text='Analyze Colors', command=self.analyze_image)
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        self.import_button = tk.Button(top_button_frame, text='Import Data', command=self.import_data)
        self.import_button.pack(side=tk.LEFT, padx=5)

        self.low_power_var = tk.BooleanVar()
        self.low_power_checkbox = tk.Checkbutton(top_button_frame, text="Low Power Mode (+15%)", variable=self.low_power_var)
        self.low_power_checkbox.pack(side=tk.LEFT, padx=5)

        text_frame = tk.Frame(master)
        text_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.left_text = scrolledtext.ScrolledText(text_frame, height=10, width=40)
        self.left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_text = scrolledtext.ScrolledText(text_frame, height=10, width=40)
        self.right_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        entry_frame = tk.Frame(master)
        entry_frame.pack(pady=5)

        self.color_label = tk.Label(entry_frame, text="Color:  #")
        self.color_label.pack(side=tk.LEFT, padx=0)

        self.color_input = tk.Entry(entry_frame, width=20)
        self.color_input.insert(0, "")
        self.color_input.pack(side=tk.LEFT, padx=0)

        self.search_button = tk.Button(master, text='Search Color', command=self.search_color)
        self.search_button.pack(pady=5)

        self.all_coords_var = tk.BooleanVar()
        self.all_coords_checkbox = tk.Checkbutton(entry_frame, text="list all", variable=self.all_coords_var)
        self.all_coords_checkbox.pack(side=tk.LEFT, padx=5)

        self.min_label = tk.Label(entry_frame, text="Min (x,y):")
        self.min_label.pack(side=tk.LEFT, padx=5)

        self.min_input = tk.Entry(entry_frame, width=10)
        self.min_input.pack(side=tk.LEFT, padx=5)

        self.max_label = tk.Label(entry_frame, text="Max (x,y):")
        self.max_label.pack(side=tk.LEFT, padx=5)

        self.max_input = tk.Entry(entry_frame, width=10)
        self.max_input.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(master, orient="horizontal", mode="determinate", length=500)
        self.progress.pack(pady=10)

        bottom_button_frame = tk.Frame(master)
        bottom_button_frame.pack(pady=10)

        self.export_button = tk.Button(bottom_button_frame, text='Export Data', command=self.export_data)
        self.export_button.pack(side=tk.LEFT, padx=5)

    def select_image(self):
        file_name = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
        if file_name:
            self.image_path = file_name
            self.left_text.delete('1.0', tk.END)
            self.left_text.insert(tk.END, f"Selected image: {file_name}")

    def analyze_image(self):
        if not self.image_path:
            self.left_text.delete('1.0', tk.END)
            self.left_text.insert(tk.END, "select an image first.")
            return

        image = Image.open(self.image_path).convert('RGB')
        self.image_size = image.size
        width, height = self.image_size
        self.bit_depth = image.getbands()

        xaxis = 48
        yaxis = int(xaxis * height / width)
        total_pixels = width * height
        self.color_locations = {}
        self.left_text.delete('1.0', tk.END)

        self.start_time = time.time()

        if self.low_power_var.get():
            for x in range(width):
                for y in range(height):
                    r, g, b = image.getpixel((x, y))[:3]
                    color = f"#{r:02X}{g:02X}{b:02X}"
                    if color not in self.color_locations:
                        self.color_locations[color] = []
                    self.color_locations[color].append((x, y))

        else:
            # self.start_time = time.time()    
            pixels_processed = 0
            grid = [['-' for _ in range(xaxis)] for _ in range(yaxis)]
            last_update_time = self.start_time 

            for x in range(width):
                for y in range(height):
                    r, g, b = image.getpixel((x, y))[:3]
                    color = f"#{r:02X}{g:02X}{b:02X}"
                    if color not in self.color_locations:
                        self.color_locations[color] = []
                    self.color_locations[color].append((x, y))

                    pixels_processed += 1
                    progress = (pixels_processed / total_pixels) * 100

                    current_time = time.time()
                    if current_time - last_update_time >= 1.0:
                        last_update_time = current_time

                        cells_filled = min(xaxis * yaxis, int((progress / 100) * (xaxis * yaxis)))
                        for i in range(cells_filled):
                            row_index = i % yaxis
                            col_index = i // yaxis
                            grid[row_index][col_index] = '#'

                        grid_display = '\n'.join([''.join(row) for row in grid])
                        elapsed_time = time.time() - self.start_time
                        elapsed_time_str = time.strftime("%M:%S", time.gmtime(elapsed_time))

                        self.left_text.delete('1.0', tk.END)
                        self.left_text.insert(tk.END, f"{elapsed_time_str} [{progress:.1f}%]\n{grid_display}")
                        self.master.update_idletasks()
                        self.master.update()

        result = ""
        for color, locations in self.color_locations.items():
            result += f"{color}: {len(locations)} pixels\n"
            if len(locations) <= 10:
                for location in locations:
                    result += f"    {location}\n"

        self.left_text.delete('1.0', tk.END)
        elapsed_time = time.time() - self.start_time
        result += f"\nResolution: {self.image_size[0]}x{self.image_size[1]}"
        result += f"\nBit Depth: {len(self.bit_depth) * 8} bits\n"
        result += f"\nTime taken: {elapsed_time:.1f} s\n"
        self.left_text.delete('1.0', tk.END)
        self.left_text.insert(tk.END, result)

    def search_color(self):
        if not self.color_locations:
            self.right_text.delete('1.0', tk.END)
            self.right_text.insert(tk.END, "Analyze an image or import data first.")
            return

        color = self.color_input.get().strip().upper()
        if len(color) == 6 and all(c in '0123456789ABCDEF' for c in color):
            color = f"#{color}"
        else:
            self.right_text.delete('1.0', tk.END)
            self.right_text.insert(tk.END, "Invalid format. Hexadecimal: (XXXXXX)")
            return

        if color in self.color_locations:
            min_coord = self.min_input.get().strip()
            max_coord = self.max_input.get().strip()

            min_x, min_y = (0, 0)
            max_x, max_y = self.image_size

            if min_coord:
                try:
                    min_x, min_y = map(int, min_coord.split(','))
                except ValueError:
                    self.right_text.delete('1.0', tk.END)
                    self.right_text.insert(tk.END, "Invalid min. format: x,y")
                    return

            if max_coord:
                try:
                    max_x, max_y = map(int, max_coord.split(','))
                except ValueError:
                    self.right_text.delete('1.0', tk.END)
                    self.right_text.insert(tk.END, "Invalid max. format: x,y")
                    return

            if min_x > max_x or min_y > max_y:
                self.right_text.delete('1.0', tk.END)
                self.right_text.insert(tk.END, "Min > Max. re-enter your range.")
                return

            if self.all_coords_var.get():
                selected_coords = self.color_locations[color]
            else:
                selected_coords = [
                    (x, y) for x, y in self.color_locations[color]
                    if min_x <= x <= max_x and min_y <= y <= max_y
                ]

            if not self.all_coords_var.get() and not min_coord and not max_coord:
                limited_coords = selected_coords[:50]
            else:
                limited_coords = selected_coords

            fixed_width = 48
            width, height = self.image_size if self.image_size else (max(x for x, _ in selected_coords) + 1, max(y for _, y in selected_coords) + 1)
            grid_height = math.ceil(fixed_width * height / width)
            grid = [['-' for _ in range(fixed_width)] for _ in range(grid_height)]

            total_pixels = len(selected_coords)
            self.progress['maximum'] = total_pixels
            self.progress['value'] = 0

            start_time = time.time()
            for idx, (x, y) in enumerate(selected_coords):
                grid_x = min(fixed_width - 1, int(x * fixed_width / width))
                grid_y = min(grid_height - 1, int(y * grid_height / height))
                grid[grid_y][grid_x] = '#'

                if time.time() - start_time >= 1.0:
                    self.progress['value'] = idx + 1
                    self.master.update_idletasks()
                    self.master.update()
                    start_time = time.time()

            self.progress['value'] = total_pixels
            self.master.update_idletasks()
            self.master.update()
            grid_display = '\n'.join([''.join(row) for row in grid])

            result = f"Color: {color}\n"
            result += grid_display + "\n\n"
            result += f"occurrences: {total_pixels}\n\n"
            for location in limited_coords:
                result += f"    {location}\n"
            if len(limited_coords) < len(selected_coords):
                result += "    ...\n"

            self.right_text.delete('1.0', tk.END)
            self.right_text.insert(tk.END, result)




    def export_data(self):
        if not self.color_locations:
            self.right_text.delete('1.0', tk.END)
            self.right_text.insert(tk.END, "No data to export. analyze an image first.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pkl",
                                                filetypes=[("Pickle files", "*.pkl")])
        if file_path:
            with open(file_path, 'wb') as f:
                pickle.dump((self.color_locations, self.image_size, getattr(self, 'bit_depth', None)), f)
            
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)

            self.right_text.delete('1.0', tk.END)
            self.right_text.insert(tk.END, f"Success\n{file_path} \n{file_size_mb:.2f} MB")


    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pkl")])
        if file_path:
            with open(file_path, 'rb') as f:
                self.color_locations, self.image_size, self.bit_depth = pickle.load(f)
            
            result = ""
            for color, locations in self.color_locations.items():
                result += f"{color}: {len(locations)} pixels\n"
            if self.image_size:
                result += f"\nResolution: {self.image_size[0]}x{self.image_size[1]}"
                result += f"\nBit Depth: {len(self.bit_depth) * 8} bits\n"
            
            self.left_text.delete('1.0', tk.END)
            self.left_text.insert(tk.END, result)

            self.right_text.delete('1.0', tk.END)
            self.right_text.insert(tk.END, "Success")


if __name__ == '__main__':
    root = tk.Tk()
    app = PixelRollCall(root)
    root.mainloop()