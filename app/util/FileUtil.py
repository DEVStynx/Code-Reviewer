from werkzeug.datastructures import ImmutableMultiDict, FileStorage


def unpackFilesToDict(files: ImmutableMultiDict[str, FileStorage]) -> dict[str, list[FileStorage]]:
    return files.to_dict(flat=False)