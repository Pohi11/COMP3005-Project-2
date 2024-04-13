#Jonathan Dorfman
#101241425
#COMP 3005 PROJECT 2
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import AsIs
import json

def get_db_connection():
    return psycopg2.connect(
        dbname="HealthClubDB",
        user="postgres",
        password="postgres",
        host="localhost"
    )

def register_user():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    
    # Collect health metrics individually
    weight = input("Enter weight (kg): ")
    height = input("Enter height (cm): ")
    body_fat = input("Enter body fat percentage (%): ")
    goal_weight = input("Enter goal weight (kg): ")
    goal_body_fat = input("Enter goal body fat percentage (%): ")

    # Construct the health_metrics dictionary
    health_metrics = {
        "weight": weight,
        "height": height,
        "body_fat": body_fat,
        "fitness_goals": {
            "goal_weight": goal_weight,
            "goal_body_fat": goal_body_fat
        }
    }

    # Convert the dictionary to a JSON string
    health_metrics_json = json.dumps(health_metrics)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Members (FirstName, LastName, Email, Password, HealthMetrics) 
                VALUES (%s, %s, %s, %s, %s) RETURNING MemberID;
            """, (first_name, last_name, email, password, health_metrics_json))
            member_id = cur.fetchone()[0]
            conn.commit()
            print(f"User registered successfully with MemberID: {member_id}")

def update_user_profile():
    member_id = int(input("Enter your Member ID: "))
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    
    # Asking for individual health metrics instead of JSON input
    weight = input("Enter your weight (kg): ")
    height = input("Enter your height (cm): ")
    body_fat = input("Enter your body fat percentage (%): ")
    goal_weight = input("Enter your goal weight (kg): ")
    goal_body_fat = input("Enter your goal body fat percentage (%): ")

    # Creating a dictionary for health metrics
    health_metrics = {
        "weight": weight,
        "height": height,
        "body_fat": body_fat,
        "fitness_goals": {
            "goal_weight": goal_weight,
            "goal_body_fat": goal_body_fat
        }
    }

    # Converting the dictionary to a JSON string
    health_metrics_json = json.dumps(health_metrics)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Members 
                SET FirstName = %s, LastName = %s, Email = %s, HealthMetrics = %s
                WHERE MemberID = %s;
            """, (first_name, last_name, email, health_metrics_json, member_id))
            conn.commit()
            print("Profile updated successfully.")
            
def view_dashboard():
    member_id = int(input("Enter your Member ID: "))

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Fetch member profile and health metrics
            cur.execute("""
                SELECT FirstName, LastName, Email, HealthMetrics FROM Members WHERE MemberID = %s;
            """, (member_id,))
            profile = cur.fetchone()
            if profile:
                print(f"\nProfile for {profile[0]} {profile[1]}:")
                print(f"Email: {profile[2]}")
                health_metrics = profile[3]
                
                print("Health Metrics:")
                print(f"  Height: {health_metrics.get('height')} cm")
                print(f"  Weight: {health_metrics.get('weight')} kg")
                print(f"  Body Fat: {health_metrics.get('body_fat')}%")
                print("  Fitness Goals:")
                if health_metrics.get('fitness_goals'):
                    print(f"    Goal Weight: {health_metrics['fitness_goals'].get('goal_weight')} kg")
                    print(f"    Goal Body Fat: {health_metrics['fitness_goals'].get('goal_body_fat')}%")
            else:
                print("No profile found.")
            
            # Fetch upcoming personal training sessions
            cur.execute("""
                SELECT s.SessionID, s.Date, s.Time, t.FirstName, t.LastName
                FROM PersonalTrainingSessions s
                JOIN Trainers t ON s.TrainerID = t.TrainerID
                WHERE s.MemberID = %s AND s.Date >= CURRENT_DATE;
            """, (member_id,))
            sessions = cur.fetchall()
            if sessions:
                print("\nUpcoming Personal Training Sessions:")
                for session in sessions:
                    date_str = session[1].strftime('%Y-%m-%d')
                    time_str = session[2].strftime('%H:%M')
                    print(f"  Session ID: {session[0]}, Date: {date_str}, Time: {time_str}, Trainer: {session[3]} {session[4]}")
            else:
                print("No upcoming personal training sessions found.")

            # Fetch upcoming classes
            cur.execute("""
                SELECT c.ClassID, c.ClassName, c.Schedule, t.FirstName, t.LastName
                FROM Classes c
                JOIN MemberClasses mc ON c.ClassID = mc.ClassID
                JOIN Trainers t ON c.TrainerID = t.TrainerID
                WHERE mc.MemberID = %s AND c.Schedule >= CURRENT_TIMESTAMP
                ORDER BY c.Schedule;
            """, (member_id,))
            classes = cur.fetchall()
            if classes:
                print("\nUpcoming Classes:")
                for cls in classes:
                    schedule_str = cls[2].strftime('%Y-%m-%d %H:%M')
                    print(f"  Class ID: {cls[0]}, Name: {cls[1]}, Schedule: {schedule_str}, Trainer: {cls[3]} {cls[4]}")
            else:
                print("No upcoming classes found.")


