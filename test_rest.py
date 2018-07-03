import requests
import os
from json import JSONDecoder, loads, dumps


address = "http://localhost:5000"
decoder = JSONDecoder()

test_file_urls = dumps({'image_paths': ['http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg','http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg','http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg','http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg','http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg','http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg']})


print("DEBUG::chkpt0")
print(test_file_urls)

try:
    print("DEBUG::chkpt1")
    r = requests.post(
        address + "/test-fileupload",
        json=test_file_urls,
        headers={"content-type": "application/json"})

    print("DEBUG::chkpt2")
    print(r)
    result = decoder.decode(r.text)	

    print("DEBUG::success!!")
    print("The output from UNICORN is:")
    print(result)

except Exception as e:
    print(e)
    print("DEBUG::Failure! Sorry! Please check and try again...")
