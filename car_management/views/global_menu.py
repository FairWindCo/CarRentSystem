from django_helpers.views import MainMenuView


class GlobalMainMenu(MainMenuView):
    main_menu = {
        'DashBoard': {
            'icon': 'grid-fill',
            'view': 'dashboard',
            # 'user': 'admin_pages'
        },
        'Финансы': {
            'group': 'anon'
        },
        'Балансы': {
            'icon': 'basket-fill',
            'submenu': {
                'Машин': {
                    'view': 'cars',
                    'icon': 'card',
                },
                'Ивест.': {
                    'view': 'invest',
                },
                'Водители': {
                    'view': 'drivers',
                },
                'Патнеры': {
                    'view': 'investors',
                },
                'Контрагенты': {
                    'view': 'counterparts',
                },
                'Операторы': {
                    'view': 'taxi_operators',
                },
            }
        },
        'Поездки': {
            'icon': 'map',
            'submenu': {
                'Такси': {
                    'icon': 'smartwatch',
                    'view': 'all_trips',
                },
                'GPS': {
                    'icon': 'broadcast',
                    'view': 'all_wialon_trips',
                },
            }
        },
        'Затраты': {
            'view': 'all_expenses',
            'icon': 'bag',
        },
        'Средства': {
            'icon': 'credit-card',
            'submenu': {
                'Кассы': {
                    'view': 'cashbox',
                    'icon': 'cash',
                },
                'Транзакции': {
                    'view': 'all_transactions',
                },
                'Операции': {
                    'view': 'all_operations',
                },
            },
        },
        'Статистика': {
            'icon': 'calendar2-date-fill',
            'submenu': {
                'Статистика Такси': {
                    'icon': 'smartwatch',
                    'view': 'trip_stat',
                },
                'Статистика GPS': {
                    'icon': 'broadcast',
                    'view': 'all_wialon_stat',
                },
            }
        },
        'Отчеты': {
            'icon': 'receipt',
            'submenu': {
                'Отчет по авто': {
                    'view': 'car_report',
                },
            }
        },
    }
