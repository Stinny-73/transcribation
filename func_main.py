import flet as ft
import threading
import os
from recording import Recording
from promt import transl_p, summ_p
from ai_api_client import ai_request
import asyncio
import platform

def main(page: ft.Page):
    page.title = "Smart Notes"
    page.window_width = 900
    page.window_height = 650
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F5F7FA"

    recorder = Recording()
    recording = False
    file_counter = 0

    # --- файловая логика ---
    FILES_DIR = "notes"
    os.makedirs(FILES_DIR, exist_ok=True)

    current_file_path = None
    is_new_file = False
    active_file_button = None
    file_picker_mode = None
    
    def file_picker_result(e: ft.FilePickerResultEvent):
        nonlocal current_file_path, is_new_file, file_picker_mode
        
        #print(f"📂 FilePicker result: mode={file_picker_mode}, files={e.files}, path={e.path}")

        # ---------- OPEN ----------
        if file_picker_mode == "open":
            if not e.files:
                print("⚠️ Файл не выбран")
                return

            path = e.files[0].path
            print(f"✓ Выбран файл: {path}")
            
            if not path.lower().endswith(".txt"):
                print("⚠️ Файл не .txt")
                return

            try:
                with open(path, "r", encoding="utf-8") as f:
                    enter.value = f.read()

                current_file_path = path
                is_new_file = False
                add_file_to_list(path)
                
                # Подсветка
                for c in files_list.controls:
                    if hasattr(c, 'data') and c.data == path:
                        highlight_file(c.content.controls[0])  # Обновлено для Row
                        break
                
                page.update()
                print(f"✓ Файл открыт успешно")
            except Exception as ex:
                print(f"✗ Ошибка открытия: {ex}")

        # ---------- SAVE ----------
        elif file_picker_mode == "save":
            if not e.path:
                print("⚠️ Путь для сохранения не выбран")
                return

            try:
                with open(e.path, "w", encoding="utf-8") as f:
                    f.write(enter.value or "")

                current_file_path = e.path
                is_new_file = False
                add_file_to_list(e.path)
                page.update()
                print(f"✓ Файл сохранен: {e.path}")
            except Exception as ex:
                print(f"✗ Ошибка сохранения: {ex}")
                
    file_picker = ft.FilePicker(on_result=file_picker_result)
    page.overlay.append(file_picker)
    
    # --- интерфейс элементов ---
    files_list = ft.ListView(expand=True, spacing=5)

    enter = ft.TextField(
        multiline=True,
        border_color="#E5E7EB",
        focused_border_color="#3B82F6",
        hint_text="Введите текст...",
        hint_style=ft.TextStyle(color="#9CA3AF"),
        text_style=ft.TextStyle(size=14, color="#1F2937"),
        filled=True,
        bgcolor="#FFFFFF",
    )

    # --- запись речи ---
    def toggle_recording(e):
        nonlocal recording
        recording = not recording

        if recording:
            recorder.clear()
            recorder.flag = True

            thread = threading.Thread(target=recorder.record)
            thread.start()
            recorder._thread = thread

            record_btn.bgcolor = "#EF4444"
            record_btn.icon = ft.Icons.STOP
            record_btn.text = "Прервать"
            page.update()

        else:
            recorder.flag = False
            if hasattr(recorder, "_thread"):
                recorder._thread.join()

            record_btn.bgcolor = "#F59E0B"
            record_btn.icon = ft.Icons.HOURGLASS_EMPTY
            record_btn.text = "Загрузка.."
            page.update()

            text = recorder.transcribe_audio_v2()

            record_btn.text = "Запись"
            record_btn.icon = ft.Icons.MIC
            record_btn.bgcolor = "#10B981"

            if text and "Нет аудиоданных" not in text:
                enter.value = (enter.value or "") + str(text) + " "
            page.update()

    def run_ai_task(e, prompt_func, task_name="Задача"):
        btn = e.control
        original_text = btn.text
        original_bgcolor = btn.bgcolor
        original_icon = btn.icon
        
        btn.text = "Загрузка.."
        btn.bgcolor = ft.Colors.GREY_500
        btn.icon = ft.Icons.HOURGLASS_EMPTY
        btn.disabled = True
        e.page.update()

        try:
            user_input = enter.value
            if not user_input.strip():
                e.page.snack_bar = ft.SnackBar(ft.Text("Поле пустое"))
                e.page.snack_bar.open = True
                e.page.update()
                return

            result = [None]
            def worker():
                result[0] = ai_request(prompt_func(user_input))

            thread = threading.Thread(target=worker)
            thread.start()
            thread.join()

            if result[0] is not None:
                enter.value = result[0]
                e.page.update()

        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {str(ex)}"))
            e.page.snack_bar.open = True
            e.page.update()

        finally:
            btn.text = original_text
            btn.bgcolor = original_bgcolor
            btn.icon = original_icon
            btn.disabled = False
            e.page.update()

    # --- кнопки управления ---
    record_btn = ft.ElevatedButton(
        "Запись",
        icon=ft.Icons.MIC,
        bgcolor="#10B981",
        color=ft.Colors.WHITE,
        icon_color=ft.Colors.WHITE,
        height=50,
        on_click=toggle_recording,
        expand=1,
    )

    translate_btn = ft.ElevatedButton(
        "Перевод",
        icon=ft.Icons.TRANSLATE,
        bgcolor="#8B5CF6",
        color=ft.Colors.WHITE,
        icon_color=ft.Colors.WHITE,
        height=50,
        on_click=lambda e: run_ai_task(e, transl_p, "Перевод"),
        expand=1,
    )

    summarize_btn = ft.ElevatedButton(
        "Обобщить",
        icon=ft.Icons.SUMMARIZE,
        bgcolor="#F59E0B",
        color=ft.Colors.WHITE,
        icon_color=ft.Colors.WHITE,
        height=50,
        on_click=lambda e: run_ai_task(e, summ_p, "Обобщение"),
        expand=1,
    )

    # --- работа с файлами ---
    file_counter = len(os.listdir(FILES_DIR))
    active_file_button = None

    def highlight_file(button):
        nonlocal active_file_button
        if active_file_button and active_file_button is not button:
            active_file_button.bgcolor = None
            active_file_button.update()
        button.bgcolor = "#E5E7EB"
        button.update()
        active_file_button = button

    def remove_file_from_list(container):
        """Удаляет файл из списка (не из файловой системы)"""
        nonlocal current_file_path, active_file_button
        
        # Если удаляем активный файл, очищаем состояние
        if hasattr(container, 'data') and container.data == current_file_path:
            current_file_path = None
            active_file_button = None
            enter.value = ""
        
        # Удаляем из списка
        files_list.controls.remove(container)
        page.update()

    def add_file_to_list(filepath):
        """Добавляет файл в левую панель с кнопкой удаления"""
        filename = os.path.basename(filepath)
        
        # Проверяем, не добавлен ли уже файл
        for c in files_list.controls:
            if hasattr(c, 'data') and c.data == filepath:
                return

        # Кнопка с названием файла
        btn = ft.TextButton(
            f"📄 {filename}",
            style=ft.ButtonStyle(
                color="#1F2937",
                text_style=ft.TextStyle(size=16)
            ),
            expand=True,
        )

        def on_file_click(e):
            nonlocal current_file_path, is_new_file
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    enter.value = f.read()
                current_file_path = filepath
                is_new_file = False
                highlight_file(btn)
                page.update()
            except Exception as ex:
                print(f"Ошибка открытия файла: {ex}")

        btn.on_click = on_file_click

        # Кнопка удаления
        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color="#EF4444",
            icon_size=18,
            tooltip="Убрать из списка",
        )

        # Контейнер для всей строки
        container = ft.Container(
            content=ft.Row(
                controls=[btn, delete_btn],
                spacing=5,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            width=220,
            height=45,
            data=filepath,
        )

        # Привязываем удаление к кнопке
        delete_btn.on_click = lambda e: remove_file_from_list(container)

        files_list.controls.append(container)
        page.update()

    def create_file(e=None):
        """Создает новый файл"""
        nonlocal file_counter, current_file_path, is_new_file
        file_counter += 1
        filename = f"Запись{file_counter}.txt"
        filepath = os.path.join(FILES_DIR, filename)

        with open(filepath, "w", encoding="utf-8"):
            pass

        add_file_to_list(filepath)

        # Находим кнопку последнего добавленного файла
        last_container = files_list.controls[-1]
        last_btn = last_container.content.controls[0]  # Первый элемент Row
        
        with open(filepath, "r", encoding="utf-8") as f:
            enter.value = f.read()
        current_file_path = filepath
        is_new_file = False
        highlight_file(last_btn)
        page.update()

    def save_current_file(e):
        """Сохранение файла через FilePicker (кроссплатформенно)"""
        nonlocal file_picker_mode
        
        if is_new_file or not current_file_path:
            # Используем FilePicker на всех платформах
            file_picker_mode = "save"
            file_picker.save_file(file_name="Запись.txt", allowed_extensions=["txt"])
        else:
            try:
                with open(current_file_path, "w", encoding="utf-8") as f:
                    f.write(enter.value or "")
                print(f"✓ Сохранен: {os.path.basename(current_file_path)}")
            except Exception as ex:
                print(f"✗ Ошибка: {ex}")

    # --- загрузка существующих файлов ---
    for fn in sorted(os.listdir(FILES_DIR)):
        if fn.lower().endswith(".txt"):
            add_file_to_list(os.path.join(FILES_DIR, fn))

    save_btn = ft.ElevatedButton(
        "Сохранить",
        icon=ft.Icons.SAVE,
        bgcolor="#3B82F6",
        color=ft.Colors.WHITE,
        icon_color=ft.Colors.WHITE,
        height=50,
        expand=1,
        on_click=save_current_file,
    )

    buttons_row = ft.Row(
        [record_btn, translate_btn, summarize_btn, save_btn],
        spacing=15,
    )

    # --- интерфейс ---
    page.add(
        ft.Row(
            [
                # Левая панель
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Text(
                                            "Файлы",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color="#1F2937",
                                        ),
                                        ft.PopupMenuButton(
                                            icon=ft.Icons.ADD,
                                            icon_color="#1F2937",
                                            icon_size=20,
                                            tooltip="Добавить файл",
                                            items=[
                                                ft.PopupMenuItem(
                                                    text="📄 Создать новый файл",
                                                    on_click=create_file,
                                                )
                                            ],
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    expand=True,
                                ),
                                padding=ft.padding.only(bottom=10),
                            ),
                            ft.Divider(color="#E5E7EB", height=1),
                            files_list,
                        ]
                    ),
                    width=220,
                    bgcolor="#FFFFFF",
                    padding=20,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=10,
                        color=ft.Colors.with_opacity(0.1, "#000000"),
                    ),
                ),
                # Правая часть
                ft.Container(
                    content=ft.Column(
                        [
                            buttons_row,
                            ft.Container(
                                content=enter,
                                expand=True,
                                margin=ft.margin.only(top=15),
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=5,
                                    color=ft.Colors.with_opacity(0.05, "#000000"),
                                ),
                                border_radius=8,
                            ),
                        ]
                    ),
                    padding=20,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=0,
        )
    )


ft.app(target=main)