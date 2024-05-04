import warnings
import contextlib

import requests
from urllib3.exceptions import InsecureRequestWarning
import os
from security import safe_requests

old_merge_environment_settings = requests.Session.merge_environment_settings

@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        # Verification happens only once per connection so we need to close
        # all the opened adapters once we're done. Otherwise, the effects of
        # verify=False persist beyond the end of this context manager.
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except:
                pass

def download_data(antigen, out_path, antibody='Murine'):
    """    Download data for a specific antigen and save it to the specified output path.

    It constructs a URL based on the antigen and antibody type, creates a directory if it doesn't exist,
    and downloads the data as a zip file from the constructed URL.

    Args:
        antigen (str): The name of the antigen for which data is to be downloaded.
        out_path (str): The path where the downloaded data will be saved.
        antibody (str?): The type of antibody. Defaults to 'Murine'.


    Raises:
        HTTPError: If the HTTP request returns an unsuccessful status code.
        Timeout: If the request times out.
    """

    url = f"https://ns9999k.webs.sigma2.no/10.11582_2021.00063/projects/NS9603K/pprobert/AbsolutOnline/RawBindings{antibody}/{antigen}"
    if not os.path.exists(f"{out_path}/RawBindings{antibody}"):
        os.makedirs(f"{out_path}/RawBindings{antibody}")
    file_ = f"{out_path}/RawBindings{antibody}/{antigen}.zip"
    if not os.path.exists(file_):
        file_url = f"{url}.zip"
        with no_ssl_verification():
            with safe_requests.get(file_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(f"{out_path}/RawBindings{antibody}/{antigen}.zip", 'wb') as f:
                    for chunk in r.iter_content():
                        f.write(chunk)

antibody = ['Murine', 'Human']
#antigens = ['1ADQ_A', '5EZO_A', '4OII_A', '4OKV_E', '1NCA_N', '4ZFO_F', '5CZV_A', '5JW4_A']
antigens = [antigen.strip().split()[1] for antigen in open(f"/nfs/aiml/asif/CDRdata/antigens.txt", 'r') if antigen!='\n']

for abdy in antibody:
    for antigen in antigens:
        print(f"Downloading Data Antigen {antigen} Antibody {abdy}")
        try:
            download_data(antigen, "/nfs/aiml/asif/CDRdata", abdy)
        except:
            pass