def schedule_training_session():
    # Display available trainers
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT TrainerID, FirstName, LastName, Specialization FROM Trainers;
            """)
            trainers = cur.fetchall()
            print("\nAvailable Trainers:")
            for trainer in trainers:
                print(f"Trainer ID: {trainer[0]}, Name: {trainer[1]} {trainer[2]}, Specialization: {trainer[3]}")

    # Prompt for inputs
    member_id = int(input("\nEnter your Member ID: "))
    trainer_id = int(input("Choose Trainer ID from the list above: "))
    date = input("Enter Date (YYYY-MM-DD): ")

    # Display booked times for the chosen trainer on the selected date
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT Time FROM PersonalTrainingSessions
                WHERE TrainerID = %s AND Date = %s;
            """, (trainer_id, date))
            sessions = cur.fetchall()
            if sessions:
                print(f"\nTimes already booked for Trainer {trainer_id} on {date}:")
                for session in sessions:
                    print(f" - {session[0]}")
            else:
                print(f"\nNo times booked for Trainer {trainer_id} on {date}. They are available all day.")

    # Continue with booking a new session
    time = input("Enter Time (HH:MM) for the new session: ")

    # Check if the selected time is already booked
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM PersonalTrainingSessions
                WHERE TrainerID = %s AND Date = %s AND Time = %s;
            """, (trainer_id, date, time))
            if cur.fetchone():
                print("Trainer is not available at the selected time. Please choose another time.")
                return

            # Schedule the new session
            cur.execute("""
                INSERT INTO PersonalTrainingSessions (MemberID, TrainerID, Date, Time) 
                VALUES (%s, %s, %s, %s) RETURNING SessionID;
            """, (member_id, trainer_id, date, time))
            session_id = cur.fetchone()[0]
            conn.commit()
            print(f"Session scheduled successfully with SessionID: {session_id}")


def set_trainer_availability():
    trainer_id = int(input("Enter your Trainer ID: "))
    date = input("Enter Date (YYYY-MM-DD) for availability: ")
    time = input("Enter Time (HH:MM) for availability: ")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Inserting a dummy session with MemberID NULL to indicate availability
            cur.execute("""
                INSERT INTO PersonalTrainingSessions (TrainerID, Date, Time, Status) 
                VALUES (%s, %s, %s, 'Available')
                RETURNING SessionID;
            """, (trainer_id, date, time))
            session_id = cur.fetchone()[0]
            conn.commit()
            print(f"Availability set successfully with SessionID: {session_id}")
            
def view_member_profile():
    search_name = input("Enter member's name to search: ")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT MemberID, FirstName, LastName, Email, HealthMetrics 
                FROM Members
                WHERE FirstName ILIKE %s OR LastName ILIKE %s;
            """, ('%' + search_name + '%', '%' + search_name + '%'))
            profiles = cur.fetchall()

            if not profiles:
                print("No profiles found for the given name.")
                return

            print("\nMember Profiles:")
            for profile in profiles:
                member_id, first_name, last_name, email, health_metrics = profile

                # Check if health_metrics is already a dictionary
                if isinstance(health_metrics, str):
                    try:
                        health_metrics = json.loads(health_metrics)
                    except json.JSONDecodeError:
                        health_metrics = {}  # Default to empty dict if parsing fails

                print(f"\nMember ID: {member_id}")
                print(f"Name: {first_name} {last_name}")
                print(f"Email: {email}")
                if health_metrics:
                    print("Health Metrics:")
                    print(f"  Weight: {health_metrics.get('weight', 'N/A')} kg")
                    print(f"  Height: {health_metrics.get('height', 'N/A')} cm")
                    print(f"  Body Fat: {health_metrics.get('body_fat', 'N/A')}%")
                    if 'fitness_goals' in health_metrics:
                        print("  Fitness Goals:")
                        print(f"    Goal Weight: {health_metrics['fitness_goals'].get('goal_weight', 'N/A')} kg")
                        print(f"    Goal Body Fat: {health_metrics['fitness_goals'].get('goal_body_fat', 'N/A')}%")
                else:
                    print("  No health metrics available.")

                    
