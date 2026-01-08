import os
import tempfile
import unittest

import pandas as pd

import analysis
from analysis import AnalysisException


class AnalysisTestCase(unittest.TestCase):
    def make_csv(self, rows):
        """Create a temporary CSV file with required headers and provided rows (list of dicts)."""
        required_fields = [
            'issue_id',
            'issue_key',
            'issue_type_name',
            'issue_created_date',
            'changelog_id',
            'status_change_date',
            'status_from_name',
            'status_to_name',
            'status_from_category_name',
            'status_to_category_name',
            'project_key',
            'issue_points',
        ]
        df = pd.DataFrame(rows, columns=required_fields)
        fd, path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        df.to_csv(path, index=False)
        return path

    def test_read_data_missing_fields_raises(self):
        # Missing 'status_to_name' to trigger exception
        data = pd.DataFrame([
            {
                'issue_id': 1,
                'issue_key': 'PRJ-1',
                'issue_type_name': 'Task',
                'issue_created_date': '2025-01-02T10:00:00Z',
                'changelog_id': 1,
                'status_change_date': '2025-01-03T09:00:00Z',
                'status_from_name': 'To Do',
                # 'status_to_name': 'In Progress',
                'status_from_category_name': 'To Do',
                'status_to_category_name': 'In Progress',
                'project_key': 'PRJ',
                'issue_points': 1,
            }
        ])
        fd, path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        data.drop(columns=['status_to_name'], inplace=True)
        data.to_csv(path, index=False)
        try:
            with self.assertRaises(AnalysisException):
                analysis.read_data(path)
        finally:
            os.remove(path)

    def test_read_data_filters_and_counts_duplicates(self):
        # Two rows for same issue/changelog (duplicate) + one valid, and one row outside 'until' filter excluded
        rows = [
            {
                'issue_id': 1,
                'issue_key': 'PRJ-1',
                'issue_type_name': 'Task',
                'issue_created_date': '2025-01-02T10:00:00Z',
                'changelog_id': 1,
                'status_change_date': '2025-01-03T09:00:00Z',
                'status_from_name': 'To Do',
                'status_to_name': 'In Progress',
                'status_from_category_name': 'To Do',
                'status_to_category_name': 'In Progress',
                'project_key': 'PRJ',
                'issue_points': 1,
            },
            {
                # duplicate of above
                'issue_id': 1,
                'issue_key': 'PRJ-1',
                'issue_type_name': 'Task',
                'issue_created_date': '2025-01-02T10:00:00Z',
                'changelog_id': 1,
                'status_change_date': '2025-01-03T09:00:00Z',
                'status_from_name': 'To Do',
                'status_to_name': 'In Progress',
                'status_from_category_name': 'To Do',
                'status_to_category_name': 'In Progress',
                'project_key': 'PRJ',
                'issue_points': 1,
            },
            {
                'issue_id': 1,
                'issue_key': 'PRJ-1',
                'issue_type_name': 'Task',
                'issue_created_date': '2025-01-02T10:00:00Z',
                'changelog_id': 2,
                'status_change_date': '2025-01-06T09:00:00Z',
                'status_from_name': 'In Progress',
                'status_to_name': 'Done',
                'status_from_category_name': 'In Progress',
                'status_to_category_name': 'Done',
                'project_key': 'PRJ',
                'issue_points': 1,
            },
            {
                # outside until (created exactly at until date, should be excluded)
                'issue_id': 2,
                'issue_key': 'PRJ-2',
                'issue_type_name': 'Bug',
                'issue_created_date': '2025-01-10T00:00:00Z',
                'changelog_id': 3,
                'status_change_date': '2025-01-10T01:00:00Z',
                'status_from_name': 'To Do',
                'status_to_name': 'Done',
                'status_from_category_name': 'To Do',
                'status_to_category_name': 'Done',
                'project_key': 'PRJ',
                'issue_points': 1,
            },
        ]
        path = self.make_csv(rows)
        try:
            data, dupes, filtered = analysis.read_data(
                path, since='2025-01-01', until='2025-01-10'
            )
            # One duplicate should be removed
            self.assertEqual(dupes, 1)
            # The last row should be filtered out by 'until' (strictly less than)
            self.assertTrue((data['issue_key'] == 'PRJ-2').sum() == 0)
            # Remaining rows should be 2 (first valid + complete)
            self.assertEqual(len(data), 2)
        finally:
            os.remove(path)

    def test_process_issue_data_weekend_exclusion_and_non_negative(self):
        # Build dataset with weekend between in_progress and complete and one invalid negative case
        rows = [
            # Issue 1: Fri 3rd -> Mon 6th, weekend excluded reduces cycle time from 3 to 1
            {
                'issue_id': 1,
                'issue_key': 'PRJ-1',
                'issue_type_name': 'Task',
                'issue_created_date': '2025-01-02T10:00:00Z',
                'changelog_id': 1,
                'status_change_date': '2025-01-03T09:00:00Z',
                'status_from_name': 'To Do',
                'status_to_name': 'In Progress',
                'status_from_category_name': 'To Do',
                'status_to_category_name': 'In Progress',
                'project_key': 'PRJ',
                'issue_points': 1,
            },
            {
                'issue_id': 1,
                'issue_key': 'PRJ-1',
                'issue_type_name': 'Task',
                'issue_created_date': '2025-01-02T10:00:00Z',
                'changelog_id': 2,
                'status_change_date': '2025-01-06T09:00:00Z',
                'status_from_name': 'In Progress',
                'status_to_name': 'Done',
                'status_from_category_name': 'In Progress',
                'status_to_category_name': 'Done',
                'project_key': 'PRJ',
                'issue_points': 1,
            },
            # Issue 2: completion before creation -> times should be coerced to 0
            {
                'issue_id': 2,
                'issue_key': 'PRJ-2',
                'issue_type_name': 'Bug',
                'issue_created_date': '2025-01-10T10:00:00Z',
                'changelog_id': 3,
                'status_change_date': '2025-01-09T09:00:00Z',
                'status_from_name': 'To Do',
                'status_to_name': 'Done',
                'status_from_category_name': 'To Do',
                'status_to_category_name': 'Done',
                'project_key': 'PRJ',
                'issue_points': 3,
            },
        ]
        path = self.make_csv(rows)
        try:
            data, _, _ = analysis.read_data(path, since='2025-01-01', until='2025-01-15')

            # Without weekend exclusion
            issue_data, _ = analysis.process_issue_data(data, exclude_weekends=False)
            # PRJ-1 cycle_time_days ~ 3 days, lead_time_days ~ 4 days
            self.assertAlmostEqual(issue_data.loc['PRJ-1']['cycle_time_days'], 3.0, places=4)
            self.assertAlmostEqual(issue_data.loc['PRJ-1']['lead_time_days'], 4.0, places=4)

            # With weekend exclusion
            issue_data_excl, _ = analysis.process_issue_data(data, exclude_weekends=True)
            self.assertAlmostEqual(issue_data_excl.loc['PRJ-1']['cycle_time_days'], 1.0, places=4)
            self.assertAlmostEqual(issue_data_excl.loc['PRJ-1']['lead_time_days'], 2.0, places=4)

            # Non-negative enforcement for PRJ-2
            self.assertEqual(issue_data_excl.loc['PRJ-2']['cycle_time_days'], 0)
            self.assertEqual(issue_data_excl.loc['PRJ-2']['lead_time_days'], 0)
        finally:
            os.remove(path)

    def test_process_throughput_data_computes_daily_and_weekly(self):
        rows = [
            {
                'issue_id': 1,
                'issue_key': 'PRJ-1',
                'issue_type_name': 'Task',
                'issue_created_date': '2025-01-02T10:00:00Z',
                'changelog_id': 1,
                'status_change_date': '2025-01-03T09:00:00Z',
                'status_from_name': 'To Do',
                'status_to_name': 'In Progress',
                'status_from_category_name': 'To Do',
                'status_to_category_name': 'In Progress',
                'project_key': 'PRJ',
                'issue_points': 2,
            },
            {
                'issue_id': 1,
                'issue_key': 'PRJ-1',
                'issue_type_name': 'Task',
                'issue_created_date': '2025-01-02T10:00:00Z',
                'changelog_id': 2,
                'status_change_date': '2025-01-06T09:00:00Z',
                'status_from_name': 'In Progress',
                'status_to_name': 'Done',
                'status_from_category_name': 'In Progress',
                'status_to_category_name': 'Done',
                'project_key': 'PRJ',
                'issue_points': 2,
            },
        ]
        path = self.make_csv(rows)
        try:
            data, _, _ = analysis.read_data(path, since='2025-01-01', until='2025-01-10')
            issue_data, _ = analysis.process_issue_data(data)
            t, tw = analysis.process_throughput_data(issue_data, since='2025-01-01', until='2025-01-10')

            # Daily throughput should have a 1 on 2025-01-06 and 0 elsewhere in range
            self.assertIn(pd.Timestamp('2025-01-06'), t.index)
            self.assertEqual(int(t.loc[pd.Timestamp('2025-01-06')]['Throughput']), 1)
            # Velocity equals points if points present
            self.assertEqual(int(t.loc[pd.Timestamp('2025-01-06')]['Velocity']), 2)

            # Weekly throughput should be non-empty and include the week bin that contains Jan 6 (W-Mon)
            self.assertGreater(len(tw), 0)
            self.assertTrue('Throughput' in tw.columns)
        finally:
            os.remove(path)

    def test_montecarlo_returns_none_on_empty_throughput(self):
        empty = pd.DataFrame()
        self.assertIsNone(analysis.forecast_montecarlo_how_long_items(empty))
        self.assertIsNone(analysis.forecast_montecarlo_how_many_items(empty))

    def test_calculate_flow_efficiency(self):
        # Missing file -> 0
        self.assertEqual(analysis.calculate_flow_efficiency('nonexistent.csv', 'PRJ'), 0)

        # Valid file
        fd, path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        df = pd.DataFrame([
            {'project_key': 'PRJ', 'status_name': 'To Do', 'wait_status': True},
            {'project_key': 'PRJ', 'status_name': 'In Progress', 'wait_status': False},
            {'project_key': 'PRJ', 'status_name': 'Done', 'wait_status': False},
            {'project_key': 'OTHER', 'status_name': 'Other', 'wait_status': True},
        ])
        df.to_csv(path, index=False)
        try:
            eff = analysis.calculate_flow_efficiency(path, 'PRJ')
            # 2 work statuses out of 3 PRJ statuses = 66.666...
            self.assertAlmostEqual(eff, (2/3)*100, places=3)
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
