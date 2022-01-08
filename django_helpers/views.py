# Create your views here.
from typing import Union, Iterable

from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin


class MeniItem:
    delimiter = ','
    item_delimiter = ';'

    def __init__(self, name: str, url: str = None, view: str = None, icon: str = None,
                 user: str = None, group: str = None, submenu: Iterable = None):
        self.url = url if not view else reverse_lazy(view)
        self.icon = icon
        self.name = name
        self.submenu = submenu
        self.active = None
        self.visible = True
        self.user_name = user
        self.group_name = group

    def is_has_submenu(self):
        return False if self.submenu is None else False if not self.submenu else True

    def check_active(self, request):
        if self.active is None:
            if hasattr(request, 'user'):
                if self.user_name is not None and self.user_name:
                    if not hasattr(request.user, 'USERNAME_FIELD'):
                        self.visible = self.user_name == 'anonymous'
                    else:
                        self.visible = getattr(request.user, request.user.USERNAME_FIELD) == self.user_name
                elif self.group_name is not None and self.group_name:
                    self.visible = self.group_name in request.user.groups.all() if hasattr(request.user,
                                                                                           'groups') else False
            self.active = True if self.url == request.path else str(request.path).startswith(
                str(self.url)) if self.url else False
            active = self.active
            if self.submenu:
                for item in self.submenu:
                    active |= item.check_active(request)
            self.active |= active
            # print(self.name, self.url, self.active, request.path)
            return active
        return self.active

    def is_active_submenu(self):
        if self.submenu:
            for item in self.submenu:
                # print(item.name, item.url, item.active)
                if item.active:
                    return True
        return False

    def is_active_element(self):
        # print(self.name, self.active)
        return self.active

    def is_active(self):
        if self.active:
            print(self.name, 'ACTIVE')
            return True
        return self.is_active_submenu()

    @classmethod
    def get_from_description_one(cls, description: Union[dict, Iterable, str]):
        if isinstance(description, str):
            if description.find(cls.delimiter):
                return cls(*description.split(cls.delimiter))
            else:
                return cls(description)
        elif isinstance(description, dict):
            return cls(**description)
        elif isinstance(description, Iterable):
            return cls(*description)
        else:
            return None

    @classmethod
    def get_from_description(cls, description: Union[dict, Iterable, str]):
        if description is None or not description:
            return []

        if isinstance(description, str):
            if description.find(cls.item_delimiter):
                return [cls.get_from_description_one(item) for item in description.split(cls.item_delimiter)]
            else:
                return [cls.get_from_description_one(description)]
        elif isinstance(description, dict):
            result = []
            for name in description:
                value = description[name]
                if 'submenu' in value:
                    subs = value['submenu']
                    url = value.get('url', None)
                    view = value.get('view', None)
                    icon = value.get('icon', None)
                    user = value.get('user', None)
                    group = value.get('group', None)
                    if isinstance(subs, Iterable):
                        result.append(cls(name, url, view, icon, user, group, cls.get_from_description(subs)))
                    else:
                        result.append(cls(name, url, view, icon, user, group, [cls.get_from_description_one(subs)]))
                else:
                    result.append(cls(name, **value))
            return result
        elif isinstance(description, Iterable):
            if len(description) < 7:
                return [cls.get_from_description_one(description)]
            else:
                name, url, view, icon, user, group, subs = description
                if isinstance(subs, Iterable):
                    return [cls(name, url, view, icon, user, group, cls.get_from_description(subs))]
                else:
                    return [cls(name, url, view, icon, user, group, [cls.get_from_description_one(subs)])]
        else:
            return []


class MainMenuView(ContextMixin):
    main_menu = {}
    main_menu_variable_name = 'main_menu'

    def __init__(self) -> None:
        super().__init__()
        self.main_menu = MeniItem.get_from_description(self.main_menu)

    def get_context_data(self, *args, **kwargs):
        context = super(MainMenuView, self).get_context_data(*args, **kwargs)
        context[self.main_menu_variable_name] = self.form_main_menu()
        return context

    def form_main_menu(self):
        return self.main_menu

    @classmethod
    def form_menu_context(cls, request):
        menu = cls()
        return {
            menu.main_menu_variable_name: menu.form_main_menu()
        }
