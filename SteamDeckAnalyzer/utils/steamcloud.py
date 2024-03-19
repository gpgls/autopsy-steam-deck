# -*- coding: utf-8 -*-

import json
import urllib2

class SteamCloudUtils:

    SANITY_CHECK_MIN_APP_COUNT = 100000

    @staticmethod
    def download_app_dictionary(filepath, timeout=90):
        try:
            # fetch list of apps from API
            url = 'https://api.steampowered.com/ISteamApps/GetAppList/v2?format=json'
            headers = {"Content-Type": "application/json"}
            response = urllib2.urlopen(urllib2.Request(url=url, headers=headers), timeout=timeout)
            assert response.code == 200, "{}".format(response.code)

            # parse JSON response, and conduct sanity checks
            data = json.loads(response.read().decode('utf-8'))
            assert isinstance(data, dict), "{}".format(type(data))
            assert "applist" in data, "{}".format(sorted(data.keys()))
            data = data["applist"]
            assert isinstance(data, dict), "{}".format(type(data))
            assert "apps" in data, "{}".format(sorted(data.keys()))
            data = data["apps"]
            assert isinstance(data, list), "{}".format(type(data))
            assert len(data) > SteamCloudUtils.SANITY_CHECK_MIN_APP_COUNT, \
                "{} apps".format(len(data))

            # make dictionary: { <APP_ID> = <APP_NAME>, ... }
            apps = {}
            for item in data:
                assert isinstance(item, dict), "{} > {}".format(type(item), item)
                assert "name" in item, "{}".format(sorted(item.keys()))
                assert "appid" in item, "{}".format(sorted(item.keys()))
                apps[item["appid"]] = item["name"]

            # write dictionary to disk as JSON file
            with open(filepath, 'w+') as f:
                f.write(json.dumps(apps, indent=2, sort_keys=True))

            return True

        except:
            return False
