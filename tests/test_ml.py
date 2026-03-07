import unittest
import os
import shutil
from unittest.mock import patch, MagicMock

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from geemap import ml
import ee

class TestML(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We don't need FakeEE here if we strictly mock ee objects when testing
        # Or we can patch ee.Geometry.Point, ee.Feature, ee.FeatureCollection
        pass

    def setUp(self):
        self.temp_dir = "tests/temp_ml_data"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @unittest.skipIf(not HAS_SKLEARN, "sklearn not installed")
    def test_tree_to_string_classification(self):
        # Create a simple decision tree classifier
        X = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])
        y = np.array([0, 1, 1, 0])
        clf = DecisionTreeClassifier(max_depth=2, random_state=42)
        clf.fit(X, y)

        tree_str = ml.tree_to_string(clf, feature_names=["f1", "f2"], output_mode="CLASSIFICATION")
        self.assertIsInstance(tree_str, str)
        self.assertTrue(tree_str.startswith("1) root"))

    @unittest.skipIf(not HAS_SKLEARN, "sklearn not installed")
    def test_tree_to_string_regression(self):
        # Create a simple decision tree regressor
        X = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])
        y = np.array([0.1, 0.9, 0.8, 0.2])
        reg = DecisionTreeRegressor(max_depth=2, random_state=42)
        reg.fit(X, y)

        tree_str = ml.tree_to_string(reg, feature_names=["f1", "f2"], output_mode="REGRESSION")
        self.assertIsInstance(tree_str, str)
        self.assertTrue(tree_str.startswith("1) root"))

    @unittest.skipIf(not HAS_SKLEARN, "sklearn not installed")
    @patch('multiprocessing.Pool')
    def test_rf_to_strings(self, mock_pool):
        # We need to mock multiprocessing because we don't want to actually spin up processes
        mock_pool_instance = mock_pool.return_value.__enter__.return_value
        # Mock map_async to return a mock result
        mock_async_result = MagicMock()
        mock_async_result.get.return_value = ["tree1_str", "tree2_str"]
        mock_pool_instance.map_async.return_value = mock_async_result

        X = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])
        y = np.array([0, 1, 1, 0])
        rf = RandomForestClassifier(n_estimators=2, max_depth=2, random_state=42)
        rf.fit(X, y)

        # Mock classes_ to avoid issues if output_mode INFER logic needs it
        rf.classes_ = np.array([0, 1])
        # Set criterion to gini so INFER mode knows it's a classifier
        rf.criterion = 'gini'

        trees = ml.rf_to_strings(rf, feature_names=["f1", "f2"], processes=1, output_mode="CLASSIFICATION")
        self.assertEqual(len(trees), 2)
        self.assertEqual(trees[0], "tree1_str")
        self.assertEqual(trees[1], "tree2_str")

    @patch('ee.Classifier.decisionTreeEnsemble')
    @patch('ee.String')
    def test_strings_to_classifier(self, mock_ee_string, mock_ensemble):
        mock_ensemble.return_value = "mocked_classifier"
        mock_ee_string.side_effect = lambda x: x

        trees = ["tree1", "tree2"]
        classifier = ml.strings_to_classifier(trees)
        self.assertEqual(classifier, "mocked_classifier")
        mock_ensemble.assert_called_once()
        mock_ee_string.assert_any_call("tree1")

    @patch('ee.Classifier.decisionTreeEnsemble')
    def test_fc_to_classifier(self, mock_ensemble):
        mock_ensemble.return_value = "mocked_classifier"

        # Mock ee.FeatureCollection and its aggregate_array method
        mock_fc = MagicMock()
        mock_aggregate = MagicMock()
        # The map function should return a list-like of ee.Strings, we'll just return a list
        mock_aggregate.map.return_value = ["tree1\n", "tree2\n"]
        mock_fc.aggregate_array.return_value = mock_aggregate

        classifier = ml.fc_to_classifier(mock_fc)
        self.assertEqual(classifier, "mocked_classifier")
        mock_ensemble.assert_called_once()
        mock_fc.aggregate_array.assert_called_with("tree")

    @patch('ee.batch.Export.table.toAsset')
    @patch('ee.FeatureCollection')
    @patch('ee.Feature')
    @patch('ee.Geometry.Point')
    def test_export_trees_to_fc(self, mock_point, mock_feature, mock_fc, mock_to_asset):
        mock_task = MagicMock()
        mock_to_asset.return_value = mock_task
        mock_point.return_value = "mocked_point"
        mock_feature.return_value = "mocked_feature"
        mock_fc.return_value = "mocked_fc"

        trees = ["tree1\n", "tree2\n"]
        ml.export_trees_to_fc(trees, asset_id="users/test/test_rf")

        mock_to_asset.assert_called_once_with(
            collection="mocked_fc",
            description="geemap_rf_export",
            assetId="users/test/test_rf"
        )
        mock_task.start.assert_called_once()

    def test_trees_to_csv(self):
        trees = ["tree1\n", "tree2\n"]
        out_csv = os.path.join(self.temp_dir, "test_trees.csv")
        ml.trees_to_csv(trees, out_csv)
        self.assertTrue(os.path.exists(out_csv))

        with open(out_csv, "r") as f:
            content = f.read()
        self.assertIn("tree1#", content)
        self.assertIn("tree2#", content)

    @patch('geemap.ml.fc_to_classifier')
    @patch('ee.FeatureCollection')
    @patch('ee.Feature')
    @patch('ee.Geometry.Point')
    def test_csv_to_classifier(self, mock_point, mock_feature, mock_fc, mock_fc_to_classifier):
        mock_fc_to_classifier.return_value = "mocked_classifier"

        trees = ["tree1", "tree2"]
        out_csv = os.path.join(self.temp_dir, "test_trees.csv")
        with open(out_csv, "w") as f:
            f.write("\n".join(trees))

        classifier = ml.csv_to_classifier(out_csv)
        self.assertEqual(classifier, "mocked_classifier")
        mock_fc_to_classifier.assert_called_once()

    def test_csv_to_classifier_file_not_found(self):
        classifier = ml.csv_to_classifier("non_existent_file.csv")
        self.assertIsNone(classifier)


if __name__ == '__main__':
    unittest.main()
