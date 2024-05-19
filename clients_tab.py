import customtkinter as ctk
from tkinter import ttk
import tkinter as tk

def adjust_columns_width(tree):
    # Проходим по всем столбцам
    for col in tree["columns"]:
        # Получаем список значений для каждого элемента в столбце
        values = [tree.set(item, col) for item in tree.get_children('')]
        # Проверяем, что список значений не пустой
        if values:
            # Устанавливаем ширину столбца равной максимальной длине текста
            tree.column(col, width=max([len(value) for value in values]) * 9)

# Функция для создания интерфейса на вкладке "Клиенты"
def create_clients_tab(tab, connection):
    def update_clients_table(tree, connection):
        # Очистка таблицы перед обновлением
        for row in tree.get_children():
            tree.delete(row)

        cursor = connection.cursor()

        # Получаем данные из таблицы orders с условием status = "Принято"
        cursor.execute("SELECT id, name, phone, car, date_start,date_end,stage FROM orders WHERE status=?",
                       ("Принято",))
        orders_rows = cursor.fetchall()

        # Обновляем данные в таблице clients
        for order_row in orders_rows:
            tree.insert("", "end", values=order_row)

        # Подгоняем ширину столбцов
        adjust_columns_width(tree)

    # Создание фрейма для вкладки "Клиенты"
    clients_frame = ctk.CTkFrame(tab)
    clients_frame.pack(expand=True, fill='both')

    # Создание заголовков таблицы
    columns = ("ID", "ФИО", "Номер телефона", "Автомобиль", "Дата приема", "Дата завершения", "Этап работы")

    # Создание и заполнение таблицы
    tree = ttk.Treeview(clients_frame, columns=columns, show="headings", selectmode="browse")
    tree.pack(side="left", fill="both", expand=True)

    # Установка ширины столбцов
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)  # Задайте желаемую ширину

    # Обновление данных в таблице при открытии вкладки
    update_clients_table(tree, connection)

    # Кнопка для обновления данных
    button_refresh = ctk.CTkButton(clients_frame, text="Обновить", command=lambda: update_clients_table(tree, connection))

    button_refresh.pack(side="top", padx=5, pady=5)

    # Кнопка для изменения информации о работе
    button_edit_work = ctk.CTkButton(clients_frame, text="Изменить данные", command=lambda: open_work_info_dialog(tree, connection))
    button_edit_work.pack(side="top", padx=5, pady=5)

def open_work_info_dialog(tree, connection):
    # Получение выделенной строки
    selected_item = tree.focus()
    if selected_item:
        # Получение данных о работе из выбранной строки
        work_info = tree.item(selected_item)['values']

        # Создание диалогового окна
        dialog = tk.Toplevel()
        dialog.title("Информация о работе")

        # Переменные для хранения данных
        date_start_var = tk.StringVar(value=work_info[4])
        date_end_var = tk.StringVar(value=work_info[5])
        stage_var = tk.StringVar(value=work_info[6])


        # Создание меток и полей для ввода
        tk.Label(dialog, text="Дата приема:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=date_start_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Дата завершения:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=date_end_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Этап работы:").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=stage_var).grid(row=2, column=1, padx=5, pady=5)

        # Установка центрирования окна
        dialog_width = 340
        dialog_height = 150
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x_coordinate = (screen_width - dialog_width) / 2
        y_coordinate = (screen_height - dialog_height) / 2
        dialog.geometry("%dx%d+%d+%d" % (dialog_width, dialog_height, x_coordinate, y_coordinate))
        dialog.resizable(False, False)

        # Кнопка "Готово"
        def update_data():
            # Обновление данных в выбранной строке
            tree.item(selected_item, values=(
                work_info[0], work_info[1], work_info[2], work_info[3], date_start_var.get(), date_end_var.get(),
                stage_var.get()))

            # Обновление данных в таблице orders
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE orders 
                SET date_start=?, date_end=?, stage=?
                WHERE id=?
            """, (date_start_var.get(), date_end_var.get(), stage_var.get(), work_info[0]))
            connection.commit()

            dialog.destroy()

        tk.Button(dialog, text="Готово", command=update_data).grid(row=3, columnspan=2, padx=5, pady=5)

