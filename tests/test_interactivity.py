import re
from collections.abc import Generator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from myst_nb_json import CLS_COLLAPSED, JsonMimeRenderPlugin


@pytest.fixture
def plugin() -> JsonMimeRenderPlugin:
    return JsonMimeRenderPlugin()


JSON_DATA = {
    "key1": "value1",
    "key2": {
        "key21": "str",
        "key22": 42,
        "key23": 3.14,
        "key24": True,
        "key25": False,
        "key26": None,
        "key27": {},
        "key28": [],
    },
    "key3": ["str", 42, 3.14, True, False, None, {}, []],
}


@pytest.fixture
def browser() -> Generator[WebDriver]:
    # Set up headless Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    # Initialize the WebDriver
    driver: WebDriver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()


def test_interactive_collapse_expand(plugin: JsonMimeRenderPlugin, browser: WebDriver):
    # Load the HTML string
    html_content = plugin.html(JSON_DATA, root="test", expanded=True)
    # Hash (in CSS color) causes problems for Selenium Chrome webdriver
    html_content = re.sub("#", "&num;", html_content)
    browser.get("data:text/html;charset=utf-8," + html_content)

    # Wait for the JavaScript to execute
    browser.implicitly_wait(2)

    text_to_click = "key2"
    element_to_click = browser.find_element(By.XPATH, f"//*[contains(text(), '{text_to_click}')]")
    value_element = element_to_click.find_element(By.XPATH, "following-sibling::*[1]")
    li_element = element_to_click.find_element(By.XPATH, "ancestor::li[1]")

    assert CLS_COLLAPSED not in li_element.get_attribute("class")
    assert value_element.value_of_css_property("display") != "none"

    # Collapse
    element_to_click.click()
    assert CLS_COLLAPSED in li_element.get_attribute("class")
    assert value_element.value_of_css_property("display") == "none"

    # Expand
    element_to_click.click()
    assert CLS_COLLAPSED not in li_element.get_attribute("class")
    assert value_element.value_of_css_property("display") != "none"
