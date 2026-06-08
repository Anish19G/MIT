import math

while True:
    print("\nChoose a shape:")
    print("1. Rectangle")
    print("2. Square")
    print("3. Circle")
    print("4. Cone")
    print("5. Pyramid")
    print("6. Triangle")
    print("0. Exit")

    shape_choice = input("Enter number: ").strip()

    if shape_choice == "0":
        print("Exiting.")
        break

    print("\nWhat do you want to calculate?")
    print("1. Area")
    print("2. Perimeter (or equivalent)")
    calc_choice = input("Enter 1 or 2: ").strip()

    # Rectangle
    if shape_choice == "1":
        length = float(input("Enter length: "))
        width  = float(input("Enter width: "))

        if calc_choice == "1":
            area = length * width
            print(f"Rectangle area = {area}")
        elif calc_choice == "2":
            perimeter = 2 * (length + width)
            print(f"Rectangle perimeter = {perimeter}")
        else:
            print("Invalid choice in submenu.")

    # Square
    elif shape_choice == "2":
        side = float(input("Enter side: "))

        if calc_choice == "1":
            area = side * side
            print(f"Square area = {area}")
        elif calc_choice == "2":
            perimeter = 4 * side
            print(f"Square perimeter = {perimeter}")
        else:
            print("Invalid choice in submenu.")

    # Circle
    elif shape_choice == "3":
        radius = float(input("Enter radius: "))

        if calc_choice == "1":
            area = math.pi * radius * radius
            print(f"Circle area = {area}")
        elif calc_choice == "2":
            circumference = 2 * math.pi * radius
            print(f"Circle circumference = {circumference}")
        else:
            print("Invalid choice in submenu.")

    # Cone
    elif shape_choice == "4":
        radius = float(input("Enter base radius of cone: "))
        slant  = float(input("Enter slant height of cone: "))

        if calc_choice == "1":
            surface_area = math.pi * radius * (radius + slant)
            print(f"Cone surface area = {surface_area}")
        elif calc_choice == "2":
            base_perimeter = 2 * math.pi * radius
            print(f"Cone base perimeter (circumference) = {base_perimeter}")
        else:
            print("Invalid choice in submenu.")

    # Pyramid (assuming square base)
    elif shape_choice == "5":
        base_side = float(input("Enter base side length of pyramid: "))
        slant     = float(input("Enter slant height of pyramid: "))

        if calc_choice == "1":
            base_area = base_side * base_side
            face_area = (base_side * slant) / 2
            surface_area = base_area + 4 * face_area
            print(f"Pyramid surface area = {surface_area}")
        elif calc_choice == "2":
            base_perimeter = 4 * base_side
            print(f"Pyramid base perimeter = {base_perimeter}")
        else:
            print("Invalid choice in submenu.")

    # Triangle
    elif shape_choice == "6":
        if calc_choice == "2":
            a = float(input("Enter side a: "))
            b = float(input("Enter side b: "))
            c = float(input("Enter side c: "))
            perimeter = a + b + c
            print(f"Triangle perimeter = {perimeter}")
        elif calc_choice == "1":
            base   = float(input("Enter base: "))
            height = float(input("Enter height: "))
            area   = 0.5 * base * height
            print(f"Triangle area = {area}")
        else:
            print("Invalid choice in submenu.")

    else:
        print("Invalid shape choice. Try again.")
