# Controllers/TranslationController.py
import os
import json
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class TranslationController:
    """多语言翻译控制器，负责管理翻译资源和语言切换"""

    def __init__(self, assets_dir="Assets"):
        """
        初始化翻译控制器

        Args:
            assets_dir: 存储翻译文件的目录
        """
        self.assets_dir = assets_dir
        self.languages = {
            "en": {"name": "English", "file": "EnglishTranslation.json"},
            "zh": {"name": "中文", "file": "ChineseTranslation.json"},
            "sv": {"name": "Svenska", "file": "SwedishTranslation.json"}
        }
        self.current_language = None  # 当前语言
        self.translations = {}  # 当前语言的翻译

        # 确保资源目录存在
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)

        # 检查翻译文件是否存在
        self._check_translation_files()

        # 首先尝试加载用户偏好语言
        preferred_lang = self.load_language_preference()
        if preferred_lang and self.set_language(preferred_lang):
            pass
        # 默认使用英语
        elif "en" in self.languages and self.set_language("en"):
            pass
        # 如果英语也不可用，尝试加载第一个可用语言
        elif len(self.languages) > 0:
            self.set_language(next(iter(self.languages)))

    def _check_translation_files(self):
        """检查翻译文件是否存在，移除不存在的语言"""
        available_languages = {}
        for lang_code, lang_info in self.languages.items():
            file_path = os.path.join(self.assets_dir, lang_info["file"])
            if os.path.exists(file_path):
                available_languages[lang_code] = lang_info
            else:
                print(f"警告：翻译文件 '{lang_info['file']}' 不存在，将不可使用 {lang_info['name']} 语言")

        self.languages = available_languages

    def get_available_languages(self):
        """返回所有可用语言的代码和名称"""
        return {code: info["name"] for code, info in self.languages.items()}

    def set_language(self, lang_code):
        """
        设置当前语言

        Args:
            lang_code: 语言代码，例如 "en", "zh", "sv"

        Returns:
            bool: 是否成功加载语言
        """
        if lang_code not in self.languages:
            print(f"语言 {lang_code} 不可用")
            return False

        try:
            file_path = os.path.join(self.assets_dir, self.languages[lang_code]["file"])
            with open(file_path, 'r', encoding='utf-8') as file:
                self.translations = json.load(file)
                self.current_language = lang_code
                self.save_language_preference(lang_code)
                return True
        except Exception as e:
            print(f"加载语言 {lang_code} 失败: {e}")
            return False

    def get_text(self, key_path, default=None, **format_args):
        """
        获取指定键路径的翻译文本

        Args:
            key_path: 点分隔的键路径，例如 "general.welcome"
            default: 如果键不存在，返回的默认值
            format_args: 用于格式化字符串的参数

        Returns:
            str: 翻译后的文本
        """
        if not self.translations:
            return default if default is not None else key_path

        # 沿着键路径查找值
        value = self.translations
        keys = key_path.split('.')

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default if default is not None else key_path

        # 如果有格式化参数，应用它们
        if isinstance(value, str) and format_args:
            try:
                return value.format(**format_args)
            except KeyError:
                # 如果格式化失败，返回原始字符串
                return value

        return value

    def get_current_language(self):
        """返回当前语言代码"""
        return self.current_language

    def save_language_preference(self, lang_code):
        """
        保存用户的语言偏好

        Args:
            lang_code: 语言代码
        """
        try:
            # 创建一个用户配置文件目录（如果不存在）
            config_dir = os.path.expanduser("~/.barapp")
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            # 写入语言偏好
            with open(os.path.join(config_dir, "language.txt"), 'w') as file:
                file.write(lang_code)
        except:
            # 如果保存失败，默默忽略
            pass

    def load_language_preference(self):
        """
        加载用户的语言偏好

        Returns:
            str: 语言代码，如果找不到则为None
        """
        try:
            # 尝试读取语言偏好
            config_file = os.path.expanduser("~/.barapp/language.txt")
            if os.path.exists(config_file):
                with open(config_file, 'r') as file:
                    lang_code = file.read().strip()
                    if lang_code in self.languages:
                        return lang_code
        except:
            pass

        return None

    def set_language(self, lang_code):
        """
        设置当前语言

        Args:
            lang_code: 语言代码，例如 "en", "zh", "sv"

        Returns:
            bool: 是否成功加载语言
        """
        if lang_code not in self.languages:
            print(f"语言 {lang_code} 不可用")
            return False

        try:
            file_path = os.path.join(self.assets_dir, self.languages[lang_code]["file"])
            print(f"尝试加载翻译文件: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as file:
                self.translations = json.load(file)
                self.current_language = lang_code
                self.save_language_preference(lang_code)

                # 打印一些关键翻译项以验证
                print(
                    f"已加载 {lang_code} 语言，translations['general']['app_title'] = {self.translations.get('general', {}).get('app_title', 'Not found')}")
                return True
        except Exception as e:
            print(f"加载语言 {lang_code} 失败: {e}")
            return False

    def get_text(self, key_path, default=None, **format_args):
        """
        获取指定键路径的翻译文本

        Args:
            key_path: 点分隔的键路径，例如 "general.welcome"
            default: 如果键不存在，返回的默认值
            format_args: 用于格式化字符串的参数

        Returns:
            str: 翻译后的文本
        """
        if not self.translations:
            print(f"翻译字典为空，返回默认值: {default}")
            return default if default is not None else key_path

        # 沿着键路径查找值
        value = self.translations
        keys = key_path.split('.')

        for i, key in enumerate(keys):
            path_so_far = '.'.join(keys[:i + 1])
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                print(f"翻译键 '{key_path}' 不存在 (在 '{path_so_far}' 处找不到 '{key}')")
                return default if default is not None else key_path

        # 如果有格式化参数，应用它们
        if isinstance(value, str) and format_args:
            try:
                return value.format(**format_args)
            except KeyError as e:
                print(f"格式化翻译文本失败: {e}")
                # 如果格式化失败，返回原始字符串
                return value

        return value