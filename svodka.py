import customtkinter as ctk
from tkinter import ttk
import sqlite3
import tkinter as tk
from tkinter import messagebox

from parts_tab import update_parts_table, adjust_columns_width

connection = sqlite3.connect('repair_shop.db')
cursor = connection.cursor()
# Функция для обновления таблицы
def update_table_sv(tree, connection):
    # Очистка таблицы
    for row in tree.get_children():
        tree.delete(row)
    # Получение данных из базы данных
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, phone, car, date_start, date_end, stage FROM orders WHERE status=\"Принято\"")
    rows = cursor.fetchall()
    # Вставка данных в таблицу
    for row in rows:
        tree.insert("", "end", values=row)

def create_summary_tab(tab, tree):
    # Создание фрейма для вкладки "Сводка заказов"
    summary_frame = ctk.CTkFrame(tab)
    summary_frame.pack(expand=True, fill='both')

    # Создаем метку для текста "Выбрать детали"
    clients_label = tk.Label(summary_frame, text="Выберите клиента для формирования заказа на ремонт его автомобиля.")
    clients_label.pack(side="top", pady=10)

    # Создание кнопки выбора клиента
    select_client_button = ctk.CTkButton(summary_frame, text="Выбрать клиента",
                                         command=lambda: (select_client(selected_client_text, selected_client_text_var,
                                                                       connection),update_parts_table(parts_tree, connection)))
    select_client_button.pack(pady=10)

    # Создание рамок для отображения информации о клиенте и его проблеме
    selected_client_frame = tk.Frame(summary_frame, bd=2, relief=tk.GROOVE)
    selected_client_frame.pack(pady=5, padx=350, fill=tk.X)
    # Виджет с прокруткой текста для отображения информации о клиенте
    selected_client_text = tk.Text(selected_client_frame, wrap="word", height=5)
    selected_client_text.pack(side="left", fill="both", expand=True)

    # Виджеты для отображения выбранного клиента и его проблемы в рамках
    selected_client_text_var = tk.StringVar()
    selected_client_label = tk.Label(selected_client_frame, textvariable=selected_client_text_var)
    selected_client_label.pack(pady=5, padx=5, anchor="w")
    def write_to_text():
        data = f"Выбранный клиент:  \n\nПроблема:  "
        selected_client_text.tag_configure("fontstyle", font=("Arial", 16))  # Настройка шрифта
        selected_client_text.insert("end", data + "\n\n",
                                    "fontstyle")  # Применение настроенного шрифта к вставленному тексту
        return data
    datasv = write_to_text()
    #----------------------------------------------------------------------------------------------#
    # Создаем метку для текста "Выбрать детали"
    detail_label = tk.Label(summary_frame, text="Выберите необходимые для ремонта запчасти.")
    detail_label.pack(padx=(1,480),pady=10)

    # Фрейм для отображения выбранных деталей
    selected_details_frame = tk.Frame(summary_frame, bd=2, relief=tk.GROOVE)
    selected_details_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=(0, 10))

    # Создание таблицы с запчастями
    parts_columns = ("ID", "Компания", "Артикул", "Описание", "Количество", "Цена")
    parts_tree = ttk.Treeview(selected_details_frame, columns=parts_columns, show="headings", selectmode="browse")
    parts_tree.pack(side="left", fill="both", expand=True)

    # Словарь для установки ширины столбцов
    column_widths = {
        "ID": 30,
        "Компания": 100,
        "Артикул": 100,
        "Описание": 240,
        "Количество": 60,
        "Цена": 50
    }
    # Установка ширины столбцов
    for col, width in column_widths.items():
        parts_tree.column(col, width=width, anchor="center")

    # Установка текста для заголовков
    for col in parts_columns:
        parts_tree.heading(col, text=col)

    # Вставка данных в таблицу
    update_parts_table(parts_tree, connection)  # Функция, которая обновляет таблицу с запчастями

    # Создание фрейма для кнопок
    button_frame = tk.Frame(summary_frame)
    button_frame.pack(side="top", pady=5)

    # Создание кнопки для выбора деталей
    add_detail_button = ctk.CTkButton(button_frame, text="Добавить деталь", fg_color="#008c08",
                                      command=lambda: add_detail(selected_parts_listbox, parts_tree,connection))
    add_detail_button.pack(side="left", padx=(0, 5))

    # Создание кнопки для удаления детали
    remove_button = ctk.CTkButton(button_frame, text="Удалить деталь" , fg_color="#b80000",
                                  command=lambda: remove_detail(selected_parts_listbox, parts_tree,connection))
    remove_button.pack(side="left", padx=(5, 0))

    # Фрейм для отображения выбранных деталей
    selected_details_frame = tk.Frame(summary_frame, bd=2, relief=tk.GROOVE)
    selected_details_frame.pack(pady=5)

    # Создаем Listbox для отображения выбранных деталей
    selected_parts_listbox = tk.Listbox(selected_details_frame, width=50, height=10)
    selected_parts_listbox.pack(side="top", fill="both", expand=True)

    def add_detail(selected_parts_listbox, parts_tree, connection):
        # Получение текста из виджета selected_client_text
        text_data = selected_client_text.get("1.0", "end")
        if(text_data[21] != 'П'):
            selected_item = parts_tree.focus()
            if selected_item:
                selected_part = parts_tree.item(selected_item)['values']
                # Исключаем предпоследний элемент из данных и формируем строку
                selected_part_str = ', '.join(map(str, selected_part[:-2])) + ', ' + str(selected_part[-1])

                cursor = connection.cursor()
                cursor.execute("SELECT quantity FROM parts WHERE id = ?", (selected_part[0],))
                quantity = cursor.fetchone()[0]
                if (int)(quantity) > 0:
                    # Уменьшаем количество выбранного элемента в базе данных на 1
                    decrease_quantity(selected_part[0], connection)
                    selected_parts_listbox.insert(tk.END, selected_part_str)
                else:
                    messagebox.showwarning("Ошибка", f"Недостаточное количество на складе")
        else:
            messagebox.showwarning("Ошидка", f"Сначало необходимо выбрать клиента")

    def remove_detail(selected_parts_listbox, parts_tree, connection):
        text_data = selected_client_text.get("1.0", "end")
        if (text_data[21] != 'П'):
            try:
                # Получаем выбранный элемент из таблицы
                selected_item = parts_tree.focus()
                if selected_item:
                    # Получаем данные выбранного элемента
                    selected_part = parts_tree.item(selected_item)['values']
                    # Исключаем предпоследний элемент из данных и формируем строку
                    selected_string = ', '.join(map(str, selected_part[:-2])) + ', ' + str(selected_part[-1])
                    # Пытаемся найти строку в Listbox и удалить её
                    for i in range(selected_parts_listbox.size()):
                        if selected_string == selected_parts_listbox.get(i):
                            selected_parts_listbox.delete(i)
                            # Увеличиваем количество выбранного элемента в базе данных на 1
                            increase_quantity(selected_part[0], connection)
                            break
            except Exception as e:
                # Если произошла ошибка, показываем предупреждение
                messagebox.showwarning("Ошибка", f"Ошибка удаления: {str(e)}")
        else:
            messagebox.showwarning("Ошибка", f"Сначало необходимо выбрать клиента")

    def decrease_quantity(part_id, connection):
        try:
            # Уменьшаем количество выбранного элемента на 1 в базе данных
            cursor.execute("UPDATE parts SET quantity = quantity - 1 WHERE id = ?", (part_id,))
            connection.commit()  # Применяем изменения
            update_parts_table(parts_tree, connection)
        except sqlite3.Error as e:
            messagebox.showwarning("Ошибка", f"Ошибка при уменьшении количества: {str(e)}")

    def increase_quantity(part_id, connection):
        try:
            cursor = connection.cursor()
            # Увеличиваем количество выбранного элемента на 1 в базе данных
            cursor.execute("UPDATE parts SET quantity = quantity + 1 WHERE id = ?", (part_id,))
            connection.commit()  # Применяем изменения
            update_parts_table(parts_tree, connection)
        except sqlite3.Error as e:
            print("Ошибка при увеличении количества:", e)

    #----------------------------------------------------------------------------------------------#
    def clear_widgets():
        selected_client_text.delete("1.0", tk.END)  # Очистка Text виджета
        data = f"Выбранный клиент:  \n\nПроблема:  "
        selected_client_text.tag_configure("fontstyle", font=("Arial", 16))  # Настройка шрифта
        selected_client_text.insert("end", data + "\n\n",
                                    "fontstyle")  # Применение настроенного шрифта к вставленному тексту
        selected_parts_listbox.delete(0, tk.END)  # Очистка Listbox

    # Создание кнопки для формирования заказа
    create_order_button = ctk.CTkButton(summary_frame, text="Сформировать заказ", height=100, width=300, font=("Arial", 22, "bold"), fg_color="green",
                                        command=lambda: (open_order_window(selected_client_text, selected_parts_listbox, tree), clear_widgets()))
    create_order_button.pack(pady=100)

