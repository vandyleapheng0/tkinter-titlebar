import tkinter as tk
from ctypes import windll


class LabelButton(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **self.valid_kwargs(kwargs))
        self.rebind()

    def rebind(self):
        # button hover
        self.bind(
            "<Enter>",
            lambda event: self.config(
                bg=self.settings["hover_bg"],
                fg=self.settings["hover_fg"]
            ),
        )

        # button hover reset
        self.bind(
            "<Leave>", lambda event: self.config(
                bg=self.settings["bg"],
                fg=self.settings["fg"]
            )
        )
        # button press
        self.bind("<Button-1>", self.settings["command"])
        self.bind(
            "<Button-1>",
            lambda event: self.config(
                bg=self.settings["press_bg"],
                fg=self.settings["press_fg"]
            ),
            add=True,
        )

    def valid_kwargs(self, kwargs):
        self.settings = {
            "bg": "#333",
            "fg": "#fff",
            "command": None,
            "hover_bg": "#555",
            "hover_fg": "#fff",
            "press_bg": "#777",
            "press_fg": "#fff",
        }
        self.settings.update(kwargs)
        kwargs["bg"] = kwargs.get("bg", self.settings["bg"])
        kwargs["fg"] = kwargs.get("fg", self.settings["fg"])
        for setting in ("hover_bg", "hover_fg", "press_bg", "press_fg", "command"):
            if setting in kwargs:
                del kwargs[setting]
        return kwargs


