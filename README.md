# restaurant-go

Restaurant Mobile App Backend

![flow](static/assets/images/Restaurant-Go.png)




sequenceDiagram
    participant User
    participant API
    participant OrderModel
    participant TrayItemModel
    User->>API: POST /orders
    API->>OrderModel: Create Order
    API->>TrayItemModel: Add Items to Order
    OrderModel-->>API: Order Created
    TrayItemModel-->>API: Items Added
    API-->>User: Order Confirmation



sequenceDiagram
    participant User
    participant API
    participant UserModel
    participant TrayModel
    User->>API: POST /register
    API->>UserModel: Create User
    UserModel-->>API: User Created
    API->>TrayModel: Create Tray for User
    TrayModel-->>API: Tray Created
    API-->>User: Registration Confirmation
