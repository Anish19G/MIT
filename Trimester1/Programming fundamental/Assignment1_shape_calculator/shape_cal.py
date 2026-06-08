"""Command line shape calculator that uses functions in `shapes.py`.

This script is intentionally small and delegates math to shapes.py so
we can test functions separately. It provides friendly input validation
and a simple interactive menu.
"""
from __future__ import annotations

import sys
from typing import Optional

from shapes import (
    circle_area,
    circle_circumference,
    cone_base_circumference,
    cone_total_surface_area,
    pyramid_base_perimeter,
    pyramid_total_surface_area,
    rectangle_area,
    rectangle_perimeter,
    square_area,
    square_perimeter,
    triangle_area,
    triangle_perimeter,
)


def read_positive_float(prompt: str) -> float:
    while True:
        v = input(prompt).strip()
        if v.lower() in ("q", "quit", "exit"):
            print("Exiting.")
            sys.exit(0)
        try:
            f = float(v)
        except ValueError:
            print("Invalid. Try again.")
            continue
        if f <= 0:
            print("Enter positive number")
            continue
        return f


def read_choice(prompt: str, allowed: Optional[list[str]] = None) -> str:
    c = input(prompt).strip().lower()
    if allowed and c not in allowed:
        return c
    return c


def main() -> None:
    while True:
        print("\nMenu: 1-Rectangle 2-Square 3-Circle 4-Cone 5-Pyramid 6-Triangle q-Quit")
        choice = read_choice("Select: ")
        if choice in ("q", "quit", "exit"):
            print("Exiting.")
            break

        if choice == "1":
            print("1) Area  2) Perimeter  (b to go back)")
            sub = input("-> ").strip().lower()
            if sub == "b":
                continue
            L = read_positive_float("Length: ")
            W = read_positive_float("Width: ")
            if sub == "1":
                print(f"Area = {rectangle_area(L, W):.6f}")
            else:
                print(f"Perimeter = {rectangle_perimeter(L, W):.6f}")

        elif choice == "2":
            print("1) Area  2) Perimeter")
            sub = input("-> ").strip()
            S = read_positive_float("Side: ")
            if sub == "1":
                print(f"Area = {square_area(S):.6f}")
            else:
                print(f"Perimeter = {square_perimeter(S):.6f}")

        elif choice == "3":
            print("1) Area  2) Circumference")
            sub = input("-> ").strip()
            R = read_positive_float("Radius: ")
            if sub == "1":
                print(f"Area = {circle_area(R):.6f}")
            else:
                print(f"Circumference = {circle_circumference(R):.6f}")

        elif choice == "4":
            print("1) Total surface area  2) Base circumference")
            sub = input("-> ").strip()
            R = read_positive_float("Radius: ")
            if sub == "1":
                H = read_positive_float("Height: ")
                print(f"Total surface area = {cone_total_surface_area(R, H):.6f}")
            else:
                print(f"Base circumference = {cone_base_circumference(R):.6f}")

        elif choice == "5":
            print("1) Total surface area  2) Base perimeter")
            sub = input("-> ").strip()
            A = read_positive_float("Base side a: ")
            if sub == "1":
                H = read_positive_float("Height: ")
                print(f"Total surface area = {pyramid_total_surface_area(A, H):.6f}")
            else:
                print(f"Base perimeter = {pyramid_base_perimeter(A):.6f}")

        elif choice == "6":
            print("1) Area (base & height)  2) Perimeter (three sides)")
            sub = input("-> ").strip()
            if sub == "1":
                B = read_positive_float("Base: ")
                H = read_positive_float("Height: ")
                print(f"Area = {triangle_area(B, H):.6f}")
            else:
                a = read_positive_float("Side a: ")
                b = read_positive_float("Side b: ")
                c = read_positive_float("Side c: ")
                print(f"Perimeter = {triangle_perimeter(a, b, c):.6f}")

        else:
            print("Invalid selection")


if __name__ == "__main__":
    main()
"""Command line shape calculator that uses functions in `shapes.py`.

This script is intentionally small and delegates math to shapes.py so
we can test functions separately. It provides friendly input validation
and a simple interactive menu.
"""
from __future__ import annotations

import sys
from typing import Optional

from shapes import (
    circle_area,
    circle_circumference,
    cone_base_circumference,
    cone_total_surface_area,
    pyramid_base_perimeter,
    pyramid_total_surface_area,
    rectangle_area,
    rectangle_perimeter,
    square_area,
    square_perimeter,
    triangle_area,
    triangle_perimeter,
)


def read_positive_float(prompt: str) -> float:
    while True:
        v = input(prompt).strip()
        if v.lower() in ("q", "quit", "exit"):
            print("Exiting.")
            sys.exit(0)
        try:
            f = float(v)
        except ValueError:
            print("Invalid. Try again.")
            continue
        if f <= 0:
            print("Enter positive number")
            continue
        return f


def read_choice(prompt: str, allowed: Optional[list[str]] = None) -> str:
    c = input(prompt).strip().lower()
    if allowed and c not in allowed:
        return c
    return c


