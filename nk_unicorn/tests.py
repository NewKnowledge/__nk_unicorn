from . import Unicorn, ImagenetModel


# TODO WIP
def test_unicorn():
    unicorn = Unicorn()
    from glob import glob
    image_paths = glob('images/*.jpg')
    print('image paths to cluster:', image_paths)
    image_net = ImagenetModel()
    dat = image_net.get_features_from_paths(image_paths)
    print('shape of array data to cluster:', dat.shape)
    clusters = unicorn.cluster(dat)
    print('clusters:', clusters)
