-- Creating the Customers table
CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT,
    PhoneNumber TEXT,
    Email TEXT,
    Address TEXT
);

-- Creating the Employees table
CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT,
    Position TEXT,
    Salary REAL,
    HireDate DATE
);

-- Creating the Inventory table
CREATE TABLE Inventory (
    InventoryID INTEGER PRIMARY KEY,
    ItemName TEXT,
    CategoryID INTEGER,
    Quantity INTEGER,
    UnitPrice REAL,
    SupplierID INTEGER,
    FOREIGN KEY (CategoryID) REFERENCES ItemCategories(CategoryID),
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
);

-- Creating the ItemCategories table
CREATE TABLE ItemCategories (
    CategoryID INTEGER PRIMARY KEY,
    Category TEXT
);

-- Creating the Accountings table
CREATE TABLE Accountings (
    TransactionID INTEGER PRIMARY KEY,
    TransactionDate DATE,
    Amount REAL,
    TypeID INTEGER,
    CustomerID INTEGER,
    EmployeeID INTEGER,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- Creating the Orders table
CREATE TABLE Orders (
    OrderID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    EmployeeID INTEGER,
    OrderDate DATE,
    TotalAmount REAL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- Creating the Suppliers table
CREATE TABLE Suppliers (
    SupplierID INTEGER PRIMARY KEY,
    SupplierName TEXT,
    ContactPerson TEXT,
    PhoneNumber TEXT
);

-- Creating the Menu table
CREATE TABLE Menu (
    MenuItemID INTEGER PRIMARY KEY,
    ItemName TEXT,
    Price REAL,
    CategoryID INTEGER,
    FOREIGN KEY (CategoryID) REFERENCES FoodCategories(CategoryID)
);

-- Creating the FoodCategories table
CREATE TABLE FoodCategories (
    CategoryID INTEGER PRIMARY KEY,
    Category TEXT
);

-- Creating the OrderItems table
CREATE TABLE OrderItems (
    OrderItemID INTEGER PRIMARY KEY,
    OrderID INTEGER,
    MenuItemID INTEGER,
    Quantity INTEGER,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (MenuItemID) REFERENCES Menu(MenuItemID)
);

INSERT INTO Customers (CustomerID, FirstName, LastName, PhoneNumber, Email, Address) VALUES
(1, 'John', 'Smith', '123-456-7890', 'john@example.com', '123 Elm St'),
(2, 'Jane', 'Doe', '234-567-8901', 'jane@example.com', '456 Oak St'),
(3, 'Alice', 'Brown', '345-678-9012', 'alice@example.com', '789 Pine St'),
(4, 'Bob', 'White', '456-789-0123', 'bob@example.com', '101 Maple St'),
(5, 'Carol', 'Black', '567-890-1234', 'carol@example.com', '202 Birch St');

INSERT INTO Employees (FirstName, LastName, Position, Salary, HireDate) VALUES
('Mark', 'Green', 'Manager', 50000, '2020-01-01'),
('Sarah', 'Blue', 'Chef', 45000, '2021-03-15'),
('Tom', 'Red', 'Waiter', 30000, '2019-07-20'),
('Lucy', 'Yellow', 'Waitress', 32000, '2022-05-10'),
('James', 'Purple', 'Dishwasher', 25000, '2023-02-28');

INSERT INTO Inventory (InventoryID, ItemName, CategoryID, Quantity, UnitPrice, SupplierID) VALUES
(1, 'Tomato', 1, 100, 0.5, 1),
(2, 'Chicken', 2, 50, 2, 2),
(3, 'Milk', 3, 20, 1.2, 3),
(4, 'Bread', 4, 30, 1, 4),
(5, 'Eggs', 3, 40, 0.2, 3);

INSERT INTO ItemCategories (CategoryID, Category) VALUES
(1, 'Produce'),
(2, 'Meat'),
(3, 'Dairy'),
(4, 'Bakery'),
(5, 'Fruits');

INSERT INTO Accountings (TransactionID, TransactionDate, Amount, TypeID, CustomerID, EmployeeID) VALUES
(1, '2024-01-01', 50, 1, 1, 3),
(2, '2024-01-02', 75, 1, 2, 3),
(3, '2024-01-03', -20, 2, 1, 4),
(4, '2024-01-04', 100, 1, 3, 4),
(5, '2024-01-05', 150, 1, 4, 4);

INSERT INTO Orders (OrderID, CustomerID, EmployeeID, OrderDate, TotalAmount) VALUES
(1, 1, 3, '2024-01-01', 50),
(2, 2, 3, '2024-01-02', 75),
(3, 1, 4, '2024-01-03', 30),
(4, 3, 4, '2024-01-04', 100),
(5, 4, 4, '2024-01-05', 150);

INSERT INTO Suppliers (SupplierID, SupplierName, ContactPerson, PhoneNumber) VALUES
(1, 'Fresh Farms', 'Anna Green', '111-222-3333'),
(2, 'Meat Co.', 'Mike Brown', '222-333-4444'),
(3, 'Dairy Pro', 'Susan White', '333-444-5555'),
(4, 'Ocean Delights', 'Sarah Blue', '444-555-6666'),
(5, 'Spice World', 'Raj Patel', '555-666-7777');

INSERT INTO Menu (MenuItemID, ItemName, Price, CategoryID) VALUES
(1, 'Burger', 10, 1),
(2, 'Salad', 8, 2),
(3, 'Steak', 20, 1),
(4, 'Soup', 6, 2),
(5, 'Cake', 5, 3);

INSERT INTO FoodCategories (CategoryID, Category) VALUES
(1, 'Main'),
(2, 'Appetizer'),
(3, 'Dessert'),
(4, 'Beverage'),
(5, 'Side Dish');

INSERT INTO OrderItems (OrderItemID, OrderID, MenuItemID, Quantity) VALUES
(1, 1, 1, 2),
(2, 2, 3, 1),
(3, 3, 2, 1),
(4, 4, 4, 3),
(5, 5, 5, 2);

CREATE TRIGGER AddAccountingEntryAfterPayment
AFTER INSERT ON Orders
FOR EACH ROW
BEGIN
    INSERT INTO Accountings (TransactionDate, Amount, TypeID, CustomerID, EmployeeID)
    VALUES (NEW.OrderDate, NEW.TotalAmount, 1, NEW.CustomerID, NEW.EmployeeID);
END
