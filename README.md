placeholder -- LIS1 protocol listening server
=====

###### version: 20201030a

A flask based project that collects and retransmits Quidel instrument data. The
Sofia2 is a Fluorescent Immunoassay Analyzer and has been used to communicate
testing results via the LIS1/ASTM protocol to this service.

Install/Setup
----------

### Install packages needed to compile python libraries

```bash
sudo apt install git git-flow build-essential autoconf  zlib1g-dev libncursesw5-dev \
libreadline-gplv2-dev libssl-dev libgdbm-dev libc6-dev libsqlite3-dev libbz2-dev \
libffi-dev liblzma-dev postgresql postgresql-contrib \
postgresql-server-dev-all libacl1-dev libpango1.0-0 libcairo2 libpq-dev \
libtiff-dev keychain  uuid-dev libcap-dev libpcre3 libpcre3-dev libjpeg-dev \
automake autotools-dev dh-make debhelper devscripts fakeroot xutils lintian pbuilder
```

### Setup Pyenv : [https://github.com/pyenv/pyenv]

```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
## update shell
# - bash only -
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile
# - zsh only -
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
# reload shell
git clone https://github.com/pyenv/pyenv-update.git $(pyenv root)/plugins/pyenv-update
git clone https://github.com/pyenv/pyenv-doctor.git $(pyenv root)/plugins/pyenv-doctor
git clone https://github.com/doloopwhile/pyenv-register.git $(pyenv root)/plugins/pyenv-register
git clone https://github.com/pyenv/pyenv-which-ext.git $(pyenv root)/plugins/pyenv-which-ext
# Reload shell again
```

### Install python under pyenv

```bash
pyenv install 3.7.9
pyenv virtualenv 3.7.9 lis-env
# Clone "project"
mkdir -p $HOME/projects/placeholder-dev
cd $HOME/projects/placeholder-dev
git clone git@github.com:ua-data7/placeholder.git placeholder
pyenv local lis-env
cd ./placeholder
pip install -r requirements.txt
```

### Setup Config

`cp example.env .env`

Now edit the .env file and change:

- SQLALCHEMY_DATABASE_URI
- SECRET_KEY
- DEFAULT_LIS_NIC
- DEFAULT_LIS_PORT
- SARS_UPLINK_API_URL
- SARS_UPLINK_API_KEY

Note the value for SQLALCHEMY_DATABASE_URI is set as:

`SQLALCHEMY_DATABASE_URI='postgresql://databaseuser:databasepass@localhost:5432/databasename'`

Which might look like:

`SQLALCHEMY_DATABASE_URI='postgresql://agentpi:somesecretpassword@localhost:5432/agentpidb'`

### Setup database

Become postgres admin

`sudo su - postgres`

Create a user for our app (define password)

`createuser agentpi -P`

Create a database for our app

`createdb --template=template1 --encoding=UTF8 --owner=agentpi agentpidb`

### Test service is working

In three separate terminals, launch the following commands:

 1. Terminal #1 *LIS service*
  `flask start_lis_server`
 2. Terminal #2 *Webserver*
  `flask run`
 3. Terminal #3 *Test command*
  `flask send_lis_test`

This should result in a message on flask webserver like so:

```json
{
   'resultTime': '20200727154712',
   'results': 'negative',
   'serialNo': '29000021',
   'testType': 'SARS',
   'vialId': 'TST1-0000001'
}
```

### Usage

?????

### Contributing

 1. Fork it!
 2. Create your feature branch: `git checkout -b my-new-feature`
 3. Commit your changes: `git commit -am 'Add some feature'`
 4. Push to the branch: `git push origin my-new-feature`
 5. Submit a pull request :D

## History

None yet

## Credits

Hagan Franks / Jim Davis / Nirav Merchant / ....

## License

see license documentation [here](LICENSE)
