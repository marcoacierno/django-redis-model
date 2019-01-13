from django_redis_models import RedisModel, GenericType


class ShopItem(RedisModel):
    id = GenericType()
    listing_id = GenericType()
    title = GenericType()
    description = GenericType()
    price = GenericType()
    currency_code = GenericType()
    quantity = GenericType()
    url = GenericType()

    class Meta:
        primary_key_name = 'id'


class ShopItemImage(RedisModel):
    id = GenericType()
    listing_image_id = GenericType()

    shop_item = GenericType()

    height = GenericType()
    width = GenericType()

    format_75x75 = GenericType()
    format_170x135 = GenericType()
    format_570xN = GenericType()
    format_fullxfull = GenericType()

    class Meta:
        primary_key_name = 'id'
