import io

from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def download_shopcart(list_ing):
    sans_regular = 'core/static/fonts/OpenSans-Regular.ttf'
    sans_regular_name = 'OpenSans-Regular'
    sans_bold = 'core/static/fonts/OpenSans-Bold.ttf'
    sans_bold_name = 'OpenSans-Bold'

    pdfmetrics.registerFont(TTFont(sans_regular_name, sans_regular))
    pdfmetrics.registerFont(TTFont(sans_bold_name, sans_bold))

    buffer = io.BytesIO()
    draw = canvas.Canvas(buffer)

    canvas.setFillC
    draw.setFont(sans_bold_name, 32)
    draw.drawString(30, 775, 'FOODGRAM')

    draw.setFont(sans_regular_name, 20)
    draw.drawString(30, 740, 'Список покупок')
    draw.line(30, 730, 580, 730)

    draw.drawString(30, 700, 'К любым продуктам подойдет винишко =)')
    draw.line(30, 680, 580, 680)
    draw.line(30, 679, 580, 679)

    draw.setFont(sans_bold_name, 20)
    draw.drawString(30, 660, 'Для выбранных рецептов необходимо купить:')
    draw.setFont(sans_regular_name, 20)
    val = 640
    for step, ing in enumerate(list_ing):
        ingredient = list(ing.values())
        product = ingredient[0]
        unit = ingredient[1]
        amount = ingredient[2]
        string = f'{step+1}. {product} - {amount} {unit} '
        draw.drawString(30, val, string)
        val -= 20

    draw.showPage()
    draw.save()
    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename='shopcart.pdf'
    )