def select_client(selected_client_text,selected_client_text_var,connection):
    # Функция для записи данных в виджет с прокруткой текста
    def write_to_text(data):
        selected_client_text.delete("1.0", "end")
        selected_client_text.tag_configure("fontstyle", font=("Arial", 16))  # Настройка шрифта
        selected_client_text.insert("end", data + "\n\n",
                                    "fontstyle")  # Применение настроенного шрифта к вставленному тексту

    # Создание нового окна для выбора клиента
    client_window = tk.Toplevel()
    client_window.title("Выбор клиента")

    # Установка центрирования окна
    dialog_width = 900
    dialog_height = 200
    screen_width = client_window.winfo_screenwidth()
    screen_height = client_window.winfo_screenheight()
    x_coordinate = (screen_width - dialog_width) / 2
    y_coordinate = (screen_height - dialog_height) / 2
    client_window.geometry("%dx%d+%d+%d" % (dialog_width, dialog_height, x_coordinate, y_coordinate))
    client_window.resizable(False, False)

    # Создание таблицы с клиентами
    columns = ("ID", "ФИО", "Номер телефона", "Автомобиль", "Проблема", "Статус", "Дата приема", "Дата завершения", "Этап работы")
    used_columns = (columns[0], columns[1], columns[2], columns[3], columns[6], columns[7], columns[8])

    client_tree = ttk.Treeview(client_window, columns=used_columns, show="headings", selectmode="browse")
    client_tree.pack(side="left", fill="both", expand=True)

    # Установка ширины столбцов
    for col in used_columns:
        client_tree.column(col, width=100)

    # Установка текста для заголовков
    for col in used_columns:
        client_tree.heading(col, text=col)

    # Вставка данных в таблицу
    update_table_sv(client_tree, connection)
    if client_tree.get_children():
        # Автоматическое подгонка ширины столбцов
        adjust_columns_width(client_tree)

    # Функция для выбора клиента
    def select():
        selected_item = client_tree.focus()
        if selected_item:
            selected_client = client_tree.item(selected_item)['values']
            selected_client_text_var.set(f"Выбранный клиент: {selected_client[1]}")
            problem = get_problem(connection, selected_client[0])
            write_to_text(f"Выбранный клиент: {selected_client[1]}\n\nПроблема: {problem}")
            client_window.destroy()

    # Кнопка "Принять"
    select_button = tk.Button(client_window, text="Принять", command=select)
    select_button.pack(side="top", padx=5, pady=1)
    # Кнопка "Закрыть"
    select_button = tk.Button(client_window, text="Закрыть", command=client_window.destroy)
    select_button.pack(side="top", padx=5, pady=1)

