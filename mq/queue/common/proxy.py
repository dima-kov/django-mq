from apps.core.models import SiteConfiguration
import zipfile


class ProxyStorage(object):

    proxy = None

    def get(self):
        return self.proxy or self.load_proxy()

    def load_proxy(self):
        proxy = SiteConfiguration.get_solo().proxy
        self.proxy = str(proxy) or None
        return self.proxy


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
"""


def generate_proxy_plugin(proxy_host, proxy_port, proxy_user, proxy_pass):
    proxy_plugin_file = 'selenium_proxy_auth_plugin.zip'
    background_js_formatted = background_js % (proxy_host, proxy_port, proxy_user, proxy_pass)

    with zipfile.ZipFile(proxy_plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js_formatted)
    return proxy_plugin_file
