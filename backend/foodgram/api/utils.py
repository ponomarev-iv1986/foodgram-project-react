from io import BytesIO

from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .serializers import IngredientRecipe


def download_cart(request):
    ingredients = IngredientRecipe.objects.filter(
        recipe__shoppingcarts__user=request.user).values_list(
        'ingredient__name', 'ingredient__measurement_unit',
        'amount')
    cart_list = {}
    for name, unit, amount in ingredients:
        if name not in cart_list:
            cart_list[name] = {"amount": amount, "unit": unit}
        else:
            cart_list[name]["amount"] += amount
    height = 700
    buffer = BytesIO()
    pdfmetrics.registerFont(TTFont('arial', 'arial.ttf'))
    page = canvas.Canvas(buffer)
    page.setFont('arial', 14)
    page.drawString(100, 750, "Список покупок")
    for i, (name, data) in enumerate(cart_list.items(), start=1):
        page.drawString(
            80, height, f"{i}. {name} – {data['amount']} {data['unit']}"
        )
        height -= 25
    page.showPage()
    page.save()
    buffer.seek(0)
    return FileResponse(
        buffer, as_attachment=True, filename='shopping_list.pdf'
    )
