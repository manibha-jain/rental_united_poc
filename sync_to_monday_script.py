from sync_rental_to_monday.sync_rental_properties import sync_rental_to_monday

def main():
    api_respose = sync_rental_to_monday()
    return api_respose


if __name__ == "__main__":
    main()
