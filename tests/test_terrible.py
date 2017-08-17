#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `terrible` package."""

import shutil
import tempfile
import unittest
from click.testing import CliRunner

from terrible import terrible
from terrible import cli


class TestTerrible(unittest.TestCase):
    """Tests for `terrible` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        shutil.rmtree(self.test_dir)

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main, [self.test_dir])
        assert result.exit_code == 0
        assert '' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help       Show this message and exit.' in help_result.output
