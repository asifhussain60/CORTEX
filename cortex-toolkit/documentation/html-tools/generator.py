#!/usr/bin/env python3
"""
CORTEX Native HTML Generator
Pure Python HTML generation (zero dependencies)

Features:
- Type-safe HTML element creation
- Automatic attribute escaping
- Context managers for nesting
- Template generation

Author: Asif Hussain
Date: December 27, 2025
"""

from typing import Dict, List, Optional, Union
from html import escape
from pathlib import Path


class HTMLElement:
    """Represents an HTML element"""
    
    def __init__(
        self,
        tag: str,
        content: Union[str, List['HTMLElement'], None] = None,
        attrs: Optional[Dict[str, str]] = None,
        void: bool = False
    ):
        self.tag = tag
        self.content = content if content is not None else []
        self.attrs = attrs or {}
        self.void = void
    
    def add_child(self, element: 'HTMLElement'):
        """Add a child element"""
        if isinstance(self.content, str):
            raise ValueError("Cannot add child to element with text content")
        if isinstance(self.content, list):
            self.content.append(element)
    
    def add_text(self, text: str):
        """Add text content"""
        if isinstance(self.content, list) and self.content:
            raise ValueError("Cannot add text to element with children")
        self.content = text
    
    def set_attr(self, name: str, value: str):
        """Set an attribute"""
        self.attrs[name] = value
    
    def render(self, indent: int = 0, indent_size: int = 2) -> str:
        """Render element to HTML string"""
        spacing = " " * (indent * indent_size)
        
        # Build opening tag
        tag_parts = [f"<{self.tag}"]
        
        # Add attributes
        for name, value in sorted(self.attrs.items()):
            if value is None:
                tag_parts.append(f" {name}")
            else:
                escaped_value = escape(str(value), quote=True)
                tag_parts.append(f' {name}="{escaped_value}"')
        
        # Void elements
        if self.void:
            tag_parts.append(" />")
            return spacing + "".join(tag_parts)
        
        tag_parts.append(">")
        
        # No content
        if not self.content:
            return spacing + "".join(tag_parts) + f"</{self.tag}>"
        
        # Text content
        if isinstance(self.content, str):
            escaped_content = escape(self.content)
            return spacing + "".join(tag_parts) + escaped_content + f"</{self.tag}>"
        
        # Child elements
        lines = [spacing + "".join(tag_parts)]
        for child in self.content:
            lines.append(child.render(indent + 1, indent_size))
        lines.append(spacing + f"</{self.tag}>")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return self.render()


