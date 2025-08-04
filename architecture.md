# LocalEngine Architecture Document
This document outlines the core components of any LocalEngine implementation, ensuring a consistent design between different languages, platforms, and third party libraries. For those that are using a LocalEngine implementation, please refer to the [User Guide](USER.md) for instructions on how to use the engine in your application.

## Architecture Info
- Version: 1.0.0
- Last Updated: 2025-08-03

## Why this specification?
We plan to endorse and advertise other libraries that follow along with this specification, including those that are not written in officially supported languages. This will allow for a consistent experience across different platforms and languages, making it easier for developers to implement localization in their applications.

In order to ensure that all implementations are consistent, we have defined a set of core components that must be present in any LocalEngine implementation in order for them to be endorsed and permitted to use the LocalEngine name. This document serves as a guide for developers to follow when creating their own implementations, ensuring that they meet the requirements for endorsement.

## Quick Definitions
- **Locale**: A specific language and region combination, such as `en-US` for English (United States) or `fr-FR` for French (France).
- **Locale File**: A file containing translations for a specific locale, typically in a structured format like JSON, XML, or YAML.
- **Core Feature**: Any feature that is provided in this official implementation shall be considered a core feature

## Core Components (Must Haves)
- **Locale Auto-Detection**: The engine should automatically detect the user's locale based on their system settings or browser preferences.
- **Locale File Management**: The engine should be able to load, parse, and manage locale files in various formats (e.g., JSON, XML, YAML).
- **Translation Retrieval**: The engine should provide a method to retrieve translations for a given key in the user's locale.
- **Fallback Mechanism**: The engine should have a fallback mechanism to use a default locale if the requested locale is not available, based from a local file bundled with the application.
- **Dynamic Locale Switching**: The engine should allow for dynamic switching of locales at runtime without requiring a page reload or application restart.
- **Offline Support**: The engine should be able to function offline, using cached locale files when the user is not connected to the internet, meaning that once locales are retrieved, they should be stored for future use and only periodically refreshed when the user is online in case of edits.
- **Common Base API**: The engine should provide a common API for accessing translations, regardless of the underlying implementation or language. Meaning that any implementation should be a *drop-in replacement* for any other implementation, allowing for easy swapping of libraries without changing the code that uses the engine even if the new library provides more features. We reccommend implementing part of this packages code into any third party library to ensure that the API is consistent across all implementations, however this is not a requirement as long as the core workings are consistent.


## Source Code Requirements
- **Open Source**: The source code of the implementation must be open source and available for public use, allowing others to contribute and improve the implementation.
- **Documentation**: The implementation must include comprehensive documentation, including setup instructions, API references, and examples of usage.
- **Tests**: The implementation must include unit tests to ensure the correctness of the code and to facilitate future development and maintenance.
- **Versioning**: The implementation must follow semantic versioning to ensure compatibility and ease of updates.
- **License**: The implementation is preferred to be released under a permissive open source license, such as MIT, Apache 2.0, or The GNU Lesser General Public License (LGPL) to allow for wide adoption and use.
- **USER.md**: A specific documentation requirement, simply copy the [User Guide](USER.md) into your implementation repository, and ensure that it is up to date with the latest compliant version of the engine. This will ensure that users have access to the same basic information about how to use the engine, regardless of the implementation they are using. For adding your own user guide, link to that file at the top of the provided USER.md, and vice versa (e.g) `See the [LocalEngine Basic User Guide](USER.md) for information about versioning, file layout, and locale file hosting via GitHub.`, this will ensure that users can easily find the documentation for your implementation as well as documentation for setting up the core features of the engine. We like this approach as it also allows third party library authors to not have to worry about documenting the same things that we have already documented, and allows them to focus on the specific features of their library that are not covered by the core engine (if any).
- **Exceptions to the above**: If the implementation is not open source, and/or does not meet licensing requirements, it must be approved by the LocalEngine team before being endorsed. This is to ensure that the implementation meets the quality and consistency standards set by the LocalEngine project, to do this you will be required to give us access to the source code to your LocalEngine implementation. For security reasons, you may request a PGP key to be created specifically for your project to allow seamless and secure transfers of source code. Submitted code will only be used to verify that the implementation meets the requirements set forth in this document, and will not be used for any other purpose or shared with any third parties without your permission.