def manage_room_booking():
    print("Current Room Bookings:")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ClassID, RoomID, Schedule FROM Classes;
            """)
            classes = cur.fetchall()
            for cls in classes:
                print(f"Class ID: {cls[0]}, Room ID: {cls[1]}, Schedule: {cls[2]}")

    action = input("\nEnter action (add, update, delete): ").lower()
    class_id = int(input("Enter Class ID: "))

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if action == 'add':
                room_id = int(input("Enter Room ID: "))
                schedule = input("Enter Schedule (YYYY-MM-DD HH:MM): ")
                cur.execute("""
                    INSERT INTO Classes (ClassID, RoomID, Schedule) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (ClassID) DO NOTHING;
                """, (class_id, room_id, schedule))
                print("Room booking added.")
            
            elif action == 'update':
                room_id = int(input("Enter new Room ID: "))
                schedule = input("Enter new Schedule (YYYY-MM-DD HH:MM): ")
                cur.execute("""
                    UPDATE Classes
                    SET RoomID = %s, Schedule = %s
                    WHERE ClassID = %s;
                """, (room_id, schedule, class_id))
                print("Room booking updated.")

            elif action == 'delete':
                cur.execute("""
                    DELETE FROM Classes WHERE ClassID = %s;
                """, (class_id,))
                print("Room booking deleted.")

            
def monitor_equipment_maintenance():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EquipmentID, EquipmentName, MaintenanceSchedule, EquipmentStatus
                FROM Equipment;
            """)
            equipments = cur.fetchall()
            print("\nCurrent Equipment Status:")
            for eq in equipments:
                print(f"ID: {eq[0]}, Name: {eq[1]}, Next Maintenance: {eq[2]}, Status: {eq[3]}")

    equipment_id = int(input("\nEnter Equipment ID to update: "))
    new_maintenance_date = input("Enter new Maintenance Date (YYYY-MM-DD): ")
    equipment_status = input("Enter Equipment Status (Available/Maintenance): ")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Equipment
                SET MaintenanceSchedule = %s, EquipmentStatus = %s
                WHERE EquipmentID = %s;
            """, (new_maintenance_date, equipment_status, equipment_id))
            conn.commit()
            print(f"Equipment {equipment_id} maintenance updated.")


def update_class_schedule():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ClassID, ClassName, Schedule, Status
                FROM Classes;
            """)
            classes = cur.fetchall()
            print("\nCurrent Class Schedules:")
            for cl in classes:
                print(f"ID: {cl[0]}, Name: {cl[1]}, Schedule: {cl[2]}, Status: {cl[3]}")

    class_id = int(input("\nEnter Class ID to update: "))
    new_schedule = input("Enter new Schedule (YYYY-MM-DD HH:MM): ")
    status = input("Enter new Status (Open/Closed): ")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE Classes
                SET Schedule = %s, Status = %s
                WHERE ClassID = %s;
            """, (new_schedule, status, class_id))
            conn.commit()
            print(f"Class {class_id} schedule updated to {new_schedule} and status to {status}.")

def process_payment():
    member_id = int(input("Enter Member ID: "))

    # List unpaid bills
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT BillID, Amount, Description, BillDate FROM Billing
                WHERE MemberID = %s AND Paid = FALSE;
            """, (member_id,))
            bills = cur.fetchall()
            if bills:
                print("\nUnpaid Bills:")
                for bill in bills:
                    print(f"Bill ID: {bill[0]}, Amount: {bill[1]}, Description: {bill[2]}, Date: {bill[3]}")
                bill_choice = input("Enter Bill ID to pay or type 'new' to create a new bill: ")
            else:
                print("No unpaid bills found.")
                bill_choice = 'new'

            if bill_choice.lower() != 'new':
                # Process payment for an existing bill
                cur.execute("""
                    UPDATE Billing
                    SET Paid = TRUE
                    WHERE BillID = %s;
                """, (bill_choice,))
                conn.commit()
                print(f"Payment for BillID {bill_choice} processed successfully.")
            else:
                # Create a new bill
                amount = float(input("Enter Billing Amount: "))
                description = input("Enter Payment Description: ")
                cur.execute("""
                    INSERT INTO Billing (MemberID, Amount, Description, BillDate, Paid)
                    VALUES (%s, %s, %s, CURRENT_DATE, FALSE)
                    RETURNING BillID;
                """, (member_id, amount, description))
                bill_id = cur.fetchone()[0]
                print(f"Bill created with BillID: {bill_id}")

                # Ask for payment confirmation
                pay_confirmation = input("Confirm payment? (yes/no): ").lower()
                if pay_confirmation == "yes":
                    cur.execute("""
                        UPDATE Billing
                        SET Paid = TRUE
                        WHERE BillID = %s;
                    """, (bill_id,))
                    conn.commit()
                    print(f"Payment for BillID {bill_id} processed successfully.")
                else:
                    print("Payment cancelled.")


