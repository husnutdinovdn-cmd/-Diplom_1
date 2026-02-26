"""
Юнит-тесты для класса Burger.
Используются моки для Bun и Ingredient, параметризация для проверки разных сценариев.
"""
import pytest
from unittest.mock import Mock

from praktikum.burger import Burger
from praktikum.bun import Bun
from praktikum.ingredient import Ingredient


class TestBurgerInit:
    """Тесты инициализации бургера."""

    def test_init_bun_is_none(self):
        burger = Burger()
        assert burger.bun is None

    def test_init_ingredients_empty(self):
        burger = Burger()
        assert burger.ingredients == []


class TestBurgerSetBuns:
    """Тесты установки булочки."""

    def test_set_buns_sets_bun(self):
        burger = Burger()
        bun = Mock(spec=Bun)
        burger.set_buns(bun)
        assert burger.bun is bun


class TestBurgerAddIngredient:
    """Тесты добавления ингредиентов."""

    def test_add_ingredient_appends_to_list(self):
        burger = Burger()
        ingredient = Mock(spec=Ingredient)
        burger.add_ingredient(ingredient)
        assert burger.ingredients == [ingredient]

    def test_add_ingredient_multiple_preserves_order(self):
        burger = Burger()
        ing1, ing2, ing3 = Mock(spec=Ingredient), Mock(spec=Ingredient), Mock(spec=Ingredient)
        burger.add_ingredient(ing1)
        burger.add_ingredient(ing2)
        burger.add_ingredient(ing3)
        assert burger.ingredients == [ing1, ing2, ing3]


class TestBurgerRemoveIngredient:
    """Тесты удаления ингредиента по индексу (параметризация)."""

    @pytest.mark.parametrize('index_to_remove', [0, 1, 2])
    def test_remove_ingredient_at_index(self, index_to_remove):
        burger = Burger()
        ingredients = [Mock(spec=Ingredient) for _ in range(3)]
        for ing in ingredients:
            burger.add_ingredient(ing)
        burger.remove_ingredient(index_to_remove)
        expected = [ing for i, ing in enumerate(ingredients) if i != index_to_remove]
        assert burger.ingredients == expected

    def test_remove_ingredient_index_error_if_invalid(self):
        burger = Burger()
        burger.add_ingredient(Mock(spec=Ingredient))
        with pytest.raises(IndexError):
            burger.remove_ingredient(5)


class TestBurgerMoveIngredient:
    """Тесты перемещения ингредиента (параметризация)."""

    @pytest.mark.parametrize('index,new_index,expected_order', [
        (0, 2, [1, 2, 0]),
        (2, 0, [2, 0, 1]),
        (1, 1, [0, 1, 2]),
        (0, 1, [1, 0, 2]),
    ])
    def test_move_ingredient_reorders_correctly(self, index, new_index, expected_order):
        burger = Burger()
        ingredients = [Mock(spec=Ingredient) for _ in range(3)]
        for ing in ingredients:
            burger.add_ingredient(ing)
        burger.move_ingredient(index, new_index)
        expected = [ingredients[i] for i in expected_order]
        assert burger.ingredients == expected


class TestBurgerGetPrice:
    """Тесты расчёта цены с моками и параметризацией."""

    def test_get_price_only_bun_doubled(self):
        burger = Burger()
        mock_bun = Mock(spec=Bun)
        mock_bun.get_price.return_value = 50.0
        burger.set_buns(mock_bun)
        assert burger.get_price() == 100.0
        mock_bun.get_price.assert_called_once()

    @pytest.mark.parametrize('bun_price,expected_total', [
        (100.0, 200.0),
        (50.5, 101.0),
        (0.0, 0.0),
    ])
    def test_get_price_bun_only_parametrized(self, bun_price, expected_total):
        burger = Burger()
        mock_bun = Mock(spec=Bun)
        mock_bun.get_price.return_value = bun_price
        burger.set_buns(mock_bun)
        assert burger.get_price() == expected_total

    def test_get_price_bun_plus_ingredients(self):
        burger = Burger()
        mock_bun = Mock(spec=Bun)
        mock_bun.get_price.return_value = 10.0
        burger.set_buns(mock_bun)
        ing1 = Mock(spec=Ingredient)
        ing1.get_price.return_value = 5.0
        ing2 = Mock(spec=Ingredient)
        ing2.get_price.return_value = 3.0
        burger.add_ingredient(ing1)
        burger.add_ingredient(ing2)
        assert burger.get_price() == 10.0 * 2 + 5.0 + 3.0  # 28.0

    @pytest.mark.parametrize('ingredient_prices', [
        [10.0],
        [1.0, 2.0, 3.0],
        [0.5, 0.5],
    ])
    def test_get_price_sum_of_ingredients_parametrized(self, ingredient_prices):
        burger = Burger()
        mock_bun = Mock(spec=Bun)
        mock_bun.get_price.return_value = 0.0
        burger.set_buns(mock_bun)
        for p in ingredient_prices:
            ing = Mock(spec=Ingredient)
            ing.get_price.return_value = p
            burger.add_ingredient(ing)
        assert burger.get_price() == sum(ingredient_prices)


