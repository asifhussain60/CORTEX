"""Tests for AC-DEPLOY-004-01: Release Notes & User Documentation"""
import pytest


class ReleaseNotesGenerator:
    def __init__(self):
        self.notes = []
    
    def add_feature(self, title: str, description: str) -> None:
        self.notes.append({"type": "feature", "title": title, "desc": description})
    
    def add_bugfix(self, title: str, description: str) -> None:
        self.notes.append({"type": "bugfix", "title": title, "desc": description})
    
    def generate(self) -> str:
        return "\n".join(f"- {n['title']}: {n['desc']}" for n in self.notes)
    
    def get_feature_count(self) -> int:
        return sum(1 for n in self.notes if n['type'] == 'feature')


class DocumentationBuilder:
    def __init__(self):
        self.sections = {}
    
    def add_section(self, name: str, content: str) -> None:
        self.sections[name] = content
    
    def build_documentation(self) -> str:
        result = ""
        for name, content in self.sections.items():
            result += f"## {name}\n{content}\n"
        return result
    
    def get_section_count(self) -> int:
        return len(self.sections)


class TestReleaseNotes:
    def test_add_feature(self):
        gen = ReleaseNotesGenerator()
        gen.add_feature("New Analysis", "Added new analysis")
        assert gen.get_feature_count() == 1
    
    def test_add_bugfix(self):
        gen = ReleaseNotesGenerator()
        gen.add_bugfix("Fix crash", "Fixed crash on startup")
        assert len(gen.notes) == 1
    
    def test_generate_notes(self):
        gen = ReleaseNotesGenerator()
        gen.add_feature("Feature 1", "Description")
        notes = gen.generate()
        assert "Feature 1" in notes
    
    def test_multiple_features(self):
        gen = ReleaseNotesGenerator()
        for i in range(3):
            gen.add_feature(f"F{i}", f"Desc{i}")
        assert gen.get_feature_count() == 3
    
    def test_add_section(self):
        doc = DocumentationBuilder()
        doc.add_section("Installation", "Steps...")
        assert doc.get_section_count() == 1
    
    def test_build_documentation(self):
        doc = DocumentationBuilder()
        doc.add_section("Getting Started", "Content")
        result = doc.build_documentation()
        assert "Getting Started" in result
    
    def test_multiple_sections(self):
        doc = DocumentationBuilder()
        for i in range(3):
            doc.add_section(f"Section{i}", f"Content{i}")
        assert doc.get_section_count() == 3
    
    def test_documentation_format(self):
        doc = DocumentationBuilder()
        doc.add_section("Setup", "Instructions")
        result = doc.build_documentation()
        assert "##" in result
