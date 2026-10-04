import argparse
import json
from pathlib import Path
import tempfile
import unittest
from architecture_motion_video.cli import settings

class StyleSettingsTests(unittest.TestCase):
    def test_existing_configs_keep_plush_default(self):
        self.assertEqual(settings(argparse.Namespace(config=None))['style'], 'plush')

    def test_cli_style_overrides_json_and_resolves_panel_path(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'render.json'
            config.write_text(json.dumps({'style': 'terminal-dark', 'panel_config': 'panel.json'}))
            result = settings(argparse.Namespace(config=config, style='light-pastel'))
            self.assertEqual(result['style'], 'light-pastel')
            self.assertEqual(result['panel_config'], str((Path(directory) / 'panel.json').resolve()))

    def test_rejects_unknown_or_wrong_type_styles(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'render.json'
            for value in ['missing', [], None]:
                config.write_text(json.dumps({'style': value}))
                with self.subTest(value=value), self.assertRaises(ValueError):
                    settings(argparse.Namespace(config=config))

    def test_panel_defaults_keep_sparse_reference_motion(self):
        result = settings(argparse.Namespace(config=None, style='terminal-dark'))
        self.assertEqual((result['speed'], result['spacing']), (80, 180))
        result = settings(argparse.Namespace(config=None, style='light-pastel', spacing=40))
        self.assertEqual((result['speed'], result['spacing']), (80, 40))

    def test_density_and_speed_remain_independent(self):
        result = settings(argparse.Namespace(config=None, speed=80))
        self.assertEqual(result['speed'], 80)
        self.assertEqual(result['spacing'], 23)

if __name__ == '__main__':
    unittest.main()
