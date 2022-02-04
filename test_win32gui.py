import ctypes, win32api, win32gui
ctypes.windll.user32.SetProcessDPIAware(2)

handle = win32gui.FindWindow(None, None)

def get_opposite(handle):
    """获取对角线"""
    left, top, right, bottom = win32gui.GetWindowRect(handle)
    return (left, top), (right, bottom)



from rich import *

def show_window_attr(hwnd):
    if not hwnd:
        inspect(hwnd)
        return
    else:
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        if title and class_name:
            if "Edge" in title and class_name == "Chrome_WidgetWin_1":
                print(f"[bright_cyan]{hwnd = }, {title = }, {class_name = }")
                print(demo_child_windows(hwnd))
            elif "Mozilla Firefox" in title and class_name == "MozillaWindowClass":
                print(f"[bright_green]{hwnd = }, {title = }, {class_name = }")
                print(demo_child_windows(hwnd))

def show_all(hWndList):
    for hwnd in hWndList:
        show_window_attr(hwnd)

def demo_top_windows():
    hWndList = []
    win32gui.EnumWindows(lambda hWnd, hWndList: hWndList.append(hWnd), hWndList)

    show_all(hWndList)

    return hWndList

def demo_child_windows(parent):
    if not parent:
        return

    children = []
    win32gui.EnumChildWindows(parent, lambda hWnd, children: children.append(hWnd), children)
    show_all(children)

    for hwnd in children:
        title = win32gui.GetWindowText(hwnd)
        class_name = win32gui.GetClassName(hwnd)
        print(f"{hwnd = }, {title = }, {class_name = }")
        print(demo_child_windows(hwnd))

    return children


if __name__ == '__main__':

    hWndList = demo_top_windows()

    parent = hWndList[123]
    # 若无法遍历，需要使用spy++确认是否存在子窗口
    hWndChildList = demo_child_windows(parent)

    # print('-----top windows-----')
    # print(hWndList)

    # print('-----sub windows:from %s------' % parent)
    # print(hWndChildList)