def create_new_class():
    class_name = input("Enter class name: ")
    trainer_id = int(input("Enter Trainer ID: "))
    room_id = int(input("Enter Room ID: "))
    schedule = input("Enter Schedule (YYYY-MM-DD HH:MM): ")
    status = input("Enter class status (Open/Closed): ")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Classes (ClassName, TrainerID, RoomID, Schedule, Status)
                VALUES (%s, %s, %s, %s, %s) RETURNING ClassID;
            """, (class_name, trainer_id, room_id, schedule, status))
            class_id = cur.fetchone()[0]
            conn.commit()
            print(f"New class created successfully with ClassID: {class_id}")

def register_for_class():
    print("Available Classes:")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ClassID, ClassName, Status FROM Classes WHERE Status = 'Open';
            """)
            classes = cur.fetchall()
            for cls in classes:
                print(f"Class ID: {cls[0]}, Name: {cls[1]}, Status: {cls[2]}")

    member_id = int(input("\nEnter your Member ID: "))
    class_id = int(input("Enter Class ID to register for: "))

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if the class exists and is open for registration
            cur.execute("""
                SELECT c.ClassID, c.Status, r.Capacity, COUNT(mc.MemberID) as registered_members
                FROM Classes c
                JOIN Rooms r ON c.RoomID = r.RoomID
                LEFT JOIN MemberClasses mc ON c.ClassID = mc.ClassID
                WHERE c.ClassID = %s
                GROUP BY c.ClassID, r.Capacity;
            """, (class_id,))
            class_info = cur.fetchone()
            
            if class_info is None:
                print("Class does not exist.")
                return
            
            if class_info[1] != 'Open':
                print("Registration for this class is not open.")
                return
            
            # Check if there's available space in the class
            if class_info[3] >= class_info[2]:  # if registered_members >= Capacity
                print("Class is full.")
                return
            
            # Register the member for the class
            cur.execute("""
                INSERT INTO MemberClasses (MemberID, ClassID)
                VALUES (%s, %s)
                ON CONFLICT (MemberID, ClassID) DO NOTHING;
            """, (member_id, class_id))
            conn.commit()
            print("You've been successfully registered for the class.")