class TitleTk(tk.Tk):
    """"Main window with darkmode titlebar widget pack on the top"""

    def __init__(self):
        super().__init__()
        self.overrideredirect(True)

        self.settings = {"bg": "#111", "fg": "#fff"}
        self.maximized = False
        # self.minimized = False
        self.resizable_values = (True, True)
        self.minsize_values = (120, 30)
        self.maxsize_values = (self.winfo_screenwidth(), self.winfo_screenheight())
        self.restore_down_image = tk.PhotoImage(file="images/restore_down_white15.png")

        self.titlebar = tk.Frame(self, bg=self.settings["bg"], height=30)
        self.titlebar.pack(fill="x")
        self.titlebar.pack_propagate(False)

        self.title_ = tk.Label(
            self.titlebar,
            text="Tk",
            **self.settings,
            font=(None, 10)
        )
        self.close = LabelButton(
            self.titlebar,
            command=lambda event: self.quit(),
            text="×",
            hover_bg="#da2e25",
            font=(None, 20),
            **self.settings,
        )
        self.maximize = LabelButton(
            self.titlebar,
            text="☐",
            font=(None, 11),
            **self.settings,
            command=self.maximize_window,
        )
        self.minimize = LabelButton(
            self.titlebar,
            text="—",
            font=(None, 12),
            **self.settings,
            command=self.iconify,
        )

        self.title_.pack(side="left", padx=(5, 0))
        self.close.pack(side="right", fill="y", ipadx=4)
        self.maximize.pack(side="right", fill="y", ipadx=4)
        self.minimize.pack(side="right", fill="y", ipadx=4)

        self.title_bind("<B1-Motion>", self.move_window)
        self.title_bind("<Double-Button-1>", self.maximize_window)
        self.bind("<Motion>", self.get_resize_info)
        self.bind("<Button-1>", self.record_movement)
        self.bind("<B1-Motion>", self.resize_window)
        self.bind("<FocusIn>", self.deiconify, add="+")
        # self.after(10, lambda: self.set_appwindow())
        self.add_to_taskbar()

    def add_to_taskbar(self):
        self.after(10, lambda: self.set_appwindow())

    def config_titlebar(self, light_theme=False, bg=None, fg=None):
        """toggle light_theme or changing the fg: foreground or bg: background"""
        if not light_theme:
            bg = bg or self.settings["bg"]
            fg = fg or self.settings["fg"]
        else:
            bg = bg or "white",
            fg = fg or "black"
            settings = {
                "hover_bg": "#ccc",
                "hover_fg": fg,
                "press_bg": "#aaa",
                "press_fg": fg,
            }
        if fg not in ("white", "black"):
            raise ValueError("foreground can only be white or black")

        self.titlebar.config(bg=bg)
        for widget in self.titlebar.pack_slaves():
            if hasattr(widget, "settings"):
                widget.settings.update(bg=bg, fg=fg)
                if light_theme:
                    widget.settings.update(settings)
                    widget.rebind()
            widget.config(bg=bg, fg=fg)

        if light_theme:
            self.close.settings["hover_bg"] = "#da2e25"
            self.close.rebind()

        if fg == "black":
            self.restore_down_image = tk.PhotoImage(file="images/restore_down_dark15.png")
        elif fg:
            self.resize_down_image = tk.PhotoImage(file="images/restore_down_white15.png")

    def maximize_window(self, event=None):
        if sum(self.resizable_values) == 2:
            if not self.maximized:
                self.maximized = True
                self.maximize.config(text="", image=self.restore_down_image)
                self.old_geometry = self.geometry()
                self.geometry("%ix%i+0+0" % (self.winfo_screenwidth(), self.winfo_screenheight()))
            else:
                self.maximized = False
                self.maximize.config(text="☐", image="")
                self.geometry(self.old_geometry)

    def iconify(self, event=None):
        self.attributes("-alpha", 0)

    def deiconify(self, event=None):
        if event.widget == self:
            self.focus()
            self.attributes("-alpha", 1)

    def record_movement(self, event=None):
        self.last_movement = (event.x_root, event.y_root)

    def title_bind(self, key, command, add=False):
        self.title_.bind(key, command, add=add)
        self.titlebar.bind(key, command, add=add)

    def title(self, text):
        super().title(text)
        self.title_.config(text=text)

    def move_window(self, event=None):
        # record the last_movement
        # (next movement) calculate the different and move the main-window
        if not (
            self.maximized
            or self.resize_top
            or self.resize_bottom
            or self.resize_right
            or self.resize_left
        ):
            self.geometry(
                "+{}+{}".format(
                    self.winfo_x() + event.x_root - self.last_movement[0],
                    self.winfo_y() + event.y_root - self.last_movement[1],
                )
            )
            self.last_movement = (event.x_root, event.y_root)

    def set_appwindow(self):
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080

        hwnd = windll.user32.GetParent(self.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

        self.wm_withdraw()
        self.after(10, lambda: self.wm_deiconify())

    def resizable(self, x, y):
        self.resizable_values = (x, y)

    def maxsize(self, width, height):
        self.maxsize_values = (width, height)
        self.update()
        if self.winfo_width() > width:
            self.geometry(f"{width}x{self.winfo_height()}")

        self.update()
        if self.winfo_height() > height:
            self.geometry(f"{self.winfo_width()}x{height}")

    def minsize(self, width, height):
        self.minsize_values = (width, height)
        self.update()
        if self.winfo_width() < width:
            self.geometry(f"{width}x{self.winfo_height()}")

        self.update()
        if self.winfo_height() < height:
            self.geometry(f"{self.winfo_width()}x{height}")

    def get_resize_info(self, event=None):
        """Get the resize info and change the cursor style to indecate user that widget is resizable"""

        self.resize_left = event.x_root - self.winfo_x() < 5
        self.resize_right = event.x_root > self.winfo_x() + self.winfo_width() - 5

        self.resize_top = event.y_root - self.winfo_y() < 5
        self.resize_bottom = event.y_root > self.winfo_y() + self.winfo_height() - 5

        if not self.resizable_values[1]:
            self.resize_left = self.resize_right = False

        if not self.resizable_values[0]:
            self.resize_top = self.resize_bottom = False

        if self.resize_left or self.resize_right:
            self.config(cursor="sb_h_double_arrow")
        elif self.resize_top or self.resize_bottom:
            self.config(cursor="sb_v_double_arrow")
        else:
            self.config(cursor="arrow")

    def resize_window(self, event=None):
        # We need last_movement to calculate width and height to resize
        # resizing: "bottom" and "right" are the same. Calculate the different and add to geometry
        # resizing: "top" and "left" the same above, but we need to MOVE and RESIZE widget along with cursor
        resize_x = self.maxsize_values[0] >= self.winfo_width() >= self.minsize_values[0]
        resize_y = self.maxsize_values[1] >= self.winfo_height() >= self.minsize_values[1]

        try:
            if self.resize_bottom and resize_y:
                self.geometry(
                    "{}x{}".format(
                        self.winfo_width(),
                        self.winfo_height() + event.y_root - self.last_movement[1],
                    )
                )
            elif self.resize_top and resize_y:
                self.geometry(
                    "{}x{}+{}+{}".format(
                        self.winfo_width(),
                        self.winfo_height() + self.last_movement[1] - event.y_root,
                        self.winfo_x(),
                        self.winfo_y() + event.y_root - self.last_movement[1],
                    )
                )
            elif self.resize_left and resize_x:
                self.geometry(
                    "{}x{}+{}+{}".format(
                        self.winfo_width() + self.last_movement[0] - event.x_root,
                        self.winfo_height(),
                        self.winfo_x() + event.x_root - self.last_movement[0],
                        self.winfo_y(),
                    )
                )
            elif self.resize_right and resize_x:
                self.geometry(
                    "{}x{}".format(
                        self.winfo_width() + event.x_root - self.last_movement[0],
                        self.winfo_height(),
                    )
                )
        except tk.TclError:
            print("TclError")

        self.last_movement = (event.x_root, event.y_root)
        if not resize_x or not resize_y:
            self.maxsize(*self.maxsize_values)
            self.minsize(*self.minsize_values)


if __name__ == "__main__":
    # root = TitleTk()
    # root.geometry("500x400+800+100")
    # root.attributes("-topmost", 1)
    # root.config(bg="#333")
    # label = tk.Label(root, text="hello world".upper())
    # label.pack(ipadx=5, ipady=5)
    # root.mainloop()

    root = TitleTk()
    root.title("Tkinter")
    root.geometry("400x400")
    # root.resizable(0, 1)
    # root.maxsize(400, 300)
    # root.minsize(300, 200)
    # root.config_titlebar(light_theme=True, bg="grey")
    window = tk.Frame(root, bg="#333")
    window.pack(fill="both", expand=True)
    label = tk.Label(window, text="hello world".upper())
    label.pack(ipadx=5, ipady=5)
    root.mainloop()
