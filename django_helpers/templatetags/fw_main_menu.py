from django import template

register = template.Library()


@register.inclusion_tag('main_menu/menu.html', takes_context=True)
def fw_main_menu(context, menu, is_sub_menu: bool = False, *args, **kwargs):
    if context and hasattr(context, 'request'):
        active = False
        for item in menu:
            active |= item.check_active(context.request)
            # print(item.name, item.url, item.submenu, item.is_has_submenu())
    return {
        'menu': menu,
        'is_sub_menu': is_sub_menu,
        'open': active,
    }