## Locale File Format
Specific file formats must be supported for locale files to ensure compatibility across different implementations. The following formats are required:
- **JSON**: A widely used format that is easy to read and write, and is supported by most programming languages.
- **XML**: A markup language that is also widely used, providing a structured way to represent data.
- **YAML**: A human-readable data serialization format that is often used for configuration files and data exchange between languages with different data structures.

### Locale File Structure
Locale files should follow a consistent structure to ensure that translations can be easily retrieved. The recommended structure is as follows:
```json FILENAME = "en-US.json"
{
    "meta": {
        "version": "1.0.0",
        "last_updated": "2023-10-01",
        "description": "Locale file for English (United States)",
        "locale": "en-US"
    },
    
    "field_ID":"Field Content",
    "greeting": "Hello",
    "farewell": "Goodbye",
    "optional_category_section": {
        "about":"An optional way to organize a file into sections, this is not required but is recommended for larger files. This does not need to be automatically detected, but should be supported by the engine."
    }
}
```

This structure allows for easy retrieval of translations using the field ID as the key. The engine should be able to handle nested structures and arrays if needed, but the above format is the minimum requirement.

```yaml FILENAME = "en-US.yaml"
meta:
    version: "1.0.0"
    last_updated: "2023-10-01"
    description: "Locale file for English (United States)"
    locale: "en-US"
field_ID: Field Content
greeting: Hello
farewell: Goodbye
optional_category_section:
  about: An optional way to organize a file into sections, this is not required but is recommended for larger files. This does not need to be automatically detected, but should be supported by the engine.
```
```xml FILENAME = "en-US.xml"
<meta>
    <version>1.0.0</version>
    <last_updated>2023-10-01</last_updated>
    <description>Locale file for English (United States)</description>
    <locale>en-US</locale>
</meta>
<locale>
    <field_ID>Field Content</field_ID>
    <greeting>Hello</greeting>
    <farewell>Goodbye</farewell>
    <optional_category_section>
        <about>An optional way to organize a file into sections, this is not required but is recommended for larger files. This does not need to be automatically detected, but should be supported by the engine.</about>
    </optional_category_section>
</locale>
```
The benefit of using XML is that it allows for a metadata section to be included in the file that is separate from the translations, which can be useful for providing additional information about the locale file, such as the version and last updated date. Having it separate from the translations allows for easier parsing and retrieval of translations without having to worry about metadata and vice versa.

### More About Metadata
The metadata section is optional but recommended for all locale files. It MUST support the following fields:
- **version**: The version of the locale file, following semantic versioning.
- **last_updated**: The date when the locale file was last updated, in ISO 8601 format (YYYY-MM-DD).
- **description**: A brief description of the locale file, including the language and region it represents.
- **locale**: The locale identifier, such as `en-US` for English (United States) or `fr-FR` for French (France).

This metadata can be used by the engine to display information about the locale file, such as the version and last updated date, and to ensure that the correct locale file is being used.

## Loading Locale Files
Locale files should be loaded from a specified directory or URL, depending on the implementation. The engine should provide a method to load locale files at runtime, allowing for dynamic updates to the translations without requiring a restart of the application. The loading process should handle errors gracefully, such as missing files or invalid formats, and provide fallback translations if the requested locale file is not available.

Implementations should require that locale files are stored in one of two ways:
1. **locales/filename.json**: A locale file stored in a locales directory either remotely or on the device, the engine should be able to load this file from the specified path and parse it according to the format specified in the file.
2. **locales/localename/filename.json**: A locale file stored in a subdirectory of the locales directory, where the subdirectory is named after the locale (e.g., `en-US` for English (United States)). This allows for multiple locale files to be stored in the same directory without conflicts.

Loading from method 1 is required, while method 2 is optional but not considered a core feature. Implementations may choose to support both methods, but at a minimum, method 1 must be supported.

