import curses

import wx


def wx_ui_run(controller):
    app = MyApp()
    main_frame = WxCurses(app, controller)
    main_frame.Show()
    app.MainLoop()
    return app.get_result()


WX_BG = (0, 43, 54)
WX_FG = (101, 123, 131)
WX_RED = (220, 50, 47)
WX_GREEN = (133, 153, 0)
WX_WHITE = (255, 255, 255)


class MyApp(wx.App):

    def __init__(self):
        wx.App.__init__(self, False)
        self.set_result(None)

    def set_result(self, result):
        self._result = result

    def get_result(self):
        return self._result


class WxCurses(wx.Frame):

    def __init__(self, app, controller):
        wx.Frame.__init__(self, None, size=(800, 600))
        self._screen = WxScreen(self, app, controller)


class WxScreen(wx.Panel):

    def __init__(self, parent, app, controller):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER | wx.WANTS_CHARS)
        self._app = app
        self._controller = controller
        self._surface_bitmap = None
        self._commands = []
        self._init_fonts()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_CHAR, self._on_key_down)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        wx.CallAfter(self._after_init)

    def _after_init(self):
        self._controller.setup(self)
        self._controller.render(self)

    def getmaxyx(self):
        ww, wh = self.GetSizeTuple()
        max_y = int(wh) / int(self._fh)
        max_x = int(ww) / int(self._fw)
        return (max_y, max_x)

    def erase(self):
        self._commands = []

    def addstr(self, y, x, text, style):
        self._commands.append((y, x, text, style))

    def refresh(self):
        width, height = self.GetSizeTuple()
        self._surface_bitmap = wx.EmptyBitmap(width, height)
        memdc = wx.MemoryDC()
        memdc.SelectObject(self._surface_bitmap)
        memdc.BeginDrawing()
        memdc.SetBackground(wx.Brush(WX_BG, wx.SOLID))
        memdc.SetBackgroundMode(wx.PENSTYLE_SOLID)
        memdc.Clear()
        for (y, x, text, style) in self._commands:
            if style == "highlight":
                memdc.SetFont(self._base_font_bold)
                fg, bg = WX_RED, WX_BG
            elif style == "select":
                memdc.SetFont(self._base_font_bold)
                fg, bg = WX_WHITE, WX_GREEN
            elif style == "status":
                memdc.SetFont(self._base_font_bold)
                fg, bg = WX_BG, WX_FG
            else:
                memdc.SetFont(self._base_font)
                fg, bg = WX_FG, WX_BG
            memdc.SetTextBackground(bg)
            memdc.SetTextForeground(fg)
            memdc.DrawText(text, x*self._fw, y*self._fh)
        memdc.EndDrawing()
        del memdc
        self.Refresh()
        self.Update()

    def _init_fonts(self):
        self._base_font = wx.Font(
            11,
            wx.FONTFAMILY_TELETYPE,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL
        )
        self._base_font_bold = self._base_font.Bold()
        self._find_text_size()

    def _find_text_size(self):
        bitmap = wx.EmptyBitmap(100, 100)
        memdc = wx.MemoryDC()
        memdc.SetFont(self._base_font)
        memdc.SelectObject(bitmap)
        self._fw, self._fh = memdc.GetTextExtent(".")

    def _on_key_down(self, evt):
        result = self._controller.process_input(evt.GetUnicodeKey())
        if result:
            self._app.set_result(result)
            self.GetParent().Close()
        self._controller.render(self)

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.BeginDrawing()
        if self._surface_bitmap:
            dc.DrawBitmap(self._surface_bitmap, 0, 0, True)
        dc.EndDrawing()
