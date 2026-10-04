"""Regression checks for fixed layout and portable browser-rendered plush output."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PlushWebTests(unittest.TestCase):
    def test_plush_cli_produces_live_html_and_source_config(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)/'preview.mp4'
            result = subprocess.run([sys.executable, '-m', 'architecture_motion_video.cli',
                'render', '--out', str(out), '--poster-only', '--duration', '2'],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            assets = out.with_name('preview-assets')
            self.assertTrue((assets/'plush.html').is_file(), 'Plush must now output a live webpage')
            self.assertTrue((assets/'plush.json').is_file(), 'Keep the editable scene')
            self.assertFalse(out.exists(), 'Preview must not create MP4')
            report=json.loads((assets/'web-validation.json').read_text())
            self.assertTrue(report['fixed_nodes'])
            self.assertTrue(report['repeat_seek'])
            self.assertEqual(report['canvas_overflow'], [])
            self.assertTrue(report['motion_changes'])
            self.assertEqual(report['mascots'], 6)
            page = (assets/'plush.html').read_text()
            self.assertIn('window.seek', page)
            self.assertNotIn('file:///Users/', page, 'HTML must not rely on creator paths')

class ArcLengthTests(unittest.TestCase):
    def test_speed_does_not_change_density(self):
        from architecture_motion_video.scripts.plush_scene import route
        curve=[[0,0],[0,100],[200,100],[200,0]]
        slow=route(curve,'#aabbcc',80,23)
        fast=route(curve,'#aabbcc',160,23)
        self.assertEqual(slow['count'],fast['count'])
        self.assertGreater(route(curve,'#aabbcc',80,12)['count'],slow['count'])

    def test_arc_length_matches_straight_line(self):
        from architecture_motion_video.scripts.plush_scene import route
        curve=[[0,0],[100,0],[200,0],[300,0]]
        path=route(curve,'#aabbcc',160,23)
        self.assertAlmostEqual(path['length'],300)
        self.assertTrue(all(a<b for a,b in zip(path['distances'],path['distances'][1:])))

if __name__ == '__main__':
    unittest.main()
