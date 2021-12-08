from main_menu.views import MainMenuView


class GlobalMainMenu(MainMenuView):
    main_menu = {
        'DashBoard': {
            'icon': 'grid-fill',
            'view': 'dashboard',
            # 'user': 'admin'
        },
        'Финансы': {
            'group': 'anon'
        },
        'Балансы': {
            'icon': 'grid-fill',
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
            'view': 'all_trips',
            'icon': 'map',
        },
        'Затраты': {
            'view': 'all_expenses',
            'icon': 'bag',
        },
        'Средства': {
            'icon': 'credit-card',
            'submenu': {
                'Транзакции': {
                    'view': 'all_transactions',
                },
                'Операции': {
                    'view': 'all_operations',
                },
            },
        },
        'Статистика': {
            'submenu': {
                'Статистика': {
                    'view': 'trip_stat',
                },
            }
        },
        'Отчеты': {
            'submenu': {
                'Отчет по авто': {
                    'view': 'car_report',
                },
            }
        },
    }