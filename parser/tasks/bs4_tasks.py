import json
from random import  randint
from bs4 import BeautifulSoup

from bs4 import BeautifulSoup
from aiohttp import ClientSession
from selenium.webdriver.common.devtools.v85.runtime import await_promise
from asyncio import sleep


def parse_product_data(page_source):
    """Парсит HTML страницы продукта и извлекает информацию о продукте."""
    soup = BeautifulSoup(page_source, 'lxml')
    # Находим основной контейнер продукта
    product_container = soup.find('div', class_='product-secondary-section pdp-standard')
    print("Found the item container")
    if not product_container:
        print("Product container not found.")
        return None

    # Инициализируем переменные для хранения данных
    product = {
        "name": None,
        "brand_name": None,
        "description": None,
        "original_price_USD": None,
        "discount_price_USD": None,
        "color": None,  # Массив цветов
        "style_code": None
    }

    try:
        # Извлекаем бренд
        brand_tag = soup.find('span', class_='product-brand-name')
        if brand_tag:
            brand_link = brand_tag.find('a')
            product["brand_name"] = brand_link.get_text(strip=True) if brand_link else None

        # Извлекаем название продукта
        name_tag = soup.find('span', class_='product-name h2')
        if name_tag:
            product["name"] = name_tag.get_text(strip=True)

        # Извлекаем описание
        description_tag = soup.find('div', class_='value content', id='collapsible-details-1')
        if description_tag:
            description = description_tag.get_text(strip=True).split(".")[0] + "."
            product["description"] = description

        # Locate the prices container
        prices_container = soup.find('div', class_='prices')

        if prices_container:
            # Extract the original price
            original_price_tag = prices_container.find('span', class_='value')
            product["original_price_USD"] = (
                float(original_price_tag['content'].replace(',', ''))
                if original_price_tag and original_price_tag.has_attr('content')
                else None
            )

            # Extract the discount price
            discount_price_tag = prices_container.find('span', class_='value bfx-price')
            product["discount_price_USD"] = (
                float(discount_price_tag['content'].replace(',', ''))
                if discount_price_tag and discount_price_tag.has_attr('content')
                else None
            )

        # Извлекаем цвет (массив)
        colors = []

        # Проверяем наличие единственного цвета
        single_color_container = soup.find('span', class_='color non-input-label attribute-single')
        if single_color_container:
            color_tag = single_color_container.find('span', class_='text2')
            if color_tag:
                colors.append(color_tag.get_text(strip=True).lower())

        # Ищем элемент с множественными цветами
        multi_color_container = soup.find('ul', class_='color-wrapper radio-group-list', role='radiogroup')
        if multi_color_container:
            color_buttons = multi_color_container.find_all('button', class_='color-attribute')
            for button in color_buttons:
                aria_label = button.get('aria-label', '')
                if 'Select Color' in aria_label:
                    color_name = aria_label.split('Select Color')[-1].strip()
                    colors.append(color_name.lower())

        # Устанавливаем значение массива цветов или None, если цветов нет
        product["color"] = colors if colors else None

        # Устанавливаем значение массива цветов или None, если цветов нет
        # Конвертируем в JSON-string
        product["color"] = json.dumps(colors) if colors else None


        # Извлекаем Style Code
        style_code_tag = soup.find('div', class_='product-detail-id')
        if style_code_tag:
            style_code_text = style_code_tag.get_text(strip=True)
            if "Style Code:" in style_code_text:
                product["style_code"] = style_code_text.split("Style Code:")[-1].strip()

    except Exception as e:
        print(f"Error parsing product details: {e}")
    return product





import random
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    # Add more user agents
]

