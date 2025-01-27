"""コレクション要素の検出テスト

以下の機能をテストします：
1. 基本的なコレクション検出
2. 階層構造の処理
3. エッジケースの処理
"""

import pytest
from xml2xlsx.converter import XmlToExcelConverter
from xml2xlsx.entity import EntityContext
import xml.etree.ElementTree as ET


@pytest.fixture
def context():
    """EntityContextのフィクスチャ"""
    xml = "<root></root>"
    root = ET.fromstring(xml)
    return EntityContext(root)


def test_simple_collection(context: EntityContext):
    """基本的な複数形タグの検出をテスト。"""
    xml = """<items>
        <item id="1">
            <name>Test 1</name>
        </item>
        <item id="2">
            <name>Test 2</name>
        </item>
    </items>"""

    element = ET.fromstring(xml)
    is_collection, child_tag = context.is_collection_element(element)
    assert is_collection
    assert child_tag == "item"


def test_mixed_content_not_collection(context: EntityContext):
    """異なるタグが混在する場合はコレクションとみなさないことをテスト。"""
    xml = """<data>
        <item id="1">
            <name>Test 1</name>
        </item>
        <summary>
            <total>2</total>
        </summary>
    </data>"""

    element = ET.fromstring(xml)
    is_collection, child_tag = context.is_collection_element(element)
    assert not is_collection
    assert child_tag is None


def test_empty_elements_not_collection(context: EntityContext):
    """空の要素を含む場合はコレクションとみなさないことをテスト。"""
    xml = """<items>
        <item/>
        <item/>
    </items>"""

    element = ET.fromstring(xml)
    is_collection, child_tag = context.is_collection_element(element)
    assert not is_collection
    assert child_tag is None


def test_deep_hierarchy_collection(context: EntityContext):
    """深い階層でのコレクション検出をテスト。"""
    xml = """<root>
        <departments>
            <department id="1">
                <projects>
                    <project id="1">
                        <tasks>
                            <task id="1">
                                <name>Test Task</name>
                            </task>
                        </tasks>
                    </project>
                </projects>
            </department>
        </departments>
    </root>"""

    element = ET.fromstring(xml)

    # departments要素の検証
    departments = element.find("departments")
    assert departments is not None
    is_collection, child_tag = context.is_collection_element(departments)
    assert is_collection
    assert child_tag == "department"

    # projects要素の検証
    projects = element.find(".//projects")
    assert projects is not None
    is_collection, child_tag = context.is_collection_element(projects)
    assert is_collection
    assert child_tag == "project"

    # tasks要素の検証
    tasks = element.find(".//tasks")
    assert tasks is not None
    is_collection, child_tag = context.is_collection_element(tasks)
    assert is_collection
    assert child_tag == "task"


def test_attributes_make_entity(context: EntityContext):
    """属性を持つ要素がエンティティとして処理されることをテスト。"""
    xml = """<items>
        <item id="1" status="active"/>
    </items>"""

    element = ET.fromstring(xml)
    item = element.find(".//item")
    assert item is not None
    assert item.get("id") == "1"
    assert item.get("status") == "active"
    assert context._should_process_as_entity(item)


def test_nested_elements_make_entity(context: EntityContext):
    """ネストされた要素がエンティティとして処理されることをテスト。"""
    xml = """<items>
        <item>
            <details>
                <value>123</value>
            </details>
        </item>
    </items>"""

    element = ET.fromstring(xml)
    item = element.find(".//item")
    assert item is not None
    assert context._should_process_as_entity(item)


def test_text_content_makes_entity(context: EntityContext):
    """テキストコンテンツを持つ要素がエンティティとして処理されることをテスト。"""
    xml = """<items>
        <item>
            <name>Test Item</name>
        </item>
    </items>"""

    element = ET.fromstring(xml)
    item = element.find(".//item")
    assert item is not None
    assert context._should_process_as_entity(item)
