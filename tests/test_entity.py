"""エンティティのテスト"""

from textwrap import dedent
import pytest
import xml.etree.ElementTree as ET
from xml2xlsx.entity import EntityContext


def test_entity_basic_data():
    """基本的なエンティティデータの処理をテスト"""
    xml = dedent(
        """
        <root>
            <item>
                <id>1</id>
                <name>Test</name>
            </item>
        </root>
    """
    )
    context = EntityContext()
    entity = context.process_xml_element(ET.fromstring(xml))

    item = context.process_xml_element(entity.element.find("item"), "root", entity)
    assert item is not None
    assert "id" in item.get_columns()
    assert "name" in item.get_columns()
    assert item.get_value("id") == "1"
    assert item.get_value("name") == "Test"


def test_entity_with_attributes():
    """属性を持つエンティティの処理をテスト"""
    xml = dedent(
        """
        <root>
            <item id="1" type="test">
                <name>Test</name>
            </item>
        </root>
    """
    )
    context = EntityContext()
    entity = context.process_xml_element(ET.fromstring(xml))

    item = context.process_xml_element(entity.element.find("item"), "root", entity)
    assert item is not None
    assert "@id" in item.get_columns()
    assert "@type" in item.get_columns()
    assert "name" in item.get_columns()
    assert item.get_value("@id") == "1"
    assert item.get_value("@type") == "test"
    assert item.get_value("name") == "Test"


def test_entity_without_id():
    """IDを持たないエンティティの処理をテスト"""
    xml = dedent(
        """
        <root>
            <item>
                <name>Test</name>
                <description>Test Description</description>
            </item>
        </root>
    """
    )
    context = EntityContext()
    entity = context.process_xml_element(ET.fromstring(xml))

    item = context.process_xml_element(entity.element.find("item"), "root", entity)
    assert item is not None
    assert "name" in item.get_columns()
    assert "description" in item.get_columns()
    assert item.get_value("name") == "Test"
    assert item.get_value("description") == "Test Description"


def test_parent_reference():
    """親要素への参照をテスト"""
    xml = dedent(
        """
        <root>
            <organization name="Org1">
                <department name="Dev1">
                    <employee name="Emp1"/>
                </department>
            </organization>
        </root>
    """
    )
    context = EntityContext()
    root = context.process_xml_element(ET.fromstring(xml))
    org = context.process_xml_element(root.element.find("organization"), "root", root)
    dept = context.process_xml_element(org.element.find("department"), "root.organization", org)
    emp = context.process_xml_element(dept.element.find("employee"), "root.organization.department", dept)

    # 親要素の属性を参照
    assert emp.parent is not None
    assert emp.parent.get_value("@name") == "Dev1"  # 直接の親の属性
    assert emp.parent.parent is not None
    assert emp.parent.parent.get_value("@name") == "Org1"  # 親の親の属性


def test_multiple_parent_references():
    """複数の親要素への参照をテスト"""
    xml = dedent(
        """
        <root>
            <organization name="Org1">
                <department name="Dev1">
                    <project name="Proj1">
                        <task>Task1</task>
                    </project>
                </department>
            </organization>
        </root>
    """
    )
    context = EntityContext()
    root = context.process_xml_element(ET.fromstring(xml))
    org = context.process_xml_element(root.element.find("organization"), "root", root)
    dept = context.process_xml_element(org.element.find("department"), "root.organization", org)
    proj = context.process_xml_element(dept.element.find("project"), "root.organization.department", dept)
    task = context.process_xml_element(proj.element.find("task"), "root.organization.department.project", proj)

    # 親の親の親まで辿って属性を参照
    assert task.parent is not None
    assert task.parent.get_value("@name") == "Proj1"  # 直接の親
    assert task.parent.parent is not None
    assert task.parent.parent.parent is not None
    assert task.parent.parent.parent.get_value("@name") == "Org1"  # 親の親の親


@pytest.fixture
def context():
    """テスト用のコンテキスト"""
    return EntityContext()


def test_simple_collection(context: EntityContext):
    """基本的な複数形タグの検出をテスト"""
    xml = dedent(
        """
        <items>
            <item id="1">
                <name>Test 1</name>
            </item>
            <item id="2">
                <name>Test 2</name>
            </item>
        </items>
    """
    )
    element = ET.fromstring(xml)
    is_collection, child_tag = context.is_collection_element(element)
    assert is_collection
    assert child_tag == "item"


def test_mixed_content_not_collection(context: EntityContext):
    """異なる要素を含む場合はコレクションとみなさないことをテスト"""
    xml = dedent(
        """
        <data>
            <header>Header</header>
            <item>Item 1</item>
            <footer>Footer</footer>
        </data>
    """
    )
    element = ET.fromstring(xml)
    is_collection, child_tag = context.is_collection_element(element)
    assert not is_collection
    assert child_tag is None


def test_empty_elements_not_collection(context: EntityContext):
    """空の要素を含む場合はコレクションとみなさないことをテスト"""
    xml = dedent(
        """
        <items>
            <item/>
            <item/>
        </items>
    """
    )
    element = ET.fromstring(xml)
    is_collection, child_tag = context.is_collection_element(element)
    assert not is_collection
    assert child_tag is None


def test_hierarchical_entity_conversion():
    """階層構造を持つエンティティの変換をテスト"""
    xml = dedent(
        """
        <organization>
            <employees>
                <employee>
                    <id>E001</id>
                    <name>従業員1</name>
                    <department>開発部</department>
                </employee>
                <employee>
                    <id>E002</id>
                    <name>従業員2</name>
                    <department>営業部</department>
                </employee>
            </employees>
        </organization>
    """
    )
    context = EntityContext()
    org = context.process_xml_element(ET.fromstring(xml))
    emps = context.process_xml_element(org.element.find("employees"), "organization", org)
    emp = context.process_xml_element(emps.element.find("employee"), "organization.employees", emps)

    assert emp is not None
    assert "id" in emp.get_columns()
    assert "name" in emp.get_columns()
    assert "department" in emp.get_columns()
    assert emp.get_value("id") == "E001"


def test_deep_hierarchy_collection(context: EntityContext):
    """深い階層のコレクションをテスト"""
    xml = dedent(
        """
        <root>
            <department>
                <projects>
                    <project>
                        <tasks>
                            <task>
                                <id>1</id>
                                <name>Task 1</name>
                            </task>
                            <task>
                                <id>2</id>
                                <name>Task 2</name>
                            </task>
                        </tasks>
                    </project>
                </projects>
            </department>
        </root>
    """
    )
    element = ET.fromstring(xml)
    tasks_element = element.find(".//tasks")

    is_collection, child_tag = context.is_collection_element(tasks_element)
    assert is_collection
    assert child_tag == "task"

    # エンティティの階層構造も検証
    root = context.process_xml_element(element)
    dept = context.process_xml_element(root.element.find("department"), "root", root)
    projs = context.process_xml_element(dept.element.find("projects"), "root.department", dept)
    proj = context.process_xml_element(projs.element.find("project"), "root.department.projects", projs)
    tasks = context.process_xml_element(proj.element.find("tasks"), "root.department.projects.project", proj)
    task = context.process_xml_element(
        tasks.element.find("task"),
        "root.department.projects.project.tasks",
        tasks,
    )

    assert task is not None
    assert "id" in task.get_columns()
    assert "name" in task.get_columns()
    assert task.get_value("id") == "1"
    assert task.get_value("name") == "Task 1"
