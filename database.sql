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
    FOREIGN KEY (TypeID) REFERENCES Types(TypeID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- Creating the Types table
CREATE TABLE Types (
    TypeID INTEGER PRIMARY KEY,
    Type TEXT
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
