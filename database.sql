CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(15),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Staff (
    StaffID INTEGER PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Role VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(15),
    Salary DECIMAL(10, 2) NOT NULL,
    HireDate DATE NOT NULL
);

CREATE TABLE Suppliers (
    SupplierID INTEGER PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    ContactName VARCHAR(50),
    ContactEmail VARCHAR(100),
    PhoneNumber VARCHAR(15),
    Address TEXT
);

CREATE TABLE Ingredients (
    IngredientID INTEGER PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Unit VARCHAR(50) NOT NULL,
    SupplierID INTEGER,
    PricePerUnit DECIMAL(10, 2) NOT NULL,
    StockQuantity INT DEFAULT 0,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE SET NULL
);

CREATE TABLE Menus (
    MenuID INTEGER PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Description TEXT
);

CREATE TABLE MenuItems (
    MenuItemID INTEGER PRIMARY KEY,
    MenuID INTEGER NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Description TEXT,
    Price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (MenuID) REFERENCES Menus(MenuID) ON DELETE CASCADE
);

CREATE TABLE MenuIngredients (
    MenuItemID INTEGER NOT NULL,
    IngredientID INTEGER NOT NULL,
    Quantity DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (MenuItemID, IngredientID),
    FOREIGN KEY (MenuItemID) REFERENCES MenuItems(MenuItemID) ON DELETE CASCADE,
    FOREIGN KEY (IngredientID) REFERENCES Ingredients(IngredientID) ON DELETE CASCADE
);

CREATE TABLE Reservations (
    ReservationID INTEGER PRIMARY KEY,
    CustomerID INTEGER NOT NULL,
    ReservationDateTime DATETIME NOT NULL,
    NumberOfGuests INTEGER NOT NULL,
    SpecialRequests TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
);

CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    StaffID INTEGER,
    MenuID INTEGER,
    OrderDateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10, 2),
    PaymentMethod VARCHAR(50),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE SET NULL,
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID) ON DELETE SET NULL
);

CREATE TABLE OrderDetails (
    OrderDetailID INTEGER PRIMARY KEY,
    OrderID INTEGER NOT NULL,
    MenuItemID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (MenuItemID) REFERENCES MenuItems(MenuItemID) ON DELETE CASCADE
);

CREATE TABLE Payments (
    PaymentID INTEGER PRIMARY KEY,
    OrderID INTEGER NOT NULL,
    PaymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentMethod VARCHAR(50) NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE
);

INSERT INTO Customers (FirstName, LastName, Email, PhoneNumber) VALUES
('John', 'Doe', 'john.doe@example.com', '1234567890'),
('Jane', 'Smith', 'jane.smith@example.com', '9876543210'),
('Alice', 'Johnson', 'alice.johnson@example.com', '4567891230'),
('Bob', 'Brown', 'bob.brown@example.com', '6543217890'),
('Charlie', 'Davis', 'charlie.davis@example.com', '7891234560');

INSERT INTO Staff (FirstName, LastName, Role, Email, PhoneNumber, Salary, HireDate) VALUES
('Emily', 'White', 'Manager', 'emily.white@example.com', '3216549870', 55000.00, '2022-01-15'),
('Michael', 'Green', 'Chef', 'michael.green@example.com', '1597534862', 45000.00, '2022-03-01'),
('Sarah', 'Black', 'Waiter', 'sarah.black@example.com', '7531598462', 30000.00, '2023-05-20'),
('David', 'Wilson', 'Bartender', 'david.wilson@example.com', '9513574862', 25000.00, '2021-11-10'),
('Laura', 'Taylor', 'Host', 'laura.taylor@example.com', '1594867532', 20000.00, '2023-07-05');

INSERT INTO Suppliers (Name, ContactName, ContactEmail, PhoneNumber, Address) VALUES
('Fresh Produce Co.', 'Tom Rogers', 'tom.rogers@example.com', '1231231234', '123 Farm Lane, Springfield'),
('Beverage Distributors', 'Nancy Miles', 'nancy.miles@example.com', '2342342345', '456 Drink St, Hometown'),
('Meat Suppliers Inc.', 'Gary Cook', 'gary.cook@example.com', '3453453456', '789 Meat Rd, Cityville'),
('Seafood Delights', 'Diane Fisher', 'diane.fisher@example.com', '4564564567', '101 Ocean Ave, Seaside'),
('Bakery Goods Co.', 'Paul Baker', 'paul.baker@example.com', '5675675678', '202 Bread Blvd, Crustown');

