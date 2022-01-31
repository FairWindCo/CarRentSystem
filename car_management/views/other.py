from django.shortcuts import render


def test_view(request):
    return render(request, 'admin_template/base_template.html', {})