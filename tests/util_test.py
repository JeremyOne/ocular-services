#!/usr/bin/env python3

import unittest
from enum import Enum
import sys
import os
from pathlib import Path
from ..tools.util import list_enums, load_template, log_text

class TestEnum(Enum):
    OPTION1 = "value1"
    OPTION2 = "value2"
    
    def __init__(self, value):
        self.description = f"Description for {value}"


class EmptyEnum(Enum):
    pass


class EnumWithoutDescription(Enum):
    OPTION1 = 1
    OPTION2 = 2


class TestListEnums(unittest.TestCase):
    
    def test_list_enums_with_valid_enum(self):
        """Test list_enums with a valid enum class"""
        result = list_enums(TestEnum)
        expected = "OPTION1: Description for value1\r\n, OPTION2: Description for value2\r\n"
        self.assertEqual(result, expected)
    
    def test_list_enums_with_empty_enum(self):
        """Test list_enums with an empty enum class"""
        result = list_enums(EmptyEnum)
        self.assertEqual(result, "")
    
    def test_list_enums_returns_string(self):
        """Test that list_enums returns a string"""
        result = list_enums(TestEnum)
        self.assertIsInstance(result, str)

    def test_list_enums_without_description(self):
        """Test list_enums with enum lacking description attribute"""
        with self.assertRaises(AttributeError):
            list_enums(EnumWithoutDescription)


class TestLoadTemplate(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary template file for testing
        self.test_template_path = "test_template.md"
        with open(self.test_template_path, "w", encoding="utf-8") as f:
            f.write("Test template content")
    
    def tearDown(self):
        # Remove the temporary template file
        if os.path.exists(self.test_template_path):
            os.remove(self.test_template_path)
    
    def test_load_template_success(self):
        """Test loading a template successfully"""
        result = load_template(self.test_template_path)
        self.assertEqual(result, "Test template content")
    
    def test_load_template_nonexistent_file(self):
        """Test loading a template that doesn't exist"""
        result = load_template("nonexistent_template.md")
        self.assertTrue(result.startswith("Error loading template:"))


class TestLogText(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary log file for testing
        self.test_log_file = "test_log.txt"
        
    def tearDown(self):
        # Remove the temporary log file
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)
        
        # Remove any created reports directory
        if os.path.exists("reports"):
            for file in os.listdir("reports"):
                if file.startswith("ocular_") and file.endswith(".log"):
                    os.remove(os.path.join("reports", file))
            if len(os.listdir("reports")) == 0:
                os.rmdir("reports")
    
    def test_log_text_custom_file(self):
        """Test logging text to a custom file"""
        test_text = "Test log message"
        log_text(test_text, self.test_log_file)
        
        with open(self.test_log_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        self.assertEqual(content, test_text)
    
    def test_log_text_default_file(self):
        """Test logging text to the default file"""
        test_text = "Default log test"
        log_text(test_text)
        
        # Check that reports directory was created
        self.assertTrue(os.path.exists("reports"))
        
        # Find the created log file
        log_files = [f for f in os.listdir("reports") if f.startswith("ocular_") and f.endswith(".log")]
        self.assertTrue(len(log_files) > 0)
        
        # Check content of the file
        with open(os.path.join("reports", log_files[0]), "r", encoding="utf-8") as f:
            content = f.read().strip()
        
        self.assertEqual(content, test_text)


if __name__ == '__main__':
    unittest.main()