import tkinter as tk
from tkinter import filedialog, messagebox
import os

class HexEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("HEX Editor")
        self.root.geometry("1050x720")
        self.root.configure(bg="#0f0f0f")

        # UI Styling
        self.CLR_BG = "#1e1e1e"
        self.CLR_ACCENT = "#007acc"
        self.CLR_TEXT = "#cccccc"
        self.CLR_HOVER = "#333333"
        self.CLR_SAVE = "#28a745"

        self.path = None
        self.page = 1
        self.data = []
        self.selected_idx = None

        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#1a1a1a", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(header, text="OPEN FILE", command=self.load_f, 
                  bg=self.CLR_ACCENT, fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=15, cursor="hand2").pack(side="left", padx=15)

        self.btn_save = tk.Button(header, text="SAVE CHANGES", command=self.save_to_disk, 
                  bg=self.CLR_SAVE, fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=15, cursor="hand2", state="disabled")
        self.btn_save.pack(side="left", padx=5)

        self.lbl_path = tk.Label(header, text="NO FILE LOADED", bg="#1a1a1a", 
                                 fg="#666666", font=("Segoe UI", 9))
        self.lbl_path.pack(side="right", padx=20)

        container = tk.Frame(self.root, bg="#0f0f0f")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        self.left_pane = tk.Frame(container, bg="#1e1e1e", bd=1, relief="solid")
        self.left_pane.pack(side="left", fill="both", expand=True)

        self.grid_frame = tk.Frame(self.left_pane, bg="#1e1e1e", padx=20, pady=20)
        self.grid_frame.pack(expand=True)

        self.lbls = []
        for i in range(100):
            l = tk.Label(self.grid_frame, text="--", bg="#1e1e1e", fg="#444444",
                         width=4, height=2, font=("Consolas", 12), cursor="hand2")
            l.grid(row=i//10, column=i%10, padx=2, pady=2)
            l.bind("<Button-1>", lambda e, idx=i: self.on_click(idx))
            self.lbls.append(l)

        self.side = tk.Frame(container, bg="#1e1e1e", width=280, bd=1, relief="solid")
        self.side.pack(side="right", fill="y", padx=(20, 0))
        self.side.pack_propagate(False)

        tk.Label(self.side, text="BYTE INSPECTOR", bg="#1e1e1e", fg=self.CLR_ACCENT, 
                 font=("Segoe UI", 10, "bold")).pack(pady=20)

        self.h_v, self.d_v, self.b_v = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.create_field("HEXADECIMAL (00-FF)", self.h_v)
        self.create_field("DECIMAL (0-255)", self.d_v)
        self.create_field("BINARY (8-bit)", self.b_v)

        tk.Button(self.side, text="APPLY CHANGE", command=self.apply_change,
                  bg="#444444", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", pady=10, cursor="hand2").pack(fill="x", padx=15, pady=20)

        footer = tk.Frame(self.root, bg="#0f0f0f", height=60)
        footer.pack(fill="x", side="bottom")
        
        btn_nav = {"bg": "#2d2d2d", "fg": "white", "relief": "flat", "width": 4}
        tk.Button(footer, text="←", command=self.prev, **btn_nav).pack(side="left", padx=100, pady=10)
        self.lbl_pg = tk.Label(footer, text="PAGE 0/0", bg="#0f0f0f", fg="#888888")
        self.lbl_pg.pack(side="left", expand=True)
        tk.Button(footer, text="→", command=self.next, **btn_nav).pack(side="right", padx=100, pady=10)

    def create_field(self, label, var):
        f = tk.Frame(self.side, bg="#1e1e1e", padx=15)
        f.pack(fill="x", pady=10)
        tk.Label(f, text=label, bg="#1e1e1e", fg="#888888", font=("Segoe UI", 8)).pack(anchor="w")
        e = tk.Entry(f, textvariable=var, bg="#2d2d2d", insertbackground="white",
                     fg="white", font=("Consolas", 12), relief="flat", bd=8)
        e.pack(fill="x", pady=5)

    def load_f(self):
        p = filedialog.askopenfilename()
        if p:
            self.path, self.page = p, 1
            self.lbl_path.config(text=os.path.basename(p).upper())
            self.btn_save.config(state="normal")
            self.refresh()

    def refresh(self):
        if not self.path: return
        sz = os.path.getsize(self.path)
        tot = max(1, (sz + 99) // 100)
        self.lbl_pg.config(text=f"PAGE {self.page} OF {tot}")
        
        with open(self.path, "rb") as f:
            f.seek((self.page - 1) * 100)
            self.data = list(f.read(100))

        for i, l in enumerate(self.lbls):
            if i < len(self.data):
                l.config(text=f"{self.data[i]:02X}", fg=self.CLR_TEXT)
            else:
                l.config(text="--", fg="#333333")

    def on_click(self, idx):
        if idx >= len(self.data): return
        if self.selected_idx is not None:
            self.lbls[self.selected_idx].config(bg="#1e1e1e")
        
        self.selected_idx = idx
        self.lbls[idx].config(bg=self.CLR_ACCENT, fg="white")
        
        val = self.data[idx]
        self.h_v.set(f"{val:02X}")
        self.d_v.set(str(val))
        self.b_v.set(f"{val:08b}")

    def apply_change(self):
        if self.selected_idx is None:
            messagebox.showwarning("Warning", "Select a byte first!")
            return

        try:
           
            
            h, d, b = self.h_v.get(), self.d_v.get(), self.b_v.get()
            
            new_val = int(h, 16)
            
            if 0 <= new_val <= 255:
                self.data[self.selected_idx] = new_val
                self.lbls[self.selected_idx].config(text=f"{new_val:02X}")
                # Synchronize boxes
                self.d_v.set(str(new_val))
                self.b_v.set(f"{new_val:08b}")
            else:
                raise ValueError
        except:
            messagebox.showerror("Error", "Invalid entry. Ensure value is between 0-255 (00-FF).")

    def save_to_disk(self):
        if not self.path: return
        if messagebox.askyesno("Save", "Write changes to the original file?"):
            try:
                with open(self.path, "r+b") as f:
                    f.seek((self.page - 1) * 100)
                    f.write(bytes(self.data))
                messagebox.showinfo("Success", "File updated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

    def next(self):
        self.page += 1
        self.selected_idx = None
        self.refresh()

    def prev(self):
        if self.page > 1:
            self.page -= 1
            self.selected_idx = None
            self.refresh()

if __name__ == "__main__":
    root = tk.Tk()
    app = HexEditor(root)
    root.mainloop()