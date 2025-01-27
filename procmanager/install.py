import os
import tempfile
import requests

from procmanager.config import HOME_BIN
from procmanager.config import KINETIC_BINARY_URL_X64


# path = ~/.config/systemd/user/kin.service
kin_dot_service_file= """
[Unit]
Description=A process runner

[Service]
Type=simple
ExecStart=%h/bin/kin serve
PrivateTmp=true
Restart=Always

[Install]
# WantedBy=default.target
WantedBy=multi-user.target
"""


def install():
    systemctl_path = os.path.expanduser('~/.config/systemd/user/')
    os.makedirs(systemctl_path, exist_ok=True)
    with open(f'{systemctl_path}/kin.service', 'w') as f:
        f.write(kin_dot_service_file)
    print('Enabling linger for systemctl...')
    os.system('loginctl enable-linger $(whoami)') 
    print('Reloading systemctl')
    os.system('systemctl --user daemon-reload')
    os.system('systemctl --user enable kin')
    os.system('systemctl --user restart kin')
    os.system('systemctl --user status kin')


def do_update():
    # 1 dl relevant binary from gh
    save_path = os.path.expanduser('~/bin')
    os.makedirs(save_path, exist_ok=True)
    
    # 2 copy to ~/bin/kin
    bin_path = os.path.join(f'{HOME_BIN}', 'kin')
    url_path = KINETIC_BINARY_URL_X64
    print(f'Downloading from {url_path}')
    #with urllib.request.urlopen(KINETIC_BINARY_URL_X64) as response,\ needs headrs
    #  open(bin_path, 'wb') as f:
    #    shutil.copyfileobj(response, f)
    # subprocess.run(f'curl -O https://kinetic.icedb.info/x64/kin', cwd=save_path)


    r = requests.get(f'{KINETIC_BINARY_URL_X64}')
    #with open(bin_path, 'wb') as f:
    #    f.write(r.content)
    with tempfile.NamedTemporaryFile(delete=False) as fp:  # delete_on_close avail 3.12+
        fp.write(r.content)
    os.chmod(fp.name, 0o744)
    os.rename(fp.name, bin_path)

    # Refresh the service file and ensure it is running and refresh the binary for systemd.
    install()


if __name__ == '__main__':
    install()
