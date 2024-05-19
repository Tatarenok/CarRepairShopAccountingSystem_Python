from create_window import *
from orders_tab import *
from clients_tab import *
from parts_tab import *
from svodka import *

# Создание соединения с базой данных SQLite
connection = sqlite3.connect('repair_shop.db')
cursor = connection.cursor()
# Создание таблиц, если они не существуют
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                  id INTEGER PRIMARY KEY,
                  name TEXT,
                  phone TEXT,
                  car TEXT,
                  problem TEXT,
                  status TEXT,
                  date_start TEXT,
                  date_end TEXT,
                  stage TEXT)''')
# Создание таблицы parts
cursor.execute('''CREATE TABLE IF NOT EXISTS parts (
                  id INTEGER PRIMARY KEY,
                  company TEXT,
                  article TEXT,
                  description TEXT,
                  quantity INTEGER,
                  cost INTEGER)''')


# Функция для создания интерфейса на вкладке "Стартовая страница"
def create_startup_tab(tab):
    # Создание фрейма для вкладки "Стартовая страница"
    startup_frame = ctk.CTkFrame(tab)
    startup_frame.pack(expand=True, fill='both')

    # Создание и добавление надписи в центре фрейма
    start = ctk.CTkLabel(startup_frame, text="Добро пожаловать!",font=("Helvetica", 36))
    start.place(relx=0.5, rely=0.2, anchor='center')
    label = ctk.CTkLabel(startup_frame, text="Приложение \"Система учета в авторемонтной мастерской\" разработанно студентом \nНурмухамедовым Наилем Радиковичем.\n\nДля начала работы, пожалуйста, выберите вкладку в навигационной панели сверху.", font=("Helvetica", 24))
    label.place(relx=0.5, rely=0.5, anchor='center')

# Функция для создания вкладок и добавления на вкладочный контрол
def create_tabs(connection):
    tab_control = ttk.Notebook(root)

    # Создание вкладок для разделов
    tab_startup = ctk.CTkFrame(tab_control) # Добавление дополнительной вкладки
    tab_orders = ctk.CTkFrame(tab_control)
    tab_clients = ctk.CTkFrame(tab_control)
    tab_parts = ctk.CTkFrame(tab_control)
    tab_summary = ctk.CTkFrame(tab_control)

    tab_control.add(tab_startup, text='Стартовая страница')
    create_startup_tab(tab_startup)
    tab_control.add(tab_orders, text='Заявки')
    create_orders_tab(tab_orders, connection)  # Передача соединения с базой данных
    tab_control.add(tab_clients, text='Клиенты')
    create_clients_tab(tab_clients, connection)
    tab_control.add(tab_parts, text='Запчасти')
    treesv = create_parts_tab(tab_parts,connection)
    tab_control.add(tab_summary, text='Сводка заказов')
    create_summary_tab(tab_summary,  treesv)

    return tab_control,tab_startup

# Создание основного окна
root = ctk.CTk()

ctk.set_appearance_mode("dark")

# Настройка заголовка окна
root.title("Система учета в авторемонтной мастерской")

# Установка стартового размера окна по центру
set_window_geometry(root)

# Создание вкладок и добавление на вкладочный контрол
tab_control,tab_startup = create_tabs(connection)
# Привязка функции к событию изменения вкладки
tab_control.bind("<<NotebookTabChanged>>", lambda event: tab_clicked(event, tab_startup,tab_control))

# Размещение вкладочного контрола на главном окне
tab_control.pack(expand=1, fill="both")

# Запуск главного цикла обработки событий
root.mainloop()
