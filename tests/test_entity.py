"""エンティティ処理のテストモジュール

以下のエンティティ機能をテストします：
1. 基本データ抽出
2. 属性処理
3. 親子関係の管理
4. 複数階層の参照
"""

import pytest
from xml2xlsx.entity import Entity, EntityContext
import xml.etree.ElementTree as ET


def test_entity_basic_data():
    """エンティティの基本データ抽出機能をテスト"""
    xml = """
        <item>
            <id>001</id>
            <name>Test Item</name>
            <price>1000</price>
            <description>Test Description</description>
        </item>
    """
    element = ET.fromstring(xml)
    entity = Entity(element)

    # 基本データの確認
    data = entity.data
    assert data["id"] == "001"
    assert data["name"] == "Test Item"
    assert data["price"] == "1000"
    assert data["description"] == "Test Description"


def test_entity_with_attributes():
    """エンティティの属性処理機能をテスト"""
    xml = """
        <item code="ABC123" status="active" type="product">
            <id>001</id>
            <name>Test Item</name>
        </item>
    """
    element = ET.fromstring(xml)
    entity = Entity(element)

    # 属性データの確認
    data = entity.data
    assert data["@code"] == "ABC123"
    assert data["@status"] == "active"
    assert data["@type"] == "product"
    assert data["id"] == "001"
    assert data["name"] == "Test Item"


def test_entity_id_handling():
    """エンティティのID処理機能をテスト"""
    xml = """
        <item>
            <id>001</id>
            <name>Test Item</name>
        </item>
    """
    element = ET.fromstring(xml)
    entity = Entity(element)

    # IDの取得確認
    assert entity.id == "001"
    assert entity.data["id"] == "001"


def test_parent_reference():
    """親エンティティ参照の基本機能をテスト"""
    xml = """
        <root>
            <company>
                <id>C001</id>
                <name>Test Company</name>
                <department>
                    <id>D001</id>
                    <name>Test Department</name>
                </department>
            </company>
        </root>
    """
    root = ET.fromstring(xml)
    context = EntityContext(root)

    # 親子関係の確認
    assert "department" in context.entities
    department = context.entities["department"][0]
    assert department.data["company.id"] == "C001"


def test_multiple_parent_references():
    """複数階層の親参照機能をテスト"""
    xml = """
        <root>
            <company>
                <id>C001</id>
                <department>
                    <id>D001</id>
                    <project>
                        <id>P001</id>
                        <task>
                            <id>T001</id>
                        </task>
                    </project>
                </department>
            </company>
        </root>
    """
    root = ET.fromstring(xml)
    context = EntityContext(root)

    # 多階層の参照確認
    task = context.entities["task"][0]
    assert task.data["company.id"] == "C001"
    assert task.data["department.id"] == "D001"
    assert task.data["project.id"] == "P001"


def test_entity_without_id():
    """ID要素のないエンティティの処理をテスト"""
    xml = """
        <item>
            <name>Test Item</name>
            <description>Test Description</description>
        </item>
    """
    element = ET.fromstring(xml)
    entity = Entity(element)

    # IDなしデータの確認
    assert entity.id is None
    assert "id" not in entity.data
    assert entity.data["name"] == "Test Item"
    assert entity.data["description"] == "Test Description"


def test_entity_with_empty_elements():
    """空要素を含むエンティティの処理をテスト"""
    xml = """
        <item>
            <id>001</id>
            <name></name>
            <description/>
            <price>1000</price>
        </item>
    """
    element = ET.fromstring(xml)
    entity = Entity(element)

    # 空要素の処理確認
    data = entity.data
    assert data["id"] == "001"
    assert data.get("name", "") == ""
    assert "description" not in data
    assert data["price"] == "1000"


def test_sibling_entities():
    """兄弟エンティティの参照関係をテスト"""
    xml = """
        <root>
            <company>
                <id>C001</id>
                <departments>
                    <department>
                        <id>D001</id>
                        <name>Department 1</name>
                    </department>
                    <department>
                        <id>D002</id>
                        <name>Department 2</name>
                    </department>
                </departments>
            </company>
        </root>
    """
    root = ET.fromstring(xml)
    context = EntityContext(root)

    # 兄弟要素の参照確認
    departments = context.entities["department"]
    assert len(departments) == 2
    assert all(dept.data["company.id"] == "C001" for dept in departments)
    assert departments[0].data["id"] == "D001"
    assert departments[1].data["id"] == "D002"
