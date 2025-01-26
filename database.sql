CREATE TABLE Addresses (
    AddressID INTEGER PRIMARY KEY,
    Street VARCHAR(200) NOT NULL,
    City VARCHAR(100) NOT NULL,
    State VARCHAR(100),
    ZipCode VARCHAR(20),
    Country VARCHAR(100) NOT NULL
);

CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL CHECK (Email LIKE '%@%'),
    PhoneNumber VARCHAR(20) UNIQUE NOT NULL,
    AddressID INTEGER,
    FOREIGN KEY (AddressID) REFERENCES Addresses(AddressID) ON DELETE SET NULL
);

CREATE TABLE Staff (
    StaffID INTEGER PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Role VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL CHECK (Email LIKE '%@%'),
    PhoneNumber VARCHAR(20) UNIQUE NOT NULL,
    Salary DECIMAL(10, 2) NOT NULL,
    HireDate DATE NOT NULL,
    AddressID INTEGER,
    FOREIGN KEY (AddressID) REFERENCES Addresses(AddressID) ON DELETE SET NULL
);

CREATE TABLE Suppliers (
    SupplierID INTEGER PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    ContactName VARCHAR(50),
    ContactEmail VARCHAR(100) UNIQUE NOT NULL CHECK (ContactEmail LIKE '%@%'),
    PhoneNumber VARCHAR(20) UNIQUE NOT NULL,
    AddressID INTEGER,
    FOREIGN KEY (AddressID) REFERENCES Addresses(AddressID) ON DELETE SET NULL
);

CREATE TABLE Ingredients (
    IngredientID INTEGER PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Unit VARCHAR(50) NOT NULL,
    SupplierID INTEGER,
    StockQuantity INT DEFAULT 0,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE SET NULL
);

CREATE TABLE Menus (
    MenuID INTEGER PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Description VARCHAR(500)
);

CREATE TABLE MenuItems (
    MenuItemID INTEGER PRIMARY KEY,
    MenuID INTEGER NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Description VARCHAR(500),
    Price DECIMAL(10, 2) NOT NULL,
    Availability VARCHAR(20) NOT NULL,
    Image BLOB NOT NULL,
    FOREIGN KEY (MenuID) REFERENCES Menus(MenuID) ON DELETE CASCADE
);

CREATE TABLE MenuIngredients (
    MenuItemID INTEGER,
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
    SpecialRequests VARCHAR(500),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE CASCADE
);

CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    StaffID INTEGER,
    MenuID INTEGER,
    OrderDateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10, 2),
    PaymentMethod VARCHAR(50) NOT NULL,
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
    PaymentStatus TEXT DEFAULT 'Pending' CHECK (PaymentStatus IN ('Pending', 'Completed', 'Failed')),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE
);

CREATE TABLE FinancialRecords (
    RecordID INTEGER PRIMARY KEY,
    RecordDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    RecordType VARCHAR(50) NOT NULL CHECK (RecordType IN ('Revenue', 'Expense')),
    Description TEXT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    RelatedID INTEGER, 
    RelatedType VARCHAR(50) 
);

INSERT INTO Addresses (Street, City, State, ZipCode, Country) VALUES
('123 Elm Street', 'Springfield', 'IL', '62701', 'USA'),
('456 Oak Avenue', 'Hometown', 'CA', '90210', 'USA'),
('789 Pine Road', 'Cityville', 'NY', '10001', 'USA'),
('101 Maple Lane', 'Seaside', 'FL', '33101', 'USA'),
('202 Birch Blvd', 'Crustown', 'TX', '73301', 'USA'),
('303 Cedar St', 'Greenville', 'SC', '29601', 'USA'),
('404 Willow Way', 'Fairview', 'OR', '97024', 'USA'),
('505 Aspen Ave', 'Lakeside', 'MI', '49116', 'USA'),
('606 Redwood Rd', 'Hilltop', 'CO', '80021', 'USA'),
('707 Fir Ln', 'Meadowbrook', 'PA', '19046', 'USA'),
('808 Spruce Dr', 'Brookfield', 'CT', '06804', 'USA'),
('909 Cypress Ct', 'Stonebridge', 'GA', '30024', 'USA'),
('1010 Palm St', 'Palmview', 'FL', '33176', 'USA'),
('1111 Pinewood Pl', 'Woodland', 'WA', '98674', 'USA'),
('1212 Cherry Cir', 'Cherryville', 'NJ', '07002', 'USA');