## Load with the text.
The engine should provide a method to load localized text as the text appears on the screen. The core implementation is to provide a method that takes a key and returns the localized text for the current locale. This method should handle the following:
- **Key Retrieval**: The method should retrieve the localized text for the given key from the loaded locale file.
- **Fallback Handling**: If the key is not found in the current locale file, the method should check for the key in the fallback locale file (if available) and return the corresponding text. If the key is not found in either locale file, the method should return a default value, such as an empty string or a placeholder text.

## Efficient Updating
The engine should support efficient updating of locale files without requiring a full reload of the application. This can be achieved through the following mechanisms:
- **Hot Reloading**: The engine should allow for hot reloading of locale files, meaning that changes to the locale files can be detected and applied at runtime without requiring a restart of the application. This can be done by periodically checking for changes to the locale files or by using file watchers to detect changes in real-time. The minimum requirement is to check for changes every 5 minutes, but implementations may choose to check more frequently if desired.
- **Translation Caching**: The engine should cache translations to improve performance and reduce the need for repeated file reads. This can be done by storing the loaded translations in memory and only reloading them when a change is detected or when the application is restarted. The cache should be cleared when the locale is changed, when the application is restarted, or when on user request. (e.g. a function to clear the cache is called when the user goes to the next level on a text adventure game, or when the user switches menus in a GUI application).

## Conclusion
This architecture document outlines the core components and requirements for any LocalEngine implementation. By adhering to these guidelines, developers can create consistent and reliable localization engines that provide a seamless experience for users across different platforms and languages. The goal is to ensure that all implementations meet the same standards for functionality, performance, and usability, allowing for easy integration and use in a wide range of applications.
By following this specification, developers can contribute to the LocalEngine ecosystem and help create a unified localization experience for users worldwide. We encourage developers to share their implementations and contribute to the ongoing development of the LocalEngine project, ensuring that it remains a valuable resource for the community.
We look forward to seeing the diverse range of implementations that will emerge from this specification, and we hope that it will lead to a more consistent and user-friendly localization experience across different applications and platforms.
If you have any questions or suggestions regarding this architecture document, please feel free to reach out to the LocalEngine team. We are always open to feedback and collaboration to improve the specification and the overall LocalEngine project.

## Also see
- [User Guide](USER.md): For instructions on how to use the engine in your application.
- [API Reference](API.md): For detailed information about the API provided by this specific LocalEngine implementation.
- [Email us](mailto:code@envopen.org): For any questions or suggestions regarding this architecture document or the LocalEngine project in general.
- [The LGPL](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html): For information about the GNU Lesser General Public License (LGPL) under which this project is licensed.
- [The LGPL but in the repo](LICENSE.md): For the full text of the GNU Lesser General Public License (LGPL) under which this project is licensed.

## Acknowledgements
We would like to thank Argo Nickerson for their contributions to the LocalEngine project, including the initial implementation and the development of this architecture document. Their work has been instrumental in shaping the direction of the project and ensuring that it meets the needs of developers and users alike.
We also appreciate the contributions of the wider LocalEngine community, whose feedback and suggestions have helped to refine and improve the specification. The collaborative efforts of developers from various backgrounds and platforms have enriched the LocalEngine project and made it a valuable resource for localization in software development.
We look forward to continuing to work with the community to enhance the LocalEngine project and to support the development of high-quality localization engines that adhere to this specification. Together, we can create a more consistent and user-friendly localization experience for users worldwide.
We encourage developers to share their implementations, contribute to the ongoing development of the LocalEngine project, and help us build a unified localization experience across different applications and platforms. Your contributions are invaluable to the success of the LocalEngine project, and we look forward to collaborating with you to make localization easier and more accessible for everyone.
We also acknowledge the contributions of the open source community, whose libraries and tools have inspired and informed the design of the LocalEngine architecture. By building on existing technologies and best practices, we aim to create a robust and flexible localization engine that meets the needs of developers across different languages and platforms.
We hope that this architecture document serves as a useful guide for developers looking to implement their own LocalEngine solutions, and we encourage you to reach out with any questions, suggestions, or feedback. Together, we can continue to improve the LocalEngine project and create a better localization experience for users around the world.  

<sup><sub>Copyright © 2025, [Env Open](https://envopen.org) | Licensed under the GNU Lesser General Public License (LGPL) v2.1. | Version 1.0.0</sub></sup>