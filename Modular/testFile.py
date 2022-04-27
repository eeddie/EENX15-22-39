import subprocess
import os

# subprocess.run("Dir",shell=True)
# subprocess.run("Dir",shell=True)
# subprocess.run("Dir",shell=True)
# subprocess.run("Dir",shell=True)
# subprocess.run("Dir",shell=True)
# subprocess.run("Dir",shell=True)
# subprocess.run("Dir",shell=True)
# subprocess.run("Dir",shell=True)
# subprocess.run("Dir",shell=True)
# subprocess.run("Dir",shell=True)
# subprocess.run("Dir",shell=True)

APIKey = r"1d7d48e5290892a61c0e8f2106d40825"
import requests

arr = [1, [1, 1], [[1, 2]]]

def flatten(arr):
    element = []
    listExtend(arr, element)
    return element

def listExtend(arr, element):
    if type(arr) is list:
        for i in arr:
            listExtend(i, element)
    else:
        element.append(arr)


print(flatten(arr))
