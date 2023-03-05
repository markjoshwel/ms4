"""
This is unpolished and unfinished. Hic sunt dracones.
See the README for an explanation.
"""

from json import JSONDecodeError
from pathlib import Path

import flet as ft  # type: ignore

import scribbplyscrobbply


def gui(page: ft.Page) -> None:
    page.title = "scribbplyscrobbply"

    elm_global_status = ft.Text("Ready.")

    def status(mesg: str) -> None:
        elm_global_status.value = mesg
        elm_global_status.update()

    def act_on_file_pick(e: ft.FilePickerResultEvent) -> None:
        elm_file_select_list.value = (
            ("Selected:\n" + "\n".join([f.name for f in e.files]))
            if e.files
            else "No files selected."
        )
        elm_file_select_list.update()

        status("Upload 1")

        if not e.files:
            return

        for file in e.files:
            status(f"Upload {file.name}")
            elm_file_select.upload(
                [
                    ft.FilePickerUploadFile(
                        file.name, upload_url=page.get_upload_url(f"{file.name}", 600)
                    )
                ]
            )

        status("Upload 2")

    elm_file_select = ft.FilePicker(on_result=act_on_file_pick)
    elm_file_select_button = ft.ElevatedButton(
        "Select Files",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: elm_file_select.pick_files(
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
            allow_multiple=True,
        ),
    )
    elm_file_select_list = ft.Text("No files selected.")

    def act_min_s_verify(e: ft.ControlEvent) -> None:
        if isinstance(e.data, str) and (not e.data.isdigit()):
            e.control.error_text = "Invalid input! Must be a number/integer."

        else:
            e.control.error_text = None

        e.control.update()

    elm_min_s_field = ft.TextField(
        label="Minimum Seconds", hint_text="30", on_change=act_min_s_verify, dense=True
    )
    elm_min_s_field.value = "30"

    elm_format_dropdown = ft.Dropdown(
        label="Format Type",
        options=[
            ft.dropdown.Option(tf.value) for tf in scribbplyscrobbply.TakeoutFormats
        ],
        tooltip="\n".join(
            [
                "Type of export.",
                f"'{scribbplyscrobbply.TakeoutFormats.JSON_SCRUBBLER_WPF.value}' for Last.fm-Scrubbler-WPF",
            ]
        ),
        dense=True,
    )
    elm_format_dropdown.value = scribbplyscrobbply.TakeoutFormats.JSON_SCRUBBLER_WPF.value

    def act_process(e: ft.ControlEvent) -> None:
        # TODO
        page.launch_url("hello.txt")

    elm_process_button = ft.ElevatedButton(
        "Process",
        icon=ft.icons.DOWNLOAD_DONE,
        on_click=act_process,
    )

    # Layout
    page.overlay.append(elm_file_select)

    page.add(
        ft.Column(
            [
                elm_file_select_button,
                elm_format_dropdown,
                elm_min_s_field,
            ]
        )
    )
    page.add(ft.Column([elm_file_select_list]))
    page.add(ft.Column([elm_process_button, elm_global_status]))


ft.app(target=gui, view=ft.WEB_BROWSER, upload_dir="uploads", assets_dir="uploads")
