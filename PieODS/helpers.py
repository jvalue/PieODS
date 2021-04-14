


# def fill(string_to_fill, *fillers):
#     pass

def _url(r, *path_components):
    for c in path_components:
        r += "/{}".format(str(c)) 
    return r


