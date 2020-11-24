import json
import supervisely_lib as sly

project_id = 124

api = sly.Api.from_env()
stats_json = api.project.get_stats(project_id)
print(json.dumps(stats_json, indent=4))

# Output:
# {
#     "datasets": {
#         "items": [
#             {
#                 "id": 137,
#                 "imagesCount": 6,
#                 "size": "861069",
#                 "name": "ds1"
#             }
#         ],
#         "total": {
#             "imagesCount": 6,
#             "size": "861069"
#         }
#     },
#     "images": {
#         "datasets": [
#             {
#                 "id": 137,
#                 "name": "ds1",
#                 "imagesMarked": 6,
#                 "imagesNotMarked": 0,
#                 "imagesInDataset": 6
#             }
#         ],
#         "objectClasses": [
#             {
#                 "objectClass": {
#                     "id": 241,
#                     "name": "lemon",
#                     "color": "#51C6AA"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "name": "ds1",
#                         "count": 6
#                     }
#                 ],
#                 "total": 6
#             },
#             {
#                 "objectClass": {
#                     "id": 242,
#                     "name": "kiwi",
#                     "color": "#FF0000"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "name": "ds1",
#                         "count": 6
#                     }
#                 ],
#                 "total": 6
#             },
#             {
#                 "objectClass": {
#                     "id": 1685,
#                     "name": "eee",
#                     "color": "#E44ECB"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "name": "ds1",
#                         "count": 0
#                     }
#                 ],
#                 "total": 0
#             },
#             {
#                 "objectClass": {
#                     "id": 4004,
#                     "name": "ddd",
#                     "color": "#936AC8"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "name": "ds1",
#                         "count": 3
#                     }
#                 ],
#                 "total": 3
#             }
#         ],
#         "total": {
#             "imagesMarked": 6,
#             "imagesNotMarked": 0,
#             "imagesInDataset": 6
#         }
#     },
#     "imageTags": {
#         "datasets": [
#             {
#                 "id": 137,
#                 "name": "ds1",
#                 "imagesTagged": 4,
#                 "imagesNotTagged": 2,
#                 "imagesInDataset": 6
#             }
#         ],
#         "items": [
#             {
#                 "tagMeta": {
#                     "id": 1133,
#                     "name": "multi",
#                     "color": "#E32B34"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "name": "ds1",
#                         "count": 1
#                     }
#                 ],
#                 "total": 1
#             },
#             {
#                 "tagMeta": {
#                     "id": 234,
#                     "name": "very-very-very-long-name-that-can-break-changes",
#                     "color": "#3B975E"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "name": "ds1",
#                         "count": 4
#                     }
#                 ],
#                 "total": 4
#             }
#         ],
#         "total": {
#             "imagesTagged": 4,
#             "imagesNotTagged": 2,
#             "imagesInDataset": 6
#         }
#     },
#     "objectTags": {
#         "datasets": [
#             {
#                 "id": 137,
#                 "name": "ds1",
#                 "objectsTagged": 2,
#                 "objectsNotTagged": 33,
#                 "objectsInDataset": 35
#             }
#         ],
#         "items": [
#             {
#                 "tagMeta": {
#                     "id": 1133,
#                     "name": "multi",
#                     "color": "#E32B34"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "name": "ds1",
#                         "count": 1
#                     }
#                 ],
#                 "total": 1
#             },
#             {
#                 "tagMeta": {
#                     "id": 234,
#                     "name": "very-very-very-long-name-that-can-break-changes",
#                     "color": "#3B975E"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "name": "ds1",
#                         "count": 2
#                     }
#                 ],
#                 "total": 2
#             }
#         ],
#         "total": {
#             "objectsTagged": 2,
#             "objectsNotTagged": 33,
#             "objectsInDataset": 35
#         }
#     },
#     "objects": {
#         "datasets": [
#             {
#                 "id": 137,
#                 "name": "ds1",
#                 "objectsInDataset": 35
#             }
#         ],
#         "items": [
#             {
#                 "objectClass": {
#                     "id": 241,
#                     "name": "lemon",
#                     "color": "#51C6AA"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "count": 6
#                     }
#                 ],
#                 "total": 6
#             },
#             {
#                 "objectClass": {
#                     "id": 242,
#                     "name": "kiwi",
#                     "color": "#FF0000"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "count": 20
#                     }
#                 ],
#                 "total": 20
#             },
#             {
#                 "objectClass": {
#                     "id": 1685,
#                     "name": "eee",
#                     "color": "#E44ECB"
#                 },
#                 "datasets": [],
#                 "total": 0
#             },
#             {
#                 "objectClass": {
#                     "id": 4004,
#                     "name": "ddd",
#                     "color": "#936AC8"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "count": 9
#                     }
#                 ],
#                 "total": 9
#             }
#         ],
#         "total": {
#             "objectsInDataset": 35
#         }
#     },
#     "objectsArea": {
#         "datasets": [
#             {
#                 "id": 137,
#                 "name": "ds1",
#                 "objectsAreaInDataset": "249038",
#                 "imagesAreaInDataset": "20486400",
#                 "percentageInDataset": 4.862503905029678
#             }
#         ],
#         "items": [
#             {
#                 "objectClass": {
#                     "id": 241,
#                     "name": "lemon",
#                     "color": "#51C6AA"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "percentage": 0,
#                         "objectsArea": "0",
#                         "imagesArea": "5121600"
#                     }
#                 ],
#                 "total": 0
#             },
#             {
#                 "objectClass": {
#                     "id": 242,
#                     "name": "kiwi",
#                     "color": "#FF0000"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "percentage": 0.7088800374882849,
#                         "objectsArea": "36306",
#                         "imagesArea": "5121600"
#                     }
#                 ],
#                 "total": 0.7088800374882849
#             },
#             {
#                 "objectClass": {
#                     "id": 1685,
#                     "name": "eee",
#                     "color": "#E44ECB"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "percentage": 0,
#                         "objectsArea": "0",
#                         "imagesArea": "5121600"
#                     }
#                 ],
#                 "total": 0
#             },
#             {
#                 "objectClass": {
#                     "id": 4004,
#                     "name": "ddd",
#                     "color": "#936AC8"
#                 },
#                 "datasets": [
#                     {
#                         "id": 137,
#                         "percentage": 4.153623867541393,
#                         "objectsArea": "212732",
#                         "imagesArea": "5121600"
#                     }
#                 ],
#                 "total": 4.153623867541394
#             }
#         ],
#         "total": {
#             "objectsAreaInDataset": "249038",
#             "imagesAreaInDataset": "20486400",
#             "percentageInDataset": 4.862503905029678
#         }
#     }
# }