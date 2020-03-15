#! /usr/bin/python3
#
# Credits: Madpixel for the Minecraft font - https://www.dafont.com/minecrafter.font

import json
import os
import platform
import subprocess
from random import randint
from time import sleep
from tkinter import Tk, Frame, Canvas, ttk, PhotoImage
from typing import Optional, Dict, List

import PIL
import PIL.Image
import PIL.ImageTk
from pmlauncher import mlogin, pml
from pmlauncher.mprofileinfo import getProfilesFromLocal
from pmlauncher.pycraft import authentication
from pmlauncher.pycraft.exceptions import YggdrasilError

if platform.system().lower() == "windows":
    DATA_FOLDER = f"/Users/{os.getlogin()}/AppData/Roaming/QMinecraft/"
else:
    print("This program is currently Windows only")
    print("")
    input("Press ENTER to close this window")
    exit()

COL_PLAY_BTN = "#008944"
REL_PLAY_BTN = "raised"
BD_PLAY_BTN = 5

TREEVIEW_BG = "#7f7f7f"
TREEVIEW_FG = "#9f9f9f"
TREEVIEW_SEL_BG = "gold"
TREEVIEW_SEL_FG = "white"

BUTTON_BG = "#7f7f7f"
BUTTON_BG_FOC = "gold"
BUTTON_BG_DIS = "#5c5c5c"
BUTTON_FG = "#a7a7a7"
BUTTON_FG_FOC = "white"
BUTTON_FG_DIS = "#7f7f7f"
BUTTON_BD_COL = "gold"
BUTTON_RELIEF = "flat"
BUTTON_BD_WID = 0

ENTRY_BG = "#7f7f7f"
ENTRY_BG_FOC = "gold"
ENTRY_BG_DIS = "#5c5c5c"
ENTRY_FG = "#a7a7a7"
ENTRY_FG_FOC = "white"
ENTRY_FG_DIS = "#7f7f7f"
ENTRY_BD_COL = "gold"
ENTRY_RELIEF = "flat"
ENTRY_BD_WID = 0
ENTRY_SEL_BG = "gold"
ENTRY_SEL_BG_FOC = "#fce58a"
ENTRY_SEL_BG_DIS = "#ec9712"
ENTRY_SEL_FG = "gold"
ENTRY_SEL_FG_FOC = "white"
ENTRY_SEL_FG_DIS = "#7f7f7f"

LAUNCHER_CFG = os.path.join(DATA_FOLDER, "launchercfg.json")

from PIL import Image, ImageTk, ImageDraw, ImageFont


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class CustomScrollbar(Canvas):
    def __init__(self, parent, **kwargs):
        self.command = kwargs.pop("command", None)
        kw = kwargs.copy()
        if "fg" in kw.keys():
            del kw["fg"]
        Canvas.__init__(self, parent, **kw, highlightthickness=0, border=0, bd=0)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"

        # coordinates are irrelevant; they will be recomputed
        # in the 'set' method\
        self.old_y = 0
        self._id = self.create_rectangle(0, 0, 1, 1, fill=kwargs["fg"], outline=kwargs["fg"], tags=("thumb",))
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def configure(self, cnf=None, **kwargs):
        command = kwargs.pop("command", None)
        self.command = command if command is not None else self.command
        kw = kwargs.copy()
        if "fg" in kw.keys():
            del kw["fg"]
        super().configure(**kw, highlightthickness=0, border=0, bd=0)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"
        self.itemconfig(self._id, fill=kwargs["fg"], outline=kwargs["fg"])

    def config(self, cnf=None, **kwargs):
        self.configure(cnf, **kwargs)

    def redraw(self, event):
        # The command is presumably the `yview` method of a widget.
        # When called without any arguments it will return fractions
        # which we can pass to the `set` command.
        self.set(*self.command())

    def set(self, first, last):
        first = float(first)
        last = float(last)
        height = self.winfo_height()
        x0 = 2
        x1 = self.winfo_width() - 2
        y0 = max(int(height * first), 0)
        y1 = min(int(height * last), height)
        self._x0 = x0
        self._x1 = x1
        self._y0 = y0
        self._y1 = y1

        self.coords("thumb", x0, y0, x1, y1)

    def on_press(self, event):
        self.bind("<Motion>", self.on_click)
        self.pressed_y = event.y
        self.on_click(event)

    def on_release(self, event):
        self.unbind("<Motion>")

    def on_click(self, event):
        y = event.y / self.winfo_height()
        y0 = self._y0
        y1 = self._y1
        a = y + ((y1 - y0) / -(self.winfo_height() * 2))
        self.command("moveto", a)


# noinspection PyUnusedLocal
class ScrolledWindow(Frame):
    """
    1. Master widget gets scrollbars and a canvas. Scrollbars are connected
    to canvas scrollregion.

    2. self.scrollwindow is created and inserted into canvas

    Usage Guideline:
    Assign any widgets as children of <ScrolledWindow instance>.scrollwindow
    to get them inserted into canvas

    __init__(self, parent, canv_w = 400, canv_h = 400, *args, **kwargs)
    docstring:
    Parent = master of scrolled window
    canv_w - width of canvas
    canv_h - height of canvas

    """

    def __init__(self, parent, canv_w=400, canv_h=400, expand=False, fill=None, height=None, width=None, *args,
                 scrollcommand=lambda: None, scrollbarbg=None, scrollbarfg="darkgray", **kwargs):
        """Parent = master of scrolled window
        canv_w - width of canvas
        canv_h - height of canvas

       """
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.scrollCommand = scrollcommand

        # creating a scrollbars

        if width is None:
            __width = 0
        else:
            __width = width

        if height is None:
            __height = 0
        else:
            __height = width

        self.canv = Canvas(self.parent, bg='#FFFFFF', width=canv_w, height=canv_h,
                           scrollregion=(0, 0, __width, __height), highlightthickness=0)

        self.vbar = CustomScrollbar(self.parent, width=10, command=self.canv.yview, bg=scrollbarbg, fg=scrollbarfg)
        self.canv.configure(yscrollcommand=self.vbar.set)

        self.vbar.pack(side="right", fill="y")
        self.canv.pack(side="left", fill=fill, expand=expand)

        # creating a frame to inserto to canvas
        self.scrollwindow = Frame(self.parent, height=height, width=width)

        self.scrollwindow2 = self.canv.create_window(0, 0, window=self.scrollwindow, anchor='nw', height=height,
                                                     width=width)

        self.canv.config(  # xscrollcommand=self.hbar.set,
            yscrollcommand=self.vbar.set,
            scrollregion=(0, 0, canv_h, canv_w))

        self.scrollwindow.bind('<Configure>', self._configure_window)
        self.scrollwindow.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollwindow.bind('<Leave>', self._unbound_to_mousewheel)

        return

    def _bound_to_mousewheel(self, event):
        self.canv.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canv.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # self.scrollCommand(int(-1 * (event.delta / 120)), self.scrollwindow.winfo_reqheight(), self.vbar.get(),
        # self.vbar)

    def _configure_window(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.scrollwindow.winfo_reqwidth(), self.scrollwindow.winfo_reqheight() + 1)
        self.canv.config(scrollregion='0 0 %s %s' % size)
        # if self.scrollwindow.winfo_reqwidth() != self.canv.winfo_width():
        #     # update the canvas's width to fit the inner frame
        #     # self.canv.config(width=self.scrollwindow.winfo_reqwidth())
        # if self.scrollwindow.winfo_reqheight() != self.canv.winfo_height():
        #     # update the canvas's width to fit the inner frame
        #     # self.canv.config(height=self.scrollwindow.winfo_reqheight())


