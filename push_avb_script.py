from push_avb_units.avb_utils import get_available_units_monday


def main():
    api_respose = get_available_units_monday()
    return api_respose


if __name__ == "__main__":
    main()