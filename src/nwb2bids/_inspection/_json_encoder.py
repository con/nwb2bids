# class CustomJSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, enum.Enum):
#             return obj.name
#         elif isinstance(obj, pydantic.HttpUrl):
#             return str(obj)
#         elif isinstance(obj, pathlib.Path):
#             return str(obj)
#         return super().default(obj)