def main() -> None:
    while True:
        print("\nMenu: 1-Rectangle 2-Square 3-Circle 4-Cone 5-Pyramid 6-Triangle q-Quit")
        choice = read_choice("Select: ")
        if choice in ("q", "quit", "exit"):
            print("Exiting.")
            break

        if choice == "1":
            print("1) Area  2) Perimeter  (b to go back)")
            sub = input("-> ").strip().lower()
            if sub == "b":
                continue
            L = read_positive_float("Length: ")
            W = read_positive_float("Width: ")
            if sub == "1":
                print(f"Area = {rectangle_area(L, W):.6f}")
            else:
                print(f"Perimeter = {rectangle_perimeter(L, W):.6f}")

        elif choice == "2":
            print("1) Area  2) Perimeter")
            sub = input("-> ").strip()
            S = read_positive_float("Side: ")
            if sub == "1":
                print(f"Area = {square_area(S):.6f}")
            else:
                print(f"Perimeter = {square_perimeter(S):.6f}")

        elif choice == "3":
            print("1) Area  2) Circumference")
            sub = input("-> ").strip()
            R = read_positive_float("Radius: ")
            if sub == "1":
                print(f"Area = {circle_area(R):.6f}")
            else:
                print(f"Circumference = {circle_circumference(R):.6f}")

        elif choice == "4":
            print("1) Total surface area  2) Base circumference")
            sub = input("-> ").strip()
            R = read_positive_float("Radius: ")
            if sub == "1":
                H = read_positive_float("Height: ")
                print(f"Total surface area = {cone_total_surface_area(R, H):.6f}")
            else:
                print(f"Base circumference = {cone_base_circumference(R):.6f}")

        elif choice == "5":
            print("1) Total surface area  2) Base perimeter")
            sub = input("-> ").strip()
            A = read_positive_float("Base side a: ")
            if sub == "1":
                H = read_positive_float("Height: ")
                print(f"Total surface area = {pyramid_total_surface_area(A, H):.6f}")
            else:
                print(f"Base perimeter = {pyramid_base_perimeter(A):.6f}")

        elif choice == "6":
            print("1) Area (base & height)  2) Perimeter (three sides)")
            sub = input("-> ").strip()
            if sub == "1":
                B = read_positive_float("Base: ")
                H = read_positive_float("Height: ")
                print(f"Area = {triangle_area(B, H):.6f}")
            else:
                a = read_positive_float("Side a: ")
                b = read_positive_float("Side b: ")
                c = read_positive_float("Side c: ")
                print(f"Perimeter = {triangle_perimeter(a, b, c):.6f}")

        else:
            print("Invalid selection")


if __name__ == "__main__":
    main()
"""Command line shape calculator.

This script provides a simple command-line menu but keeps the
mathematical logic in the `shapes` module so it's easy to test.
"""
from __future__ import annotations

import math
import sys
from typing import Callable

from shapes import (
    circle_area,
    circle_circumference,
    cone_base_circumference,
    cone_total_surface_area,
    pyramid_base_perimeter,
    pyramid_total_surface_area,
    rectangle_area,
    rectangle_perimeter,
    square_area,
    square_perimeter,
    triangle_area,
    triangle_perimeter,
)


def read_positive_float(prompt: str) -> float:
    """Read a positive float from stdin. 'q', 'quit', 'exit' will exit.

    Keeps asking until a valid positive number is entered.
    """
    while True:
        v = input(prompt).strip()
        if v.lower() in ("q", "quit", "exit"):
            print("Exiting.")
            sys.exit(0)
        try:
            f = float(v)
            if f <= 0:
                print("Enter positive number")
                continue
            return f
        except ValueError:
            print("Invalid. Try again.")


def read_choice(prompt: str, allowed: list[str] | None = None) -> str:
    """Read a menu choice; normalize and optionally validate."""
    c = input(prompt).strip().lower()
    if allowed and c not in allowed:
        return c
    return c


