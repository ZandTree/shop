import random
import string
from django.utils.text import slugify
import os


def make_random_string(chars=(string.ascii_lowercase + string.hexdigits),size=6):
    """
    return string made of random (ascii-chars,digits)of length = size
    """
    output = [random.choice(chars) for _ in range(size)]
    return "".join(output)

def make_unique_id(instance):
    """
    make unique id for objects based on random string
    """
    new_order_id = make_random_string().upper()
    Instance_Class = instance.__class__
    qs =  Instance_Class.objects.filter(order_unid=new_order_id).exists()
    if qs:
        return make_unique_id(instance)
    return new_order_id


def make_unique_slug(instance,new_slug=None):
    """
    make unique slug for objects with attr= name and = slug.
    make slug based on name attr,check it existance. if yes,add a random_string
    """
    print('starting making unique slug')
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)
    Instance_Class = instance.__class__
    qs =  Instance_Class.objects.filter(slug=slug).exists()
    if qs:
        new_slug = "{slug}-{random_string}".format(slug=slug,
                                                    random_string=make_random_string(size=4))
        # here call same function again to check whether its's unique
        # otherwise make another one
        #короче пойду на второй заход в попытке создать уникальную комби
        return make_unique_slug(instance,new_slug)
    return slug

def clean_empty_img_prods():
    """
    can be run for cleaning image directory from empty sub-dirs
    (in case of deleting categories with related products)
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    media_path = os.path.join(BASE_DIR,'media','image')
    inhoud = os.listdir(media_path)
    for item in inhoud:
        path = os.path.join(media_path,item)
        if os.path.isdir(path):
            if os.listdir(path):
                pass
                # print("path is: ",os.listdir(path))
                # print('Folder is not empty')
            else:
                os.rmdir(path)
