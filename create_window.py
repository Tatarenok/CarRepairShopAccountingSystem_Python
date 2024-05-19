# Глобальный флаг для отслеживания выбора вкладки пользователем
user_tab_selected = False

# Функция для установки стартового размера окна по центру
def set_window_geometry(root):
    root.geometry("1200x800")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 1200) // 2
    y = (screen_height - 800) // 2
    root.geometry(f"1200x800+{x}+{y}")
    root.resizable(False, False)

# Функция для обработки события изменения вкладки
def tab_clicked(event, tab_startup,tab_control):
    global user_tab_selected
    if event.widget.select() == event.widget.tabs()[0]:
        user_tab_selected = True
    else:
        user_tab_selected = False
        tab_control.hide(tab_startup)