def create_trainer():
    first_name = input("Enter trainer's first name: ")
    last_name = input("Enter trainer's last name: ")
    specialization = input("Enter trainer's specialization: ")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Trainers (FirstName, LastName, Specialization)
                VALUES (%s, %s, %s) RETURNING TrainerID;
            """, (first_name, last_name, specialization))
            trainer_id = cur.fetchone()[0]
            conn.commit()
            print(f"New trainer created successfully with TrainerID: {trainer_id}")
def view_classes():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.ClassID, c.ClassName, c.Schedule, c.Status, t.FirstName, t.LastName, r.RoomName
                FROM Classes c
                JOIN Trainers t ON c.TrainerID = t.TrainerID
                JOIN Rooms r ON c.RoomID = r.RoomID
                ORDER BY c.Schedule;
            """)
            classes = cur.fetchall()
            if classes:
                print("\nAvailable Classes:")
                for cls in classes:
                    print(f"Class ID: {cls[0]}, Name: {cls[1]}, Schedule: {cls[2].strftime('%Y-%m-%d %H:%M')}, Status: {cls[3]}, Trainer: {cls[4]} {cls[5]}, Room: {cls[6]}")
            else:
                print("No classes available.")

def main():
    while True:
        print("\nWelcome to the Health and Fitness Club Management System")
        print("Please choose an option:")
        print("1. Member Functions")
        print("2. Trainer Functions")
        print("3. Administrative Staff Functions")
        print("4. Exit")
        user_choice = input("Enter your choice: ")

        if user_choice == "1":
            while True:
                print("\nMember Functions:")
                print("1. Register User")
                print("2. Update User Profile")
                print("3. View Dashboard")
                print("4. Schedule Training Session")
                print("5. Register for Class")
                print("6. View Classes")  # New option to view available classes
                print("7. Back")
                member_choice = input("Enter your choice: ")

                if member_choice == "1":
                    register_user()
                elif member_choice == "2":
                    update_user_profile()
                elif member_choice == "3":
                    view_dashboard()
                elif member_choice == "4":
                    schedule_training_session()
                elif member_choice == "5":
                    register_for_class()
                elif member_choice == "6":
                    view_classes()  # Call to the new function to view classes
                elif member_choice == "7":
                    break
                else:
                    print("Invalid option, please try again.")

        elif user_choice == "2":
            while True:
                print("\nTrainer Functions:")
                print("1. Set Availability")
                print("2. View Member Profile")
                print("3. Back")
                trainer_choice = input("Enter your choice: ")

                if trainer_choice == "1":
                    set_trainer_availability()
                elif trainer_choice == "2":
                    view_member_profile()
                elif trainer_choice == "3":
                    break
                else:
                    print("Invalid option, please try again.")

        elif user_choice == "3":
            while True:
                print("\nAdministrative Staff Functions:")
                print("1. Monitor Equipment Maintenance")
                print("2. Update Class Schedule")
                print("3. Process Payment")
                print("4. Manage Room Booking")
                print("5. Create New Class")
                print("6. Register New Trainer")  # New option to create a trainer
                print("7. Back")
                admin_choice = input("Enter your choice: ")

                if admin_choice == "1":
                    monitor_equipment_maintenance()
                elif admin_choice == "2":
                    update_class_schedule()
                elif admin_choice == "3":
                    process_payment()
                elif admin_choice == "4":
                    manage_room_booking()
                elif admin_choice == "5":
                    create_new_class()  # Call the function to create a new class
                elif admin_choice == "6":
                    create_trainer()  
                elif admin_choice == "7":
                    break
                else:
                    print("Invalid option, please try again.")

        elif user_choice == "4":
            print("Exiting the system. Goodbye!")
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main()
