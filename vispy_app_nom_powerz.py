from multiprocessing import freeze_support

import vispy_app

if __name__ == '__main__':
    freeze_support()
    vispy_app.run_with_args(col_name=('PWR', 'Unix'))