def main() -> None:
    """Run the interactive CLI loop."""
    while True:
        print("\nMenu: 1-Rectangle 2-Square 3-Circle 4-Cone 5-Pyramid 6-Triangle q-Quit")
        choice = read_choice("Select: ")
        if choice in ("q", "quit", "exit"):
            print("Exiting.")
            break

        # Rectangle
        if choice == "1":
            print("1) Area  2) Perimeter  (b to go back)")
            sub = input("-> ").strip().lower()
            if sub == "b":
                continue
            L = read_positive_float("Length: ")
            W = read_positive_float("Width: ")
            if sub == "1":
                print(f"Area = {rectangle_area(L, W):.6f}")
            else:
                print(f"Perimeter = {rectangle_perimeter(L, W):.6f}")

        # Square
        elif choice == "2":
        print("1) Area  2) Perimeter")
        sub = input("-> ").strip()
        while True:
            v = input("Side: ").strip()
            if v.lower() in ('q', 'quit', 'exit'):
                print("Exiting.")
                sys.exit(0)
            try:
                S = float(v)
                if S <= 0:
                    print("Enter positive number")
                    continue
                break
            except ValueError:
                print("Invalid. Try again.")
        if sub == '1':
            print(f"Area = {S*S:.6f}")
        else:
            print(f"Perimeter = {4*S:.6f}")

        # Circle
        elif choice == "3":
        print("1) Area  2) Circumference")
        sub = input("-> ").strip()
        while True:
            v = input("Radius: ").strip()
            if v.lower() in ('q', 'quit', 'exit'):
                print("Exiting.")
                sys.exit(0)
            try:
                R = float(v)
                if R <= 0:
                    print("Enter positive number")
                    continue
                break
            except ValueError:
                print("Invalid. Try again.")
        if sub == '1':
            print(f"Area = {math.pi*R*R:.6f}")
        else:
            print(f"Circumference = {2*math.pi*R:.6f}")

        # Cone
        elif choice == "4":
        print("1) Total surface area  2) Base circumference")
        sub = input("-> ").strip()
        while True:
            v = input("Radius: ").strip()
            if v.lower() in ('q', 'quit', 'exit'):
                print("Exiting.")
                sys.exit(0)
            try:
                R = float(v)
                if R <= 0:
                    print("Enter positive number")
                    continue
                break
            except ValueError:
                print("Invalid. Try again.")
        if sub == '1':
            while True:
                v = input("Height: ").strip()
                if v.lower() in ('q', 'quit', 'exit'):
                    print("Exiting.")
                    sys.exit(0)
                try:
                    H = float(v)
                    if H <= 0:
                        print("Enter positive number")
                        continue
                    break
                except ValueError:
                    print("Invalid. Try again.")
            sl = math.hypot(R, H)
            print(f"Total surface area = {math.pi*R*(R+sl):.6f}")
        else:
            print(f"Base circumference = {2*math.pi*R:.6f}")

        # Pyramid (regular square)
        elif choice == "5":
        print("1) Total surface area  2) Base perimeter")
        sub = input("-> ").strip()
        while True:
            v = input("Base side a: ").strip()
            if v.lower() in ('q', 'quit', 'exit'):
                print("Exiting.")
                sys.exit(0)
            try:
                A = float(v)
                if A <= 0:
                    print("Enter positive number")
                    continue
                break
            except ValueError:
                print("Invalid. Try again.")
        if sub == '1':
            while True:
                v = input("Height: ").strip()
                if v.lower() in ('q', 'quit', 'exit'):
                    print("Exiting.")
                    sys.exit(0)
                try:
                    H = float(v)
                    if H <= 0:
                        print("Enter positive number")
                        continue
                    break
                except ValueError:
                    print("Invalid. Try again.")
            sl = math.hypot(A/2.0, H)
            print(f"Total surface area = {A*A + 2*A*sl:.6f}")
        else:
            print(f"Base perimeter = {4*A:.6f}")

        # Triangle
        elif choice == "6":
        print("1) Area (base & height)  2) Perimeter (three sides)")
        sub = input("-> ").strip()
        if sub == '1':
            while True:
                v = input("Base: ").strip()
                if v.lower() in ('q', 'quit', 'exit'):
                    print("Exiting.")
                    sys.exit(0)
                try:
                    B = float(v)
                    if B <= 0:
                        print("Enter positive number")
                        continue
                    break
                except ValueError:
                    print("Invalid. Try again.")
            while True:
                v = input("Height: ").strip()
                if v.lower() in ('q', 'quit', 'exit'):
                    print("Exiting.")
                    sys.exit(0)
                try:
                    H = float(v)
                    if H <= 0:
                        print("Enter positive number")
                        continue
                    break
                except ValueError:
                    print("Invalid. Try again.")
            print(f"Area = {0.5*B*H:.6f}")
        else:
            while True:
                v = input("Side a: ").strip()
                if v.lower() in ('q', 'quit', 'exit'):
                    print("Exiting.")
                    sys.exit(0)
                try:
                    a = float(v)
                    if a <= 0:
                        print("Enter positive number")
                        continue
                    break
                except ValueError:
                    print("Invalid. Try again.")
            while True:
                v = input("Side b: ").strip()
                if v.lower() in ('q', 'quit', 'exit'):
                    print("Exiting.")
                    sys.exit(0)
                try:
                    b = float(v)
                    if b <= 0:
                        print("Enter positive number")
                        continue
                    break
                except ValueError:
                    print("Invalid. Try again.")
            while True:
                v = input("Side c: ").strip()
                if v.lower() in ('q', 'quit', 'exit'):
                    print("Exiting.")
                    sys.exit(0)
                try:
                    c = float(v)
                    if c <= 0:
                        print("Enter positive number")
                        continue
                    break
                except ValueError:
                    print("Invalid. Try again.")
            print(f"Perimeter = {a+b+c:.6f}")

        else:
            print("Invalid selection")


if __name__ == "__main__":
    main()

