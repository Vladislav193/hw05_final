from datetime import date


def year(request):
    """Добавляет переменную с текущим годом."""
    date_now = date.today().year
    return {'year': date_now}