def get_problem(connection, client_id):
    cursor = connection.cursor()
    cursor.execute("SELECT problem FROM orders WHERE id=?", (client_id,))
    problem = cursor.fetchone()
    if problem:
        return problem[0]
    else:
        return "Проблема не найдена"


def open_order_window(selected_client_text, selected_parts_listbox, tree):
    text_data = selected_client_text.get("1.0", "end")
    if (text_data[21] != 'П'):
        # Создаем новое окно для формирования заказа
        order_window = tk.Toplevel()
        order_window.title("Формирование заказа")

        # Установка центрирования окна
        dialog_width = 500
        dialog_height = 480
        screen_width = order_window.winfo_screenwidth()
        screen_height = order_window.winfo_screenheight()
        x_coordinate = (screen_width - dialog_width) / 2
        y_coordinate = (screen_height - dialog_height) / 2
        order_window.geometry("%dx%d+%d+%d" % (dialog_width, dialog_height, x_coordinate, y_coordinate))
        order_window.resizable(False, False)

        # Добавляем метку для отображения выбранного клиента
        selected_client_label = tk.Label(order_window, text="Выбранный клиент с проблемой:", font=("Arial", 18))
        selected_client_label.pack(pady=10)

        # Получаем текст из виджета selected_client_text
        client_text_content = selected_client_text.get("1.0", "end-1c")

        selected_client_display = tk.Text(order_window, height=5, width=50)
        selected_client_display.insert(tk.END, client_text_content)
        selected_client_display.pack(pady=10)

        # Увеличение шрифта
        selected_client_display.config(font=("Arial", 16))


        # Добавляем метку для отображения выбранных деталей
        selected_parts_label = tk.Label(order_window, text="Выбранные детали:", font=("Arial", 16))
        selected_parts_label.pack(pady=10)

        # Добавляем текстовое поле для отображения выбранных деталей
        selected_parts_text = tk.Text(order_window, height=10, width=50, font=("Arial", 16))
        selected_parts_text.pack(pady=10)
        selected_parts_text.insert("end", "\n".join(selected_parts_listbox.get(0, "end")))

        # Вычисляем общую стоимость
        total_cost = sum(int(detail.split(", ")[-1]) for detail in selected_parts_listbox.get(0, "end"))

        # Добавляем метку для отображения общей стоимости
        total_cost_label = tk.Label(order_window, text=f"Общая стоимость: {total_cost}", font=("Arial", 18))
        total_cost_label.pack(pady=10)

        # Вставка данных в таблицу
        update_parts_table(tree, connection)
    else:
        messagebox.showwarning("Ошибка", f"Сначало необходимо выбрать клиента")

