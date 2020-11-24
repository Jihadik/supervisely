import supervisely_lib as sly

api = sly.Api.from_env()

model_id = 75
info = api.model.get_info_by_id(model_id)
api.model.remove(model_id)

print("finish")