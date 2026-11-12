def lookup_drink_code(code_string):
    menu_prices = {
        "LAT": 4.50,
        "CAP": 4.00,
        "ESP": 3.00,
        "AME": 3.50,
        "MOC": 5.00,   # fixed: key normalised to uppercase so a "MOC" prefix can match
    }
    # Defensive: reject anything that is not a string instead of crashing on .upper()
    if not isinstance(code_string, str):
        return None
    code_prefix = code_string.upper()[:3]
    # Defensive: .get() returns None for an unknown code instead of raising KeyError
    return menu_prices.get(code_prefix)


def calculate_average_shot_cost(pricing_csv):
    # Defensive: non-string input (e.g. None) returns 0.0 instead of crashing on .split()
    if not isinstance(pricing_csv, str):
        return 0.0

    prices = []
    for p in pricing_csv.split(','):
        p = p.strip()
        if not p:
            continue                 # skip empty tokens ("1,,2")
        try:
            prices.append(float(p))
        except ValueError:
            continue                 # skip non-numeric tokens ("abc")

    # Defensive: avoid ZeroDivisionError when there are no valid prices
    if not prices:
        return 0.0
    return sum(prices) / len(prices)


def parse_order_modifiers(order_spec):
    modifier_dict = {}
    # Defensive: non-string input returns an empty dict instead of crashing on .split()
    if not isinstance(order_spec, str):
        return modifier_dict

    for item in order_spec.split(';'):
        # Defensive: skip entries with no ':' instead of crashing on tuple unpacking
        if ':' not in item:
            continue
        # partition keeps everything after the first ':' as the value ("a:b:c" is safe)
        key, _, value = item.partition(':')
        key = key.strip()
        if key:                      # ignore entries with an empty key
            modifier_dict[key] = value.strip()
    return modifier_dict


def main():
    print("==== Running lookup_drink_code ====")
    drink_input = input("Enter drink code prefix (e.g. LAT, CAP, ESP): ")
    price = lookup_drink_code(drink_input)
    if price is None:
        print("Base Price: unknown drink code")
    else:
        print("Base Price: $", price)

    print("\n==== Running calculate_average_shot_cost ====")
    shots_input = input("Enter CSV of shot prices (e.g. 1.0, 1.5, 2.0): ")
    avg_price = calculate_average_shot_cost(shots_input)
    print("Average Shot Price: $", avg_price)

    print("\n==== Running parse_order_modifiers ====")
    spec_input = input("Enter modifiers (e.g. milk:oat;syrup:vanilla): ")
    mods = parse_order_modifiers(spec_input)
    print("Parsed Modifiers:", mods)


if __name__ == "__main__":
    main()