INSERT INTO Customers (FirstName, LastName, Email, PhoneNumber, AddressID) VALUES
('John', 'Cat', 'john@example.com', '1234567890', 1),
('Jane', 'Smith', 'jane@example.com', '9876543210', 2),
('Alice', 'Johnson', 'alice@example.com', '4567891230', 3),
('Bob', 'White', 'bob@example.com', '6543217890', 4),
('Carol', 'Davis', 'carol@example.com', '7891234560', 5);

INSERT INTO Staff (FirstName, LastName, Role, Email, PhoneNumber, Salary, HireDate, AddressID) VALUES
('Emily', 'White', 'Manager', 'emily.white@example.com', '3216549870', 55000.00, '2022-01-15', 6),
('Michael', 'Green', 'Chef', 'michael.green@example.com', '1597534862', 45000.00, '2022-03-01', 7),
('Thomas', 'Black', 'Waiter', 'sarah.black@example.com', '7531598462', 30000.00, '2023-05-20', 8),
('David', 'Wilson', 'Bartender', 'david.wilson@example.com', '9513574862', 25000.00, '2021-11-10', 9),
('Laura', 'Taylor', 'Host', 'laura.taylor@example.com', '1594867532', 20000.00, '2023-07-05', 10);

INSERT INTO Suppliers (Name, ContactName, ContactEmail, PhoneNumber, AddressID) VALUES
('Fresh Produce Co.', 'Tom Rogers', 'tom.rogers@example.com', '1231231234', 1),
('Beverage Distributors', 'Nancy Miles', 'nancy.miles@example.com', '2342342345', 2),
('Meat Suppliers Inc.', 'Gary Cook', 'gary.cook@example.com', '3453453456', 3),
('Seafood Delights', 'Diane Fisher', 'diane.fisher@example.com', '4564564567', 4),
('Bakery Goods Co.', 'Paul Baker', 'paul.baker@example.com', '5675675678', 5);

INSERT INTO Ingredients (Name, Unit, SupplierID, StockQuantity) VALUES
('Tomatoes', 'kg', 1, 100),
('Beef', 'kg', 3, 50),
('Salomon', 'kg', 4, 30),
('Flour', 'kg', 5, 200),
('Cheese', 'kg', 2, 75);

INSERT INTO Menus (Name, Description) VALUES
('Breakfast Menu', 'Delicious breakfast options to start your day'),
('Lunch Menu', 'Tasty and satisfying lunch selections'),
('Dinner Menu', 'Hearty and gourmet dinner dishes'),
('Kids Menu', 'Fun and delicious meals for kids'),
('Dessert Menu', 'Sweet treats to end your meal');

INSERT INTO MenuItems (MenuID, Name, Description, Price, Availability,Image) VALUES
(1,'Margherita Pizza', 'Classic pizza with fresh mozzarella and basil', 5.99,'Unavailable','x'),
(2,'Lasagna Bolognese', 'Traditional layered pasta with meat sauce', 9.99,'Available','x'),
(3,'Grilled Branzino', 'Fresh Mediterranean sea bass with herbs', 14.99,'Available','x'),
(4,'Arancini', 'Crispy risotto balls stuffed with cheese', 6.49,'Available','x'),
(5,'Tiramisu', 'Classic Italian dessert with coffee and mascarpone', 4.99,'Available','x');

INSERT INTO MenuIngredients (IngredientID, Quantity) VALUES
(4, 0.2),
(2, 0.25),
(3, 0.3),
(5, 0.15),
(4, 0.1);

INSERT INTO Reservations (CustomerID, ReservationDateTime, NumberOfGuests, SpecialRequests) VALUES
(1, '2025-01-13 08:00:00', 2, 'Window seat'),
(2, '2025-01-13 12:30:00', 4, 'Birthday party'),
(3, '2025-01-13 19:00:00', 3, 'Vegetarian menu'),
(4, '2025-01-14 07:30:00', 1, 'Quiet corner'),
(5, '2025-01-14 18:00:00', 5, 'Anniversary celebration');

