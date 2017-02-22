# Zabbix LLD and monitoring for Adaptec RAID controllers

It is:

* JSON-formatted data for Zabbix LLD
* **arcconf** output parser for Zabbix
* Zabbix template

Demo screenshot:

![screenshot](https://cloud.githubusercontent.com/assets/2463895/21681285/486738be-d357-11e6-999a-6f5139230826.png)

Tested on:
* arcconf Version 2.02 (B22404)
* Ubuntu 16.04.1 LTS
* Adaptec 3405 controller
* Zabbix Server 2.4

## Limitation

* 1 controller only (ID 1)
* up to 10 logical devices only (ID 0-9)
* up to 10 physical drives only (ID 0-9)
* parameters values reads and being stored as raw string, not numbers (e.q. "33 C/ 91 F (Normal)")

## Installation

### arcconf

Script use a **arcconf** utility by Adaptec from https://hwraid.le-vert.net/. 

    wget -O - https://hwraid.le-vert.net/debian/hwraid.le-vert.net.gpg.key | sudo apt-key add -
    echo "deb http://hwraid.le-vert.net/debian jessie main" | sudo tee /etc/apt/sources.list.d/hwraid.list
    apt update
    apt install arcconf

Assuming arrconf is installed to **/usr/sbin/arcconf**.

``whereis arcconf``:

    arcconf: /usr/sbin/arcconf

If not — consider to change path to the earcconf executable in the script.

### Script download

Assuming current user is in the *sudo* group.

    sudo mkdir /opt/zabbix_scripts
    sudo chown zabbix:sudo /opt/zabbix_scripts
    sudo chmod 775 /opt/zabbix_scripts
    cd /opt/zabbix_scripts
    
    git clone git@github.com:YSmetana/raid_arcconf_zabbix_lld.git

    sudo chown -R zabbix:sudo raid_arcconf_zabbix_lld
    sudo chmod 775 raid_arcconf_zabbix_lld
    cd raid_arcconf_zabbix_lld
    sudo chmod 774 *.py

### Sudo

arcconf need *sudo*.

    sudo chown root:root raid_arcconf_zabbix_lld_sudo
    sudo chmod 440 raid_arcconf_zabbix_lld_sudo
    sudo ln -s /opt/zabbix_scripts/raid_arcconf_zabbix_lld/raid_arcconf_zabbix_lld_sudo /etc/sudoers.d/
    sudo sudo -k

### Zabbix "UserParameter"

    sudo ln -s /opt/zabbix_scripts/raid_arcconf_zabbix_lld/raid_arcconf_zabbix_lld.conf /etc/zabbix/zabbix_agentd.conf.d/
    sudo service zabbix-agent restart

### Manual test

``sudo -u zabbix bash``

``zabbix_agentd -t "raid.arcconf[ad,-1,lld]"``

    raid.arcconf[ad,all,lld]                      [t|{"data": [{"{#OBJ_ALIAS}": "Adaptec 3405", "{#OBJ_TYPE}": "ad", "{#OBJ_ID}": 1}]}]


``zabbix_agentd -t "raid.arcconf[ld,1,Status of Logical Device]"``

    raid.arcconf[ld,1,Status of Logical Device]   [t|Optimal]

### Zabbix GUI

Import template **raid_arcconf_zabbix_lld.xml** into Zabbix: "Configuration -> Templates -> Import.". You shuld see template named **Service_Adaptec_Raid**.

Add host to the Template, or link template to the Host.

--------------------------------

## Appendix

### Using script for debugging purpose

Short help: ``raid_arcconf_zabbix_lld.py --help``.

Logical (virtual) drives LLD:

``raid_arcconf_zabbix_lld.py --verbose ld -1 lld``:

    {"data": [{"OBJ_TYPE": "ld", "OBJ_ALIAS": "zeta-r1-3t", "OBJ_ID": 0}, {"OBJ_TYPE": "ld", "OBJ_ALIAS": "zeta-v-s03", "OBJ_ID": 1}]}

To get a desired value you can use any "key" available in arcconf output (see "arcconf output example" below).

``raid_arcconf_zabbix_lld.py ld 1 "Status of Logical Device"``

    Optimal

### arcconf example output

#### Adapter (controller) information

``arcconf GETCONFIG 1 AD``:

    Controllers found: 1
    ----------------------------------------------------------------------
    Controller information
    ----------------------------------------------------------------------
       Controller Status                        : Optimal
       Channel description                      : SAS/SATA
       Controller Model                         : Adaptec 3405
       Controller Serial Number                 : 8C16103DF1D
       Controller World Wide Name               : 50000D11009C9400
       Controller Alarm                         : Enabled
       Physical Slot                            : 3
       Temperature                              : 35 C/ 95 F (Normal)
       Installed memory                         : 128 MB
       Global task priority                     : High
       Host bus type                            : unknown
       Host bus speed                           : 0 MHz
       Host bus link width                      : 0 bit(s)/link(s)
       PCI Device ID                            : 645
       Stayawake period                         : Disabled
       Spinup limit internal drives             : 0
       Spinup limit external drives             : 0
       Defunct disk drive count                 : 1
       Logical devices/Failed/Degraded          : 2/0/1
       NCQ status                               : Enabled
       --------------------------------------------------------
       RAID Properties
       --------------------------------------------------------
       Copyback                                 : Disabled
       Automatic Failover                       : Enabled
       Background consistency check             : Disabled
       Background consistency check period      : 30
       --------------------------------------------------------
       Controller Version Information
       --------------------------------------------------------
       BIOS                                     : 5.2-0 (17342)
       Firmware                                 : 5.2-0 (17342)
       Driver                                   : 1.2-1 (41010)
       Boot Flash                               : 5.2-0 (17342)
       --------------------------------------------------------
       Controller Battery Information
       --------------------------------------------------------
       Status                                   : Optimal
       Over temperature                         : No
       Capacity remaining                       : 100 percent
       Time remaining (at current draw)         : 3 days, 1 hours, 52 minutes

#### Logical (virtual) disk information

``arcconf GETCONFIG 1 LD 0``

    Controllers found: 1
    ----------------------------------------------------------------------
    Logical device information
    ----------------------------------------------------------------------
    Logical Device number 0
       Logical Device name                      : zeta-r1-3t
       Block Size of member drives              : 512 Bytes
       RAID level                               : 1
       Unique Identifier                        : B715F832
       Status of Logical Device                 : Degraded
       Additional details                       : Initialized with Build/Clear
       Size                                     : 2856950 MB
       Parity space                             : 2856960 MB
       Interface Type                           : SAS/SATA
       Device Type                              : HDD
       Read-cache setting                       : Enabled
       Read-cache status                        : On
       Write-cache setting                      : On when protected by battery/ZMM
       Write-cache status                       : On
       Partitioned                              : Yes
       Protected by Hot-Spare                   : No
       Bootable                                 : Yes
       Failed stripes                           : No
       Power settings                           : Disabled
       --------------------------------------------------------
       Logical Device segment information
       --------------------------------------------------------
       Segment 0                                : Present (2861588MB, SATA, HDD, Channel:0, Device:10)      WD-WCC4N0RUUPKF
       Segment 1                                : Missing

#### Physical disk information

``arcconf GETCONFIG 1 PD``

    Controllers found: 1
    ----------------------------------------------------------------------
    Physical Device information
    ----------------------------------------------------------------------
          Device #0
             Device is a Hard drive
             State                              : Online
             Block Size                         : 512 Bytes
             Supported                          : Yes
             Transfer Speed                     : SATA 3.0 Gb/s
             Reported Channel,Device(T:L)       : 0,10(10:0)
             Vendor                             : WDC
             Model                              : WD30EFRX-68EUZN0
             Firmware                           : 82.00A82
             Serial number                      : WD-WCC4N0RUUPKF
             Reserved Size                      : 4739480 KB
             Used Size                          : 2856960 MB
             Unused Size                        : 64 KB
             Total Size                         : 2861588 MB
             Write Cache                        : Enabled (write-back)
             FRU                                : None
             S.M.A.R.T.                         : No
             S.M.A.R.T. warnings                : 0
             SSD                                : No
             Temperature                        : Not Supported
             NCQ status                         : Enabled
          ----------------------------------------------------------------
          Device Phy Information                
          ----------------------------------------------------------------
             Phy #0
                PHY Identifier                  : 0
                SAS Address                     : 5001517507FE6003
                Attached PHY Identifier         : 2
                Attached SAS Address            : 5001517507FE6000

          Device #1
             Device is a Hard drive
             State                              : Online
             Block Size                         : 512 Bytes
             Supported                          : Yes
             Transfer Speed                     : SATA 3.0 Gb/s
             Reported Channel,Device(T:L)       : 0,11(11:0)
             Vendor                             : HUA72201
             Model                              : 0CLA330
             Firmware                           : JP4OA3NB
             Serial number                      : JPW9P0N0139JZD
             Reserved Size                      : 538264 KB
             Used Size                          : 953344 MB
             Unused Size                        : 64 KB
             Total Size                         : 953869 MB
             Write Cache                        : Enabled (write-back)
             FRU                                : None
             S.M.A.R.T.                         : No
             S.M.A.R.T. warnings                : 0
             SSD                                : No
             Temperature                        : Not Supported
             NCQ status                         : Enabled
          ----------------------------------------------------------------
          Device Phy Information                
          ----------------------------------------------------------------
             Phy #0
                PHY Identifier                  : 0
                SAS Address                     : 5001517507FE6004
                Attached PHY Identifier         : 3
                Attached SAS Address            : 5001517507FE6000

          Device #2
             Device is a Hard drive
             State                              : Failed
             Block Size                         : Unknown
             Supported                          : Yes
             Reported Channel,Device(T:L)       : 0,13(13:0)
             Vendor                             : 
             Model                              : 
             Firmware                           : 
             World-wide name                    : 0000000000000000
             Total Size                         : 0 MB
             Write Cache                        : Unknown
             FRU                                : None
             S.M.A.R.T.                         : No
             S.M.A.R.T. warnings                : 0
             SSD                                : No
             Temperature                        : Not Supported
          ----------------------------------------------------------------
          Device Phy Information                
          ----------------------------------------------------------------
             No Phy information available       

          Device #3
             Device is an Enclosure Services Device
             Reported Channel,Device(T:L)       : 2,0(0:0)
             Type                               : SAF-TE
             Vendor                             : ESG-SHV.
             Model                              : SCA HSBP M13....
             Firmware                           : 2.05
