from put_prices.prices_utils import upload_prices

def main():
    api_respose = upload_prices()

    return api_respose


if __name__ == "__main__":
    main()