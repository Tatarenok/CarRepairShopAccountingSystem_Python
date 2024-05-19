import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
import tkinter.messagebox as mb


def adjust_columns_width(tree):
    # Проходим по всем столбцам
    for col in tree["columns"]:
        # Устанавливаем ширину столбца равной максимальной длине текста
        tree.column(col, width=max([len(tree.set(item, col)) for item in tree.get_children('')]) * 9)


# Функция для добавления записи
def add_entry(tree, connection):
    # Создание диалогового окна для ввода данных
    dialog = tk.Toplevel()
    dialog.title("Добавление записи")

    # Создание меток и полей для ввода данных
    labels = ["ФИО:", "Номер телефона:", "Автомобиль:", "Проблема:", "Статус:"]
    entries = []

    for label_text in labels:
        label = tk.Label(dialog, text=label_text)
        label.grid(sticky="w")

        entry = tk.Entry(dialog)
        entry.grid(sticky="we")
        entries.append(entry)

    # Функция для добавления записи
    def add():
        # Получение данных из полей ввода
        new_values = [entry.get() for entry in entries]
        if(new_values[4] == "Принято" or new_values[4] == "Отказано" or new_values[4] == "На рассмотрении"):
            # Вставка новой записи в базу данных
            cursor = connection.cursor()
            cursor.execute("INSERT INTO orders (id, name, phone, car, problem, status) VALUES (NULL, ?, ?, ?, ?, ?)", new_values)
            connection.commit()
        else:
            mb.showerror("Ошибка", "Вы ввели некорректный статус.")

        # Обновление таблицы
        update_table(tree, connection)
        adjust_columns_width(tree)
        # Закрытие диалогового окна
        dialog.destroy()

    # Кнопка для добавления записи
    button_add = tk.Button(dialog, text="Добавить", command=add)
    button_add.grid(row=len(labels) + 5, column=0, columnspan=2, pady=5)

    # Вычисление размера окна для центрирования
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)

    # Центрирование окна
    dialog.geometry(f"+{x}+{y}")
    dialog.resizable(False, False)

    # Отображение диалогового окна
    dialog.mainloop()

def edit_entry(tree, connection):
    # Получение выделенной строки
    selected_item = tree.focus()
    if selected_item:
        # Получение данных о работе из выбранной строки
        work_info = tree.item(selected_item)['values']

        # Создание диалогового окна
        dialog = tk.Toplevel()
        dialog.title("Информация о заказе")

        # Переменные для хранения данных
        name_var = tk.StringVar(value=work_info[1])
        phone_var = tk.StringVar(value=work_info[2])
        car_var = tk.StringVar(value=work_info[3])
        problem_var = tk.StringVar(value=work_info[4])
        status_var = tk.StringVar(value=work_info[5])

        # Создание меток и полей для ввода
        tk.Label(dialog, text="ФИО:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Номер телефона:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=phone_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Автомобиль:").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=car_var).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Проблема:").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=problem_var).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Статус:").grid(row=4, column=0, padx=5, pady=5)
        tk.Entry(dialog, textvariable=status_var).grid(row=4, column=1, padx=5, pady=5)

        # Установка центрирования окна
        dialog_width = 380
        dialog_height = 250
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x_coordinate = (screen_width - dialog_width) / 2
        y_coordinate = (screen_height - dialog_height) / 2
        dialog.geometry("%dx%d+%d+%d" % (dialog_width, dialog_height, x_coordinate, y_coordinate))
        dialog.resizable(False, False)

        # Кнопки "Готово" и "Отмена"
        def update_data():
            # Обновление данных в выбранной строке
            tree.item(selected_item, values=(
                work_info[0], name_var.get(), phone_var.get(), car_var.get(), problem_var.get(), status_var.get()))

            # Обновление данных в базе данных
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE orders SET name=?, phone=?, car=?, problem=?, status=? WHERE id=?
            """, (name_var.get(), phone_var.get(), car_var.get(), problem_var.get(), status_var.get(), work_info[0]))
            connection.commit()

            dialog.destroy()

        tk.Button(dialog, text="Готово", command=update_data).grid(row=5, column=0, padx=(70, 5), pady=5, columnspan=1)
        tk.Button(dialog, text="Отмена", command=dialog.destroy).grid(row=5, column=1, padx=(5, 70), pady=5, columnspan=1)



# Функция для обновления таблицы
def update_table(tree, connection):
    # Очистка таблицы
    for row in tree.get_children():
        tree.delete(row)
    # Получение данных из базы данных
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM orders")
    rows = cursor.fetchall()
    # Вставка данных в таблицу
    for row in rows:
        tree.insert("", "end", values=row)



# Функция для создания вкладки "Заявки"
def create_orders_tab(tab, connection):
    # Создание фрейма для вкладки "Заявки"
    orders_frame = ctk.CTkFrame(tab)
    orders_frame.pack(expand=True, fill='both')

    # Создание заголовков таблицы
    columns = ("ID", "ФИО", "Номер телефона", "Автомобиль", "Проблема", "Статус")

    # Создание и заполнение таблицы
    tree = ttk.Treeview(orders_frame, columns=columns, show="headings", selectmode="browse")
    tree.pack(side="left", fill="both", expand=True)

    # Установка ширины столбцов
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)  # Задайте желаемую ширину

    # Вставка данных в таблицу
    update_table(tree, connection)

    # Проверяем, есть ли данные в таблице перед вызовом adjust_columns_width
    if tree.get_children():
        # Автоматическое подгонка ширины столбцов
        adjust_columns_width(tree)

    # Создание фрейма для кнопок и упаковка его справа от таблицы
    buttons_frame = ctk.CTkFrame(orders_frame)
    buttons_frame.pack(side="top", padx=5, pady=5)

    # Создание кнопок для добавления, обновления и удаления записи и упаковка их во фрейм с кнопками
    button_add = ctk.CTkButton(buttons_frame, text="Добавить", command=lambda: add_entry(tree, connection))
    button_add.pack(side="top", padx=5, pady=5)
    button_edit = ctk.CTkButton(buttons_frame, text="Редактировать", command=lambda: edit_entry(tree, connection))
    button_edit.pack(side="top", padx=5, pady=5)
    button_delete = ctk.CTkButton(buttons_frame, text="Удалить", command=lambda: delete_entry(tree, connection))
    button_delete.pack(side="top", padx=5, pady=5)

# Функция для удаления записи
def delete_entry(tree, connection):
    # Получение выделенной записи
    selected_item = tree.selection()
    if selected_item:
        # Получение ID записи
        item_id = tree.item(selected_item, "values")[0]
        # Удаление записи из базы данных
        cursor = connection.cursor()
        cursor.execute("DELETE FROM orders WHERE id=?", (item_id,))
        connection.commit()
        # Обновление таблицы
        update_table(tree, connection)