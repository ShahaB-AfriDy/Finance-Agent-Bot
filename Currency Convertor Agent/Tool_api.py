from pydantic import BaseModel, Field
from typing import Union
from langchain.tools import tool
from pydantic import BaseModel, Field, ValidationError
import json
import requests
import os

from dotenv import load_dotenv

load_dotenv()



class CurrencyConversionInput(BaseModel):
    base_currency: str = Field(..., description="Base currency code, e.g., 'USD'")
    target_currency: str = Field(..., description="Target currency code, e.g., 'PKR'")


@tool
def get_conversion_factor(input_data) -> float:
    """
    Fetches the conversion rate from base_currency to target_currency using the ExchangeRate API.

    Args:
        input_data (dict or str): A dictionary or JSON string with:
            - base_currency (str)
            - target_currency (str)

    Returns:
        float: The conversion rate

    Raises:
        Exception: If validation or API request fails
    """
    try:
        # 📥 If input is a JSON string, convert it to dict
        if isinstance(input_data, str):
            input_data = json.loads(input_data)

        # 🛡️ Validate input using Pydantic
        validated_input = CurrencyConversionInput(**input_data)
        base = validated_input.base_currency
        target = validated_input.target_currency
        # api key
        exchange_api_key = os.getenv("exchange_api_key")
        # 🌍 API call
        url = f'https://v6.exchangerate-api.com/v6/{exchange_api_key}/pair/{base}/{target}'
        response = requests.get(url)
        response.raise_for_status()

        # 📦 Parse response
        data = response.json()
        if "conversion_rate" in data:
            return data["conversion_rate"]
        else:
            raise ValueError(f"'conversion_rate' not found in response: {data}")

    except ValidationError as ve:
        raise Exception(f"Input validation error: {ve}")
    except json.JSONDecodeError:
        raise Exception("Invalid JSON string input. Provide a valid dictionary or JSON-formatted string.")
    except requests.exceptions.HTTPError as http_err:
        raise Exception(f"HTTP error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise Exception(f"Request error: {req_err}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")




class CurrencyConvertInput(BaseModel):
    base_currency_value: float = Field(..., description="The amount in base currency (e.g., 10)")
    conversion_rate: float = Field(..., description="The currency conversion rate (e.g., 283.7195)")

@tool
def currency_convert(input_data: Union[dict, str]) -> float:
    """
    Converts a currency amount using a given conversion rate.
    
    Accepts input_data as either a dictionary or a JSON string with:
    {
        "base_currency_value": float,
        "conversion_rate": float
    }
    """
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    validated = CurrencyConvertInput(**input_data)
    result = validated.base_currency_value * validated.conversion_rate
    return round(result, 4)


if __name__ == "__main__":
    print(get_conversion_factor.invoke('{"base_currency": "USD", "target_currency": "PKR"}'))
