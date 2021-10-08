import os
import sys
import shutil
import tempfile
import time

import requests
from pandas import DataFrame

from classifier import TestService

sys.path.append("./")
from deploy import deploy
from describe import describe
from delete import delete


class Setup:
    def __init__(self):
        """
        Setup the deployment on the deployment choosen
        """
        self.deployment_name = "ec2_bento_deploy_test"
        self.dirpath = tempfile.mkdtemp()
        print("temp dir {} created!".format(self.dirpath))
        self.saved_dir = os.path.join(self.dirpath, "saved_dir")

        # make config file
        config = """
        {
          "project_id": "bentoml-316710",
          "region": "us-central1",
          "port": 5001,
          "min_instances": 0,
          "max_instances": 1,
          "memory": "512Mi",
          "cpu": 1,
          "allow_unauthenticated": true,
          "platform": "managed"
        }
        """
        self.config_file = os.path.join(self.dirpath, "config.json")
        with open(self.config_file, "w") as f:
            f.write(config)

        # make bento service
        os.mkdir(self.saved_dir)
        test_service = TestService()
        # test_service.pack()
        test_service.save_to_dir(self.saved_dir)

    @staticmethod
    def check_if_up(url, num_attempts=5, wait_time=20):
        attempt = 0
        while attempt < num_attempts:
            try:
                if requests.get(url).status_code == 400:
                    print("Ok!")
                    return True
                else:
                    print("not Ok", end=" ")
                    time.sleep(wait_time)
            except Exception as e:
                print(e)
                time.sleep(wait_time)
            finally:
                attempt += 1
        return False

    def make_deployment(self):
        deploy(self.saved_dir, self.deployment_name, self.config_file)
        info_json = describe(
            deployment_name=self.deployment_name,
            config_json=self.config_file,
            return_json=True,
        )
        url = info_json["status"]["url"] + "/{}"

        # ping /healthz to check if deployment is up
        print("Checking is service is up...", end="")
        url_healthz = url.format("jsonapi")
        self.check_if_up(url_healthz, num_attempts=8, wait_time=60)

        return url

    def teardown(self):
        delete(self.deployment_name, self.config_file)
        shutil.rmtree(self.dirpath)
        print("Removed {}!".format(self.dirpath))


def test_json(url):
    """
    GIVEN the api is deployed
    WHEN a valid json is given
    THEN accepts the binary_data and returns it
    """
    headers = {"content-type": "application/json"}
    input_json = "[[1, 2, 3, 4]]"
    resp = requests.post(url, data=input_json, headers=headers)
    assert resp.ok
    assert resp.content == bytearray(input_json, "ascii")


def test_df(url):
    """
    GIVEN the api is deployed
    WHEN a dataframe is passed, as json or csv
    THEN accepts the binary_data and returns it
    """
    input_array = [[1, 2, 3, 4]]

    # request as json
    resp = requests.post(url, json=input_array)
    assert resp.ok
    assert DataFrame(resp.json()).to_json() == DataFrame(input_array).to_json()

    # request as csv
    headers = {"content-type": "text/csv"}
    csv = DataFrame(input_array).to_csv(index=False)
    resp = requests.post(url.format("dfapi"), data=csv, headers=headers)
    assert resp.ok
    assert DataFrame(resp.json()).to_json() == DataFrame(input_array).to_json()


def test_files(url):
    """
    GIVEN the api is deployed
    WHEN a file is passed either as raw bytes with any content-type or as mulitpart/form
    THEN it accepts the binary_data and returns it
    """
    binary_data = b"test"

    # request with raw data
    headers = {"content-type": "image/jpeg"}
    resp = requests.post(url, data=binary_data, headers=headers)
    assert resp.ok
    assert resp.content == b'"test"'

    # request mulitpart/form-data
    file = {"audio": ("test", binary_data)}
    resp = requests.post(url.format("fileapi"), files=file)
    assert resp.ok
    assert resp.content == b'"test"'


if __name__ == "__main__":

    setup = Setup()
    failed = False
    try:
        url = setup.make_deployment()
        print(url)
    except Exception as e:
        print("Setup failed")
        raise e
    else:
        # setup successful!
        print("Setup successful")

        # list of tests to perform
        TESTS = [(test_json, "jsonapi"), (test_df, "dfapi"), (test_files, "fileapi")]

        for test_func, endpoint in TESTS:
            try:
                print("Testing endpoint /{}...".format(endpoint), end="")
                test_func(url.format(endpoint))
                print("\033[92m passed! \033[0m")
            except Exception as e:
                print("\033[91m failed! \033[0m")
                print("\nTest at endpoint /{} failded: ".format(endpoint), e)
                failed = True
    finally:
        setup.teardown()

    if failed:
        sys.exit(1)
    else:
        sys.exit(0)
