import datetime
import glob
import logging
import os
import shutil
import subprocess
from typing import Union

import PySimpleGUI as sg

import config_utils as cf

SET_GAMEPATH_BUTTON = 'set game path'
SET_SAVEPATH_BUTTON = 'set save path'
MILLISECONDS_PER_SECOND = 1000

SAVE_NAME = 'Save Name'

SAVES_LOCATION_TEXT = 'Location'


def main():
    if not os.path.isfile('config.ini'):
        cf.initialize()

    res = cf.config.read('config.ini')
    log_level = cf.config.getint('main', 'Logging Level')
    logging.basicConfig(level=log_level)
    logging.info(f'Config file: "{res and res[0]}" read')

    path = cf.config.get("main", cf.SAVEFILE_PATH_C)
    savename_prefix = generate_savename_prefix()
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
            sg.Button(SET_SAVEPATH_BUTTON),
            sg.Button(SET_GAMEPATH_BUTTON),
        ],
        [
            sg.HorizontalSeparator(),
        ],
        [
            sg.In(default_text=savename_prefix, key=SAVE_NAME),
            sg.Button('Save'),
            sg.Button('Load from file'),
        ]
    ]
    window = sg.Window('NEOSaver', layout, return_keyboard_events=True)
    neo_process: Union[None, subprocess.Popen] = None

    while True:
        event, values = window.read(60 * MILLISECONDS_PER_SECOND)

        if event == sg.WIN_CLOSED:
            break
        elif event == SET_SAVEPATH_BUTTON:
            res = ask_for_path(
                title=SET_SAVEPATH_BUTTON,
                exit_button='Save Settings',
                initial_for_browse=best_effort_find_savefile(),
                initial_path=cf.config.get('main', cf.SAVEFILE_PATH_C),
                browse_kwargs={'file_types': (('SOL files', '.sol'),)})
            if not res:
                continue
            cf.set_c(cf.SAVEFILE_PATH_C, res)
            window[SAVES_LOCATION_TEXT].update(f'Save location:\n{res}')
        elif event == SET_GAMEPATH_BUTTON:
            res = ask_for_path(
                title=SET_GAMEPATH_BUTTON,
                exit_button='Save Settings',
                browse_kwargs={'file_types': (('EXE files', '.exe'),)}
            )
            if not res:
                continue
            cf.set_c(cf.GAMEFILE_PATH_C, res)
        elif event == 'Save':
            save_name = values[SAVE_NAME]
            save_name = ''.join(c for c in save_name if c.isalnum() or c in '-_() ')
            save_dir = os.path.abspath(f'./saves/{save_name}/')
            os.makedirs(save_dir, exist_ok=True)
            try:
                shutil.copy(cf.config.get('main', cf.SAVEFILE_PATH_C), save_dir)
            except Exception:
                os.rmdir(save_dir)
                raise
        elif event == 'Load from file':
            res = ask_for_path(
                title='Load from file',
                exit_button='Load',
                initial_for_browse='./saves/',
                browse_kwargs={'file_types': (("SOL files", ".sol"),)})
            if not res:
                continue

            logging.debug('Killing Neoscavenger.exe...')
            err = (neo_process and neo_process.terminate()) or os.system('taskkill /IM Neoscavenger.exe')
            if err is not None and err == 0:
                logging.debug(f'Killed Neoscavenger.exe with {err=}')
            elif err and err == 128:
                logging.debug('Neoscavenger.exe was already dead')

            shutil.copyfile(res, cf.config.get('main', cf.SAVEFILE_PATH_C))

            logging.debug('Starting Neoscavenger.exe...')
            neo_process = subprocess.Popen(cf.config.get("main", cf.GAMEFILE_PATH_C))
            if neo_process is None:
                raise RuntimeError("Couldn't start Neoscavenger.exe")
            logging.debug(f'Started Neoscavenger.exe')

        elif event == sg.TIMEOUT_EVENT:
            full_savename: str = values[SAVE_NAME]
            if full_savename.startswith(savename_prefix):
                savename = full_savename.removeprefix(savename_prefix)
                new_prefix = generate_savename_prefix()
                window[SAVE_NAME].update(new_prefix + savename)
                logging.debug(f'Updated prefix of {full_savename} to {new_prefix}')
        elif event == 'Escape:27':
            window.send_to_back()

    window.close()


def generate_savename_prefix():
    return datetime.datetime.now().strftime('%d-%m-%y_%H:%M_')


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
