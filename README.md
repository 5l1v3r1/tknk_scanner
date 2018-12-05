tknk_scanner
===
The original code of a malware must be scanned using YARA rules after processing with a debugger (or other means) to account for obfuscated malware binaries. This is a complicated process and requires an extensive malware analysis environment. The tknk_scanner is a community-based integrated malware identification system, which aims to easily identify malware families by automating this process using an integration of open source community-based tools and freeware. The original malware code can be scanned with  with your own YARA rules by submitting the malware in PE format to the scanner. tknk_scanner can thus support surface analysis performed by SOC operators, CSIRT members, and malware analysts.

![tknk02](https://user-images.githubusercontent.com/18203311/49505070-4cc12080-f8be-11e8-8904-3a02e72d3882.png)

## Features
* Automatic identification and classification of malware
    * Scan the original code of malware with yara.
* Dumps original code of malware
    * You can easily get the original code. 
* User-friendly Web-UI
    * Users can submit malware and check scan results using the Web-UI.

## Requirements
* python 3.5 or later
* yara-python 3.7.0
* qemu-kvm
* nginx

## Installation

### Preparing the Host
1. git clone *repository_url*
2. Run `setup/setup.sh`
3. Install yara-python
  ```
$ git clone --recursive https://github.com/VirusTotal/yara-python
$ cd yara-python
$ python3 setup.py build
$ sudo python3 setup.py install
```
4. Edit tknk.conf
    * vm_name
    * vm_url
5. Download Tools and copy to `tools/`
    * [hollows_hunter](https://github.com/hasherezade/hollows_hunter)
6. Set yara rules  
  Save yara rules in "rules" folder. You need to add the rule to index.yar.

### Preparing the Guest
1. Install Windows on `KVM`
2. Turn off `Windows Defender` and `Windows SmartScreen`
3. Install Python 3.6
4. Set to the IP address described in vm_url.
5. Copy and run `xmlrpc_server.py`
6. Make snapshot

### Setting Web-UI
```
cd frontend/
npm install
npm run generate
mkdir /usr/share/nginx/tknk/
sudo cp -rf dist/* /usr/share/nginx/tknk/
cd ../
sudo cp -f tknk-scanner.nginx.conf /etc/nginx/sites-available/default
sudo systemctl restart nginx
```
### Run
```
cd tknk_scanner/
./tknk.py
```

```
cd tknk_scanner/
rq worker
```

## Usage
![tknk01](https://user-images.githubusercontent.com/18203311/49504641-72015f00-f8bd-11e8-967c-ff5a746d25cd.PNG)
* File upload  
Upload the file to be scanned.

* time  
Sets the time to start runing dump tools.
The default is 120 seconds.

* mode
    * hollows_hunter  
        Using [hollows_hunter](https://github.com/hasherezade/hollows_hunter).
    * prodump  
        Using procdump dump.
    * diff(procdump)  
        Dump the newly created process while running with procdump.

![tknk03](https://user-images.githubusercontent.com/18203311/49511433-7d10bb00-f8ce-11e8-88dd-d81fe5f24e93.png)
![tknk04](https://user-images.githubusercontent.com/18203311/49511682-28217480-f8cf-11e8-8481-d6cd93ca3070.png)
## License
tknk_scanner is open-sourced software licensed under the MIT License

## Thanks
@hasherezade - [hollows_hunter](https://github.com/hasherezade/hollows_hunter)  
yara-python -  https://github.com/VirusTotal/yara-python  
