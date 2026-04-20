"""Tests for the cli and ai modules."""

import datetime
import unittest
import unittest.mock

from click.testing import CliRunner

try:
    from geemap import ai

    HAS_AI = True
except ImportError:
    HAS_AI = False

from geemap.cli import main


@unittest.skipIf(not HAS_AI, "geemap.ai dependencies are not installed")
class TestMatchesDatetime(unittest.TestCase):

    def setUp(self):
        self.start_date = datetime.datetime(2020, 1, 1, tzinfo=datetime.UTC)
        self.end_date = datetime.datetime(2021, 1, 1, tzinfo=datetime.UTC)
        self.now = datetime.datetime.now(tz=datetime.UTC)
        self.before_start = datetime.datetime(2019, 12, 31, tzinfo=datetime.UTC)
        self.after_end = datetime.datetime(2021, 1, 2, tzinfo=datetime.UTC)
        self.within_interval = datetime.datetime(2020, 6, 1, tzinfo=datetime.UTC)
        self.after_now = self.now + datetime.timedelta(days=1)

    def test_end_date_set_query_within_interval(self):
        collection_interval = (self.start_date, self.end_date)
        self.assertTrue(ai.matches_datetime(collection_interval, self.within_interval))

    def test_end_date_set_query_exactly_at_start(self):
        collection_interval = (self.start_date, self.end_date)
        self.assertTrue(ai.matches_datetime(collection_interval, self.start_date))

    def test_end_date_set_query_exactly_at_end(self):
        collection_interval = (self.start_date, self.end_date)
        self.assertTrue(ai.matches_datetime(collection_interval, self.end_date))

    def test_end_date_set_query_before_start(self):
        collection_interval = (self.start_date, self.end_date)
        self.assertFalse(ai.matches_datetime(collection_interval, self.before_start))

    def test_end_date_set_query_after_end(self):
        collection_interval = (self.start_date, self.end_date)
        self.assertFalse(ai.matches_datetime(collection_interval, self.after_end))

    def test_end_date_none_query_before_start(self):
        collection_interval = (self.start_date, None)
        self.assertFalse(ai.matches_datetime(collection_interval, self.before_start))

    def test_end_date_none_query_within_interval(self):
        collection_interval = (self.start_date, None)
        # Assuming the interval from start_date to now contains this date
        self.assertTrue(ai.matches_datetime(collection_interval, self.within_interval))

    def test_end_date_none_query_after_now(self):
        collection_interval = (self.start_date, None)
        self.assertFalse(ai.matches_datetime(collection_interval, self.after_now))


