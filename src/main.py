import datetime
import glob
import logging
import os
import shutil

import PySimpleGUI as sg

import config_utils

SAVE_NAME = 'Save Name'

SAVES_LOCATION_TEXT = 'Location'


def main():
    logging.basicConfig(level=logging.INFO)

    if not os.path.isfile('config.ini'):
        config_utils.initialize()

    res = config_utils.config.read('config.ini')
    logging.info(f'Config file: "{res and res[0]}" read')

    path = config_utils.config.get("main", config_utils.SAVEFILE_PATH_C)
    layout = [
        [
            sg.Text(
                f'Save location:\n{path}',
                size=(60, None),
                justification='right',
                relief=sg.RELIEF_RAISED,
                key=SAVES_LOCATION_TEXT
            ),
            sg.VerticalSeparator(),
            sg.Button("settings")
        ],
        [
            sg.HorizontalSeparator(),
        ],
        [
            sg.In(default_text=(datetime.datetime.now().strftime('%d-%m-%y_%H:%M_')), key=SAVE_NAME),
            sg.Button("Save"),
            sg.Button("Load from file"),
        ]
    ]
    window = sg.Window('NEOSaver', layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break
        elif event == 'settings':
            res = ask_for_path(
                title='settings',
                exit_button='Save Settings',
                initial_for_browse=best_effort_find_savefile(),
                initial_path=config_utils.config.get('main', config_utils.SAVEFILE_PATH_C),
                browse_kwargs={'file_types': (("SOL files", ".sol"),)})
            if not res:
                continue
            config_utils.set_c(config_utils.SAVEFILE_PATH_C, res)
            window[SAVES_LOCATION_TEXT].update(f'Save location:\n{res}')
        elif event == 'Save':
            save_name = values[SAVE_NAME]
            save_name = ''.join(c for c in save_name if c.isalnum() or c in '-_() ')
            save_dir = os.path.abspath(f'./saves/{save_name}/')
            os.makedirs(save_dir, exist_ok=True)
            try:
                shutil.copy(config_utils.config.get('main', config_utils.SAVEFILE_PATH_C), save_dir)
            except Exception:
                os.rmdir(save_dir)
                raise
        elif event == 'Load from file':
            res = ask_for_path(
                title='Load from file',
                exit_button='Load',
                initial_for_browse='.',
                browse_kwargs={'file_types': (("SOL files", ".sol"),)})
            if not res:
                continue
            # replace savefile
            # relaunch NS

    window.close()


def ask_for_path(
        title,
        exit_button='Save',
        initial_for_browse=None,
        initial_path='',
        browse=sg.FileBrowse,
        browse_kwargs=None,
):
    if browse_kwargs is None and browse is sg.FileBrowse:
        browse_kwargs = {'file_types': sg.FILE_TYPES_ALL_FILES}
    else:
        browse_kwargs = {}

    layout = [
        [
            sg.Text('Save Folder:'),
            sg.In(size=(60, 3), key='-FOLDER-', default_text=initial_path),
            browse(initial_folder=initial_path or initial_for_browse, **browse_kwargs)
        ],
        [
            sg.Button('Cancel'),
            sg.Button(exit_button),
        ],
    ]
    window = sg.Window(title, layout=layout, modal=True, )

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':
            window.close()
            return ''
        if event == exit_button:
            window.close()
            return values['-FOLDER-']


def best_effort_find_savefile():
    path1 = r'%APPDATA%\Macromedia\Flash Player\#SharedObjects'
    path2 = r'*\localhost\SteamLibrary\steamapps\common\NEO Scavenger\NEOScavenger.exe\nsSGv1.sol'
    expanded = os.path.expandvars(path1)
    joined = os.path.join(expanded, path2)
    g = glob.glob(joined)
    return g and g[0]


if __name__ == '__main__':
    main()