class TestBurgerGetReceipt:
    """Тесты формирования чека с моками."""

    def test_get_receipt_calls_bun_get_name(self):
        burger = Burger()
        mock_bun = Mock(spec=Bun)
        mock_bun.get_name.return_value = 'black bun'
        mock_bun.get_price.return_value = 100.0
        burger.set_buns(mock_bun)
        receipt = burger.get_receipt()
        assert '(==== black bun ====)' in receipt
        assert 'Price: 200.0' in receipt
        assert mock_bun.get_name.call_count >= 2  # в шапке и в подвале

    def test_get_receipt_includes_ingredient_lines(self):
        burger = Burger()
        mock_bun = Mock(spec=Bun)
        mock_bun.get_name.return_value = 'white bun'
        mock_bun.get_price.return_value = 50.0
        burger.set_buns(mock_bun)
        mock_ing = Mock(spec=Ingredient)
        mock_ing.get_type.return_value = 'SAUCE'
        mock_ing.get_name.return_value = 'hot sauce'
        mock_ing.get_price.return_value = 10.0
        burger.add_ingredient(mock_ing)
        receipt = burger.get_receipt()
        assert '= sauce hot sauce =' in receipt
        assert 'Price: 110.0' in receipt  # 50*2 + 10

    @pytest.mark.parametrize('ing_type,ing_name,expected_line', [
        ('SAUCE', 'sour cream', '= sauce sour cream ='),
        ('FILLING', 'cutlet', '= filling cutlet ='),
    ])
    def test_get_receipt_ingredient_type_lowercase(self, ing_type, ing_name, expected_line):
        burger = Burger()
        mock_bun = Mock(spec=Bun)
        mock_bun.get_name.return_value = 'bun'
        mock_bun.get_price.return_value = 0.0
        burger.set_buns(mock_bun)
        mock_ing = Mock(spec=Ingredient)
        mock_ing.get_type.return_value = ing_type
        mock_ing.get_name.return_value = ing_name
        mock_ing.get_price.return_value = 0.0
        burger.add_ingredient(mock_ing)
        receipt = burger.get_receipt()
        assert expected_line in receipt

    def test_get_receipt_full_structure_only_bun(self):
        burger = Burger()
        mock_bun = Mock(spec=Bun)
        mock_bun.get_name.return_value = 'black bun'
        mock_bun.get_price.return_value = 100.0
        burger.set_buns(mock_bun)
        receipt = burger.get_receipt()
        expected = (
            '(==== black bun ====)\n'
            '(==== black bun ====)\n\n'
            'Price: 200.0'
        )
        assert receipt == expected

    def test_get_receipt_full_structure_bun_and_ingredients(self):
        burger = Burger()
        mock_bun = Mock(spec=Bun)
        mock_bun.get_name.return_value = 'white bun'
        mock_bun.get_price.return_value = 50.0
        burger.set_buns(mock_bun)
        ing1 = Mock(spec=Ingredient)
        ing1.get_type.return_value = 'SAUCE'
        ing1.get_name.return_value = 'hot sauce'
        ing1.get_price.return_value = 10.0
        ing2 = Mock(spec=Ingredient)
        ing2.get_type.return_value = 'FILLING'
        ing2.get_name.return_value = 'cutlet'
        ing2.get_price.return_value = 20.0
        burger.add_ingredient(ing1)
        burger.add_ingredient(ing2)
        receipt = burger.get_receipt()
        expected = (
            '(==== white bun ====)\n'
            '= sauce hot sauce =\n'
            '= filling cutlet =\n'
            '(==== white bun ====)\n\n'
            'Price: 130.0'
        )
        assert receipt == expected

    def test_get_receipt_empty_ingredients_order_and_price(self):
        burger = Burger()
        mock_bun = Mock(spec=Bun)
        mock_bun.get_name.return_value = 'bun'
        mock_bun.get_price.return_value = 0.0
        burger.set_buns(mock_bun)
        receipt = burger.get_receipt()
        assert '(==== bun ====)' in receipt
        assert receipt.endswith('Price: 0.0')
        assert mock_bun.get_name.call_count >= 2
