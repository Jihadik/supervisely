import supervisely_lib as sly

print("start")

api = sly.Api.from_env()

#lj_info = api.labeling_job.create(name="lj_with_reviewer", dataset_id=808, user_ids=[1], reviewer_id=6)
#print(lj_info)

info = api.labeling_job.get_info_by_id(id=32)
print(info.reviewer_id)
print(info.reviewer_login)


print("end")