import pytest
import time

# Example usage of sleep
time.sleep(1)  # Sleep for 1 second

from playwright.sync_api import sync_playwright

@pytest.fixture(scope='session')
def playwright():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope='session')
def browser(playwright):
    browser = playwright.chromium.launch(headless=True)  # Launch browser headlessly
    try:
        yield browser
    finally:
        browser.close()

@pytest.fixture
def context(browser):
    context = browser.new_context(ignore_https_errors=True)
    try:
        yield context
    finally:
        context.close()

@pytest.fixture
def page(context):
    page = context.new_page()
    try:
        yield page
    finally:
        page.close()

def test_search_no_query(page):
    page.goto("http://127.0.0.1:5002/search", wait_until="domcontentloaded")
    page_content = page.content()
    expected_text = "Keep yourself updated"
    # Debug by printing the page content to understand what is being rendered
    print(page_content)  # Temporarily add this to see what the page actually contains
    assert expected_text in page_content, f"Expected text not found on the page. Page content: {page_content}"
    time.sleep(3)  

def test_search_with_query(page):
    search_query = "business"
    page.goto(f"http://127.0.0.1:5002/search?query={search_query}", wait_until="domcontentloaded")
    page_content = page.content()
    expected_text = "Business contents insuranc"
    # Debug output to check the state of the page
    print(page.content())  # This might help to understand what's happening on the page

    # Check if the selector exists before waiting for it
    assert expected_text in page_content, f"Expected text not found on the page. Page content: {page_content}"
    time.sleep(3)  