INSERT INTO Ingredients (Name, Unit, SupplierID, PricePerUnit, StockQuantity) VALUES
('Tomatoes', 'kg', 1, 2.50, 100),
('Beef', 'kg', 3, 15.00, 50),
('Salmon', 'kg', 4, 20.00, 30),
('Flour', 'kg', 5, 1.20, 200),
('Cheese', 'kg', 1, 5.00, 75);

INSERT INTO Menus (Name, Description) VALUES
('Breakfast Menu', 'Delicious breakfast options to start your day'),
('Lunch Menu', 'Tasty and satisfying lunch selections'),
('Dinner Menu', 'Hearty and gourmet dinner dishes'),
('Kids Menu', 'Fun and delicious meals for kids'),
('Dessert Menu', 'Sweet treats to end your meal');

INSERT INTO MenuItems (MenuID, Name, Description, Price) VALUES
(1, 'Pancakes', 'Fluffy pancakes with syrup', 5.99),
(2, 'Burger', 'Juicy beef burger with cheese', 9.99),
(3, 'Grilled Salmon', 'Fresh salmon with herbs', 14.99),
(4, 'Chicken Nuggets', 'Crispy chicken nuggets', 6.49),
(5, 'Chocolate Cake', 'Rich chocolate dessert', 4.99);

INSERT INTO MenuIngredients (MenuItemID, IngredientID, Quantity) VALUES
(1, 4, 0.2),
(2, 2, 0.25),
(3, 3, 0.3),
(4, 2, 0.15),
(5, 5, 0.1);

INSERT INTO Reservations (CustomerID, ReservationDateTime, NumberOfGuests, SpecialRequests) VALUES
(1, '2025-01-13 08:00:00', 2, 'Window seat'),
(2, '2025-01-13 12:30:00', 4, 'Birthday party'),
(3, '2025-01-13 19:00:00', 3, 'Vegetarian menu'),
(4, '2025-01-14 07:30:00', 1, 'Quiet corner'),
(5, '2025-01-14 18:00:00', 5, 'Anniversary celebration');

INSERT INTO Orders (CustomerID, StaffID, TotalAmount, MenuID, PaymentMethod)
VALUES 
    (1, 1, 19.98, 2, 'Cash'), 
    (3, 3, 29.98, 3, 'Card'), 
    (4, 4, 12.98, 4, 'Card'),
    (5, 5, 9.98, 5, 'Cash'), 
    (1, 2, 44.97, 3, 'Cash');

INSERT INTO OrderDetails (OrderID,MenuItemID,Quantity,Price)
VALUES 
    (1,2,2,9.99),
    (2,3,2,14.99),
    (3,4,2,6.49),
    (4,5,2,4.99),
    (5,3,3,14.99);

INSERT INTO Payments (OrderID,Amount,PaymentMethod)
VALUES 
    (1,19.98,'Cash'),
    (2,29.98,'Card'),
    (3,12.98,'Card'),
    (4,9.98,'Cash'),
    (5,44.97,'Cash');

CREATE TRIGGER after_insert_orders
AFTER INSERT ON Orders
FOR EACH ROW
BEGIN
    INSERT INTO OrderDetails (OrderID, MenuItemID, Quantity, Price)
    VALUES (
        NEW.OrderID,
        NEW.MenuID,
        CAST(NEW.TotalAmount / (SELECT Price FROM MenuItems WHERE MenuItemID = NEW.MenuID) AS INTEGER),
        (SELECT Price FROM MenuItems WHERE MenuItemID = NEW.MenuID)
    );
    
    INSERT INTO Payments (OrderID, Amount, PaymentMethod)
    VALUES (NEW.OrderID, NEW.TotalAmount, NEW.PaymentMethod);
END;

CREATE TRIGGER update_stock_quantity_after_order
AFTER INSERT ON OrderDetails
FOR EACH ROW
BEGIN
    UPDATE Ingredients
    SET StockQuantity = StockQuantity - (
        SELECT Quantity * NEW.Quantity
        FROM MenuIngredients
        WHERE MenuIngredients.IngredientID = Ingredients.IngredientID
          AND MenuIngredients.MenuItemID = NEW.MenuItemID
    )
    WHERE EXISTS (
        SELECT 1
        FROM MenuIngredients
        WHERE MenuIngredients.IngredientID = Ingredients.IngredientID
          AND MenuIngredients.MenuItemID = NEW.MenuItemID
    );
END;
