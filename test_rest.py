import requests
import os
from json import JSONDecoder, loads, dumps


address = "http://localhost:5000"
decoder = JSONDecoder()

# test_file_urls = dumps({'image_paths': ['http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg','http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg','http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg','http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg','http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg','http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg']})

# testing on docker:
test_file_urls = dumps({'image_paths': ['/app/nk_unicorn/images/ferry-boat.jpg', '/app/nk_unicorn/images/macbook.jpg', '/app/nk_unicorn/images/fox.jpg', '/app/nk_unicorn/images/yacht.jpg', '/app/nk_unicorn/images/wolf.jpg', '/app/nk_unicorn/images/raccoon.jpg', '/app/nk_unicorn/images/iphone.jpg', '/app/nk_unicorn/images/office.jpg', '/app/nk_unicorn/images/mobile.jpg', '/app/nk_unicorn/images/winter.jpg', '/app/nk_unicorn/images/freerider.jpg', '/app/nk_unicorn/images/sailing-ship.jpg', '/app/nk_unicorn/images/field-of-poppies.jpg', '/app/nk_unicorn/images/bike.jpg', '/app/nk_unicorn/images/poppies.jpg', '/app/nk_unicorn/images/iphone-copy.jpg', '/app/nk_unicorn/images/yacht-copy.jpg', '/app/nk_unicorn/images/imac.jpg', '/app/nk_unicorn/images/wanderer.jpg', '/app/nk_unicorn/images/bear.jpg', '/app/nk_unicorn/images/sea.jpg']})

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