class TestMain(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_main_no_args_returns_zero(self):
        result = self.runner.invoke(main)
        self.assertEqual(result.exit_code, 0)

    def test_main_no_args_outputs_message(self):
        result = self.runner.invoke(main)
        self.assertIn("geemap.cli.main", result.output)

    def test_main_no_args_outputs_click_docs_reference(self):
        result = self.runner.invoke(main)
        self.assertIn("click.palletsprojects.com", result.output)

    def test_main_help_flag_shows_help(self):
        result = self.runner.invoke(main, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Console script for geemap", result.output)

    def test_main_help_flag_shows_usage(self):
        result = self.runner.invoke(main, ["--help"])
        self.assertIn("Usage:", result.output)





@unittest.skipIf(not HAS_AI, "geemap.ai dependencies are not installed")
class TestFixEEPythonCode(unittest.TestCase):
    def test_fix_true_false_enabled(self):
        code = "var x = true; var y = false;"
        fixed = ai.fix_ee_python_code(code, fix_true_false=True)
        self.assertEqual(fixed, "var x = True; var y = False;")

    def test_fix_true_false_disabled(self):
        code = "var x = true; var y = false;"
        fixed = ai.fix_ee_python_code(code, fix_true_false=False)
        self.assertEqual(fixed, "var x = true; var y = false;")

    def test_fix_true_false_word_boundaries(self):
        code = "var str = 'this is true'; var not_true = true_ish;"
        fixed = ai.fix_ee_python_code(code, fix_true_false=True)
        self.assertEqual(fixed, "var str = 'this is True'; var not_true = true_ish;")



@unittest.skipIf(not HAS_AI, "geemap.ai dependencies are not installed")
class TestFixEEPythonCodeAI(unittest.TestCase):

    @unittest.mock.patch('geemap.ai.run_ee_code')
    def test_fix_ee_python_code_success_first_try(self, mock_run_ee_code):
        # Setup
        code = "import ee\nee.Image('FOO')"
        ee_mock = unittest.mock.MagicMock()
        geemap_mock = unittest.mock.MagicMock()

        # Action
        result = ai.fix_ee_python_code(code, ee_mock, geemap_mock)

        # Assert
        self.assertEqual(result, code)
        mock_run_ee_code.assert_called_once_with(code, ee_mock, geemap_mock)

    @unittest.mock.patch('geemap.ai.run_ee_code')
    @unittest.mock.patch('geemap.ai.genai.GenerativeModel')
    def test_fix_ee_python_code_success_second_try(self, mock_generative_model, mock_run_ee_code):
        # Setup
        broken_code = "import ee\nee.Image(FOO)"
        fixed_code = "import ee\nee.Image('FOO')"
        ee_mock = unittest.mock.MagicMock()
        geemap_mock = unittest.mock.MagicMock()

        # Make run_ee_code fail on first try, succeed on second try
        mock_run_ee_code.side_effect = [Exception("SyntaxError"), None]

        # Mock GenerativeModel
        mock_model_instance = unittest.mock.MagicMock()
        mock_response = unittest.mock.MagicMock()
        mock_response.text = '{"code": "' + fixed_code.replace('\n', '\\n') + '", "thoughts": "Added quotes."}'
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model_instance

        # Action
        result = ai.fix_ee_python_code(broken_code, ee_mock, geemap_mock)

        # Assert
        self.assertEqual(result, fixed_code)
        self.assertEqual(mock_run_ee_code.call_count, 2)
        mock_run_ee_code.assert_any_call(broken_code, ee_mock, geemap_mock)
        mock_run_ee_code.assert_any_call(fixed_code, ee_mock, geemap_mock)

    @unittest.mock.patch('geemap.ai.run_ee_code')
    @unittest.mock.patch('geemap.ai.genai.GenerativeModel')
    def test_fix_ee_python_code_exhaust_attempts(self, mock_generative_model, mock_run_ee_code):
        # Setup
        broken_code = "import ee\nee.Image(FOO)"
        ee_mock = unittest.mock.MagicMock()
        geemap_mock = unittest.mock.MagicMock()

        # Make run_ee_code always fail
        mock_run_ee_code.side_effect = Exception("SyntaxError")

        # Mock GenerativeModel
        mock_model_instance = unittest.mock.MagicMock()
        mock_response = unittest.mock.MagicMock()
        mock_response.text = '{"code": "' + broken_code.replace('\n', '\\n') + '", "thoughts": "Tried fixing."}'
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model_instance

        # Action & Assert
        with self.assertRaises(Exception) as context:
            ai.fix_ee_python_code(broken_code, ee_mock, geemap_mock)

        self.assertEqual(str(context.exception), "SyntaxError")
        self.assertEqual(mock_run_ee_code.call_count, 5)


    def test_fix_null_enabled(self):
        code = "var x = null;"
        fixed = ai.fix_ee_python_code(code, fix_null=True)
        self.assertEqual(fixed, "var x = None;")

    def test_fix_null_disabled(self):
        code = "var x = null;"
        fixed = ai.fix_ee_python_code(code, fix_null=False)
        self.assertEqual(fixed, "var x = null;")

    def test_quote_list_content(self):
        code = "var bands = [B4, B3, B2];"
        fixed = ai.fix_ee_python_code(code, quote_list_content=True)
        self.assertEqual(fixed, "var bands = ['B4', 'B3', 'B2'];")

    def test_quote_list_content_disabled(self):
        code = "var bands = [B4, B3, B2];"
        fixed = ai.fix_ee_python_code(code, quote_list_content=False)
        self.assertEqual(fixed, "var bands = [B4, B3, B2];")

if __name__ == "__main__":
    unittest.main()