async def async_parse_product_data(session: ClientSession, url: str):
    """Asynchronously parses the HTML of a product page and extracts product information."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }

    async with session.get(url,headers=headers) as response:
        # Here you might process the page content asynchronously.
        page_content = await response.text()
        await sleep(randint(1,5))
        soup = BeautifulSoup(page_content, 'lxml')
        print(soup.prettify())
        # Locate the main product container
        product_container = soup.find('div', class_='product-secondary-section pdp-standard')

        if not product_container:
            print("Product container not found.")
            return None
        print("Found the item container")

        # Initialize product data dictionary
        product = {
            "name": None,
            "brand_name": None,
            "description": None,
            "original_price_USD": None,
            "discount_price_USD": None,
            "color": None,
            "style_code": None
        }

        def extract_text(tag, class_name, default=None, get_link_text=False):
            """Helper function to extract text from a given tag."""
            element = tag.find(class_=class_name) if tag else None
            if get_link_text and element:
                link = element.find('a')
                return link.get_text(strip=True) if link else default
            return element.get_text(strip=True) if element else default

        try:
            # Extract brand name
            product["brand_name"] = extract_text(soup, 'product-brand-name', get_link_text=True)

            # Extract product name
            product["name"] = extract_text(soup, 'product-name h2')

            # Extract product description (use only the first sentence)
            description = extract_text(soup, 'value content', default="", get_link_text=False)
            product["description"] = description.split(".")[0] + "." if description else None



            # Extract colors (as a list)
            colors = []

            # Check for a single color
            single_color_tag = soup.find('span', class_='color non-input-label attribute-single')
            if single_color_tag:
                color_name = extract_text(single_color_tag, 'text2')
                if color_name:
                    colors.append(color_name.lower())

            # Extract multiple colors if available
            multi_color_container = soup.find('ul', class_='color-wrapper radio-group-list', role='radiogroup')
            if multi_color_container:
                color_buttons = multi_color_container.find_all('button', class_='color-attribute')
                colors += [
                    button.get('aria-label', '').split('Select Color')[-1].strip().lower()
                    for button in color_buttons
                    if 'Select Color' in button.get('aria-label', '')
                ]

            # Set the colors as a JSON string or None
            product["color"] = json.dumps(colors) if colors else None

            # Extract Style Code
            style_code_tag = soup.find('div', class_='product-detail-id')
            if style_code_tag:
                style_code_text = style_code_tag.get_text(strip=True)
                product["style_code"] = style_code_text.split("Style Code:")[-1].strip() if "Style Code:" in style_code_text else None

        except Exception as e:
            print(f"Error parsing product details: {e}")

        return product

# product = {
    #   "style_code": <div class="product-detail-id">Style Code: 0400021492026</div>
    #    "brand_name":<span class="product-brand-name">
    # <a href="/brand/joe-s-jeans" class="product-brand adobelaunch__brand" data-adobelaunchproductid="0400021910443">Joe's Jeans</a>
    # </span>
    #     "name": <span class="product-name h2">
    # Harris Plaid Bouclé Flannel Shirt</span>,
    #     "description": <div class="value content" id="collapsible-details-1">
    # Joe's Jeans' Harris flannel shirt features a Sedona plaid print and comfortbale bouclé texture. Crafted of soft cotton, the woven design offers both style and comfort.<ul><li>Spread collar</li><li>Long sleeves, barrel cuffs</li><li>Button-front placket</li><li>100% cotton</li><li>Machine wash</li><li>Imported</li></ul><br><b>SIZE &amp; FIT</b><ul><li>Model measurements: 6’2” tall, 40” chest, 31” waist</li><li>Model is wearing a US size Medium</li></ul>
    # <div class="product-detail-id">
    # Style Code: 0400021910443
    # </div>
    # </div>,
    #     "original_price": <span class="formatted_price bfx-price bfx-list-price" content="$189" data-unformatted-price="189" data-bfx="{&quot;original&quot;:[&quot;$189&quot;],&quot;id&quot;:&quot;yzozuibyb&quot;}">
    # &#xFEFF;HKD 1,584.12
    # </span>,
    #     "discount_price": <span class="formatted_sale_price formatted_price js-final-sale-price bfx-price bfx-sale-price" data-unformatted-price="69.99" data-bfx="{&quot;original&quot;:[&quot;$69.99&quot;],&quot;id&quot;:&quot;5a8z34gn0&quot;}">&#xFEFF;HKD 586.63</span>,
    #     "color": container - <ul class="color-wrapper radio-group-list" role="radiogroup">, <ul class="color-wrapper radio-group-list" role="radiogroup"><li role="radio" aria-checked="true">
    # 										<button class="color-attribute radio-group-trigger adobelaunch__colorlink selectable selected" aria-label="Select Color BANDANA" aria-describedby="BANDANA"
# container div class="prices">
# original price <span class="value" content="570.00">
# discount price <span class="value bfx-price" content="299.99">