# noinspection PyUnboundLocalVariable
def load_auth_tokens(file_path=os.path.join(DATA_FOLDER, "launchercfg.json")):
    """
    Loads authentication tokens.

    :param file_path:
    :return:
    """

    if os.path.exists(file_path):
        with open(file_path) as file:
            try:
                return json.load(file)
            except ValueError:
                pass
    return {}


def save_auth_tokens(auth_tokens, file_path=os.path.join(DATA_FOLDER, "launchercfg.json")):
    """
    Saves authentication tokens.

    :param auth_tokens:
    :param file_path:
    :return:
    """

    exists = os.path.exists(file_path)
    with open(file_path, 'w') as file:
        json.dump(auth_tokens, file, indent=4)


class CustomFontButton(ttk.Button):
    def __init__(self, master, text, width=None, foreground="black", truetype_font=None, font_path=None, size=None,
                 **kwargs):
        """
        Custom font for buttons.

        :param master:
        :param text:
        :param width:
        :param foreground:
        :param truetype_font:
        :param font_path:
        :param size:
        :param kwargs:
        """

        if truetype_font is None:
            if font_path is None:
                raise ValueError("Font path can't be None")

            # Initialize font
            truetype_font = ImageFont.truetype(font_path, size)

        w, h = truetype_font.getsize(text)
        # w, h = draw
        W = width + 20
        H = h + 20
        #
        # if width > width_2:
        #     width_ = width
        # else:
        #     width_ = width_2
        # print(width_2, width)

        image = Image.new("RGBA", (W, H), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # print(width)
        # print(width / 2)

        draw.text((((W - w) / 2) + 1, ((H - h) / 2) + 2), text, font=truetype_font, fill="#00000037", align="center")
        draw.text(((W - w) / 2, (H - h) / 2), text, font=truetype_font, fill=foreground)

        self._photoimage = ImageTk.PhotoImage(image)
        ttk.Button.__init__(self, master, image=self._photoimage, **kwargs)

        self.truetype_font = truetype_font
        self.font_path = font_path
        self.fsize = size
        self.text = text
        self.foreground = foreground
        self.width = width

    def configure(self, cnf=None, **kw):
        truetype_font = kw.pop("truetype_font", None)
        font_path = kw.pop("font_path", None)
        size = kw.pop("fsize", None)
        text = kw.pop("text", None)
        foreground = kw.pop("foreground", None)
        width = kw.pop("width", None)
        if foreground is None:
            foreground = kw.pop("fg", None)

        if (truetype_font is None) and (font_path is None) and (size is None) and (text is None) and (
                foreground is None) and (width is None):
            changed = False
        else:
            changed = True

        if truetype_font is None:
            truetype_font = self.truetype_font
        if font_path is None:
            font_path = self.font_path
        if size is None:
            size = self.fsize
        if text is None:
            text = self.text
        if foreground is None:
            foreground = self.foreground
        if width is None:
            width = self.width

        if changed:
            # Initialize font
            truetype_font = ImageFont.truetype(font_path, size)
            w, h = truetype_font.getsize(text)
        else:
            w, h = truetype_font.getsize(text)

        # print(width, width_2)
        # exit()

        if changed:
            # w, h = draw
            W = width + 20
            H = h + 20
            image = Image.new("RGBA", (W, H), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            # print(width_2, width)

            draw.text(((W - w) / 2, ((H - h) / 2) - 2), text, font=truetype_font, fill=0x0000007f, align="center")
            draw.text(((W - w) / 2, (H - h) / 2), text, font=truetype_font, fill=foreground, align="center")

            self._photoimage = ImageTk.PhotoImage(image)
            super().configure(cnf, image=self._photoimage, **kw)

        else:
            super().configure(cnf, **kw)

        self.truetype_font = truetype_font
        self.font_path = font_path
        self.fsize = size
        self.text = text
        self.foreground = foreground

    def config(self, cnf=None, **kw):
        self.configure(cnf, **kw)


class LauncherConfig(object):
    def __init__(self, token):
        """
        Not Implemented!

        :param token:
        """

        pass


def get_resized_img(img, video_size):
    """
    Get resized image.

    :param img:
    :param video_size:
    :return:
    """

    width, height = video_size  # these are the MAX dimensions
    video_ratio = width / height
    img_ratio = img.size[0] / img.size[1]
    if video_ratio >= 1:  # the video is wide
        if img_ratio <= video_ratio:  # image is not wide enough
            height_new = int(width / img_ratio)
            size_new = width, height_new
        else:  # image is wider than video
            width_new = int(height * img_ratio)
            size_new = width_new, height
    else:  # the video is tall
        if img_ratio >= video_ratio:  # image is not tall enough
            width_new = int(height * img_ratio)
            size_new = width_new, height
        else:  # image is taller than video
            height_new = int(width / img_ratio)
            size_new = width, height_new
    return img.resize(size_new, resample=Image.LANCZOS)


def data_path(path: str):
    """
    Get a file or folder path from data path.

    :param path:
    :return:
    """

    return os.path.join(DATA_FOLDER, path)


class QMinecraftWindow(Tk):
    def __init__(self):
        # Initialize account file path
        accountfile_path = data_path("account.json")
        print(accountfile_path)

        def makefile():
            """
            Look on QTwitchWindow for makefile() doc.

            :return:
            """
            from tkinter.messagebox import showinfo
            root = Tk()
            root.withdraw()

            showinfo("Note", f"""Account file is corrupt or doesn't exists!
This program will create and open the file for you.
Then replace <username> with your username or email (use your email when username doen't work).
And replace <password> with your password.

When all this is done, reopen the launcher. 
If prompted choose an program to open it, like Notepad (Windows) or Gedit (Ubuntu)""", master=root)
            with open(accountfile_path, "w+") as file_:
                file_.write(json.dumps({"username": "<username>", "password": "<password>"}, indent=4, sort_keys=True))
                file_.close()
            sleep(2)
            if (platform.system().lower() == "unix") or (platform.system().lower() == "linux"):
                os.startfile(accountfile_path)
            elif platform.system().lower() == "windows":
                os.startfile("C:\\" + accountfile_path.replace("/", "\\"))
                # print(f"notepad \"C:" + accountfile_path.replace("/", "\\") + "\""
                #           if " " in accountfile_path else
                #           f"notepad C:" + accountfile_path.replace('/', "\\"))
                # os.system(f"notepad \"C:" + accountfile_path.replace("/", "\\") + "\""
                #           if " " in accountfile_path else
                #           f"notepad C:" + accountfile_path.replace('/', "\\"))
            exit()

        if os.path.exists(accountfile_path):
            try:
                with open(accountfile_path) as file:
                    self.launcherData = json.JSONDecoder().decode(file.read())
            except json.JSONDecodeError:
                makefile()
        else:
            makefile()

        # Initialize window
        super(QMinecraftWindow, self).__init__()

        # Configure window
        self.title("QMinecraft Launcher")
        self.geometry("900x506")
        self.minsize(614, 400)

        pml.initialize("/")

        # Makes closing the window, kills the process (or program)
        self.wm_protocol("WM_DELETE_WINDOW", lambda: os.kill(os.getpid(), 0))

        print("Reading launcher config")

        # Reading launcher configuration.
        tokens = {}
        if os.path.exists(LAUNCHER_CFG):
            with open(os.path.join(LAUNCHER_CFG)) as file:
                self.launcherConfig = json.JSONDecoder().decode(file.read())
                # print(self.launcherConfig["tokens"])
            if "tokens" in self.launcherConfig.keys():
                tokens = self.launcherConfig["tokens"]
        else:
            print("Launcher config doen't exists, creating a new one...")
            self.launcherConfig = {}

        # Update launcher config keys if non-existend
        if "fullscreen" not in self.launcherConfig.keys():
            self.launcherConfig["fullscreen"] = False
        if "tokens" not in self.launcherConfig.keys():
            self.launcherConfig["tokens"] = {}
            # print(self.launcherConfig["tokens"])
        if "profilename" not in self.launcherConfig.keys():
            self.launcherConfig["profilename"] = f"player{randint(100, 999)}"
        if "uuid" not in self.launcherConfig.keys():
            self.launcherConfig["uuid"] = None
        self.save_launchercfg()

        # Get local versions.
        self.profiles = []
        versions_dir = os.path.join(DATA_FOLDER, "versions")
        for item in os.listdir(os.path.join(DATA_FOLDER, "versions")):
            _item_dir = os.path.join(versions_dir, item)
            if os.path.isdir(_item_dir):
                if os.path.exists(os.path.join(_item_dir, item + ".jar")):
                    if os.path.exists(os.path.join(_item_dir, item + ".json")):
                        self.profiles.append(item)

        # print(self.profiles)

        # return self.auth_token

        print("Getting versions")

        # Getting versions
        from requests.exceptions import ConnectionError

        try:
            self.profiles = pml.updateProfiles()
        except ConnectionError:
            self.profiles = []
        self.username = self.launcherData["username"]
        self.password = self.launcherData["password"]
        self.auth_token: Optional[authentication.AuthenticationToken] = None

        # Initialize game folder
        pml.initialize(DATA_FOLDER)

        # Initialize versions
        try:
            _temp_prof0001 = pml.updateProfiles()
        except ConnectionError:
            _temp0003 = getProfilesFromLocal()
            _temp0004 = []
            for p in _temp0003:
                if "forge" in p.name:
                    pass
                elif "fabric" in p.name:
                    pass
                else:
                    _temp0004.append(p)

            self.profiles = _temp0004

            _temp_prof0001 = getProfilesFromLocal()

        _temp_prof0002 = []
        _temp_profnames = [p.name for p in self.profiles]

        for profile in _temp_prof0001:
            if profile.name not in _temp_profnames:
                _temp_prof0002.append(profile)

        _temp_prof0002.extend(self.profiles)
        self.profiles = _temp_prof0002

        # Define selected version
        self.selVersion = self.profiles[0].name

        # Gets authentication token.
        if self.auth_token is None:
            token = tokens.get(self.username.lower(), None)
            print("Have already a token" if token is not None else "Haven't already a token")
            if token is not None:
                self.auth_token = authentication.AuthenticationToken(
                    username=self.username,
                    access_token=token['accessToken'],
                    client_token=token['clientToken'])
            self.online = True
        # print(self.auth_token)
        if self.auth_token is not None:
            print("Refreshing token...")
            try:
                self.auth_token.refresh()
                self.online = True
            except YggdrasilError:
                print("Refreshing failed")
                self.auth_token = None
                self.online = True
            except ConnectionError:
                print("No internet connection")
                self.auth_token = None
                self.online = False
        if (self.auth_token is None) and self.online:
            print("Create a new token...")
            try:
                self.auth_token = authentication.AuthenticationToken()
                self.auth_token.authenticate(self.username, self.password)
            except YggdrasilError:
                print("Creating a token failed")
                self.auth_token = None
                raise
            except ConnectionError:
                self.online = False

        # Saves authentication tokens.
        self._authenticate_save(tokens=tokens)

        # self.auth_token = None

        # Creates authentication session for Minecraft account.
        if self.auth_token is None:
            print("Can't find a token, using default player account")
            self.session = mlogin.session()  # set session object
            self.session.username = self.launcherConfig["profilename"]
            # noinspection PyTypeChecker
            # print(self.launcherConfig["tokens"])
            self.session.access_token = self.launcherConfig["tokens"][self.username]["accessToken"]
            if self.launcherConfig["uuid"] is not None:
                self.session.uuid = self.launcherConfig["uuid"]
        else:
            print(f"Login successful, profile name: {self.auth_token.profile.name}")
            self.session = mlogin.session()  # set session object
            self.session.username = self.auth_token.profile.name
            self.session.uuid = self.auth_token.profile.id_
            self.session.access_token = self.auth_token.access_token

        # Define profile name
        self.profilename = self.session.username

        # Update profile name and UUID.
        self.launcherConfig["profilename"] = self.profilename
        self.launcherConfig["uuid"] = self.session.uuid
        self.save_launchercfg()

        # Setup theme
        self.setup_theme()

        print("Setup UI...")

        # Initialize icons for the modloader and Minecraft
        self.iconRift = PhotoImage(file="icons/rift.png")
        self.iconForge = PhotoImage(file="icons/forge.png")
        self.iconFabric = PhotoImage(file="icons/fabric.png")
        self.iconClassic = PhotoImage(file="icons/classic.png")
        self.iconOptifine = PhotoImage(file="icons/optifine.png")
        self.iconMinecraft = PhotoImage(file="icons/minecraft.png")

        # Initialize colors for the modloader and Minecraft
        self.colorRift = "#D7D7D7"
        self.colorForge = "#3E5482"
        self.colorFabric = "#BFB49C"
        self.colorClassic = "#7A7A7A"
        self.colorOptifine = "#AD393B"
        self.colorMinecraft = "#A8744F"

        self._backgroundImage: PIL.Image.Image = PIL.Image.open("background.png")
        self._tmp_img_tk = PIL.ImageTk.PhotoImage(self._backgroundImage)

        self.rootFrame = Frame(self, bg="#282828")

        # Version list width
        vlw = 300

        # Initialize left panel
        self.leftPanel = Frame(self.rootFrame, height=75, width=vlw)

        # Initialize user info and status
        self.userFrame = Canvas(self.leftPanel, bg="#282828", height=75, highlightthickness=0, width=vlw)
        self.userNameText = self.userFrame.create_text(10, 10, text=self.session.username,
                                                       font=("helvetica", 10, "bold"), fill="white", anchor="nw")
        self.userStatusIcon = self.userFrame.create_rectangle(11, 41, 19, 49,
                                                              fill="#008542" if self.auth_token is not None else "#434343",
                                                              outline=COL_PLAY_BTN if self.auth_token is not None else "#434343")
        self.userStatusText = self.userFrame.create_text(25, 45,
                                                         text="Online" if self.auth_token is not None else "Offline",
                                                         fill="#a5a5a5", anchor="w", font=("helvetica", 10))
        self.userFrame.pack(fill="x")

        # Slots frame.
        self.sPanel = Frame(self.leftPanel, height=self.rootFrame.winfo_height() - 100, width=vlw)
        self.sPanel.pack(side="left", fill="y")

        # Scrollwindow for the slots frame
        self.sw = ScrolledWindow(self.sPanel, vlw, self.winfo_height() + 0, expand=True, fill="both")

        # Configurate the canvas from the scrollwindow
        self.canv = self.sw.canv
        self.canv.config(bg="#1e1e1e")
        self.sw.vbar.config(bg="#1e1e1e", fg="#353535")

        # Initialize frames.
        self.frame_sw = self.sw.scrollwindow
        self.frames = []

        # Defining the list of widgets
        self._id = {}
        self.index = {}
        self.canvass = []
        self.buttons = []

        # Initialize canvas selected and hovered data.
        self.oldSelected: Optional[Canvas] = None
        self.selectedCanvas: Optional[Canvas] = None
        self._hoverCanvasOld: Optional[Canvas] = None
        self._hoverCanvas: Optional[Canvas] = None

        # Define the index variable.
        i = 0

        # Initialize colors, canvas and text.
        self.cColors: Dict[Canvas, str] = {}
        self.tColors: Dict[Canvas, List[str]] = {}

        # Creates items in the versions menu.
        for profile in self.profiles:
            self.frames.append(Frame(self.frame_sw, height=32, width=vlw, bd=0))
            self.canvass.append(Canvas(self.frames[-1], height=32, width=vlw, bg="#1e1e1e", highlightthickness=0, bd=0))
            self.canvass[-1].pack()
            self._id[self.canvass[-1]] = {}
            if "rift" in profile.name.lower():
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconRift,
                                                                                   anchor="nw")
                color = self.colorRift
            elif "forge" in profile.name.lower():
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconForge,
                                                                                   anchor="nw")
                color = self.colorForge
            elif "fabric" in profile.name.lower():
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconFabric,
                                                                                   anchor="nw")
                color = self.colorFabric
            elif "optifine" in profile.name.lower():
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconOptifine,
                                                                                   anchor="nw")
                color = self.colorOptifine
            elif profile.name.startswith("a") or profile.name.startswith("b") or profile.name.startswith(
                    "c") or profile.name.startswith("rd") or profile.name.startswith("inf"):
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconClassic,
                                                                                   anchor="nw")
                color = self.colorClassic
            else:
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconMinecraft,
                                                                                   anchor="nw")
                color = self.colorMinecraft
            if profile.name not in os.listdir(versions_dir):
                t_color = ["#434343", "#7f7f7f", "#a5a5a5"]
                color = "#434343"
            else:
                t_color = ["#a5a5a5", "#ffffff", "#ffffff"]
            self._id[self.canvass[-1]]["Title"] = self.canvass[-1].create_text(37, 15, text=profile.name,
                                                                               fill=t_color[0], anchor="w",
                                                                               font=("helvetica", 11))
            self.cColors[self.canvass[-1]] = color
            self.tColors[self.canvass[-1]] = t_color
            self.canvass[-1].bind("<ButtonRelease-1>",
                                  lambda event, v=profile.name, c=self.canvass[-1]: self.select_version(c, v))
            self.canvass[-1].bind("<Double-Button-1>", lambda event, v=profile.name: self.play_version(v))
            self.canvass[-1].bind("<Motion>", lambda event, c=self.canvass[-1]: self._on_canv_motion(c))
            self.canvass[-1].bind("<Leave>", lambda event, c=self.canvass[-1]: self._on_canv_leave(c))
            self.index[self.canvass[-1]] = i
            self.frames[-1].pack(side="top")

            i += 1

        self.leftPanel.pack(side="left", fill="y")

        self.rightPanels = Frame(self.rootFrame, bg="#282828")
        self.canvas = Canvas(self.rightPanels, bg="#282828", highlightthickness=0)
        self.background = self.canvas.create_image(0, 0, anchor="nw", image=self._tmp_img_tk)
        self.canvas.pack(fill="both", expand=True)
        self.bottomPanel = Frame(self.rightPanels, bg="#262626", height=60)
        self.playBtn = CustomFontButton(self.rightPanels, width=200,
                                        text="PLAY" if self.auth_token is not None else "PLAY OFFLINE",
                                        font_path="Minecrafter.Reg.ttf", foreground="white", size=24, command=self.play)
        self.playBtn.place(x=self.bottomPanel.winfo_width() / 2, y=self.bottomPanel.winfo_y() + 10, anchor="n")
        self.bottomPanel.pack(side="bottom", fill="x")
        self.rightPanels.pack(side="right", fill="both", expand=True)
        self.rootFrame.pack(side="left", fill="both", expand=True)

        # Event bindings
        self.canvas.bind("<Configure>", self.configure_event)
        self.bottomPanel.bind("<Configure>", self.on_bottompanel_configure)

        self.wm_attributes("-fullscreen", self.launcherConfig["fullscreen"])

    def _on_canv_leave(self, hover_canvas):
        """
        Updates canvas when the cursor is leaving the menu item region.

        :param hover_canvas:
        :return:
        """

        if self._hoverCanvasOld is not None:
            if self.selectedCanvas != self._hoverCanvasOld:
                self._hoverCanvasOld.config(bg="#1e1e1e")
                self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Title"],
                                                fill=self.tColors[self._hoverCanvasOld][0], font=("helvetica", 11))
            else:
                self._hoverCanvasOld.config(bg=self.cColors[self._hoverCanvasOld])
                self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Title"],
                                                fill=self.tColors[self._hoverCanvasOld][2], font=("helvetica", 11))
        self._hoverCanvasOld = None

    def _on_canv_motion(self, hover_canvas):
        """
        Updates menu item hover color, and the old hover menu item color.

        :param hover_canvas:
        :return:
        """

        if self._hoverCanvasOld == hover_canvas:
            return
        if self._hoverCanvasOld is not None:
            if self.selectedCanvas != self._hoverCanvasOld:
                self._hoverCanvasOld.config(bg="#1e1e1e")
                self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Title"],
                                                fill=self.tColors[self._hoverCanvasOld][0], font=("helvetica", 11))
            else:
                self._hoverCanvasOld.config(bg=self.cColors[self._hoverCanvasOld])
                self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Title"],
                                                fill=self.tColors[self._hoverCanvasOld][2], font=("helvetica", 11))
        self._hoverCanvasOld = hover_canvas

        if hover_canvas != self.selectedCanvas:
            hover_canvas.config(bg="#353535")
            hover_canvas.itemconfig(self._id[hover_canvas]["Title"], fill=self.tColors[hover_canvas][1],
                                    font=("helvetica", 11, "bold"))
        else:
            hover_canvas.config(bg=self.cColors[hover_canvas])
            hover_canvas.itemconfig(self._id[hover_canvas]["Title"], fill=self.tColors[hover_canvas][2],
                                    font=("helvetica", 11, "bold"))
        self._hoverCanvas = hover_canvas

    def _on_canv_lclick(self, c: Canvas):
        """
        Event for clicking on an item in the versions menu.

        :param c:
        :return:
        """

        self.selectedCanvas = c

    def select_version(self, c: Canvas, version):
        """
        Update canvas colors, and sets selected version.

        :param c:
        :param version:
        :return:
        """

        if self.oldSelected is not None:
            self.oldSelected.config(bg="#1e1e1e")
            self.oldSelected.itemconfig(self._id[self.oldSelected]["Title"], fill=self.tColors[self.oldSelected][0],
                                        font=("helvetica", 11))
        self.oldSelected = c

        c.config(bg=self.cColors[c])
        c.itemconfig(self._id[c]["Title"], fill=self.tColors[c][2], font=("helvetica", 11, "bold"))

        self.selectedCanvas = c

        self.selVersion = version

    def play_version(self, version):
        """
        Runs a specific version instead from selected version.

        :param version:
        :return:
        """

        self.selVersion = version
        self.play()

    def on_bottompanel_configure(self, evt):
        """
        Update playbutton when resizing the window, this event is called from the bottom panel.

        :param evt:
        :return:
        """
        self.playBtn.place_forget()
        self.playBtn.place(x=self.bottomPanel.winfo_width() / 2, y=self.bottomPanel.winfo_y() - 10, anchor="n")

    def save_launchercfg(self):
        """
        Saves launcher configuration

        :return:
        """

        print("Saving launcher configuration...")

        # Open file and write the JSON data.
        with open(os.path.join(LAUNCHER_CFG), "w+") as file:
            file.write(json.dumps(self.launcherConfig, sort_keys=True, indent=4) + "\n")

    def _authenticate_save(self, tokens=None):
        """
        Saves authentication tokens

        :param tokens:
        :return:
        """
        luname = self.username.lower()
        if tokens is None:
            tokens = load_auth_tokens()
        self.auth_token: authentication.AuthenticationToken
        if self.auth_token is not None:
            tokens[luname] = {
                "accessToken": self.auth_token.access_token,
                "clientToken": self.auth_token.client_token,
                "username": self.auth_token.username}
        # elif luname in tokens:
        #     del tokens[luname]
        if tokens.get(luname) != self.auth_token:
            print("Saving authentication tokens...")
            # Update tokens in launcher config
            self.launcherConfig["tokens"] = tokens

            # Save launcher config
            self.save_launchercfg()

    def download_event(self, x):
        """
        Download event, used to update the playbutton text to show how far with downloading.

        :param x:
        :return:
        """

        try:
            self.playBtn.config(text=str(x.currentvalue) + "/" + str(x.maxvalue))
        except RuntimeError:  # Fixes crashing when closing the window while downloading
            exit()
        self.update()

    def play(self):
        """
        Runs the game version. (Or in other words: Open an process for the game version)

        :return:
        """
        # Intitialize Minecraft in the {DATA_FOLDER} path.
        pml.initialize(DATA_FOLDER)

        # Update play button to be disabled
        self.playBtn.configure(state="disabled")

        # Update download event handler
        pml.downloadEventHandler = self.download_event

        print("Get Args")

        # Get arguments for running the game
        args = pml.startProfile(self.selVersion,
                                xmx_mb=1024,
                                session=self.session,

                                launcher_name="qminecraft",  # option
                                server_ip="",
                                jvm_args="",
                                screen_width=0,
                                screen_height=0)
        # print(args)

        print("Make Subprocess")

        # Possible fix for gamedir
        os.chdir(pml.getGamePath())

        # We don't need the launcher for now.
        self.destroy()

        # Run the game, using java.
        mc = subprocess.Popen("java " + args, cwd=pml.getGamePath(), shell=True)

    def configure_event(self, evt):
        """
        Configure event for updating the background image for the resolution and scale

        :param evt:
        :return:
        """
        # Closes previous opened image
        self._backgroundImage.close()

        # Open image and resize it
        self._backgroundImage: PIL.Image.Image = PIL.Image.open("background.png")
        self._backgroundImage = get_resized_img(self._backgroundImage, (evt.width, evt.height))

        # Convert to tkinter.PhotoImage(...)
        self._tmp_img_tk = PIL.ImageTk.PhotoImage(self._backgroundImage)

        # Update background
        self.canvas.itemconfig(self.background, image=self._tmp_img_tk)
        self.canvas.update()

    @staticmethod
    def setup_theme():
        # Creating theme
        style = ttk.Style()
        style.theme_settings("default", {
            "TEntry": {
                "configure": {"font": ("Consolas", 10), "relief": "flat", "selectborderwidth": 0},
                "map": {
                    "relief": [("active", ENTRY_RELIEF),
                               ("focus", ENTRY_RELIEF),
                               ("!disabled", ENTRY_RELIEF)],
                    "bordercolor": [("active", ENTRY_BD_COL),
                                    ("focus", ENTRY_BD_COL),
                                    ("!disabled", ENTRY_BD_COL)],
                    "background": [("active", ENTRY_BG_DIS),
                                   ("focus", ENTRY_BG_FOC),
                                   ("!disabled", ENTRY_BG)],
                    "fieldbackground": [("active", ENTRY_BG_DIS),
                                        ("focus", ENTRY_BG_FOC),
                                        ("!disabled", ENTRY_BG)],
                    "foreground": [("active", ENTRY_FG_DIS),
                                   ("focus", ENTRY_FG_FOC),
                                   ("!disabled", ENTRY_FG)],
                    "selectbackground": [("active", ENTRY_SEL_BG_DIS),
                                         ("focus", ENTRY_SEL_BG_FOC),
                                         ("!disabled", ENTRY_SEL_BG)],
                    "selectforeground": [("active", ENTRY_SEL_FG_DIS),
                                         ("focus", ENTRY_SEL_FG_FOC),
                                         ("!disabled", ENTRY_SEL_FG)]
                }
            },
            "TLabel": {
                "configure": {"background": "#5c5c5c",
                              "foreground": "#7f7f7f",
                              "font": ("Consolas", 10)}
            },
            "TButton": {
                "configure": {"font": ("FixedSys", 18, "bold"), "relief": REL_PLAY_BTN, "borderwidth": BD_PLAY_BTN,
                              "highlightcolor": "white"},
                "map": {
                    "background": [("active", "#0a944e"),
                                   ("focus", COL_PLAY_BTN),
                                   ("pressed", "#0C6E3D"),
                                   ("!disabled", COL_PLAY_BTN),
                                   ("disabled", "#5f5f5f")],
                    "lightcolor": [("active", "#27CE40"),
                                   ("focus", "#27CE40"),
                                   ("!disabled", "#27CE40")],
                    "darkcolor": [("active", "#0a944e"),
                                  ("focus", "#27CE40"),
                                  ("!disabled", "#27CE40")],
                    "bordercolor": [("active", "#0A944E"),
                                    ("focus", COL_PLAY_BTN),
                                    ("pressed", "#0C6E3D"),
                                    ("!disabled", COL_PLAY_BTN),
                                    ("disabled", "#5f5f5f")],
                    "foreground": [("active", "white"),
                                   ("focus", "white"),
                                   ("pressed", "white"),
                                   ("!disabled", "white")],
                    "relief": [("active", REL_PLAY_BTN),
                               ("focus", REL_PLAY_BTN),
                               ("pressed", REL_PLAY_BTN),
                               ("!disabled", REL_PLAY_BTN)]
                }
            },
            "Treeview": {
                "configure": {"padding": 0, "font": ("Consolas", 10), "relief": "flat", "border": 0, "rowheight": 24},
                "map": {
                    "background": [("active", TREEVIEW_BG),
                                   ("focus", TREEVIEW_SEL_BG),
                                   ("!disabled", TREEVIEW_BG),
                                   ("selected", TREEVIEW_BG)],
                    "fieldbackground": [("active", TREEVIEW_BG),
                                        ("focus", TREEVIEW_BG),
                                        ("!disabled", TREEVIEW_BG)],
                    "foreground": [("active", TREEVIEW_FG),
                                   ("focus", TREEVIEW_SEL_FG),
                                   ("!disabled", TREEVIEW_FG),
                                   ("selected", TREEVIEW_FG)],
                    "relief": [("focus", "flat"),
                               ("active", "flat"),
                               ("!disabled", "flat")]
                }
            },
            "Treeview.Item": {
                "configure": {"padding": 0},
                "map": {
                    "background": [("active", TREEVIEW_SEL_BG),
                                   ("!disabled", TREEVIEW_SEL_BG),
                                   ("!selected", TREEVIEW_SEL_BG)],
                    "fieldbackground": [("!disabled", TREEVIEW_SEL_BG),
                                        ("active", TREEVIEW_SEL_BG),
                                        ("!selected", TREEVIEW_SEL_BG)],
                    "foreground": [("active", TREEVIEW_SEL_BG),
                                   ("focus", TREEVIEW_SEL_FG),
                                   ("!disabled", TREEVIEW_SEL_FG),
                                   ("selected", TREEVIEW_SEL_BG)],
                    "relief": [("focus", "flat"),
                               ("active", "flat"),
                               ("!disabled", "flat")]
                }
            },
            "Treeview.Cell": {
                "configure": {"padding": 0},
                "map": {
                    "background": [("active", TREEVIEW_SEL_BG),
                                   ("!disabled", TREEVIEW_SEL_BG),
                                   ("!selected", TREEVIEW_SEL_BG)],
                    "fieldbackground": [("!disabled", TREEVIEW_SEL_BG),
                                        ("active", TREEVIEW_SEL_BG),
                                        ("!selected", TREEVIEW_SEL_BG)],
                    "foreground": [("focus", TREEVIEW_SEL_FG),
                                   ("!disabled", TREEVIEW_SEL_FG),
                                   ("!selected", TREEVIEW_SEL_BG)],
                    "relief": [("focus", "flat"),
                               ("active", "flat"),
                               ("!disabled", "flat")]
                }
            }
        })
        # Using theme and configure
        style.theme_use("default")
        style.configure('TEntry', relief='flat')

        # Configure TEntry layout, for removing border relief
        style.layout('TEntry', [
            ('Entry.highlight', {
                'sticky': 'nswe',
                'children':
                    [('Entry.border', {
                        'border': '5',
                        'sticky': 'nswe',
                        'children':
                            [('Entry.padding', {
                                'sticky': 'nswe',
                                'children':
                                    [('Entry.textarea',
                                      {'sticky': 'nswe'})]
                            })]
                    })]
            })])


