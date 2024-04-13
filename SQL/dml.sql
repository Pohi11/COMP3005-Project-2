DO $$DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DELETE FROM ' || quote_ident(r.tablename);
    END LOOP;
END$$;

BEGIN;

-- Resetting the sequence for clear starting points in case of repeated tests
ALTER SEQUENCE trainers_trainerid_seq RESTART WITH 1;
ALTER SEQUENCE rooms_roomid_seq RESTART WITH 1;
ALTER SEQUENCE classes_classid_seq RESTART WITH 1;
ALTER SEQUENCE members_memberid_seq RESTART WITH 1;

-- Insert Members
INSERT INTO Members (FirstName, LastName, Email, Password, HealthMetrics) VALUES
('John', 'Doe', 'john.doe@example.com', 'password123', '{"weight": 80, "height": 180, "body_fat": 15, "fitness_goals": {"goal_weight": 75, "goal_body_fat": 12}}'),
('Jane', 'Smith', 'jane.smith@example.com', 'password123', '{"weight": 65, "height": 165, "body_fat": 25, "fitness_goals": {"goal_weight": 60, "goal_body_fat": 20}}'),
('Alice', 'Johnson', 'alice.johnson@example.com', 'password123', '{"weight": 70, "height": 170, "body_fat": 30, "fitness_goals": {"goal_weight": 65, "goal_body_fat": 25}}'),
('Bob', 'Brown', 'bob.brown@example.com', 'password123', '{"weight": 90, "height": 175, "body_fat": 20, "fitness_goals": {"goal_weight": 85, "goal_body_fat": 15}}'),
('Emma', 'Williams', 'emma.williams@example.com', 'password123', '{"weight": 55, "height": 160, "body_fat": 22, "fitness_goals": {"goal_weight": 50, "goal_body_fat": 18}}');

-- Display all MemberIDs for verification
SELECT MemberID FROM Members;

-- Insert Trainers
INSERT INTO Trainers (FirstName, LastName, Specialization) VALUES
('Dave', 'Roberts', 'Yoga'),
('Lucy', 'Taylor', 'Weightlifting'),
('Mark', 'Wilson', 'Cardio'),
('Chloe', 'Davis', 'Pilates'),
('Nina', 'Garcia', 'Crossfit');

-- Insert Rooms
INSERT INTO Rooms (RoomName, Capacity) VALUES
('Aerobics Room', 20),
('Yoga Studio', 15),
('Weight Room', 30),
('Cardio Zone', 25),
('Pilates Studio', 10);

-- Insert Classes ensuring TrainerID and RoomID are available
INSERT INTO Classes (ClassName, TrainerID, RoomID, Schedule, Status) VALUES
('Morning Yoga', 1, 1, '2024-05-01 08:00:00', 'Open'),
('Evening Weightlifting', 2, 2, '2024-05-01 19:00:00', 'Open'),
('Cardio Blast', 3, 3, '2024-05-02 09:00:00', 'Open'),
('Pilates Beginner', 4, 4, '2024-05-02 10:30:00', 'Open'),
('Crossfit Challenge', 5, 5, '2024-05-02 18:00:00', 'Open');

-- Insert Personal Training Sessions ensuring MemberID and TrainerID are available
INSERT INTO PersonalTrainingSessions (MemberID, TrainerID, Date, Time, Status) VALUES
(1, 1, '2024-05-01', '10:00', 'Scheduled'),
(2, 2, '2024-05-02', '11:00', 'Scheduled'),
(3, 3, '2024-05-03', '12:00', 'Scheduled'),
(4, 4, '2024-05-04', '13:00', 'Scheduled'),
(5, 5, '2024-05-05', '14:00', 'Scheduled');

-- Insert Equipment
INSERT INTO Equipment (EquipmentName, MaintenanceSchedule, LastMaintenanceDate, EquipmentStatus) VALUES
('Treadmill 1', '2024-12-01', '2024-04-01', 'Available'),
('Elliptical 2', '2024-12-02', '2024-04-02', 'Maintenance'),
('Rowing Machine 3', '2024-12-03', '2024-04-03', 'Available'),
('Exercise Bike 4', '2024-12-04', '2024-04-04', 'Available'),
('Stair Climber 5', '2024-12-05', '2024-04-05', 'Maintenance');

-- Insert Member Classes ensuring MemberID and ClassID are available
INSERT INTO MemberClasses (MemberID, ClassID) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5);

-- Insert Billing ensuring MemberID is available
INSERT INTO Billing (MemberID, Amount, Description, BillDate, Paid) VALUES
(1, 50.00, 'Monthly Membership Fee', '2024-05-01', FALSE),
(2, 150.00, 'Personal Training Package', '2024-05-01', TRUE),
(3, 100.00, 'Annual Gym Access', '2024-05-01', FALSE),
(4, 75.00, 'Six-month Yoga Pass', '2024-05-01', TRUE),
(5, 80.00, 'Pilates Class Fees', '2024-05-01', FALSE);

-- Commit the transaction
COMMIT;
