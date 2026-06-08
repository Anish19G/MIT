def display_menu():
    """Displays the main menu options to the user[cite: 22]."""
    print("\n--- Warehouse Inventory Management System ---")
    print("1. Add New Product")
    print("2. Update Stock")
    print("3. Search for a Product")
    print("4. Display Inventory Details")
    print("5. Exit")

def add_product(inventory):
    """
    Handles adding a new product with ID, Name, Category, and Quantity[cite: 8, 9, 10, 11, 12].
    Includes exception handling for duplicate IDs.
    """
    try:
        p_id = input("Enter Product ID: ").strip()
        
        # Exception handling for existing Product ID 
        if p_id in inventory:
            raise KeyError(f"Validation Error: Product ID '{p_id}' already exists.")
        
        name = input("Enter Product Name: ").strip()
        if not name:
            raise ValueError("Product Name cannot be empty.")
            
        category = input("Enter Category: ").strip()
        
        # Input validation for numeric quantity 
        quantity = int(input("Enter Initial Quantity: "))
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
            
        inventory[p_id] = {
            "name": name,
            "category": category,
            "quantity": quantity
        }
        print(f"Product '{name}' added successfully.")
        
    except KeyError as e:
        print(e)
    except ValueError as e:
        print(f"Input Error: {e}. Please enter valid data.")

def update_stock(inventory):
    """Updates stock levels by increasing or decreasing quantities[cite: 15, 16, 17]."""
    p_id = input("Enter Product ID to update: ").strip()
    
    if p_id not in inventory:
        print("Error: Product ID not found.")
        return

    print(f"Current Stock for {inventory[p_id]['name']}: {inventory[p_id]['quantity']}")
    print("a. Increase stock")
    print("b. Decrease stock")
    choice = input("Select option (a/b): ").lower()

    try:
        amount = int(input("Enter quantity amount: "))
        if amount < 0:
            print("Amount must be positive.")
            return

        if choice == 'a':
            inventory[p_id]['quantity'] += amount
            print("Stock increased successfully.")
        elif choice == 'b':
            if amount > inventory[p_id]['quantity']:
                print("Error: Insufficient stock. Decrease amount exceeds current inventory.")
            else:
                inventory[p_id]['quantity'] -= amount
                print("Stock decreased successfully.")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input. Please enter a whole number for quantity.")

def search_product(inventory):
    """Searches for a product using either ID or Name[cite: 18, 19]."""
    query = input("Enter Product ID or Product Name to search: ").strip().lower()
    found = False
    
    for p_id, details in inventory.items():
        if query == p_id.lower() or query == details['name'].lower():
            print(f"\n--- Product Found ---")
            print(f"ID: {p_id}")
            print(f"Name: {details['name']}")
            print(f"Category: {details['category']}")
            print(f"Stock: {details['quantity']}")
            found = True
            break
    
    if not found:
        print("No product found matching that criteria.")

def display_inventory(inventory):
    """Displays all inventory details including ID, Name, Category, and Stock[cite: 20, 21]."""
    if not inventory:
        print("\nInventory is currently empty.")
        return

    print("\n" + "="*60)
    print(f"{'Product ID':<12} {'Product Name':<20} {'Category':<15} {'Stock Status':<10}")
    print("-" * 60)
    for p_id, d in inventory.items():
        print(f"{p_id:<12} {d['name']:<20} {d['category']:<15} {d['quantity']:<10}")
    print("="*60)

def main():
    """Main program loop."""
    inventory = {}
    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            add_product(inventory)
        elif choice == '2':
            update_stock(inventory)
        elif choice == '3':
            search_product(inventory)
        elif choice == '4':
            display_inventory(inventory)
        elif choice == '5':
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice, please select 1-5.")

if __name__ == "__main__":
    main()