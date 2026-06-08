import math
from datetime import datetime

# 1. ENCAPSULATION: Using a class to bundle data and methods 
class Vehicle:
    def __init__(self, plate_number, vehicle_type):
        self.__plate_number = plate_number  # Private attribute
        self.__vehicle_type = vehicle_type
        self.__entry_time = datetime.now()

    def get_plate(self):
        return self.__plate_number

    def get_info(self):
        return f"Type: {self.__vehicle_type} | Plate: {self.__plate_number} | Entered: {self.__entry_time.strftime('%H:%M:%S')}"

# 2. INHERITANCE: Car and Bike inherit from Vehicle 
class Car(Vehicle):
    def __init__(self, plate_number):
        super().__init__(plate_number, "Car")

class Bike(Vehicle):
    def __init__(self, plate_number):
        super().__init__(plate_number, "Bike")

# 3. POLYMORPHISM & MANAGEMENT 
class ParkingManager:
    def __init__(self):
        self.parked_vehicles = {} # Stores plate: vehicle_object
        self.total_revenue = 0.0
        self.hourly_rate = 10.0 # Flat rate for simulation

    def register_entry(self):
        # EXCEPTION HANDLING & INPUT HANDLING [cite: 12, 19]
        try:
            v_type = input("Enter vehicle type (1 for Car, 2 for Bike): ")
            plate = input("Enter Plate Number: ").strip().upper()
            
            if not plate:
                raise ValueError("Plate number cannot be empty.")
            if plate in self.parked_vehicles:
                print("Error: Vehicle already parked.")
                return

            if v_type == '1':
                self.parked_vehicles[plate] = Car(plate)
            elif v_type == '2':
                self.parked_vehicles[plate] = Bike(plate)
            else:
                print("Invalid type selected.")
                return
            
            print(f"Vehicle {plate} registered successfully.")
        except Exception as e:
            print(f"Input Error: {e}")

    def remove_vehicle(self):
        plate = input("Enter Plate Number to exit: ").strip().upper()
        if plate in self.parked_vehicles:
            # Simple revenue logic using Math library 
            # Calculating a fixed 'minimum' fee for demonstration
            fee = math.ceil(self.hourly_rate) 
            self.total_revenue += fee
            del self.parked_vehicles[plate]
            print(f"Vehicle {plate} removed. Fee collected: ${fee}")
        else:
            print("Vehicle not found.")

    def display_vehicles(self):
        if not self.parked_vehicles:
            print("Parking lot is empty.")
        else:
            print("\n--- Currently Parked Vehicles ---")
            for vehicle in self.parked_vehicles.values():
                print(vehicle.get_info())

    def show_revenue(self):
        print(f"Total Revenue Collected Today: ${self.total_revenue:.2f}")

# 4. MENU DRIVEN PROGRAM [cite: 13]
def main():
    manager = ParkingManager()
    while True:
        print("\n--- Smart Parking Management System ---")
        print("1. Register vehicle entry")
        print("2. Remove vehicle (Exit)")
        print("3. Display all parked vehicles")
        print("4. Display total revenue")
        print("5. Exit")
        
        choice = input("Select an option (1-5): ")
        
        if choice == '1': manager.register_entry()
        elif choice == '2': manager.remove_vehicle()
        elif choice == '3': manager.display_vehicles()
        elif choice == '4': manager.show_revenue()
        elif choice == '5': 
            print("Exiting system...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()