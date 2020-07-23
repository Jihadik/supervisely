import supervisely_lib as sly

project_id = 75563
dataset_id = 317675

image_path = '/workdir/src/examples/d.jpg'
image_name = sly.fs.get_file_name_with_ext(image_path)

api = sly.Api.from_env()

if api.image.get_info_by_name(dataset_id, image_name) is not None:
    print('image (name={!r}) already exists in dataset (id={!r})'.format(image_name, dataset_id))
    new_name = '{}_{}{}'.format(sly.fs.get_file_name(image_name), sly.rand_str(5), sly.fs.get_file_ext(image_name))
    print('new name: ', new_name)
    image_name = new_name

meta = {"xxx": 777, "yyy": 999}
uploaded_image_info = api.image.upload_path(dataset_id, image_name, image_path, meta)
print("!!! uploaded_image_info", uploaded_image_info)
print("[FOR DEBUG] Image meta on server: ", uploaded_image_info.meta)

image_info = api.image.get_info_by_name(dataset_id, image_name)
print("Image meta on server: ", image_info.meta)