class QTwitchWindow(QMinecraftWindow):
    def __init__(self):
        # Define accountfile path
        accountfile_path = data_path("account.json")

        def makefile():
            """
            Showing information for account file, creates the account file, then opens the account file.
            Simple as what.

            :return:
            """
            from tkinter.messagebox import showinfo
            root = Tk()
            root.withdraw()

            showinfo("Note", f"""Account file is corrupt or doesn't exists!
        This program will create and open the file for you.
        Then replace <username> with your username or email (use your email when username doen't work).
        And replace <password> with your password.

        When all this is done, reopen the launcher. 
        If prompted choose an program to open it, like Notepad (Windows) or Gedit (Ubuntu)""", master=root)
            with open(accountfile_path, "w+") as file_:
                file_.write(json.dumps({"username": "<username>", "password": "<password>"}, indent=4, sort_keys=True))
                file_.close()
            sleep(2)
            if (platform.system().lower() == "unix") or (platform.system().lower() == "linux"):
                os.startfile(accountfile_path)
            elif platform.system().lower() == "windows":
                os.startfile("C:\\" + accountfile_path.replace("/", "\\"))
            exit()

        if os.path.exists(accountfile_path):
            try:
                with open(accountfile_path) as file:
                    self.launcherData = json.JSONDecoder().decode(file.read())
            except json.JSONDecodeError:
                makefile()
        else:
            makefile()

        super(QMinecraftWindow, self).__init__()

        # Configure the window
        self.title("QMinecraft Twitch Launcher")
        self.geometry("900x506")
        self.minsize(614, 400)

        # Temporary game directory
        pml.initialize("/")

        # Make closing the window, killing the program
        self.wm_protocol("WM_DELETE_WINDOW", lambda: os.kill(os.getpid(), 0))

        print("Reading launcher config")

        # Reading launcher config
        tokens = {}
        if os.path.exists(LAUNCHER_CFG):
            with open(os.path.join(LAUNCHER_CFG)) as file:
                self.launcherConfig = json.JSONDecoder().decode(file.read())
            if "tokens" in self.launcherConfig.keys():
                tokens = self.launcherConfig["tokens"]
        else:
            print("Launcher config doen't exists, creating a new one...")
            self.launcherConfig = {}

        # Update launcher config, if some keys are non-existend
        if "fullscreen" not in self.launcherConfig.keys():
            self.launcherConfig["fullscreen"] = False
        if "tokens" not in self.launcherConfig.keys():
            self.launcherConfig["tokens"] = {}
        if "profilename" not in self.launcherConfig.keys():
            self.launcherConfig["profilename"] = f"player{randint(100, 999)}"
        if "uuid" not in self.launcherConfig.keys():
            self.launcherConfig["uuid"] = None
        if "-Xmx" not in self.launcherConfig.keys():
            self.launcherConfig["-Xmx"] = 1024
        self.save_launchercfg()

        # Get local Minecraft versions
        self.profiles = []
        versions_dir = os.path.join(DATA_FOLDER, "versions")
        for item in os.listdir(os.path.join(DATA_FOLDER, "versions")):
            _item_dir = os.path.join(versions_dir, item)
            if os.path.isdir(_item_dir):
                if os.path.exists(os.path.join(_item_dir, item + ".jar")):
                    if os.path.exists(os.path.join(_item_dir, item + ".json")):
                        self.profiles.append(item)

        print("Getting versions")

        # Get versions
        from requests.exceptions import ConnectionError

        try:
            self.profiles = getProfilesFromLocal()
        except ConnectionError:
            self.profiles = []

        # Get username (or email) and password from account data ({DATA_FOLDER}/account.json)
        self.username = self.launcherData["username"]
        self.password = self.launcherData["password"]
        self.auth_token: Optional[authentication.AuthenticationToken] = None

        # Initialize Python Minecraft Launcher library
        pml.initialize(DATA_FOLDER)

        # Initialize Minecraft versions
        _temp0003 = getProfilesFromLocal()
        _temp0004 = []
        for p in _temp0003:
            if "forge" in p.name:
                pass
            elif "fabric" in p.name:
                pass
            else:
                _temp0004.append(p)

        self.profiles = _temp0004

        _temp_prof0001 = getProfilesFromLocal()

        _temp_prof0002 = []
        _temp_profnames = [p.name for p in self.profiles]

        for instance in _temp_prof0001:
            if instance.name not in _temp_profnames:
                _temp_prof0002.append(instance)

        _temp_prof0002.extend(self.profiles)
        self.profiles = _temp_prof0002

        # Initialize authentication
        if self.auth_token is None:
            token = tokens.get(self.username.lower(), None)
            print("Have already a token" if token is not None else "Haven't already a token")
            if token is not None:
                self.auth_token = authentication.AuthenticationToken(
                    username=self.username,
                    access_token=token['accessToken'],
                    client_token=token['clientToken'])
            self.online = True
        if self.auth_token is not None:
            print("Refreshing token...")
            try:
                self.auth_token.refresh()
                self.online = True
            except YggdrasilError:
                print("Refreshing failed")
                self.auth_token = None
                self.online = True
            except ConnectionError:
                print("No internet connection")
                self.auth_token = None
                self.online = False
        if (self.auth_token is None) and self.online:
            print("Create a new token...")
            try:
                self.auth_token = authentication.AuthenticationToken()
                self.auth_token.authenticate(self.username, self.password)
            except YggdrasilError:
                print("Creating a token failed")
                self.auth_token = None
                raise
            except ConnectionError:
                self.online = False

        # Saves Minecraft authentication
        self._authenticate_save(tokens=tokens)

        # self.auth_token = None

        # Make the Minecraft account session
        if self.auth_token is None:
            print("Can't find a token, using default player account")
            self.session = mlogin.session()  # set session object
            self.session.username = self.launcherConfig["profilename"]
            # noinspection PyTypeChecker
            self.session.access_token = self.launcherConfig["tokens"][self.username]["accessToken"]
            if self.launcherConfig["uuid"] is not None:
                self.session.uuid = self.launcherConfig["uuid"]
        else:
            print(f"Login successful, profile name: {self.auth_token.profile.name}")
            self.session = mlogin.session()  # set session object
            self.session.username = self.auth_token.profile.name
            self.session.uuid = self.auth_token.profile.id_
            self.session.access_token = self.auth_token.access_token

        # Define profile name
        self.profilename = self.session.username

        # Update launcher config for user profile name and uuid
        self.launcherConfig["profilename"] = self.profilename
        self.launcherConfig["uuid"] = self.session.uuid
        self.save_launchercfg()

        # Setup theme
        self.setup_theme()

        print("Setup UI...")

        # Initialize modloader and Minecraft icons
        self.iconRift = PhotoImage(file="icons/rift.png")
        self.iconForge = PhotoImage(file="icons/forge.png")
        self.iconFabric = PhotoImage(file="icons/fabric.png")
        self.iconClassic = PhotoImage(file="icons/classic.png")
        self.iconOptifine = PhotoImage(file="icons/optifine.png")
        self.iconMinecraft = PhotoImage(file="icons/minecraft.png")

        # Initialize modloader and Minecraft colors (background when selecting)
        self.colorRift = "#D7D7D7"
        self.colorForge = "#3E5482"
        self.colorFabric = "#BFB49C"
        self.colorClassic = "#7A7A7A"
        self.colorOptifine = "#AD393B"
        self.colorMinecraft = "#A8744F"

        # Index instances and initialize information
        instances = os.listdir(f"/Users/{os.getlogin()}/Twitch/Minecraft/Instances")
        self.instances = []
        for instance in instances:
            with open(f"/Users/{os.getlogin()}/Twitch/Minecraft/Instances/{instance}/minecraftinstance.json", "r") as file:
                data = json.loads(file.read())
            if data is None:
                continue
            if data["baseModLoader"] is None:
                version = data["gameVersion"]
            else:
                version = data["baseModLoader"]["name"]
            self.instances.append({"version": version,
                                   "path": f"C:\\Users\\{os.getlogin()}\\Twitch\\Minecraft\\Instances\\{instance}",
                                   "name": instance})

        # Define selected instance
        self.selInstance = self.instances[0]

        # Initialize background image
        self._backgroundImage: PIL.Image.Image = PIL.Image.open("background.png")
        self._tmp_img_tk = PIL.ImageTk.PhotoImage(self._backgroundImage)

        self.rootFrame = Frame(self, bg="#282828")

        vlw = 300

        # Initialize left panel
        self.leftPanel = Frame(self.rootFrame, height=75, width=vlw)

        # User info and status
        self.userFrame = Canvas(self.leftPanel, bg="#282828", height=75, highlightthickness=0, width=vlw)
        self.userNameText = self.userFrame.create_text(10, 10, text=self.session.username,
                                                       font=("helvetica", 10, "bold"), fill="white", anchor="nw")
        self.userStatusIcon = self.userFrame.create_rectangle(11, 41, 19, 49,
                                                              fill="#008542" if self.auth_token is not None else "#434343",
                                                              outline=COL_PLAY_BTN if self.auth_token is not None else "#434343")
        self.userStatusText = self.userFrame.create_text(25, 45,
                                                         text="Online" if self.auth_token is not None else "Offline",
                                                         fill="#a5a5a5", anchor="w", font=("helvetica", 10))
        self.userFrame.pack(fill="x")

        # Slots frame.
        self.sPanel = Frame(self.leftPanel, height=self.rootFrame.winfo_height() - 100, width=vlw)
        self.sPanel.pack(side="left", fill="y")

        # Scrollwindow for the slots frame
        self.sw = ScrolledWindow(self.sPanel, vlw, self.winfo_height() + 0, expand=True, fill="both")

        # Configurate the canvas from the scrollwindow
        self.canv = self.sw.canv
        self.canv.config(bg="#1e1e1e")
        self.sw.vbar.config(bg="#1e1e1e", fg="#353535")

        # self.frame.
        self.frame_sw = self.sw.scrollwindow
        self.frames = []

        # Defining the list of widgets
        self._id = {}
        self.index = {}
        self.canvass = []
        self.buttons = []

        # Initialize canvas selection and hover data
        self.oldSelected: Optional[Canvas] = None
        self.selectedCanvas: Optional[Canvas] = None
        self._hoverCanvasOld: Optional[Canvas] = None
        self._hoverCanvas: Optional[Canvas] = None

        # Define the index variable.
        i = 0

        # Initilalize colors
        self.cColors: Dict[Canvas, str] = {}  # Background colors
        self.tColors: Dict[Canvas, List[str]] = {}  # Text colors

        # Create all items in the instances menu
        for instance in self.instances:
            self.frames.append(Frame(self.frame_sw, height=32, width=vlw, bd=0))
            self.canvass.append(Canvas(self.frames[-1], height=32, width=vlw, bg="#1e1e1e", highlightthickness=0, bd=0))
            self.canvass[-1].pack()
            self._id[self.canvass[-1]] = {}
            if "rift" in instance["version"].lower():
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconRift,
                                                                                   anchor="nw")
                color = self.colorRift
            elif "forge" in instance["version"].lower():
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconForge,
                                                                                   anchor="nw")
                color = self.colorForge
            elif "fabric" in instance["version"].lower():
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconFabric,
                                                                                   anchor="nw")
                color = self.colorFabric
            elif "optifine" in instance["version"].lower():
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconOptifine,
                                                                                   anchor="nw")
                color = self.colorOptifine
            elif instance["version"].startswith("a") or instance["version"].startswith("b") or instance["version"].startswith(
                    "c") or instance["version"].startswith("rd") or instance["version"].startswith("inf"):
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconClassic,
                                                                                   anchor="nw")
                color = self.colorClassic
            else:
                self._id[self.canvass[-1]]["Icon"] = self.canvass[-1].create_image(0, 0, image=self.iconMinecraft,
                                                                                   anchor="nw")
                color = self.colorMinecraft
            if instance["version"] not in os.listdir(versions_dir):
                t_color = ["#434343", "#7f7f7f", "#a5a5a5"]
                color = "#434343"
            else:
                t_color = ["#a5a5a5", "#ffffff", "#ffffff"]
            self._id[self.canvass[-1]]["Title"] = self.canvass[-1].create_text(37, 15, text=instance["name"],
                                                                               fill=t_color[0], anchor="w",
                                                                               font=("helvetica", 11))
            self.cColors[self.canvass[-1]] = color
            self.tColors[self.canvass[-1]] = t_color
            # self.canvass[-1].create_rectangle(0, 0, 699, 201, outline="#1e1e1e")
            self.canvass[-1].bind("<ButtonRelease-1>",
                                  lambda event, i=instance, c=self.canvass[-1]: self.select_version(c, i))
            self.canvass[-1].bind("<Double-Button-1>", lambda event, i=instance: self.play_version(i))
            self.canvass[-1].bind("<Motion>", lambda event, c=self.canvass[-1]: self._on_canv_motion(c))
            self.canvass[-1].bind("<Leave>", lambda event, c=self.canvass[-1]: self._on_canv_leave(c))
            self.index[self.canvass[-1]] = i
            self.frames[-1].pack(side="top")

            i += 1

        # Select most top instance
        self.select_version(self.canvass[0], self.instances[0])

        # Pack the left panel
        self.leftPanel.pack(side="left", fill="y")

        # Right panels
        self.rightPanels = Frame(self.rootFrame, bg="#282828")

        # Wallpaper
        self.canvas = Canvas(self.rightPanels, bg="#282828", highlightthickness=0)
        self.background = self.canvas.create_image(0, 0, anchor="nw", image=self._tmp_img_tk)
        self.canvas.pack(fill="both", expand=True)

        # Bottom panel, and Play button
        self.bottomPanel = Frame(self.rightPanels, bg="#262626", height=60)
        self.playBtn = CustomFontButton(self.rightPanels, width=250,
                                        text="PLAY" if self.auth_token is not None else "PLAY OFFLINE",
                                        font_path="Minecrafter.Reg.ttf", foreground="white", size=30, command=self.play)
        self.playBtn.place(x=self.bottomPanel.winfo_width() / 2, y=self.bottomPanel.winfo_y() + 10, anchor="n")
        self.bottomPanel.pack(side="bottom", fill="x")
        self.rightPanels.pack(side="right", fill="both", expand=True)
        self.rootFrame.pack(side="left", fill="both", expand=True)

        # Event bindings
        self.canvas.bind("<Configure>", self.configure_event)
        self.bottomPanel.bind("<Configure>", self.on_bottompanel_configure)

        self.wm_attributes("-fullscreen", self.launcherConfig["fullscreen"])

    def select_version(self, c: Canvas, instance):
        if self.oldSelected is not None:
            self.oldSelected.config(bg="#1e1e1e")
            self.oldSelected.itemconfig(self._id[self.oldSelected]["Title"], fill=self.tColors[self.oldSelected][0],
                                        font=("helvetica", 11))
        self.oldSelected = c

        c.config(bg=self.cColors[c])
        c.itemconfig(self._id[c]["Title"], fill=self.tColors[c][2], font=("helvetica", 11, "bold"))

        self.selectedCanvas = c

        self.selInstance = instance

    def play_version(self, instance):
        self.selInstance = instance
        self.play()

    def play(self):
        self.playBtn.configure(state="disabled")

        print(self.selInstance)

        pml.downloadEventHandler = self.download_event

        print("Get Args")

        args = pml.startProfile(self.selInstance["version"],
                                xmx_mb=self.launcherConfig["-Xmx"],
                                session=self.session,

                                launcher_name="qminecraft_twitch",  # option
                                server_ip="",
                                jvm_args="",
                                screen_width=0,
                                screen_height=0)

        game_folder = self.selInstance["path"]

        args = args.replace(
            f"--gameDir "+("\""+DATA_FOLDER[:-1]+"\"" if " " in DATA_FOLDER else DATA_FOLDER[:-1]).replace("/", "\\"),
            f"--gameDir "+("\""+game_folder+"\"" if " " in game_folder else game_folder).replace("/", "\\"))

        print(f"--gameDir "+("\""+DATA_FOLDER[:-1]+"\"" if " " in DATA_FOLDER else DATA_FOLDER[:-1]).replace("/", "\\"))

        print(args)

        # exit(0)

        print("Make Subprocess")

        os.chdir(self.selInstance["path"])
        print(os.getcwd())
        print(self.selInstance["path"])

        self.destroy()

        mc = subprocess.Popen("java " + args, cwd=self.selInstance["path"], shell=True)


