-- Members Table
CREATE TABLE Members (
    MemberID SERIAL PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    HealthMetrics JSONB -- For storing health metrics like weight, goals, etc.
);

-- Trainers Table
CREATE TABLE Trainers (
    TrainerID SERIAL PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Specialization VARCHAR(255)
);

-- Rooms Table
CREATE TABLE Rooms (
    RoomID SERIAL PRIMARY KEY,
    RoomName VARCHAR(255) NOT NULL,
    Capacity INT CHECK (Capacity > 0) NOT NULL
);

-- Classes Table
CREATE TABLE Classes (
    ClassID SERIAL PRIMARY KEY,
    ClassName VARCHAR(255) NOT NULL,
    TrainerID INT NOT NULL,
    RoomID INT NOT NULL,
    Schedule TIMESTAMP NOT NULL,
    Status VARCHAR(255) DEFAULT 'Open', -- Added status field
    FOREIGN KEY (TrainerID) REFERENCES Trainers(TrainerID),
    FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID)
);

-- Personal Training Sessions Table
CREATE TABLE PersonalTrainingSessions (
    SessionID SERIAL PRIMARY KEY,
    MemberID INT,
    TrainerID INT NOT NULL,
    Date DATE NOT NULL,
    Time TIME NOT NULL,
    Status VARCHAR(255) DEFAULT 'Scheduled', -- Added status field
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
    FOREIGN KEY (TrainerID) REFERENCES Trainers(TrainerID)
);

-- Equipment Table
CREATE TABLE Equipment (
    EquipmentID SERIAL PRIMARY KEY,
    EquipmentName VARCHAR(255) NOT NULL,
    MaintenanceSchedule DATE NOT NULL,
    LastMaintenanceDate DATE, -- Added last maintenance date field
    EquipmentStatus VARCHAR(255) DEFAULT 'Available' -- Added equipment status field
);

-- Member Classes Table (Association Table for Members and Classes)
CREATE TABLE MemberClasses (
    MemberID INT NOT NULL,
    ClassID INT NOT NULL,
    PRIMARY KEY (MemberID, ClassID),
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID),
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
);

-- Billing Table
CREATE TABLE Billing (
    BillID SERIAL PRIMARY KEY,
    MemberID INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    Description TEXT,
    BillDate DATE NOT NULL,
    Paid BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);