class HTMLGenerator:
    """HTML document generator with fluent API"""
    
    def __init__(self, title: str = "Document", lang: str = "en"):
        self.lang = lang
        self.title_text = title
        self.head_elements: List[HTMLElement] = []
        self.body_elements: List[HTMLElement] = []
        self.charset = "UTF-8"
    
    def add_meta(self, name: str, content: str) -> 'HTMLGenerator':
        """Add meta tag to head"""
        meta = HTMLElement('meta', attrs={'name': name, 'content': content}, void=True)
        self.head_elements.append(meta)
        return self
    
    def add_stylesheet(self, href: str) -> 'HTMLGenerator':
        """Add stylesheet link"""
        link = HTMLElement(
            'link',
            attrs={'rel': 'stylesheet', 'href': href},
            void=True
        )
        self.head_elements.append(link)
        return self
    
    def add_script(self, src: str, defer: bool = False) -> 'HTMLGenerator':
        """Add script tag"""
        attrs = {'src': src}
        if defer:
            attrs['defer'] = None
        script = HTMLElement('script', attrs=attrs)
        self.head_elements.append(script)
        return self
    
    def add_to_body(self, element: HTMLElement) -> 'HTMLGenerator':
        """Add element to body"""
        self.body_elements.append(element)
        return self
    
    def render(self) -> str:
        """Render complete HTML document"""
        lines = ['<!DOCTYPE html>']
        
        # HTML element
        html = HTMLElement('html', attrs={'lang': self.lang})
        
        # Head
        head = HTMLElement('head')
        
        # Charset
        charset_meta = HTMLElement(
            'meta',
            attrs={'charset': self.charset},
            void=True
        )
        head.add_child(charset_meta)
        
        # Viewport
        viewport_meta = HTMLElement(
            'meta',
            attrs={
                'name': 'viewport',
                'content': 'width=device-width, initial-scale=1.0'
            },
            void=True
        )
        head.add_child(viewport_meta)
        
        # Title
        title = HTMLElement('title')
        title.add_text(self.title_text)
        head.add_child(title)
        
        # Additional head elements
        for element in self.head_elements:
            head.add_child(element)
        
        html.add_child(head)
        
        # Body
        body = HTMLElement('body')
        for element in self.body_elements:
            body.add_child(element)
        
        html.add_child(body)
        
        lines.append(html.render())
        
        return "\n".join(lines)
    
    def save(self, file_path: Path):
        """Save document to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.render())


# Convenience functions for common elements

def div(content=None, class_name: Optional[str] = None, **attrs) -> HTMLElement:
    """Create a div element"""
    if class_name:
        attrs['class'] = class_name
    return HTMLElement('div', content, attrs)


def p(text: str, class_name: Optional[str] = None, **attrs) -> HTMLElement:
    """Create a paragraph"""
    if class_name:
        attrs['class'] = class_name
    elem = HTMLElement('p', attrs=attrs)
    elem.add_text(text)
    return elem


def h1(text: str, **attrs) -> HTMLElement:
    """Create h1 heading"""
    elem = HTMLElement('h1', attrs=attrs)
    elem.add_text(text)
    return elem


def h2(text: str, **attrs) -> HTMLElement:
    """Create h2 heading"""
    elem = HTMLElement('h2', attrs=attrs)
    elem.add_text(text)
    return elem


def h3(text: str, **attrs) -> HTMLElement:
    """Create h3 heading"""
    elem = HTMLElement('h3', attrs=attrs)
    elem.add_text(text)
    return elem


def a(text: str, href: str, **attrs) -> HTMLElement:
    """Create a link"""
    attrs['href'] = href
    elem = HTMLElement('a', attrs=attrs)
    elem.add_text(text)
    return elem


def img(src: str, alt: str, **attrs) -> HTMLElement:
    """Create an image"""
    attrs.update({'src': src, 'alt': alt})
    return HTMLElement('img', attrs=attrs, void=True)


def ul(items: List[str], class_name: Optional[str] = None) -> HTMLElement:
    """Create unordered list"""
    attrs = {'class': class_name} if class_name else {}
    ul_elem = HTMLElement('ul', attrs=attrs)
    for item in items:
        li = HTMLElement('li')
        li.add_text(item)
        ul_elem.add_child(li)
    return ul_elem


def create_html_document(
    title: str,
    body_content: List[HTMLElement],
    stylesheets: Optional[List[str]] = None,
    scripts: Optional[List[str]] = None
) -> str:
    """
    Quick helper to create a complete HTML document
    
    Args:
        title: Document title
        body_content: List of HTML elements for body
        stylesheets: List of CSS file paths
        scripts: List of JS file paths
    
    Returns:
        Complete HTML document string
    """
    generator = HTMLGenerator(title=title)
    
    # Add stylesheets
    if stylesheets:
        for stylesheet in stylesheets:
            generator.add_stylesheet(stylesheet)
    
    # Add scripts
    if scripts:
        for script in scripts:
            generator.add_script(script, defer=True)
    
    # Add body content
    for element in body_content:
        generator.add_to_body(element)
    
    return generator.render()


if __name__ == "__main__":
    # Example usage
    print("Creating example HTML document...\n")
    
    # Method 1: Using HTMLGenerator
    doc = HTMLGenerator(title="CORTEX Example")
    doc.add_stylesheet("assets/css/main.css")
    doc.add_meta("description", "Example HTML document")
    
    # Build content
    header = div(class_name="header")
    header.add_child(h1("Welcome to CORTEX"))
    header.add_child(p("This is a dynamically generated HTML document."))
    
    doc.add_to_body(header)
    
    # Method 2: Using helper functions
    content = [
        h1("CORTEX HTML Generator"),
        p("Pure Python HTML generation with zero dependencies.", class_name="lead"),
        h2("Features"),
        ul([
            "Type-safe element creation",
            "Automatic HTML escaping",
            "Clean, readable API",
            "No external dependencies"
        ]),
        a("Visit GitHub", href="https://github.com/asifhussain60/CORTEX")
    ]
    
    html = create_html_document(
        title="CORTEX Demo",
        body_content=content,
        stylesheets=["main.css"]
    )
    
    print(html)
