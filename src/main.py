import os

import PySimpleGUI as sg

import config_utils

NEO_SCAVENGER_EXE = r'%APPDATA%\\Macromedia\\Flash Player\\#SharedObjects\\'


def main():
    isfile = os.path.isfile('config.ini')
    print(isfile)
    if not isfile:
        config_utils.make_config()
    config_utils.config.read('config.ini')

    folder_name = config_utils.config.get('main', config_utils.NEO_EXE_FOLDER_C)
    layout = [
        [sg.Text(f"Save location:\n{folder_name}", size=(60, None), justification='right', relief=sg.RELIEF_RAISED),
         sg.VerticalSeparator(),
         sg.Button("settings")],
        [sg.HorizontalSeparator()],
    ]
    window = sg.Window("NEOSaver", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break
        if event == "settings":
            open_settings_window()

    window.close()


def open_settings_window():
    initial_for_browse = os.path.expandvars(NEO_SCAVENGER_EXE)
    folder_from_config = config_utils.config.get('main', config_utils.NEO_EXE_FOLDER_C)
    layout = [[sg.Text("Save Folder"),
               sg.In(size=(60, 3), enable_events=True, key="-FOLDER-", default_text=folder_from_config),
               sg.FolderBrowse(initial_folder=initial_for_browse)], [sg.Button("Cancel"), sg.Button("Save Settings")]]
    window = sg.Window("settings", layout=layout, modal=True, )
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Cancel":
            break
        if event == "Save Settings":
            config_utils.set_config(config_utils.NEO_EXE_FOLDER_C, values["-FOLDER-"])
            break

    window.close()


if __name__ == '__main__':
    main()
