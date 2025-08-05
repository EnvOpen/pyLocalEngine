#!/usr/bin/env python3
"""
Migration utilities for converting locale files to LocalEngine format.

This script helps migrate from other localization libraries and formats
to the LocalEngine specification-compliant format.
"""

import json
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import argparse


class LocaleFileMigrator:
    """Utility class for migrating locale files to LocalEngine format."""
    
    def __init__(self, target_format: str = 'json'):
        """
        Initialize the migrator.
        
        Args:
            target_format: Target format ('json', 'yaml', or 'xml')
        """
        self.target_format = target_format.lower()
        if self.target_format not in ['json', 'yaml', 'xml']:
            raise ValueError("Target format must be 'json', 'yaml', or 'xml'")
    
    def migrate_i18next_format(self, source_file: Path, locale: str) -> Dict[str, Any]:
        """
        Migrate from i18next format to LocalEngine format.
        
        Args:
            source_file: Path to the i18next locale file
            locale: Locale identifier (e.g., 'en-US')
            
        Returns:
            Dict containing LocalEngine-formatted data
        """
        print(f"Migrating i18next file: {source_file}")
        
        # Load the source file
        with open(source_file, 'r', encoding='utf-8') as f:
            if source_file.suffix.lower() == '.json':
                data = json.load(f)
            elif source_file.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported source format: {source_file.suffix}")
        
        # Convert to LocalEngine format
        locale_data = {
            "meta": {
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "description": f"Migrated from i18next for {locale}",
                "locale": locale,
                "migrated_from": "i18next"
            }
        }
        
        # Copy translation data (i18next format is already compatible)
        for key, value in data.items():
            if key not in ['meta']:  # Don't override our metadata
                locale_data[key] = value
        
        return locale_data
    
    def migrate_gettext_po(self, po_file: Path, locale: str) -> Dict[str, Any]:
        """
        Migrate from gettext .po format to LocalEngine format.
        
        Args:
            po_file: Path to the .po file
            locale: Locale identifier
            
        Returns:
            Dict containing LocalEngine-formatted data
        """
        print(f"Migrating gettext .po file: {po_file}")
        
        locale_data: Dict[str, Any] = {
            "meta": {
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "description": f"Migrated from gettext for {locale}",
                "locale": locale,
                "migrated_from": "gettext"
            }
        }
        
        # Parse .po file (simplified parser)
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into entries
        entries = content.split('\n\n')
        
        for entry in entries:
            lines = entry.strip().split('\n')
            msgid = None
            msgstr = None
            
            for line in lines:
                if line.startswith('msgid "'):
                    msgid = line[7:-1]  # Remove 'msgid "' and closing '"'
                elif line.startswith('msgstr "'):
                    msgstr = line[8:-1]  # Remove 'msgstr "' and closing '"'
            
            if msgid and msgstr and msgid != '':
                # Convert gettext key format to nested if needed
                if '.' in msgid:
                    # Handle nested keys
                    self._set_nested_value(locale_data, msgid, msgstr)
                else:
                    locale_data[msgid] = msgstr
        
        return locale_data
    
    def migrate_django_format(self, source_file: Path, locale: str) -> Dict[str, Any]:
        """
        Migrate from Django locale format to LocalEngine format.
        
        Args:
            source_file: Path to Django locale file
            locale: Locale identifier
            
        Returns:
            Dict containing LocalEngine-formatted data
        """
        print(f"Migrating Django locale file: {source_file}")
        
        # Django typically uses .po files, so delegate to gettext parser
        if source_file.suffix.lower() == '.po':
            return self.migrate_gettext_po(source_file, locale)
        
        # Handle JSON format if used
        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        locale_data = {
            "meta": {
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "description": f"Migrated from Django for {locale}",
                "locale": locale,
                "migrated_from": "django"
            }
        }
        
        # Copy translation data
        for key, value in data.items():
            if key not in ['meta']:
                locale_data[key] = value
        
        return locale_data
    
    def migrate_react_intl_format(self, source_file: Path, locale: str) -> Dict[str, Any]:
        """
        Migrate from React Intl format to LocalEngine format.
        
        Args:
            source_file: Path to React Intl locale file
            locale: Locale identifier
            
        Returns:
            Dict containing LocalEngine-formatted data
        """
        print(f"Migrating React Intl file: {source_file}")
        
        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        locale_data = {
            "meta": {
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "description": f"Migrated from React Intl for {locale}",
                "locale": locale,
                "migrated_from": "react-intl"
            }
        }
        
        # React Intl often uses flat structure with dot notation
        for key, value in data.items():
            if isinstance(value, dict) and 'message' in value:
                # React Intl format: {"key": {"message": "text", "description": "..."}}
                self._set_nested_value(locale_data, key, value['message'])
            elif isinstance(value, str):
                # Simple format: {"key": "text"}
                self._set_nested_value(locale_data, key, value)
        
        return locale_data
    
    def _set_nested_value(self, data: Dict[str, Any], key: str, value: str) -> None:
        """Set a nested value using dot notation."""
        if '.' not in key:
            data[key] = value
            return
        
        keys = key.split('.')
        current = data
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def save_locale_file(self, data: Dict[str, Any], output_file: Path) -> None:
        """
        Save locale data to file in the specified format.
        
        Args:
            data: Locale data dictionary
            output_file: Output file path
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.target_format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif self.target_format == 'yaml':
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        elif self.target_format == 'xml':
            root = ET.Element('root')
            
            # Add metadata
            if 'meta' in data:
                meta_elem = ET.SubElement(root, 'meta')
                for key, value in data['meta'].items():
                    elem = ET.SubElement(meta_elem, key)
                    elem.text = str(value)
            
            # Add locale data
            locale_elem = ET.SubElement(root, 'locale')
            self._dict_to_xml(data, locale_elem, skip_keys=['meta'])
            
            # Write to file
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
        
        print(f"Saved: {output_file}")
    
    def _dict_to_xml(self, data: Dict[str, Any], parent: ET.Element, skip_keys: Optional[list] = None) -> None:
        """Convert dictionary to XML elements."""
        skip_keys = skip_keys or []
        
        for key, value in data.items():
            if key in skip_keys:
                continue
            
            if isinstance(value, dict):
                elem = ET.SubElement(parent, key)
                self._dict_to_xml(value, elem)
            else:
                elem = ET.SubElement(parent, key)
                elem.text = str(value)


def migrate_directory(source_dir: Path, output_dir: Path, source_format: str, 
                     target_format: str = 'json', locale_mapping: Optional[Dict[str, str]] = None) -> None:
    """
    Migrate an entire directory of locale files.
    
    Args:
        source_dir: Source directory containing locale files
        output_dir: Output directory for migrated files
        source_format: Source format ('i18next', 'gettext', 'django', 'react-intl')
        target_format: Target format ('json', 'yaml', 'xml')
        locale_mapping: Optional mapping of filename to locale identifier
    """
    migrator = LocaleFileMigrator(target_format)
    locale_mapping = locale_mapping or {}
    
    # Create output directory
    locales_dir = output_dir / 'locales'
    locales_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all locale files
    extensions = ['.json', '.yaml', '.yml', '.po']
    locale_files = []
    
    for ext in extensions:
        locale_files.extend(source_dir.glob(f'*{ext}'))
    
    if not locale_files:
        print(f"No locale files found in {source_dir}")
        return
    
    print(f"Found {len(locale_files)} locale files to migrate")
    
    for source_file in locale_files:
        # Determine locale from filename or mapping
        filename_base = source_file.stem
        locale = locale_mapping.get(filename_base, filename_base)
        
        # Ensure locale is in correct format
        if locale and '_' in locale:
            locale = locale.replace('_', '-')
        
        if not locale:
            print(f"Could not determine locale for {source_file}")
            continue
        
        try:
            # Migrate based on source format
            if source_format == 'i18next':
                data = migrator.migrate_i18next_format(source_file, locale)
            elif source_format == 'gettext':
                data = migrator.migrate_gettext_po(source_file, locale)
            elif source_format == 'django':
                data = migrator.migrate_django_format(source_file, locale)
            elif source_format == 'react-intl':
                data = migrator.migrate_react_intl_format(source_file, locale)
            else:
                print(f"Unsupported source format: {source_format}")
                continue
            
            # Save migrated file
            output_file = locales_dir / f"{locale}.{target_format}"
            migrator.save_locale_file(data, output_file)
            
        except Exception as e:
            print(f"Error migrating {source_file}: {e}")


def main():
    """Command-line interface for the migration tool."""
    parser = argparse.ArgumentParser(description='Migrate locale files to LocalEngine format')
    
    parser.add_argument('source', type=Path, help='Source directory or file')
    parser.add_argument('output', type=Path, help='Output directory')
    parser.add_argument('--source-format', choices=['i18next', 'gettext', 'django', 'react-intl'],
                       required=True, help='Source locale format')
    parser.add_argument('--target-format', choices=['json', 'yaml', 'xml'], 
                       default='json', help='Target format (default: json)')
    parser.add_argument('--locale', help='Locale identifier (for single file migration)')
    
    args = parser.parse_args()
    
    if args.source.is_file():
        # Single file migration
        if not args.locale:
            # Try to infer from filename
            args.locale = args.source.stem.replace('_', '-')
        
        migrator = LocaleFileMigrator(args.target_format)
        
        try:
            # Migrate based on source format
            data = None
            if args.source_format == 'i18next':
                data = migrator.migrate_i18next_format(args.source, args.locale)
            elif args.source_format == 'gettext':
                data = migrator.migrate_gettext_po(args.source, args.locale)
            elif args.source_format == 'django':
                data = migrator.migrate_django_format(args.source, args.locale)
            elif args.source_format == 'react-intl':
                data = migrator.migrate_react_intl_format(args.source, args.locale)
            
            if data:
                output_file = args.output / f"{args.locale}.{args.target_format}"
                migrator.save_locale_file(data, output_file)
                print("Single file migration completed!")
            else:
                print(f"Unsupported source format: {args.source_format}")
            
        except Exception as e:
            print(f"Migration failed: {e}")
    
    elif args.source.is_dir():
        # Directory migration
        migrate_directory(args.source, args.output, args.source_format, args.target_format)
        print("Directory migration completed!")
    
    else:
        print(f"Source path does not exist: {args.source}")


if __name__ == "__main__":
    main()
