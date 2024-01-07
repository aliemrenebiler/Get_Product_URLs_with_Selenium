"Trendyol Utils"

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.constants.urls import (
    TRENDYOL_MAIN_PAGE_URL,
    TRENDYOL_PARTNER_PRODUCTS_PAGE_URL,
    TRENDYOL_PARTNER_DASHBOARD_PAGE_URL,
    TRENDYOL_PARTNER_LOGIN_PAGE_URL,
    TRENDYOL_PARTNER_REDIRECT_AFTER_LOGIN_PAGE_URL,
)
from models.errors import LoginError, WebDriverError
from models.web_driver import WebDriver

# pylint: disable=broad-except


def login_to_trendyol(
    browser: WebDriver, email: str, password: str, timeout: int = 300
):
    "Logins to Trendyol"

    try:
        if browser.current_url != TRENDYOL_PARTNER_LOGIN_PAGE_URL:
            browser.get(TRENDYOL_PARTNER_LOGIN_PAGE_URL)

        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@class="email-phone g-input"]//input',
                )
            )
        ).send_keys(email)

        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@class="password g-input"]//input',
                )
            )
        ).send_keys(password)

        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//button[@class="invisible-captcha-btn btn '
                    + 'btn-lg btn-mp-primary btn-block g-button -primary"]',
                )
            )
        ).click()

        WebDriverWait(browser, timeout).until(
            EC.url_to_be(TRENDYOL_PARTNER_DASHBOARD_PAGE_URL)
            or EC.url_to_be(TRENDYOL_PARTNER_REDIRECT_AFTER_LOGIN_PAGE_URL)
        )
    except Exception as exc:
        raise LoginError("Could not login to Trendyol.") from exc


def accept_trendyol_cookies(browser: WebDriver, timeout: int = 10):
    "Accepts Trendyol cookies"

    try:
        if browser.current_url != TRENDYOL_MAIN_PAGE_URL:
            browser.get(TRENDYOL_MAIN_PAGE_URL)

        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//button[@id="onetrust-accept-btn-handler"]',
                )
            )
        ).click()
    except Exception as exc:
        raise WebDriverError("Error during accepting Trendyol cookies.") from exc


def get_product_url_from_trendyol(
    browser: WebDriver, product_code: str, timeout: int = 10
) -> str | None:
    "Gets the URL of the product with specified code from Trendyol"

    try:
        if browser.current_url != TRENDYOL_PARTNER_PRODUCTS_PAGE_URL:
            browser.get(TRENDYOL_PARTNER_PRODUCTS_PAGE_URL)
    except Exception as exc:
        raise WebDriverError("Could not found Trendyol partner products page.") from exc

    try:
        search_input_element = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//bl-input[@cy-id="stockCodeFilter"]',
                )
            )
        )
        search_input_element.send_keys(Keys.CONTROL + "A", Keys.BACK_SPACE)
        search_input_element.send_keys(product_code, Keys.ENTER)
    except Exception as exc:
        raise WebDriverError(
            "Error during product search on Trendyol partner page."
        ) from exc

    try:
        product_url = (
            WebDriverWait(browser, timeout)
            .until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//sc-product-info | //div[@class="not_found"]',
                    )
                )
            )
            .get_attribute("href")
        )

        return product_url
    except Exception:
        return None


def get_product_info_from_trendyol(
    browser: WebDriver, product_url: str, timeout: int = 10
) -> (str | None, str | None):
    "Gets the product name and description on Trendyol"

    try:
        if browser.current_url != product_url:
            browser.get(product_url)
    except Exception as exc:
        raise WebDriverError(
            "Could not get product information, could not reach Trendyol product page."
        ) from exc

    try:
        product_name_brand = (
            WebDriverWait(browser, timeout)
            .until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//a[@class="product-brand-name-with-link"]',
                    )
                )
            )
            .text
        )
    except Exception:
        product_name_brand = None

    try:
        product_name = (
            WebDriverWait(browser, timeout)
            .until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//div[@class="product-detail-wrapper"]//h1[@class="pr-new-br"]/span',
                    )
                )
            )
            .text
        )
        if product_name_brand:
            product_name = f"{product_name_brand} {product_name}"
    except Exception:
        product_name = None

    try:
        product_desc_child_elements = (
            WebDriverWait(browser, timeout)
            .until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//div[@class="info-wrapper"]',
                    )
                )
            )
            .find_elements(By.XPATH, "*")
        )

        product_desc = "".join(
            [child.get_attribute("outerHTML") for child in product_desc_child_elements]
        )
    except Exception:
        product_desc = None

    return product_name, product_desc
