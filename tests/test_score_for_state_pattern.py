
import unittest
from ..bowling_state_pattern import FrameManager as FM

class FrameManagerTester(unittest.TestCase):

    def setUp(self):
        self.game_result = 'X4/34-4XXX45-34/'

    def test_good_result_national_rules(self):
        result = FM(self.game_result, rules=0).get_score()
        self.assertEqual(result['total_frames'], 10)
        self.assertEqual(result['total_score'], 133)

    def test_good_result_international_rules(self):
        result = FM(self.game_result).get_score()
        self.assertEqual(result['total_frames'], 10)
        self.assertEqual(result['total_score'], 139)

    def test_empty_game_result(self):
        self.game_result = ''
        with self.assertRaises(ValueError):
            FM(self.game_result).get_score()

    def test_single_char_game_result(self):
        self.game_result = '5'
        with self.assertRaises(ValueError):
            FM(self.game_result).get_score()

    def test_single_char_last_frame(self):
        self.game_result = f'{FM.STRIKE_SYMBOL*9}1'
        with self.assertRaises(ValueError):
            FM(self.game_result).get_score()

    def test_spare_frame(self):
        self.game_result = f'{FM.STRIKE_SYMBOL*9}{FM.SPARE_SYMBOL}1'
        with self.assertRaises(ValueError):
            FM(self.game_result).get_score()

    def test_strike_frame_with_extra_char(self):
        self.game_result = f'{FM.STRIKE_SYMBOL*9}1{FM.STRIKE_SYMBOL}'
        with self.assertRaises(ValueError):
            FM(self.game_result).get_score()

    def test_spare_frame_presented_as_digits(self):
        self.game_result = f'{FM.STRIKE_SYMBOL*9}55'
        with self.assertRaises(ValueError):
            FM(self.game_result).get_score()

    def test_frame_score_exceeds_pins_qty(self):
        self.game_result = f'{FM.STRIKE_SYMBOL*9}95'
        with self.assertRaises(ValueError):
            FM(self.game_result).get_score()

    def test_frames_qty_exceeds_frames_limit(self):
        self.game_result = f'{FM.STRIKE_SYMBOL*15}'
        with self.assertRaises(ValueError):
            FM(self.game_result).get_score()

if __name__ == '__main__':
    unittest.main()