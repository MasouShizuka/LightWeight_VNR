import win32gui
import win32process


def get_hwnds_for_pid(pid):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId (hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
            return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds

def set_focus(pid):
    try:
        hwnds = get_hwnds_for_pid(pid)
        for hwnd in hwnds:
            win32gui.SetForegroundWindow(hwnd)
    except:
        pass
