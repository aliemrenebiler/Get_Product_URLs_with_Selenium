"Trendyol Utils"

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from models.errors import LoginError, WebDriverError
from models.web_driver import WebDriver

# pylint: disable=broad-except


def login_to_trendyol(
    browser: WebDriver, email: str, password: str, timeout: int = 300
):
    "Logins to Trendyol"

    try:
        browser.get("https://partner.trendyol.com/account/login")

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
            EC.url_to_be("https://partner.trendyol.com/dashboard")
            or EC.url_to_be(
                "https://partner.trendyol.com/account/info"
                + "?tab=contractAndDocuments&openApproveModal=true"
            )
        )
    except Exception as exc:
        raise LoginError("Could not login to Trendyol.") from exc


def get_product_url_from_trendyol(
    browser: WebDriver, product_code: str, timeout: int = 3
) -> str | None:
    "Gets the URL of the product with specified code from Trendyol"
    try:
        if (
            browser.current_url
            != "https://partner.trendyol.com/product-listing/all-products"
        ):
            browser.get("https://partner.trendyol.com/product-listing/all-products")
    except Exception as exc:
        raise WebDriverError("Could not found Trendyol partner products page.") from exc

    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//bl-input[@cy-id="stockCodeFilter"]',
                )
            )
        ).send_keys(product_code)

        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//bl-button[@cy-id="submitFilter"]',
                )
            )
        ).click()
    except Exception as exc:
        raise WebDriverError("Error during Trendyol product search.") from exc

    try:
        product_url = (
            WebDriverWait(browser, timeout)
            .until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//sc-product-info",
                    )
                )
            )
            .get_attribute("href")
        )

        return product_url
    except Exception:
        return None


def get_product_info_from_trendyol(
    browser: WebDriver, product_url: str, timeout: int = 3
) -> (str | None, str | None):
    "Gets the product name and description on Trendyol"

    try:
        browser.get(product_url)
    except Exception as exc:
        raise WebDriverError(
            "Could not get product information, could not reach Trendyol product page."
        ) from exc

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