INSERT INTO Orders (CustomerID, StaffID, MenuID, TotalAmount,PaymentMethod) VALUES 
(1, 1, 2, 19.98, 'Cash'), 
(3, 3, 3, 29.98, 'Card'), 
(4, 4, 4, 12.98, 'Card'),
(5, 5, 5,  9.98, 'Cash'), 
(1, 2, 3, 44.97, 'Cash');

INSERT INTO OrderDetails (OrderID, MenuItemID, Quantity, Price) VALUES 
(1, 2, 2, 9.99),
(2, 3, 2, 14.99),
(3, 4, 2, 6.49),
(4, 5, 2, 4.99),
(5, 3, 3, 14.99);

INSERT INTO Payments (OrderID, Amount, PaymentMethod) VALUES 
(1, 19.98, 'Cash'),
(2, 29.98, 'Card'),
(3, 12.98, 'Card'),
(4, 9.98, 'Cash'),
(5, 44.97, 'Cash');

INSERT INTO FinancialRecords (RecordType, Description, Amount, RelatedID, RelatedType) VALUES 
('Revenue', 'Payment received for Order 1', 19.98, 1, 'Order'),
('Revenue', 'Payment received for Order 2', 29.98, 2, 'Order'),
('Revenue', 'Payment received for Order 3', 12.98, 3, 'Order'),
('Revenue', 'Payment received for Order 4', 9.98, 4, 'Order'),
('Revenue', 'Payment received for Order 5', 44.97, 5, 'Order');

-------------------------------------------------------------------------------------

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

CREATE TRIGGER after_insert_payments
AFTER INSERT ON Payments
FOR EACH ROW
BEGIN
    INSERT INTO FinancialRecords (RecordType, Description, Amount, RelatedID, RelatedType)
    VALUES (
        'Revenue', 
        'Payment received for Order ' || NEW.OrderID, 
        NEW.Amount, 
        NEW.OrderID, 
        'Order'
    );
END;

CREATE VIEW OrdersSummary AS
SELECT 
    Orders.OrderID, 
    Customers.FirstName || ' ' || Customers.LastName AS CustomerName, 
    Staff.FirstName || ' ' || Staff.LastName AS StaffName, 
    Orders.OrderDateTime, 
    Orders.TotalAmount, 
    Orders.PaymentMethod
FROM 
    Orders
LEFT JOIN 
    Customers ON Orders.CustomerID = Customers.CustomerID
LEFT JOIN 
    Staff ON Orders.StaffID = Staff.StaffID;

CREATE VIEW IngredientStockLevels AS
SELECT 
    Ingredients.IngredientID, 
    Ingredients.Name AS IngredientName, 
    Ingredients.Unit, 
    Ingredients.StockQuantity, 
    Suppliers.Name AS SupplierName
FROM 
    Ingredients
LEFT JOIN 
    Suppliers ON Ingredients.SupplierID = Suppliers.SupplierID;

CREATE VIEW MenuItemsWithIngredients AS
SELECT 
    MenuItems.MenuItemID, 
    MenuItems.Name AS MenuItemName, 
    MenuItems.Description AS MenuItemDescription, 
    MenuItems.Price, 
    Menus.Name AS MenuName, 
    Ingredients.Name AS IngredientName, 
    MenuIngredients.Quantity
FROM 
    MenuItems
JOIN 
    Menus ON MenuItems.MenuID = Menus.MenuID
JOIN 
    MenuIngredients ON MenuItems.MenuItemID = MenuIngredients.MenuItemID
JOIN 
    Ingredients ON MenuIngredients.IngredientID = Ingredients.IngredientID;

CREATE VIEW FinancialSummary AS
SELECT 
    RecordType, 
    SUM(Amount) AS TotalAmount, 
    COUNT(*) AS TransactionCount
FROM 
    FinancialRecords
GROUP BY 
    RecordType;

CREATE VIEW FinancialDetails AS
SELECT 
    RecordID, 
    RecordDate, 
    RecordType, 
    Description, 
    Amount, 
    RelatedID, 
    RelatedType
FROM 
    FinancialRecords
ORDER BY 
    RecordDate DESC;