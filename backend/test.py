import requests
import pprint

# reqs =[
#     requests.get(
#         "http://127.0.0.1:8000/students/"
#         ),
#     requests.get(
#         "http://127.0.0.1:8000/student/",
#         params={"student_id": 1}
#         )
# ]

# for req in reqs:
#     json = req.json()
#     url = req.url
#     print(url)
#     print(json)




req = requests.get(
    "http://127.0.0.1:8000/students/"
    )
for i in req.json()['students']:
    req = requests.get(
        "http://127.0.0.1:8000/student/",
        params={"student_id": i}
        )
    print(req.json())



