# Steam Deck Analyzer — Ingest Module Plugins for Autopsy

This repository contains the sources of **Steam Deck Analyzer**, a collection of Ingest Module plugins for [Autopsy](https://www.autopsy.com/) to extract forensic artifacts from [Steam Deck](https://store.steampowered.com/steamdeck/) device images. Steam Deck Analyzer is a research artifact of our [_Well Played, Suspect!_](#paper) paper which was presented at DFRWS EU 2024.

Initially developed for and tested on the latest versions of Autopsy on Windows 10 and 11 at the time of writing, namely [4.20.0](https://github.com/sleuthkit/autopsy/releases/download/autopsy-4.20.0/autopsy-4.20.0-64bit.msi) (Aug'23) and [4.21.0](https://github.com/sleuthkit/autopsy/releases/download/autopsy-4.21.0/autopsy-4.21.0-64bit.msi) (Sep'23). Written in Python [2.7.18](https://www.python.org/downloads/release/python-2718/) by [necessity](https://sleuthkit.org/autopsy/docs/api-docs/4.21.0/mod_dev_py_page.html).

## Contents

- [Installation of Plugins](#installation-of-plugins)
- [Use of Plugins in Autopsy](#use-of-plugins-in-autopsy)
- [Modules](#modules)
- [Development](#development)
- [License](#license)
- [Paper](#paper)

## Installation of Plugins

Assuming that you have [Autopsy](https://www.autopsy.com/) already installed on your system:

1. Copy this repository using `git clone`, or download the repository as ZIP archive.

2. Copy the entire plugin directory `SteamDeckAnalyzer` to `%APPDATA%\autopsy\python_modules`.

3. The destination directory `python_modules` should then look like this:
   ```
   C:\Users\<USERNAME>\AppData\Roaming\autopsy\
   └────python_modules\
        └───SteamDeckAnalyzer\
            ├───README.md
            ├───sda_boot_partitions.py
            ├───sda_device.py
            ├───sda_factory_reset.py
            └───...
   ```

## Use of Plugins in Autopsy

After adding the Steam Deck image as a data source to your case:

- In the taskbar, navigate to Tools > Run Ingest Modules > _Select Image_, and select all or individual plugins of Steam Deck Analyzer which are named `Steam Deck - *`.
- After processing (see progress bar in the bottom right corner), the results are shown within _Data Artifacts_ in the tree navigation (left) and categorized by plugin names (i.e., `Steam Deck - *`).
  - Note that some modules may not be shown in the tree navigation if there were no respective findings.

If in doubt whether the plugins worked correctly, navigate to _Help_ > _Open Log Folder_ in the taskbar, open the log file `autopsy.log.0`, and look for plugin-related error messages.

## Modules

As a plugin collection for Autopsy, Steam Deck Analyzer consists of individual [File and Data Source ingest modules](https://sleuthkit.org/autopsy/docs/api-docs/4.21.0/mod_ingest_page.html) aiming to extract different types of local artifacts persisted on Steam Deck devices:

| Module                                                           | Ingest Module | Artifacts                                                                                                                                                                                                 |
| ---------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Boot Partitions](./SteamDeckAnalyzer/sda_boot_partitions.py)    | File          | Boot count, status, etc.                                                                                                                                                                                  |
| [Device](./SteamDeckAnalyzer/sda_device.py)                      | Data Source   | Steam OS build ID and version, Steam Client version, timezone, local IP address, etc.                                                                                                                     |
| [Factory Reset](./SteamDeckAnalyzer/sda_factory_reset.py)        | Data Source   | Existence of a specific directory that indicates a factory reset occurred                                                                                                                                 |
| [Friends](./SteamDeckAnalyzer/sda_friends.py)                    | File          | Friend IDs, names, name histories, and avatars                                                                                                                                                            |
| [Games and Apps](./SteamDeckAnalyzer/sda_gameapps.py)            | Data Source   | List of apps; incl. app ID and name, auto login user, timestamps, etc. (fetches ID-to-name dictionary for apps remotely from Steam, or uses a [local copy](./SteamDeckAnalyzer/assets/apps_default.json)) |
| [Log Entries (Slow)](./SteamDeckAnalyzer/sda_log_entries.py)     | Data Source   | Entries of Steam log files (**slow, may take hours**)                                                                                                                                                     |
| [Log Files](./SteamDeckAnalyzer/sda_log_files.py)                | File          | Steam log files                                                                                                                                                                                           |
| [Power History](./SteamDeckAnalyzer/sda_power_history.py)        | Data Source   | UPower history entries                                                                                                                                                                                    |
| [Screenshots](./SteamDeckAnalyzer/sda_screenshots.py)            | File          | Screenshots taken in games/apps; incl. timestamp, friend ID of player, and game ID                                                                                                                        |
| [Secrets](./SteamDeckAnalyzer/sda_secrets.py)                    | File          | Authentication token, credentials, keys, etc. found on disk (for Wi-Fi, there is a separate module)                                                                                                       |
| [Users](./SteamDeckAnalyzer/sda_users.py)                        | Data Source   | User information; incl. steam ID, account name, persona name, remember password, etc.                                                                                                                     |
| [Web: Cookies](./SteamDeckAnalyzer/sda_web_cookies.py)           | File          | Cookie information, incl. decrypted values, parsed WebKit format timestamps (UTC), etc.                                                                                                                   |
| [Web: QuotaManager](./SteamDeckAnalyzer/sda_web_quotamanager.py) | File          | Use counts of origins, parsed WebKit format timestamps, etc.                                                                                                                                              |
| [Wi-Fi](./SteamDeckAnalyzer/sda_wifi.py)                         | File          | Wi-Fi credentials for WPA-PSK (Personal; pre-shared key) and WPA-802.1X (Enterprise)                                                                                                                      |

## Development

If you want to work on the source code of Steam Deck Analyzer, and if you are not yet familiar with plugin development for Autopsy, you may find the following remarks helpful:

- We introduced a custom parent class `IngestModulePlus` to encapsulate and extend common functions and behavior of Autopsy's _FileIngestModule_ and _DataSourceIngestModule_ classes. Correspondingly, all plugins of Steam Deck Analyzer inherit from one of two custom classes, namely `FileIngestModulePlus` and `DataSourceIngestModulePlus`.

- To ease development, create a symlink to the directory `SteamDeckAnalyzer` of this repository within Autopsy's `python_modules` directory by running the following command in the PowerShell as administrator _after_ editing the mentioned paths:

  ```
  cmd /c mklink /D "C:\Users\USERNAME\AppData\Roaming\autopsy\python_modules\SteamDeckAnalyzer" "C:\Users\USERNAME\path\to\SteamDeckAnalyzer"
  ```

- After editing the source code of Autopsy plugins, be on the safe side and restart Autopsy before re-running plugins for changes to take effect. Additionally, you may want to execute the `cleanup.ps1` PowerShell script to delete temporary Python files recursively:

  ```
  cd SteamDeckAnalyzer\dev\
  .\cleanup.ps1
  ```

  - If you cannot execute the script because you are told that _"running scripts is disabled on this system"_, run the following command in the PowerShell as administrator:
    ```
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
    ```

- When running plugins during development, always open the log file `autopsy.log.0` via _Help_ > _Open Log Folder_ (taskbar) to catch errors and info messages.

- As it is not possible by default to delete artifact and attribute definitions of plugins via Autopsy's GUI, consider the following ways to counteract this limitation:

  - During development, change the following constant in the code after each deployment to ensure that changes to artifacts and attributes are persisted by re-introducing them under varying names:
    - `utils/module.py` $\rightarrow$ variable `PREFIX_MODULE` $\rightarrow$ add incrementing prefix to existing value (e.g., "`DEV - 001 - Steam Deck - `")
  - Read [this article](https://markmckinnon-80619.medium.com/a-plugin-for-developer-remove-artifacts-352f1eff8fe7), and install the [`Remove_Artifacts.py`](https://github.com/markmckinnon/Autopsy-Plugins/tree/master/Remove_Artifacts) plugin (only intended for development purposes). Select to delete all custom artifacts and attributes. After running it, you need to restart Autopsy for the modules' nodes to disappear from the tree navigation.

- Refer to the version of the [Developer's Guide and API Reference](https://www.sleuthkit.org/autopsy/docs/api-docs/) which corresponds to your Autopsy version:
  - Open the online version of the user documentation via <kbd>F1</kbd> in Autopsy (Windows; _Help_ > _Online Autopsy Documentation_).
  - Refer to the official tutorials on [File Ingest Modules](https://sleuthkit.org/autopsy/docs/api-docs/4.21.0/mod_python_file_ingest_tutorial_page.html) and [Data Source Ingest Modules](https://sleuthkit.org/autopsy/docs/api-docs/4.21.0/mod_python_ds_ingest_tutorial_page.html) to develop Autopsy plugins using Python 2.7.
  - You may want to use the [IntelliJ IDEA setup](https://sleuthkit.org/autopsy/docs/api-docs/4.21.0/mod_dev_py_page.html) recommended in the Autopsy documentation.
  - Since [_Autopsy uses Jython to enable Python scripting_](https://sleuthkit.org/autopsy/docs/api-docs/4.21.0/mod_dev_py_page.html), you may want to download [Jython](https://www.jython.org/download) to test Java imports and functions within a Python script outside of the Autopsy context, e.g.:
    ```
    java -jar .\jython-standalone-2.7.3.jar C:\Users\USERNAME\Desktop\test.py
    ```

## License

This project is licensed under an [MIT license](./LICENSE). It is neither endorsed or authorized by nor affiliated or associated with Valve Corporation, Sleuth Kit Labs LLC, or any of their subsidiaries. All rights related to names, services, or products which have been used or mentioned in this project belong to their respective owner(s).

## Paper

Our paper was presented at the 11th Annual _Digital Forensics Research Conference Europe_ ([DFRWS EU 2024](https://dfrws.org/presentation/well-played-suspect-forensic-examination-of-the-handheld-gaming-console-steam-deck/)):

> Maximilian Eichhorn, Janine Schneider, and Gaston Pugliese. [_Well Played, Suspect!_ — Forensic Examination of the Handheld Gaming Console “Steam Deck”](https://www.sciencedirect.com/science/article/pii/S266628172300207X). Forensic Science International: Digital Investigation 48 (2024): 301688.

<details>
<summary>BibTeX</summary>

```bibtex
@article{eichhorn2024steamdeck,
    title={{\emph{Well Played, Suspect!} --- Forensic Examination of the Handheld Gaming Console “Steam Deck”}},
    author={Maximilian Eichhorn and Janine Schneider and Gaston Pugliese},
    journal={{Forensic Science International: Digital Investigation}},
    volume={48},
    pages={301688},
    year={2024},
    month={3},
    publisher={Elsevier},
    doi={10.1016/j.fsidi.2023.301688}
}
```

</details>