if __name__ == '__main__':
    if os.path.exists(data_path("launchermode.json")):
        with open(data_path("launchermode.json"), "r+") as file2:
            try:
                launchermode = json.loads(file2.read())
            except json.JSONDecodeError:
                _temp0005 = {"mode": "qmc", "available": ["qmc", "mc"]}
                file2.write(json.dumps(_temp0005))
                launchermode = _temp0005
    else:
        with open(data_path("launchermode.json"), "w") as file2:
            _temp0005 = {"mode": "qmc", "available": ["qmc", "mc"]}
            file2.write(json.dumps(_temp0005))
            launchermode = _temp0005

    if launchermode["mode"] == "mc":
        DATA_FOLDER = f"/Users/{os.getlogin()}/AppData/Roaming/.minecraft/"
        QMinecraftWindow().mainloop()
    elif launchermode["mode"] == "twitch":
        DATA_FOLDER = f"/Users/{os.getlogin()}/Twitch/Minecraft/Install/"
        QTwitchWindow().mainloop()
    elif launchermode["mode"] == "qmc":
        QMinecraftWindow().mainloop()
    else:
        with open(data_path("launchermode.json"), "w") as file2:
            _temp0005 = {"mode": "qmc", "available": ["qmc", "mc"]}
            file2.write(json.dumps(_temp0005))
            launchermode = _temp0005
            QMinecraftWindow().mainloop()
