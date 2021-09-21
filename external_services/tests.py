from unittest import TestCase

from external_services.fuel_price_request import get_fuel_price, parse_liga_html


class FuelRequest(TestCase):
    def setUp(self):
        pass

    def test_request(self):
        response, fuel = get_fuel_price()
        self.assertTrue(response)
        for name, value in fuel.items():
            self.assertIn(name, ['a95', 'a92', 'disel', 'gas'])
            self.assertTrue(value > 0, f'{name} is {value} - incorrect (zero or less)')

    def test_request_parser(self):
        html = '''
        <div class="biz-listoil-page">
<div class="main-part">
<div class="center-part">
<h1>цены на топливо</h1>

<div class="graphStat maingraphStat clearfix">
<div class="stat-block">
<div class="stat">
<table class="table striped">
<tbody><tr>
<th>Топливо</th>
<th>Цены, грн.</th>
<th>Динамика</th>
<th>Min/Max</th>
</tr>
<tr class="odd" onclick="if (!window.__cfRLUnblockHandlers) return false; window.location.href='/tek/oil/a-95'">
<td>
<a href="/tek/oil/a-95">Бензин А-95</a>
</td>
<td>
23.02 </td>
<td>
<i class="up">+</i><span class="upDown">0</span><i class="fas fa-caret-up" aria-hidden="true"></i> </td>
<td>
19.68 / 26.98 </td>
</tr>
<tr class="even" onclick="if (!window.__cfRLUnblockHandlers) return false; window.location.href='/tek/oil/a-92'">
<td>
<a href="/tek/oil/a-92">Бензин А-92</a>
</td>
<td>
21.96 </td>
<td>
<i class="up">+</i><span class="upDown">0</span><i class="fas fa-caret-up" aria-hidden="true"></i> </td>
<td>
 18.78 / 25.98 </td>
</tr>
<tr class="odd" onclick="if (!window.__cfRLUnblockHandlers) return false; window.location.href='/tek/oil/dt'">
<td>
<a href="/tek/oil/dt">Дизельное топливо</a>
</td>
<td>
22.43 </td>
<td>
<i class="up">+</i><span class="upDown">0</span><i class="fas fa-caret-up" aria-hidden="true"></i> </td>
<td>
18.50 / 25.98 </td>
</tr>
<tr class="even" onclick="if (!window.__cfRLUnblockHandlers) return false; window.location.href='/tek/oil/lpg'">
<td>
<a href="/tek/oil/lpg">Газ</a>
</td>
<td>
12.18 </td>
<td>
<i class="up">+</i><span class="upDown">0.01</span><i class="fas fa-caret-up" aria-hidden="true"></i> </td>
<td>
10.95 / 12.99 </td>
</tr>
</tbody></table>
</div>
        '''
        res, fuel = parse_liga_html(html)
        self.assertTrue(res)
        self.assertEqual(fuel, {'disel': 22.43, 'gas': 12.18, 'a95': 23.02, 'a92': 21.96})