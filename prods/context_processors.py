from .models import Category,Cart

def list_categories(request):
    """
    List categories in sidebar
    """
    return {"cats":Category.objects.all()}

# Note: let op cart gets created NOT at the stage of index view, but
# when custemer clicks first to ADD prod into a Cart...
def count_items_cart(request):
    """
    Amount items for menubar
    """
    cart_id = request.session.get('cart_id', 0)
    #print(cart_id)
    if cart_id:
        qs = Cart.objects.filter(id=cart_id,accepted =False)
        cart_obj = qs.last()
        try:
            qty = cart_obj.get_sum_items_amount()
            return {"qty":qty}
        except:
            print('Smth wrong with sessions')
            qty = ""

    else:
        return {"qty":0}
